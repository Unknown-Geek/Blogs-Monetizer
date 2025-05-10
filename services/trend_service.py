import requests
import json
import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class TrendService:
    """Service to detect trending topics for blog generation"""
    
    def __init__(self):
        self.google_trends_api_url = "https://trends.google.com/trends/api/dailytrends"
        self.twitter_api_url = "https://api.twitter.com/2/tweets/search/recent"
        self.twitter_bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "YOUR_TWITTER_BEARER_TOKEN")
        self.news_api_url = "https://newsapi.org/v2/top-headlines"
        self.news_api_key = os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY")
        
    def get_google_trends(self, geo="US") -> List[Dict]:
        """Fetch trending searches from Google Trends"""
        params = {
            "geo": geo,
            "hl": "en-US",
            "ns": 15
        }
        
        try:
            response = requests.get(self.google_trends_api_url, params=params)
            # Google Trends API returns a strange prefix before the JSON data
            json_data = response.text[5:]  # Remove ")]}'"
            data = json.loads(json_data)
            
            trending_searches = []
            for topic in data.get("default", {}).get("trendingSearchesDays", [])[0].get("trendingSearches", []):
                trending_searches.append({
                    "title": topic.get("title", {}).get("query", ""),
                    "traffic": topic.get("formattedTraffic", ""),
                    "related_topics": [item.get("query", "") for item in topic.get("relatedQueries", [])]
                })
            
            return trending_searches
        
        except Exception as e:
            print(f"Error fetching Google Trends: {e}")
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
    
    def get_news_headlines(self, country="us", category="technology") -> List[Dict]:
        """Fetch top news headlines"""
        params = {
            "country": country,
            "category": category,
            "apiKey": self.news_api_key
        }
        
        try:
            response = requests.get(self.news_api_url, params=params)
            data = response.json()
            
            headlines = []
            for article in data.get("articles", []):
                headlines.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "url": article.get("url", "")
                })
            
            return headlines
        
        except Exception as e:
            print(f"Error fetching news headlines: {e}")
            return []
    
    def get_trending_topics(self, sources=["google", "news"], count=5) -> List[Dict]:
        """Get trending topics from multiple sources"""
        all_trends = []
        
        if "google" in sources:
            google_trends = self.get_google_trends()
            all_trends.extend([{"source": "google", "topic": trend["title"]} for trend in google_trends])
        
        if "twitter" in sources:
            twitter_trends = self.get_twitter_trends()
            all_trends.extend([{"source": "twitter", "topic": trend["text"]} for trend in twitter_trends])
        
        if "news" in sources:
            news_trends = self.get_news_headlines()
            all_trends.extend([{"source": "news", "topic": headline["title"]} for headline in news_trends])
        
        # Return the top trends
        return all_trends[:count]
    
    def generate_blog_topic(self, trend: Dict) -> str:
        """Convert a trend into a blog topic prompt"""
        source = trend.get("source", "")
        topic = trend.get("topic", "")
        
        if source == "google":
            return f"Write an informative blog post about {topic}, including recent developments and why it's trending"
        
        elif source == "twitter":
            return f"Create an engaging blog post discussing {topic} that's currently trending on social media"
        
        elif source == "news":
            return f"Write a comprehensive blog post analyzing the recent news: {topic}"
        
        else:
            return f"Write a blog post about the trending topic: {topic}"

trend_service = TrendService()

# Usage example
if __name__ == "__main__":
    trends = trend_service.get_trending_topics()
    for trend in trends:
        print(f"Source: {trend['source']}, Topic: {trend['topic']}")
        print(f"Blog Prompt: {trend_service.generate_blog_topic(trend)}")
        print("---")
