#!/usr/bin/env python
"""
Heartbeat Monitoring Script
---------------------------
This script checks the status of the blog generation heartbeat.
It can also be used to enable/disable the heartbeat mechanism.
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime, timedelta

def check_heartbeat_status(server_url):
    """Check the status of the heartbeat"""
    try:
        response = requests.get(f"{server_url}/status")
        response.raise_for_status()
        status = response.json()
        
        print("\nHeartbeat Status:")
        print("----------------")
        print(f"Heartbeat Running: {status['heartbeat_running']}")
        print(f"Heartbeat Interval: {status['heartbeat_interval_minutes']} minutes")
        
        if status['last_blog_generation']:
            last_gen = datetime.fromisoformat(status['last_blog_generation'])
            current = datetime.fromisoformat(status['current_time'])
            time_since = current - last_gen
            print(f"Last Blog Generation: {last_gen.strftime('%Y-%m-%d %H:%M:%S')} ({time_since.total_seconds() / 60:.1f} minutes ago)")
            
            # Calculate next expected generation
            next_gen = last_gen + timedelta(minutes=status['heartbeat_interval_minutes'])
            time_until = next_gen - current
            if time_until.total_seconds() > 0:
                print(f"Next Blog Generation: {next_gen.strftime('%Y-%m-%d %H:%M:%S')} (in {time_until.total_seconds() / 60:.1f} minutes)")
            else:
                print(f"Next Blog Generation: Due now")
        else:
            print("Last Blog Generation: None (no blogs generated yet)")
        
        return True
    except Exception as e:
        print(f"Error checking heartbeat status: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Heartbeat Monitoring Tool")
    parser.add_argument('--server', type=str, default="http://localhost:7860", 
                        help='Server URL (default: http://localhost:7860)')
    parser.add_argument('--status', action='store_true',
                        help='Check heartbeat status')
    parser.add_argument('--generate', action='store_true',
                        help='Trigger blog generation manually')
    
    args = parser.parse_args()
    
    if args.status:
        check_heartbeat_status(args.server)
    elif args.generate:
        try:
            print("Triggering blog generation...")
            response = requests.get(args.server)
            response.raise_for_status()
            result = response.json()
            print("Blog generation triggered successfully")
            if "message" in result:
                print(f"Result: {result['message']}")
        except Exception as e:
            print(f"Error triggering blog generation: {str(e)}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
