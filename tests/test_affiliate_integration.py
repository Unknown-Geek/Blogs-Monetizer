"""
Test script for verifying spreadsheet access and data fetching.
This script attempts to connect to the Google Spreadsheet defined in the .env file
and fetch affiliate product data.
"""
import os
import sys
from dotenv import load_dotenv
from services.sheets_service import google_sheets_service

# Load environment variables
load_dotenv()

def test_spreadsheet_access():
    """Test if we can access the spreadsheet and fetch data."""
    print("\n===== TESTING GOOGLE SHEETS ACCESS =====")
    
    # Get spreadsheet URL from environment
    spreadsheet_url = os.getenv("AFFILIATE_SPREADSHEET_URL")
    if not spreadsheet_url:
        print("Error: AFFILIATE_SPREADSHEET_URL not found in .env file")
        return False
    
    print(f"Using spreadsheet URL: {spreadsheet_url}")
    
    # Test authentication
    print("\nTesting authentication...")
    if not google_sheets_service.authenticate():
        print("Authentication failed. Check service-account.json file.")
        return False
    print("Authentication successful!")
      # Test raw data access
    print("\nTesting raw spreadsheet data access...")
    raw_data = google_sheets_service.get_spreadsheet_data(spreadsheet_url)
    
    if not raw_data:
        print("Failed to fetch data from spreadsheet.")
        print("Please check:")
        print("1. The spreadsheet URL is correct")
        print("2. The service account has access to the spreadsheet")
        print("\nIMPORTANT: You must share the spreadsheet with this email address:")
        print(f"   {os.environ.get('GA_CLIENT_EMAIL', 'blogs-monetizer-152@blogs-monetizer.iam.gserviceaccount.com')}")
        print("\nTo fix this issue:")
        print("1. Open your spreadsheet in Google Sheets")
        print("2. Click 'Share' in the top-right corner")
        print("3. Add the service account email address")
        print("4. Set permission to 'Editor'")
        print("5. Click 'Send'")
        return False
    
    print(f"Successfully fetched {len(raw_data)} rows of raw data!")
    
    # Print first few rows as sample
    if raw_data:
        print("\nSample data from spreadsheet (first 2 rows):")
        for i, row in enumerate(raw_data[:2]):
            print(f"Row {i+1}: {row}")
    
    return True

def test_affiliate_products():
    """Test if we can fetch and process affiliate products."""
    print("\n===== TESTING AFFILIATE PRODUCTS =====")
    
    # Get spreadsheet URL from environment
    spreadsheet_url = os.getenv("AFFILIATE_SPREADSHEET_URL")
    if not spreadsheet_url:
        print("Error: AFFILIATE_SPREADSHEET_URL not found in .env file")
        return False
    
    # Fetch formatted affiliate products
    print("\nFetching affiliate products...")
    products = google_sheets_service.fetch_affiliate_products(spreadsheet_url)
    
    if not products:
        print("Failed to fetch any affiliate products.")
        return False
    
    # Check if these are sample products or real ones
    sample_product_name = "Premium Fitness Tracker"
    using_samples = any(p["product_name"] == sample_product_name for p in products)
    
    if using_samples:
        print("Warning: Using sample products, not real data from spreadsheet.")
        print("Please check if your spreadsheet has the correct columns and valid product data.")
    else:
        print(f"Successfully fetched {len(products)} real affiliate products!")
    
    # Print first few products as sample
    print("\nSample affiliate products (first 2):")
    for i, product in enumerate(products[:2]):
        print(f"Product {i+1}:")
        for key, value in product.items():
            print(f"  {key}: {value}")
        print()
    
    return not using_samples

if __name__ == "__main__":
    print("Starting Affiliate Spreadsheet Integration Tests")
    
    # Test spreadsheet access
    access_success = test_spreadsheet_access()
    
    if access_success:
        # Test affiliate products formatting
        products_success = test_affiliate_products()
        
        if products_success:
            print("\n✅ All tests passed successfully! Your affiliate integration is working properly.")
        else:
            print("\n⚠️ Spreadsheet access works, but using sample products.")
            print("Check your spreadsheet format and make sure it has valid product data.")
    else:
        print("\n❌ Failed to access spreadsheet data.")
        print("Fix the issues above before continuing.")
    
    print("\nTest completed.")
