from transformers import pipeline
import os
from dotenv import load_dotenv

# Load environment variables if not already loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class ImageService:
    def __init__(self):
        self.model = os.environ.get("IMAGE_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
        self.output_dir = os.environ.get("IMAGE_OUTPUT_DIR", ".")
        
    def generate_image(self, prompt):
        pipe = pipeline("text-to-image", model=self.model)
        image = pipe(prompt, num_inference_steps=50)["images"][0]
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save image to the configured directory
        image_path = os.path.join(self.output_dir, "blog_image.png")
        image.save(image_path)
        return image_path

image_service = ImageService()