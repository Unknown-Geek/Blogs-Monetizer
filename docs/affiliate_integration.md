# Affiliate Product Integration Guide

This document explains how to use the affiliate product integration feature in the Monetize-blogs system.

## Overview

The affiliate product integration allows you to automatically place relevant affiliate product links in your blog content. These links are sourced from a Google Spreadsheet, which makes it easy to update your product offerings without changing code.

## How It Works

1. You create a Google Spreadsheet with your affiliate products
2. You share this spreadsheet with our service account
3. The system fetches products from the spreadsheet
4. When generating blogs, relevant products are inserted into the content
5. If a product doesn't have an image, the system will try to fetch one from the product page

## Setup

### 1. Configure Google Spreadsheet

1. Create a Google Spreadsheet with the following columns:

   | Product Name      | Description                   | Affiliate Link                   | Image URL                     | Category          | Commission | Price |
   | ----------------- | ----------------------------- | -------------------------------- | ----------------------------- | ----------------- | ---------- | ----- |
   | Apple MacBook Air | Thin and light laptop with... | https://affiliate.amazon.com/... | https://images.amazon.com/... | technology,laptop | 4%         | $999  |

   **Note**: Make sure the first row contains these exact headers.

2. Set up appropriate sharing permissions:

   - **You must share your spreadsheet** with our service account: `blogs-monetizer-152@blogs-monetizer.iam.gserviceaccount.com`
   - Give it "Editor" access
   - For detailed instructions, see `docs/spreadsheet_sharing.md`

3. Copy the spreadsheet URL and add it to your `.env` file:
   ```
   AFFILIATE_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/your-spreadsheet-id/edit?usp=sharing
   ```

## Column Explanations

1. **Product Name**: The name of your affiliate product
2. **Description**: A brief description (100-150 characters recommended)
3. **Affiliate Link**: The full affiliate URL including your tracking code
4. **Image URL**: (Optional) URL to the product image. If left blank, the system will try to extract it from the product page
5. **Category**: Comma-separated list of categories (e.g., "technology,laptop,productivity")
6. **Commission**: Your commission rate (e.g., "4%", "$5 per sale")
7. **Price**: The product price (e.g., "$999", "€149.99")

## Testing Your Setup

1. Run the `test_affiliate_integration.py` script to verify spreadsheet access:

   ```
   python test_affiliate_integration.py
   ```

2. Run the `test_affiliate_products.py` script to test product fetching and integration:

   ```
   python test_affiliate_products.py
   ```

3. Run the `test_image_fetching.py` script to verify image extraction from product URLs:
   ```
   python test_image_fetching.py
   ```

## Usage

### Automatic Integration

The affiliate products are automatically integrated into blog content during the generation process. The system:

1. Fetches affiliate products from your configured spreadsheet
2. Analyzes blog content for relevant keywords and categories
3. Inserts the most relevant affiliate products at optimal positions in the content
4. Renders the products with attractive styling, including images when available

### API Endpoints

The system provides two API endpoints for affiliate product integration:

#### 1. Add Affiliate Ads

- **URL**: `/api/add-affiliate-ads`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "content": "<p>Your blog content here...</p>",
    "max_affiliate_ads": 2,
    "category": "technology"
  }
  ```
- **Parameters**:

  - `content` (required): The HTML content of your blog post
  - `max_affiliate_ads` (optional): Maximum number of affiliate ads to insert (default: 2)
  - `category` (optional): Filter products by category

- **Response**:
  ```json
  {
    "content": "<p>Your blog content with affiliate ads inserted...</p>",
    "products_used": 2,
    "total_products_available": 5
  }
  ```

#### 2. Get Affiliate Products

- **URL**: `/api/affiliate-products`
- **Method**: `GET`
- **Query Parameters**:

  - `category` (optional): Filter products by category
  - `limit` (optional): Limit the number of products returned

- **Response**:
  ```json
  {
    "products": [
      {
        "product_name": "Product Name",
        "description": "Product description",
        "affiliate_link": "https://example.com/product",
        "image_url": "https://example.com/image.jpg",
        "category": "category1,category2",
        "commission": "10%",
        "price": "$99.99"
      }
      // More products...
    ],
    "total": 5
  }
  ```

## Image Fetching

The system will automatically attempt to fetch product images from the affiliate link URLs when no image URL is provided. This feature:

1. Extracts product images from the destination pages
2. Uses various strategies to find the most relevant image:
   - Open Graph images
   - Social media card images
   - Product showcase images
   - Largest relevant images on the page

If no image can be extracted, a placeholder image is used instead.

## Ad Formats

Affiliate products can be displayed in several formats:

1. **Rectangle** - Standard rectangular ad format suitable for sidebar or in-content placement
2. **Banner** - Horizontal banner suitable for placement between paragraphs
3. **Leaderboard** - Larger horizontal banner for top/bottom placement
4. **Skyscraper** - Vertical format for sidebar placement

## Integration Examples

### Example 1: Basic Integration

```python
from services.ad_service import ad_service

# Fetch affiliate products
affiliate_products = ad_service.fetch_affiliate_products()

# Insert into content
monetized_content = ad_service.insert_affiliate_ads(
    content,
    affiliate_products,
    max_affiliate_ads=2
)
```

### Example 2: Category-Specific Products

```python
from services.ad_service import ad_service

# Fetch all affiliate products
all_products = ad_service.fetch_affiliate_products()

# Filter by category
tech_products = [p for p in all_products if "technology" in p.get("category", "").lower()]

# Insert into content
monetized_content = ad_service.insert_affiliate_ads(
    content,
    tech_products,
    max_affiliate_ads=3
)
```

#### Get Affiliate Products

```
POST /api/affiliate-products
```

Returns a list of all available affiliate products from your configured spreadsheet.

#### Add Affiliate Ads to Content

```
POST /api/add-affiliate-ads
```

Request body:

```json
{
  "content": "<p>Your HTML blog content here...</p>",
  "max_ads": 2
}
```

Returns the content with affiliate product ads inserted at optimal positions.

## How It Works

The system uses several techniques to ensure affiliate products are relevant to the content:

1. **Category Matching**: Products in categories mentioned in the content get higher relevance scores
2. **Keyword Matching**: Products whose names or descriptions contain words used in the content get higher scores
3. **Placement Optimization**: Products are placed at strategic positions in the content for maximum visibility
4. **Adaptive Display**: Different ad formats are used based on the content structure and device

## Customization

You can customize how affiliate products appear by modifying the ad format templates in `services/ad_service.py`. The system supports multiple ad formats including:

- Rectangle (default)
- Banner
- Leaderboard
- Skyscraper

Each format has responsive design and includes fallback mechanisms for missing images.

## Testing

You can test the affiliate product integration using the provided test script:

```
python test_affiliate_products.py
```

This will generate a sample blog post with affiliate products and open it in your browser for review.

## Advanced Integration Logic

- **Relevance Scoring:** When inserting affiliate ads, the system scores all products for relevance to the blog content (using category and keyword matching). The most relevant products are displayed; if no strong matches, random products are chosen.
- **No Products, No Ads:** If there are no products in the spreadsheet, no affiliate ads are shown in the blog.
- **AI Clickbait Phrases:** Optionally, the system can use Gemini to generate clickbait ad phrases for each product.
- **Duplicate Blog Prevention:** The system prevents more than one blog from being written about the same or very similar news using fuzzy matching and URL/title checks.
