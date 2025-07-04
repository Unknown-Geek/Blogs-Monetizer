"""
Test the trend service to make sure it's working properly.
This will:
1. Get trending topics from different sources
2. Generate blog topic prompts based on them
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to sys.path to allow importing from services
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the trend service
from services.trend_service import trend_service

def test_trend_service():
    print("Testing Trend Service...")
    print("=" * 80)
    
    # Test with news sources
    sources = ["news"]
    print(f"Getting trends from sources: {sources}")
    
    trends = trend_service.get_trending_topics(sources=sources, count=10)
    print(f"Found {len(trends)} trending topics")
    print("-" * 80)
    
    # Print and test each trend
    for i, trend in enumerate(trends):
        print(f"Trend #{i+1}: {trend.get('source')} - {trend.get('topic')}")
        
        # Generate a blog prompt
        prompt = trend_service.generate_blog_topic(trend)
        print(f"Blog prompt: {prompt[:100]}...")
        print("-" * 80)
    
    # Test caching
    print("\nTesting trend caching...")
    start_time = datetime.now()
    cached_trends = trend_service.get_trending_topics(sources=sources, count=10)
    end_time = datetime.now()
    
    elapsed_ms = (end_time - start_time).total_seconds() * 1000
    print(f"Cached retrieval took {elapsed_ms:.2f}ms")
    print(f"Retrieved {len(cached_trends)} cached trends")
    
    # Save the results to a file for inspection
    results = {
        "timestamp": datetime.now().isoformat(),
        "trends": trends,
        "blog_prompts": [trend_service.generate_blog_topic(trend) for trend in trends]
    }
    
    output_dir = os.path.join(parent_dir, "logs")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "trend_test_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nTest results saved to logs/trend_test_results.json")
    print("=" * 80)

if __name__ == "__main__":
    test_trend_service()
