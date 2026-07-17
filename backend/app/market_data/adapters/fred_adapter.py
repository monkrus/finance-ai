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

class FredAdapter(BaseAdapter, ProviderInterface):
    """
    FRED API Adapter (Federal Reserve Economic Data).
    Specializes in macro-economic indicators.
    """
    def __init__(self, api_key: str):
        super().__init__(base_url="https://api.stlouisfed.org/fred")
        self.api_key = api_key
        
    async def _get_auth(self, endpoint: str, params: dict = None) -> any:
        p = params or {}
        p["api_key"] = self.api_key
        p["file_type"] = "json"
        return await self._get(endpoint, params=p)

    # Return None / [] for stock-specific methods
    async def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]: return None
    async def get_quote(self, ticker: str) -> Optional[StockQuote]: return None
    async def get_historical_prices(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Optional[HistoricalPriceSeries]: return None
    async def get_income_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[IncomeStatement]: return []
    async def get_balance_sheets(self, ticker: str, limit: int = 4, period: str = "annual") -> List[BalanceSheet]: return []
    async def get_cash_flow_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[CashFlowStatement]: return []
    async def search_company(self, query: str) -> List[CompanySearchResult]: return []
    async def get_financial_ratios(self, ticker: str) -> List[FinancialRatios]: return []
    async def get_market_news(self, ticker: str, limit: int = 10) -> List[MarketNews]: return []
    async def get_exchange_rate(self, base_currency: str, target_currency: str) -> Optional[ExchangeRate]: return None
    async def get_earnings_calendar(self, ticker: str) -> List[EarningsEvent]: return []
    async def get_dividend_history(self, ticker: str) -> List[DividendHistory]: return []
    async def get_stock_splits(self, ticker: str) -> List[StockSplit]: return []
    async def get_market_indices(self) -> List[MarketIndex]: return []
    async def get_sector_industry(self, ticker: str) -> Optional[SectorIndustryClass]: return None

    async def get_economic_indicator(self, indicator: str) -> List[EconomicIndicator]:
        # indicator should be a FRED series ID like 'GDP', 'CPIAUCSL'
        data = await self._get_auth("/series/observations", {"series_id": indicator, "limit": 10, "sort_order": "desc"})
        if not data or "observations" not in data:
            return []
            
        results = []
        for obs in data["observations"]:
            try:
                val = float(obs.get("value", 0))
                results.append(EconomicIndicator(
                    indicator_id=indicator,
                    name=indicator,
                    date=obs.get("date", ""),
                    value=val
                ))
            except ValueError:
                continue # FRED sometimes returns '.' for null
        return results
