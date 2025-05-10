import re
from collections import Counter
from typing import Dict, List, Optional
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

class SEOService:
    def __init__(self):
        self.min_word_count = 300
        self.optimal_keyword_density = 0.02  # 2%
        self.optimal_max_density = 0.04  # 4%
        self.min_headings = 3
        self.min_paragraphs = 5
        self.max_paragraphs_length = 150  # words
        
        # Set up NLTK resources
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            try:
                nltk.download('punkt', quiet=True)
            except:
                pass
                
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            try:
                nltk.download('stopwords', quiet=True)
            except:
                pass

    def analyze_seo(self, content: str) -> Dict:
        """Analyze content for SEO optimization and provide recommendations"""
        # Strip HTML tags for raw text analysis
        raw_text = re.sub(r'<[^>]*>', ' ', content)
        
        # Run basic text analysis
        words = re.findall(r'\w+', raw_text.lower())
        word_count = len(words)
        
        # Use NLTK for better tokenization if available
        try:
            sentences = sent_tokenize(raw_text)
            stop_words = set(stopwords.words('english'))
        except:
            # Fallback if NLTK fails
            sentences = [s.strip() for s in re.split(r'[.!?]+', raw_text) if s.strip()]
            stop_words = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'on', 'with', 'that', 'this', 'it', 'are', 'be', 'as', 'by', 'was', 'or'}
        
        # Calculate word frequency excluding stop words
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        word_frequency = Counter(filtered_words)
        
        # Find potential keywords (most common meaningful words)
        keywords = {word: count for word, count in word_frequency.most_common(15) 
                   if word not in stop_words}
        
        # Calculate keyword density
        keyword_density = {word: count/word_count for word, count in keywords.items()}
        
        # HTML structure analysis
        headings = len(re.findall(r'<h[1-6][^>]*>', content))
        paragraphs = len(re.findall(r'<p[^>]*>.*?</p>', content, re.DOTALL))
        
        # Check for images
        images = len(re.findall(r'<img[^>]*>', content))
        
        # Average sentence length and paragraph length
        avg_sentence_length = word_count / max(1, len(sentences))
        
        # Check for lists/bullets
        has_lists = bool(re.search(r'<[ou]l[^>]*>.*?</[ou]l>', content, re.DOTALL))
        
        # Compile the issues and recommendations
        issues = []
        recommendations = []
        
        # Content length
        if word_count < self.min_word_count:
            issues.append(f"Content length ({word_count} words) is below recommended minimum of {self.min_word_count}")
            recommendations.append(f"Expand content to at least {self.min_word_count} words for better search engine visibility")
        
        # Keyword density
        keyword_issues = []
        for word, density in keyword_density.items():
            if density > self.optimal_max_density:
                keyword_issues.append(f"Keyword '{word}' is overused (density: {density:.1%})")
                recommendations.append(f"Reduce usage of '{word}' to avoid keyword stuffing")
            elif density < self.optimal_keyword_density / 2 and word in list(keywords.keys())[:5]:
                recommendations.append(f"Consider using the keyword '{word}' more frequently (current density: {density:.1%})")
        
        # Add the top 3 keyword issues to not overwhelm the report
        if keyword_issues:
            issues.extend(keyword_issues[:3])
            if len(keyword_issues) > 3:
                issues.append(f"... and {len(keyword_issues) - 3} more keyword density issues")
        
        # Heading structure
        if headings < self.min_headings:
            issues.append(f"Too few headings ({headings}). Recommended: {self.min_headings}+")
            recommendations.append("Add more headings to structure your content better")
        
        # Paragraph structure
        if paragraphs < self.min_paragraphs:
            issues.append(f"Too few paragraphs ({paragraphs}). Recommended: {self.min_paragraphs}+")
            recommendations.append("Break content into more paragraphs for better readability")
        
        # Image usage
        if images == 0:
            issues.append("No images found in content")
            recommendations.append("Add at least one relevant image to improve engagement")
        
        # List usage
        if not has_lists:
            recommendations.append("Consider adding bulleted or numbered lists to improve readability")
        
        # Sentence length
        if avg_sentence_length > 25:
            issues.append(f"Average sentence length ({avg_sentence_length:.1f} words) is too long")
            recommendations.append("Try to keep sentences under 25 words for better readability")
        
        # Calculate overall SEO score
        score = self._calculate_score(word_count, headings, paragraphs, images, has_lists, len(issues))
        
        return {
            'word_count': word_count,
            'keywords': dict(list(keywords.items())[:10]),  # Top 10 keywords
            'keyword_density': {k: v for k, v in keyword_density.items() if k in dict(list(keywords.items())[:10])},
            'headings': headings,
            'paragraphs': paragraphs,
            'images': images,
            'has_lists': has_lists,
            'avg_sentence_length': avg_sentence_length,
            'issues': issues,
            'recommendations': recommendations,
            'score': score
        }
    
    def _calculate_score(self, word_count: int, headings: int, paragraphs: int, 
                         images: int, has_lists: bool, issues_count: int) -> int:
        """Calculate an overall SEO score based on various factors"""
        base_score = 100
        
        # Deductions for issues
        base_score -= min(50, issues_count * 8)  # Cap at 50 points deduction
        
        # Word count factor
        if word_count < self.min_word_count:
            base_score -= min(25, (self.min_word_count - word_count) // 20)
        
        # Structure factors
        if headings < self.min_headings:
            base_score -= min(15, (self.min_headings - headings) * 5)
            
        if paragraphs < self.min_paragraphs:
            base_score -= min(10, (self.min_paragraphs - paragraphs) * 2)
            
        # Image bonus
        if images > 0:
            base_score += min(5, images * 2)
            
        # Lists bonus
        if has_lists:
            base_score += 5
            
        return max(0, min(100, base_score))
    
    def get_improvement_suggestions(self, content: str, target_keywords: Optional[List[str]] = None) -> Dict:
        """Get specific suggestions to improve content for better SEO"""
        seo_report = self.analyze_seo(content)
        
        suggestions = []
        
        # Content length suggestions
        if seo_report['word_count'] < self.min_word_count:
            suggestions.append({
                "type": "content_length",
                "suggestion": f"Add about {self.min_word_count - seo_report['word_count']} more words to reach the minimum recommended length of {self.min_word_count} words",
                "priority": "high"
            })
        
        # Structure suggestions
        if seo_report['headings'] < self.min_headings:
            suggestions.append({
                "type": "headings",
                "suggestion": "Add more headings (H1, H2, H3) to better structure your content",
                "priority": "medium"
            })
            
        # Target keyword suggestions
        if target_keywords:
            for keyword in target_keywords:
                if keyword.lower() not in content.lower():
                    suggestions.append({
                        "type": "keyword_usage",
                        "suggestion": f"Include the target keyword '{keyword}' in your content",
                        "priority": "high"
                    })
        
        # Image suggestions
        if seo_report['images'] == 0:
            suggestions.append({
                "type": "images",
                "suggestion": "Add at least one relevant image with appropriate alt text",
                "priority": "medium"
            })
        
        # List suggestions
        if not seo_report['has_lists']:
            suggestions.append({
                "type": "lists",
                "suggestion": "Consider adding a bulleted or numbered list to improve readability",
                "priority": "low"
            })
            
        # Include original recommendations
        for rec in seo_report['recommendations']:
            suggestions.append({
                "type": "general",
                "suggestion": rec,
                "priority": "medium"
            })
        
        return {
            "score": seo_report['score'],
            "suggestions": suggestions
        }

seo_service = SEOService()