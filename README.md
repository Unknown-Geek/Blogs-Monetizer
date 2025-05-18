---
title: Blogs Monetizer
emoji: 🐢
colorFrom: red
colorTo: green
sdk: docker
pinned: false
---

# Blogs Monetizer

A comprehensive system for generating, optimizing, and monetizing blog content with AI assistance.

## Overview

This system automates the entire process of blog content creation and publication:

1. **Trend Detection**: Automatically discovers trending topics from news sources and social media
2. **Content Generation**: Creates high-quality blog posts using Google's Gemini API
3. **SEO Optimization**: Analyzes and improves content for search engine visibility
4. **Monetization**: Implements optimal ad placement strategies for revenue generation

## Utility Scripts

The `helpers` directory contains utility scripts to assist with setup and configuration:

- `convert_service_account_to_env.py` - Converts service account JSON to environment variable format
- `set_env_variables.py` - Sets up environment variables for different deployment scenarios
- `check_env_setup.py` - Verifies that environment variables are properly configured
- `get_blogger_token.py` - Generates a refresh token for Blogger API authentication
- `image_utils.py` - Utilities for managing image assets

5. **Image Generation**: Sources relevant images from Unsplash with proper attribution
6. **Publishing**: Publishes content to Blogger with formatting intact
7. **Social Sharing**: Logging of social sharing activity (actual sharing disabled)
8. **Automation**: Schedules multiple posts per day with configurable frequency

## System Architecture

The system is built with a modular service-based architecture:

- **API Layer**: FastAPI application providing endpoints for all functionality
- **Service Layer**: Specialized services for each major function
- **Automation**: Scheduled processes for autonomous operation

### Core Services

- `trend_service.py`: Detects trending topics across various sources
- `blog_service.py`: Generates and publishes blog content
- `seo_service.py`: Analyzes and optimizes content for SEO
- `ad_service.py`: Implements advertising and monetization strategies
- `image_service.py`: Generates relevant images for posts
- `social_service.py`: Shares content across social platforms
- `automation_service.py`: Orchestrates the entire process with scheduling

## Setup and Configuration

### Prerequisites

- Python 3.8+
- Required API keys:
  - Google Gemini API
  - Blogger API
  - Unsplash API
  - News API
  - News API (for trending topics)

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/monetize-blogs.git
   cd monetize-blogs
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Configure API keys in `.env` file (see the existing file for format)

### Running the System

#### Start the API Server

```
python app.py
```

This starts the FastAPI server on http://localhost:8000 by default.

#### Run the Automation Service Directly

To start the automated blog posting:

```
python auto_blog.py
```

## Quick Start

The following scripts provide quick access to key functionality:

- `generate_sample_blog.py` - Creates and publishes a single blog post
- `auto_blog.py` - Runs the automated blog publishing system continuously
- `enhance_blog_ads.py` - Updates existing blog posts with improved ad displays
- `app.py` - Starts the FastAPI server for web interface access

For testing specific components:

- See the `tests/` directory for component-specific test scripts

## API Endpoints

### Trend Detection

- `GET /api/trending-topics`: Get current trending topics

### Blog Generation

- `POST /api/generate-blog`: Generate blog content
- `POST /api/analyze-seo`: Analyze content for SEO
- `POST /api/generate-image`: Generate a blog image
- `POST /api/publish`: Publish a blog post

### Automation

- `POST /api/automation/start`: Start the automation process
- `POST /api/automation/stop`: Stop the automation process
- `GET /api/automation/status`: Check automation status
- `POST /api/automation/run-now`: Run the automation once immediately

### Configuration

- `GET /api/config`: Get current configuration
- `POST /api/config`: Update configuration

## Testing

Run the test suite to verify all components are working:

```
python tests/run_tests.py
```

Individual tests can be run directly:

```
python tests/test_trend_service.py
python tests/test_seo_service.py
python tests/test_image_service.py
```

## Configuration Options

The system can be configured through environment variables or via the API:

- `POSTS_PER_DAY`: Number of posts to generate per day (default: 1)
- `MIN_SEO_SCORE`: Minimum SEO score to accept (default: 70)
- `IMAGE_OUTPUT_DIR`: Directory for storing generated images
- `ENABLE_HEARTBEAT`: Enable/disable the heartbeat mechanism (default: true)
- `HEARTBEAT_INTERVAL_MINUTES`: Interval between heartbeats in minutes (default: 15)

## Improvements

Recent improvements to the system include:

1. **Enhanced SEO Analysis**: More detailed recommendations with NLTK integration
2. **Image Service Fallbacks**: Ensures image generation never fails
3. **Content Formatting**: Better markdown to HTML conversion for blog posts
4. **Trend Service Caching**: Reduces API calls and handles rate limiting
5. **Duplicate Prevention**: Ensures similar articles aren't published on the same day
6. **Auto Image Cleanup**: Clears image directory after successful posting to save space
7. **Removed Google Trends**: Shifted to more reliable news sources for trending topics
8. **Heartbeat Mechanism**: Prevents HuggingFace Spaces from going to sleep by generating blogs at configurable intervals

## Monetization Features

The system implements comprehensive monetization strategies for blog content:

### Ad Formats and Placement

