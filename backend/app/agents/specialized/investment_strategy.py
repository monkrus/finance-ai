"""Investment Strategy agent.

Two modes, one config:

* `chat` / `chat_stream` (inherited from `BaseAgent`) — conversational use via
  the `AgentRouter`, tool-calling as usual.
* `build_strategy` — the structured path behind `POST /agents/investment-strategy`.
  It assembles context deterministically, generates once against a strict schema,
  then validates the output against the context before returning it.

The validation step is the point. A model asked to cite will cite; whether the
refs it produced actually exist is a question only the server can answer, so the
server answers it rather than trusting the citation list.
"""

import logging
from typing import Any, Dict, List, Optional

from app.agents.base import BaseAgent
from app.agents.models import AgentConfig
from app.ai.gateway import AIGatewayService
from app.schemas.investment_strategy import (
    GroundedFinding,
    InvestmentStrategyRequest,
    InvestmentStrategyResponse,
    StrategyContext,
    StrategySection,
    ValidationReport,
)

logger = logging.getLogger(__name__)

SECTION_KEYS = [
    ("portfolio_review", "Portfolio Review"),
    ("asset_allocation", "Asset Allocation"),
    ("diversification", "Diversification Analysis"),
    ("risk_explanation", "Risk Explanation"),
    ("long_term_plan", "Long-Term Plan"),
]


