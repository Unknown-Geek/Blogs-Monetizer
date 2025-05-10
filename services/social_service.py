import os
import tweepy
import json
from typing import Dict, Optional, List
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class SocialService:
    """Service for sharing blog posts on Twitter"""
    
    def __init__(self):
        # Twitter credentials
        self.twitter_bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "")
        self.twitter_api_key = os.environ.get("TWITTER_API_KEY", "")
        self.twitter_api_secret = os.environ.get("TWITTER_API_SECRET", "")
        self.twitter_access_token = os.environ.get("TWITTER_ACCESS_TOKEN", "")
        self.twitter_access_secret = os.environ.get("TWITTER_ACCESS_SECRET", "")
        
        # Create log directory
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.sharing_log = os.path.join(self.log_dir, "social_sharing.json")
    
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
            
            result = {
                "success": True,
                "platform": "twitter",
                "id": response.data["id"],
                "text": message,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log the share
            self._log_share(result)
            
            return result
        
        except Exception as e:
            error_result = {
                "success": False,
                "platform": "twitter",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self._log_share(error_result)
            return error_result
    
    def share_across_platforms(self, message: str, link: Optional[str] = None, platforms: List[str] = None) -> Dict:
        """
        Share content on Twitter (other platforms removed)
        
        Args:
            message: The message to share
            link: Optional link to include (not used for Twitter)
            platforms: List of platforms to share on (only Twitter is supported)
            
        Returns:
            Dict with results for Twitter
        """
        results = {}
        
        # Only Twitter is now supported, so we'll share on Twitter regardless of the platforms list
        twitter_message = message
        if len(message) > 280:
            twitter_message = message[:277] + "..."
        results["twitter"] = self.share_on_twitter(twitter_message)
        
        return results
    
    def _log_share(self, share_data: Dict) -> None:
        """Log a social media share to a file"""
        try:
            # Load existing logs
            logs = []
            if os.path.exists(self.sharing_log):
                with open(self.sharing_log, 'r') as f:
                    logs = json.load(f)
            
            # Add new log entry
            logs.append(share_data)
            
            # Save logs
            with open(self.sharing_log, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Error logging social share: {str(e)}")
    
    def get_share_history(self, platform: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Get history of social media shares"""
        try:
            if not os.path.exists(self.sharing_log):
                return []
                
            with open(self.sharing_log, 'r') as f:
                logs = json.load(f)
            
            # Filter by platform if specified
            if platform:
                logs = [log for log in logs if log.get("platform") == platform]
                
            # Return most recent logs
            return logs[-limit:]
            
        except Exception as e:
            print(f"Error getting share history: {str(e)}")
            return []

social_service = SocialService()
