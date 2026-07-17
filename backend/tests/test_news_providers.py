import pytest
from unittest.mock import AsyncMock, patch
from app.news.providers.finnhub import FinnhubAdapter
from app.news.providers.newsapi import NewsAPIAdapter
from app.news.providers.alphavantage import AlphaVantageAdapter
from app.news.providers.fmp import FMPAdapter
from app.news.providers.rss import RSSAdapter
from app.news.providers.sec import SECPressReleaseAdapter

@pytest.fixture
def mock_httpx():
    with patch("httpx.AsyncClient.get") as mock_get:
        yield mock_get

@pytest.mark.asyncio
async def test_finnhub_adapter():
    adapter = FinnhubAdapter()
    with patch("app.news.providers.finnhub.FinnhubAdapter._safe_fetch", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = []
        res = await adapter.fetch_latest_news()
        assert res == []

        mock_fetch.return_value = [{"id": 1, "headline": "Test", "datetime": 1600000000, "summary": "test", "url": "url", "image": "img", "category": "cat"}]
        with patch("os.getenv", return_value="key"):
            res = await adapter.fetch_latest_news()
            assert len(res) == 1
            
            res2 = await adapter.fetch_company_news("AAPL")
            assert len(res2) == 1

@pytest.mark.asyncio
async def test_fmp_adapter():
    adapter = FMPAdapter()
    with patch("app.news.providers.fmp.FMPAdapter._safe_fetch", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {}
        res = await adapter.fetch_latest_news()
        assert res == []
        
        mock_fetch.return_value = {"content": [{"title": "Test", "publishedDate": "2023-01-01 00:00:00", "text": "test", "url": "url", "image": "img", "site": "site"}]}
        with patch("os.getenv", return_value="key"):
            res = await adapter.fetch_latest_news()
            assert len(res) == 1
            
        mock_fetch.return_value = [{"title": "Test", "publishedDate": "2023-01-01 00:00:00", "text": "test", "url": "url", "image": "img", "site": "site"}]
        with patch("os.getenv", return_value="key"):
            res2 = await adapter.fetch_company_news("AAPL")
            assert len(res2) == 1

@pytest.mark.asyncio
async def test_newsapi_adapter():
    adapter = NewsAPIAdapter()
    with patch("app.news.providers.newsapi.NewsAPIAdapter._safe_fetch", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {"articles": []}
        res = await adapter.fetch_latest_news()
        assert res == []
        
        mock_fetch.return_value = {"articles": [{"title": "Test", "publishedAt": "2023-01-01T00:00:00Z", "description": "test", "url": "url", "urlToImage": "img"}]}
        with patch("os.getenv", return_value="key"):
            res = await adapter.fetch_latest_news()
            assert len(res) == 1
            
            res2 = await adapter.fetch_company_news("AAPL")
            assert len(res2) == 1

@pytest.mark.asyncio
async def test_alphavantage_adapter():
    adapter = AlphaVantageAdapter()
    with patch("app.news.providers.alphavantage.AlphaVantageAdapter._safe_fetch", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {"feed": []}
        res = await adapter.fetch_latest_news()
        assert res == []
        
        mock_fetch.return_value = {"feed": [{"title": "Test", "time_published": "20230101T000000", "summary": "test", "url": "url", "banner_image": "img"}]}
        with patch("os.getenv", return_value="key"):
            res = await adapter.fetch_latest_news()
            assert len(res) == 1
            
            res2 = await adapter.fetch_company_news("AAPL")
            assert len(res2) == 1

@pytest.mark.asyncio
async def test_rss_adapter(mock_httpx):
    adapter = RSSAdapter()
    
    xml = """<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
    <channel>
      <title>Test News</title>
      <item>
        <title>Test Headline</title>
        <link>http://test.com</link>
        <description>Test Desc</description>
      </item>
    </channel>
    </rss>"""
    
    # We must patch the httpx.AsyncClient.get return value properly for async
    mock_resp = AsyncMock()
    mock_resp.text = xml
    # raise_for_status is synchronous usually, but we mock it correctly
    mock_resp.raise_for_status = lambda: None
    mock_httpx.return_value = mock_resp
    
    res = await adapter.fetch_latest_news()
    assert len(res) == 1

@pytest.mark.asyncio
async def test_sec_adapter(mock_httpx):
    adapter = SECPressReleaseAdapter()
    
    xml = """<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
    <channel>
      <title>SEC News</title>
      <item>
        <title>SEC Headline</title>
        <link>http://sec.gov</link>
      </item>
    </channel>
    </rss>"""
    
    mock_resp = AsyncMock()
    mock_resp.text = xml
    mock_resp.raise_for_status = lambda: None
    mock_httpx.return_value = mock_resp
    
    res = await adapter.fetch_latest_news()
    assert len(res) == 1

@pytest.mark.asyncio
async def test_base_provider(mock_httpx):
    from app.news.providers.base import BaseNewsProvider
    class DummyProvider(BaseNewsProvider):
        @property
        def provider_name(self): return "Dummy"
        async def fetch_latest_news(self): return []
        async def fetch_company_news(self, ticker): return []
        def _normalize(self, raw): return None
        
    provider = DummyProvider()
    
    mock_resp = AsyncMock()
    # httpx response json is synchronous
    mock_resp.json = lambda: {"success": True}
    mock_resp.raise_for_status = lambda: None
    mock_httpx.return_value = mock_resp
    
    data = await provider._safe_fetch("http://test.com")
    assert data == {"success": True}
    
    mock_httpx.side_effect = Exception("HTTP Error")
    data2 = await provider._safe_fetch("http://test.com")
    assert data2 is None
