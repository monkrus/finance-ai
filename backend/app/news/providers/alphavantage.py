import os
from typing import List
from datetime import datetime, timezone
from app.news.providers.base import BaseNewsProvider
from app.schemas.news import NewsArticleCreate

class AlphaVantageAdapter(BaseNewsProvider):
    @property
    def provider_name(self) -> str:
        return "AlphaVantage"

    async def fetch_latest_news(self) -> List[NewsArticleCreate]:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not api_key:
            return []
            
        data = await self._safe_fetch(
            "https://www.alphavantage.co/query",
            params={"function": "NEWS_SENTIMENT", "limit": 20, "apikey": api_key}
        )
        if not data or "feed" not in data:
            return []
            
        return [self._normalize(item) for item in data["feed"]]

    async def fetch_company_news(self, ticker: str) -> List[NewsArticleCreate]:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not api_key:
            return []
            
        data = await self._safe_fetch(
            "https://www.alphavantage.co/query",
            params={"function": "NEWS_SENTIMENT", "tickers": ticker, "limit": 20, "apikey": api_key}
        )
        if not data or "feed" not in data:
            return []
            
        return [self._normalize(item) for item in data["feed"]]

    def _normalize(self, raw: dict) -> NewsArticleCreate:
        try:
            pub_date = datetime.strptime(raw.get("time_published", ""), "%Y%m%dT%H%M%S")
            pub_date = pub_date.replace(tzinfo=timezone.utc)
        except ValueError:
            pub_date = datetime.now(timezone.utc)

        return NewsArticleCreate(
            provider=self.provider_name,
            provider_id=raw.get("url", ""),
            headline=raw.get("title", ""),
            content=raw.get("summary", ""),
            source_url=raw.get("url", ""),
            image_url=raw.get("banner_image", ""),
            published_at=pub_date,
            article_type="General"
        )
