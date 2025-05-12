import os
import requests
import urllib.parse
from dotenv import load_dotenv
import json
import random
from datetime import datetime
import shutil
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if (os.path.exists(dotenv_path)):
    load_dotenv(dotenv_path)

class ImageService:
    def extract_amazon_product_image(self, product_url, product_name):
        """Try to extract a high-quality image for an Amazon product"""
        import re
        import requests
        import os
        from datetime import datetime
        
        # Get product ID using various patterns
        patterns = [
            r'/dp/([A-Z0-9]{10})(?:/|\?|$)',  # Standard dp pattern
            r'/gp/product/([A-Z0-9]{10})(?:/|\?|$)',  # gp/product pattern
            r'/([A-Z0-9]{10})(?:/|\?|$)',  # Directly in URL
            r'ASIN=([A-Z0-9]{10})(?:&|$)'  # In query params
        ]
        
        product_id = None
        for pattern in patterns:
            match = re.search(pattern, product_url)
            if match:
                product_id = match.group(1)
                print(f"Extracted Amazon product ID: {product_id}")
                break
        
        if not product_id:
            return None
            
        # Try multiple high-quality image URL patterns
        image_formats = [
            f"https://m.media-amazon.com/images/I/{product_id}._AC_SL1500_.jpg",
            f"https://m.media-amazon.com/images/I/{product_id}._AC_UL1500_.jpg", 
            f"https://m.media-amazon.com/images/I/{product_id}._AC_SL1000_.jpg",
            f"https://m.media-amazon.com/images/I/{product_id}._SL1500_.jpg",
            f"https://m.media-amazon.com/images/I/{product_id}._SX1500_.jpg",
            f"https://images-na.ssl-images-amazon.com/images/I/{product_id}._AC_SL1500_.jpg",
            f"https://m.media-amazon.com/images/I/{product_id}.jpg"
        ]
        
        # Standard headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        # Try each image format
        for image_url in image_formats:
            try:
                # Check if the image exists
                response = requests.head(image_url, headers=headers, timeout=5)
                
                if response.status_code == 200 and 'content-length' in response.headers:
                    content_length = int(response.headers.get('content-length', 0))
                    
                    # Skip small images (likely icons)
                    if content_length < 10000:
                        continue
                        
                    print(f"Found Amazon product image: {image_url}")
                    
                    # Download the actual image
                    img_response = requests.get(image_url, headers=headers, timeout=10)
                    
                    # Save the image
                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                    safe_product_name = "".join(c if c.isalnum() else "_" for c in product_name[:50])
                    image_filename = f"product_amazon_{safe_product_name}_{timestamp}.jpg"
                    image_path = os.path.join(self.product_image_dir, image_filename)
                    
                    with open(image_path, "wb") as f:
                        f.write(img_response.content)
                        
                    print(f"Saved Amazon product image: {image_path}")
                    return image_path
            except Exception as e:
                print(f"Error fetching {image_url}: {str(e)}")
                continue
                
        # If we got here, none of the image formats worked
        return None
    

    def _extract_amazon_product_image(self, product_url, product_id, headers):
        """
        Extract a high-quality product image for Amazon products using various techniques.
        Returns the path to the saved image or None if no image could be found.
        """
        print(f"Trying to extract high-quality image for Amazon product ID: {product_id}")
        
        # List of possible image formats to try (ordered by preference)
        image_formats = [
            f"https://m.media-amazon.com/images/I/{product_id}.jpg",
            f"https://m.media-amazon.com/images/I/{product_id}._AC_SL1500_.jpg",
            f"https://m.media-amazon.com/images/I/{product_id}._AC_UL1500_.jpg",
            f"https://m.media-amazon.com/images/I/{product_id}._AC_SL1000_.jpg",
            f"https://m.media-amazon.com/images/I/{product_id}._SL1500_.jpg",
            f"https://m.media-amazon.com/images/I/{product_id}._SX1500_.jpg",
            f"https://images-na.ssl-images-amazon.com/images/I/{product_id}.jpg",
            f"https://images-na.ssl-images-amazon.com/images/I/{product_id}._AC_SL1500_.jpg"
        ]
        
        # Additional product ID formats to try (Amazon sometimes uses different ID formats)
        # Extract ASIN (Amazon Standard Identification Number) if present
        asin_match = re.search(r'/(?:dp|product|gp/product)/([A-Z0-9]{10})(?:/|\?|$)', product_url)
        if asin_match and asin_match.group(1) != product_id:
            # Try with the ASIN too
            asin = asin_match.group(1)
            image_formats.extend([
                f"https://m.media-amazon.com/images/I/{asin}.jpg",
                f"https://m.media-amazon.com/images/I/{asin}._AC_SL1500_.jpg"
            ])
        
        # Try each image URL format until one works
        for image_url in image_formats:
            try:
                # Try to fetch this image directly
                import requests
                img_response = requests.head(image_url, headers=headers, timeout=5)
                if img_response.status_code == 200 and 'content-length' in img_response.headers:
                    # Check if image is large enough (not a tiny icon)
                    content_length = int(img_response.headers.get('content-length', 0))
                    if content_length > 10000:  # Skip tiny images (likely icons, not product images)
                        print(f"Successfully found direct Amazon product image: {image_url}")
                        
                        # Download the image
                        img_response = requests.get(image_url, headers=headers, timeout=10)
                        
                        # Extract product name from URL for better identification
                        product_name = self._extract_product_name_from_amazon_url(product_url)
                        
                        # Save the image
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                        safe_product_name = "".join(c if c.isalnum() else "_" for c in product_name[:50])
                        image_filename = f"product_amazon_{safe_product_name}_{timestamp}.jpg"
                        image_path = os.path.join(self.product_image_dir, image_filename)
                        
                        with open(image_path, "wb") as f:
                            f.write(img_response.content)
                            
                        print(f"Saved Amazon product image directly: {image_path}")
                        return image_path
            except Exception as e:
                print(f"Failed to fetch Amazon image {image_url}: {str(e)}")
                continue  # Try next format
        
        return None  # Failed to find a suitable image
        
    def _extract_product_name_from_amazon_url(self, product_url):
        """Extract a more descriptive product name from an Amazon URL"""
        # For Amazon links, try to get product name from the URL
        import re
        
        # Default product name (fallback)
        product_name = "Amazon Product"
        
        # Try to find product title in URL
        url_parts = product_url.split('/')
        
        for part in url_parts:
            # Skip common non-title parts
            if part.startswith('dp') or part.startswith('gp') or part.startswith('ref=') or part.startswith('pf_rd'):
                continue
                
            # Look for URL part that contains product title (usually contains dashes between words)
            if len(part) > 5 and '-' in part:
                better_name = part.replace('-', ' ').title()
                # Remove common suffixes and product codes
                better_name = re.sub(r'B[0-9A-Z]{9}', '', better_name)
                better_name = re.sub(r'Ref=.*', '', better_name)
                
                if len(better_name.strip()) > 5:
                    return better_name.strip()
        
        return product_name

    def __init__(self):
        self.unsplash_api_key = os.environ.get("UNSPLASH_API_KEY", "")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self.output_dir = os.environ.get("IMAGE_OUTPUT_DIR", "./images")
        self.fallback_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fallback_images")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create fallback directory if it doesn't exist
        os.makedirs(self.fallback_dir, exist_ok=True)
        
        # Create product images directory
        self.product_image_dir = os.path.join(self.output_dir, "products")
        os.makedirs(self.product_image_dir, exist_ok=True)
        
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

    def fetch_image_from_url(self, product_url: str, product_name: str) -> Optional[str]:
        """
        Fetches an image from a product URL.
        Tries to find a prominent image on the page.
        Saves the image to the product_image_dir.
        """
        if not product_url:
            return None
        try:
            print(f"Fetching image for '{product_name}' from URL: {product_url}")
            
            # For Amazon, check if we're hitting a CAPTCHA (Amazon has strong anti-bot measures)

            is_amazon = "amazon" in product_url.lower()
            
            # For Amazon products, first try our direct image extraction method
            if is_amazon:
                amazon_image = self.extract_amazon_product_image(product_url, product_name)
                if amazon_image:
                    return amazon_image
    
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }                # Check if it's an Amazon link and get the product ID
            if is_amazon:
                # Try to extract product name directly from URL
                # For Amazon links, get product info from the URL (dp/PRODUCTID)
                import re
                product_id_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
                if product_id_match:
                    product_id = product_id_match.group(1)
                    print(f"Extracted Amazon product ID: {product_id}")
                    
                    # Try multiple image formats and sizes for Amazon product images
                    amazon_image_urls = [
                        f"https://m.media-amazon.com/images/I/{product_id}._AC_SL1500_.jpg",
                        f"https://m.media-amazon.com/images/I/{product_id}._AC_SL1000_.jpg",
                        f"https://m.media-amazon.com/images/I/{product_id}._AC_SL500_.jpg",
                        f"https://m.media-amazon.com/images/I/{product_id}.jpg",
                        f"https://images-na.ssl-images-amazon.com/images/I/{product_id}.jpg",
                        f"https://images-na.ssl-images-amazon.com/images/I/{product_id}._AC_SL1500_.jpg"
                    ]
                    
                    # Try each image URL format until one works
                    for amazon_image_url in amazon_image_urls:
                        try:
                            # Try to fetch this image directly
                            img_response = requests.head(amazon_image_url, headers=headers, timeout=5)
                            if img_response.status_code == 200 and 'content-length' in img_response.headers:
                                # Check if image is large enough (not a tiny icon)
                                content_length = int(img_response.headers.get('content-length', 0))
                                if content_length > 10000:  # Skip tiny images (likely icons, not product images)
                                    print(f"Successfully found direct Amazon product image: {amazon_image_url}")
                                    
                                    # Download the image
                                    img_response = requests.get(amazon_image_url, headers=headers, timeout=10)
                                    
                                    # Save the image
                                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                                    safe_product_name = "".join(c if c.isalnum() else "_" for c in product_name[:50])
                                    image_filename = f"product_amazon_{safe_product_name}_{timestamp}.jpg"
                                    image_path = os.path.join(self.product_image_dir, image_filename)
                                    
                                    with open(image_path, "wb") as f:
                                        f.write(img_response.content)
                                        
                                    print(f"Saved Amazon product image directly: {image_path}")
                                    return image_path
                        except Exception as e:
                            print(f"Failed to fetch Amazon image {amazon_image_url}: {str(e)}")
                            continue  # Try next format
                    
                    # For Amazon products, generate a default image path to handle captcha issues
                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                    safe_product_name = "".join(c if c.isalnum() else "_" for c in product_name[:50])
                    image_filename = f"product_amazon_{safe_product_name}_{timestamp}.jpg"
                    image_path = os.path.join(self.product_image_dir, image_filename)
                    
                    # Create a fallback image for Amazon products (this will be replaced if we can fetch the real image)
                    # Copy a fallback image to the product image directory
                    fallback_images = [f for f in os.listdir(self.fallback_dir) 
                                    if f.endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(self.fallback_dir, f))]
                    if fallback_images:
                        fallback_path = os.path.join(self.fallback_dir, fallback_images[0])
                        shutil.copy2(fallback_path, image_path)
                        print(f"Created fallback image for Amazon product: {image_path}")
                        
                        # Try to get more accurate product name
                        if product_name == "Product 1" or product_name.startswith("Product "):
                            # Extract product name from URL
                            url_parts = product_url.split('/')
                            for part in url_parts:
                                if part.startswith('dp') or part.startswith('gp'):
                                    continue
                                if len(part) > 5 and '-' in part and not part.startswith('ref=') and not part.startswith('pf_rd'):
                                    better_name = part.replace('-', ' ').title()
                                    print(f"Extracted better product name from URL: {better_name}")
                                    return image_path
                        
                        return image_path
            
            # Now try to fetch the actual page
            response = requests.get(product_url, headers=headers, timeout=10, allow_redirects=True)
              # For debugging
            if "captcha" in response.url.lower() or response.status_code >= 400:
                print(f"Received error or captcha page: {response.url}")
                if is_amazon:
                    # Try to extract product name directly from URL
                    # For Amazon links, get product info from the URL (dp/PRODUCTID)
                    import re
                    product_id_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
                    if product_id_match:
                        product_id = product_id_match.group(1)
                        # Try the fixed format amazon URL for product images
                        amazon_image_url = f"https://m.media-amazon.com/images/I/{product_id}._AC_SL1500_.jpg"
                        try:
                            img_response = requests.get(amazon_image_url, headers=headers, timeout=10)
                            if img_response.status_code == 200 and len(img_response.content) > 10000:
                                # Save the image
                                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                                safe_product_name = "".join(c if c.isalnum() else "_" for c in product_name[:50])
                                image_filename = f"product_amazon_fallback_{safe_product_name}_{timestamp}.jpg"
                                image_path = os.path.join(self.product_image_dir, image_filename)
                                
                                with open(image_path, "wb") as f:
                                    f.write(img_response.content)
                                    
                                print(f"Saved fallback Amazon product image: {image_path}")
                                return image_path
                        except Exception as e:
                            print(f"Failed to fetch fallback Amazon image: {str(e)}")
                    
                    # Use fallback for Amazon products
                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                    safe_product_name = "".join(c if c.isalnum() else "_" for c in product_name[:50])
                    image_filename = f"product_amazon_{safe_product_name}_{timestamp}.jpg"
                    image_path = os.path.join(self.product_image_dir, image_filename)
                    
                    # Copy a fallback image
                    fallback_images = [f for f in os.listdir(self.fallback_dir) 
                                    if f.endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(self.fallback_dir, f))]
                    if fallback_images:
                        fallback_path = os.path.join(self.fallback_dir, fallback_images[0])
                        shutil.copy2(fallback_path, image_path)
                        print(f"Using fallback image for Amazon product with captcha: {image_path}")
                        return image_path
                return None
            
            response.raise_for_status() # Raise an exception for bad status codes

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Also try to extract product name and details from the page
            page_title = soup.find('title')
            if page_title and page_title.text:
                # Clean and extract product name from title
                clean_title = page_title.text.strip()
                # For Amazon, remove the Amazon.in part
                if "Amazon" in clean_title:
                    clean_title = clean_title.split(':')[0].strip()
                    if "Buy" in clean_title and clean_title.startswith("Buy"):
                        clean_title = clean_title[4:].strip()  # Remove "Buy " prefix
                product_name = clean_title[:100]  # Limit length
            
            # Try to find Open Graph image first (most reliable for product images)
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                image_url = og_image["content"]
            else:
                # Fallback: Find the largest image on the page (simple heuristic)
                images = soup.find_all("img")
                best_image_url = None
                max_area = 0
                product_image_candidates = []
                if not images:
                    print(f"No <img> tags found on {product_url}")
                    return None

                # First pass: collect all potential product images with their sizes
                for img in images:
                    src = img.get("src")
                    if not src or src.startswith("data:image"): # ignore inline images
                        continue
                    
                    # Skip typical non-product images
                    img_lower = src.lower()
                    if any(skip in img_lower for skip in ["logo", "icon", "avatar", "spinner", "loader", "banner", "button", "social", "payment", "footer"]):
                        continue
                    
                    # Make URL absolute
                    src = urllib.parse.urljoin(product_url, src)
                    
                    # Basic check for image type (can be improved)
                    if not (src.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))):
                        # Try to see if there's a URL parameter that indicates an image
                        if ".jpg" in src or ".jpeg" in src or ".png" in src or ".webp" in src:
                            # It's probably an image with query parameters
                            pass
                        else:
                            continue
                        
                    # Prefer Amazon product images
                    if "amazon" in product_url.lower():
                        # Amazon product images typically follow these patterns
                        if "images/I/" in src or "/images/P/" in src or "-images." in src:
                            # Check if it's likely a product image (avoid small thumbnails)
                            if ("_SL" in src or "_AC_" in src or "_SX" in src or "_UL" in src) and not "icon" in src.lower() and not "logo" in src.lower():
                                best_image_url = src
                                print(f"Found Amazon product image: {src}")
                                break
                    # Simplistic way to find a prominent image - check for width/height or just take the first one
                    # This part can be significantly improved with more sophisticated heuristics
                    if "logo" not in src.lower() and "icon" not in src.lower() and "avatar" not in src.lower() and "spinner" not in src.lower() and "loader" not in src.lower():
                        best_image_url = src # Take the first plausible candidate
                        break 
                
                if not best_image_url:
                     # If no specific image found, take the first src
                    img_tags = soup.find_all('img')
                    if img_tags:
                        first_img_src = img_tags[0].get('src')
                        if first_img_src and not first_img_src.startswith("data:image"):
                             best_image_url = urllib.parse.urljoin(product_url, first_img_src)
                    if not best_image_url:
                        print(f"Could not find a suitable image on {product_url}")
                        return None
                image_url = best_image_url

            print(f"Found image URL: {image_url}")
            
            # Download the image
            img_response = requests.get(image_url, headers=headers, timeout=10, stream=True)
            img_response.raise_for_status()

            # Sanitize product name for filename
            safe_product_name = "".join(c if c.isalnum() else "_" for c in product_name[:50])
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            
            # Get file extension
            content_type = img_response.headers.get('content-type')
            extension = '.jpg' # default
            if content_type:
                if 'jpeg' in content_type:
                    extension = '.jpg'
                elif 'png' in content_type:
                    extension = '.png'
                elif 'webp' in content_type:
                    extension = '.webp'
            else: # Try to guess from URL
                parsed_url = urllib.parse.urlparse(image_url)
                path_extension = os.path.splitext(parsed_url.path)[1]
                if path_extension and path_extension.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    extension = path_extension.lower()

            image_filename = f"product_{safe_product_name}_{timestamp}{extension}"
            image_path = os.path.join(self.product_image_dir, image_filename)
            
            with open(image_path, "wb") as f:
                for chunk in img_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Saved product image to: {image_path}")
            return image_path

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {product_url} or image: {e}")
            # For Amazon products, use a fallback image
            if "amazon" in product_url.lower():
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                safe_product_name = "".join(c if c.isalnum() else "_" for c in product_name[:50])
                image_filename = f"product_amazon_{safe_product_name}_{timestamp}.jpg"
                image_path = os.path.join(self.product_image_dir, image_filename)
                
                # Copy a fallback image
                fallback_images = [f for f in os.listdir(self.fallback_dir) 
                                  if f.endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(self.fallback_dir, f))]
                if fallback_images:
                    fallback_path = os.path.join(self.fallback_dir, fallback_images[0])
                    shutil.copy2(fallback_path, image_path)
                    print(f"Using fallback image for Amazon product with error: {image_path}")
                    return image_path
            return None
        except Exception as e:
            print(f"An unexpected error occurred while fetching image from {product_url}: {e}")
            # For Amazon products, use a fallback image
            if "amazon" in product_url.lower():
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                safe_product_name = "".join(c if c.isalnum() else "_" for c in product_name[:50])
                image_filename = f"product_amazon_{safe_product_name}_{timestamp}.jpg"
                image_path = os.path.join(self.product_image_dir, image_filename)
                
                # Copy a fallback image
                fallback_images = [f for f in os.listdir(self.fallback_dir) 
                                  if f.endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(self.fallback_dir, f))]
                if fallback_images:
                    fallback_path = os.path.join(self.fallback_dir, fallback_images[0])
                    shutil.copy2(fallback_path, image_path)
                    print(f"Using fallback image for Amazon product with general error: {image_path}")
                    return image_path
            return None

image_service = ImageService()
