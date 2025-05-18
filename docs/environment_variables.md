# Using Environment Variables for Service Account Credentials

## Overview

For production deployments, storing service account credentials in environment variables instead of files provides better security and easier configuration management. This guide explains how to set up and use environment variables for your Google service account credentials.

> **Note**: As part of the recent project restructuring, all credentials are now managed through environment variables for production, and service account files are stored in the project root directory for development only.

## Moving from File-Based to Environment-Based Authentication

The application can now use service account credentials from either:

1. A file (recommended for development)
2. Environment variables (recommended for production)

## Setting Up Environment Variables

### Using the Helper Script

We've included a helper script that makes setting up environment variables easy:

```bash
# Development mode - updates your .env file
python helpers/set_env_variables.py --mode=dev

# Production mode - outputs commands to set environment variables
python helpers/set_env_variables.py --mode=prod

# For specific platforms - e.g., Docker, Heroku, GitHub Actions
python helpers/set_env_variables.py --mode=prod --platform=docker
python helpers/set_env_variables.py --mode=prod --platform=heroku
python helpers/set_env_variables.py --mode=prod --platform=github
```

### Manual Setup

If you prefer to set up environment variables manually:

1. Convert your service account JSON file to a single line:

   ```bash
   python helpers/convert_service_account_to_env.py
   ```

2. Copy the output and set it as an environment variable named `GOOGLE_SERVICE_ACCOUNT_INFO`

3. Also set these additional environment variables from your service account:
   - `GA_CLIENT_EMAIL` - The service account email (e.g., `blogs-monetizer-152@blogs-monetizer.iam.gserviceaccount.com`)
   - `GA_PROJECT_ID` - Your Google Cloud project ID
   - `USE_SERVICE_ACCOUNT` - Set to "true"

## Docker Deployment

When deploying with Docker, use the environment variables directly with the Docker run command:

```bash
docker run -e GOOGLE_SERVICE_ACCOUNT_INFO="..." -e GA_CLIENT_EMAIL="..." your-image-name
```

Alternatively, use an environment file:

```bash
docker run --env-file .env your-image-name
```

## Security Considerations

1. **Never commit** your .env file or service account JSON file to version control
2. Use secret management services provided by your hosting platform
3. Restrict access to environment variable configurations
4. Regularly rotate service account credentials

## Heartbeat Configuration for HF Spaces

For preventing HuggingFace Spaces from going to sleep due to inactivity:

1. Set `ENABLE_HEARTBEAT` to "true" (enabled by default)
2. Configure `HEARTBEAT_INTERVAL_MINUTES` to control frequency (default: 15 minutes)

These settings ensure periodic activity by generating blogs at the specified interval.

## Troubleshooting

If authentication fails:

1. Verify that the `GOOGLE_SERVICE_ACCOUNT_INFO` environment variable contains valid JSON
2. Confirm that you've shared your Google Sheet with the service account email
3. Check that the `USE_SERVICE_ACCOUNT` environment variable is set to "true"
4. For Docker deployments, ensure quotes are properly escaped
