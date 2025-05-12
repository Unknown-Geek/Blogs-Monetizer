#!/usr/bin/env python
"""
Test Spreadsheet Fetching
-------------------------
This script tests fetching your specified affiliate products from Google Sheets.
It will display product information and check specifically that we're using your
spreadsheet rather than the fallback sample products.
"""
import os
import sys
import json
from dotenv import load_dotenv
from pprint import pprint

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load environment variables
load_dotenv()

def test_spreadsheet_fetch():
    """Test that we're fetching from the spreadsheet correctly"""
    print("=" * 80)
    print("AFFILIATE SPREADSHEET FETCH TEST")
    print("=" * 80)
    
    # Import services
    from services.sheets_service import google_sheets_service
    from services.ad_service import ad_service
    
    # 1. Verify environment variables are set
    spreadsheet_url = os.environ.get("AFFILIATE_SPREADSHEET_URL")
    if not spreadsheet_url:
        print("❌ AFFILIATE_SPREADSHEET_URL not found in .env file")
        return False
    
    print(f"✅ Using spreadsheet URL: {spreadsheet_url}")
    
    # 2. Verify service account settings
    use_service_account = os.environ.get("USE_SERVICE_ACCOUNT", "false").lower() == "true"
    print(f"✅ Using service account authentication: {use_service_account}")
    
    service_account_path = os.path.join(current_dir, "credentials", "service-account.json")
    if use_service_account and not os.path.exists(service_account_path):
        print(f"❌ Service account file not found at {service_account_path}")
        return False
    
    print(f"✅ Service account file exists at {service_account_path}")
    
    # 3. Authenticate with Google Sheets API
    print("\nAuthenticating with Google Sheets API...")
    auth_success = google_sheets_service.authenticate(use_service_account=use_service_account)
    
    if auth_success:
        print("✅ Successfully authenticated with Google Sheets API")
    else:
        print("❌ Failed to authenticate with Google Sheets API")
        print("Make sure you've set up the credentials correctly and shared your spreadsheet")
        print(f"with the service account email: {os.environ.get('GA_CLIENT_EMAIL')}")
        return False
    
    # 4. Fetch raw spreadsheet data directly
    print("\nFetching raw spreadsheet data...")
    raw_data = google_sheets_service.get_spreadsheet_data(spreadsheet_url)
    
    if raw_data:
        print(f"✅ Successfully fetched {len(raw_data)} rows from spreadsheet")
        print("\nSample raw data (first 2 rows):")
        pprint(raw_data[:2])
    else:
        print("❌ Failed to fetch raw data from spreadsheet")
        return False
    
    # 5. Fetch formatted affiliate products
    print("\nFetching formatted affiliate products...")
    affiliate_products = google_sheets_service.fetch_affiliate_products(spreadsheet_url)
    
    if affiliate_products:
        print(f"✅ Successfully fetched {len(affiliate_products)} formatted products")
        print("\nSample formatted products (first 2):")
        pprint(affiliate_products[:2])
    else:
        print("❌ Failed to fetch formatted affiliate products")
        return False
    
    # 6. Verify we're NOT using sample products
    print("\nVerifying these are NOT sample products...")
    sample_product_names = set([
        "Premium Fitness Tracker",
        "Professional Home Office Chair",
        "Complete Web Development Course",
        "Smart Home Security System",
        "Organic Skincare Bundle"
    ])
    
    product_names = set([p.get("product_name") for p in affiliate_products])
    
    if product_names.issubset(sample_product_names):
        print("❌ We are still using sample products, not fetching from your spreadsheet")
        return False
    else:
        print("✅ Confirmed we are using products from your spreadsheet")
        
    # 7. Test ad service fetch
    print("\nTesting ad_service.fetch_affiliate_products()...")
    ad_service_products = ad_service.fetch_affiliate_products()
    
    if ad_service_products:
        print(f"✅ ad_service successfully fetched {len(ad_service_products)} products")
        
        # Check if we're using the real data
        ad_service_product_names = set([p.get("product_name") for p in ad_service_products])
        
        if ad_service_product_names.issubset(sample_product_names):
            print("❌ ad_service is still using sample products")
            return False
        else:
            print("✅ ad_service is using products from your spreadsheet")
            
    else:
        print("❌ ad_service failed to fetch affiliate products")
        return False
        
    print("\n✅ SUCCESS! We are properly fetching affiliate products from your spreadsheet")
    return True

if __name__ == "__main__":
    success = test_spreadsheet_fetch()
    
    if not success:
        print("\nPlease follow these steps to fix the issue:")
        print("1. Make sure your spreadsheet has columns: Product Name, Description, Affiliate Link, Image URL, Category, Commission, Price")
        print("2. Ensure you've shared your spreadsheet with the service account email: " + os.environ.get("GA_CLIENT_EMAIL", "[service account email not found in env]"))
        print("3. Check that your .env file has the correct AFFILIATE_SPREADSHEET_URL")
        print("4. Set USE_SERVICE_ACCOUNT=true in your .env file")
        sys.exit(1)
    else:
        sys.exit(0)
