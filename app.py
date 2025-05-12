from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import uvicorn
from pydantic import BaseModel

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Import services
try:
    from services import blog_service, seo_service, image_service, social_service, analytics_service, ad_service
    from services.trend_service import trend_service
    from services.automation_service import automation_service
except ImportError:
    # Alternative import if running from a different directory
    from backend.services import blog_service, seo_service, image_service, social_service, analytics_service, ad_service
    from backend.services.trend_service import trend_service
    from backend.services.automation_service import automation_service

app = FastAPI(
    title="Blogs Monetizer API",
    description="API for generating, optimizing, and monetizing blog content with AI assistance",
    version="1.0.0",
)

# Add CORS middleware
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],    # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],    # Allows all methods
        allow_headers=["*"],    # Allows all headers
    )
except Exception as e:
    print(f"Warning: Could not add CORS middleware: {e}")

# Global flag to track automation status
automation_running = False
automation_thread = None

# Define Pydantic models for request validation
class BlogGenerateRequest(BaseModel):
    prompt: str

class SeoAnalysisRequest(BaseModel):
    content: str

class ImageGenerateRequest(BaseModel):
    prompt: str

class PublishRequest(BaseModel):
    title: str
    content: str
    image_path: str
    labels: List[str]
    share_on_social: bool = False

class AutomationConfigUpdate(BaseModel):
    posts_per_day: Optional[int] = None
    min_hours_between_posts: Optional[int] = None
    trending_sources: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    min_seo_score: Optional[int] = None

class ConfigUpdate(BaseModel):
    automation: Optional[Dict[str, Any]] = None
    seo: Optional[Dict[str, Any]] = None
    image: Optional[Dict[str, Any]] = None

class AffiliateRequest(BaseModel):
    content: str
    max_affiliate_ads: int = 2
    category: Optional[str] = None

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Blogs Monetizer API"}

@app.post("/api/generate-blog")
async def generate_blog(request: BlogGenerateRequest):
    try:
        content = blog_service.generate_blog_content(request.prompt)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-seo")
async def analyze_seo(request: SeoAnalysisRequest):
    try:
        report = seo_service.analyze_seo(request.content)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-image")
