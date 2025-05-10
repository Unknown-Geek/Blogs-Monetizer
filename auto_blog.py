#!/usr/bin/env python
"""
Autonomous Blog Generator
-------------------------
This script runs the autonomous blog generator that:
1. Finds trending topics
2. Generates blog content using AI
3. Creates matching images
4. Publishes to a blogging platform
5. Shares on social media
"""

import os
import sys
import argparse
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from the backend/.env file
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
dotenv_path = os.path.join(backend_dir, '.env')
load_dotenv(dotenv_path)

# Adjust path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.services.automation_service import automation_service
except ImportError:
    try:
        # Try alternative import path
        from services.automation_service import automation_service
    except ImportError:
        print("Error: Could not import automation_service. Check your directory structure.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Autonomous Blog Generator")
    parser.add_argument('--config', type=str, help='Path to config JSON file')
    parser.add_argument('--run-once', action='store_true', help='Run once and exit')
    parser.add_argument('--schedule', action='store_true', help='Run on a schedule')
    parser.add_argument('--posts-per-day', type=int, default=1, help='Number of posts per day')
    parser.add_argument('--sources', type=str, default='google,news', help='Comma-separated list of trend sources')
    args = parser.parse_args()
    
    # Load config from file if provided
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
                automation_service.config.update(config)
                print(f"Loaded configuration from {args.config}")
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Update config from command-line args
    if args.posts_per_day:
        automation_service.config['posts_per_day'] = args.posts_per_day
    
    if args.sources:
        automation_service.config['trending_sources'] = args.sources.split(',')
    
    # Display configuration
    print("\nAutonomous Blog Generator")
    print("------------------------")
    print(f"Configuration:")
    for key, value in automation_service.config.items():
        print(f"  {key}: {value}")
    
    # Run once or schedule
    if args.run_once:
        print("\nRunning blog generation once...")
        try:
            start_time = datetime.now()
            result = automation_service.generate_and_publish_blog()
            duration = datetime.now() - start_time
            
            print(f"\nBlog generation completed in {duration.total_seconds():.1f} seconds")
            print(f"Status: {result['status']}")
            
            if result['status'] == 'success':
                print(f"Topic: {result.get('topic', {}).get('topic', 'Unknown')}")
                print(f"SEO Score: {result.get('seo_score', 'N/A')}")
                if 'publish_result' in result and 'url' in result['publish_result']:
                    print(f"Published URL: {result['publish_result']['url']}")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"Error during execution: {e}")
    
    elif args.schedule:
        print(f"\nStarting scheduled blog generation ({automation_service.config['posts_per_day']} posts per day)...")
        try:
            automation_service.run()
        except KeyboardInterrupt:
            print("\nStopping scheduled blog generation...")
        except Exception as e:
            print(f"Error during scheduled execution: {e}")
    
    else:
        # If no action specified, show help
        parser.print_help()

if __name__ == "__main__":
    main()
