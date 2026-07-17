import os
from typing import List
from datetime import datetime, timezone
from app.news.providers.base import BaseNewsProvider
from app.schemas.news import NewsArticleCreate

class FinnhubAdapter(BaseNewsProvider):
    @property
    def provider_name(self) -> str:
        return "Finnhub"

    async def fetch_latest_news(self) -> List[NewsArticleCreate]:
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            return []
            
        data = await self._safe_fetch(
            "https://finnhub.io/api/v1/news",
            params={"category": "general", "token": api_key}
        )
        if not data:
            return []
            
        return [self._normalize(item) for item in data]

    async def fetch_company_news(self, ticker: str) -> List[NewsArticleCreate]:
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            return []
            
        import datetime as dt
        today = dt.date.today()
        last_week = today - dt.timedelta(days=7)
        
        data = await self._safe_fetch(
            "https://finnhub.io/api/v1/company-news",
            params={"symbol": ticker, "from": last_week.strftime("%Y-%m-%d"), "to": today.strftime("%Y-%m-%d"), "token": api_key}
        )
        if not data:
            return []
            
        return [self._normalize(item) for item in data]

    def _normalize(self, raw: dict) -> NewsArticleCreate:
        return NewsArticleCreate(
            provider=self.provider_name,
            provider_id=str(raw.get("id", "")),
            headline=raw.get("headline", ""),
            content=raw.get("summary", ""),
            source_url=raw.get("url", ""),
            image_url=raw.get("image", ""),
            published_at=datetime.fromtimestamp(raw.get("datetime", 0), tz=timezone.utc),
            article_type=raw.get("category", "General")
        )
