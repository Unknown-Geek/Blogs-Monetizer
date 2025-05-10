"""
Test the conversion of ad placement hooks to real ad HTML.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(parent_dir))

from services.ad_service import ad_service

def test_ad_conversion():
    """Test converting ad placement hooks to real ad HTML and save to a test file."""
    print("Testing ad placement conversion...")
    
    # Sample content with ad placement hooks
    sample_content = """
    <h1>Ad Test Article</h1>
    <p>This is the first paragraph of our test article.</p>
    <p>Here's a second paragraph with more content.</p>
    <!-- AD_PLACEMENT: rectangle -->
    <h2>Second Section</h2>
    <p>This is the start of our second section.</p>
    <p>More content in the second section.</p>
    <!-- AD_PLACEMENT: skyscraper -->
    <p>Final paragraph before the conclusion.</p>
    <h2>Conclusion</h2>
    <p>This is our conclusion paragraph.</p>
    <!-- AD_PLACEMENT: leaderboard -->
    """
    
    # Add CSS for ad containers
    ad_styles = """
    <style>
    .ad-container {
        margin: 20px 0;
        padding: 10px;
        text-align: center;
        background-color: #f9f9f9;
        border-radius: 5px;
        clear: both;
        overflow: hidden;
    }
    .ad-container.leaderboard {
        max-width: 728px;
        margin: 20px auto;
    }
    .ad-container.skyscraper {
        float: right;
        margin: 0 0 15px 15px;
    }
    .ad-container.rectangle {
        margin: 20px auto;
        max-width: 300px;
    }
    .custom-ad-content {
        padding: 20px;
        border: 1px dashed #ccc;
        color: #777;
        font-size: 14px;
    }
    </style>
    """
    
    # Try all supported ad networks
    networks = ["google", "carbon", "direct"]
    output_path = Path(__file__).parent / "ad_conversion_result.html"
    
    with open(output_path, "w") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write("<title>Ad Conversion Test Results</title>\n")
        f.write(ad_styles)
        f.write('\n<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>\n')
        f.write("</head>\n<body>\n")
        
        for network in networks:
            f.write(f"<h1>Ad Network: {network.capitalize()}</h1>\n")
            
            # Convert ad hooks to actual ad HTML
            content_with_ads = ad_service.insert_ads_into_content(sample_content, network)
            
            # Write the result to the output file
            f.write(content_with_ads)
            
            f.write("<hr>\n")
        
        f.write("</body>\n</html>")
    
    print(f"Test results saved to: {output_path}")
    print(f"Open this file in a browser to verify ad rendering")

if __name__ == "__main__":
    test_ad_conversion()
