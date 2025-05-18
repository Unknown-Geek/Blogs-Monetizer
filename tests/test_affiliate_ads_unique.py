#!/usr/bin/env python
"""
Test for ensuring affiliate ads don't show duplicate products
-----------------------------------------
This test verifies that when multiple affiliate ads are shown,
they represent different products rather than duplicates.
"""
import os
import sys
import re
from pprint import pprint

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)  # Go up one level to project root
sys.path.append(project_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_unique_affiliate_ads():
    """
    Test that the ad_service.insert_affiliate_ads method shows unique products
    """
    from services.ad_service import ad_service
    
    print("\n" + "=" * 80)
    print("TESTING UNIQUE AFFILIATE PRODUCTS IN ADS")
    print("=" * 80 + "\n")
    
    # Create some test content with multiple topics to trigger different ads
    test_content = """
    <h1>Test Article with Multiple Topics</h1>
    
    <h2>Technology Section</h2>
    <p>This section is about technology products including smartphones, laptops, 
    and other electronic devices. Many people look for the best tech products 
    for their daily use at home or in the office.</p>
    
    <h2>Home Improvement Section</h2>
    <p>This section discusses home improvement and furniture. Having a comfortable
    and well-designed living space is important for many families.</p>
    
    <h2>Health and Wellness Section</h2>
    <p>Health products and fitness equipment are essential for maintaining a 
    healthy lifestyle. Many people invest in quality health products.</p>
    """
    
    # Fetch affiliate products
    affiliate_products = ad_service.fetch_affiliate_products()
    if not affiliate_products:
        print("❌ No affiliate products found for testing")
        return False
    
    # Insert multiple ads
    max_ads_count = min(5, len(affiliate_products))  # Try to insert up to 5 ads
    print(f"Testing with {len(affiliate_products)} available products, trying to insert {max_ads_count}")
    
    result_content = ad_service.insert_affiliate_ads(
        test_content,
        affiliate_products,
        max_affiliate_ads=max_ads_count
    )
    
    # Extract the products that were inserted
    product_urls = re.findall(r'href="([^"]+)"[^>]*>Shop Now</a>', result_content)
    product_names = re.findall(r'<div[^>]*class="product-catchphrase"[^>]*>([^<]+)</div>', result_content)
    
    # Count the number of ads actually inserted
    num_ads_inserted = len(product_urls)
    
    # Get unique values
    unique_urls = set(product_urls)
    unique_names = set(product_names)
    
    # Display results
    print(f"\nInserted {num_ads_inserted} affiliate ads")
    print(f"Unique URLs: {len(unique_urls)}")
    print(f"Unique product names/catchphrases: {len(unique_names)}")
    
    # Print the products that were selected
    print("\nSelected products:")
    for i, name in enumerate(product_names):
        print(f"  {i+1}. {name}")
        if i < len(product_urls):
            print(f"     URL: {product_urls[i]}")
    
    # Test for duplicates
    has_duplicate_urls = len(product_urls) != len(unique_urls)
    has_duplicate_names = len(product_names) != len(unique_names)
    
    if has_duplicate_urls:
        print("\n❌ FAILED: Found duplicate product URLs!")
        # Find which URLs are duplicated
        url_counts = {}
        for url in product_urls:
            url_counts[url] = url_counts.get(url, 0) + 1
        
        for url, count in url_counts.items():
            if count > 1:
                print(f"  URL appears {count} times: {url}")
    else:
        print("\n✅ SUCCESS: All product URLs are unique")
    
    if has_duplicate_names:
        print("\n⚠️ WARNING: Found similar product catchphrases")
        # Find which names are duplicated
        name_counts = {}
        for name in product_names:
            name_counts[name] = name_counts.get(name, 0) + 1
        
        for name, count in name_counts.items():
            if count > 1:
                print(f"  Catchphrase appears {count} times: {name}")
    else:
        print("✅ SUCCESS: All product catchphrases are unique")
    
    # Save output to a file for inspection
    output_dir = os.path.join(current_dir, "test_outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "unique_affiliate_ads_test.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unique Affiliate Ads Test</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
        <h1>Test Results for Unique Affiliate Ads</h1>
        """)
        f.write(result_content)
        f.write("""
        </body>
        </html>
        """)
    
    print(f"\nTest output saved to: {output_file}")
    
    return not (has_duplicate_urls or has_duplicate_names)

def test_affiliate_ads_unique():
    """Main test function for the test runner to find"""
    return test_unique_affiliate_ads()

if __name__ == "__main__":
    success = test_unique_affiliate_ads()
    
    if success:
        print("\n" + "=" * 80)
        print("TEST PASSED: All affiliate ads show different products")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("TEST FAILED: Some duplicate products were found in affiliate ads")
        print("=" * 80)
