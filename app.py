import os
import time
import threading
from fastapi import FastAPI
from dotenv import load_dotenv
from services.blog_service import blog_service
from services.trend_service import trend_service

# Load environment variables
load_dotenv()

app = FastAPI(title="Blogs Monetizer Space API")

latest_blog = {"title": None, "content": None, "status": "Not started", "last_run": None, "error": None}

def blog_generation_loop():
    while True:
        try:
            latest_blog["status"] = "Generating..."
            # Get a trending topic
            topic = trend_service.get_trending_topics(count=1)
            if topic and isinstance(topic, list):
                topic = topic[0]
            elif isinstance(topic, dict):
                pass
            else:
                latest_blog["error"] = "No trending topic found."
                latest_blog["status"] = "Idle"
                time.sleep(1200)
                continue
            prompt = topic["title"] if "title" in topic else str(topic)
            # Generate blog content
            content = blog_service.generate_blog_content(prompt)
            # Publish blog (optional: you can comment this out if you only want to preview)
            result = blog_service.publish_blog(title=prompt, content=content)
            latest_blog["title"] = prompt
            latest_blog["content"] = content
            latest_blog["status"] = "Success"
            latest_blog["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
            latest_blog["error"] = None
        except Exception as e:
            latest_blog["status"] = "Error"
            latest_blog["error"] = str(e)
        time.sleep(1200)  # 20 minutes

def start_background_thread():
    t = threading.Thread(target=blog_generation_loop, daemon=True)
    t.start()

@app.on_event("startup")
def on_startup():
    start_background_thread()

@app.get("/status")
def get_status():
    return latest_blog

@app.get("/")
def root():
    return {"message": "Blogs Monetizer Space is running.", "status": latest_blog["status"], "last_run": latest_blog["last_run"]}
