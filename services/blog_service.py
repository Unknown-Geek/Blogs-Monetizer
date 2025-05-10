import requests
import os
from io import BytesIO
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class BlogService:
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
        self.blogger_id = os.environ.get("BLOGGER_ID", "YOUR_BLOGGER_ID")
        
        # Blogger OAuth credentials
        self.blogger_client_id = os.environ.get("BLOGGER_CLIENT_ID", "")
        self.blogger_client_secret = os.environ.get("BLOGGER_CLIENT_SECRET", "")
        self.blogger_refresh_token = os.environ.get("BLOGGER_REFRESH_TOKEN", "")
        
    def generate_blog_content(self, prompt):
        """Generate blog content using Google's Gemini API"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.9,
                "maxOutputTokens": 1000,
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Gemini API Error: {response.text}")
        
        # Extract the content from the Gemini response
        response_data = response.json()
        
        try:
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                content = response_data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise Exception("No content returned from Gemini API")
                
            # Add basic HTML formatting
            formatted_content = self._format_content(content)
            return formatted_content
        except Exception as e:
            raise Exception(f"Error processing Gemini API response: {str(e)}")
        
    def _format_content(self, content):
        """Add basic HTML formatting to the generated content"""
        paragraphs = content.split("\n\n")
        formatted_paragraphs = []
        for p in paragraphs:
            if p.startswith("# "):
                # This is a header
                formatted_paragraphs.append(f"<h1>{p[2:]}</h1>")
            elif p.startswith("## "):
                # This is a subheader
                formatted_paragraphs.append(f"<h2>{p[3:]}</h2>")
            elif p.strip():
                # This is a regular paragraph
                formatted_paragraphs.append(f"<p>{p}</p>")
        
        return "\n".join(formatted_paragraphs)

    def publish_blog(self, title, content, image_path, labels):
        """Publish blog content to Blogger platform"""
        try:
            # Create credentials from environment variables
            if self.blogger_client_id and self.blogger_client_secret and self.blogger_refresh_token:
                # Create OAuth credentials from environment variables
                credentials = Credentials(
                    None,  # No access token initially
                    refresh_token=self.blogger_refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=self.blogger_client_id,
                    client_secret=self.blogger_client_secret
                )
            else:
                raise Exception("Blogger credentials not available in environment variables")
                
            service = build("blogger", "v3", credentials=credentials)

            # Upload image to Blogger if path is provided
            image_url = None
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as img:
                    media = service.media().insert(
                        blogId=self.blogger_id,
                        media_body=BytesIO(img.read()),
                        media_mime_type="image/png",
                    ).execute()
                    image_url = media.get("url")

            # Prepare the post content
            post_content = content
            if image_url:
                post_content = f"<img src='{image_url}' alt='Blog Image'/>\n{content}"

            # Create the post
            post = {
                "kind": "blogger#post",
                "blog": {"id": self.blogger_id},
                "title": title,
                "content": post_content,
            }
            
            # Add labels if provided
            if labels:
                post["labels"] = labels

            # Insert the post
            result = service.posts().insert(blogId=self.blogger_id, body=post).execute()
            return result
            
        except Exception as e:
            raise Exception(f"Failed to publish blog: {str(e)}")

blog_service = BlogService()
