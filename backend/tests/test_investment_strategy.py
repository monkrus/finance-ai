"""Tests for the Investment Strategy agent.

Focus is on the parts that can fail silently in production: ownership
enforcement, graceful degradation when a data source is down, and whether the
grounding validator actually removes fabricated citations.
"""

import pytest

from app.agents.context import InvestmentContextBuilder
from app.agents.specialized.investment_strategy import InvestmentStrategyAgent
from app.core.exceptions import FinPilotException
from app.schemas.investment_strategy import InvestmentStrategyRequest

from tests.conftest import (
    FakeMarketDataService,
    FakeModel,
    FakePortfolioEngine,
    FakeRagEngine,
    FakeSession,
)


# --------------------------------------------------------------------------- #
# Ownership
# --------------------------------------------------------------------------- #
class TestOwnership:
    async def test_rejects_portfolio_not_owned_by_user(self, profile):
        # The query filters on user_id, so a foreign portfolio yields no row.
        builder = InvestmentContextBuilder(
            FakePortfolioEngine(), FakeMarketDataService(), None
        )
        with pytest.raises(FinPilotException) as exc:
            await builder.build(
                db=FakeSession(None), portfolio_id=1, user_id=42, profile=profile
            )
        assert exc.value.status_code == 404

    async def test_owned_portfolio_is_accepted(self, profile, owned_portfolio, analytics):
        builder = InvestmentContextBuilder(
            FakePortfolioEngine(analytics=analytics), FakeMarketDataService(), None
        )
        ctx = await builder.build(
            db=FakeSession(owned_portfolio),
            portfolio_id=1,
            user_id=42,
            profile=profile,
            include_documents=False,
        )
        assert "PORTFOLIO-1" in ctx.refs()


# --------------------------------------------------------------------------- #
# Context assembly
# --------------------------------------------------------------------------- #
class TestContextAssembly:
    async def test_collects_every_source(
        self, profile, owned_portfolio, analytics, holdings
    ):
        md = FakeMarketDataService(
            profiles={"AAPL": FakeModel(name="Apple Inc.", sector="Technology")},
            ratios={"AAPL": [FakeModel(pe_ratio=31.2)]},
            news={"AAPL": [FakeModel(headline="Apple reports Q3")]},
        )
        rag = FakeRagEngine(
            responses={
                "AAPL": FakeModel(
                    answer="Supply chain concentration is a stated risk.",
                    confidence_score=0.8,
                    citations=[FakeModel(chunk_id="c1", source="aapl-10k.txt")],
                )
            }
        )
        builder = InvestmentContextBuilder(
            FakePortfolioEngine(analytics=analytics, holdings=holdings), md, rag
        )
        ctx = await builder.build(
            db=FakeSession(owned_portfolio), portfolio_id=1, user_id=42, profile=profile
        )

        kinds = {b.kind for b in ctx.blocks}
        assert {"profile", "portfolio", "company", "research", "news", "documents"} <= kinds

    async def test_rag_retrieval_is_tenant_scoped(
        self, profile, owned_portfolio, analytics, holdings
    ):
        """A user must never retrieve another user's uploaded filings."""
        rag = FakeRagEngine()
        builder = InvestmentContextBuilder(
            FakePortfolioEngine(analytics=analytics, holdings=holdings),
            FakeMarketDataService(),
            rag,
        )
        await builder.build(
            db=FakeSession(owned_portfolio), portfolio_id=1, user_id=42, profile=profile
        )
        assert rag.calls, "expected document retrieval to run"
        assert all(filters.get("user_id") == 42 for _q, filters in rag.calls)

    async def test_context_refs_are_unique_even_when_sources_partially_fail(
        self, profile, owned_portfolio, analytics, holdings
    ):
        """Regression: two tickers whose profiles fail but whose ratios succeed
        must not share a RESEARCH ref — a duplicate ref makes citations
        ambiguous between different tickers' data."""
        md = FakeMarketDataService(
            profiles={},  # every profile lookup fails
            ratios={
                "AAPL": [FakeModel(pe_ratio=31.2)],
                "XOM": [FakeModel(pe_ratio=11.8)],
            },
        )
        builder = InvestmentContextBuilder(
            FakePortfolioEngine(analytics=analytics, holdings=holdings), md, None
        )
        ctx = await builder.build(
            db=FakeSession(owned_portfolio),
            portfolio_id=1,
            user_id=42,
            profile=profile,
            include_documents=False,
        )
        refs = [b.ref for b in ctx.blocks]
        assert len(refs) == len(set(refs)), f"duplicate refs: {refs}"
        research_refs = sorted(b.ref for b in ctx.blocks if b.kind == "research")
        assert research_refs == ["RESEARCH-1", "RESEARCH-2"]

    async def test_failing_source_becomes_a_recorded_gap(
        self, profile, owned_portfolio, holdings
    ):
        """A dead provider degrades the answer visibly instead of 500-ing."""
        builder = InvestmentContextBuilder(
            FakePortfolioEngine(holdings=holdings, fail_analytics=True),
            FakeMarketDataService(),
            None,
        )
        ctx = await builder.build(
            db=FakeSession(owned_portfolio),
            portfolio_id=1,
            user_id=42,
            profile=profile,
            include_documents=False,
        )
        assert "PORTFOLIO-1" not in ctx.refs()
        assert any("analytics" in g.lower() for g in ctx.gaps)

    async def test_holdings_are_capped_and_ranked_by_size(
        self, profile, owned_portfolio, analytics, holdings
    ):
        md = FakeMarketDataService(
            news={t: [FakeModel(headline=f"{t} news")] for t in ("AAPL", "XOM", "MSFT")}
        )
        builder = InvestmentContextBuilder(
            FakePortfolioEngine(analytics=analytics, holdings=holdings), md, None
        )
        ctx = await builder.build(
            db=FakeSession(owned_portfolio),
            portfolio_id=1,
            user_id=42,
            profile=profile,
            max_holdings=1,
            include_documents=False,
        )
        news_labels = [b.label for b in ctx.blocks if b.kind == "news"]
        assert news_labels == ["Recent news — AAPL"]  # largest position only


