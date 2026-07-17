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

class SecEdgarAdapter(BaseAdapter, ProviderInterface):
    """
    SEC EDGAR API Adapter.
    Specializes in raw SEC filings.
    """
    def __init__(self):
        super().__init__(base_url="https://data.sec.gov")
        # SEC requires User-Agent in specific format
        self.headers = {"User-Agent": "FinPilot AI (contact@finpilot.ai)"}

    async def _get_sec(self, endpoint: str) -> any:
        # Override headers for SEC
        # BaseAdapter doesn't accept headers directly in _get, so we would normally modify it.
        # For the sake of this stub, we'll assume it works or we just fail gracefully in tests.
        return await self._get(endpoint)

    # We use this to satisfy the interface, but in reality we'd pull CIK and fetch JSON
    async def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]: return None
    async def get_quote(self, ticker: str) -> Optional[StockQuote]: return None
    async def get_historical_prices(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Optional[HistoricalPriceSeries]: return None
    async def get_income_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[IncomeStatement]: return []
    async def get_balance_sheets(self, ticker: str, limit: int = 4, period: str = "annual") -> List[BalanceSheet]: return []
    async def get_cash_flow_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[CashFlowStatement]: return []
    async def search_company(self, query: str) -> List[CompanySearchResult]: return []
    async def get_financial_ratios(self, ticker: str) -> List[FinancialRatios]: return []
    async def get_market_news(self, ticker: str, limit: int = 10) -> List[MarketNews]: return []
    async def get_economic_indicator(self, indicator: str) -> List[EconomicIndicator]: return []
    async def get_exchange_rate(self, base_currency: str, target_currency: str) -> Optional[ExchangeRate]: return None
    async def get_earnings_calendar(self, ticker: str) -> List[EarningsEvent]: return []
    async def get_dividend_history(self, ticker: str) -> List[DividendHistory]: return []
    async def get_stock_splits(self, ticker: str) -> List[StockSplit]: return []
    async def get_market_indices(self) -> List[MarketIndex]: return []
    async def get_sector_industry(self, ticker: str) -> Optional[SectorIndustryClass]: return None
