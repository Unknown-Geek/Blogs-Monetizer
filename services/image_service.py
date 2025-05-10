# filepath: e:\Projects\Monetize-blogs\services\image_service.py
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
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self.output_dir = os.environ.get("IMAGE_OUTPUT_DIR", "./images")
        self.fallback_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fallback_images")
        
        # Create fallback directory if it doesn't exist
        os.makedirs(self.fallback_dir, exist_ok=True)
        
    def _generate_relevant_keywords(self, topic):
        """
        Generate relevant image search keywords using Gemini API based on the blog topic
        """
        if not self.gemini_api_key:
            print("Gemini API key not available, using original topic as keywords")
            return [topic]
            
        try:
            prompt = f"""
            Based on the blog topic: "{topic}"
            
            Generate 3-5 SPECIFIC image search keywords or short phrases that would produce highly relevant, 
            visually appealing images when used with the Unsplash API. 
            
            Focus on concrete, visual concepts rather than abstract terms.
            Return only the keywords, one per line, with no numbering or additional text.
            """
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "topK": 40,
                    "topP": 0.9,
                    "maxOutputTokens": 100,
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                print(f"Gemini API Error for image keywords: {response.status_code}")
                return [topic]
                
            response_data = response.json()
            
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                content = response_data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Clean up the response, keeping only valid lines
                keywords = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Add the original topic as well, to ensure we have a variety of options
                if topic not in keywords:
                    keywords.append(topic)
                    
                print(f"Generated image keywords: {keywords}")
                return keywords
            else:
                print("No content returned from Gemini API for image keywords")
                return [topic]
                
        except Exception as e:
            print(f"Error generating image keywords with Gemini: {str(e)}")
            return [topic]
            
    def generate_image(self, prompt):
        """Get a relevant image from Unsplash based on the prompt"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Get enhanced keywords for the prompt
            keywords = self._generate_relevant_keywords(prompt)
            
            # Try each keyword until we find a suitable image
            for keyword in keywords:
                # Sanitize the keyword for use in API query
                query = urllib.parse.quote(keyword)
                
                # Call Unsplash API to search for relevant images
                url = f"https://api.unsplash.com/search/photos?query={query}&per_page=10"
                headers = {"Authorization": f"Client-ID {self.unsplash_api_key}"}
                
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    print(f"Unsplash API Error for keyword '{keyword}': {response.text}")
                    continue
                    
                data = response.json()
                
                # If we got results, use them
                results = data.get("results", [])
                if results:
                    # Pick a random image from the results
                    image = random.choice(results)
                    image_url = image["urls"]["regular"]
                    
                    # Download the image
                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                    image_path = os.path.join(self.output_dir, f"blog_image_{timestamp}.jpg")
                    
                    img_response = requests.get(image_url)
                    
                    if img_response.status_code != 200:
                        print(f"Failed to download image from Unsplash: {img_response.status_code}")
                        continue
                        
                    # Save the image to disk
                    with open(image_path, "wb") as f:
                        f.write(img_response.content)
                        
                    # Add attribution metadata
                    attribution = {
                        "photographer": image["user"]["name"],
                        "photographer_url": image["user"]["links"]["html"],
                        "source": "Unsplash",
                        "source_url": image["links"]["html"],
                        "keyword_used": keyword,
                        "original_topic": prompt
                    }
                    
                    attribution_path = image_path + ".json"
                    with open(attribution_path, "w") as f:
                        json.dump(attribution, f, indent=2)
                        
                    return image_path
            
            # If no keywords produced viable results, try generic fallback
            fallback_queries = ["blogging", "writing", "content", "business"]
            fallback_query = random.choice(fallback_queries)
            
            url = f"https://api.unsplash.com/search/photos?query={fallback_query}&per_page=5"
            headers = {"Authorization": f"Client-ID {self.unsplash_api_key}"}
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Unsplash API Error (fallback): {response.text}")
                return self._use_fallback_image(prompt)
                
            data = response.json()
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
                "source_url": image["links"]["html"],
                "keyword_used": fallback_query,
                "original_topic": prompt,
                "note": "Used fallback keyword"
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
                "note": "This is a fallback image used when external API calls fail",
                "original_topic": prompt
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