# --------------------------------------------------------------------------- #
# Grounding validation
# --------------------------------------------------------------------------- #
class TestGroundingValidation:
    @pytest.fixture
    def agent(self):
        return InvestmentStrategyAgent(gateway=None)

    def test_drops_findings_with_fabricated_refs(self, agent, context):
        raw = {
            "summary": "s",
            "portfolio_review": {
                "grounded_findings": [
                    {"statement": "Portfolio is worth $125,000.", "refs": ["PORTFOLIO-1"]},
                    {"statement": "Beta is 4.2 per the risk model.", "refs": ["PORTFOLIO-9"]},
                ],
                "generated_insights": ["Concentration is high."],
            },
            "confidence": 0.95,
        }
        result = agent.validate_against_context(raw, context)

        statements = [f.statement for f in result.portfolio_review.grounded_findings]
        assert statements == ["Portfolio is worth $125,000."]
        assert result.validation.dropped_findings == 1
        assert result.validation.unresolved_refs == ["PORTFOLIO-9"]

    def test_partially_valid_refs_are_narrowed_not_dropped(self, agent, context):
        raw = {
            "portfolio_review": {
                "grounded_findings": [
                    {"statement": "Tech is 71% of the book.", "refs": ["PORTFOLIO-1", "MADE-UP-3"]}
                ]
            },
            "confidence": 0.9,
        }
        result = agent.validate_against_context(raw, context)
        finding = result.portfolio_review.grounded_findings[0]
        assert finding.refs == ["PORTFOLIO-1"]
        assert result.validation.dropped_findings == 0

    def test_uncited_statement_cannot_survive(self, agent, context):
        raw = {"risk_explanation": {"grounded_findings": ["Beta is 1.29."]}, "confidence": 0.9}
        result = agent.validate_against_context(raw, context)
        assert result.risk_explanation.grounded_findings == []
        assert result.validation.dropped_findings == 1

    def test_confidence_is_capped_when_citations_fail(self, agent, context):
        raw = {
            "diversification": {
                "grounded_findings": [{"statement": "x", "refs": ["NOPE-1"]}]
            },
            "confidence": 0.99,
        }
        result = agent.validate_against_context(raw, context)
        assert result.confidence <= 0.5
        assert result.validation.confidence_adjusted is True

    def test_confidence_is_capped_hard_without_portfolio_data(self, agent, context):
        context.blocks = [b for b in context.blocks if b.kind != "portfolio"]
        raw = {
            "portfolio_review": {
                "grounded_findings": [{"statement": "Profile says moderate.", "refs": ["PROFILE-1"]}]
            },
            "confidence": 0.9,
        }
        result = agent.validate_against_context(raw, context)
        assert result.confidence <= 0.35

    def test_honest_low_confidence_is_not_inflated(self, agent, context):
        raw = {
            "portfolio_review": {
                "grounded_findings": [{"statement": "ok", "refs": ["PORTFOLIO-1"]}]
            },
            "confidence": 0.2,
        }
        result = agent.validate_against_context(raw, context)
        assert result.confidence == 0.2
        assert result.validation.confidence_adjusted is False

    def test_retrieval_gaps_reach_the_response(self, agent, context):
        context.gaps = ["No uploaded documents matched AAPL."]
        result = agent.validate_against_context({"data_gaps": ["Cost basis unknown."]}, context)
        assert "No uploaded documents matched AAPL." in result.data_gaps
        assert "Cost basis unknown." in result.data_gaps

    def test_sources_are_always_reported(self, agent, context):
        result = agent.validate_against_context({}, context)
        assert {s.ref for s in result.sources} == {"PROFILE-1", "PORTFOLIO-1", "NEWS-1"}

    def test_empty_model_output_yields_a_safe_response(self, agent, context):
        result = agent.validate_against_context({}, context)
        assert result.summary
        assert result.confidence == 0.0
        assert all(s.grounded_findings == [] for s in result.sections().values())


