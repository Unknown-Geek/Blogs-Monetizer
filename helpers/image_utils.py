import os
import shutil
from datetime import datetime

def clear_images_directory():
    """Clear the images directory of all image files and their metadata"""
    # Define the images directory path
    images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
    
    if not os.path.exists(images_dir):
        print(f"Images directory does not exist: {images_dir}")
        return False
    
    try:
        # Get all files in the directory
        file_count = 0
        for filename in os.listdir(images_dir):
            file_path = os.path.join(images_dir, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
                file_count += 1
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                file_count += 1
        
        print(f"Cleared {file_count} files from images directory: {images_dir}")
        return True
    except Exception as e:
        print(f"Error clearing images directory: {str(e)}")
        return False
