#!/usr/bin/env python
"""
Utility to convert service-account.json to an environment variable format.

This script reads your service-account.json file and outputs the contents
in a format that can be added to your .env file or set as an environment
variable in your production environment.
"""
import os
import json
import sys

def convert_service_account_to_env():    # Get the path to the service account file
    main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    service_account_file = os.path.join(main_dir, "service-account.json")
    template_file = os.path.join(main_dir, "templates", "service-account.json.template")
    
    # Check if the file exists
    if not os.path.exists(service_account_file):
        print(f"Error: Service account file not found at {service_account_file}")
        return False
    
    try:
        # Read the service account file
        with open(service_account_file, 'r') as f:
            service_account_json = json.load(f)
        
        # Convert to a single line JSON string
        service_account_str = json.dumps(service_account_json)
        
        # Output the environment variable
        print("\n=== Add this to your .env file or set as environment variable ===\n")
        print(f"GOOGLE_SERVICE_ACCOUNT_INFO='{service_account_str}'")
        print("\n=== OR for Bash/Linux environments ===\n")
        print("export GOOGLE_SERVICE_ACCOUNT_INFO='", end="")
        print(service_account_str, end="'\n")
        print("\n=== OR for Windows Command Prompt ===\n")
        print("set GOOGLE_SERVICE_ACCOUNT_INFO=", end="")
        print(service_account_str)
        print("\n=== OR for PowerShell ===\n")
        print("$env:GOOGLE_SERVICE_ACCOUNT_INFO='", end="")
        print(service_account_str, end="'\n")
        return True
        
    except Exception as e:
        print(f"Error: Failed to convert service account file: {str(e)}")
        return False

if __name__ == "__main__":
    convert_service_account_to_env()
