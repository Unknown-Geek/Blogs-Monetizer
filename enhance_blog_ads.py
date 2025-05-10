"""
This script analyzes existing blog posts and enhances them with improved ad displays.
It can be run periodically to update ad placements and ensure they're visible.
"""
import os
import sys
import json
import requests
import re
from datetime import datetime

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(parent_dir))

from services import blog_service, ad_service

def enhance_blog_ads():
    """Analyze and enhance existing blog posts with improved ad displays."""
    print("=" * 80)
    print("BLOG AD ENHANCEMENT TOOL")
    print("=" * 80)
    
    # 1. Get a list of recent posts
    print("\n1. Fetching recent blog posts...")
    try:
        blogs = blog_service.get_recent_posts(max_results=5)
        if not blogs:
            print("No recent blogs found.")
            return False
        
        print(f"Found {len(blogs)} recent blog posts.")
    except Exception as e:
        print(f"ERROR: Failed to fetch blogs: {str(e)}")
        return False
    
    # 2. Process each blog
    print("\n2. Processing blog posts...")
    success_count = 0
    
    for i, blog in enumerate(blogs):
        try:
            print(f"\nProcessing blog: {blog.get('title', 'Unknown')[:50]}...")
            
            # Get the content
            content = blog.get("content", "")
            
            # Check if content already has ads
            ad_count = 0
            for ad_format in ad_service.ad_formats:
                ad_count += content.count(f'class="ad-container {ad_format}"')
            
            if ad_count > 0:
                print(f"  - Blog already has {ad_count} ads. Skipping.")
                continue
            
            # Look for ad placement hooks
            hook_count = 0
            for ad_format in ad_service.ad_formats:
                hook_count += content.count(f'<!-- AD_PLACEMENT: {ad_format} -->')
            
            # Determine if we need to add ad hooks or just convert existing ones
            if hook_count == 0:
                print("  - No ad hooks found. Adding new ad placements...")
                # Extract text content without HTML for better content analysis
                text_content = re.sub(r'<[^>]+>', '', content)
                word_count = len(text_content.split())
                
                # Gather content info for ad strategy
                content_info = {
                    "topic": blog.get("title", ""),
                    "word_count": word_count,
                    "category": blog.get("labels", ["general"])[0] if blog.get("labels") else "general",
                    "audience": "general"
                }
                
                # Generate ad strategy
                ad_strategy = ad_service.generate_ad_strategy(content_info)
                print(f"  - Ad strategy generated: {ad_strategy['density']} density")
                
                # Prepare content with ad placement hooks
                content_with_hooks = ad_service.prepare_content_for_ads(
                    content, 
                    ad_density=ad_strategy["density"]
                )
                
                # Convert hooks to actual ads
                enhanced_content = ad_service.insert_ads_into_content(content_with_hooks, network="google")
            else:
                print(f"  - Found {hook_count} ad hooks. Converting to visible ads...")
                enhanced_content = ad_service.insert_ads_into_content(content, network="google")
            
            # Update the blog post
            success = blog_service.update_post(
                post_id=blog.get("id"),
                content=enhanced_content
            )
            
            if success:
                print("  - Blog updated successfully!")
                success_count += 1
            else:
                print("  - Failed to update blog.")
                
        except Exception as e:
            print(f"  - ERROR processing blog: {str(e)}")
    
    # 3. Display summary
    print("\n3. Enhancement Summary")
    print(f"  - Successfully processed {success_count} out of {len(blogs)} blogs.")
    
    return success_count > 0

if __name__ == "__main__":
    success = enhance_blog_ads()
    print("\n" + "=" * 80)
    print(f"Process {'completed successfully' if success else 'failed'}")
    print("=" * 80)
