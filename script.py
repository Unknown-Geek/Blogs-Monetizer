import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import tweepy
from PIL import Image
from io import BytesIO
from transformers import pipeline
from backend.services.seo_service import seo_service  # Updated import

# ==== SETUP ====
# Replace these with your API keys and credentials
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
BLOGGER_CREDENTIALS_FILE = "credentials.json"
BLOGGER_ID = "YOUR_BLOGGER_ID"
TWITTER_BEARER_TOKEN = "YOUR_TWITTER_BEARER_TOKEN"
GA_CREDENTIALS_FILE = "ga_credentials.json"
GA_VIEW_ID = "YOUR_VIEW_ID"

# Hugging Face model
IMAGE_GEN_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

# ==== STEP 1: Generate Blog Content ====
def generate_blog_content(prompt):
    url = "https://api.gemini.com/v1/content/generate"
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    payload = {"prompt": prompt, "max_tokens": 1000}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["content"]
    else:
        raise Exception(f"Gemini API Error: {response.text}")

# ==== STEP 2: Analyze SEO ====
def analyze_seo(content):
    return seo_service.analyze_seo(content)

# ==== STEP 3: Generate Blog Image ====
def generate_image(prompt):
    pipe = pipeline("text-to-image", model=IMAGE_GEN_MODEL)
    image = pipe(prompt, num_inference_steps=50)["images"][0]
    # Save image locally
    image_path = "blog_image.png"
    image.save(image_path)
    return image_path

# ==== STEP 4: Publish to Blogger ====
def post_to_blogger(title, content, image_path, labels):
    creds = Credentials.from_authorized_user_file(BLOGGER_CREDENTIALS_FILE)
    service = build("blogger", "v3", credentials=creds)

    # Upload image to Blogger
    image_url = None
    with open(image_path, "rb") as img:
        media = service.media().insert(
            blogId=BLOGGER_ID,
            media_body=BytesIO(img.read()),
            media_mime_type="image/png",
        ).execute()
        image_url = media.get("url")

    post = {
        "kind": "blogger#post",
        "blog": {"id": BLOGGER_ID},
        "title": title,
        "content": f"<img src='{image_url}' alt='Blog Image'/>{content}",
        "labels": labels,
    }
    result = service.posts().insert(blogId=BLOGGER_ID, body=post).execute()
    return result

# ==== STEP 5: Share on Twitter ====
def post_to_twitter(message):
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    response = client.create_tweet(text=message)
    return response

# ==== STEP 6: Fetch Analytics Data ====
def get_analytics_data():
    creds = Credentials.from_authorized_user_file(GA_CREDENTIALS_FILE)
    analytics = build("analyticsreporting", "v4", credentials=creds)

    report = analytics.reports().batchGet(
        body={
            "reportRequests": [
                {
                    "viewId": GA_VIEW_ID,
                    "dateRanges": [{"startDate": "30daysAgo", "endDate": "today"}],
                    "metrics": [{"expression": "ga:sessions"}],
                }
            ]
        }
    ).execute()
    return report

# ==== MAIN SCRIPT ====
def main():
    try:
        # Step 1: Generate Blog Content
        blog_idea = "The latest trends in AI and technology"
        blog_content = generate_blog_content(blog_idea)

        # Step 2: Analyze SEO
        seo_report = analyze_seo(blog_content)
        print("SEO Report:", seo_report)

        # Step 3: Generate Blog Image
        image_path = generate_image("A futuristic AI robot working on cutting-edge technology")
        print("Image saved at:", image_path)

        # Step 4: Post to Blogger
        post_response = post_to_blogger("AI and Tech Trends", blog_content, image_path, ["AI", "Tech"])
        print("Blogger Post Response:", post_response)

        # Step 5: Share on Twitter
        twitter_response = post_to_twitter(f"Check out my latest blog: {post_response['url']}")
        print("Twitter Response:", twitter_response)

        # Step 6: Fetch Analytics
        analytics_data = get_analytics_data()
        print("Analytics Data:", analytics_data)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