- **Banner & Leaderboard Ads**: Optimally placed wide format ads ("wide fellas")
- **Skyscraper Ads**: Vertical ads ("long lads") placed alongside content
- **Rectangle Ads**: Medium-sized ads integrated within content
- **Interstitial Ads**: Full-page ads displayed at strategic points

### Revenue Models

- **CPM (Cost Per Thousand Impressions)**: Earn based on ad views
- **CPA (Cost Per Action/Click)**: Earn when users interact with ads

### Optimization Strategies

- **Content-Length Optimization**: Longer content creates more opportunities for ad placement
- **Audience Targeting**: Ad relevance increases through demographic analysis
- **Advertiser Relationships**: Direct advertiser connections yield better rates than networks
- **Ethical Considerations**: Configurable density and content-appropriate ad filtering

### Integration Methods

- **Ad Networks**: Ready to integrate with Google Ads, Carbon, and other networks
- **Direct Partnerships**: Support for custom direct advertiser relationships

## Affiliate Product Integration

### Setting Up Your Affiliate Products Spreadsheet

The blog monetization system can integrate affiliate products from your Google Spreadsheet. Follow these steps to set it up:

1. **Create a Google Spreadsheet** with the following columns:

   - Product Name
   - Description
   - Affiliate Link
   - Image URL
   - Category (comma-separated tags)
   - Commission
   - Price

2. **Share the spreadsheet** with your service account email (found in your `.env` file under `GA_CLIENT_EMAIL` or in your service account credentials file).

3. **Set the environment variables** in your `.env` file:

   ```
   AFFILIATE_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit?usp=sharing
   USE_SERVICE_ACCOUNT=true
   AFFILIATE_SHEET_NAME=Products  # Optional: Name of the sheet tab with your products
   ```

4. **Test the integration** by running:
   ```
   python test_spreadsheet_fetch.py
   python test_affiliate_products.py
   ```

If you don't have a spreadsheet set up, the system will use sample affiliate products for testing purposes.

### Service Account Setup

To use the Google Sheets integration, you need a service account:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API
4. Create a service account with "Editor" permissions
5. Create and download a JSON key for the service account

#### Development Environment

6. Save the JSON key as `service-account.json` in the project root directory
7. Share your Google Sheets with the service account email address

#### Production Environment

6. Convert your service account JSON to an environment variable format:
   ```bash
   python helpers/convert_service_account_to_env.py
   ```
7. Add the output to your `.env` file or set it as an environment variable named `GOOGLE_SERVICE_ACCOUNT_INFO`
8. Share your Google Sheets with the service account email address

The application will automatically use the environment variable if available, or fall back to the file-based approach if needed.

For detailed instructions on using environment variables in different deployment scenarios, see:

- [Environment Variables Guide](docs/environment_variables.md)
- [HuggingFace Spaces Deployment Guide](docs/huggingface_spaces.md)
- Helper script: `python helpers/set_env_variables.py --help`

## Features

### Autonomous Blog Generation

- **Trend Detection:** Automatically identifies trending topics from Google News and other sources
- **Scheduled Publishing:** Configurable schedule for automatic blog generation and posting
- **Zero-Touch Operation:** End-to-end process from topic selection to social sharing

### Content Generation

- **AI-Powered Blog Creation:** Generate blog content based on trending topics using Google's Gemini API
- **Prompt Engineering:** Enhanced prompts for better blog structure and SEO
- **Content Formatting:** Markdown to HTML conversion with enhanced formatting

### SEO Optimization

- **Keyword Analysis:** Automatic detection of potential keywords from generated content
- **Keyword Density Calculation:** Monitors keyword density to prevent overuse
- **Word Count Validation:** Ensures content meets minimum length requirements for SEO
- **SEO Scoring:** Provides a quantitative assessment of content SEO quality (score out of 100)
- **Issue Detection:** Identifies potential SEO issues with recommendations for improvement

### Monetization

- **Ad Placement:** Strategic ad placement (banner, leaderboard, rectangle, skyscraper, interstitial)
- **Affiliate Product Integration:** Fetches affiliate products from Google Sheets and inserts relevant ads
- **Ad Relevance:** Selects the most relevant affiliate products for each blog post
- **Revenue Estimation:** Estimates potential ad revenue based on content and views

### Affiliate Product Integration

- **Google Sheets Integration:** Fetches products from a user-managed spreadsheet
- **Image Handling:** Uses product image URLs or fetches images from product pages
- **Catchphrase & Description:** Generates clickbait phrases and short descriptions for each ad
- **No Products, No Ads:** If no products are available, no affiliate ads are shown

### Image Generation

- **AI Image Service:** Generates or fetches relevant images for blog posts
- **Image Directory Management:** Cleans up images after publishing

### Publishing & Social Sharing

- **Blogger Integration:** Publishes content to Blogger with formatting intact
- **Social Sharing (Logging):** Logs social sharing activity (actual sharing disabled for safety)

### Automation & Logging

- **Automation Service:** Schedules and manages blog generation and publishing
- **Duplicate Prevention:** Prevents duplicate blogs on the same or similar news
- **Logging:** Logs ad placements, strategies, automation activity, and errors

### Testing & Extensibility

- **Test Suite:** Includes scripts for testing all major features (ad integration, SEO, image, spreadsheet, etc.)
- **Extensible Architecture:** Modular services for easy extension and customization
