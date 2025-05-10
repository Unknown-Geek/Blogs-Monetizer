from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import threading
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Import services
try:
    from services import blog_service, seo_service, image_service, social_service, analytics_service
    from services.trend_service import trend_service
    from services.automation_service import automation_service
except ImportError:
    # Alternative import if running from a different directory
    from backend.services import blog_service, seo_service, image_service, social_service, analytics_service
    from backend.services.trend_service import trend_service
    from backend.services.automation_service import automation_service

app = Flask(__name__)
CORS(app)

# Global flag to track automation status
automation_running = False
automation_thread = None

@app.route('/api/generate-blog', methods=['POST'])
def generate_blog():
    data = request.json
    try:
        content = blog_service.generate_blog_content(data['prompt'])
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-seo', methods=['POST'])
def analyze_seo():
    data = request.json
    try:
        report = seo_service.analyze_seo(data['content'])
        return jsonify({'report': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    try:
        image_path = image_service.generate_image(data['prompt'])
        return jsonify({'image_path': image_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/publish', methods=['POST'])
def publish():
    data = request.json
    try:
        result = blog_service.publish_blog(
            data['title'],
            data['content'],
            data['image_path'],
            data['labels']
        )
        
        # Share on social media if requested
        if data.get('share_on_social', False):
            social_result = social_service.share_on_twitter(
                f"New blog post: {data['title']} - Check it out! {result.get('url', '')}"
            )
            result['social_share'] = social_result
            
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trending-topics', methods=['GET'])
def get_trending_topics():
    """Get current trending topics"""
    try:
        sources = request.args.get('sources', 'google,news').split(',')
        count = int(request.args.get('count', 5))
        
        trends = trend_service.get_trending_topics(sources=sources, count=count)
        return jsonify({'trends': trends})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """Start the blog automation process"""
    global automation_running, automation_thread
    
    if automation_running:
        return jsonify({'status': 'Automation already running'})
    
    try:
        # Set config from request if provided
        if request.json:
            automation_service.config.update(request.json)
            
        # Start automation in a separate thread
        def run_automation():
            global automation_running
            automation_running = True
            automation_service.run()
            automation_running = False
            
        automation_thread = threading.Thread(target=run_automation)
        automation_thread.daemon = True
        automation_thread.start()
        
        return jsonify({
            'status': 'Automation started',
            'config': automation_service.config
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    """Stop the blog automation process"""
    global automation_running
    
    if not automation_running:
        return jsonify({'status': 'Automation is not running'})
    
    try:
        # This is a crude way to stop the thread - in production you'd want a better mechanism
        automation_running = False
        return jsonify({'status': 'Automation stop signal sent'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/status', methods=['GET'])
def automation_status():
    """Get automation status and logs"""
    try:
        logs = automation_service.load_logs()
        
        # Get the most recent logs
        recent_logs = logs[-10:] if logs else []
        
        return jsonify({
            'running': automation_running,
            'config': automation_service.config,
            'recent_logs': recent_logs,
            'last_post_time': automation_service.last_post_time.isoformat() if automation_service.last_post_time else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/automation/run-now', methods=['POST'])
def run_automation_now():
    """Run the automation process once immediately"""
    try:
        result = automation_service.generate_and_publish_blog()
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
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
            },
            "seo": {
                "min_word_count": seo_service.min_word_count,
                "optimal_keyword_density": seo_service.optimal_keyword_density
            },
            "image": {
                "model": image_service.model,
                "output_dir": image_service.output_dir
            }
        }
        return jsonify(safe_config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration settings"""
    data = request.json
    try:
        # Update automation config
        if "automation" in data:
            automation_service.config.update(data["automation"])
        
        # Update SEO settings
        if "seo" in data and "min_word_count" in data["seo"]:
            seo_service.min_word_count = data["seo"]["min_word_count"]
        if "seo" in data and "optimal_keyword_density" in data["seo"]:
            seo_service.optimal_keyword_density = data["seo"]["optimal_keyword_density"]
        
        # Update image settings
        if "image" in data and "output_dir" in data["image"]:
            image_service.output_dir = data["image"]["output_dir"]
            # Create directory if it doesn't exist
            os.makedirs(image_service.output_dir, exist_ok=True)
        
        return jsonify({"status": "Configuration updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
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
        
        return jsonify({
            'summary': summary,
            'top_posts': top_posts,
            'traffic_sources': traffic_sources,
            'posts_count': posts_count,
            'last_post': last_post_time
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)