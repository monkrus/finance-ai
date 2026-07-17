import logging
from typing import List, Optional
from app.market_data.interfaces import ProviderInterface
from app.market_data.adapters.base import BaseAdapter
from app.market_data.models import (
    CompanyProfile, StockQuote, HistoricalPriceSeries, HistoricalPrice,
    IncomeStatement, BalanceSheet, CashFlowStatement,
    CompanySearchResult, FinancialRatios, MarketNews,
    EconomicIndicator, ExchangeRate, EarningsEvent,
    DividendHistory, StockSplit, MarketIndex, SectorIndustryClass
)

logger = logging.getLogger(__name__)

class AlphaVantageAdapter(BaseAdapter, ProviderInterface):
    """
    Alpha Vantage API Adapter.
    Specializes in historical data and time series.
    """
    def __init__(self, api_key: str):
        super().__init__(base_url="https://www.alphavantage.co/query")
        self.api_key = api_key
        
    async def _get_auth(self, function: str, params: dict = None) -> any:
        p = params or {}
        p["function"] = function
        p["apikey"] = self.api_key
        return await self._get("", params=p)

    async def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        data = await self._get_auth("OVERVIEW", {"symbol": ticker})
        if not data or "Symbol" not in data:
            return None
        return CompanyProfile(
            ticker=data.get("Symbol", ticker),
            company_name=data.get("Name", ""),
            sector=data.get("Sector", ""),
            industry=data.get("Industry", ""),
            description=data.get("Description", ""),
            website=None,
            employees=None,
            ceo=None,
            market_cap=float(data.get("MarketCapitalization", 0.0)) if data.get("MarketCapitalization", "0").isdigit() else 0.0
        )

    async def get_quote(self, ticker: str) -> Optional[StockQuote]:
        data = await self._get_auth("GLOBAL_QUOTE", {"symbol": ticker})
        if not data or "Global Quote" not in data:
            return None
        q = data["Global Quote"]
        return StockQuote(
            ticker=q.get("01. symbol", ticker),
            price=float(q.get("05. price", 0.0)),
            change=float(q.get("09. change", 0.0)),
            change_percent=float(q.get("10. change percent", "0").replace("%", "")),
            day_low=float(q.get("04. low", 0.0)),
            day_high=float(q.get("03. high", 0.0)),
            year_low=None,
            year_high=None,
            volume=float(q.get("06. volume", 0.0)),
            timestamp=q.get("07. latest trading day", "")
        )

    async def get_historical_prices(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Optional[HistoricalPriceSeries]:
        data = await self._get_auth("TIME_SERIES_DAILY_ADJUSTED", {"symbol": ticker})
        if not data or "Time Series (Daily)" not in data:
            return None
        
        series = data["Time Series (Daily)"]
        prices = []
        for date, v in list(series.items())[:100]: # limit to 100 for stub
            prices.append(HistoricalPrice(
                date=date,
                open=float(v.get("1. open", 0)),
                high=float(v.get("2. high", 0)),
                low=float(v.get("3. low", 0)),
                close=float(v.get("5. adjusted close", v.get("4. close", 0))),
                volume=float(v.get("6. volume", 0))
            ))
        return HistoricalPriceSeries(ticker=ticker, prices=prices)

    async def get_income_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[IncomeStatement]:
        return []

    async def get_balance_sheets(self, ticker: str, limit: int = 4, period: str = "annual") -> List[BalanceSheet]:
        return []

    async def get_cash_flow_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[CashFlowStatement]:
        return []

    async def search_company(self, query: str) -> List[CompanySearchResult]:
        data = await self._get_auth("SYMBOL_SEARCH", {"keywords": query})
        if not data or "bestMatches" not in data:
            return []
        return [CompanySearchResult(ticker=i.get("1. symbol"), name=i.get("2. name"), exchange=i.get("4. region")) for i in data["bestMatches"]]

    async def get_financial_ratios(self, ticker: str) -> List[FinancialRatios]:
        return []

    async def get_market_news(self, ticker: str, limit: int = 10) -> List[MarketNews]:
        data = await self._get_auth("NEWS_SENTIMENT", {"tickers": ticker, "limit": limit})
        if not data or "feed" not in data:
            return []
        return [MarketNews(id=i.get("url", ""), symbol=ticker, title=i.get("title", ""), published_at=i.get("time_published", ""), source=i.get("source", ""), url=i.get("url", ""), summary=i.get("summary", "")) for i in data["feed"]]

    async def get_economic_indicator(self, indicator: str) -> List[EconomicIndicator]:
        return []

    async def get_exchange_rate(self, base_currency: str, target_currency: str) -> Optional[ExchangeRate]:
        return None

    async def get_earnings_calendar(self, ticker: str) -> List[EarningsEvent]:
        return []

    async def get_dividend_history(self, ticker: str) -> List[DividendHistory]:
        return []

    async def get_stock_splits(self, ticker: str) -> List[StockSplit]:
        return []

    async def get_market_indices(self) -> List[MarketIndex]:
        return []

    async def get_sector_industry(self, ticker: str) -> Optional[SectorIndustryClass]:
        return None