async def generate_image(request: ImageGenerateRequest):
    try:
        image_path = image_service.generate_image(request.prompt)
        return {"image_path": image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/publish")
async def publish(request: PublishRequest):
    try:
        result = blog_service.publish_blog(
            request.title,
            request.content,
            request.image_path,
            request.labels
        )        # Share on social media if requested
        if request.share_on_social:
            social_result = social_service.share_across_platforms(
                message=f"New blog post: {request.title} - Check it out!",
                link=result.get('url', '')
            )
            result['social_share'] = social_result
            
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trending-topics")
async def get_trending_topics(sources: str = "google,news", count: int = 5):
    """Get current trending topics"""
    try:
        sources_list = sources.split(',')
        trends = trend_service.get_trending_topics(sources=sources_list, count=count)
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/start")
async def start_automation(background_tasks: BackgroundTasks, config: Optional[Dict[str, Any]] = None):
    """Start the blog automation process"""
    global automation_running, automation_thread
    
    if automation_running:
        return {"status": "Automation already running"}
    
    try:
        # Set config from request if provided
        if config:
            automation_service.config.update(config)
            
        # Start automation in a background task
        def run_automation():
            global automation_running
            automation_running = True
            automation_service.run()
            automation_running = False
        
        background_tasks.add_task(run_automation)
        automation_running = True
        
        return {
            "status": "Automation started",
            "config": automation_service.config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/stop")
async def stop_automation():
    """Stop the blog automation process"""
    global automation_running
    
    if not automation_running:
        return {"status": "Automation is not running"}
    
    try:
        # This is a crude way to stop the thread - in production you'd want a better mechanism
        automation_running = False
        return {"status": "Automation stop signal sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/automation/status")
async def automation_status():
    """Get automation status and logs"""
    try:
        logs = automation_service.load_logs()
        
        # Get the most recent logs
        recent_logs = logs[-10:] if logs else []
        
        return {
            "running": automation_running,
            "config": automation_service.config,
            "recent_logs": recent_logs,
            "last_post_time": automation_service.last_post_time.isoformat() if automation_service.last_post_time else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/run-now")
async def run_automation_now():
    """Run the automation process once immediately"""
    try:
        result = automation_service.generate_and_publish_blog()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    """Get current configuration settings (non-sensitive)"""
    try:
        # Only return non-sensitive configuration
        safe_config = {
            "automation": {
                "posts_per_day": automation_service.config.get("posts_per_day", 1),
                "min_hours_between_posts": automation_service.config.get("min_hours_between_posts", 8),
                "trending_sources": automation_service.config.get("trending_sources", ["google", "news"]),
                "categories": automation_service.config.get("categories", ["technology", "business", "science"]),
                "min_seo_score": automation_service.config.get("min_seo_score", 70)
            },            "seo": {
                "min_word_count": seo_service.min_word_count,
                "optimal_keyword_density": seo_service.optimal_keyword_density
            },
            "image": {
                "unsplash_api": True,
                "output_dir": image_service.output_dir
            }
        }
        return safe_config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    """Update configuration settings"""
    try:
        # Update automation config
        if config.automation:
            automation_service.config.update(config.automation)
        
        # Update SEO settings
        if config.seo and "min_word_count" in config.seo:
            seo_service.min_word_count = config.seo["min_word_count"]
        if config.seo and "optimal_keyword_density" in config.seo:
            seo_service.optimal_keyword_density = config.seo["optimal_keyword_density"]
        
        # Update image settings
        if config.image and "output_dir" in config.image:
            image_service.output_dir = config.image["output_dir"]
            # Create directory if it doesn't exist
            os.makedirs(image_service.output_dir, exist_ok=True)
        
        return {"status": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_analytics():
    """Get analytics data for the blog"""
    try:
        # Get summary analytics
        summary = analytics_service.get_analytics_summary()
        
        # Get top performing posts
        top_posts = analytics_service.get_top_posts(limit=5)
        
        # Get traffic sources
        traffic_sources = analytics_service.get_traffic_sources()
        
        # Include automation data
        posts_count = len(automation_service.load_logs())
        last_post_time = None
        if automation_service.last_post_time:
            last_post_time = automation_service.last_post_time.isoformat()
        
        return {
            "summary": summary,
            "top_posts": top_posts,
            "traffic_sources": traffic_sources,
            "posts_count": posts_count,
            "last_post": last_post_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/affiliate-products")
async def get_affiliate_products(category: Optional[str] = None, limit: Optional[int] = None):
    """Fetch affiliate products with optional filtering"""
    try:
        # Fetch all affiliate products
        affiliate_products = ad_service.fetch_affiliate_products()
        
        # Filter by category if provided
        if category:
            affiliate_products = [
                product for product in affiliate_products 
                if category.lower() in product.get("category", "").lower()
            ]
            
        # Get total count before limiting
        total_count = len(affiliate_products)
            
        # Limit results if requested
        if limit and limit > 0:
            affiliate_products = affiliate_products[:limit]
        
        return {
            "products": affiliate_products,
            "total": total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/affiliate-products")
async def get_affiliate_products():
    """Get affiliate products from the configured Google Sheet"""
    try:
        from services.ad_service import ad_service
        affiliate_products = ad_service.fetch_affiliate_products()
        return {"products": affiliate_products, "count": len(affiliate_products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/add-affiliate-ads")
async def add_affiliate_ads(request: AffiliateRequest):
    """Add affiliate product ads to blog content based on relevance"""
    try:
        content = request.content
        max_ads = request.max_affiliate_ads
        category_filter = request.category
        
        # Fetch affiliate products
        affiliate_products = ad_service.fetch_affiliate_products()
        
        # Filter products by category if provided
        if category_filter:
            affiliate_products = [
                product for product in affiliate_products 
                if category_filter.lower() in product.get("category", "").lower()
            ]
            
        # Insert affiliate ads into content
        monetized_content = ad_service.insert_affiliate_ads(
            content, 
            affiliate_products, 
            max_affiliate_ads=max_ads
        )
        
        return {
            "content": monetized_content, 
            "products_used": min(max_ads, len(affiliate_products)),
            "total_products_available": len(affiliate_products)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
