import re
from collections import Counter
from typing import Dict, List

class SEOService:
    def __init__(self):
        self.min_word_count = 300
        self.optimal_keyword_density = 0.02  # 2%

    def analyze_seo(self, content: str) -> Dict:
        words = re.findall(r'\w+', content.lower())
        word_count = len(words)
        word_frequency = Counter(words)
        
        # Find potential keywords (most common words excluding common stop words)
        stop_words = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'on', 'with'}
        keywords = {word: count for word, count in word_frequency.most_common(10) 
                   if word not in stop_words}
        
        # Calculate keyword density
        keyword_density = {word: count/word_count for word, count in keywords.items()}
        
        # Basic SEO checks
        issues = []
        if word_count < self.min_word_count:
            issues.append(f"Content length ({word_count} words) is below recommended minimum of {self.min_word_count}")
        
        for word, density in keyword_density.items():
            if density > self.optimal_keyword_density * 2:
                issues.append(f"Keyword '{word}' may be overused (density: {density:.1%})")
        
        return {
            'word_count': word_count,
            'keywords': keywords,
            'keyword_density': keyword_density,
            'issues': issues,
            'score': self._calculate_score(word_count, issues)
        }
    
    def _calculate_score(self, word_count: int, issues: List[str]) -> int:
        base_score = 100
        if word_count < self.min_word_count:
            base_score -= 20
        base_score -= len(issues) * 10
        return max(0, base_score)

seo_service = SEOService()