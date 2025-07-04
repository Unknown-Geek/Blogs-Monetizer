import schedule
import time
import random
import threading
import re
import difflib
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from .trend_service import trend_service
from .blog_service import blog_service
from .seo_service import seo_service
from .image_service import image_service
from .social_service import social_service
from helpers.image_utils import clear_images_directory

class AutomationService:
    """Service to manage automated blog generation and publishing"""
    
    def __init__(self):
        # Setup log file in logs directory
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(self.log_dir, exist_ok=True)        
        self.log_file = os.path.join(self.log_dir, "automation_log.json")
          # Configuration with defaults and override from environment
        self.config = {
            "posts_per_day": int(os.environ.get("POSTS_PER_DAY", 1)),
            "trending_sources": ["news"],  # Removed google, only using news sources now
            "categories": ["technology", "business", "science", "health"],
            "min_seo_score": int(os.environ.get("MIN_SEO_SCORE", 70)),
            "social_sharing": True,
            "retry_failed": True,
            "max_retries": 3,
            "post_timing": "distributed"  # "distributed" or "scheduled"
        }
        
        self.last_post_time = None
        self.running = False
        self.stop_requested = False
        self.scheduler_thread = None
        self.failed_attempts = {}  # Track failed attempts for each topic
        
    def load_logs(self) -> List[Dict]:
        """Load past automation logs"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_log(self, log_entry: Dict) -> None:
        """Save a log entry to the log file"""
        logs = self.load_logs()
        logs.append(log_entry)
        
        # Keep logs manageable (max 1000 entries)
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def generate_and_publish_blog(self, specific_topic: Optional[Dict] = None) -> Dict:
        """Main process to generate and publish a blog based on trending topics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": "started"
        }
        
        try:
            # 1. Get trending topics or use provided topic
            if specific_topic:
                selected_topic = specific_topic
                log_entry["topic"] = selected_topic
            else:
                topics = trend_service.get_trending_topics(
                    sources=self.config["trending_sources"],
                    count=10,
                    categories=self.config["categories"]
                )
                
                if not topics:
                    log_entry["status"] = "failed"
                    log_entry["error"] = "No trending topics found"
                    self.save_log(log_entry)
                    return log_entry
                
                # Filter out topics that have repeatedly failed
                filtered_topics = [t for t in topics if self._get_failure_count(t) < self.config["max_retries"]]
                
                # If all topics have failed too many times, reset failure counts and use original list
                if not filtered_topics and self.config["retry_failed"]:
                    self.failed_attempts = {}
                    filtered_topics = topics
                elif not filtered_topics:
                    # Use original topics but prioritize ones with fewer failures
                    filtered_topics = sorted(topics, key=lambda t: self._get_failure_count(t))
                
                # 2. Select a topic, prioritizing those that haven't been attempted recently
                selected_topic = filtered_topics[0] if filtered_topics else topics[0]
                  # Check for recently used topics
                recent_topics = self._get_recent_topics(hours=24)
                
                # Filter out topics that have been published recently
                non_duplicate_topics = []
                for topic in filtered_topics:
                    if not self._is_duplicate_topic(topic, recent_topics):
                        non_duplicate_topics.append(topic)
                
                if non_duplicate_topics:
                    selected_topic = non_duplicate_topics[0]
                else:
                    # If all topics are duplicates, select the oldest one
                    print("All trending topics are duplicates! Using oldest one with lowest failure count.")
                    filtered_topics.sort(key=lambda t: (self._get_failure_count(t)))
                    selected_topic = filtered_topics[0]
                
                log_entry["topic"] = selected_topic
            
            # 3. Generate blog prompt with enhanced context
            blog_prompt = trend_service.generate_blog_topic(selected_topic)
            log_entry["prompt"] = blog_prompt
            
            # 4. Generate blog content
            start_time = time.time()
            try:
                content = blog_service.generate_blog_content(blog_prompt)
                generation_time = time.time() - start_time
                log_entry["generation_time_seconds"] = round(generation_time, 2)
            except Exception as e:
                log_entry["content_error"] = str(e)
                raise Exception(f"Failed to generate content: {str(e)}")
            
            # 5. Analyze SEO and possibly improve content
            try:
                seo_report = seo_service.analyze_seo(content)
                log_entry["seo_score"] = seo_report["score"]
                log_entry["word_count"] = seo_report["word_count"]
                
                # If SEO score is too low, try to improve the content
                if seo_report["score"] < self.config["min_seo_score"]:
                    improved_prompt = blog_prompt + "\n\nPlease improve this content based on the following SEO recommendations:\n"
                    
                    # Add specific recommendations from SEO report
                    for issue in seo_report.get("issues", []):
                        improved_prompt += f"- {issue}\n"
                    
                    for rec in seo_report.get("recommendations", []):
                        improved_prompt += f"- {rec}\n"
                    
                    # Add word count target
                    improved_prompt += f"\nAim for at least {max(500, seo_service.min_word_count)} words and ensure good keyword density."
                    
                    # Regenerate with improved prompt
                    content = blog_service.generate_blog_content(improved_prompt)
                    
                    # Re-analyze SEO
                    seo_report = seo_service.analyze_seo(content)
                    log_entry["seo_score_after_improvement"] = seo_report["score"]
                    log_entry["word_count_after_improvement"] = seo_report["word_count"]
            except Exception as e:
                log_entry["seo_error"] = str(e)
                # Continue anyway to publish what we have
            
            # 6. Generate blog title (extract from content or generate separately)
            blog_title = self._extract_title_from_content(content)
            if not blog_title:
                if "topic" in selected_topic:
                    blog_title = f"Latest Trends: {selected_topic['topic']}"
                else:
                    blog_title = "New Blog Post: " + datetime.now().strftime("%Y-%m-%d")
                    
            log_entry["title"] = blog_title
            
            # 7. Generate image
            try:
                image_prompt = f"A professional blog image related to {selected_topic['topic']}"
                image_path = image_service.generate_image(image_prompt)
                if image_path:
                    log_entry["image_path"] = image_path
                else:
                    log_entry["image_error"] = "Failed to generate image, but continuing without one"
            except Exception as e:
                log_entry["image_error"] = str(e)
                image_path = None  # Continue without an image
            
            # 8. Generate labels/tags
            try:
                labels = self._generate_labels(selected_topic, seo_report)
                log_entry["labels"] = labels
            except Exception as e:
                log_entry["labels_error"] = str(e)
                labels = []  # Continue without labels
            
            # 9. Publish blog

            
            try:

            
                result = blog_service.publish_blog(

            
                    title=blog_title,

            
                    content=content,

            
                    image_path=image_path,

            
                    labels=labels

            
                )

            
                

            
                if result.get("success", True):  # Default to True for backward compatibility
                    log_entry["publish_result"] = result
                    log_entry["published_url"] = result.get("url", "")
                    
                    # Reset failure count for this topic
                    self._reset_failure_count(selected_topic)
                    
                    # Clear the images directory after successful posting
                    try:
                        if clear_images_directory():
                            log_entry["images_cleared"] = True
                        else:
                            log_entry["images_cleared"] = False
                    except Exception as e:
                        log_entry["images_clear_error"] = str(e)
                    
                    # Clear the images directory after successful posting
                    try:
                        if clear_images_directory():
                            log_entry["images_cleared"] = True
                        else:
                            log_entry["images_cleared"] = False
                    except Exception as e:
                        log_entry["images_clear_error"] = str(e)
                else:
                    log_entry["publish_error"] = result.get("error", "Unknown publishing error")
                    # Increment failure count
                    self._increment_failure_count(selected_topic)
                    raise Exception(log_entry["publish_error"])
            except Exception as e:
                log_entry["publish_error"] = str(e)
                # Increment failure count for this topic
                self._increment_failure_count(selected_topic)
                # Continue with the process even if publishing fails
                result = {"error": str(e)}
              # 10. Share on social media only if publishing succeeded and social sharing is enabled
            if "publish_error" not in log_entry and self.config["social_sharing"]:
                try:
                    if hasattr(social_service, "share_across_platforms") and result.get("url"):
                        share_message = f"New blog post: {blog_title} - Check it out! {result.get('url', '')}"
                        
                        # Add hashtags from the labels
                        hashtags = [f"#{label.replace(' ', '')}" for label in labels[:3] if ' ' not in label]
                        if hashtags:                        share_message += " " + " ".join(hashtags)
                            
                        share_result = social_service.share_across_platforms(
                            message=share_message,
                            link=result.get("url", "")
                            # No specific platforms needed since all sharing is disabled
                        )
                        log_entry["social_sharing_result"] = share_result
                except Exception as e:
                    log_entry["social_sharing_error"] = str(e)
            
            # Mark as success if we at least generated content, even if publishing failed
            log_entry["status"] = "success" if "publish_error" not in log_entry else "partial"
            self.last_post_time = datetime.now()
            
        except Exception as e:
            log_entry["status"] = "failed"
            log_entry["error"] = str(e)
            
            # Increment failure count if we have a topic
            if "topic" in log_entry:
                self._increment_failure_count(log_entry["topic"])
        
        # Save log
        self.save_log(log_entry)
        return log_entry
    
    def _extract_title_from_content(self, content: str) -> Optional[str]:
        """Extract a title from the generated content"""
        # Check for h1 tag first
        h1_match = re.search(r'<h1>(.*?)</h1>', content)
        if h1_match:
            return h1_match.group(1)
        
        # Then check for h2 tag
        h2_match = re.search(r'<h2>(.*?)</h2>', content)
        if h2_match:
            return h2_match.group(1)
        
        # Take first sentence if it's a reasonable length
        sentences = content.split(". ")
        if sentences and 3 < len(sentences[0]) < 100:
            # Remove any HTML tags
            clean_sentence = re.sub(r'<[^>]*>', '', sentences[0])
            return clean_sentence
        
        return None
    
    def _generate_labels(self, topic: Dict, seo_report: Dict) -> List[str]:
        """Generate tags/labels for the blog post"""
        labels = []
        
        # Add topic source as label
        if "source" in topic:
            labels.append(topic["source"])
        
        # Add category if available
        if "category" in topic:
            labels.append(topic["category"])
        
        # Add top keywords from SEO report
        if "keywords" in seo_report:
            top_keywords = list(seo_report["keywords"].keys())[:3]
            labels.extend(top_keywords)
        
        # Add date label
        labels.append(datetime.now().strftime("%B %Y"))
        
        # Remove duplicates and truncate labels if too long
        unique_labels = []
        for label in labels:
            # Limit label length
            if len(label) > 25:
                label = label[:25]
            
            # Only add if unique
            if label not in unique_labels:
                unique_labels.append(label)
        
        return unique_labels
    
    def _get_recent_topics(self, hours: int = 24) -> Dict[str, datetime]:
        """Get topics posted in the recent past"""
        logs = self.load_logs()
        recent_topics = {}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for log in logs:
            if log.get("status") in ["success", "partial"]:
                log_time = datetime.fromisoformat(log["timestamp"])
                if log_time > cutoff_time and "topic" in log:
                    topic = log["topic"]
                    
                    # Create more specific unique keys to avoid duplicates
                    if "url" in topic:
                        # For news articles, use the URL as a unique identifier
                        topic_key = f"{topic['source']}:{topic['url']}"
                    else:
                        # For other sources, use the topic text
                        topic_key = f"{topic['source']}:{topic['topic']}"
                        
                    # Also add the exact title as a key to prevent exact title duplicates
                    if "title" in log:
                        title_key = f"title:{log['title']}"
                        recent_topics[title_key] = log_time
                        
                    recent_topics[topic_key] = log_time
                    
                    # For news articles, also add a key based on title similarity to catch rewrites of the same news
                    if topic['source'] == 'news' and 'topic' in topic:
                        # Normalize the topic title (lowercase, remove punctuation)
                        normalized_title = re.sub(r'[^\w\s]', '', topic['topic'].lower())
                        title_words = set(normalized_title.split())
                        
                        # Only keep significant words (longer than 3 chars)
                        significant_words = [w for w in title_words if len(w) > 3]
                        if significant_words:
                            # Create a key from the sorted words to detect similar titles
                            words_key = f"keywords:{','.join(sorted(significant_words))}"
                            recent_topics[words_key] = log_time
        
        return recent_topics
    
    def _is_duplicate_topic(self, topic: Dict, recent_topics: Dict[str, datetime]) -> bool:
        """Check if a topic is a duplicate of a recently published one (strengthened)"""
        # Check exact URL match for news articles
        if "url" in topic:
            topic_key = f"{topic['source']}:{topic['url']}"
            if topic_key in recent_topics:
                return True
        # Check exact topic match
        topic_key = f"{topic['source']}:{topic['topic']}"
        if topic_key in recent_topics:
            return True
        # For news articles, check title and description similarity
        if topic['source'] == 'news' and 'topic' in topic:
            normalized_title = re.sub(r'[^\w\s]', '', topic['topic'].lower())
            title_words = set(normalized_title.split())
            significant_words = [w for w in title_words if len(w) > 3]
            if significant_words:
                words_key = f"keywords:{','.join(sorted(significant_words))}"
                if words_key in recent_topics:
                    return True
            # Fuzzy match: compare with all recent news topics and descriptions
            for key in recent_topics:
                if key.startswith('news:') or key.startswith('title:') or key.startswith('keywords:'):
                    # Extract the recent topic string
                    recent_topic = key.split(':', 1)[-1]
                    # Compare titles
                    ratio = difflib.SequenceMatcher(None, topic['topic'].lower(), recent_topic.lower()).ratio()
                    if ratio > 0.85:
                        return True
                    # Compare descriptions if available
                    if 'description' in topic and topic['description']:
                        ratio_desc = difflib.SequenceMatcher(None, topic['description'].lower(), recent_topic.lower()).ratio()
                        if ratio_desc > 0.85:
                            return True
        return False
    
    def _get_failure_count(self, topic: Dict) -> int:
        """Get the number of failed attempts for a topic"""
        topic_key = f"{topic['source']}:{topic['topic']}"
        return self.failed_attempts.get(topic_key, 0)
    
    def _increment_failure_count(self, topic: Dict) -> None:
        """Increment the failure count for a topic"""
        topic_key = f"{topic['source']}:{topic['topic']}"
        self.failed_attempts[topic_key] = self.failed_attempts.get(topic_key, 0) + 1
    
    def _reset_failure_count(self, topic: Dict) -> None:
        """Reset the failure count for a topic"""
        topic_key = f"{topic['source']}:{topic['topic']}"
        if topic_key in self.failed_attempts:
            del self.failed_attempts[topic_key]
    
    def run_scheduled_job(self) -> None:
        """Run the scheduled job if conditions are met"""        # No need to check for minimum time between posts
        if self.last_post_time:
            hours_since_last_post = (datetime.now() - self.last_post_time).total_seconds() / 3600
            print(f"Time since last post: {hours_since_last_post:.1f} hours")
        
        result = self.generate_and_publish_blog()
        print(f"Blog automation result: {result['status']}")
    
    def schedule_tasks(self) -> None:
        """Set up the scheduling of automated blog posts"""
        schedule.clear()  # Clear any existing schedules
        
        if self.config["post_timing"] == "distributed":
            # Distribute posts throughout the day
            posts_per_day = self.config["posts_per_day"]
            if posts_per_day <= 0:
                posts_per_day = 1
            
            day_minutes = 24 * 60
            minutes_between_posts = day_minutes // posts_per_day
            
            # Calculate post times
            for i in range(posts_per_day):
                minutes_offset = i * minutes_between_posts
                hour = (minutes_offset // 60) % 24
                minute = minutes_offset % 60
                
                # Add a small random offset (±15 minutes) to make it less predictable
                random_offset = random.randint(-15, 15)
                minute = (minute + random_offset) % 60
                
                time_str = f"{hour:02d}:{minute:02d}"
                schedule.every().day.at(time_str).do(self.run_scheduled_job)
                print(f"Scheduled post at {time_str}")
        else:
            # Fixed schedule based on posts_per_day
            if self.config["posts_per_day"] == 1:
                # Once a day at 9 AM
                schedule.every().day.at("09:00").do(self.run_scheduled_job)
            elif self.config["posts_per_day"] == 2:
                # Twice a day at 9 AM and 5 PM
                schedule.every().day.at("09:00").do(self.run_scheduled_job)
                schedule.every().day.at("17:00").do(self.run_scheduled_job)
            elif self.config["posts_per_day"] == 3:
                # Three times a day
                schedule.every().day.at("09:00").do(self.run_scheduled_job)
                schedule.every().day.at("13:00").do(self.run_scheduled_job)
                schedule.every().day.at("17:00").do(self.run_scheduled_job)
            else:
                # Default schedule
                hours_between = max(1, 24 // self.config["posts_per_day"])
                schedule.every(hours_between).hours.do(self.run_scheduled_job)
    
    def run(self) -> None:
        """Run the automation service"""
        if self.running:
            print("Automation service is already running")
            return
            
        self.stop_requested = False
        self.running = True
        
        self.schedule_tasks()
        
        print(f"Automation service started. Posting {self.config['posts_per_day']} blog(s) per day.")
        while not self.stop_requested:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
        self.running = False
        print("Automation service stopped")
    
    def start_in_thread(self) -> None:
        """Start the automation service in a background thread"""
        if self.running:
            print("Automation service is already running")
            return
            
        def run_thread():
            self.run()
            
        self.scheduler_thread = threading.Thread(target=run_thread)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop(self) -> None:
        """Stop the automation service"""
        if not self.running:
            print("Automation service is not running")
            return
            
        self.stop_requested = True
        print("Stop signal sent to automation service")
    
    def update_config(self, config_updates: Dict[str, Any]) -> Dict:
        """Update the configuration with new values"""
        for key, value in config_updates.items():
            if key in self.config:
                self.config[key] = value
        
        # Reschedule if running
        if self.running:
            self.schedule_tasks()
            
        return self.config
    
    def get_next_scheduled_times(self, count: int = 5) -> List[str]:
        """Get the next scheduled post times"""
        result = []
        for job in schedule.jobs:
            next_run = job.next_run
            result.append(next_run.strftime("%Y-%m-%d %H:%M:%S"))
            
        return sorted(result)[:count]

automation_service = AutomationService()

# Example standalone usage
if __name__ == "__main__":
    # Run once immediately
    result = automation_service.generate_and_publish_blog()
    print(f"Blog generation result: {result}")
    
    # Or run scheduled
    # automation_service.run()
