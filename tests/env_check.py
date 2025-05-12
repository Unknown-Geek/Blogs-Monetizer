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
        ]
    }
    
    # Optional variables that enhance functionality but aren't strictly required
    optional_vars = [
        "GA_PROPERTY_ID", "GA_PRIVATE_KEY_ID", "GA_CLIENT_ID"
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
        print("✅ All required environment variables are set.")
    else:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
    
    print("\nUsing environment credentials:", is_valid)
    
    return is_valid

if __name__ == "__main__":
    # Print status and exit with appropriate code
    is_valid = print_environment_status()
    sys.exit(0 if is_valid else 1)
