"""
Main test runner for the Monetize-blogs system.
This will run all available tests and generate a summary report.
"""

import os
import sys
import importlib
import time
from datetime import datetime
import json

# Add the parent directory to sys.path to allow importing from services
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def run_tests():
    print("\n" + "=" * 80)
    print(f"RUNNING MONETIZE-BLOGS SYSTEM TESTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    # Collect tests to run
    test_modules = [
        "test_trend_service",
        "test_seo_service",
        "test_image_service"
    ]
    
    results = {}
    
    for test_module in test_modules:
        print(f"\n\nRUNNING TEST: {test_module}\n")
        print("-" * 80 + "\n")
        
        try:
            # Import the test module
            module = importlib.import_module(f"tests.{test_module}")
            
            # Get the main test function
            test_function_name = test_module
            if hasattr(module, test_function_name):
                test_function = getattr(module, test_function_name)
            else:
                # Try alternative naming
                test_function_name = f"{test_module.replace('test_', '')}"
                if hasattr(module, test_function_name):
                    test_function = getattr(module, test_function_name)
                else:
                    raise AttributeError(f"Could not find test function in {test_module}")
            
            # Run the test and record result
            start_time = time.time()
            test_function()
            end_time = time.time()
            
            results[test_module] = {
                "status": "success",
                "time_seconds": round(end_time - start_time, 2)
            }
            
        except Exception as e:
            print(f"ERROR in {test_module}: {str(e)}")
            results[test_module] = {
                "status": "error",
                "error": str(e)
            }
    
    # Print summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    error_count = sum(1 for r in results.values() if r["status"] == "error")
    
    print(f"\nTotal tests: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {error_count}")
    
    print("\nDetailed results:")
    for test_name, result in results.items():
        status_symbol = "✓" if result["status"] == "success" else "✗"
        status_text = f"SUCCESS ({result.get('time_seconds', 0)}s)" if result["status"] == "success" else f"ERROR: {result.get('error')}"
        print(f"{status_symbol} {test_name}: {status_text}")
    
    # Save summary to file
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "successful": success_count,
        "failed": error_count,
        "detailed_results": results
    }
    
    output_dir = os.path.join(parent_dir, "logs")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "test_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\nTest summary saved to logs/test_summary.json")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_tests()