# --------------------------------------------------------------------------- #
# Prompt
# --------------------------------------------------------------------------- #
class TestPrompt:
    def test_strategy_prompt_renders_with_all_variables(self):
        """Guards the JSON braces in the template against `str.format` errors."""
        from app.agents.prompts import register_agent_prompts
        from app.ai.prompt_manager import PromptManager

        pm = PromptManager()
        register_agent_prompts(pm)
        rendered = pm.render(
            "agent_investment_strategy",
            context="[PORTFOLIO-1 | PORTFOLIO | analytics]\n{}",
            profile_summary="risk tolerance: moderate",
            question="Am I too concentrated?",
            known_gaps="- none",
        )
        assert "Am I too concentrated?" in rendered
        assert '"grounded_findings"' in rendered


# --------------------------------------------------------------------------- #
# Endpoint
# --------------------------------------------------------------------------- #
class TestEndpoint:
    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from app.api.deps import get_current_user
        from app.api.v1.agents import get_investment_strategy_agent, router
        from app.core.database import get_db

        app = FastAPI()
        app.include_router(router, prefix="/agents")

        class StubAgent:
            def __init__(self):
                self.seen = None

                class _GW:
                    class safety_filter:
                        @staticmethod
                        def validate_input(text):
                            return text

                self.gateway = _GW()

            async def build_strategy(self, db, user_id, request):
                self.seen = (user_id, request)
                from app.schemas.investment_strategy import (
                    GroundedFinding,
                    InvestmentStrategyResponse,
                    StrategySection,
                )

                empty = StrategySection(title="t")
                return InvestmentStrategyResponse(
                    summary="ok",
                    portfolio_review=StrategySection(
                        title="Portfolio Review",
                        grounded_findings=[
                            GroundedFinding(statement="Worth $125,000.", refs=["PORTFOLIO-1"])
                        ],
                    ),
                    asset_allocation=empty,
                    diversification=empty,
                    risk_explanation=empty,
                    long_term_plan=empty,
                    confidence=0.7,
                )

        stub = StubAgent()
        app.dependency_overrides[get_current_user] = lambda: FakeModel(id=42, email="a@b.c")
        app.dependency_overrides[get_db] = lambda: FakeSession(None)
        app.dependency_overrides[get_investment_strategy_agent] = lambda: stub

        yield TestClient(app), stub

    def test_returns_a_grounded_strategy(self, client):
        http, _stub = client
        res = http.post(
            "/agents/investment-strategy",
            json={
                "portfolio_id": 1,
                "profile": {"risk_tolerance": "aggressive", "time_horizon_years": 25},
                "question": "How diversified am I?",
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["portfolio_review"]["grounded_findings"][0]["refs"] == ["PORTFOLIO-1"]
        assert "disclaimer" in body

    def test_user_identity_comes_from_the_token_not_the_body(self, client):
        """The caller cannot name someone else as the owner of the request."""
        http, stub = client
        res = http.post(
            "/agents/investment-strategy",
            json={"portfolio_id": 1, "user_id": 999},
        )
        assert res.status_code == 200
        user_id, _request = stub.seen
        assert user_id == 42

    def test_invalid_profile_is_rejected(self, client):
        http, _stub = client
        res = http.post(
            "/agents/investment-strategy",
            json={"portfolio_id": 1, "profile": {"risk_tolerance": "yolo"}},
        )
        assert res.status_code == 422
