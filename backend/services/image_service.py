from transformers import pipeline

class ImageService:
    def __init__(self):
        self.model = "stabilityai/stable-diffusion-xl-base-1.0"
        
    def generate_image(self, prompt):
        pipe = pipeline("text-to-image", model=self.model)
        image = pipe(prompt, num_inference_steps=50)["images"][0]
        image_path = "blog_image.png"
        image.save(image_path)
        return image_path

image_service = ImageService()