import os
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.news import NewsArticleCreate

class BaseNewsProvider(ABC):
    """
    Abstract base class for all News Providers.
    Ensures every provider normalizes its proprietary data payload into FinPilot's NewsArticleCreate schema.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def fetch_latest_news(self) -> List[NewsArticleCreate]:
        """Fetch general/latest market news."""
        pass

    @abstractmethod
    async def fetch_company_news(self, ticker: str) -> List[NewsArticleCreate]:
        """Fetch news specific to a company."""
        pass

    async def _safe_fetch(self, url: str, params: Dict[str, Any] = None, headers: Dict[str, Any] = None) -> Any:
        """Helper to fetch from external APIs with graceful degradation."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            # Graceful degradation on API failure
            return None
