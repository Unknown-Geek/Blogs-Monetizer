"""
Test the SEO service to make sure it's working properly.
This will:
1. Analyze a sample piece of content
2. Generate improvement suggestions
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to sys.path to allow importing from services
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the SEO service
from services.seo_service import seo_service

def test_seo_service():
    print("Testing SEO Service...")
    print("=" * 80)
    
    # Sample content with different qualities for testing
    sample_content_good = """
    <h1>Ultimate Guide to SEO in 2024</h1>
    <p>Search Engine Optimization continues to evolve in 2024. With the rise of AI and new algorithms, businesses need to adapt their strategies to stay competitive in search results.</p>
    
    <h2>Key SEO Trends for 2024</h2>
    <p>Several major trends are shaping SEO this year. Voice search is gaining popularity as more households adopt smart speakers and voice assistants. Mobile optimization remains crucial with Google's mobile-first indexing.</p>
    <p>User experience signals are heavily weighted in rankings now. Page speed, interactivity, and visual stability (Core Web Vitals) directly impact how well your site performs in search results.</p>
    
    <h2>Technical SEO Best Practices</h2>
    <p>Technical optimization forms the foundation of good SEO practices. Start with a crawlable site structure that makes it easy for search engines to discover your content.</p>
    <ul>
        <li>Implement proper schema markup</li>
        <li>Optimize image size and use descriptive alt text</li>
        <li>Create a comprehensive XML sitemap</li>
        <li>Use canonical tags to prevent duplicate content issues</li>
    </ul>
    
    <h2>Content Strategy</h2>
    <p>Content remains king in the SEO world. However, the focus has shifted from keyword stuffing to creating comprehensive, valuable resources that answer user questions.</p>
    <p>Topic clusters work well for establishing authority. Create pillar content that broadly covers a topic, then link to cluster content that addresses specific aspects in detail.</p>
    
    <h3>E-A-T Principle</h3>
    <p>Google's E-A-T (Expertise, Authoritativeness, Trustworthiness) principle has become increasingly important, especially for YMYL (Your Money Your Life) topics.</p>
    
    <h2>Conclusion</h2>
    <p>SEO continues to evolve, but the fundamentals remain: create valuable content, optimize for technical excellence, and build your site's authority. By staying current with these best practices, you'll be well-positioned for SEO success in 2024 and beyond.</p>
    """
    
    sample_content_poor = """
    SEO Tips
    
    Here are some tips for better SEO. First, use keywords. Second, have good content. Third, get backlinks from other sites.
    
    Make sure your website loads fast. Also use headings.
    """
    
    # Analyze both samples
    print("Analyzing good quality content...")
    good_analysis = seo_service.analyze_seo(sample_content_good)
    
    print(f"Word count: {good_analysis['word_count']}")
    print(f"SEO score: {good_analysis['score']}")
    print(f"Headings: {good_analysis['headings']}")
    print(f"Paragraphs: {good_analysis['paragraphs']}")
    print(f"Top keywords: {list(good_analysis['keywords'].keys())[:5]}")
    
    if good_analysis['issues']:
        print("\nIssues found:")
        for issue in good_analysis['issues']:
            print(f"- {issue}")
    else:
        print("\nNo issues found!")
    
    print("\n" + "-" * 80 + "\n")
    
    print("Analyzing poor quality content...")
    poor_analysis = seo_service.analyze_seo(sample_content_poor)
    
    print(f"Word count: {poor_analysis['word_count']}")
    print(f"SEO score: {poor_analysis['score']}")
    print(f"Headings: {poor_analysis['headings']}")
    print(f"Paragraphs: {poor_analysis['paragraphs']}")
    print(f"Top keywords: {list(poor_analysis['keywords'].keys())[:5]}")
    
    if poor_analysis['issues']:
        print("\nIssues found:")
        for issue in poor_analysis['issues']:
            print(f"- {issue}")
    
    # Test improvement suggestions
    print("\nTesting improvement suggestions for poor content...")
    suggestions = seo_service.get_improvement_suggestions(
        sample_content_poor, 
        target_keywords=["SEO", "optimization", "search engine"]
    )
    
    print(f"Improvement score: {suggestions['score']}")
    
    print("\nImprovement suggestions:")
    for suggestion in suggestions['suggestions']:
        print(f"- [{suggestion['priority']}] {suggestion['suggestion']}")
    
    # Save the results to a file for inspection
    results = {
        "timestamp": datetime.now().isoformat(),
        "good_content_analysis": good_analysis,
        "poor_content_analysis": poor_analysis,
        "improvement_suggestions": suggestions
    }
    
    output_dir = os.path.join(parent_dir, "logs")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "seo_test_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nTest results saved to logs/seo_test_results.json")
    print("=" * 80)

if __name__ == "__main__":
    test_seo_service()
