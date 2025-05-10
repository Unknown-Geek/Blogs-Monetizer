---
title: Blogs Monetizer
emoji: 🐢
colorFrom: red
colorTo: green
sdk: docker
pinned: false
---

# Blogs Monetizer 🚀

A comprehensive system for generating, optimizing, and monetizing blog content with AI assistance.

## Overview

This system automates the entire process of blog content creation and publication:

1. **Trend Detection**: Automatically discovers trending topics from Google Trends, news sources, and social media
2. **Content Generation**: Creates high-quality blog posts using Google's Gemini API
3. **SEO Optimization**: Analyzes and improves content for search engine visibility
4. **Image Generation**: Sources relevant images from Unsplash with proper attribution
5. **Publishing**: Publishes content to Blogger with formatting intact
6. **Social Sharing**: Shares new posts on Twitter and other platforms
7. **Automation**: Schedules multiple posts per day with configurable frequency

## System Architecture

The system is built with a modular service-based architecture:

- **API Layer**: FastAPI application providing endpoints for all functionality
- **Service Layer**: Specialized services for each major function
- **Automation**: Scheduled processes for autonomous operation

### Core Services

- `trend_service.py`: Detects trending topics across various sources
- `blog_service.py`: Generates and publishes blog content
- `seo_service.py`: Analyzes and optimizes content for SEO
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
  - Twitter API (optional for social sharing)

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
- `MIN_HOURS_BETWEEN_POSTS`: Minimum hours between posts (default: 8)
- `MIN_SEO_SCORE`: Minimum SEO score to accept (default: 70)
- `IMAGE_OUTPUT_DIR`: Directory for storing generated images

## Improvements

Recent improvements to the system include:

1. **Enhanced SEO Analysis**: More detailed recommendations with NLTK integration
2. **Image Service Fallbacks**: Ensures image generation never fails
3. **Content Formatting**: Better markdown to HTML conversion for blog posts
4. **Trend Service Caching**: Reduces API calls and handles rate limiting
5. **Social Media Integration**: Better error handling and multi-platform support
