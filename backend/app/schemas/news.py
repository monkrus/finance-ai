from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional, Dict, Any

class NewsSummarySchema(BaseModel):
    executive_summary: str
    key_takeaways: List[str]
    bullish_signals: List[str]
    bearish_signals: List[str]
    opportunities: List[str]
    risks: List[str]
    market_impact: str

class NewsSentimentSchema(BaseModel):
    label: str # Positive, Neutral, Negative
    score: float # -1.0 to 1.0
    confidence: float # 0.0 to 1.0
    reasoning: str

class NewsEventSchema(BaseModel):
    event_type: str # Earnings, Dividend, M&A, etc.
    details: Dict[str, Any]

class NewsEntitySchema(BaseModel):
    entity_type: str # Company, Ticker, CEO, etc.
    entity_name: str

class NewsArticleBase(BaseModel):
    provider: str
    provider_id: str
    headline: str
    content: str
    source_url: str
    published_at: datetime
    article_type: str = "General" # Company News, Market News, etc.
    image_url: Optional[str] = None
    cluster_id: Optional[str] = None
    importance_score: int = 0
    is_breaking: bool = False

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticleResponse(NewsArticleBase):
    id: int
    created_at: datetime
    entities: List[NewsEntitySchema] = []
    sentiment: Optional[NewsSentimentSchema] = None
    events: List[NewsEventSchema] = []
    summary: Optional[NewsSummarySchema] = None

    class Config:
        from_attributes = True

class PortfolioImpactSchema(BaseModel):
    portfolio_id: int
    affected_holdings: List[str]
    impact_score: float # -1.0 to 1.0
    impact_reasoning: str
    alert_priority: str = "LOW" # LOW, MEDIUM, HIGH, CRITICAL
