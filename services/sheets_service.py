"""
Google Sheets integration for fetching affiliate product data.
"""
import os
import json
from typing import List, Dict, Any, Optional
import gspread
from gspread.exceptions import SpreadsheetNotFound, NoValidUrlKeyFound, APIError
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GoogleSheetsService:
    """
    Service for interacting with Google Sheets API.
    Handles authentication and data fetching for affiliate products.
    """
    
    def __init__(self):
        """Initialize the Google Sheets service with required credentials"""
        self.creds = None
        self.client = None
        
        # Directory for storing credentials
        self.creds_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "credentials")
        os.makedirs(self.creds_dir, exist_ok=True)
        
        # Paths for credential files
        self.service_account_file = os.path.join(self.creds_dir, "service-account.json")
        self.oauth_token_file = os.path.join(self.creds_dir, "token.json")
        self.oauth_credentials_file = os.path.join(self.creds_dir, "credentials.json")
        
        # Scopes for Google Sheets API
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        
    def authenticate(self, use_service_account: bool = True) -> bool:
        """
        Authenticate with Google Sheets API.
        
        Args:
            use_service_account: If True, use service account auth, otherwise use OAuth
            
        Returns:
            bool: True if authentication was successful
        """
        try:
            # Check environment setting if not explicitly provided
            if os.getenv('USE_SERVICE_ACCOUNT') is not None:
                use_service_account = os.getenv('USE_SERVICE_ACCOUNT').lower() == 'true'
            
            if use_service_account and os.path.exists(self.service_account_file):
                # Service Account authentication (preferred for server applications)
                self.creds = service_account.Credentials.from_service_account_file(
                    self.service_account_file, scopes=self.scopes
                )
                self.client = gspread.authorize(self.creds)
                print("Authenticated with Google Sheets API using service account")
                return True
                
            else:
                # OAuth authentication flow (for user-authenticated access)
                if os.path.exists(self.oauth_token_file):
                    self.creds = Credentials.from_authorized_user_info(
                        json.loads(open(self.oauth_token_file, 'r').read()),
                        self.scopes
                    )
                
                # If credentials don't exist or are invalid, run the OAuth flow
                if not self.creds or not self.creds.valid:
                    if self.creds and self.creds.expired and self.creds.refresh_token:
                        self.creds.refresh(Request())
                    else:
                        if not os.path.exists(self.oauth_credentials_file):
                            print("OAuth credentials.json file not found. Please download it from Google Cloud Console.")
                            return False
                            
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.oauth_credentials_file, self.scopes
                        )
                        self.creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for future runs
                    with open(self.oauth_token_file, 'w') as token:
                        token.write(self.creds.to_json())
                
                self.client = gspread.authorize(self.creds)
                print("Authenticated with Google Sheets API using OAuth")
                return True
                
        except Exception as e:
            print(f"Error authenticating with Google Sheets API: {str(e)}")
            return False
    
    def get_spreadsheet_data(self, spreadsheet_url: str, worksheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch data from a Google Spreadsheet.
        
        Args:
            spreadsheet_url: URL of the Google Spreadsheet
            worksheet_name: Name of the worksheet to fetch (if None, uses first worksheet)
            
        Returns:
            List of dictionaries, each representing a row in the spreadsheet
        """
        if not self.client:
            if not self.authenticate():
                print("Failed to authenticate with Google Sheets API")
                return []
        
        try:
            # Open the spreadsheet
            spreadsheet = self.client.open_by_url(spreadsheet_url)
            
            # Get the specified worksheet or default to first
            if worksheet_name:
                worksheet = spreadsheet.worksheet(worksheet_name)
            else:
                worksheet = spreadsheet.sheet1
            
            # Get all records as dictionaries
            records = worksheet.get_all_records()
            
            print(f"Successfully fetched {len(records)} rows from Google Spreadsheet")
            return records
            
        except SpreadsheetNotFound:
            print(f"Error: Spreadsheet not found at URL: {spreadsheet_url}")
            print("Please check the URL in your .env file")
            return []
        except NoValidUrlKeyFound:
            print(f"Error: Invalid spreadsheet URL: {spreadsheet_url}")
            print("Please make sure the URL is correctly formatted")
            return []
        except APIError as api_error:
            if "The caller does not have permission" in str(api_error):
                client_email = os.environ.get("GA_CLIENT_EMAIL", "service-account@example.com")
                print(f"Error: The service account {client_email} doesn't have permission to access this spreadsheet")
                print(f"Please share your spreadsheet with: {client_email}")
                print("For help, see docs/spreadsheet_sharing.md")
            else:
                print(f"Google Sheets API Error: {str(api_error)}")
            return []
        except Exception as e:
            print(f"Error fetching spreadsheet data: {str(e)}")
            return []
    
    def fetch_affiliate_products(self, spreadsheet_url: str, worksheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch affiliate products from a Google Spreadsheet and format them for use.
        
        Args:
            spreadsheet_url: URL of the Google Spreadsheet
            worksheet_name: Name of the worksheet to fetch (if None, uses first worksheet)
            
        Returns:
            List of affiliate product dictionaries
        """        
        # Fetch raw spreadsheet data
        raw_products = self.get_spreadsheet_data(spreadsheet_url, worksheet_name)
        
        if not raw_products:
            print("No products found in spreadsheet. Returning empty list.")
            return []
        
        # Format the products based on the spreadsheet structure
        formatted_products = []
        
        for row in raw_products:
            # Check if Affiliate Links column exists - this is our minimal requirement
            if 'Affiliate Links' in row and row['Affiliate Links'].strip():
                # Create a product with just the URL, other fields will be extracted by visiting the URL
                product = {
                    "url": row['Affiliate Links'].strip(),
                    "product_name": f"Product {len(formatted_products)+1}",  # Default name
                    "description": "",  # Empty description
                    "price": ""  # Empty price
                }
                formatted_products.append(product)
            # Also check for singular form as fallback
            elif 'Affiliate Link' in row and row['Affiliate Link'].strip():
                product = {
                    "url": row['Affiliate Link'].strip(),
                    "product_name": row.get('Product Name', f"Product {len(formatted_products)+1}"),
                    "description": row.get('Description', ''),
                    "price": row.get('Price', '')
                }
                formatted_products.append(product)
        
        print(f"Formatted {len(formatted_products)} affiliate products from spreadsheet")
        
        # If no valid products were found, return empty list
        if not formatted_products:
            print("No valid products found in spreadsheet. Returning empty list.")
            return []
            
        return formatted_products

    def _get_sample_products(self) -> List[Dict[str, Any]]:
        """
        Get sample affiliate products for testing or when spreadsheet fails.
        This method is disabled and now returns an empty list.
        
        Returns:
            Empty list
        """
        # Return empty list instead of sample products
        return []

# Singleton instance
google_sheets_service = GoogleSheetsService()