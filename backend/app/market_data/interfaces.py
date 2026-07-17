from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from app.market_data.models import (
    CompanyProfile,
    StockQuote,
    HistoricalPriceSeries,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    CompanySearchResult,
    FinancialRatios,
    MarketNews,
    EconomicIndicator,
    ExchangeRate,
    EarningsEvent,
    DividendHistory,
    StockSplit,
    MarketIndex,
    SectorIndustryClass
)

class ProviderInterface(ABC):
    @abstractmethod
    async def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        """Fetch the company profile (overview) for a specific ticker."""
        pass

    @abstractmethod
    async def get_quote(self, ticker: str) -> Optional[StockQuote]:
        """Fetch real-time or latest available quote for a specific ticker."""
        pass

    @abstractmethod
    async def get_historical_prices(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Optional[HistoricalPriceSeries]:
        """Fetch historical end-of-day prices."""
        pass

    @abstractmethod
    async def get_income_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[IncomeStatement]:
        """Fetch income statements."""
        pass

    @abstractmethod
    async def get_balance_sheets(self, ticker: str, limit: int = 4, period: str = "annual") -> List[BalanceSheet]:
        """Fetch balance sheets."""
        pass

    @abstractmethod
    async def get_cash_flow_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[CashFlowStatement]:
        """Fetch cash flow statements."""
        pass

    async def search_company(self, query: str) -> List[CompanySearchResult]:
        """Search for a company by name or ticker."""
        return []

    async def get_financial_ratios(self, ticker: str) -> List[FinancialRatios]:
        """Fetch financial ratios."""
        return []

    async def get_market_news(self, ticker: str, limit: int = 10) -> List[MarketNews]:
        """Fetch market news for a ticker."""
        return []

    async def get_economic_indicator(self, indicator: str) -> List[EconomicIndicator]:
        """Fetch an economic indicator (e.g., GDP, INFLATION)."""
        return []

    async def get_exchange_rate(self, base_currency: str, target_currency: str) -> Optional[ExchangeRate]:
        """Fetch the current exchange rate."""
        return None

    async def get_earnings_calendar(self, ticker: str) -> List[EarningsEvent]:
        """Fetch historical and upcoming earnings for a ticker."""
        return []

    async def get_dividend_history(self, ticker: str) -> List[DividendHistory]:
        """Fetch dividend history for a ticker."""
        return []

    async def get_stock_splits(self, ticker: str) -> List[StockSplit]:
        """Fetch stock splits for a ticker."""
        return []

    async def get_market_indices(self) -> List[MarketIndex]:
        """Fetch major market indices."""
        return []

    async def get_sector_industry(self, ticker: str) -> Optional[SectorIndustryClass]:
        """Fetch sector and industry classification."""
        return None
