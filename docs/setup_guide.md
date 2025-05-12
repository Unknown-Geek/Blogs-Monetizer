# Affiliate Product Integration Setup

## Overview

This document provides a step-by-step guide to setting up and using the affiliate product integration feature.

## Completed Implementation

We have successfully implemented the following features:

1. **Fixed Indentation Issues**: Corrected syntax issues in the `sheets_service.py` file.
2. **Improved Image Fetching**: Enhanced the `_fetch_image_from_url` method to use multiple strategies for finding product images.
3. **Fixed Duplicate Method Implementation**: Eliminated duplicate code issues in the `ad_service.py` file.
4. **Created Testing Tools**:
   - `test_affiliate_integration.py` for verifying spreadsheet access
   - `test_image_fetching.py` for checking image extraction
   - `test_dependencies.py` for verifying required packages
5. **Enhanced Blog Generation**: Updated the `blog_service.py` to integrate affiliate products into blog content
6. **Improved Ad Enhancement**: Updated the `enhance_blog_ads.py` script to add affiliate products to existing blogs

## Required Steps for Users

### 1. Set Up the Google Spreadsheet

1. Create a Google Spreadsheet with the following columns:

   - Product Name
   - Description
   - Affiliate Link
   - Image URL
   - Category
   - Commission
   - Price

2. **Share the Spreadsheet** with the service account email:
   ```
   blogs-monetizer-152@blogs-monetizer.iam.gserviceaccount.com
   ```
3. Update the `.env` file with your spreadsheet URL:
   ```
   AFFILIATE_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/your-spreadsheet-id/edit?usp=sharing
   ```

### 2. Install Required Dependencies

Make sure all required packages are installed:

```
pip install beautifulsoup4 requests gspread google-auth google-auth-oauthlib google-auth-httplib2 python-dotenv
```

Or run the dependency check script:

```
python test_dependencies.py
```

### 3. Test the Integration

Run the following test scripts to verify your setup:

```
python test_affiliate_integration.py
python test_image_fetching.py
python test_affiliate_products.py
```

### 4. Generate a Blog with Affiliate Products

Use the `enhance_blog_ads.py` script to test the integration with a real blog:

```
python enhance_blog_ads.py --test
```

## Troubleshooting

### 1. Spreadsheet Access Issues

If you see errors related to spreadsheet access:

- Verify the spreadsheet URL in your `.env` file
- Make sure you've shared the spreadsheet with the correct service account email
- Check that you've given "Editor" permissions to the service account

### 2. Image Fetching Issues

If the system fails to fetch images from product URLs:

- Check that the product URLs are valid and accessible
- Verify that BeautifulSoup4 and requests are installed
- Some websites may block scraping; providing direct image URLs is more reliable

### 3. No Affiliate Products Showing

If no affiliate products appear in your blogs:

- Check that your spreadsheet has products with categories matching your blog content
- Verify that the spreadsheet data is correctly formatted
- Make sure the system can access your spreadsheet

## Further Customization

### Styling Affiliate Ads

You can customize the appearance of affiliate ads by modifying the `create_affiliate_ad` method in `ad_service.py`.

### Ad Placement Strategy

Adjust the ad placement strategy by modifying the `insert_affiliate_ads` method in `ad_service.py`.

### Maximum Ads Per Blog

You can control the maximum number of affiliate ads per blog by adjusting the `max_affiliate_ads` parameter in the `blog_service.py` file.
