import os
from typing import List
from datetime import datetime, timezone
from app.news.providers.base import BaseNewsProvider
from app.schemas.news import NewsArticleCreate

class FMPAdapter(BaseNewsProvider):
    @property
    def provider_name(self) -> str:
        return "FMP"

    async def fetch_latest_news(self) -> List[NewsArticleCreate]:
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            return []
            
        data = await self._safe_fetch(
            "https://financialmodelingprep.com/api/v3/fmp/articles",
            params={"page": 0, "size": 20, "apikey": api_key}
        )
        if not data or "content" not in data:
            return []
            
        return [self._normalize(item) for item in data["content"]]

    async def fetch_company_news(self, ticker: str) -> List[NewsArticleCreate]:
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            return []
            
        data = await self._safe_fetch(
            "https://financialmodelingprep.com/api/v3/stock_news",
            params={"tickers": ticker, "limit": 20, "apikey": api_key}
        )
        if not data:
            return []
            
        return [self._normalize(item) for item in data]

    def _normalize(self, raw: dict) -> NewsArticleCreate:
        try:
            pub_date = datetime.strptime(raw.get("publishedDate", ""), "%Y-%m-%d %H:%M:%S")
            pub_date = pub_date.replace(tzinfo=timezone.utc)
        except ValueError:
            pub_date = datetime.now(timezone.utc)

        return NewsArticleCreate(
            provider=self.provider_name,
            provider_id=raw.get("url", ""), # FMP doesn't always have a distinct ID
            headline=raw.get("title", ""),
            content=raw.get("text", ""),
            source_url=raw.get("url", ""),
            image_url=raw.get("image", ""),
            published_at=pub_date,
            article_type="Company" if raw.get("symbol") else "General"
        )
