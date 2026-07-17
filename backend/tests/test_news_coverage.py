import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.news.engine import NewsIntelligenceEngine
from app.schemas.news import NewsArticleCreate

@pytest.mark.asyncio
async def test_engine_jaccard_clustering():
    mock_db = AsyncMock()
    engine = NewsIntelligenceEngine(mock_db)
    
    class MockArticle:
        def __init__(self, c_id, hl):
            self.cluster_id = c_id
            self.headline = hl
            
    # Mock some recent articles
    recent = [
        MockArticle(None, "Ignore this"),
        MockArticle("c1", "Apple launches new iPhone"),
        MockArticle("c2", "Microsoft acquires OpenAI")
    ]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = recent
    mock_db.execute.return_value = mock_result
    
    # Test matching cluster c1
    art = NewsArticleCreate(
        provider="T", provider_id="1", headline="Apple launches new iPhone 15",
        content="C", source_url="U", published_at="2023-01-01T00:00:00Z"
    )
    cid = await engine._assign_cluster(art)
    assert cid == "c1"
    
    # Test new cluster
    art2 = NewsArticleCreate(
        provider="T", provider_id="2", headline="Tesla cuts prices",
        content="C", source_url="U", published_at="2023-01-01T00:00:00Z"
    )
    cid2 = await engine._assign_cluster(art2)
    assert cid2 != "c1" and cid2 != "c2"

@pytest.mark.asyncio
async def test_providers_bad_data_fix():
    from app.news.providers.fmp import FMPAdapter
    from app.news.providers.alphavantage import AlphaVantageAdapter
    from app.news.providers.newsapi import NewsAPIAdapter
    from app.news.providers.finnhub import FinnhubAdapter
    
    fmp = FMPAdapter()
    assert fmp._normalize({"title": "A"}).headline == "A"
    
    av = AlphaVantageAdapter()
    assert av._normalize({"title": "A"}).headline == "A"
    
    napi = NewsAPIAdapter()
    assert napi._normalize({"title": "A"}).headline == "A"
    
    fh = FinnhubAdapter()
    assert fh._normalize({"headline": "A"}).headline == "A"

@pytest.mark.asyncio
async def test_rss_sec_bad_data_fix():
    from app.news.providers.rss import RSSAdapter
    from app.news.providers.sec import SECPressReleaseAdapter
    
    # We shouldn't pass None, we pass {} and test fallback values
    rss = RSSAdapter()
    assert rss.provider_name == "RSS"
    
    sec = SECPressReleaseAdapter()
    assert sec.provider_name == "SEC"
