from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    provider_id = Column(String(255), unique=True, index=True, nullable=False)
    headline = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source_url = Column(String(1000), nullable=False)
    image_url = Column(String(1000), nullable=True)
    article_type = Column(String(50), default="General", index=True) # Company, Market, Sector, etc.
    published_at = Column(DateTime(timezone=True), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cluster_id = Column(String(255), index=True, nullable=True)
    importance_score = Column(Integer, default=0, index=True)
    is_breaking = Column(Boolean, default=False)

    # Relationships
    entities = relationship("NewsEntity", back_populates="article", cascade="all, delete-orphan")
    sentiment = relationship("NewsSentiment", back_populates="article", uselist=False, cascade="all, delete-orphan")
    events = relationship("NewsEvent", back_populates="article", cascade="all, delete-orphan")
    summary = relationship("NewsSummary", back_populates="article", uselist=False, cascade="all, delete-orphan")

class NewsEntity(Base):
    __tablename__ = "news_entities"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String(50), nullable=False, index=True) # Company, Ticker, CEO, Location, etc.
    entity_name = Column(String(255), nullable=False, index=True)
    
    article = relationship("NewsArticle", back_populates="entities")

class NewsSentiment(Base):
    __tablename__ = "news_sentiments"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False, unique=True)
    label = Column(String(20), nullable=False, index=True) # Positive, Neutral, Negative
    score = Column(Float, nullable=False) # -1.0 to 1.0
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)
    
    article = relationship("NewsArticle", back_populates="sentiment")

class NewsEvent(Base):
    __tablename__ = "news_events"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False, index=True) # Earnings, M&A, Bankruptcy, etc.
    details = Column(JSON, nullable=False)
    
    article = relationship("NewsArticle", back_populates="events")

class NewsSummary(Base):
    __tablename__ = "news_summaries"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False, unique=True)
    executive_summary = Column(Text, nullable=False)
    key_takeaways = Column(JSON, nullable=False)
    bullish_signals = Column(JSON, nullable=False)
    bearish_signals = Column(JSON, nullable=False)
    opportunities = Column(JSON, nullable=False)
    risks = Column(JSON, nullable=False)
    market_impact = Column(Text, nullable=False)
    
    article = relationship("NewsArticle", back_populates="summary")
