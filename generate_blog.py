"""
Generate a sample blog post using the automated pipeline
"""
import os
import argparse
import sys
import shutil
import time
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.trend_service import trend_service
from services.blog_service import blog_service
from services.image_service import image_service
from services.seo_service import seo_service
from services.social_service import SocialService
from services.ad_service import ad_service

# Initialize social service
social_service = SocialService()

# Load environment variables
load_dotenv()

def get_trending_topic() -> Dict[str, Any]:
    """Get a trending topic from news sources"""
    topics = trend_service.get_trending_topics(sources=["news"], filter_people=True)
    return topics[0] if topics else {}

def get_trending_topics_list(count=5) -> List[Dict[str, Any]]:
    """Get a list of trending topics from news sources"""
    return trend_service.get_trending_topics(sources=["news"], count=count, filter_people=True)

def generate_blog_content(topic: Dict[str, Any]) -> Dict[str, Any]:
    """Generate blog content based on the trending topic"""
    prompt = trend_service.generate_blog_topic(topic)
    content = blog_service.generate_blog_content(prompt)
    return {"content": content}

def analyze_seo(content: str) -> Dict[str, Any]:
    """Analyze SEO metrics for the blog content"""
    seo_results = seo_service.analyze_seo(content)
    
    # Print summary
    print(f"SEO Score: {seo_results['score']}/100")
    print(f"Word count: {seo_results['word_count']} words")
    
    return seo_results

def monetize_content(content: str) -> str:
    """Add ad placements and affiliate products to the blog content"""
    content_info = {
        "word_count": len(content.split()),
        "topic": extract_blog_title(content),
        "content_type": "blog"
    }
    ad_strategy = ad_service.generate_ad_strategy(content_info)
    
    print(f"Ad strategy generated: {ad_strategy.get('strategy_name', 'N/A')}")
    
    prepared_content = ad_service.prepare_content_for_ads(content, ad_density=ad_strategy.get('density', 'medium'))
    monetized_content = ad_service.insert_ads_into_content(prepared_content, network=ad_strategy.get('primary_network', 'google'))
    
    print("Fetching affiliate products...")
    affiliate_products = ad_service.fetch_affiliate_products()
    
    if not affiliate_products:
        print("No affiliate products fetched. Skipping affiliate ads.")
        return monetized_content
        
    print(f"Fetched {len(affiliate_products)} affiliate products.")
    
    # Enhance affiliate products with images
    enriched_affiliate_products = []
    for product in affiliate_products:
        product_url = product.get("url")
        product_name = product.get("product_name", "Affiliate Product")
        if product_url:
            print(f"Attempting to fetch image for {product_name} from {product_url}")
            image_path = image_service.fetch_image_from_url(product_url, product_name)
            if image_path:
                product["image_path"] = image_path 
                print(f"Successfully fetched image for {product_name}: {image_path}")
            else:
                product["image_path"] = None
                print(f"Failed to fetch image for {product_name}")
        else:
            product["image_path"] = None
        enriched_affiliate_products.append(product)

    monetized_content = ad_service.insert_affiliate_ads(
        monetized_content, 
        enriched_affiliate_products,
        max_affiliate_ads=3
    )
    
    print(f"Added affiliate product links (with images if available).")
    
    estimated_revenue = ad_service.estimate_revenue(monetized_content, 10000)
    print(f"Estimated monthly revenue (10K views): ${estimated_revenue.get('estimated_revenue', {}).get('total', 0.0)}")
    
    return monetized_content

def extract_blog_title(content: str) -> str:
    """Extract the title from the blog content"""
    # Try to find an H1 tag first
    import re
    h1_match = re.search(r'<h1>(.*?)</h1>', content)
    if h1_match:
        title = h1_match.group(1)
        # Remove any HTML entities
        title = re.sub(r'&[a-zA-Z0-9#]+;', '', title)
        if len(title) > 50:
            title = title[:50] + "..."
        return title
        
    # Fallback to first line
    lines = content.strip().split("\n")
    title = lines[0].replace("#", "").strip()
    # Remove any HTML tags
    title = re.sub(r'<[^>]*>', '', title)
    if len(title) > 50:
        title = title[:50] + "..."
    return title

def generate_image(topic: Dict[str, Any], title: str) -> Dict[str, Any]:
    """Generate an image for the blog post"""
    prompt = f"A professional blog image related to {topic.get('topic', '')}"
    image_path = image_service.generate_image(prompt)
    
    # Create a result dictionary that matches what the rest of the code expects
    result = {
        "image_path": image_path,
        "keywords": prompt
    }
    
    return result

def generate_tags(content: str, topic: Dict[str, Any]) -> List[str]:
    """Generate tags/labels for the blog post"""
    # Get keywords from SEO analysis
    seo_results = seo_service.analyze_seo(content)
    keyword_list = list(seo_results.get('keywords', {}).keys())[:5]  # Get top 5 keywords
    
    # Add some standard tags
    category = topic.get("category", "")
    if category:
        keyword_list.append(category)
        
    source = topic.get("source", "")
    if source:
        keyword_list.append(source)
        
    # Add date tag (e.g., "May 2025")
    from datetime import datetime
    date_tag = datetime.now().strftime("%B %Y")
    keyword_list.append(date_tag)
    
    # Filter and clean tags
    cleaned_tags = []
    for tag in keyword_list:
        tag = tag.strip().lower()
        if tag and len(tag) > 2 and tag not in cleaned_tags:
            cleaned_tags.append(tag)
    
    return cleaned_tags

