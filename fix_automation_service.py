"""
Script to fix the automation_service.py file by removing the duplicate image_utils import
and fixing the indentation.
"""
import os
import re

def fix_automation_service():
    # Path to the automation_service.py file
    file_path = os.path.join('services', 'automation_service.py')
    
    # Read the original file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix duplicate imports
    content = re.sub(r'from \.image_utils import clear_images_directory\nfrom \.image_utils import clear_images_directory',
                     'from .image_utils import clear_images_directory', content)
    
    # Fix indentation of the try/except block
    pattern = r"(\s+)# 9\. Publish blog\s+try:\s+result = blog_service\.publish_blog\(.*?\s+title=.*?,\s+content=.*?,\s+image_path=.*?,\s+labels=.*?\s+\)\s+\s+if result\.get"
    replacement = r"\1# 9. Publish blog\n\1try:\n\1    result = blog_service.publish_blog(\n\1        title=blog_title,\n\1        content=content,\n\1        image_path=image_path,\n\1        labels=labels\n\1    )\n\1    \n\1    if result.get"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Change trending_sources config to use only news
    content = re.sub(r'("trending_sources": \[)"google", "news"(\])',
                     r'\1"news"\2', content)
    
    # Change platforms to only use twitter
    content = re.sub(r'(platforms=\[)"twitter", "facebook"(\])',
                     r'\1"twitter"\2', content)
    
    # Add image directory clearing
    after_reset_pattern = r'(# Reset failure count for this topic\s+self\._reset_failure_count\(selected_topic\))'
    after_reset_replacement = r'\1\n                    \n                    # Clear the images directory after successful posting\n                    try:\n                        if clear_images_directory():\n                            log_entry["images_cleared"] = True\n                        else:\n                            log_entry["images_cleared"] = False\n                    except Exception as e:\n                        log_entry["images_clear_error"] = str(e)'
    content = re.sub(after_reset_pattern, after_reset_replacement, content)
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_automation_service()
