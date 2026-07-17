import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.news.engine import NewsIntelligenceEngine
from app.schemas.news import NewsArticleCreate

@pytest.fixture
def mock_db():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    return db

@pytest.fixture
def mock_redis():
    with patch("app.news.engine.redis_client") as mock:
        mock.get.return_value = None
        yield mock

@pytest.mark.asyncio
async def test_news_engine_ingest_latest_news(mock_db, mock_redis):
    engine = NewsIntelligenceEngine(mock_db)
    
    # Mock providers
    for provider in engine.providers:
        provider.fetch_latest_news = AsyncMock(return_value=[
            NewsArticleCreate(
                provider="Test",
                provider_id="123",
                headline="Test",
                content="Content",
                source_url="http://test.com",
                published_at="2023-01-01T00:00:00Z"
            )
        ])
    
    with patch("app.news.engine.NewsIntelligenceEngine.process_article", new_callable=AsyncMock) as mock_process:
        await engine.ingest_latest_news()
        assert mock_process.called

@pytest.mark.asyncio
async def test_news_engine_process_article(mock_db, mock_redis):
    with patch("app.news.sentiment.SentimentEngine.analyze", new_callable=AsyncMock) as mock_sentiment, \
         patch("app.news.extraction.EntityEngine.extract", new_callable=AsyncMock) as mock_entity, \
         patch("app.news.extraction.EventEngine.detect", new_callable=AsyncMock) as mock_event, \
         patch("app.news.summarization.SummarizationEngine.summarize", new_callable=AsyncMock) as mock_summary:
         
        mock_sentiment.return_value = MagicMock(model_dump=lambda: {"label": "Positive", "score": 1.0})
        mock_entity.return_value = [MagicMock(entity_type="Company", entity_name="Apple")]
        mock_event.return_value = [MagicMock(event_type="Earnings", details={})]
        mock_summary.return_value = MagicMock(model_dump=lambda: {"executive_summary": "sum"})

        engine = NewsIntelligenceEngine(mock_db)
        article = NewsArticleCreate(
            provider="Test",
            provider_id="123",
            headline="Test",
            content="Content",
            source_url="http://test.com",
            published_at="2023-01-01T00:00:00Z"
        )
        await engine.process_article(article)
        assert mock_db.commit.called

@pytest.mark.asyncio
async def test_news_engine_process_article_exceptions(mock_db, mock_redis):
    with patch("app.news.sentiment.SentimentEngine.analyze", new_callable=AsyncMock) as mock_sentiment:
        mock_sentiment.side_effect = Exception("Test Error")
        
        engine = NewsIntelligenceEngine(mock_db)
        article = NewsArticleCreate(
            provider="Test",
            provider_id="123",
            headline="Test",
            content="Content",
            source_url="http://test.com",
            published_at="2023-01-01T00:00:00Z"
        )
        await engine.process_article(article)
        assert mock_db.commit.called # It should catch the exception and continue to commit
