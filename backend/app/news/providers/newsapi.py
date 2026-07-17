import os
from typing import List
from datetime import datetime, timezone
from app.news.providers.base import BaseNewsProvider
from app.schemas.news import NewsArticleCreate

class NewsAPIAdapter(BaseNewsProvider):
    @property
    def provider_name(self) -> str:
        return "NewsAPI"

    async def fetch_latest_news(self) -> List[NewsArticleCreate]:
        api_key = os.getenv("NEWSAPI_API_KEY")
        if not api_key:
            return []
            
        data = await self._safe_fetch(
            "https://newsapi.org/v2/top-headlines",
            params={"category": "business", "language": "en", "pageSize": 20, "apiKey": api_key}
        )
        if not data or "articles" not in data:
            return []
            
        return [self._normalize(item) for item in data["articles"]]

    async def fetch_company_news(self, ticker: str) -> List[NewsArticleCreate]:
        api_key = os.getenv("NEWSAPI_API_KEY")
        if not api_key:
            return []
            
        data = await self._safe_fetch(
            "https://newsapi.org/v2/everything",
            params={"q": ticker, "language": "en", "sortBy": "publishedAt", "pageSize": 20, "apiKey": api_key}
        )
        if not data or "articles" not in data:
            return []
            
        return [self._normalize(item) for item in data["articles"]]

    def _normalize(self, raw: dict) -> NewsArticleCreate:
        try:
            # Format: 2023-11-20T14:30:00Z
            pub_date = datetime.strptime(raw.get("publishedAt", ""), "%Y-%m-%dT%H:%M:%SZ")
            pub_date = pub_date.replace(tzinfo=timezone.utc)
        except ValueError:
            pub_date = datetime.now(timezone.utc)

        return NewsArticleCreate(
            provider=self.provider_name,
            provider_id=raw.get("url", ""), 
            headline=raw.get("title", ""),
            content=raw.get("content", "") or raw.get("description", ""),
            source_url=raw.get("url", ""),
            image_url=raw.get("urlToImage", ""),
            published_at=pub_date,
            article_type="General"
        )
