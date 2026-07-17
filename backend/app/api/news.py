from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.news import NewsArticle, NewsEntity, NewsSentiment, NewsEvent, NewsSummary
from app.schemas.news import NewsArticleResponse
from app.news.engine import NewsIntelligenceEngine

router = APIRouter()

@router.post("/ingest", summary="Manually trigger news ingestion")
async def ingest_news(db: AsyncSession = Depends(get_db)):
    engine = NewsIntelligenceEngine(db)
    await engine.ingest_latest_news()
    return {"status": "Success", "message": "News ingested"}

@router.get("/latest", response_model=List[NewsArticleResponse])
async def get_latest_news(
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(NewsArticle)
        .order_by(NewsArticle.published_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/company/{ticker}", response_model=List[NewsArticleResponse])
async def get_company_news(
    ticker: str,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch articles where an entity matches this ticker
    result = await db.execute(
        select(NewsArticle)
        .join(NewsArticle.entities)
        .where(NewsEntity.entity_type == "Ticker", NewsEntity.entity_name == ticker.upper())
        .order_by(NewsArticle.published_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/portfolio/{portfolio_id}")
async def get_portfolio_news_impact(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # This calls the impact engine
    from app.news.impact import PortfolioImpactEngine
    engine = PortfolioImpactEngine(db)
    # Return impact for latest news
    result = await db.execute(select(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(10))
    articles = result.scalars().all()
    
    impacts = []
    for article in articles:
        # Load relationships explicitly or lazily
        entities_res = await db.execute(select(NewsEntity).where(NewsEntity.article_id == article.id))
        events_res = await db.execute(select(NewsEvent).where(NewsEvent.article_id == article.id))
        sentiment_res = await db.execute(select(NewsSentiment).where(NewsSentiment.article_id == article.id))
        
        entities = entities_res.scalars().all()
        events = events_res.scalars().all()
        sentiment = sentiment_res.scalar_one_or_none()
        sentiment_score = sentiment.score if sentiment else 0.0
        
        # Need to map back to schemas for the engine
        # For simplicity, we just pass the models as they duck-type similarly enough or we map them
        from app.schemas.news import NewsEntitySchema, NewsEventSchema
        entity_schemas = [NewsEntitySchema(entity_type=e.entity_type, entity_name=e.entity_name) for e in entities]
        event_schemas = [NewsEventSchema(event_type=e.event_type, details=e.details) for e in events]
        
        article_impacts = await engine.determine_impact(current_user.id, entity_schemas, event_schemas, sentiment_score)
        impacts.extend(article_impacts)
        
    return {"portfolio_id": portfolio_id, "recent_impacts": impacts}

@router.get("/search", response_model=List[NewsArticleResponse])
async def search_news(
    q: str = Query(..., description="Keyword search"),
    sentiment: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(NewsArticle).where(NewsArticle.headline.ilike(f"%{q}%"))
    if sentiment:
        query = query.join(NewsArticle.sentiment).where(NewsSentiment.label == sentiment.capitalize())
        
    query = query.order_by(NewsArticle.published_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
