"""
Service to detect trending topics for automatic blog generation
"""
import requests
import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class TrendService:
    """Service to detect trending topics for blog generation"""
      def __init__(self):
        self.google_trends_api_url = "https://trends.google.com/trends/api/dailytrends"
        self.news_api_url = "https://newsapi.org/v2/top-headlines"
        self.news_api_key = os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY")
        
        # Create a cache directory to store trend data
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Define cache files
        self.google_trends_cache = os.path.join(self.cache_dir, "google_trends.json")
        self.news_cache = os.path.join(self.cache_dir, "news_trends.json")
        
        # List of terms that suggest news about people
        self.people_indicators = [
            "says", "said", "claimed", "announced", "revealed", "confirms", 
            "denies", "weighs in", "responds", "criticizes", "praises",
            "speaks out", "interview", "statement", "comments", "warns",
            "accuses", "defends", "slams", "hits back", "addresses",
            "reaction", "opinion", "weighs in", "tells", "asks",
            "explains", "expresses", "suggests", "argues", "interview with"
        ]
        
        # Common first and last names that might indicate people-focused articles
        self.common_names = ["Trump", "Biden", "Musk", "Bezos", "Gates", "Zuckerberg", 
                            "Harris", "Johnson", "Smith", "Williams", "Brown", "Jones",
                            "Miller", "Davis", "Dimon", "Cook", "Nadella", "Pichai"]
        
    def get_google_trends(self, geo="US") -> List[Dict]:
        """Fetch trending searches from Google Trends with caching"""
        # Check for cached data first (not older than 6 hours)
        cached_data = self._load_cached_data(self.google_trends_cache, max_age_hours=6)
        if cached_data:
            return cached_data
        
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
            for trend_day in data.get("default", {}).get("trendingSearchesDays", []):
                date = trend_day.get("date", "")
                for trend in trend_day.get("trendingSearches", []):
                    title = trend.get("title", {}).get("query", "")
                    related_queries = []
                    for related in trend.get("relatedQueries", []):
                        related_queries.append(related.get("query", ""))
                        
                    trending_searches.append({
                        "title": title,
                        "related": related_queries,
                        "date": date
                    })
            
            # Save to cache
            self._save_cached_data(self.google_trends_cache, trending_searches)
            
            return trending_searches
            
        except Exception as e:
            print(f"Error fetching Google Trends: {e}")
            # Try to use cached data regardless of age in case of error
            cached_data = self._load_cached_data(self.google_trends_cache, max_age_hours=24)
            if cached_data:
                return cached_data
            return []
    
    def get_news_headlines(self, country="us", category=None) -> List[Dict]:
        """
        Fetch latest news headlines from News API
        
        Args:
            country: Two-letter country code
            category: Optional category (business, technology, science, health, etc.)
        """
        # Determine cache file based on category
        category_str = category if category else "general"
        news_cache_file = os.path.join(self.cache_dir, f"news_{country}_{category_str}.json")
        
        # Check for cached data first (not older than 2 hours)
        cached_data = self._load_cached_data(news_cache_file, max_age_hours=2)
        if cached_data:
            return cached_data
        
        # Build API parameters
        params = {
            "country": country,
            "apiKey": self.news_api_key,
            "pageSize": 20
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
            
    def _is_about_person(self, title: str, description: str = "") -> bool:
        """
        Detect if a news article is primarily about a person
        
        Args:
            title: The article title
            description: The article description (optional)
            
        Returns:
            True if the article appears to be primarily about a person
        """
        # Ensure title and description are strings
        title = str(title) if title is not None else ""
        description = str(description) if description is not None else ""
        
        # Combine title and description for analysis
        full_text = (title + " " + description).lower()
        
        # Check for names of prominent people
        for name in self.common_names:
            if name.lower() in full_text:
                return True
        
        # Check for verbs and patterns that suggest people-focused content
        for indicator in self.people_indicators:
            if indicator.lower() in full_text:
                return True
        
        # Check for common patterns that suggest quotes or statements
        quote_patterns = ["'s ", " says", "'", """, """, "says", "said"]
        for pattern in quote_patterns:
            if pattern in full_text:
                return True
        
        return False
    
    def get_trending_topics(self, sources=["news"], count=5, categories=None, filter_people=True) -> List[Dict]:
        """
        Get trending topics from multiple sources
        
        Args:
            sources: List of sources to check ("news")
            count: Number of trends to return
            categories: Optional list of news categories to include
            filter_people: Whether to filter out news primarily about people
            
        Returns:
            List of trending topics
        """
        all_trends = []
        
        if "news" in sources:
            # Use specified categories or default to a variety
            news_categories = categories or ["technology", "business", "science", "health"]
            for category in news_categories:
                news_trends = self.get_news_headlines(category=category)
                for headline in news_trends:
                    # Skip news about people if filter is enabled
                    if filter_people and self._is_about_person(
                        headline["title"], 
                        headline.get("description", "")
                    ):
                        continue
                        
                    all_trends.append({
                        "source": "news",
                        "topic": headline["title"],
                        "category": category,
                        "description": headline.get("description", ""),
                        "news_source": headline.get("source", ""),
                        "url": headline.get("url", ""),
                        "publishedAt": headline.get("publishedAt", "")
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

# Create singleton instance
trend_service = TrendService()

# Usage example
if __name__ == "__main__":
    trends = trend_service.get_trending_topics()
    for trend in trends:
        print(f"Source: {trend['source']}, Topic: {trend['topic']}")
        print(f"Blog Prompt: {trend_service.generate_blog_topic(trend)}")
        print("---")
