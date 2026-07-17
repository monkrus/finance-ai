import logging
from typing import List, Optional
from app.market_data.interfaces import ProviderInterface
from app.market_data.adapters.base import BaseAdapter
from app.market_data.models import (
    CompanyProfile, StockQuote, HistoricalPriceSeries,
    IncomeStatement, BalanceSheet, CashFlowStatement,
    CompanySearchResult, FinancialRatios, MarketNews,
    EconomicIndicator, ExchangeRate, EarningsEvent,
    DividendHistory, StockSplit, MarketIndex, SectorIndustryClass
)

logger = logging.getLogger(__name__)

class FinnhubAdapter(BaseAdapter, ProviderInterface):
    """
    Finnhub API Adapter.
    Specializes in real-time quotes, news, and basic financials.
    """
    def __init__(self, api_key: str):
        super().__init__(base_url="https://finnhub.io/api/v1")
        self.api_key = api_key
        
    async def _get_auth(self, endpoint: str, params: dict = None) -> any:
        p = params or {}
        p["token"] = self.api_key
        return await self._get(endpoint, params=p)

    async def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        data = await self._get_auth("/stock/profile2", {"symbol": ticker})
        if not data or "ticker" not in data:
            return None
        return CompanyProfile(
            ticker=data.get("ticker", ticker),
            company_name=data.get("name", ""),
            sector=data.get("finnhubIndustry", ""), # Finnhub mixes sector/industry
            industry=data.get("finnhubIndustry", ""),
            description=None,
            website=data.get("weburl", ""),
            employees=None,
            ceo=None,
            market_cap=data.get("marketCapitalization", 0.0)
        )

    async def get_quote(self, ticker: str) -> Optional[StockQuote]:
        data = await self._get_auth("/quote", {"symbol": ticker})
        if not data or "c" not in data:
            return None
        return StockQuote(
            ticker=ticker,
            price=data.get("c", 0.0),
            change=data.get("d"),
            change_percent=data.get("dp"),
            day_low=data.get("l"),
            day_high=data.get("h"),
            year_low=None,
            year_high=None,
            volume=None,
            timestamp=str(data.get("t", ""))
        )

    async def get_historical_prices(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Optional[HistoricalPriceSeries]:
        # Finnhub uses UNIX timestamps for stock candles. Simplified stub.
        return None

    async def get_income_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[IncomeStatement]:
        return []

    async def get_balance_sheets(self, ticker: str, limit: int = 4, period: str = "annual") -> List[BalanceSheet]:
        return []

    async def get_cash_flow_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[CashFlowStatement]:
        return []

    async def search_company(self, query: str) -> List[CompanySearchResult]:
        data = await self._get_auth("/search", {"q": query})
        if not data or "result" not in data:
            return []
        return [CompanySearchResult(ticker=i.get("symbol"), name=i.get("description"), exchange=i.get("type")) for i in data["result"]]

    async def get_financial_ratios(self, ticker: str) -> List[FinancialRatios]:
        data = await self._get_auth("/stock/metric", {"symbol": ticker, "metric": "all"})
        if not data or "metric" not in data:
            return []
        m = data["metric"]
        return [FinancialRatios(symbol=ticker, date="", pe_ratio=m.get("peExclExtraTTM"), pb_ratio=m.get("pbAnnual"), current_ratio=m.get("currentRatioAnnual"), return_on_equity=m.get("roeTTM"))]

    async def get_market_news(self, ticker: str, limit: int = 10) -> List[MarketNews]:
        data = await self._get_auth("/company-news", {"symbol": ticker, "from": "2023-01-01", "to": "2023-12-31"})
        if not data:
            return []
        return [MarketNews(id=str(i.get("id")), symbol=ticker, title=i.get("headline", ""), published_at=str(i.get("datetime")), source=i.get("source", ""), url=i.get("url", ""), summary=i.get("summary", "")) for i in data[:limit]]

    async def get_economic_indicator(self, indicator: str) -> List[EconomicIndicator]:
        return []

    async def get_exchange_rate(self, base_currency: str, target_currency: str) -> Optional[ExchangeRate]:
        return None

    async def get_earnings_calendar(self, ticker: str) -> List[EarningsEvent]:
        data = await self._get_auth("/calendar/earnings", {"symbol": ticker})
        if not data or "earningsCalendar" not in data:
            return []
        return [EarningsEvent(symbol=ticker, date=i.get("date", ""), eps_estimate=i.get("epsEstimate"), eps_actual=i.get("epsActual"), revenue_estimate=i.get("revenueEstimate"), revenue_actual=i.get("revenueActual")) for i in data["earningsCalendar"]]

    async def get_dividend_history(self, ticker: str) -> List[DividendHistory]:
        return []

    async def get_stock_splits(self, ticker: str) -> List[StockSplit]:
        return []

    async def get_market_indices(self) -> List[MarketIndex]:
        return []

    async def get_sector_industry(self, ticker: str) -> Optional[SectorIndustryClass]:
        profile = await self.get_company_profile(ticker)
        if profile:
            return SectorIndustryClass(symbol=ticker, sector=profile.sector or "Unknown", industry=profile.industry or "Unknown")
        return None
