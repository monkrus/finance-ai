import re
from typing import List

class ImportanceScoringEngine:
    def __init__(self):
        # Base event scores
        self.event_scores = {
            "Earnings": 40,
            "M&A": 40,
            "Bankruptcy": 40,
            "Regulatory": 35,
            "Macro": 30,
            "Dividend": 20,
            "Product Launch": 20,
            "Executive Change": 20,
            "General": 0
        }
        
        # Source reliability scores
        self.source_scores = {
            "SEC": 15,
            "FMP": 15,
            "Finnhub": 10,
            "AlphaVantage": 10,
            "NewsAPI": 5,
            "RSS": 5
        }
        
        # Breaking news keywords
        self.breaking_keywords = ["urgent", "breaking", "alert", "exclusive"]

    def calculate_score(self, headline: str, provider: str, events: List[str], entities: List[str]) -> tuple[int, bool]:
        score = 0
        
        # 1. Source Reliability (0-15)
        score += self.source_scores.get(provider, 5)
        
        # 2. Event Type (0-40)
        max_event_score = 0
        for ev in events:
            ev_score = self.event_scores.get(ev, 10)
            if ev_score > max_event_score:
                max_event_score = ev_score
        score += max_event_score
        
        # 3. Breaking News (0-30)
        is_breaking = False
        headline_lower = headline.lower()
        if any(kw in headline_lower for kw in self.breaking_keywords):
            score += 30
            is_breaking = True
            
        # 4. Entity / Market Cap Heuristic (0-15)
        # In a real system, we'd lookup market cap. For now, we simulate mega-caps.
        mega_caps = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
        if any(ent in mega_caps for ent in entities):
            score += 15
        elif len(entities) > 0:
            score += 5 # Some entities detected

        # Cap at 100
        score = min(score, 100)
        
        return score, is_breaking
