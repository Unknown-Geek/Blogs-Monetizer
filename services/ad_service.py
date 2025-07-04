from typing import List, Dict
import os
import json
import requests
from datetime import datetime
import random
import re
from .sheets_service import google_sheets_service

class AdService:
    def __init__(self):
        self.affiliate_spreadsheet_url = os.environ.get("AFFILIATE_SPREADSHEET_URL")
        self.sheets_service = google_sheets_service

    def fetch_affiliate_products(self) -> List[Dict]:
        """
        Fetch affiliate products from local cache first, or if not available, from the Google Spreadsheet.
        Returns only products from the spreadsheet, never falls back to sample products.
        
        Returns:
            List of affiliate product dictionaries
        """
        # First try to load from local cache
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
        cache_file = os.path.join(cache_dir, "affiliate_products.json")
        
        if os.path.exists(cache_file):
            try:
                print(f"Loading affiliate products from local cache file: {cache_file}")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    
                if isinstance(cached_data, dict) and 'products' in cached_data and cached_data['products']:
                    print(f"Successfully loaded {len(cached_data['products'])} products from cache")
                    return cached_data['products']
            except Exception as e:
                print(f"Error loading from cache: {str(e)}")
        
        # If cache loading failed, fall back to spreadsheet
        spreadsheet_url_to_use = self.affiliate_spreadsheet_url
        if not spreadsheet_url_to_use:
            print("No AFFILIATE_SPREADSHEET_URL found in environment. No affiliate products will be used.")
            return []  # Return empty list if no spreadsheet URL
        else:
            print(f"Fetching affiliate products from spreadsheet: {spreadsheet_url_to_use}")
            try:
                # Attempt to fetch products from the Google Spreadsheet
                products = self.sheets_service.fetch_affiliate_products(spreadsheet_url_to_use)
                if not products:
                    print("Failed to fetch products from spreadsheet or spreadsheet is empty.")
                    return []  # Return empty list if fetch fails or no products
            except Exception as e:
                print(f"Error fetching affiliate products: {str(e)}")
                return []  # Return empty list on error
        
        # Log affiliate product fetch
        self._log_affiliate_products({
            "source": "local cache" if os.path.exists(cache_file) else (spreadsheet_url_to_use or "no spreadsheet URL"),
            "product_count": len(products),
            "timestamp": datetime.now().isoformat()
        })
        
        return products

    def _log_affiliate_products(self, data: Dict):
        # Placeholder implementation
        pass

    def generate_ad_strategy(self, content_info: Dict) -> Dict:
        # Placeholder implementation
        return {
            "density": "medium",
            "primary_network": "google",
            "ad_count": 3,
            "strategy_name": "medium density google ads"
        }

    def prepare_content_for_ads(self, content: str, ad_density: str) -> str:
        # Placeholder implementation
        return content # Or add ad placeholders like <!-- AD_PLACEMENT -->
        
    def insert_ads_into_content(self, content: str, network: str) -> str:
        # Placeholder implementation - replace placeholders with actual ad code
        return content.replace("<!-- AD_PLACEMENT -->", f"<div>Ad from {network}</div>")
        
    def insert_affiliate_ads(self, content: str, affiliate_products: List[Dict], max_affiliate_ads: int, context: str = None) -> str:
        # If no products, return content unchanged (no ads)
        if not affiliate_products:
            return content

        product_html_parts = []
        inserted_count = 0

        # Extract context from the content if not provided
        if context is None:
            # Try to get the first 100 words as context
            words = content.split()[:100]
            context = " ".join(words)

        # --- Relevance scoring ---
        def score_product(product):
            score = 0
            # Score by category match
            content_lower = content.lower()
            if 'category' in product and product['category']:
                for cat in str(product['category']).split(','):
                    if cat.strip().lower() in content_lower:
                        score += 3
            # Score by product name/description keyword match
            for field in ['product_name', 'description']:
                if field in product and product[field]:
                    for word in str(product[field]).split():
                        if len(word) > 3 and word.lower() in content_lower:
                            score += 1
            return score

        # Score all products
        scored_products = [(score_product(p), p) for p in affiliate_products]        # Sort by score descending, then shuffle those with same score
        scored_products.sort(key=lambda x: x[0], reverse=True)
        # Group by score
        grouped = {}
        for score, prod in scored_products:
            grouped.setdefault(score, []).append(prod)        # Flatten, shuffling within each score group
        sorted_products = []
        for score in sorted(grouped.keys(), reverse=True):
            group = grouped[score]
            random.shuffle(group)
            sorted_products.extend(group)
            
        # Track used product names and URLs to avoid duplicates
        used_product_names = set()
        used_product_urls = set()
        used_product_keywords = set()  # For similarity detection

        # Only use top N products, ensuring they're different from each other
        for product in sorted_products:
            if inserted_count >= max_affiliate_ads:
                break
                
            product_url = product.get("url", "#")
            if not product_url or product_url == "#":
                continue
                
            # Extract product name and enhance it if possible
            product_name = product.get("product_name", "Shop Now")
            if product_name.startswith("Product "):
                better_name = self._extract_product_name_from_url(product_url)
                if better_name:
                    product_name = better_name
            
            # Create a normalized version of product name for better duplicate detection
            normalized_name = product_name.lower().strip()
            
            # Extract key words from the product name (words longer than 4 chars)
            keywords = [word for word in normalized_name.split() if len(word) > 4]
            
            # Check if we've already used this URL
            if product_url in used_product_urls:
                continue
                
            # Check if the name is a direct match
            if normalized_name in used_product_names:
                continue
                
            # Check for similar products (having 2+ matching keywords)
            keyword_matches = sum(1 for kw in keywords if kw in used_product_keywords)
            if keywords and keyword_matches >= 2:
                continue
                
            # Store this product name and URL so we don't show duplicates
            used_product_names.add(normalized_name)
            used_product_urls.add(product_url)
            for kw in keywords:
                used_product_keywords.add(kw)
            
            # Process image URL to ensure it's properly formatted
            image_url = product.get("image_url", "")
            if image_url and image_url.strip() and not (image_url.startswith('http://') or image_url.startswith('https://')):
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                else:
                    image_url = 'https://' + image_url
            catchphrase = self._generate_catchphrase(product_name, context)
            # Add a short description under the catchphrase
            description = product.get('description', '').strip()
            if not description:
                # Fallback: use a generic description if missing
                description = f"Discover more about {product_name} and why it's popular with our readers."
            image_html = "<div style='width: 100%; height: 200px; background-color: #f5f5f5; display: flex; align-items: center; justify-content: center; border-radius: 4px;'>No Image</div>"
            if image_url and image_url.strip():
                image_html = f"<img src='{image_url}' alt='{product_name}' style='max-width: 100%; max-height: 200px; object-fit: contain; border-radius: 4px;'>"
            html = f"""
            <div class=\"affiliate-product\" style=\"display: flex; margin: 20px 0; padding: 15px; border: 1px solid #eee; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); background-color: #fff; overflow: hidden; max-width: 100%;\">
                <!-- Left side: Product Image -->
                <div class=\"product-image\" style=\"flex: 0 0 40%; padding-right: 15px; height: 200px; display: flex; align-items: center; justify-content: center;\">
                    {image_html}
                </div>
                <!-- Right side: Product Info -->
                <div class=\"product-info\" style=\"flex: 1; display: flex; flex-direction: column; justify-content: space-between;\">
                    <div class=\"product-catchphrase\" style=\"font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #333;\">{catchphrase}</div>
                    <div class=\"product-description\" style=\"font-size: 15px; color: #555; margin-bottom: 15px;\">{description}</div>
                    <a href=\"{product_url}\" target=\"_blank\" rel=\"noopener\" class=\"shop-now-button\" style=\"display: inline-block; background-color: #ff9900; color: white; padding: 10px 20px; text-align: center; text-decoration: none; font-weight: bold; border-radius: 4px; align-self: flex-start; transition: background-color 0.3s;\">Shop Now</a>
                </div>
            </div>
            """
            product_html_parts.append(html)
            inserted_count += 1

        if product_html_parts:
            responsive_css = """
            <style>
            .affiliate-section {
                margin-top: 40px;
                padding: 15px;
                background-color: #f9f9f9;
                border-radius: 8px;
                line-height: 1.5;
            }
            .affiliate-section h2 {
                text-align: center;
                margin-bottom: 20px;
                color: #333;
                font-size: 24px;
                line-height: 1.5;
            }            .affiliate-product {
                display: flex;
                margin: 20px 0;
                padding: 15px;
                border: 1px solid #eee;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                background-color: #fff;
                overflow: hidden;
                max-width: 100%;
            }
            .product-image {
                flex: 0 0 40%; 
                padding-right: 15px;
                height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .product-info {
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            @media screen and (max-width: 600px) {
                .affiliate-product {
                    flex-direction: column;
                }
                .product-image {
                    padding-right: 0 !important;
                    padding-bottom: 15px;
                    max-width: 100% !important;
                    height: 180px !important;
                }
            }            </style>
            """
            return content + "\n" + responsive_css + "<div class='affiliate-section'><h2>Recommended Products</h2>\n" + "\n".join(product_html_parts) + "</div>"
        return content
    
    def estimate_revenue(self, content: str, views: int) -> Dict:
        # Placeholder implementation
        return {"estimated_revenue": {"total": 5.0}}
        
    def _extract_product_name_from_url(self, product_url: str) -> str:
        """Extract a more descriptive product name from a URL, especially for Amazon products"""
        if "amazon" in product_url.lower():
            # For Amazon links, get product info from the URL (dp/PRODUCTID)
            import re
            
            # If the URL contains product details in a readable format, extract directly
            # Pattern for OnePlus and similar device listings (first try)
            product_pattern = re.search(r'/([^/]+)/dp/', product_url)
            if product_pattern:
                product_text = product_pattern.group(1)
                if '-' in product_text and len(product_text) > 5:
                    better_name = product_text.replace('-', ' ').title()
                    # Clean up the name
                    better_name = re.sub(r'B[0-9A-Z]{9}', '', better_name).strip()
                    better_name = re.sub(r'\bFor\s(Amazon|iPhone|iPad|Samsung|Android)\b', '', better_name, flags=re.IGNORECASE).strip()
                    better_name = re.sub(r'\b(Pack\sOf\s\d+|Set\sOf\s\d+|With\s\d+|Bundle)\b', '', better_name, flags=re.IGNORECASE).strip()
                    
                    if len(better_name) > 3:
                        print(f"Extracted better product name from URL pattern 1: {better_name}")
                        return better_name
            
            # If the URL contains product details in a readable format, extract directly
            # Pattern for OnePlus and similar device listings (first try)
            product_pattern = re.search(r'/([^/]+)/dp/', product_url)
            if product_pattern:
                product_text = product_pattern.group(1)
                if '-' in product_text and len(product_text) > 5:
                    better_name = product_text.replace('-', ' ').title()
                    # Clean up the name
                    better_name = re.sub(r'B[0-9A-Z]{9}', '', better_name).strip()
                    better_name = re.sub(r'\bFor\s(Amazon|iPhone|iPad|Samsung|Android)\b', '', better_name, flags=re.IGNORECASE).strip()
                    better_name = re.sub(r'\b(Pack\sOf\s\d+|Set\sOf\s\d+|With\s\d+|Bundle)\b', '', better_name, flags=re.IGNORECASE).strip()
                    
                    if len(better_name) > 3:
                        print(f"Extracted better product name from URL pattern 1: {better_name}")
                        return better_name
            
            # Try to extract product name from URL parts (fallback method)
            url_parts = product_url.split('/')
            
            # Look for parts that might contain the product name
            for part in url_parts:
                if part.startswith('dp') or part.startswith('gp') or len(part) < 5:
                    continue
                if '-' in part and not part.startswith('ref=') and not part.startswith('pf_rd'):
                    better_name = part.replace('-', ' ').title()
                    # Clean up the name (remove product IDs, colors, sizes)
                    better_name = re.sub(r'B[0-9A-Z]{9}', '', better_name).strip()
                    
                    # Further clean up common suffixes and prefixes in Amazon product names
                    better_name = re.sub(r'\bFor\s(Amazon|iPhone|iPad|Samsung|Android)\b', '', better_name, flags=re.IGNORECASE).strip()
                    better_name = re.sub(r'\b(Pack\sOf\s\d+|Set\sOf\s\d+|With\s\d+|Bundle)\b', '', better_name, flags=re.IGNORECASE).strip()
                    
                    if len(better_name) > 3:
                        print(f"Extracted better product name from URL pattern 2: {better_name}")
                        return better_name
                        
        # Default fallback
        return "Featured Product"
            
    def _generate_catchphrase(self, product_name: str, context: str = None) -> str:
        """
        Generate a compelling catchphrase for the affiliate product.
        
        Args:
            product_name: The name of the product
            context: Optional context about the blog content for more relevant phrases
            
        Returns:
            A catchphrase string
        """
        # Simple catchphrase templates
        catchphrases = [
            f"Check out this amazing {product_name}!",
            f"Upgrade your life with this {product_name}!",
            f"The {product_name} everyone's talking about!",
            f"Love this {product_name} - you will too!",
            f"Top rated {product_name} - see why!",
            f"Discover the {product_name} difference!",
            f"This {product_name} changed everything for me!",
            f"Don't miss this incredible {product_name}!",
        ]
        
        # For tech products
        tech_terms = ["phone", "laptop", "computer", "tablet", "ipad", "iphone", "android", "samsung", 
                     "oneplus", "pixel", "macbook", "headphones", "earbuds", "smartwatch", "smart watch",
                     "tech", "gadget", "gaming", "camera", "speaker", "bluetooth"]
                     
        if any(term in product_name.lower() for term in tech_terms):
            tech_phrases = [
                f"Level up your tech with this {product_name}!",
                f"The {product_name} - smart tech for modern life!",
                f"Tech enthusiasts love this {product_name}!",
                f"Power up with the latest {product_name}!",
                f"Cutting-edge {product_name} - see the difference!",
            ]
            catchphrases.extend(tech_phrases)
            
        # If we have context, try to make it more relevant (simple implementation)
        if context:
            context = context.lower()
            if "health" in context or "fitness" in context:
                if any(term in product_name.lower() for term in ["vitamin", "protein", "supplement", "workout"]):
                    return f"Boost your health with this premium {product_name}!"
            elif "tech" in context or "technology" in context:
                if any(term in product_name.lower() for term in tech_terms):
                    return f"Stay on the cutting edge with this {product_name}!"
            elif "social media" in context or "fake news" in context:
                if any(term in product_name.lower() for term in tech_terms):
                    return f"Stay connected responsibly with this {product_name}!"
        
        # Select a random catchphrase
        import random
        return random.choice(catchphrases)

    def _generate_clickbait_phrase_gemini(self, product_name: str, context: str = None) -> str:
        """
        Use Gemini API to generate a clickbait phrase for the given product.
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return f"Don't miss out on {product_name}!"

        prompt = f"Write a catchy, clickbait ad phrase for a product called '{product_name}'."
        if context:
            prompt += f" The ad is for a blog about: {context}"

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        params = {"key": api_key}

        try:
            response = requests.post(url, headers=headers, params=params, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Extract the generated phrase from Gemini's response
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            return f"Check out this amazing {product_name}!"

ad_service = AdService()
