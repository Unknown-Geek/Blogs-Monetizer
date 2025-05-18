import subprocess
import threading
import time
import datetime
import os
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse

app = FastAPI(title="Blogs Monetizer Space API")

# Global flag to control the heartbeat
heartbeat_running = False
last_blog_generation = None

def generate_blog():
    """Function to generate a blog post"""
    global last_blog_generation
    try:
        print(f"[{datetime.datetime.now()}] Running scheduled blog generation...")
        result = subprocess.run([
            "python", "generate_blog.py"
        ], capture_output=True, text=True, check=True)
        output = result.stdout
        last_blog_generation = datetime.datetime.now()
        print(f"[{datetime.datetime.now()}] Blog generation completed")
        return {"success": True, "message": "Blog generated.", "output": output}
    except subprocess.CalledProcessError as e:
        error_message = f"Error: {str(e)}, Output: {e.output}, Stderr: {e.stderr}"
        print(f"[{datetime.datetime.now()}] Blog generation failed: {error_message}")
        return {"success": False, "error": error_message}

def heartbeat_task():
    """Background task to keep the server alive by generating blogs periodically"""
    global heartbeat_running
    
    # Get the interval from environment or default to 15 minutes
    interval_minutes = int(os.environ.get("HEARTBEAT_INTERVAL_MINUTES", 15))
    
    print(f"[{datetime.datetime.now()}] Starting heartbeat task with {interval_minutes} minute interval")
    
    while heartbeat_running:
        try:
            generate_blog()
        except Exception as e:
            print(f"[{datetime.datetime.now()}] Error in heartbeat task: {str(e)}")
            
        # Sleep for the specified interval
        time.sleep(interval_minutes * 60)

@app.on_event("startup")
def startup_event():
    """Start the heartbeat task when the application starts"""
    global heartbeat_running
    
    # Check if heartbeat is enabled (default to enabled)
    heartbeat_enabled = os.environ.get("ENABLE_HEARTBEAT", "true").lower() == "true"
    
    if heartbeat_enabled:
        heartbeat_running = True
        threading.Thread(target=heartbeat_task, daemon=True).start()
        print(f"[{datetime.datetime.now()}] Heartbeat task started")

@app.on_event("shutdown")
def shutdown_event():
    """Stop the heartbeat task when the application shuts down"""
    global heartbeat_running
    heartbeat_running = False
    print(f"[{datetime.datetime.now()}] Heartbeat task stopped")

@app.get("/")
def root():
    """Manual trigger for blog generation"""
    # Run the generate_blog.py script and capture its output
    result = generate_blog()
    if result["success"]:
        return {"message": "Blog generated.", "output": result["output"]}
    else:
        return JSONResponse(
            status_code=500,
            content={"error": result["error"]}
        )

@app.get("/status")
def status():
    """Get the status of the heartbeat task"""
    global heartbeat_running, last_blog_generation
    
    interval_minutes = int(os.environ.get("HEARTBEAT_INTERVAL_MINUTES", 15))
    
    return {
        "heartbeat_running": heartbeat_running,
        "heartbeat_interval_minutes": interval_minutes,
        "last_blog_generation": last_blog_generation.isoformat() if last_blog_generation else None,
        "current_time": datetime.datetime.now().isoformat()
    }
