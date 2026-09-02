"""Context assembly for the Investment Strategy agent.

This module is deliberately LLM-free. It calls the *existing* domain services —
`PortfolioEngine`, `MarketDataService`, `RAGEngine` — and turns their output into
addressable `ContextBlock`s. No business logic (valuation, allocation, risk
maths, news impact) is reimplemented here; the agent's job is to reason over
what those services already compute.

Every source is fetched defensively: a failing provider becomes a recorded gap,
not a 500, and not a silent omission the model can paper over.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.exceptions import FinPilotException
from app.models.portfolio import Portfolio as PortfolioModel
from app.schemas.investment_strategy import (
    ContextBlock,
    InvestmentProfile,
    StrategyContext,
)

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class InvestmentContextBuilder:
    """Assembles the evidence pack the strategy agent reasons over."""

    def __init__(self, portfolio_engine, market_data_service, rag_engine=None):
        self.portfolio_engine = portfolio_engine
        self.md = market_data_service
        self.rag_engine = rag_engine

    # ------------------------------------------------------------------ #
    # Ownership
    # ------------------------------------------------------------------ #
    async def assert_portfolio_owned_by(
        self, db: AsyncSession, portfolio_id: int, user_id: int
    ) -> PortfolioModel:
        """Ownership check, enforced before any portfolio data is read.

        Deliberately returns 404 (not 403) for a portfolio owned by someone
        else, so the endpoint does not confirm the existence of other users'
        portfolio ids.
        """
        result = await db.execute(
            select(PortfolioModel).where(
                PortfolioModel.id == portfolio_id,
                PortfolioModel.user_id == user_id,
            )
        )
        portfolio = result.scalars().first()
        if portfolio is None:
            raise FinPilotException(status_code=404, message="Portfolio not found")
        return portfolio

    # ------------------------------------------------------------------ #
    # Build
    # ------------------------------------------------------------------ #
    async def build(
        self,
        db: AsyncSession,
        portfolio_id: int,
        user_id: int,
        profile: InvestmentProfile,
        max_holdings: int = 8,
        include_documents: bool = True,
        question: Optional[str] = None,
    ) -> StrategyContext:
        portfolio = await self.assert_portfolio_owned_by(db, portfolio_id, user_id)

        blocks: List[ContextBlock] = []
        gaps: List[str] = []

        # 1. User investment profile ------------------------------------ #
        blocks.append(
            ContextBlock(
                ref="PROFILE-1",
                kind="profile",
                label="User investment profile (self-reported)",
                content=profile.model_dump(exclude_none=True),
                retrieved_at=_now(),
            )
        )

        # 2. Portfolio holdings + analytics ----------------------------- #
        holdings = []
        analytics_ok = False
        try:
            analytics = await self.portfolio_engine.get_portfolio_analytics(db, portfolio_id)
            blocks.append(
                ContextBlock(
                    ref="PORTFOLIO-1",
                    kind="portfolio",
                    label=f"Analytics for portfolio '{portfolio.name}' (performance, allocation, risk)",
                    content=analytics.model_dump(),
                    retrieved_at=_now(),
                )
            )
            analytics_ok = True
        except Exception as exc:  # noqa: BLE001 - degrade, do not fail the request
            logger.warning("Portfolio analytics unavailable for %s: %s", portfolio_id, exc)
            gaps.append(
                "Portfolio analytics (performance, allocation and risk metrics) could not be "
                "computed; allocation and risk commentary is therefore unsupported by measured data."
            )

        try:
            holdings = await self.portfolio_engine.get_hydrated_holdings(db, portfolio_id)
            blocks.append(
                ContextBlock(
                    ref="PORTFOLIO-2",
                    kind="portfolio",
                    label=f"Holdings for portfolio '{portfolio.name}'",
                    content=[h.model_dump() for h in holdings],
                    retrieved_at=_now(),
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Holdings unavailable for %s: %s", portfolio_id, exc)
            gaps.append("Portfolio holdings could not be loaded.")

        if not holdings and analytics_ok:
            gaps.append("The portfolio contains no holdings; review is limited to the stated profile.")

        tickers = self._top_tickers(holdings, max_holdings)

        # 3. Company information + market research ---------------------- #
        if tickers:
            company_blocks, company_gaps = await self._company_context(tickers)
            blocks.extend(company_blocks)
            gaps.extend(company_gaps)

            news_blocks, news_gaps = await self._news_context(tickers)
            blocks.extend(news_blocks)
            gaps.extend(news_gaps)

        # 4. Documents (RAG) -------------------------------------------- #
        if include_documents and self.rag_engine is not None:
            doc_blocks, doc_gaps = await self._document_context(
                user_id=user_id, tickers=tickers, question=question, profile=profile
            )
            blocks.extend(doc_blocks)
            gaps.extend(doc_gaps)
        elif include_documents:
            gaps.append("Document retrieval was requested but no RAG engine is configured.")

        return StrategyContext(blocks=blocks, gaps=gaps)

    # ------------------------------------------------------------------ #
    # Sources
    # ------------------------------------------------------------------ #
    @staticmethod
    def _top_tickers(holdings, limit: int) -> List[str]:
        """Largest positions first, so a capped context covers what matters most."""
        ranked = sorted(
            holdings,
            key=lambda h: (h.market_value or 0.0),
            reverse=True,
        )
        seen, tickers = set(), []
        for h in ranked:
            symbol = (h.ticker_symbol or "").upper()
            if symbol and symbol not in seen:
                seen.add(symbol)
                tickers.append(symbol)
            if len(tickers) >= limit:
                break
        return tickers

    async def _company_context(self, tickers: List[str]):
        """Company profile + financial ratios per holding, fetched concurrently."""

        async def one(ticker: str):
            profile, ratios = await asyncio.gather(
                self.md.get_company_profile(ticker),
                self.md.get_financial_ratios(ticker),
                return_exceptions=True,
            )
            return ticker, profile, ratios

        results = await asyncio.gather(*(one(t) for t in tickers), return_exceptions=True)

        blocks, gaps = [], []
        company_idx, research_idx = 0, 0
        for result in results:
            if isinstance(result, Exception):
                gaps.append("Company research failed for one or more holdings.")
                continue
            ticker, profile, ratios = result

            if isinstance(profile, Exception) or not profile:
                gaps.append(f"No company profile available for {ticker}.")
            else:
                company_idx += 1
                blocks.append(
                    ContextBlock(
                        ref=f"COMPANY-{company_idx}",
                        kind="company",
                        label=f"Company profile — {ticker}",
                        content=profile.model_dump(),
                        retrieved_at=_now(),
                    )
                )

            if isinstance(ratios, Exception) or not ratios:
                gaps.append(f"No financial ratios available for {ticker}.")
            else:
                research_idx += 1
                blocks.append(
                    ContextBlock(
                        ref=f"RESEARCH-{research_idx}",
                        kind="research",
                        label=f"Financial ratios — {ticker}",
                        content=[r.model_dump() for r in ratios],
                        retrieved_at=_now(),
                    )
                )
        return blocks, gaps

    async def _news_context(self, tickers: List[str], per_ticker: int = 3):
        async def one(ticker: str):
            return ticker, await self.md.get_market_news(ticker, per_ticker)

        results = await asyncio.gather(*(one(t) for t in tickers), return_exceptions=True)

        blocks, gaps, idx = [], [], 0
        for result in results:
            if isinstance(result, Exception):
                gaps.append("News retrieval failed for one or more holdings.")
                continue
            ticker, articles = result
            if not articles:
                gaps.append(f"No recent news found for {ticker}.")
                continue
            idx += 1
            blocks.append(
                ContextBlock(
                    ref=f"NEWS-{idx}",
                    kind="news",
                    label=f"Recent news — {ticker}",
                    content=[a.model_dump() for a in articles],
                    retrieved_at=_now(),
                )
            )
        return blocks, gaps

    async def _document_context(
        self,
        user_id: int,
        tickers: List[str],
        question: Optional[str],
        profile: InvestmentProfile,
    ):
        """Retrieve from the user's own uploaded filings, always tenant-scoped."""
        focus = question or (
            "Long-term risks, competitive position and capital allocation relevant to a "
            f"{profile.time_horizon_years}-year {profile.risk_tolerance} investor."
        )

        async def one(ticker: str):
            return ticker, await self.rag_engine.query(
                query=f"{focus} ({ticker})",
                top_k=3,
                metadata_filters={"user_id": user_id, "ticker": ticker},
            )

        targets = tickers[:5] or []
        if not targets:
            return [], []

        results = await asyncio.gather(*(one(t) for t in targets), return_exceptions=True)

        blocks, gaps, idx = [], [], 0
        for result in results:
            if isinstance(result, Exception):
                gaps.append("Document retrieval failed for one or more holdings.")
                continue
            ticker, rag_response = result
            if not rag_response or not rag_response.citations:
                gaps.append(f"No uploaded documents matched {ticker}.")
                continue
            idx += 1
            blocks.append(
                ContextBlock(
                    ref=f"DOCS-{idx}",
                    kind="documents",
                    label=f"Filing extract — {ticker}",
                    content={
                        "answer": rag_response.answer,
                        "retrieval_confidence": rag_response.confidence_score,
                        "citations": [c.model_dump() for c in rag_response.citations],
                    },
                    retrieved_at=_now(),
                )
            )
        return blocks, gaps
