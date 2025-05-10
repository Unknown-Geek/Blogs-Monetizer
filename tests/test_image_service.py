"""
Test the image service to make sure it's working properly.
This will:
1. Generate images based on different prompts
2. Test the fallback functionality
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to sys.path to allow importing from services
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the image service
from services.image_service import image_service

def test_image_service():
    print("Testing Image Service...")
    print("=" * 80)
    
    # Test prompts to try
    test_prompts = [
        "A beautiful landscape with mountains and a lake",
        "Modern technology and artificial intelligence concept",
        "Healthy food and nutrition",
        "Business professionals in a meeting",
        "ThisIsARandomStringThatShouldNotReturnResults12345"  # Should trigger fallback
    ]
    
    results = []
    
    for i, prompt in enumerate(test_prompts):
        print(f"Testing prompt #{i+1}: {prompt}")
        try:
            start_time = datetime.now()
            image_path = image_service.generate_image(prompt)
            end_time = datetime.now()
            
            elapsed_seconds = (end_time - start_time).total_seconds()
            
            if image_path:
                # Check if this is a fallback image
                is_fallback = "fallback" in os.path.basename(image_path).lower()
                
                print(f"✓ Success! Image saved to: {image_path}")
                print(f"  Time taken: {elapsed_seconds:.2f} seconds")
                print(f"  Fallback used: {'Yes' if is_fallback else 'No'}")
                
                # Get attribution if available
                attribution_path = image_path + ".json"
                attribution = None
                if os.path.exists(attribution_path):
                    with open(attribution_path, 'r') as f:
                        attribution = json.load(f)
                
                results.append({
                    "prompt": prompt,
                    "success": True,
                    "image_path": image_path,
                    "time_seconds": elapsed_seconds,
                    "is_fallback": is_fallback,
                    "attribution": attribution
                })
            else:
                print(f"✗ Failed! No image was generated.")
                results.append({
                    "prompt": prompt,
                    "success": False,
                    "time_seconds": elapsed_seconds,
                    "error": "No image path returned"
                })
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            results.append({
                "prompt": prompt,
                "success": False,
                "error": str(e)
            })
        
        print("-" * 80)
    
    # Test the fallback function directly
    print("\nTesting fallback function directly...")
    try:
        fallback_image = image_service._use_fallback_image("direct fallback test")
        if fallback_image:
            print(f"✓ Direct fallback function works! Image: {fallback_image}")
            results.append({
                "prompt": "direct fallback test",
                "success": True,
                "image_path": fallback_image,
                "is_fallback": True
            })
        else:
            print("✗ Direct fallback function failed!")
            results.append({
                "prompt": "direct fallback test",
                "success": False,
                "error": "Fallback function returned None"
            })
    except Exception as e:
        print(f"✗ Error testing fallback: {str(e)}")
        results.append({
            "prompt": "direct fallback test",
            "success": False,
            "error": str(e)
        })
    
    # Save the results to a file for inspection
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "service_config": {
            "api_key_available": bool(image_service.unsplash_api_key),
            "output_dir": image_service.output_dir,
            "fallback_dir": image_service.fallback_dir
        },
        "test_results": results
    }
    
    output_dir = os.path.join(parent_dir, "logs")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "image_test_results.json"), "w") as f:
        json.dump(test_results, f, indent=2)
    
    print("\nTest results saved to logs/image_test_results.json")
    print("=" * 80)

if __name__ == "__main__":
    test_image_service()
