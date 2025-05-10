import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    RunReportResponse
)
import json
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class AnalyticsService:
    """Service for interacting with Google Analytics 4 for blog post analytics"""
      def __init__(self):
        # GA4 configuration
        self.measurement_id = os.environ.get("GA_MEASUREMENT_ID", "")  # GA4 Measurement ID (G-XXXXXXXXXX)
        
        # Service account credentials from environment variables
        self.client_email = os.environ.get("GA_CLIENT_EMAIL", "")
        self.private_key = os.environ.get("GA_PRIVATE_KEY", "")
        self.project_id = os.environ.get("GA_PROJECT_ID", "")
        self.private_key_id = os.environ.get("GA_PRIVATE_KEY_ID", "")
        
        # Extract property ID from measurement ID or environment
        self.property_id = os.environ.get("GA_PROPERTY_ID", "") or self._extract_property_id(self.measurement_id)
        
        # Log initialization state (but not sensitive values)
        print(f"Analytics Service initialized with measurement ID: {self.measurement_id}")
        print(f"Using environment credentials: {bool(self.client_email and self.private_key)}")
    
    def _extract_property_id(self, measurement_id: str) -> str:
        """
        Extract the numeric property ID from the GA4 measurement ID if possible
        For GA4, the property ID might be extractable from the measurement ID
        
        Args:
            measurement_id: The GA4 measurement ID (e.g., "G-XXXXXXXXXX")
            
        Returns:
            The property ID or empty string if not extractable
        """
        # This is a placeholder - in a real implementation, you might have
        # logic to extract the property ID from the measurement ID or look it up
        return ""
    
    def _get_analytics_client(self):
        """
        Get a Google Analytics Data API client using environment variables
        """
        try:
            if self.client_email and self.private_key:
                # Use environment variables
                print("Using environment variables for Google Analytics")
                
                # Fix newlines in private key if they're escaped
                private_key = self.private_key
                if "\\n" in private_key:
                    private_key = private_key.replace("\\n", "\n")
                
                # Create credentials object from environment variables
                credentials_dict = {
                    "type": "service_account",
                    "project_id": self.project_id,
                    "private_key_id": self.private_key_id,
                    "private_key": private_key,
                    "client_email": self.client_email,
                    "client_id": os.environ.get("GA_CLIENT_ID", ""),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.client_email.replace('@', '%40')}",
                    "universe_domain": "googleapis.com"
                }
                
                credentials = service_account.Credentials.from_service_account_info(credentials_dict)
                return BetaAnalyticsDataClient(credentials=credentials)
            else:
                print("Warning: No GA credentials found in environment variables, analytics will be unavailable")
                return None
        except Exception as e:
            print(f"Error setting up Analytics client: {str(e)}")
            return None
            
    def get_top_posts(self, limit: int = 5, days: int = 30) -> List[Dict]:
        """
        Get the top performing blog posts based on pageviews
        
        Args:
            limit: Number of posts to return
            days: Time period in days
            
        Returns:
            List of top posts with metrics
        """
        try:
            # Set up Analytics Data API client
            client = self._get_analytics_client()
            
            # Make sure we have a client and property ID
            if not client or not self.property_id:
                return []
                
            # Create request to get page view data
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[
                    Dimension(name="pagePath"),
                    Dimension(name="pageTitle")
                ],
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="engagementRate")
                ],
                date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")]
            )
            
            # Execute the request
            response = client.run_report(request)
            
            # Process the results
            posts = []
            for row in response.rows[:limit]:
                post = {
                    "path": row.dimension_values[0].value,
                    "title": row.dimension_values[1].value,
                    "views": int(row.metric_values[0].value),
                    "engagement_rate": float(row.metric_values[1].value)
                }
                posts.append(post)
                
            return posts
            
        except Exception as e:
            print(f"Error fetching analytics data: {str(e)}")
            return []
            
    def get_analytics_summary(self) -> Dict:
        """
        Get a summary of blog analytics
        
        Returns:
            Dictionary with summary metrics
        """
        try:
            # Set up Analytics Data API client
            client = self._get_analytics_client()
            
            # Make sure we have a client and property ID
            if not client or not self.property_id:
                return {
                    "error": "Property ID not configured or analytics client unavailable",
                    "total_pageviews": 0,
                    "avg_engagement_time": 0,
                    "unique_visitors": 0
                }
                
            # Create request to get summary metrics
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="totalUsers"),
                    Metric(name="averageSessionDuration")
                ],
                date_ranges=[DateRange(start_date="30daysAgo", end_date="today")]
            )
            
            # Execute the request
            response = client.run_report(request)
            
            # Process the results
            if len(response.rows) > 0:
                row = response.rows[0]
                return {
                    "total_pageviews": int(row.metric_values[0].value),
                    "unique_visitors": int(row.metric_values[1].value),
                    "avg_engagement_time": float(row.metric_values[2].value),
                    "period": "Last 30 days"
                }
            else:
                return {
                    "total_pageviews": 0,
                    "unique_visitors": 0,
                    "avg_engagement_time": 0,
                    "period": "Last 30 days",
                    "note": "No data available"
                }
                
        except Exception as e:
            print(f"Error fetching analytics summary: {str(e)}")
            return {
                "error": str(e),
                "total_pageviews": 0,
                "unique_visitors": 0,
                "avg_engagement_time": 0
            }
            
    def get_traffic_sources(self) -> Dict:
        """
        Get traffic sources breakdown
        
        Returns:
            Dictionary with traffic source data
        """
        try:
            # Set up Analytics Data API client
            client = self._get_analytics_client()
            
            # Make sure we have a client and property ID
            if not client or not self.property_id:
                return {"sources": [], "error": "Property ID not configured or analytics client unavailable"}
                
            # Create request to get traffic source data
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[
                    Dimension(name="sessionSource")
                ],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="screenPageViews")
                ],
                date_ranges=[DateRange(start_date="30daysAgo", end_date="today")]
            )
            
            # Execute the request
            response = client.run_report(request)
            
            # Process the results
            sources = []
            for row in response.rows:
                source = {
                    "source": row.dimension_values[0].value,
                    "sessions": int(row.metric_values[0].value),
                    "pageviews": int(row.metric_values[1].value)
                }
                sources.append(source)
                
            return {"sources": sources}
            
        except Exception as e:
            print(f"Error fetching traffic sources: {str(e)}")
            return {"sources": [], "error": str(e)}

analytics_service = AnalyticsService()

# Example standalone usage
if __name__ == "__main__":
    summary = analytics_service.get_analytics_summary()
    print(f"Analytics Summary: {summary}")
    
    top_posts = analytics_service.get_top_posts()
    print(f"Top Posts: {top_posts}")
