import os
import json
from typing import Dict, Optional, List
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class SocialService:
    """Service that logs social sharing attempts (all sharing functionality disabled)"""
    
    def __init__(self):
        # Create log directory
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.sharing_log = os.path.join(self.log_dir, "social_sharing.json")
        
        # Log startup
        print("Social Service initialized (all sharing disabled)")
    
    def share_across_platforms(self, message: str, link: Optional[str] = None, platforms: List[str] = None) -> Dict:
        """
        Log sharing request but do not actually share content (all sharing disabled)
        
        Args:
            message: The message that would have been shared
            link: Optional link that would have been included
            platforms: List of platforms that would have been used
            
        Returns:
            Dict with mock results
        """
        # Log that sharing was attempted
        result = {
            "success": False,
            "error": "Social sharing is completely disabled",
            "message_attempted": message,
            "link_attempted": link,
            "platforms_attempted": platforms,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log the attempt
        self._log_share(result)
        
        # Print a notification
        print("[DISABLED] Social sharing attempted but is completely disabled")
        
        return {"disabled": result}
    
    def _log_share(self, share_data: Dict) -> None:
        """Log a social media share attempt to a file"""
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
            print(f"Error logging social share attempt: {str(e)}")
    
    def get_share_history(self, platform: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Get history of social media share attempts"""
        try:
            if not os.path.exists(self.sharing_log):
                return []
                
            with open(self.sharing_log, 'r') as f:
                logs = json.load(f)
            
            # Filter by platform if specified (though all are disabled now)
            if platform:
                logs = [log for log in logs if log.get("platforms_attempted") and platform in log.get("platforms_attempted", [])]
                
            # Return most recent logs
            return logs[-limit:]
            
        except Exception as e:
            print(f"Error getting share history: {str(e)}")
            return []

# Create singleton instance
social_service = SocialService()
