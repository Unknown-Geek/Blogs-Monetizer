import os
import tweepy
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class SocialService:
    """Service for sharing blog posts on social media platforms"""
    
    def __init__(self):
        self.twitter_bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "YOUR_TWITTER_BEARER_TOKEN")
        self.twitter_api_key = os.environ.get("TWITTER_API_KEY", "YOUR_TWITTER_API_KEY")
        self.twitter_api_secret = os.environ.get("TWITTER_API_SECRET", "YOUR_TWITTER_API_SECRET")
        self.twitter_access_token = os.environ.get("TWITTER_ACCESS_TOKEN", "YOUR_TWITTER_ACCESS_TOKEN")
        self.twitter_access_secret = os.environ.get("TWITTER_ACCESS_SECRET", "YOUR_TWITTER_ACCESS_SECRET")
    
    def share_on_twitter(self, message: str) -> Dict:
        """
        Share a message on Twitter
        
        Args:
            message: The message to tweet (max 280 chars)
        
        Returns:
            Dict containing response from Twitter API
        """
        # Truncate message if it's too long
        if len(message) > 280:
            message = message[:277] + "..."
        
        try:
            # Setup Twitter client - v2 API using OAuth 1.0a
            auth = tweepy.OAuth1UserHandler(
                self.twitter_api_key, 
                self.twitter_api_secret,
                self.twitter_access_token,
                self.twitter_access_secret
            )
            client = tweepy.Client(
                bearer_token=self.twitter_bearer_token,
                consumer_key=self.twitter_api_key,
                consumer_secret=self.twitter_api_secret,
                access_token=self.twitter_access_token,
                access_token_secret=self.twitter_access_secret
            )
            
            # Create tweet
            response = client.create_tweet(text=message)
            
            return {
                "success": True,
                "id": response.data["id"],
                "text": message
            }
        
        except Exception as e:
            print(f"Error posting to Twitter: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def share_on_facebook(self, message: str, link: Optional[str] = None) -> Dict:
        """
        Share a message on Facebook (placeholder for future implementation)
        
        Args:
            message: The message to post
            link: Optional link to include
            
        Returns:
            Dict containing response
        """
        # Placeholder for Facebook API integration
        return {
            "success": False,
            "error": "Facebook sharing not yet implemented"
        }
    
    def share_on_linkedin(self, message: str, link: Optional[str] = None) -> Dict:
        """
        Share a message on LinkedIn (placeholder for future implementation)
        
        Args:
            message: The message to post
            link: Optional link to include
            
        Returns:
            Dict containing response
        """
        # Placeholder for LinkedIn API integration
        return {
            "success": False,
            "error": "LinkedIn sharing not yet implemented"
        }

social_service = SocialService()
