import schedule
import time
import random
from datetime import datetime
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from .trend_service import trend_service
from .blog_service import blog_service
from .seo_service import seo_service
from .image_service import image_service
from .social_service import social_service  # This service appears to be referenced but missing

class AutomationService:
    """Service to manage automated blog generation and publishing"""
    
    def __init__(self):
        self.log_file = "automation_log.json"
        self.config = {
            "posts_per_day": 1,
            "min_hours_between_posts": 8,
            "trending_sources": ["google", "news"],
            "categories": ["technology", "business", "science"],
            "min_seo_score": 70
        }
        self.last_post_time = None
        
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
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def generate_and_publish_blog(self) -> Dict:
        """Main process to generate and publish a blog based on trending topics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": "started"
        }
        
        try:
            # 1. Get trending topics
            topics = trend_service.get_trending_topics(
                sources=self.config["trending_sources"],
                count=5
            )
            
            if not topics:
                log_entry["status"] = "failed"
                log_entry["error"] = "No trending topics found"
                return log_entry
            
            # 2. Select a random topic
            selected_topic = random.choice(topics)
            log_entry["topic"] = selected_topic
            
            # 3. Generate blog prompt
            blog_prompt = trend_service.generate_blog_topic(selected_topic)
            
            # 4. Generate blog content
            content = blog_service.generate_blog_content(blog_prompt)
            
            # 5. Analyze SEO and possibly improve content
            seo_report = seo_service.analyze_seo(content)
            log_entry["seo_score"] = seo_report["score"]
            
            # If SEO score is too low, try to improve the content or regenerate
            if seo_report["score"] < self.config["min_seo_score"]:
                # For now, just regenerate - in future we could have a more sophisticated improvement algorithm
                content = blog_service.generate_blog_content(blog_prompt + " Include more keywords related to the topic and aim for at least 500 words.")
                seo_report = seo_service.analyze_seo(content)
                log_entry["seo_score_after_improvement"] = seo_report["score"]
            
            # 6. Generate blog title (extract from content or generate separately)
            blog_title = self._extract_title_from_content(content) or f"Latest Trends: {selected_topic['topic']}"
            
            # 7. Generate image
            image_prompt = f"A professional blog image related to {selected_topic['topic']}"
            image_path = image_service.generate_image(image_prompt)
            
            # 8. Publish blog
            result = blog_service.publish_blog(
                title=blog_title,
                content=content,
                image_path=image_path,
                labels=self._generate_labels(selected_topic, seo_report)
            )
            
            # 9. Share on social media
            try:
                social_service.share_on_twitter(f"New blog post: {blog_title} - Check it out! {result.get('url', '')}")
            except Exception as e:
                log_entry["social_sharing_error"] = str(e)
            
            log_entry["status"] = "success"
            log_entry["publish_result"] = result
            self.last_post_time = datetime.now()
            
        except Exception as e:
            log_entry["status"] = "failed"
            log_entry["error"] = str(e)
        
        # Save log
        self.save_log(log_entry)
        return log_entry
    
    def _extract_title_from_content(self, content: str) -> Optional[str]:
        """Extract a title from the generated content"""
        # Simple extraction - look for h1/h2 tags or first sentence
        if "<h1>" in content and "</h1>" in content:
            return content.split("<h1>")[1].split("</h1>")[0]
        if "<h2>" in content and "</h2>" in content:
            return content.split("<h2>")[1].split("</h2>")[0]
        
        # Take first sentence if it's a reasonable length
        sentences = content.split(". ")
        if sentences and 3 < len(sentences[0]) < 100:
            return sentences[0]
        
        return None
    
    def _generate_labels(self, topic: Dict, seo_report: Dict) -> List[str]:
        """Generate tags/labels for the blog post"""
        labels = []
        
        # Add topic source as label
        if "source" in topic:
            labels.append(topic["source"])
        
        # Add top keywords from SEO report
        if "keywords" in seo_report:
            top_keywords = list(seo_report["keywords"].keys())[:3]
            labels.extend(top_keywords)
        
        # Add date label
        labels.append(datetime.now().strftime("%B %Y"))
        
        return labels
    
    def run_scheduled_job(self) -> None:
        """Run the scheduled job if conditions are met"""
        # Check if enough time has passed since the last post
        if self.last_post_time:
            hours_since_last_post = (datetime.now() - self.last_post_time).total_seconds() / 3600
            if hours_since_last_post < self.config["min_hours_between_posts"]:
                print(f"Not enough time since last post ({hours_since_last_post:.1f} hours)")
                return
        
        result = self.generate_and_publish_blog()
        print(f"Blog automation result: {result['status']}")
    
    def schedule_tasks(self) -> None:
        """Set up the scheduling of automated blog posts"""
        # Schedule posts depending on posts_per_day setting
        if self.config["posts_per_day"] == 1:
            # Once a day at 9 AM
            schedule.every().day.at("09:00").do(self.run_scheduled_job)
        elif self.config["posts_per_day"] == 2:
            # Twice a day at 9 AM and 5 PM
            schedule.every().day.at("09:00").do(self.run_scheduled_job)
            schedule.every().day.at("17:00").do(self.run_scheduled_job)
        else:
            # Default schedule
            schedule.every(24 // max(1, self.config["posts_per_day"])).hours.do(self.run_scheduled_job)
    
    def run(self) -> None:
        """Run the automation service"""
        self.schedule_tasks()
        
        print(f"Automation service started. Posting {self.config['posts_per_day']} blog(s) per day.")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

automation_service = AutomationService()

# Example standalone usage
if __name__ == "__main__":
    # Run once immediately
    result = automation_service.generate_and_publish_blog()
    print(f"Blog generation result: {result}")
    
    # Or run scheduled
    # automation_service.run()
