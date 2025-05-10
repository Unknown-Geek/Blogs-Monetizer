# Monetize-blogs

A comprehensive platform for generating, optimizing, and monetizing blog content with AI assistance.

## Project Overview

Monetize-blogs is a platform designed to help content creators and bloggers streamline their content production workflow. It offers tools for generating blog content, optimizing it for search engines, creating relevant images, and publishing to platforms like Blogger with social media integration.

## Features

### Autonomous Blog Generation

- **Trend Detection**: Automatically identifies trending topics from Google Trends, Twitter, and News sources
- **Scheduled Publishing**: Configurable schedule for automatic blog generation and posting
- **Zero-Touch Operation**: Complete end-to-end process from topic selection to social sharing

### Content Generation

- **AI-Powered Blog Creation**: Generate blog content based on trending topics using Google's Gemini API
- **User-Friendly Interface**: Simple form-based input for manual blog topic ideas

### SEO Optimization

- **Keyword Analysis**: Automatic detection of potential keywords from generated content
- **Keyword Density Calculation**: Measures and monitors keyword density to prevent overuse
- **Word Count Validation**: Ensures content meets minimum length requirements for SEO
- **SEO Scoring**: Provides a quantitative assessment of content SEO quality (score out of 100)
- **Issue Detection**: Identifies potential SEO issues with recommendations for improvement

### Image Generation

- **AI Image Creation**: Generates relevant blog images based on descriptive prompts
- **Integration with Content**: Automatically includes generated images with blog content

### Publishing Capabilities

- **Blogger Integration**: Direct publishing to Blogger platform
- **Image Uploading**: Automatic image uploading to hosting platforms
- **Metadata Support**: Ability to add tags/labels to published content

### Social Media Integration

- **Twitter Sharing**: Automatically share blog posts on Twitter when published
- **Custom Messages**: Configure sharing messages with blog links

### Analytics

- **Google Analytics Integration**: Track blog performance metrics
- **Data Visualization**: Frontend component for displaying analytics (currently in development)

## Technical Architecture

### Backend (Python/Flask)

- **RESTful API**: Flask-based API with endpoints for all major features
- **Service-Based Architecture**: Modular services for blog, SEO, image, social media, trend detection, and automation
- **API Integrations**: Connectors for Gemini, Blogger, Google Analytics, Twitter, and trending topic sources
- **Scheduling System**: Background processes for automated content generation

### Frontend (React)

- **Modern UI**: React-based interface with Tailwind CSS styling
- **Component Structure**: Includes BlogForm, Preview, and Analytics components
- **Real-time Preview**: Immediate preview of generated blog content

## Project Status

The project is currently in active development with the following components implemented:

- ✅ SEO analysis service (fully implemented)
- ✅ Image generation service (fully implemented)
- ✅ Blog generation functionality (fully implemented)
- ✅ Frontend UI components (basic implementation)
- ✅ Backend API structure and endpoints
- ✅ Social media service (implemented for Twitter)
- ✅ Trend detection service (fully implemented)
- ✅ Automation service for scheduled posting (fully implemented)
- ⏳ Analytics dashboard (UI structure present, data integration pending)

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- API keys for: Gemini, Google (Blogger and Analytics), Twitter, News API

### Setup

1. Clone the repository
2. Set up the backend:

   ```powershell
   .\activate.bat
   ```

   This will:

   - Create a virtual environment
   - Install required Python packages
   - Set up the backend environment

3. Configure your API keys:

   ```powershell
   # Copy the .env template file and modify it with your API keys
   cd backend
   Copy-Item .env.template .env
   # Edit the .env file with your API keys
   ```

   Alternatively, you can set environment variables directly:

   ```powershell
   # Set environment variables for API keys
   $env:GEMINI_API_KEY="your_gemini_api_key"
   $env:BLOGGER_ID="your_blogger_id"
   $env:TWITTER_BEARER_TOKEN="your_twitter_bearer_token"
   $env:NEWS_API_KEY="your_news_api_key"
   ```

4. Start the backend server:

   ```powershell
   cd backend
   python app.py
   ```

5. Set up the frontend:
   ```powershell
   cd frontend
   npm install
   npm start
   ```

### Running Autonomous Blog Generator

You can run the autonomous blog generator in several ways:

1. **Run once immediately**:

   ```powershell
   python auto_blog.py --run-once
   ```

2. **Run on a schedule**:

   ```powershell
   python auto_blog.py --schedule --posts-per-day 2
   ```

3. **Use a custom configuration file**:

   ```powershell
   python auto_blog.py --config config.json --schedule
   ```

4. **API interface**:
   You can also control the automation through the REST API: - Start automation: `POST /api/automation/start`
   - Run once: `POST /api/automation/run-now`
   - Check status: `GET /api/automation/status`
   - Stop automation: `POST /api/automation/stop`
   - Get configuration: `GET /api/config`
   - Update configuration: `POST /api/config`

## Configuration Options

The autonomous blog generator supports these configuration options:

```json
{
  "posts_per_day": 1,
  "min_hours_between_posts": 8,
  "trending_sources": ["google", "news", "twitter"],
  "categories": ["technology", "business", "science"],
  "min_seo_score": 70
}
```

### Environment Variables

The application uses a `.env` file in the backend directory to manage configuration. Here are the key variables:

| Variable                | Description                                  | Default Value                            |
| ----------------------- | -------------------------------------------- | ---------------------------------------- |
| GEMINI_API_KEY          | Google Gemini API key for content generation | -                                        |
| BLOGGER_ID              | Your Blogger ID                              | -                                        |
| TWITTER_BEARER_TOKEN    | Twitter API bearer token                     | -                                        |
| NEWS_API_KEY            | News API key for trending topics             | -                                        |
| POSTS_PER_DAY           | Number of posts to generate per day          | 1                                        |
| MIN_HOURS_BETWEEN_POSTS | Minimum hours between posts                  | 8                                        |
| MIN_SEO_SCORE           | Minimum SEO score for a post to be published | 70                                       |
| IMAGE_MODEL             | Hugging Face model for image generation      | stabilityai/stable-diffusion-xl-base-1.0 |
| IMAGE_OUTPUT_DIR        | Directory to save generated images           | ./images                                 |

You can edit these values in the `.env` file or update them at runtime using the `/api/config` endpoint.

## Contributing

Contributions are welcome! Current priorities include:

- Enhancing the analytics dashboard
- Adding more social media integrations
- Improving error handling and user feedback
- Adding unit and integration tests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

- ⏳ Social media service (referenced but not fully implemented)
- ⏳ Analytics dashboard (UI structure present, data integration pending)
- ⏳ Comprehensive error handling and validation

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- API keys for: Gemini, Google (Blogger and Analytics), Twitter

### Setup

1. Clone the repository
2. Set up the backend:

   ```
   .\activate.bat
   ```

   This will:

   - Create a virtual environment
   - Install required Python packages
   - Set up the backend environment

3. Start the backend server:

   ```
   cd backend
   python app.py
   ```

4. Set up the frontend:

   ```
   cd frontend
   npm install
   npm start
   ```

5. Configure your API keys in the appropriate service files

## Contributing

Contributions are welcome! Current priorities include:

- Completing the social media service implementation
- Enhancing the analytics dashboard
- Improving error handling and user feedback
- Adding unit and integration tests

## License

This project is licensed under the MIT License - see the LICENSE file for details.
