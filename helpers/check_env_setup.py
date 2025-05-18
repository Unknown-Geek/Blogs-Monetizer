#!/usr/bin/env python3
"""
Check if environment variables for service account authentication are properly set.
This script is helpful to verify that credentials have been properly configured.
"""
import os
import sys
import json
from dotenv import load_dotenv

def main():
    """Check and validate environment variables for service account."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Check for service account info
    service_account_info = os.getenv('GOOGLE_SERVICE_ACCOUNT_INFO')
    client_email = os.getenv('GA_CLIENT_EMAIL')
    use_service_account = os.getenv('USE_SERVICE_ACCOUNT')
    
    print("Environment Variable Setup Check\n" + "="*30)
    
    # Check for service-account.json file
    main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    service_account_file = os.path.join(main_dir, "service-account.json")
    
    if os.path.exists(service_account_file):
        print("✓ Service account file found at:", service_account_file)
    else:
        print("✗ Service account file not found at:", service_account_file)
    
    # Check environment variables
    print("\nEnvironment Variables:")
    
    if service_account_info:
        try:
            # Validate JSON format
            json_data = json.loads(service_account_info)
            required_keys = ['client_email', 'private_key', 'project_id']
            
            # Check for required keys
            missing_keys = [key for key in required_keys if key not in json_data]
            
            if missing_keys:
                print("✗ GOOGLE_SERVICE_ACCOUNT_INFO is set but missing required keys:", 
                      ", ".join(missing_keys))
            else:
                print("✓ GOOGLE_SERVICE_ACCOUNT_INFO is properly set")
                
                # Check if client_email is consistent
                if client_email and client_email != json_data.get('client_email'):
                    print("⚠ Warning: GA_CLIENT_EMAIL doesn't match the email in GOOGLE_SERVICE_ACCOUNT_INFO")
                
        except json.JSONDecodeError:
            print("✗ GOOGLE_SERVICE_ACCOUNT_INFO is set but contains invalid JSON")
    else:
        print("✗ GOOGLE_SERVICE_ACCOUNT_INFO is not set")
    
    if client_email:
        print("✓ GA_CLIENT_EMAIL is set to:", client_email)
    else:
        print("✗ GA_CLIENT_EMAIL is not set")
    
    if use_service_account:
        print(f"✓ USE_SERVICE_ACCOUNT is set to: {use_service_account}")
    else:
        print("⚠ USE_SERVICE_ACCOUNT is not set (defaults to using service account if available)")
    
    # Print summary
    print("\nSummary:")
    if service_account_info or os.path.exists(service_account_file):
        print("✓ Authentication credentials are available")
        if service_account_info:
            print("  - Using environment-based authentication (recommended for production)")
        else:
            print("  - Using file-based authentication (recommended for development only)")
    else:
        print("✗ No authentication credentials found")
        print("  - See docs/google_sheets_setup.md for setup instructions")
    
    print("\nFor more information on environment setup, see docs/environment_variables.md")
    
if __name__ == "__main__":
    main()
