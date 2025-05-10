import os
import requests
import urllib.parse
from dotenv import load_dotenv
import json
import random
from datetime import datetime
import shutil

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class ImageService:
    def __init__(self):
        self.unsplash_api_key = os.environ.get("UNSPLASH_API_KEY", "")
        self.output_dir = os.environ.get("IMAGE_OUTPUT_DIR", "./images")
        self.fallback_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fallback_images")
        
        # Create fallback directory if it doesn't exist
        os.makedirs(self.fallback_dir, exist_ok=True)
        
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
                print(f"Unsplash API Error: {response.text}")
                return self._use_fallback_image(prompt)
                
            data = response.json()
            
            # If no results, use a generic fallback query
            if len(data.get("results", [])) == 0:
                fallback_queries = ["blogging", "writing", "content", "business"]
                fallback_query = random.choice(fallback_queries)
                
                url = f"https://api.unsplash.com/search/photos?query={fallback_query}&per_page=5"
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    print(f"Unsplash API Error (fallback): {response.text}")
                    return self._use_fallback_image(prompt)
                    
                data = response.json()
            
            # Pick a random image from the results
            results = data.get("results", [])
            if not results:
                return self._use_fallback_image(prompt)
                
            image = random.choice(results)
            image_url = image["urls"]["regular"]
            
            # Download the image
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            image_path = os.path.join(self.output_dir, f"blog_image_{timestamp}.jpg")
            
            img_response = requests.get(image_url)
            
            if img_response.status_code != 200:
                print(f"Failed to download image from Unsplash: {img_response.status_code}")
                return self._use_fallback_image(prompt)
                
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
            return self._use_fallback_image(prompt)
    
    def _use_fallback_image(self, prompt):
        """Use a local fallback image when Unsplash API fails"""
        try:
            # Create default fallback images if none exist
            self._ensure_fallback_images_exist()
            
            # Get list of fallback images
            fallback_images = [f for f in os.listdir(self.fallback_dir) 
                              if f.endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(self.fallback_dir, f))]
            
            if not fallback_images:
                return None
                
            # Select a random fallback image
            selected_image = random.choice(fallback_images)
            fallback_path = os.path.join(self.fallback_dir, selected_image)
            
            # Copy to output directory with a new name
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_path = os.path.join(self.output_dir, f"fallback_image_{timestamp}.jpg")
            
            shutil.copy2(fallback_path, output_path)
            
            # Create attribution metadata
            attribution = {
                "source": "Local Fallback",
                "note": "This is a fallback image used when external API calls fail"
            }
            
            attribution_path = output_path + ".json"
            with open(attribution_path, "w") as f:
                json.dump(attribution, f, indent=2)
                
            return output_path
            
        except Exception as e:
            print(f"Error using fallback image: {str(e)}")
            return None
    
    def _ensure_fallback_images_exist(self):
        """Ensure there are some fallback images available"""
        # Check if there are any images in the fallback directory
        fallback_images = [f for f in os.listdir(self.fallback_dir) 
                          if f.endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(self.fallback_dir, f))]
        
        # If no fallback images exist, create a text-based image with a placeholder
        if not fallback_images:
            try:
                # This would normally create placeholder images, but we'll leave it empty for now
                # In a real implementation, you could use a library like Pillow to generate simple images
                pass
            except Exception as e:
                print(f"Error creating fallback images: {str(e)}")

image_service = ImageService()