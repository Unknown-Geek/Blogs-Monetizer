# Google Sheets API Integration Guide

This guide explains how to set up Google Sheets API authentication to fetch affiliate product data.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

## Step 2: Create Service Account Credentials (Recommended for Server-Side Applications)

1. In your Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details and click "Create"
4. Grant the service account "Viewer" role (or more specific roles as needed)
5. Click "Done"
6. Click on the newly created service account
7. Go to the "Keys" tab
8. Click "Add Key" > "Create new key"
9. Choose "JSON" and click "Create"
10. The key file will be downloaded automatically
11. Rename this file to `service-account.json` and place it in the `credentials` folder

## Step 3: Share Your Spreadsheet with the Service Account

1. Open your Google Spreadsheet with affiliate products
2. Click the "Share" button
3. Add the service account email address. For this project, use:
   ```
   blogs-monetizer-152@blogs-monetizer.iam.gserviceaccount.com
   ```
4. Set permission to "Editor" and click "Send"

> **IMPORTANT**: This is a critical step. The service account MUST have access to your spreadsheet, or the integration will fail with "permission denied" errors.

## Step 4: Expected Spreadsheet Format

Your spreadsheet should have the following columns:

| Product Name | Description | Affiliate Link | Image URL   | Category  | Commission | Price  |
| ------------ | ----------- | -------------- | ----------- | --------- | ---------- | ------ |
| Product 1    | Description | https://...    | https://... | cat1,cat2 | 15%        | $99.99 |

Make sure:

- The first row contains headers exactly as shown above
- Categories are comma-separated
- All product URLs are valid
- Image URLs are direct links to images (can be tested in browser)

## Alternative: OAuth Authentication (For User-Based Access)

If you prefer OAuth authentication instead of a service account:

1. Create OAuth credentials in Google Cloud Console
2. Download the credentials JSON file
3. Rename it to `credentials.json` and place it in the `credentials` folder
4. Run the script, which will open a browser window for authentication
5. Grant the requested permissions
6. The access token will be saved as `token.json` for future use

## Usage

The system automatically uses service account authentication if the `service-account.json` file exists.
If not, it falls back to OAuth authentication if the `credentials.json` file exists.

When running the script, the spreadsheet URL should be:

```
https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit#gid=0
```

If authentication fails or no spreadsheet URL is provided, the system will use fallback sample products.
