"""
Test script to verify that only spreadsheet products are used and no fallback/sample products
"""
import os
import sys
from typing import Dict, List

# Make imports work correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Import services
from services.ad_service import ad_service
from services.sheets_service import google_sheets_service

def test_affiliate_products():
    """Test that we only get products from spreadsheet"""
    # Get products from the ad service
    print("\n=== Testing AdService affiliate products ===")
    affiliate_products = ad_service.fetch_affiliate_products()
    print(f"Retrieved {len(affiliate_products)} products")
    
    # Check for known sample product names
    sample_product_names = {
        "Premium Fitness Tracker",
        "Professional Home Office Chair",
        "Complete Web Development Course", 
        "Smart Home Security System",
        "Organic Skincare Bundle"
    }
    
    # Check if any product names match sample names
    product_names = {p.get("product_name", "") for p in affiliate_products}
    using_samples = any(name in sample_product_names for name in product_names)
    
    if using_samples:
        print("WARNING: Still using sample products! Fix failed.")
        for name in product_names:
            if name in sample_product_names:
                print(f"  - Sample product found: {name}")
    else:
        if affiliate_products:
            print("SUCCESS: Using real spreadsheet products or empty list.")
        else:
            print("NOTE: No products returned - this is expected if no spreadsheet is configured.")
    
    # Test direct sheets service fetch
    print("\n=== Testing SheetsService sample products ===")
    sample_products = google_sheets_service._get_sample_products()
    if sample_products:
        print("WARNING: SheetsService._get_sample_products() still returns products!")
        print(f"  - Returned {len(sample_products)} sample products")
    else:
        print("SUCCESS: SheetsService._get_sample_products() returns empty list as expected")
    
    return not using_samples and not sample_products

def test_ad_service_sample_products():
    """Test that AdService sample products method returns empty list"""
    print("\n=== Testing AdService sample products method ===")
    sample_products = ad_service._get_sample_products()
    if sample_products:
        print("WARNING: AdService._get_sample_products() still returns products!")
        print(f"  - Returned {len(sample_products)} sample products")
    else:
        print("SUCCESS: AdService._get_sample_products() returns empty list as expected")
    
    return not sample_products

if __name__ == "__main__":
    # Run tests
    print("\n==================================================")
    print("TESTING AFFILIATE PRODUCT INTEGRATION - NO FALLBACKS")
    print("==================================================\n")
    
    test_1 = test_affiliate_products()
    test_2 = test_ad_service_sample_products()
    
    print("\n==================================================")
    print(f"OVERALL RESULT: {'SUCCESS' if test_1 and test_2 else 'FAILURE'}")
    print("==================================================\n")
