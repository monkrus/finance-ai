import logging
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.exceptions import FinPilotException
from app.market_data.interfaces import ProviderInterface
from app.market_data.adapters.fmp_adapter import FMPAdapter
from app.market_data.adapters.mock_adapter import MockAdapter
from app.market_data.adapters.finnhub_adapter import FinnhubAdapter
from app.market_data.adapters.alphavantage_adapter import AlphaVantageAdapter
from app.market_data.adapters.fred_adapter import FredAdapter
from app.market_data.adapters.exchangerate_adapter import ExchangeRateAdapter
from app.market_data.cache import MarketDataCache
from app.market_data.models import (
    CompanyProfile, StockQuote, HistoricalPriceSeries, IncomeStatement,
    BalanceSheet, CashFlowStatement, CompanySearchResult, FinancialRatios,
    MarketNews, EconomicIndicator, ExchangeRate, EarningsEvent,
    DividendHistory, StockSplit, MarketIndex, SectorIndustryClass
)
from app.core.exceptions import FinPilotException

logger = logging.getLogger(__name__)

class MarketDataService:
    """
    Core orchestrator for the Market Data Layer.
    Injects caching, applies retry/circuit-breaking logic via Tenacity,
    and handles graceful degradation to fallback providers.
    """
    def __init__(self):
        self.cache = MarketDataCache()
        
        # Initialize Providers
        self.mock = MockAdapter()
        self.fmp = FMPAdapter(api_key=settings.FMP_API_KEY) if settings.FMP_API_KEY and settings.FMP_API_KEY != "your_fmp_api_key_here" else self.mock
        self.finnhub = FinnhubAdapter(api_key=settings.FINNHUB_API_KEY) if settings.FINNHUB_API_KEY and settings.FINNHUB_API_KEY != "your_finnhub_api_key_here" else self.mock
        self.alpha_vantage = AlphaVantageAdapter(api_key=settings.ALPHA_VANTAGE_API_KEY) if settings.ALPHA_VANTAGE_API_KEY and settings.ALPHA_VANTAGE_API_KEY != "your_alpha_vantage_api_key_here" else self.mock
        self.fred = FredAdapter(api_key=settings.FRED_API_KEY) if settings.FRED_API_KEY and settings.FRED_API_KEY != "your_fred_api_key_here" else self.mock
        self.exchange = ExchangeRateAdapter(api_key=settings.EXCHANGE_RATE_API_KEY) if settings.EXCHANGE_RATE_API_KEY and settings.EXCHANGE_RATE_API_KEY != "your_exchange_rate_api_key_here" else self.mock

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5), reraise=True)
    async def _fetch(self, func_name: str, providers: List[ProviderInterface], *args, **kwargs):
        """Helper to invoke providers in sequence until one succeeds."""
        last_exception = None
        for provider in providers:
            try:
                func = getattr(provider, func_name)
                result = await func(*args, **kwargs)
                if result is not None and (not isinstance(result, list) or len(result) > 0):
                    return result
            except FinPilotException as e:
                logger.warning(f"Provider {provider.__class__.__name__} failed for {func_name}: {e.message}")
                last_exception = e
            except Exception as e:
                logger.warning(f"Provider {provider.__class__.__name__} unexpected error for {func_name}: {str(e)}")
                last_exception = e
        if last_exception:
            raise last_exception
        return None

    async def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        cache_key = f"md:profile:{ticker.upper()}"
        cached = await self.cache.get(cache_key, CompanyProfile)
        if cached: return cached
            
        result = await self._fetch("get_company_profile", [self.fmp, self.finnhub, self.alpha_vantage, self.mock], ticker)
        if result: await self.cache.set(cache_key, result, ttl=86400)
        return result

    async def get_quote(self, ticker: str) -> Optional[StockQuote]:
        cache_key = f"md:quote:{ticker.upper()}"
        cached = await self.cache.get(cache_key, StockQuote)
        if cached: return cached
            
        result = await self._fetch("get_quote", [self.finnhub, self.fmp, self.alpha_vantage, self.mock], ticker)
        if result: await self.cache.set(cache_key, result, ttl=300)
        return result

    async def get_historical_prices(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Optional[HistoricalPriceSeries]:
        key_suffix = f":{from_date}:{to_date}" if from_date or to_date else ":full"
        cache_key = f"md:historical:{ticker.upper()}{key_suffix}"
        
        cached = await self.cache.get(cache_key, HistoricalPriceSeries)
        if cached: return cached
            
        result = await self._fetch("get_historical_prices", [self.alpha_vantage, self.fmp, self.mock], ticker, from_date, to_date)
        if result: await self.cache.set(cache_key, result, ttl=86400)
        return result

    async def get_income_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[IncomeStatement]:
        cache_key = f"md:income:{ticker.upper()}:{period}:{limit}"
        cached = await self.cache.get_list(cache_key, IncomeStatement)
        if cached: return cached
            
        result = await self._fetch("get_income_statements", [self.fmp, self.mock], ticker, limit, period)
        if result: await self.cache.set_list(cache_key, result, ttl=604800)
        return result or []

    async def get_balance_sheets(self, ticker: str, limit: int = 4, period: str = "annual") -> List[BalanceSheet]:
        cache_key = f"md:balance:{ticker.upper()}:{period}:{limit}"
        cached = await self.cache.get_list(cache_key, BalanceSheet)
        if cached: return cached
            
        result = await self._fetch("get_balance_sheets", [self.fmp, self.mock], ticker, limit, period)
        if result: await self.cache.set_list(cache_key, result, ttl=604800)
        return result or []

    async def get_cash_flow_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[CashFlowStatement]:
        cache_key = f"md:cashflow:{ticker.upper()}:{period}:{limit}"
        cached = await self.cache.get_list(cache_key, CashFlowStatement)
        if cached: return cached
            
        result = await self._fetch("get_cash_flow_statements", [self.fmp, self.mock], ticker, limit, period)
        if result: await self.cache.set_list(cache_key, result, ttl=604800)
        return result or []

    async def search_company(self, query: str) -> List[CompanySearchResult]:
        cache_key = f"md:search:{query.upper()}"
        cached = await self.cache.get_list(cache_key, CompanySearchResult)
        if cached: return cached
        
        result = await self._fetch("search_company", [self.finnhub, self.alpha_vantage, self.fmp, self.mock], query)
        if result: await self.cache.set_list(cache_key, result, ttl=86400)
        return result or []

    async def get_financial_ratios(self, ticker: str) -> List[FinancialRatios]:
        cache_key = f"md:ratios:{ticker.upper()}"
        cached = await self.cache.get_list(cache_key, FinancialRatios)
        if cached: return cached
        
        result = await self._fetch("get_financial_ratios", [self.fmp, self.finnhub, self.mock], ticker)
        if result: await self.cache.set_list(cache_key, result, ttl=86400)
        return result or []

    async def get_market_news(self, ticker: str, limit: int = 10) -> List[MarketNews]:
        cache_key = f"md:news:{ticker.upper()}:{limit}"
        cached = await self.cache.get_list(cache_key, MarketNews)
        if cached: return cached
        
        result = await self._fetch("get_market_news", [self.finnhub, self.alpha_vantage, self.fmp, self.mock], ticker, limit)
        if result: await self.cache.set_list(cache_key, result, ttl=900) # 15 minutes
        return result or []

    async def get_economic_indicator(self, indicator: str) -> List[EconomicIndicator]:
        cache_key = f"md:econ:{indicator.upper()}"
        cached = await self.cache.get_list(cache_key, EconomicIndicator)
        if cached: return cached
        
        result = await self._fetch("get_economic_indicator", [self.fred, self.mock], indicator)
        if result: await self.cache.set_list(cache_key, result, ttl=86400)
        return result or []

    async def get_exchange_rate(self, base_currency: str, target_currency: str) -> Optional[ExchangeRate]:
        cache_key = f"md:fx:{base_currency}:{target_currency}"
        cached = await self.cache.get(cache_key, ExchangeRate)
        if cached: return cached
        
        result = await self._fetch("get_exchange_rate", [self.exchange, self.fmp, self.mock], base_currency, target_currency)
        if result: await self.cache.set(cache_key, result, ttl=3600) # 1 hour
        return result

    async def get_earnings_calendar(self, ticker: str) -> List[EarningsEvent]:
        cache_key = f"md:earnings:{ticker.upper()}"
        cached = await self.cache.get_list(cache_key, EarningsEvent)
        if cached: return cached
        
        result = await self._fetch("get_earnings_calendar", [self.finnhub, self.fmp, self.mock], ticker)
        if result: await self.cache.set_list(cache_key, result, ttl=86400)
        return result or []

    async def get_dividend_history(self, ticker: str) -> List[DividendHistory]:
        cache_key = f"md:dividends:{ticker.upper()}"
        cached = await self.cache.get_list(cache_key, DividendHistory)
        if cached: return cached
        
        result = await self._fetch("get_dividend_history", [self.fmp, self.mock], ticker)
        if result: await self.cache.set_list(cache_key, result, ttl=86400)
        return result or []

    async def get_stock_splits(self, ticker: str) -> List[StockSplit]:
        cache_key = f"md:splits:{ticker.upper()}"
        cached = await self.cache.get_list(cache_key, StockSplit)
        if cached: return cached
        
        result = await self._fetch("get_stock_splits", [self.fmp, self.mock], ticker)
        if result: await self.cache.set_list(cache_key, result, ttl=86400)
        return result or []

    async def get_market_indices(self) -> List[MarketIndex]:
        cache_key = f"md:indices:major"
        cached = await self.cache.get_list(cache_key, MarketIndex)
        if cached: return cached
        
        result = await self._fetch("get_market_indices", [self.fmp, self.mock])
        if result: await self.cache.set_list(cache_key, result, ttl=900)
        return result or []

    async def get_sector_industry(self, ticker: str) -> Optional[SectorIndustryClass]:
        cache_key = f"md:sector:{ticker.upper()}"
        cached = await self.cache.get(cache_key, SectorIndustryClass)
        if cached: return cached
        
        result = await self._fetch("get_sector_industry", [self.fmp, self.finnhub, self.mock], ticker)
        if result: await self.cache.set(cache_key, result, ttl=86400*7) # 1 week
        return result
