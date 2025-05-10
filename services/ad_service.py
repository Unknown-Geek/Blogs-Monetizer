"""
Ad monetization service for blog content.
Implements various ad formats and placement strategies.
"""
import os
import json
from typing import Dict, List, Optional, Union
from datetime import datetime
import re

class AdService:
    """
    Service for managing ad placements and monetization strategies.
    
    Key Features:
    - Supports both CPM (cost per thousand impressions) and CPA (cost per action/click) models
    - Manages different ad formats (banners, leaderboards, skyscrapers, interstitials)
    - Analyzes content for optimal ad placement
    - Tracks ad performance and generates revenue estimates
    """
    
    def __init__(self):
        # Create log directory for ad performance tracking
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.ad_log = os.path.join(self.log_dir, "ad_performance.json")
        
        # Initialize ad networks and formats
        self.ad_networks = {
            "google": {
                "name": "Google AdSense",
                "model": "hybrid",  # Supports both CPM and CPA
                "position": "recommended"
            },
            "carbon": {
                "name": "Carbon Ads",
                "model": "cpm",
                "position": "sidebar"
            },
            "direct": {
                "name": "Direct Advertisers",
                "model": "custom",
                "position": "premium"
            }
        }
        
        self.ad_formats = {
            "banner": {
                "name": "Banner",
                "description": "Wide rectangular ad (468x60)",
                "nickname": "wide fella"
            },
            "leaderboard": {
                "name": "Leaderboard",
                "description": "Wide banner at top/bottom (728x90)",
                "nickname": "wide fella"
            },
            "skyscraper": {
                "name": "Skyscraper",
                "description": "Tall, narrow ad (160x600)",
                "nickname": "long lad"
            },
            "rectangle": {
                "name": "Medium Rectangle",
                "description": "Square ad in content (300x250)",
                "nickname": "box buddy"
            },
            "interstitial": {
                "name": "Interstitial",
                "description": "Full-page ad between content",
                "nickname": "page blocker"
            }
        }
        
        # Default CPM rates for estimation
        self.default_cpm_rates = {
            "banner": 1.50,
            "leaderboard": 2.00,
            "skyscraper": 1.75,
            "rectangle": 3.50,
            "interstitial": 8.00
        }

    def prepare_content_for_ads(self, content: str, ad_density: str = "medium") -> str:
        """
        Analyze content and insert ad placement hooks based on content length and structure.
        
        Args:
            content: HTML content
            ad_density: Desired ad density ("low", "medium", "high")
            
        Returns:
            Content with ad placement hooks
        """
        # Count paragraphs to determine potential ad placements
        paragraphs = re.findall(r'<p>.*?</p>', content, re.DOTALL)
        word_count = sum(len(re.findall(r'\w+', p)) for p in paragraphs)
        
        # Determine ad count based on density and word count
        density_factors = {"low": 0.5, "medium": 1.0, "high": 1.5}
        factor = density_factors.get(ad_density, 1.0)
        
        # Base formula: 1 ad per 300 words with the density factor applied
        ad_count = max(1, int((word_count / 300) * factor))
        
        # Limit ads based on Google's policy (max 1 ad per X words)
        max_allowed = max(1, word_count // 250)
        ad_count = min(ad_count, max_allowed)
        
        # Calculate optimal positions
        positions = []
        if len(paragraphs) > 3:
            # Place ads evenly throughout the content
            interval = len(paragraphs) // (ad_count + 1)
            positions = [interval * i for i in range(1, ad_count + 1)]
            
            # Ensure ads aren't too close together
            min_distance = 2
            filtered_positions = []
            last_pos = -min_distance - 1
            for pos in positions:
                if pos - last_pos > min_distance:
                    filtered_positions.append(pos)
                    last_pos = pos
            positions = filtered_positions
        
        # Create HTML with ad placement hooks
        parts = []
        for i, p in enumerate(paragraphs):
            parts.append(p)
            if i in positions:
                ad_format = self._choose_optimal_ad_format(i, len(paragraphs))
                parts.append(f'<!-- AD_PLACEMENT: {ad_format} -->')
        
        # Always add a rectangle ad after the first few paragraphs if there's enough content
        if len(paragraphs) >= 5 and 2 not in positions:
            rectangle_hook = '<!-- AD_PLACEMENT: rectangle -->'
            parts.insert(3, rectangle_hook)
            
        # Consider a leaderboard at the end for longer content
        if word_count > 800 and (len(paragraphs) - 1) not in positions:
            parts.append('<!-- AD_PLACEMENT: leaderboard -->')
        
        # Log the ad placement plan
        self._log_ad_placement({
            "content_stats": {
                "word_count": word_count,
                "paragraph_count": len(paragraphs)
            },
            "ad_placement": {
                "density": ad_density,
                "ad_count": len(positions) + (1 if word_count > 800 else 0) + (1 if len(paragraphs) >= 5 else 0),
                "positions": positions
            },
            "timestamp": datetime.now().isoformat()
        })
        
        return "".join(parts)
    
    def render_ad_code(self, ad_format: str, network: str = "google") -> str:
        """
        Generate the HTML code for an ad based on format and network.
        
        Args:
            ad_format: Type of ad ("banner", "leaderboard", etc.)
            network: Ad network to use
            
        Returns:
            HTML code for the ad
        """        # NOTE: These are placeholders - in a real implementation,
        # you'd use actual ad codes from the networks
        if network == "google":
            return f'''
            <div class="ad-container {ad_format}">
                <!-- Google AdSense {self.ad_formats.get(ad_format, {}).get('name', 'Ad')} -->
                <ins class="adsbygoogle"
                     style="display:block"
                     data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
                     data-ad-slot="XXXXXXXXXX"
                     data-ad-format="{ad_format}"></ins>
                <script>(adsbygoogle = window.adsbygoogle || []).push({{}})</script>
                <!-- Fallback content in case ads don't load -->
                <div class="ad-fallback" style="border: 1px dashed #ccc; padding: 10px; margin-top: 5px; font-size: 12px; color: #666;">
                    Advertisement: {self.ad_formats.get(ad_format, {}).get('name', 'Ad')} ({ad_format})
                </div>
            </div>
            '''
        elif network == "carbon":
            return f'''
            <div class="ad-container carbon {ad_format}">
                <script async type="text/javascript" src="//cdn.carbonads.com/carbon.js?serve=XXXXXXXX&placement=XXXXX" id="_carbonads_js"></script>
                <!-- Fallback content in case ads don't load -->                <div class="ad-fallback" style="border: 1px dashed #ccc; padding: 10px; margin-top: 5px; font-size: 12px; color: #666;">
                    Advertisement: Carbon {self.ad_formats.get(ad_format, {}).get('name', 'Ad')}
                </div>
            </div>
            '''
        else:  # Direct or other networks
            return f'''
            <div class="ad-container {ad_format} custom-ad">
                <!-- Custom {self.ad_formats.get(ad_format, {}).get('name', 'Advertisement')} -->
                <div class="custom-ad-content">
                    Your Ad Here - Contact us for advertising options
                </div>
            </div>
            '''
    
    def insert_ads_into_content(self, content: str, network: str = "google") -> str:
        """
        Replace ad placement hooks with actual ad code.
        
        Args:
            content: HTML content with ad placement hooks
            network: Ad network to use
            
        Returns:
            Content with actual ads inserted
        """
        for ad_format in self.ad_formats:
            placeholder = f'<!-- AD_PLACEMENT: {ad_format} -->'
            ad_code = self.render_ad_code(ad_format, network)
            content = content.replace(placeholder, ad_code)
        return content
    
    def estimate_revenue(self, content: str, views: int = 1000) -> Dict:
        """
        Estimate potential ad revenue based on content and expected views.
        
        Args:
            content: HTML content to analyze
            views: Expected number of views
            
        Returns:
            Dict with revenue estimates
        """
        # Count ad placements by type
        ad_counts = {}
        for ad_format in self.ad_formats:
            count = content.count(f'<!-- AD_PLACEMENT: {ad_format} -->')
            ad_counts[ad_format] = count
        
        # Calculate CPM-based revenue estimates
        cpm_revenue = 0
        for ad_format, count in ad_counts.items():
            rate = self.default_cpm_rates.get(ad_format, 1.0)
            # CPM is per 1000 impressions
            format_revenue = (views / 1000) * rate * count
            cpm_revenue += format_revenue
        
        # Estimate CPC (Cost Per Click) revenue
        # Assuming 0.5% CTR (Click Through Rate)
        ctr = 0.005
        avg_cpc = 0.50  # Average cost per click in dollars
        cpc_revenue = views * ctr * avg_cpc
        
        return {
            "views": views,
            "ad_placements": ad_counts,
            "estimated_revenue": {
                "cpm_model": round(cpm_revenue, 2),
                "cpc_model": round(cpc_revenue, 2),
                "total": round(cpm_revenue + cpc_revenue, 2)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_ad_strategy(self, content_info: Dict) -> Dict:
        """
        Generate a recommended ad strategy based on content information.
        
        Args:
            content_info: Dict with content metadata (topic, length, audience, etc.)
            
        Returns:
            Dict with ad strategy recommendations
        """
        topic = content_info.get("topic", "")
        word_count = content_info.get("word_count", 0)
        audience = content_info.get("audience", "general")
        
        # Default strategy
        strategy = {
            "density": "medium",
            "primary_network": "google",
            "secondary_network": None,
            "recommended_formats": ["rectangle", "leaderboard"],
            "placement_strategy": "standard",
            "ethical_considerations": []
        }
        
        # Adjust based on content length
        if word_count < 500:
            strategy["density"] = "low"
            strategy["recommended_formats"] = ["rectangle"]
        elif word_count > 1500:
            strategy["density"] = "medium"  # More content but keep reasonable
            strategy["recommended_formats"].append("skyscraper")
            strategy["secondary_network"] = "direct"  # Try direct advertisers for longer content
            
        # Add ethical considerations
        if "health" in topic.lower() or "medical" in topic.lower():
            strategy["ethical_considerations"].append(
                "Health-related content should avoid misleading ads or products with unverified claims."
            )
            
        if "children" in audience.lower() or "kids" in audience.lower():
            strategy["ethical_considerations"].append(
                "Content for children should comply with COPPA and avoid behavior-based targeting."
            )
            strategy["density"] = "low"  # Reduce ad density for children's content
        
        # Log the strategy generation
        self._log_strategy(strategy, content_info)
        
        return strategy
    
    def _choose_optimal_ad_format(self, position: int, total_paragraphs: int) -> str:
        """Choose the best ad format based on position within content"""
        position_ratio = position / total_paragraphs
        
        if position <= 2:
            return "rectangle"  # Early in content
        elif position_ratio >= 0.8:
            return "leaderboard"  # Near the end
        elif 0.3 <= position_ratio <= 0.7:
            return "skyscraper" if position % 2 == 0 else "rectangle"  # Middle of content
        else:
            return "banner"  # Default
    
    def _log_ad_placement(self, placement_data: Dict) -> None:
        """Log ad placement information"""
        self._append_to_log("ad_placements", placement_data)
    
    def _log_strategy(self, strategy: Dict, content_info: Dict) -> None:
        """Log ad strategy generation"""
        log_entry = {
            "strategy": strategy,
            "content_info": content_info,
            "timestamp": datetime.now().isoformat()
        }
        self._append_to_log("ad_strategies", log_entry)
    
    def _append_to_log(self, log_type: str, data: Dict) -> None:
        """Append data to the specified log file"""
        log_path = os.path.join(self.log_dir, f"{log_type}.json")
        
        try:
            # Load existing logs
            logs = []
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    logs = json.load(f)
            
            # Ensure it's a list
            if not isinstance(logs, list):
                logs = []
                
            # Add new log entry
            logs.append(data)
            
            # Save logs
            with open(log_path, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Error logging to {log_type}: {str(e)}")

# Singleton instance
ad_service = AdService()
