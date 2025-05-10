import requests
import os
import base64
from io import BytesIO
from typing import Dict, Optional, List
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import re
import html

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class BlogService:
    def __init__(self):
        # Load all credentials from environment variables
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self.blogger_id = os.environ.get("BLOGGER_ID", "")
        self.blogger_client_id = os.environ.get("BLOGGER_CLIENT_ID", "")
        self.blogger_client_secret = os.environ.get("BLOGGER_CLIENT_SECRET", "")
        self.blogger_refresh_token = os.environ.get("BLOGGER_REFRESH_TOKEN", "")
        
    def generate_blog_content(self, prompt: str, max_tokens: int = 1500) -> str:
        """Generate blog content using Google's Gemini API with enhanced prompt engineering"""
        # Enhance the prompt for better blog formatting
        enhanced_prompt = self._enhance_prompt(prompt)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Configure generation parameters for better quality
        payload = {
            "contents": [{"parts": [{"text": enhanced_prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.9,
                "maxOutputTokens": max_tokens,
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Gemini API Error: {response.text}")
            
            # Extract the content from the Gemini response
            response_data = response.json()
            
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                content = response_data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise Exception("No content returned from Gemini API")
                
            # Preprocess content to handle edge cases
            content = self._enhance_content_preprocessing(content)
                
            # Add enhanced HTML formatting
            formatted_content = self._format_content(content)
            return formatted_content
            
        except Exception as e:
            raise Exception(f"Error generating blog content: {str(e)}")
    
    def _enhance_prompt(self, prompt: str) -> str:
        """Enhance the blog prompt for better structure and SEO"""
        structured_prompt = f"""
Write a well-structured SEO-optimized blog post about:

{prompt}

Please follow these guidelines:
- Include a compelling title (H1)
- Write a strong introduction
- Use at least 3-4 subheadings (H2) to divide content into sections
- Include at least 5 paragraphs
- Use bullet points or numbered lists where appropriate
- Write at least 500 words
- Use a friendly, conversational tone
- Include a conclusion section
- Format using Markdown (# for H1, ## for H2, etc.)
- For bold text use **double asterisks** (not single)
- For bullet points, ensure there's a space after the asterisk: * item (not *item)

Make sure the content is original, informative, and engaging.
"""
        return structured_prompt
        
    def _format_content(self, content: str) -> str:
        """Add enhanced HTML formatting to the generated content with better Markdown parsing"""
        paragraphs = content.split("\n\n")
        formatted_paragraphs = []
        in_list = False
        list_type = None
        list_items = []
        
        for p in paragraphs:
            # Skip empty paragraphs
            if not p.strip():
                continue
                
            # Handle Markdown headers
            if p.startswith("# "):
                if in_list:
                    # Close any open list
                    formatted_paragraphs.append(self._format_list(list_items, list_type))
                    in_list = False
                    list_items = []
                # H1 header
                formatted_paragraphs.append(f"<h1>{html.escape(p[2:].strip())}</h1>")
            elif p.startswith("## "):
                if in_list:
                    # Close any open list
                    formatted_paragraphs.append(self._format_list(list_items, list_type))
                    in_list = False
                    list_items = []
                # H2 header
                formatted_paragraphs.append(f"<h2>{html.escape(p[3:].strip())}</h2>")
            elif p.startswith("### "):
                if in_list:
                    # Close any open list
                    formatted_paragraphs.append(self._format_list(list_items, list_type))
                    in_list = False
                    list_items = []
                # H3 header
                formatted_paragraphs.append(f"<h3>{html.escape(p[4:].strip())}</h3>")
            elif p.startswith("- ") or p.startswith("* "):
                # Bullet list
                if not in_list or list_type != "ul":
                    if in_list:
                        # Close previous list of different type
                        formatted_paragraphs.append(self._format_list(list_items, list_type))
                        list_items = []
                    in_list = True
                    list_type = "ul"
                # Strip list marker but preserve formatting
                list_content = p[2:].strip()
                # Process formatting within list item (bold, italic, links)
                list_content = self._process_inline_formatting(list_content)
                list_items.append(list_content)
            elif re.match(r'^[0-9]+\.', p):
                # Numbered list
                if not in_list or list_type != "ol":
                    if in_list:
                        # Close previous list of different type
                        formatted_paragraphs.append(self._format_list(list_items, list_type))
                        list_items = []
                    in_list = True
                    list_type = "ol"
                # Extract content after the number and dot
                item_content = re.sub(r'^[0-9]+\.', '', p).strip()
                # Process formatting within list item (bold, italic, links)
                item_content = self._process_inline_formatting(item_content)
                list_items.append(item_content)
            else:
                if in_list:
                    # Close any open list
                    formatted_paragraphs.append(self._format_list(list_items, list_type))
                    in_list = False
                    list_items = []
                    
                # Process all inline formatting
                p = self._process_inline_formatting(p)
                
                # Regular paragraph
                formatted_paragraphs.append(f"<p>{p}</p>")
                
        # Close any open list at the end
        if in_list:
            formatted_paragraphs.append(self._format_list(list_items, list_type))
        
        return "\n".join(formatted_paragraphs)
    
    def _process_inline_formatting(self, text: str) -> str:
        """Process inline Markdown formatting (bold, italic, links) within text"""
        # Process links in markdown format [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Process bold text first with improved regex
        text = re.sub(r'\*\*([^*]*(?:\*(?!\*)[^*]*)*)\*\*', r'<strong>\1</strong>', text)
        
        # Then process italic text with improved regex that preserves already processed bold
        text = re.sub(r'\*([^*<>]*(?:<[^>]+>[^*<>]*)*)\*', r'<em>\1</em>', text)
        
        return text

    def _format_list(self, items: List[str], list_type: str) -> str:
        """Helper to format a list in HTML"""
        if not items:
            return ""
            
        html_list = f"<{list_type}>\n"
        for item in items:
            html_list += f"  <li>{item}</li>\n"
        html_list += f"</{list_type}>"
        
        return html_list

    def _enhance_content_preprocessing(self, content: str) -> str:
        """
        Preprocess content to handle special edge cases before standard formatting
        - Fixes cases where asterisks are used both as list markers and for formatting
        - Improves handling of complex formatting patterns
        """
        # Handle special case: List items with bold text that start with "* **"
        # For example: "* **Bold Item:**" should become properly formatted
        content = re.sub(r'^\* \*\*([^*]+)\*\*', r'* <strong>\1</strong>', content, flags=re.MULTILINE)
        
        # Handle complex case like your sample:
        # "**Technological Development:** ... * **Mission Complexity:** ..."
        content = re.sub(r'(\*\*[^*:]+:\*\*[^*]+)\* (\*\*[^*:]+:\*\*)', r'\1<br>• \2', content)
        
        # Handle case where a single asterisk is used in the middle of a sentence
        # but isn't meant for formatting (often in scientific or mathematical content)
        content = re.sub(r'(\w)\*(\w)', r'\1*\2', content)
        
        return content

    def publish_blog(self, title: str, content: str, image_path: Optional[str] = None, labels: Optional[List[str]] = None) -> Dict:
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
                # Determine the correct mime type based on file extension
                mime_type = "image/jpeg"  # Default for Unsplash images (JPG)
                if image_path.lower().endswith('.png'):
                    mime_type = "image/png"
                elif image_path.lower().endswith('.gif'):
                    mime_type = "image/gif"
                
                # Use a different approach to upload images to Blogger
                # First, we'll get the blog's information to check features
                blog_info = service.blogs().get(blogId=self.blogger_id).execute()
                
                # Check if we can upload via posts directly (most reliable method)
                # Instead of using media().insert which seems to be causing issues
                with open(image_path, "rb") as img:
                    # Store image content for later use in the HTML
                    img_content = img.read()
                
                # We'll use a data URI approach which works more reliably
                # This embeds the image directly in the HTML
                import base64
                img_b64 = base64.b64encode(img_content).decode('utf-8')
                image_url = f"data:{mime_type};base64,{img_b64}"
                
                # Check if there's an attribution file
                attribution_path = image_path + ".json"
                if os.path.exists(attribution_path):
                    try:
                        import json
                        with open(attribution_path, 'r') as f:
                            attribution = json.load(f)
                            
                        # Add a credit line if this is from Unsplash
                        if attribution.get("source") == "Unsplash":
                            content += f"\n<p class='image-attribution'>Photo by <a href='{attribution.get('photographer_url')}' target='_blank'>{attribution.get('photographer')}</a> on <a href='{attribution.get('source_url')}' target='_blank'>Unsplash</a></p>"
                    except:
                        pass

            # Prepare the post content
            post_content = content
            if image_url:
                image_alt = title if title else "Blog image"
                post_content = f"<img src='{image_url}' alt='{image_alt}' class='featured-image'/>\n{content}"
                
            # Add CSS for ad containers
            ad_styles = """
            <style>
            .ad-container {
                margin: 20px 0;
                padding: 10px;
                text-align: center;
                background-color: #f9f9f9;
                border-radius: 5px;
                clear: both;
                overflow: hidden;
            }
            .ad-container.leaderboard {
                max-width: 728px;
                margin: 20px auto;
            }
            .ad-container.skyscraper {
                float: right;
                margin: 0 0 15px 15px;
            }
            .ad-container.rectangle {
                margin: 20px auto;
                max-width: 300px;
            }
            .custom-ad-content {
                padding: 20px;
                border: 1px dashed #ccc;
                color: #777;
                font-size: 14px;
            }
            </style>
            """
            
            # Add styles to the post content
            post_content = ad_styles + post_content
            
            # Convert ad placement hooks to actual ad code
            try:
                from services.ad_service import ad_service
                post_content = ad_service.insert_ads_into_content(post_content, network="google")
            except Exception as e:
                print(f"Warning: Could not insert ads into content: {str(e)}")

            # Create the post
            post = {
                "kind": "blogger#post",
                "blog": {"id": self.blogger_id},
                "title": title,
                "content": post_content,
            }
            
            # Add labels if provided (with cleaning)
            if labels:
                # Remove any duplicates and empty labels
                filtered_labels = list(set([label.strip() for label in labels if label.strip()]))
                if filtered_labels:
                    post["labels"] = filtered_labels

            # Insert the post
            result = service.posts().insert(blogId=self.blogger_id, body=post).execute()
            
            # Add metadata to the result
            result["success"] = True
            return result
            
        except Exception as e:
            error_message = str(e)
            print(f"Failed to publish blog: {error_message}")
            return {
                "success": False,
                "error": error_message
            }

    def get_recent_posts(self, max_results=10):
        """Get a list of recent blog posts"""
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
            
            # Get recent posts
            posts = service.posts().list(
                blogId=self.blogger_id,
                maxResults=max_results,
                status="LIVE",  # STATUS MUST BE UPPERCASE - "LIVE", "DRAFT", "SCHEDULED" or "SOFT_TRASHED"
                fetchBodies=True
            ).execute()
            
            if "items" in posts:
                return posts["items"]
            else:
                return []
                
        except Exception as e:
            print(f"Error fetching recent posts: {str(e)}")
            return []
    
    def update_post(self, post_id, content=None, title=None, labels=None):
        """Update an existing blog post"""
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
            
            # First get the existing post
            existing_post = service.posts().get(
                blogId=self.blogger_id,
                postId=post_id
            ).execute()
            
            # Update post fields if provided
            if content:
                existing_post["content"] = content
            if title:
                existing_post["title"] = title
            if labels:
                existing_post["labels"] = labels
                
            # Update the post
            result = service.posts().update(
                blogId=self.blogger_id,
                postId=post_id,
                body=existing_post
            ).execute()
            
            return True
                
        except Exception as e:
            print(f"Error updating post: {str(e)}")
            return False

blog_service = BlogService()
