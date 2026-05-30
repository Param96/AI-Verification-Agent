from bs4 import BeautifulSoup
import re
from typing import Dict, Any

class WebExtractor:
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.text_content = self.soup.get_text(separator=' ', strip=True)
        
    def extract_all(self) -> Dict[str, Any]:
        """Extracts structured and unstructured information from the webpage."""
        return {
            "text": self.text_content,
            "fees_extracted": self._extract_heuristics(r'(?i)(?:fee|tuition)s?\s*:?\s*[\$£€₹]?\s*([\d,]+(?:\.\d{2})?)'),
            "duration_extracted": self._extract_heuristics(r'(?i)duration\s*:?\s*(\d+\s*(?:month|year|week)s?)'),
            "qs_rank": self._extract_heuristics(r'(?i)QS.*Rank(?:ing)?\s*:?\s*#?(\d+)'),
            "nirf_rank": self._extract_heuristics(r'(?i)NIRF.*Rank(?:ing)?\s*:?\s*#?(\d+)'),
            "has_scholarship": bool(re.search(r'(?i)scholarship|financial aid', self.text_content)),
            "has_certificate": bool(re.search(r'(?i)certificate|certification', self.text_content)),
        }
        
    def _extract_heuristics(self, pattern: str) -> str:
        """Finds the first match of a regex pattern in the text."""
        match = re.search(pattern, self.text_content)
        return match.group(1) if match else None
