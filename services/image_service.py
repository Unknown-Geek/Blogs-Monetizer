import os
import requests
import urllib.parse
from dotenv import load_dotenv
import json
import random
from datetime import datetime

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class ImageService:
    def __init__(self):
        self.unsplash_api_key = os.environ.get("UNSPLASH_API_KEY", "")
        self.output_dir = os.environ.get("IMAGE_OUTPUT_DIR", "./images")
        
    def generate_image(self, prompt):
        """Get a relevant image from Unsplash based on the prompt"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Sanitize the prompt for use in API query
            query = urllib.parse.quote(prompt)
            
            # Call Unsplash API to search for relevant images
            url = f"https://api.unsplash.com/search/photos?query={query}&per_page=5"
            headers = {"Authorization": f"Client-ID {self.unsplash_api_key}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Unsplash API Error: {response.text}")
                
            data = response.json()
            
            # If no results, use a generic fallback query
            if len(data.get("results", [])) == 0:
                fallback_queries = ["blogging", "writing", "content", "business"]
                fallback_query = random.choice(fallback_queries)
                
                url = f"https://api.unsplash.com/search/photos?query={fallback_query}&per_page=5"
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    raise Exception(f"Unsplash API Error (fallback): {response.text}")
                    
                data = response.json()
            
            # Pick a random image from the results
            results = data.get("results", [])
            if not results:
                raise Exception("No images found on Unsplash for the given prompt")
                
            image = random.choice(results)
            image_url = image["urls"]["regular"]
            
            # Download the image
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            image_path = os.path.join(self.output_dir, f"blog_image_{timestamp}.jpg")
            
            img_response = requests.get(image_url)
            
            if img_response.status_code != 200:
                raise Exception(f"Failed to download image from Unsplash: {img_response.status_code}")
                
            # Save the image to disk
            with open(image_path, "wb") as f:
                f.write(img_response.content)
                
            # Add attribution metadata
            attribution = {
                "photographer": image["user"]["name"],
                "photographer_url": image["user"]["links"]["html"],
                "source": "Unsplash",
                "source_url": image["links"]["html"]
            }
            
            attribution_path = image_path + ".json"
            with open(attribution_path, "w") as f:
                json.dump(attribution, f, indent=2)
                
            return image_path
            
        except Exception as e:
            print(f"Error getting image from Unsplash: {str(e)}")
            # Return a path to a placeholder image or None
            return None

image_service = ImageService()