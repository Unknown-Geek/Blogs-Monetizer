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

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path)

# Adjust path for imports if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the automation_service
try:
    from services.automation_service import automation_service
except ImportError as e:
    print(f"Error importing automation_service: {e}")
    
    # Try an alternative approach
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "automation_service",
            os.path.join(current_dir, "services", "automation_service.py")
        )
        automation_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(automation_module)
        automation_service = automation_module.automation_service
    except Exception as e2:
        print(f"Error: Could not import automation_service. {e2}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Autonomous Blog Generator")    parser.add_argument('--config', type=str, help='Path to config JSON file')
    parser.add_argument('--run-once', action='store_true', help='Run once and exit')
    parser.add_argument('--schedule', action='store_true', help='Run on a schedule')
    parser.add_argument('--posts-per-day', type=int, help='Number of posts per day')
    parser.add_argument('--sources', type=str, help='Comma-separated list of trend sources (news)')
    parser.add_argument('--category', type=str, help='Comma-separated list of news categories')
    parser.add_argument('--min-seo', type=int, help='Minimum SEO score (0-100)')
    parser.add_argument('--social', action='store_true', help='Enable social sharing')
    parser.add_argument('--no-social', action='store_false', dest='social', help='Disable social sharing')
    parser.add_argument('--status', action='store_true', help='Show status and exit')
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
    config_updates = {}
    
    if args.posts_per_day is not None:
        config_updates['posts_per_day'] = args.posts_per_day
    
    if args.sources:
        config_updates['trending_sources'] = args.sources.split(',')
    
    if args.category:
        config_updates['categories'] = args.category.split(',')
    
    if args.min_seo is not None:
        config_updates['min_seo_score'] = args.min_seo
    
    if args.social is not None:
        config_updates['social_sharing'] = args.social
    
    # Apply config updates if any
    if config_updates:
        automation_service.update_config(config_updates)
    
    # Show status and exit if requested
    if args.status:
        logs = automation_service.load_logs()
        recent_logs = logs[-5:] if logs else []
        
        print("\nAutonomous Blog Generator - Status")
        print("----------------------------------")
        print(f"Running: {'Yes' if automation_service.running else 'No'}")
        print(f"Last post: {automation_service.last_post_time.isoformat() if automation_service.last_post_time else 'Never'}")
        
        if automation_service.running:
            next_times = automation_service.get_next_scheduled_times(3)
            print(f"Next scheduled posts: {', '.join(next_times)}")
        
        print(f"\nTotal posts: {len(logs)}")
        print(f"Recent activity:")
        
        for log in recent_logs:
            status_symbol = "✓" if log.get("status") == "success" else "✗"
            time_str = log.get("timestamp", "unknown")[:16]  # Just date and time
            topic = log.get("topic", {}).get("topic", "Unknown topic")
            print(f"{status_symbol} {time_str} - {topic[:60]}")
        
        return
    
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
                print(f"Title: {result.get('title', 'Untitled')}")
                print(f"SEO Score: {result.get('seo_score', 'N/A')}")
                print(f"Word Count: {result.get('word_count', 'N/A')}")
                
                if 'publish_result' in result and 'url' in result['publish_result']:
                    print(f"Published URL: {result['publish_result']['url']}")
                
                if 'social_sharing_result' in result:
                    print("Shared on social media:")
                    for platform, platform_result in result['social_sharing_result'].items():
                        status = "Success" if platform_result.get("success", False) else "Failed"
                        print(f"  - {platform}: {status}")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                
                # Show more detailed error if available
                if 'publish_error' in result:
                    print(f"Publishing error: {result['publish_error']}")
                if 'content_error' in result:
                    print(f"Content generation error: {result['content_error']}")
                if 'image_error' in result:
                    print(f"Image generation error: {result['image_error']}")
        
        except Exception as e:
            print(f"Error during execution: {e}")
    
    elif args.schedule:
        print(f"\nStarting scheduled blog generation ({automation_service.config['posts_per_day']} posts per day)...")
        print("Press Ctrl+C to stop")
        
        try:
            automation_service.run()
        except KeyboardInterrupt:
            print("\nStopping scheduled blog generation...")
            automation_service.stop()
        except Exception as e:
            print(f"Error during scheduled execution: {e}")
    
    else:
        # If no action specified, show help
        parser.print_help()

if __name__ == "__main__":
    main()
