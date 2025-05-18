#!/usr/bin/env python
"""
Environment Variable Helper Script

This script helps set up the necessary environment variables for different deployment scenarios.
It can extract necessary credentials from service account JSON files and prepare them
for various deployment environments.

Usage:
  - Development environment: Creates a .env file with variables
  - Production environment: Outputs commands to set environment variables
"""
import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

def extract_service_account():
    """Extract service account information into environment variables"""
    main_dir = Path(__file__).parent.parent
    service_account_path = main_dir / "service-account.json"
    template_path = main_dir / "templates" / "service-account.json.template"
    
    if not service_account_path.exists():
        print(f"Error: Service account file not found at {service_account_path}")
        return None
    
    try:
        with open(service_account_path, 'r') as f:
            service_account = json.load(f)
        
        # Extract key fields
        return {
            "GOOGLE_SERVICE_ACCOUNT_INFO": json.dumps(service_account),
            "GA_CLIENT_EMAIL": service_account.get("client_email", ""),
            "GA_PROJECT_ID": service_account.get("project_id", ""),
            "GA_PRIVATE_KEY_ID": service_account.get("private_key_id", ""),
            "GA_CLIENT_ID": service_account.get("client_id", ""),
        }
    except Exception as e:
        print(f"Error reading service account file: {e}")
        return None

def update_env_file(env_vars):
    """Update the .env file with the specified variables"""
    env_path = Path(__file__).parent.parent / ".env"
    
    # Load existing vars
    existing_vars = {}
    if env_path.exists():
        load_dotenv(env_path)
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    existing_vars[key] = value
    
    # Update with new vars
    existing_vars.update(env_vars)
    
    # Write back to file
    with open(env_path, 'w') as f:
        for key, value in existing_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"Updated .env file with {len(env_vars)} variables")

def output_cloud_commands(env_vars, platform="general"):
    """Output commands to set environment variables in cloud platforms"""
    print(f"\n=== Commands to set environment variables for {platform.upper()} ===\n")
    
    if platform == "heroku":
        for key, value in env_vars.items():
            # Quote the value if it contains spaces or special characters
            if " " in value or ";" in value or "," in value:
                print(f'heroku config:set {key}="{value}"')
            else:
                print(f"heroku config:set {key}={value}")
    
    elif platform == "vercel":
        for key, value in env_vars.items():
            print(f'vercel env add {key} "{value}"')
    
    elif platform == "netlify":
        for key, value in env_vars.items():
            print(f'netlify env:set {key} "{value}"')
    
    elif platform == "docker":
        print("# Add these environment variables to your docker command:")
        for key, value in env_vars.items():
            print(f'  -e {key}="{value}" \\')
    
    elif platform == "github":
        print("# Add these as GitHub repository secrets:")
        for key, value in env_vars.items():
            print(f'Name: {key}')
            print(f'Value: {value}')
            print("---")
    
    else:  # General bash/powershell export commands
        print("# For Linux/macOS (Bash):")
        for key, value in env_vars.items():
            print(f'export {key}="{value}"')
        
        print("\n# For Windows (PowerShell):")
        for key, value in env_vars.items():
            print(f'$env:{key}="{value}"')

def main():
    parser = argparse.ArgumentParser(description="Environment Variable Helper")
    parser.add_argument("--mode", choices=["dev", "prod"], default="dev",
                        help="Development mode (update .env) or production mode (output commands)")
    parser.add_argument("--platform", choices=["general", "heroku", "vercel", "netlify", "docker", "github"], 
                        default="general", help="Platform-specific commands in production mode")
    args = parser.parse_args()
    
    # Extract service account variables
    service_account_vars = extract_service_account()
    if not service_account_vars:
        print("Failed to extract service account information.")
        return
    
    # Set environment variables based on mode
    if args.mode == "dev":
        update_env_file(service_account_vars)
    else:
        output_cloud_commands(service_account_vars, args.platform)

if __name__ == "__main__":
    main()
