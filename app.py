import subprocess
from fastapi import FastAPI

app = FastAPI(title="Blogs Monetizer Space API")

@app.get("/")
def root():
    # Run the generate_sample_blog.py script and capture its output
    try:
        result = subprocess.run([
            "python", "generate_blog.py"
        ], capture_output=True, text=True, check=True)
        output = result.stdout
        return {"message": "Blog generated.", "output": output}
    except subprocess.CalledProcessError as e:
        return {"error": str(e), "output": e.output, "stderr": e.stderr}
