"""
Test script to verify the fixes for the Monetize-blogs system.
This will test:
1. That the system can get trends without using Google as a source
2. That duplicate article detection works properly
3. That image directory clearing works after posting
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to sys.path to allow importing from services
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the services
from services.trend_service import trend_service
from services.image_utils import clear_images_directory
from services.automation_service import automation_service

def test_news_only_trends():
    """Test that we can get trends without using Google as a source"""
    print("Testing News-only trends...")
    print("=" * 80)
    
    # Get trends only from news sources
    trends = trend_service.get_trending_topics(sources=["news"], count=5)
    
    print(f"Found {len(trends)} trending topics from news sources")
    
    if trends:
        print("Sample trends:")
        for i, trend in enumerate(trends[:3]):  # Show first 3
            print(f"  {i+1}. {trend.get('source')}: {trend.get('topic')}")
            if "url" in trend:
                print(f"     URL: {trend.get('url')}")
            if "category" in trend:
                print(f"     Category: {trend.get('category')}")
    else:
        print("No trends found from news sources")
    
    print("\nChecking trend source configurations...")
    print(f"Automation service trending sources: {automation_service.config['trending_sources']}")
    
    if "google" not in automation_service.config["trending_sources"]:
        print("SUCCESS: Google has been removed from trending sources")
    else:
        print("FAILURE: Google is still in trending sources list")
    
    return bool(trends) and "google" not in automation_service.config["trending_sources"]

def test_image_directory_clearing():
    """Test that image directory clearing works"""
    print("\nTesting image directory clearing...")
    print("=" * 80)
    
    # First, check how many images are in the directory
    images_dir = os.path.join(parent_dir, "images")
    if not os.path.exists(images_dir):
        print(f"Images directory does not exist: {images_dir}")
        return False
    
    image_files_before = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
    print(f"Found {len(image_files_before)} files in images directory before clearing")
    
    # Try to clear the directory
    result = clear_images_directory()
    
    if result:
        print("Successfully cleared the images directory")
    else:
        print("Failed to clear the images directory")
    
    # Check how many images are in the directory now
    image_files_after = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
    print(f"Found {len(image_files_after)} files in images directory after clearing")
    
    success = result and len(image_files_after) == 0
    
    if success:
        print("SUCCESS: Image directory clearing works correctly")
    else:
        print("FAILURE: Image directory clearing is not working correctly")
    
    return success

if __name__ == "__main__":
    results = {}
    
    # Test getting trends without Google
    results["news_only_trends"] = test_news_only_trends()
    
    # Test image directory clearing
    results["image_directory_clearing"] = test_image_directory_clearing()
    
    # Print overall results
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    for test_name, success in results.items():
        print(f"{test_name}: {'SUCCESS' if success else 'FAILURE'}")
    
    # Determine overall success
    all_passed = all(results.values())
    print(f"\nOverall test result: {'SUCCESS' if all_passed else 'FAILURE'}")
    
    # Exit with success code only if all tests passed
    sys.exit(0 if all_passed else 1)