def publish_blog(title: str, content: str, image_path: str, tags: List[str]) -> Dict[str, Any]:
    """Publish the blog to Blogger"""
    result = blog_service.publish_blog(
        title=title,
        content=content,
        image_path=image_path,
        labels=tags
    )
    
    published_url = result.get("url", "")
    if published_url:
        print(f"Blog published successfully!")
        print(f"Published URL: {published_url}")
    else:
        print("Failed to publish blog")
        if "error" in result:
            print(f"Error: {result['error']}")
            
    return result

def clear_images_directory():
    """Clean up the images directory, including product images"""
    image_dir = image_service.output_dir
    product_dir = image_service.product_image_dir
    
    try:
        # Clear main images directory
        main_files_count = 0
        for f in os.listdir(image_dir):
            file_path = os.path.join(image_dir, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
                main_files_count += 1
        
        # Clear products subdirectory
        product_files_count = 0
        if os.path.exists(product_dir):
            for f in os.listdir(product_dir):
                file_path = os.path.join(product_dir, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    product_files_count += 1
        
        print(f"Cleared {main_files_count} files from images directory: {image_dir}")
        print(f"Cleared {product_files_count} files from products directory: {product_dir}")
    except Exception as e:
        print(f"Error clearing images directory: {str(e)}")

def main():
    """Run the entire blog generation and publishing pipeline"""
    print("=" * 80)
    print("SAMPLE BLOG GENERATION AND POSTING")
    print("=" * 80)
    
    try:
        # 1. Find trending topics (get a list, not just one)
        print("1. Finding trending topics from news sources...")
        topics = get_trending_topics_list(count=10)
        if not topics:
            print("No trending topics found. Exiting.")
            return
        
        topic_attempted = set()
        content = None
        blog_prompt = None
        blog_title = None
        for topic in topics:
            if topic.get('topic') in topic_attempted:
                continue
            topic_attempted.add(topic.get('topic'))
            print(f"Selected topic: {topic.get('topic', '')}")
            print(f"Source: {topic.get('source', 'unknown')}")
            print(f"Category: {topic.get('category', 'general')}")
            if "description" in topic and topic["description"]:
                print(f"Description: {topic['description']}")
            # 2. Generate blog content
            print("2. Generating blog content...")
            blog_prompt = trend_service.generate_blog_topic(topic)
            print(f"Blog prompt: {blog_prompt[:100]}...")
            start_time = time.time()
            try:
                blog_data = generate_blog_content(topic)
                content = blog_data.get("content", "")
                generation_time = time.time() - start_time
                print(f"Content generated in {generation_time:.2f} seconds")
                print(f"Content length: {len(content)} characters")
                if not content:
                    print("Failed to generate blog content. Trying next topic...")
                    continue
                break  # Success!
            except Exception as e:
                err_msg = str(e)
                if "people-related topics are not allowed" in err_msg.lower():
                    print("People-related topic detected. Trying next topic...")
                    continue
                print(f"Error generating blog content: {err_msg}")
                print("Trying next topic...")
                continue
        else:
            print("Error: All topics failed to generate acceptable blog content.")
            return
        # 3. Analyze SEO
        print("3. Analyzing SEO...")
        seo_results = analyze_seo(content)
        # 3.5. Prepare for monetization
        print("3.5. Preparing ad placements for monetization...")
        monetized_content = monetize_content(content)
        # 4. Extract blog title
        print("4. Extracting blog title...")
        blog_title = extract_blog_title(content)
        print(f"Blog title: {blog_title}")
        # 5. Generate image
        print("5. Generating image...")
        image_result = generate_image(topic, blog_title)
        image_path = image_result.get("image_path", "")
        if not image_path or not os.path.exists(image_path):
            print("Failed to generate image. Using fallback image.")
            fallback_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fallback_images")
            fallback_images = [f for f in os.listdir(fallback_dir) if f.endswith((".jpg", ".png"))]
            if fallback_images:
                image_path = os.path.join(fallback_dir, fallback_images[0])
            else:
                print("No fallback images available.")
                image_path = ""
        else:
            print(f"Image generated successfully: {image_path}")
            if "keywords" in image_result:
                print(f"Generated image keywords: {image_result['keywords']}")
        # 6. Generate labels/tags
        print("6. Generating labels/tags...")
        labels = generate_tags(content, topic)
        unique_labels = list(set(labels))
        print(f"Labels: {', '.join(unique_labels)}")
        # 7. Publish to Blogger
        print("7. Publishing blog to Blogger...")
        result = publish_blog(blog_title, monetized_content, image_path, unique_labels)
        published_url = result.get("url", "")
        # 7.5 Clean up images
        clear_images_directory()
        print("Images directory cleared")
        # 8. Sharing on social media (disabled)
        if published_url:
            print("\n8. Sharing on social media...")
            try:
                share_message = f"New blog post: {blog_title} - Check it out! {published_url}"
                hashtags = [f"#{label.replace(' ', '')}" for label in unique_labels[:3] if ' ' not in label]
                if hashtags:
                    share_message += " " + " ".join(hashtags)
                print(f"Share message: {share_message}")
                share_result = social_service.share_across_platforms(
                    message=share_message,
                    link=published_url
                )
                if "disabled" in share_result:
                    print("Social sharing is disabled")
                else:
                    print("Unexpected result from social sharing")
                    print(f"Share result: {share_result}")
            except Exception as e:
                print(f"ERROR sharing on social media: {str(e)}")
        else:
            print("No URL available for sharing on social media")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    print("=" * 80)
    print("Process completed successfully")
    print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a sample blog post")
    parser.add_argument('--publish', action='store_true', help='Publish the blog to Blogger')
    args = parser.parse_args()
    
    main()
