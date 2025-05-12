# API Routes Documentation

This document provides an overview of all available API endpoints in the Monetize-blogs backend.

## Blog Generation API

### Generate Blog Content

- **URL**: `/api/generate-blog`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "prompt": "The topic or idea for the blog"
  }
  ```
- **Response**:
  ```json
  {
    "content": "Generated HTML content for the blog"
  }
  ```
- **Description**: Generates blog content using the Gemini API based on the provided prompt.

### Analyze SEO

- **URL**: `/api/analyze-seo`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "content": "The content to analyze for SEO"
  }
  ```
- **Response**:
  ```json
  {
    "report": {
      "word_count": 500,
      "keywords": { "keyword1": 10, "keyword2": 8 },
      "keyword_density": { "keyword1": 0.02, "keyword2": 0.016 },
      "issues": ["Content length is below recommended minimum"],
      "score": 80
    }
  }
  ```
- **Description**: Analyzes the SEO metrics of the provided content, including word count, keyword density, and potential issues.

### Generate Image

- **URL**: `/api/generate-image`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "prompt": "Description for the image to generate"
  }
  ```
- **Response**:
  ```json
  {
    "image_path": "path/to/generated/image.png"
  }
  ```
- **Description**: Sources a relevant image from Unsplash based on the provided prompt.

### Publish Blog

- **URL**: `/api/publish`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "title": "Blog Title",
    "content": "HTML content of the blog",
    "image_path": "path/to/image.png",
    "labels": ["tag1", "tag2"],
    "share_on_social": true
  }
  ```
- **Response**:
  ```json
  {
    "result": {
      "id": "blog_post_id",
      "url": "https://example.blogspot.com/post",
      "social_share": {
        "success": true,
        "message": "Social sharing is disabled"
      }
    }
  }
  ```
- **Description**: Publishes the blog to Blogger platform and optionally shares on social media.

## Trending Topics API

### Get Trending Topics

- **URL**: `/api/trending-topics`
- **Method**: `GET`
- **Query Parameters**:
  - `sources`: Comma-separated list of sources (e.g., "google,news")
  - `count`: Number of topics to return (default: 5)
- **Response**:
  ```json
  {
    "trends": [
      {
        "source": "google",
        "topic": "Topic Name"
      }
    ]
  }
  ```
- **Description**: Retrieves current trending topics from selected sources.

## Automation API

### Start Automation

- **URL**: `/api/automation/start`
- **Method**: `POST`
- **Request Body** (optional):
  ```json
  {
    "posts_per_day": 2,
    "min_hours_between_posts": 6,
    "trending_sources": ["google", "news"],
    "categories": ["technology"],
    "min_seo_score": 75
  }
  ```
- **Response**:
  ```json
  {
    "status": "Automation started",
    "config": {
      "posts_per_day": 2,
      "min_hours_between_posts": 6
    }
  }
  ```
- **Description**: Starts the automated blog generation process with optional configuration.

### Stop Automation

- **URL**: `/api/automation/stop`
- **Method**: `POST`
- **Response**:
  ```json
  {
    "status": "Automation stop signal sent"
  }
  ```
- **Description**: Stops the automated blog generation process.

### Check Automation Status

- **URL**: `/api/automation/status`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "running": true,
    "config": {
      "posts_per_day": 1
    },
    "recent_logs": [
      {
        "timestamp": "2025-05-10T14:00:00.000Z",
        "status": "success",
        "topic": { "source": "google", "topic": "AI advancements" }
      }
    ],
    "last_post_time": "2025-05-10T14:00:00.000Z"
  }
  ```
- **Description**: Returns the current status of the automation process, recent logs, and configuration.

### Run Automation Once

- **URL**: `/api/automation/run-now`
- **Method**: `POST`
- **Response**:
  ```json
  {
    "result": {
      "timestamp": "2025-05-10T14:00:00.000Z",
      "status": "success",
      "topic": { "source": "google", "topic": "AI advancements" },
      "seo_score": 85
    }
  }
  ```
- **Description**: Runs the blog generation process once immediately, outside of the scheduled runs.

## Configuration API

### Get Configuration

- **URL**: `/api/config`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "automation": {
      "posts_per_day": 1,
      "min_hours_between_posts": 8,
      "trending_sources": ["google", "news"],
      "categories": ["technology", "business", "science"],
      "min_seo_score": 70
    },
    "seo": {
      "min_word_count": 300,
      "optimal_keyword_density": 0.02
    },
    "image": {
      "model": "stabilityai/stable-diffusion-xl-base-1.0",
      "output_dir": "./images"
    }
  }
  ```
- **Description**: Returns the current non-sensitive configuration settings.

### Update Configuration

- **URL**: `/api/config`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "automation": {
      "posts_per_day": 2,
      "min_seo_score": 75
    },
    "seo": {
      "min_word_count": 500
    },
    "image": {
      "output_dir": "./custom_images"
    }
  }
  ```
- **Response**:
  ```json
  {
    "status": "Configuration updated successfully"
  }
  ```
- **Description**: Updates the application configuration settings.

## Analytics API

### Get Analytics Data

- **URL**: `/api/analytics`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "posts_count": 15,
    "last_post": "2025-05-10T10:30:00.000Z",
    "top_performing": {
      "title": "Sample Blog Post",
      "views": 1250,
      "shares": 42
    }
  }
  ```
- **Description**: Returns analytics data about the blog posts.

## Affiliate Product API

### Add Affiliate Ads

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
- **Response**:
  ```json
  {
    "content": "<p>Your blog content with affiliate ads inserted...</p>",
    "products_used": 2,
    "total_products_available": 5
  }
  ```
- **Description**: Inserts affiliate product ads into blog content based on relevance.

### Get Affiliate Products

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
    ],
    "total": 5
  }
  ```
- **Description**: Fetches affiliate products from the configured spreadsheet.
