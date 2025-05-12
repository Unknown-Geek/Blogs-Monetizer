#!/usr/bin/env python
"""
Test Affiliate Product Integration
---------------------------------
This script tests fetching and displaying affiliate products in blog content.
"""
import os
import sys
import json
from pprint import pprint
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load environment variables
load_dotenv()

def test_affiliate_products():
    """Test fetching and integrating affiliate products from the Google Sheet"""
    from services.ad_service import ad_service
    from services.sheets_service import google_sheets_service
    
    print("=" * 80)
    print("AFFILIATE PRODUCT INTEGRATION TEST")
    print("=" * 80)
    
    # 1. Check for the affiliate spreadsheet URL in environment variables
    spreadsheet_url = os.getenv('AFFILIATE_SPREADSHEET_URL')
    if not spreadsheet_url:
        print("❌ No AFFILIATE_SPREADSHEET_URL found in .env file")
        print("Using default test spreadsheet URL...")
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1jE-hN0O31JutWkJZRfODVQGM3jSxax4lHS2cycaB7iE/edit?usp=sharing"
    else:
        print(f"✅ Found AFFILIATE_SPREADSHEET_URL in .env: {spreadsheet_url}")
    
    # 2. Authenticate with Google Sheets API
    print("\nAuthenticating with Google Sheets API...")
    auth_success = google_sheets_service.authenticate()
    if auth_success:
        print("✅ Google Sheets API authentication successful")
    else:
        print("❌ Google Sheets API authentication failed")
        print("Using sample affiliate products instead")
    
    # 3. Fetch affiliate products
    print("\nFetching affiliate products from spreadsheet...")
    affiliate_products = ad_service.fetch_affiliate_products()
    
    if affiliate_products:
        print(f"✅ Successfully fetched {len(affiliate_products)} affiliate products")
        
        # Show product info for the first few products
        print("\nSample Products:")
        for i, product in enumerate(affiliate_products[:3]):
            print(f"  {i+1}. {product.get('product_name')} - {product.get('price')}")
            print(f"     Link: {product.get('affiliate_link')}")
            print(f"     Image: {product.get('image_url') or 'No image URL provided'}")
            print(f"     Categories: {product.get('category')}")
            print()
    else:
        print("❌ Failed to fetch affiliate products")
    
    # 4. Test inserting affiliate products into sample blog content
    print("\nTesting affiliate product insertion into blog content...")
    sample_content = """
    <h1>Test Blog Post</h1>
    <p>This is a test blog post about technology and programming. We'll talk about various topics
    including web development, mobile apps, and software engineering principles.</p>
    <p>Office equipment is essential for productivity. Having a good setup can make all the difference
    in how effectively you work from home or at the office.</p>
    <p>Health and fitness are also important considerations for modern professionals. Taking breaks
    and getting adequate exercise helps maintain productivity over the long term.</p>
    <p>When it comes to education, online courses have revolutionized how we learn and acquire new skills.
    Many professionals take advantage of these resources to advance their careers.</p>
    <p>Home security and smart home technology have also become increasingly important, allowing
    people to monitor and control their living spaces remotely.</p>
    <p>Beauty and self-care routines shouldn't be neglected either, as taking care of yourself
    is an important part of maintaining work-life balance.</p>
    """
    
    # Insert affiliate ads
    content_with_affiliates = ad_service.insert_affiliate_ads(
        sample_content, 
        affiliate_products, 
        max_affiliate_ads=2
    )
    
    # Save the result to a file for viewing
    output_dir = os.path.join(current_dir, "tests")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "affiliate_test_output.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Affiliate Product Test</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 20px;
                }
                h1 { color: #333; }
                .test-info { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="test-info">
                <h2>Affiliate Product Integration Test</h2>
                <p>Timestamp: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
                <p>Products fetched: """ + str(len(affiliate_products)) + """</p>
            </div>
            <hr>
            <h3>Blog Content with Affiliate Products:</h3>
        """)
        f.write(content_with_affiliates)
        f.write("""
        </body>
        </html>
        """)
    
    print(f"✅ Test complete! Output saved to: {output_file}")
    print(f"Open this file in a browser to view the affiliate product integration.")
    
    return output_file

if __name__ == "__main__":
    output_file = test_affiliate_products()
    
    # Try to open the output file in the default browser
    try:
        import webbrowser
        webbrowser.open('file://' + os.path.abspath(output_file))
        print("Opening test result in your default browser...")
    except:
        print("Could not automatically open the browser. Please open the output file manually.")
