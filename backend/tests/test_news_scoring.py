import pytest
from app.news.scoring import ImportanceScoringEngine

def test_importance_scoring_engine():
    engine = ImportanceScoringEngine()
    
    # Test basic
    score, is_breaking = engine.calculate_score("Apple announces new product", "NewsAPI", ["Product Launch"], ["AAPL"])
    # Base 5 (NewsAPI) + 20 (Product Launch) + 0 (breaking) + 15 (mega-cap AAPL) = 40
    assert score == 40
    assert not is_breaking
    
    # Test breaking
    score, is_breaking = engine.calculate_score("URGENT: Apple merges with Tesla", "SEC", ["M&A"], ["AAPL", "TSLA"])
    # Base 15 (SEC) + 40 (M&A) + 30 (breaking) + 15 (mega-cap) = 100
    assert score == 100
    assert is_breaking
    
    # Test cap at 100
    score, is_breaking = engine.calculate_score("URGENT: BREAKING NEWS EARNINGS FOR MEGA CAP", "SEC", ["Earnings"], ["AAPL"])
    assert score == 100 # 15 + 40 + 30 + 15 = 100
    
    # Test general news no entity
    score, is_breaking = engine.calculate_score("General market goes up", "Unknown", [], [])
    # 5 + 0 + 0 + 0 = 5
    assert score == 5
