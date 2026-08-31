"""Agent endpoints.

Currently exposes the structured Investment Strategy agent. Conversational
access to every agent stays on `/ai/chat` via the `AgentRouter`; this router is
for agents with a typed request/response contract worth calling directly.

Composition is done through FastAPI dependencies rather than module-level
globals so the agent can be swapped in tests with `app.dependency_overrides`.
"""

import logging
from functools import lru_cache

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.context import InvestmentContextBuilder
from app.agents.specialized.investment_strategy import InvestmentStrategyAgent
from app.api.deps import get_current_user
from app.core.database import get_db
from app.market_data.service import MarketDataService
from app.models.user import User
from app.portfolio.engine import PortfolioEngine
from app.schemas.investment_strategy import (
    InvestmentProfile,
    InvestmentStrategyRequest,
    InvestmentStrategyResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@lru_cache(maxsize=1)
def get_investment_strategy_agent() -> InvestmentStrategyAgent:
    """Build the agent and its context builder once per process.

    Reuses the gateway and RAG engine already constructed by the AI and
    documents routers so prompts, tools and the vector store are shared rather
    than duplicated per router.
    """
    from app.api.v1.ai import gateway
    from app.api.v1.documents import rag_engine

    md_service = MarketDataService()
    from app.analysis.engine import AnalysisEngine

    portfolio_engine = PortfolioEngine(
        market_data_service=md_service, analysis_engine=AnalysisEngine(md_service)
    )
    context_builder = InvestmentContextBuilder(
        portfolio_engine=portfolio_engine,
        market_data_service=md_service,
        rag_engine=rag_engine,
    )
    return InvestmentStrategyAgent(gateway=gateway, context_builder=context_builder)


async def resolve_investment_profile(
    request: InvestmentStrategyRequest, user: User
) -> InvestmentProfile:
    """Seam for profile resolution.

    The profile arrives in the request body today. When a persisted profile
    exists, this is the only function that changes: load the stored profile and
    treat the request body as a per-call override.
    """
    return request.profile


@router.post("/investment-strategy", response_model=InvestmentStrategyResponse)
async def investment_strategy(
    request: InvestmentStrategyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    agent: InvestmentStrategyAgent = Depends(get_investment_strategy_agent),
) -> InvestmentStrategyResponse:
    """Produce a grounded long-term investment strategy for one of the user's portfolios.

    Portfolio ownership is verified against the authenticated user before any
    holding is read — the portfolio id is never trusted on its own.
    """
    if request.question:
        # Free-text reaches the model, so it goes through the same input filter
        # as chat input rather than around it.
        request.question = agent.gateway.safety_filter.validate_input(request.question)

    request.profile = await resolve_investment_profile(request, current_user)

    logger.info(
        "Investment strategy requested by user=%s portfolio=%s", current_user.id, request.portfolio_id
    )

    return await agent.build_strategy(db=db, user_id=current_user.id, request=request)
