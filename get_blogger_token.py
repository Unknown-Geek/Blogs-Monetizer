import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

def get_blogger_refresh_token():
    """
    Generate a refresh token for Blogger API access.
    
    This script will:
    1. Open a browser window for Google authentication
    2. Ask you to log in with your Google account
    3. Request permission to access your Blogger data
    4. Return a refresh token that can be used in your application
    """
    # Get client ID and secret from user input or environment
    client_id = os.environ.get("BLOGGER_CLIENT_ID") or input("Enter your Client ID: ")
    client_secret = os.environ.get("BLOGGER_CLIENT_SECRET") or input("Enter your Client Secret: ")
    
    # Configure the OAuth flow
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                "http://localhost:8080",
                "http://localhost"
            ]
        }
    }
    
    # Define the scopes needed
    SCOPES = ['https://www.googleapis.com/auth/blogger']
    
    try:
        # Create a flow instance to manage the OAuth 2.0 Authorization Flow
        flow = InstalledAppFlow.from_client_config(
            client_config, 
            scopes=SCOPES,
            redirect_uri="http://localhost:8080"
        )
        
        # Run the flow to get credentials
        credentials = flow.run_local_server(port=8080)
        
        # Print the refresh token
        print("\n=== YOUR BLOGGER REFRESH TOKEN ===")
        print(f"BLOGGER_REFRESH_TOKEN={credentials.refresh_token}")
        print("=================================\n")
        
        # Save credentials to a file for future reference
        with open('blogger_credentials.json', 'w') as f:
            token_data = {
                "refresh_token": credentials.refresh_token,
                "client_id": client_id,
                "client_secret": client_secret
            }
            json.dump(token_data, f, indent=4)
        
        print("Credentials saved to blogger_credentials.json")
        print("Add this refresh token to your .env file")
        
        return credentials.refresh_token
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    get_blogger_refresh_token()
