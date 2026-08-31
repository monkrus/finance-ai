"""Shared fixtures.

Environment is configured before any app import so `app.core.config` does not
sys.exit on a missing SECRET_KEY, and so MemoryManager picks the fakeredis path.
"""

import os
import secrets

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", secrets.token_hex(32))
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_finpilot.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from typing import Any, List, Optional  # noqa: E402

import pytest  # noqa: E402

from app.schemas.investment_strategy import (  # noqa: E402
    ContextBlock,
    InvestmentProfile,
    StrategyContext,
)


# --------------------------------------------------------------------------- #
# Fakes
# --------------------------------------------------------------------------- #
class FakeModel:
    """Stands in for a pydantic domain model with `.model_dump()`."""

    def __init__(self, **data):
        self._data = data
        for k, v in data.items():
            setattr(self, k, v)

    def model_dump(self):
        return dict(self._data)


class FakeScalars:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value


class FakeResult:
    def __init__(self, value):
        self._value = value

    def scalars(self):
        return FakeScalars(self._value)


class FakeSession:
    """Minimal AsyncSession stand-in: returns whatever it was seeded with."""

    def __init__(self, value: Any = None):
        self.value = value
        self.executed = 0

    async def execute(self, *_args, **_kwargs):
        self.executed += 1
        return FakeResult(self.value)


class FakePortfolioEngine:
    def __init__(self, analytics=None, holdings=None, fail_analytics=False, fail_holdings=False):
        self._analytics = analytics
        self._holdings = holdings or []
        self._fail_analytics = fail_analytics
        self._fail_holdings = fail_holdings

    async def get_portfolio_analytics(self, db, portfolio_id):
        if self._fail_analytics:
            raise RuntimeError("market data provider unavailable")
        return self._analytics

    async def get_hydrated_holdings(self, db, portfolio_id):
        if self._fail_holdings:
            raise RuntimeError("db unavailable")
        return self._holdings


class FakeMarketDataService:
    def __init__(self, profiles=None, ratios=None, news=None):
        self._profiles = profiles or {}
        self._ratios = ratios or {}
        self._news = news or {}

    async def get_company_profile(self, ticker: str):
        return self._profiles.get(ticker)

    async def get_financial_ratios(self, ticker: str) -> List[Any]:
        return self._ratios.get(ticker, [])

    async def get_market_news(self, ticker: str, limit: int = 10) -> List[Any]:
        return self._news.get(ticker, [])


class FakeRagEngine:
    def __init__(self, responses=None):
        self._responses = responses or {}
        self.calls = []

    async def query(self, query: str, top_k: int = 5, metadata_filters: Optional[dict] = None):
        self.calls.append((query, metadata_filters))
        ticker = (metadata_filters or {}).get("ticker")
        return self._responses.get(ticker)


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def profile() -> InvestmentProfile:
    return InvestmentProfile(
        risk_tolerance="moderate",
        time_horizon_years=20,
        experience_level="beginner",
        goals=["retire at 60"],
    )


@pytest.fixture
def analytics() -> FakeModel:
    return FakeModel(
        performance={"portfolio_value": 125_000.0, "total_return_pct": 12.4},
        allocation={"sector_allocation": {"Technology": 0.71, "Energy": 0.29},
                    "diversification_score": 0.31},
        risk={"portfolio_beta": 1.29, "portfolio_volatility": 0.22},
    )


@pytest.fixture
def holdings() -> List[FakeModel]:
    return [
        FakeModel(ticker_symbol="AAPL", market_value=70_000.0, weight=0.56, sector="Technology"),
        FakeModel(ticker_symbol="XOM", market_value=36_000.0, weight=0.29, sector="Energy"),
        FakeModel(ticker_symbol="MSFT", market_value=19_000.0, weight=0.15, sector="Technology"),
    ]


@pytest.fixture
def owned_portfolio() -> FakeModel:
    return FakeModel(id=1, user_id=42, name="Long-term")


@pytest.fixture
def context() -> StrategyContext:
    return StrategyContext(
        blocks=[
            ContextBlock(ref="PROFILE-1", kind="profile", label="profile", content={"a": 1}),
            ContextBlock(ref="PORTFOLIO-1", kind="portfolio", label="analytics", content={"b": 2}),
            ContextBlock(ref="NEWS-1", kind="news", label="news", content=[{"headline": "x"}]),
        ],
        gaps=[],
    )
