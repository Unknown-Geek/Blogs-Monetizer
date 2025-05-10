"""
Environment validation module for Monetize-blogs application.
Checks that all required environment variables are set.
"""
import os
import sys
from typing import List, Dict, Tuple

def check_environment_variables() -> Tuple[bool, List[str]]:
    """
    Check that all required environment variables are set.
    
    Returns:
        Tuple of (is_valid, missing_vars)
    """
    required_vars = {
        "Google Analytics": [
            "GA_MEASUREMENT_ID",
            "GA_CLIENT_EMAIL",
            "GA_PRIVATE_KEY",
            "GA_PROJECT_ID"
        ],
        "Blogger": [
            "BLOGGER_ID",
            "BLOGGER_CLIENT_ID", 
            "BLOGGER_CLIENT_SECRET",
            "BLOGGER_REFRESH_TOKEN"
        ],
        "API Keys": [
            "GEMINI_API_KEY",
            "NEWS_API_KEY"
        ],
        "Twitter": [
            "TWITTER_BEARER_TOKEN"
        ]
    }
    
    # Optional variables that enhance functionality but aren't strictly required
    optional_vars = [
        "GA_PROPERTY_ID", "GA_PRIVATE_KEY_ID", "GA_CLIENT_ID",
        "TWITTER_API_KEY", "TWITTER_API_SECRET", 
        "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET"
    ]
    
    missing_vars = []
    
    # Check required vars
    for category, vars_list in required_vars.items():
        for var in vars_list:
            if not os.environ.get(var):
                missing_vars.append(var)
    
    # Return results
    return len(missing_vars) == 0, missing_vars

def print_environment_status():
    """Print the status of environment variables"""
    is_valid, missing_vars = check_environment_variables()
    
    print("\n=== Monetize-blogs Environment Status ===")
    
    if is_valid:
        print("✅ All required environment variables are set")
    else:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or in your deployment environment.")
        print("See SETUP-GUIDE.md for details on obtaining these credentials.")
    
    # Check if running in a Hugging Face Space
    if os.environ.get("SPACE_ID"):
        print("\n🚀 Running in Hugging Face Spaces environment")
        
    print("\n=========================================")

if __name__ == "__main__":
    print_environment_status()
