import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class BlogService:
    def __init__(self):
        self.gemini_api_key = "YOUR_GEMINI_API_KEY"
        self.blogger_id = "YOUR_BLOGGER_ID"

    def generate_blog_content(self, prompt):
        # ...existing code...
        return response.json()["content"]

    def publish_blog(self, title, content, image_path, labels):
        # ...existing code...
        return result

blog_service = BlogService()