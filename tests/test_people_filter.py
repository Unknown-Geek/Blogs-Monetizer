"""
Test script to compare news filtering with and without the people filter
"""
import sys
import os
from pprint import pprint

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.trend_service import trend_service

def test_people_filter():
    """Test the people filter functionality"""
    # Get topics with and without people filtering
    topics_with_people = trend_service.get_trending_topics(filter_people=False, count=15)
    topics_without_people = trend_service.get_trending_topics(filter_people=True, count=15)
    
    # Count the results
    print(f'Topics with people filtering OFF: {len(topics_with_people)}')
    print(f'Topics with people filtering ON: {len(topics_without_people)}')
    
    # Find topics that were filtered out
    filtered_out = []
    for topic in topics_with_people:
        if not any(t.get('topic') == topic.get('topic') for t in topics_without_people):
            filtered_out.append(topic)
    
    # Display filtered out topics
    print('\nTOPICS ABOUT PEOPLE (filtered out):')
    for i, topic in enumerate(filtered_out, 1):
        print(f"{i}. {topic.get('topic')}")
        if topic.get('description'):
            print(f"   Description: {topic.get('description')}")
        print(f"   Category: {topic.get('category', 'N/A')}")
        print()
    
    # Display remaining topics
    print('\nREMAINING TOPICS (not about people):')
    for i, topic in enumerate(topics_without_people, 1):
        print(f"{i}. {topic.get('topic')}")
        if topic.get('description'):
            desc = topic.get('description')
            if desc:
                print(f"   Description: {desc[:100]}...")
        print(f"   Category: {topic.get('category', 'N/A')}")
        print()

if __name__ == "__main__":
    test_people_filter()
