import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.news import NewsArticle, NewsEntity, NewsSentiment, NewsEvent, NewsSummary
from app.news.providers.finnhub import FinnhubAdapter
from app.news.providers.fmp import FMPAdapter
from app.news.providers.alphavantage import AlphaVantageAdapter
from app.news.providers.newsapi import NewsAPIAdapter
from app.news.providers.rss import RSSAdapter
from app.news.providers.sec import SECPressReleaseAdapter
from app.news.sentiment import SentimentEngine
from app.news.extraction import EntityEngine, EventEngine
from app.news.summarization import SummarizationEngine
from app.news.impact import PortfolioImpactEngine
from app.news.scoring import ImportanceScoringEngine
from app.core.redis import get_redis_client
import uuid
from datetime import timedelta
from sqlalchemy import or_
redis_client = get_redis_client()

logger = logging.getLogger(__name__)

class NewsIntelligenceEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.providers = [
            FinnhubAdapter(),
            FMPAdapter(),
            AlphaVantageAdapter(),
            NewsAPIAdapter(),
            RSSAdapter(),
            SECPressReleaseAdapter()
        ]
        self.sentiment_engine = SentimentEngine()
        self.entity_engine = EntityEngine()
        self.event_engine = EventEngine()
        self.summary_engine = SummarizationEngine()
        self.impact_engine = PortfolioImpactEngine(db)
        self.scoring_engine = ImportanceScoringEngine()

    async def ingest_latest_news(self):
        """Fetches latest news from all providers, deduplicates, and stores in DB."""
        for provider in self.providers:
            try:
                articles = await provider.fetch_latest_news()
                for article_data in articles:
                    await self.process_article(article_data)
            except Exception as e:
                logger.error(f"Failed to ingest from {provider.provider_name}: {e}")

    async def process_article(self, article_data):
        """Processes a single article through the entire intelligence pipeline."""
        # 1. Deduplication (Redis caching via URL/provider ID)
        cache_key = f"news:ingest:{article_data.provider}:{article_data.provider_id}"
        if await redis_client.get(cache_key):
            return # Already processed

        # Also check DB to ensure absolute consistency
        result = await self.db.execute(select(NewsArticle).where(NewsArticle.provider_id == article_data.provider_id))
        if result.scalar_one_or_none():
            await redis_client.set(cache_key, "1", ex=86400) # Cache for 1 day
            return

        # Assign Cluster ID
        cluster_id = await self._assign_cluster(article_data)

        # 2. Persist raw article
        new_article = NewsArticle(
            provider=article_data.provider,
            provider_id=article_data.provider_id,
            headline=article_data.headline,
            content=article_data.content,
            source_url=article_data.source_url,
            image_url=article_data.image_url,
            published_at=article_data.published_at,
            article_type=article_data.article_type,
            cluster_id=cluster_id
        )
        self.db.add(new_article)
        await self.db.flush() # Get ID

        # 3. Intelligence Pipeline (Sequential to avoid rate limits, or parallel if robust)
        try:
            # Sentiment
            sentiment = await self.sentiment_engine.analyze(new_article.headline, new_article.content)
            if sentiment:
                self.db.add(NewsSentiment(article_id=new_article.id, **sentiment.model_dump()))

            # Entities
            entities = await self.entity_engine.extract(new_article.headline, new_article.content)
            for ent in entities:
                self.db.add(NewsEntity(article_id=new_article.id, entity_type=ent.entity_type, entity_name=ent.entity_name))

            # Events
            events = await self.event_engine.detect(new_article.headline, new_article.content)
            for ev in events:
                self.db.add(NewsEvent(article_id=new_article.id, event_type=ev.event_type, details=ev.details))

            # Summary
            summary = await self.summary_engine.summarize(new_article.headline, new_article.content)
            if summary:
                self.db.add(NewsSummary(article_id=new_article.id, **summary.model_dump()))
                
            # Score
            event_names = [e.event_type for e in events]
            entity_names = [e.entity_name for e in entities]
            score, is_breaking = self.scoring_engine.calculate_score(new_article.headline, new_article.provider, event_names, entity_names)
            new_article.importance_score = score
            new_article.is_breaking = is_breaking
                
        except Exception as e:
            logger.error(f"AI Pipeline failed for article {new_article.id}: {e}")

        await self.db.commit()
        await redis_client.set(cache_key, "1", ex=86400)

    async def _assign_cluster(self, article_data) -> str:
        """Finds if this article belongs to an existing cluster or creates a new one."""
        # Simple Jaccard similarity on headline words to cluster breaking news across providers
        # Find articles in the last 24h
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        recent_threshold = now - timedelta(hours=24)
        
        result = await self.db.execute(
            select(NewsArticle).where(NewsArticle.published_at >= recent_threshold)
        )
        recent_articles = result.scalars().all()
        
        headline_words = set(article_data.headline.lower().split())
        
        best_cluster = None
        best_sim = 0.0
        
        for ra in recent_articles:
            if not ra.cluster_id:
                continue
            ra_words = set(ra.headline.lower().split())
            intersection = headline_words.intersection(ra_words)
            union = headline_words.union(ra_words)
            sim = len(intersection) / len(union) if union else 0
            
            if sim > 0.4: # Arbitrary threshold for same event
                if sim > best_sim:
                    best_sim = sim
                    best_cluster = ra.cluster_id
                    
        if best_cluster:
            return best_cluster
            
        return str(uuid.uuid4())

    async def get_recent_news(self, limit: int = 10, article_type: str = None) -> list[NewsArticle]:
        """Fetches recent news articles from the database."""
        query = select(NewsArticle).order_by(NewsArticle.published_at.desc())
        
        if article_type:
            query = query.where(NewsArticle.article_type == article_type)
            
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

