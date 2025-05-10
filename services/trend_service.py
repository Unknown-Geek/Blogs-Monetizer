import requests
import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pytrends.request import TrendReq  # Add pytrends for Google Trends

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class TrendService:
    """Service to detect trending topics for blog generation"""
    
    def __init__(self):
        # Initialize pytrends for Google Trends API
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
        self.twitter_api_url = "https://api.twitter.com/2/tweets/search/recent"
        self.twitter_bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "YOUR_TWITTER_BEARER_TOKEN")
        self.news_api_url = "https://newsapi.org/v2/top-headlines"
        self.news_api_key = os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY")
        
        # Create a cache directory to store trend data
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Define cache files
        self.google_trends_cache = os.path.join(self.cache_dir, "google_trends.json")
        self.news_cache = os.path.join(self.cache_dir, "news_trends.json")
    
    def get_google_trends(self, geo="US") -> List[Dict]:
        """Fetch trending searches from Google Trends with caching"""
        # Check for cached data first (not older than 6 hours)
        cached_data = self._load_cached_data(self.google_trends_cache, max_age_hours=6)
        if cached_data:
            return cached_data
        
        try:
            # Get trending searches from pytrends package
            print("Fetching Google trending searches...")
            
            # Get real-time trending searches
            trending_searches_df = self.pytrends.trending_searches(pn=geo.lower())
            
            # Convert to our expected format
            trending_searches = []
            
            # Get top 20 trending searches (if available)
            for i in range(min(20, len(trending_searches_df))):
                # Get the trending search term
                trend_title = trending_searches_df.iloc[i, 0]
                
                # Get related queries for this trend (needs a separate API call)
                try:
                    self.pytrends.build_payload(kw_list=[trend_title], timeframe='now 1-d')
                    related_queries = self.pytrends.related_queries()
                    related_topics = []
                    
                    # Extract top related queries if available
                    if related_queries and trend_title in related_queries:
                        top_df = related_queries[trend_title].get('top')
                        if top_df is not None and not top_df.empty:
                            related_topics = top_df['query'].tolist()[:5]  # Get top 5 related queries
                except Exception as e:
                    print(f"Error getting related queries for {trend_title}: {e}")
                    related_topics = []
                
                trending_searches.append({
                    "title": trend_title,
                    "traffic": "trending",  # pytrends doesn't provide traffic volume
                    "related_topics": related_topics
                })
            
            # Cache the results
            self._save_cached_data(self.google_trends_cache, trending_searches)
            
            return trending_searches
        
        except Exception as e:
            print(f"Error fetching Google Trends: {e}")
            # Try to use cached data regardless of age in case of error
            cached_data = self._load_cached_data(self.google_trends_cache, max_age_hours=24)
            if cached_data:
                return cached_data
            return []
            
    def get_twitter_trends(self) -> List[Dict]:
        """Fetch trending topics from Twitter"""
        headers = {
            "Authorization": f"Bearer {self.twitter_bearer_token}"
        }
        
        params = {
            "query": "is:trending",
            "max_results": 10
        }
        
        try:
            response = requests.get(self.twitter_api_url, headers=headers, params=params)
            data = response.json()
            
            trends = []
            for tweet in data.get("data", []):
                # Extract hashtags
                hashtags = [tag for tag in tweet.get("text", "").split() if tag.startswith("#")]
                
                trends.append({
                    "text": tweet.get("text", ""),
                    "hashtags": hashtags,
                    "created_at": tweet.get("created_at", "")
                })
            
            return trends
        
        except Exception as e:
            print(f"Error fetching Twitter trends: {e}")
            return []
    
    def get_news_headlines(self, country="us", category=None) -> List[Dict]:
        """
        Fetch top news headlines with caching
        
        Args:
            country: Country code (default: "us")
            category: Optional category (business, entertainment, general, health, science, sports, technology)
        """
        # Check for cached data first (not older than 2 hours)
        cache_key = f"{country}_{category or 'all'}"
        news_cache_file = os.path.join(self.cache_dir, f"news_{cache_key}.json")
        cached_data = self._load_cached_data(news_cache_file, max_age_hours=2)
        if cached_data:
            return cached_data
            
        params = {
            "country": country,
            "apiKey": self.news_api_key
        }
        
        if category:
            params["category"] = category
        
        try:
            response = requests.get(self.news_api_url, params=params)
            data = response.json()
            
            if response.status_code != 200:
                print(f"News API Error: {data.get('message', '')}")
                # Try to use cached data regardless of age in case of error
                cached_data = self._load_cached_data(news_cache_file, max_age_hours=24)
                if cached_data:
                    return cached_data
                return []
            
            headlines = []
            for article in data.get("articles", []):
                headlines.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", "")
                })
            
            # Cache the results
            self._save_cached_data(news_cache_file, headlines)
            
            return headlines
        
        except Exception as e:
            print(f"Error fetching news headlines: {e}")
            # Try to use cached data regardless of age in case of error
            cached_data = self._load_cached_data(news_cache_file, max_age_hours=24)
            if cached_data:
                return cached_data
            return []
    
    def _load_cached_data(self, cache_file: str, max_age_hours: int = 6) -> Optional[List[Dict]]:
        """Load cached data if it's not too old"""
        if not os.path.exists(cache_file):
            return None
            
        try:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_file))
            # Check if file is too old
            if datetime.now() - file_mtime > timedelta(hours=max_age_hours):
                return None
                
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cached data: {e}")
            return None
    
    def _save_cached_data(self, cache_file: str, data: List[Dict]) -> bool:
        """Save data to cache file"""
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving cache: {e}")
            return False
    
    def get_trending_topics(self, sources=["google", "news"], count=5, categories=None) -> List[Dict]:
        """
        Get trending topics from multiple sources
        
        Args:
            sources: List of sources to check ("google", "twitter", "news")
            count: Number of trends to return
            categories: Optional list of news categories to include
        """
        all_trends = []
        
        if "google" in sources:
            google_trends = self.get_google_trends()
            all_trends.extend([{
                "source": "google", 
                "topic": trend["title"],
                "related": trend.get("related_topics", [])[:3]
            } for trend in google_trends])
        
        if "twitter" in sources:
            twitter_trends = self.get_twitter_trends()
            all_trends.extend([{
                "source": "twitter", 
                "topic": trend["text"],
                "hashtags": trend.get("hashtags", [])[:3]
            } for trend in twitter_trends])
        
        if "news" in sources:
            # Use specified categories or default to a variety
            news_categories = categories or ["technology", "business", "science", "health"]
            for category in news_categories:
                news_trends = self.get_news_headlines(category=category)
                for headline in news_trends:
                    all_trends.append({
                        "source": "news",
                        "topic": headline["title"],
                        "category": category,
                        "description": headline.get("description", ""),
                        "news_source": headline.get("source", "")
                    })
        
        # Randomize to avoid always getting the same topics
        random.shuffle(all_trends)
        
        # Return the top trends
        return all_trends[:count]
    
    def generate_blog_topic(self, trend: Dict) -> str:
        """Convert a trend into a blog topic prompt with enhanced context"""
        source = trend.get("source", "")
        topic = trend.get("topic", "")
        
        if source == "google":
            related = trend.get("related", [])
            related_str = ", ".join(related[:3]) if related else ""
            if related_str:
                return f"Write an in-depth, SEO-optimized blog post about {topic}. Include information on related topics such as {related_str}. The post should be informative, engaging, and include relevant facts and insights."
            else:
                return f"Write an informative, SEO-optimized blog post about {topic}, including recent developments and why it's trending."
        
        elif source == "twitter":
            hashtags = trend.get("hashtags", [])
            hashtag_str = " ".join(hashtags[:3]) if hashtags else ""
            if hashtag_str:
                return f"Create an engaging blog post discussing {topic} that's trending on social media. Include information about these related hashtags: {hashtag_str}. Make the content shareable and relevant to current discussions."
            else:
                return f"Create an engaging blog post discussing {topic} that's currently trending on social media. Make the content shareable and include calls to action."
        
        elif source == "news":
            category = trend.get("category", "")
            description = trend.get("description", "")
            news_source = trend.get("news_source", "")
            
            prompt = f"Write a comprehensive blog post analyzing the recent news: {topic}"
            
            if description:
                prompt += f". Context: {description}"
            
            if category:
                prompt += f". This is trending in the {category} category"
                
            if news_source:
                prompt += f" and was reported by {news_source}"
                
            prompt += ". Include facts, analysis, and your own insights while maintaining journalistic integrity."
            
            return prompt
        
        else:
            return f"Write a blog post about the trending topic: {topic}. Make it informative, SEO-friendly, and engaging for readers interested in this subject."

trend_service = TrendService()

# Usage example
if __name__ == "__main__":
    trends = trend_service.get_trending_topics()
    for trend in trends:
        print(f"Source: {trend['source']}, Topic: {trend['topic']}")
        print(f"Blog Prompt: {trend_service.generate_blog_topic(trend)}")
        print("---")
