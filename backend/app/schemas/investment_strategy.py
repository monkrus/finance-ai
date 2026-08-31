"""Schemas for the Investment Strategy agent.

The response model is deliberately opinionated: it forces the model to keep
retrieved facts (`grounded_findings`, each carrying context refs) separate from
its own interpretation (`generated_insights`), and to declare `assumptions` and
`data_gaps` explicitly. Anything the model cannot ground is either dropped by
the validator or surfaced as a gap — it never gets to quietly become prose.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

RiskTolerance = Literal["conservative", "moderate", "aggressive"]
ExperienceLevel = Literal["beginner", "intermediate", "advanced"]


# --------------------------------------------------------------------------- #
# Request
# --------------------------------------------------------------------------- #
class InvestmentProfile(BaseModel):
    """The user's investment profile.

    Supplied per-request today. `resolve_investment_profile` in the API layer is
    the seam where a persisted profile would be loaded instead, without any
    change to the agent or the context builder.
    """

    risk_tolerance: RiskTolerance = "moderate"
    time_horizon_years: int = Field(default=10, ge=1, le=60)
    experience_level: ExperienceLevel = "intermediate"
    goals: List[str] = Field(default_factory=list)
    annual_contribution: Optional[float] = Field(default=None, ge=0)
    liquidity_needs: Optional[str] = None
    constraints: List[str] = Field(
        default_factory=list,
        description="Hard constraints, e.g. 'no tobacco', 'must stay 20% cash'.",
    )
    tax_status: Optional[str] = None


class InvestmentStrategyRequest(BaseModel):
    portfolio_id: int
    profile: InvestmentProfile = Field(default_factory=InvestmentProfile)
    question: Optional[str] = Field(
        default=None,
        description="Optional focus for this run, e.g. 'am I too concentrated in tech?'.",
    )
    include_documents: bool = Field(
        default=True,
        description="Whether to retrieve from the user's uploaded filings via RAG.",
    )
    max_holdings: int = Field(
        default=8,
        ge=1,
        le=25,
        description="Cap on holdings enriched with research/news, to bound latency and cost.",
    )


# --------------------------------------------------------------------------- #
# Response
# --------------------------------------------------------------------------- #
class GroundedFinding(BaseModel):
    """A factual statement that must be traceable to retrieved context."""

    statement: str
    refs: List[str] = Field(
        default_factory=list,
        description="Context block refs (e.g. 'PORTFOLIO-1') supporting this statement.",
    )


class StrategySection(BaseModel):
    title: str
    grounded_findings: List[GroundedFinding] = Field(default_factory=list)
    generated_insights: List[str] = Field(
        default_factory=list,
        description="Model interpretation built on the findings. Not itself retrieved fact.",
    )


class SourceRef(BaseModel):
    ref: str
    kind: str
    label: str
    retrieved_at: Optional[str] = None


class ValidationReport(BaseModel):
    """Post-generation checks. Populated server-side, never by the model."""

    unresolved_refs: List[str] = Field(default_factory=list)
    dropped_findings: int = 0
    ungrounded_sections: List[str] = Field(default_factory=list)
    confidence_adjusted: bool = False
    notes: List[str] = Field(default_factory=list)


class InvestmentStrategyResponse(BaseModel):
    summary: str
    portfolio_review: StrategySection
    asset_allocation: StrategySection
    diversification: StrategySection
    risk_explanation: StrategySection
    long_term_plan: StrategySection

    assumptions: List[str] = Field(default_factory=list)
    data_gaps: List[str] = Field(default_factory=list)
    sources: List[SourceRef] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    validation: ValidationReport = Field(default_factory=ValidationReport)
    disclaimer: str = (
        "Educational analysis generated from the data listed under `sources`. "
        "Not personalised financial advice."
    )

    def sections(self) -> Dict[str, StrategySection]:
        return {
            "portfolio_review": self.portfolio_review,
            "asset_allocation": self.asset_allocation,
            "diversification": self.diversification,
            "risk_explanation": self.risk_explanation,
            "long_term_plan": self.long_term_plan,
        }


# --------------------------------------------------------------------------- #
# Context (internal, but exposed for debugging / evaluation)
# --------------------------------------------------------------------------- #
class ContextBlock(BaseModel):
    """One retrieved unit of evidence, addressable by `ref`."""

    ref: str
    kind: Literal["portfolio", "research", "company", "news", "documents", "profile"]
    label: str
    content: Any
    retrieved_at: Optional[str] = None

    def render(self) -> str:
        import json

        body = (
            json.dumps(self.content, default=str, indent=2)
            if not isinstance(self.content, str)
            else self.content
        )
        return f"[{self.ref} | {self.kind.upper()} | {self.label}]\n{body}"


class StrategyContext(BaseModel):
    blocks: List[ContextBlock] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)

    def render(self) -> str:
        if not self.blocks:
            return "(no context retrieved)"
        return "\n\n".join(b.render() for b in self.blocks)

    def refs(self) -> set:
        return {b.ref for b in self.blocks}

    def as_sources(self) -> List[SourceRef]:
        return [
            SourceRef(ref=b.ref, kind=b.kind, label=b.label, retrieved_at=b.retrieved_at)
            for b in self.blocks
        ]