class InvestmentStrategyAgent(BaseAgent):
    def __init__(self, gateway: AIGatewayService, context_builder=None):
        config = AgentConfig(
            name="investment_strategy",
            description=(
                "Long-term investment strategy: portfolio review, asset allocation, "
                "diversification, risk explanation and multi-year planning."
            ),
            system_prompt_name="agent_investment_strategy",
            allowed_tools=[
                "portfolio_summary",
                "portfolio_allocation",
                "portfolio_risk",
                "portfolio_performance",
                "get_company_profile",
                "get_financial_ratios",
                "get_market_news",
                "query_financial_documents",
                "calculator",
            ],
            temperature=0.3,
        )
        super().__init__(config, gateway)
        self.context_builder = context_builder

    # ------------------------------------------------------------------ #
    # Structured path
    # ------------------------------------------------------------------ #
    async def build_strategy(
        self,
        db,
        user_id: int,
        request: InvestmentStrategyRequest,
    ) -> InvestmentStrategyResponse:
        if self.context_builder is None:
            raise RuntimeError(
                "InvestmentStrategyAgent was constructed without a context builder; "
                "the structured path is unavailable."
            )

        context = await self.context_builder.build(
            db=db,
            portfolio_id=request.portfolio_id,
            user_id=user_id,
            profile=request.profile,
            max_holdings=request.max_holdings,
            include_documents=request.include_documents,
            question=request.question,
        )

        raw = await self.gateway.generate_json(
            prompt_name=self.config.system_prompt_name,
            temperature=self.config.temperature,
            max_tokens=6144,
            context=context.render(),
            profile_summary=self._profile_summary(request),
            question=request.question or "(no specific question — produce a full strategy review)",
            known_gaps=self._render_gaps(context),
        )

        return self.validate_against_context(raw, context)

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #
    def validate_against_context(
        self, raw: Dict[str, Any], context: StrategyContext
    ) -> InvestmentStrategyResponse:
        """Enforce grounding after the fact.

        Findings citing refs that are not in the context are dropped, not
        reworded — a fabricated citation makes the statement unverifiable, and an
        unverifiable statement is exactly what this endpoint exists to avoid.
        """
        valid_refs = context.refs()
        report = ValidationReport()
        sections: Dict[str, StrategySection] = {}

        for key, default_title in SECTION_KEYS:
            payload = raw.get(key) or {}
            if not isinstance(payload, dict):
                payload = {}

            findings, insights = [], []
            for item in payload.get("grounded_findings") or []:
                finding = self._coerce_finding(item)
                if finding is None:
                    continue
                resolved = [r for r in finding.refs if r in valid_refs]
                unresolved = [r for r in finding.refs if r not in valid_refs]
                report.unresolved_refs.extend(unresolved)

                if resolved:
                    findings.append(GroundedFinding(statement=finding.statement, refs=resolved))
                else:
                    report.dropped_findings += 1

            for item in payload.get("generated_insights") or []:
                if isinstance(item, str) and item.strip():
                    insights.append(item.strip())

            if not findings and insights:
                report.ungrounded_sections.append(key)

            sections[key] = StrategySection(
                title=str(payload.get("title") or default_title),
                grounded_findings=findings,
                generated_insights=insights,
            )

        report.unresolved_refs = sorted(set(report.unresolved_refs))

        confidence = self._confidence(raw, context, report)

        gaps = [g for g in context.gaps]
        for gap in raw.get("data_gaps") or []:
            if isinstance(gap, str) and gap.strip() and gap.strip() not in gaps:
                gaps.append(gap.strip())

        if report.dropped_findings:
            report.notes.append(
                f"{report.dropped_findings} statement(s) were removed because their citations "
                "did not resolve to retrieved context."
            )
        if report.ungrounded_sections:
            report.notes.append(
                "Sections with interpretation but no grounded finding: "
                + ", ".join(report.ungrounded_sections)
            )

        return InvestmentStrategyResponse(
            summary=str(raw.get("summary") or "").strip()
            or "Insufficient grounded context to summarise this portfolio.",
            assumptions=[a.strip() for a in (raw.get("assumptions") or []) if isinstance(a, str) and a.strip()],
            data_gaps=gaps,
            sources=context.as_sources(),
            confidence=confidence,
            validation=report,
            **sections,
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _coerce_finding(item: Any) -> Optional[GroundedFinding]:
        if isinstance(item, dict):
            statement = str(item.get("statement") or "").strip()
            refs = item.get("refs") or []
            if not statement:
                return None
            if isinstance(refs, str):
                refs = [refs]
            return GroundedFinding(
                statement=statement,
                refs=[str(r).strip() for r in refs if str(r).strip()],
            )
        if isinstance(item, str) and item.strip():
            # A bare string carries no citation, so it cannot survive validation.
            return GroundedFinding(statement=item.strip(), refs=[])
        return None

    def _confidence(
        self, raw: Dict[str, Any], context: StrategyContext, report: ValidationReport
    ) -> float:
        try:
            confidence = float(raw.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))

        ceilings: List[float] = []
        if report.dropped_findings or report.unresolved_refs:
            ceilings.append(0.5)
        if report.ungrounded_sections:
            ceilings.append(0.6)
        if not any(b.kind == "portfolio" for b in context.blocks):
            # No measured portfolio data means nothing quantitative is grounded.
            ceilings.append(0.35)
        if len(context.gaps) >= 5:
            ceilings.append(0.7)

        if ceilings:
            capped = min(ceilings)
            if capped < confidence:
                report.confidence_adjusted = True
                return round(capped, 2)
        return round(confidence, 2)

    @staticmethod
    def _profile_summary(request: InvestmentStrategyRequest) -> str:
        p = request.profile
        parts = [
            f"risk tolerance: {p.risk_tolerance}",
            f"time horizon: {p.time_horizon_years} years",
            f"experience: {p.experience_level}",
        ]
        if p.goals:
            parts.append("goals: " + "; ".join(p.goals))
        if p.annual_contribution is not None:
            parts.append(f"annual contribution: {p.annual_contribution}")
        if p.liquidity_needs:
            parts.append(f"liquidity needs: {p.liquidity_needs}")
        if p.constraints:
            parts.append("constraints: " + "; ".join(p.constraints))
        if p.tax_status:
            parts.append(f"tax status: {p.tax_status}")
        return " | ".join(parts)

    @staticmethod
    def _render_gaps(context: StrategyContext) -> str:
        if not context.gaps:
            return "(none — every requested source returned data)"
        return "\n".join(f"- {g}" for g in context.gaps)
