# Task 2 — Investment Strategy Agent

## What was built

| File | Purpose |
|---|---|
| `app/schemas/investment_strategy.py` | Request/response contract, including the fact/insight separation |
| `app/agents/context.py` | `InvestmentContextBuilder` — ownership check + evidence assembly from existing services |
| `app/agents/specialized/investment_strategy.py` | The agent: structured generation + post-hoc grounding validation |
| `app/agents/prompts.py` | `agent_investment_strategy` prompt; `INVESTMENT_STRATEGY` added to the router taxonomy |
| `app/api/v1/agents.py` | `POST /agents/investment-strategy` |
| `app/ai/gateway.py` | `generate_json()` — structured generation inside the gateway |
| `app/ai/providers/{base,gemini}.py` | `generate_structured()` as a provider capability |
| `tests/` | 19 tests: ownership, degradation, tenant scoping, grounding validation, endpoint |
| `main.py` | Router mounted |

Run with `cd backend && python -m pytest`.

## Design decisions

### The agent has two modes, one config

`InvestmentStrategyAgent` subclasses `BaseAgent`, so it registers in `AgentRouter`
alongside the other six and works conversationally with tool calling — the
existing pattern, unchanged. It adds `build_strategy()` for the structured
endpoint, which does something the chat path cannot: assemble context
deterministically, generate once against a fixed schema, and verify the result.

Free-form chat is the wrong shape for this deliverable. A strategy review has
five required sections, must separate fact from inference, and must be
checkable. That needs a typed contract, not a paragraph.

> **Plain-language example:** The agent can both have a casual conversation
> ("tell me about my portfolio") and produce a formal structured report with
> verified citations. Same brain, two modes — one for chatting, one for
> delivering something you can act on.

### Context assembly is LLM-free and calls existing services

`InvestmentContextBuilder` calls `PortfolioEngine`, `MarketDataService` and
`RAGEngine` and reimplements none of them — no valuation, no allocation maths,
no risk metrics, no news impact logic. It converts their output into addressable
`ContextBlock`s (`PORTFOLIO-1`, `COMPANY-2`, `NEWS-1`, `DOCS-1`, `PROFILE-1`) and
nothing else.

Doing this deterministically rather than through tool calls is deliberate. The
endpoint has a fixed information requirement — the task specifies all five
sources — so letting the model decide whether to fetch the portfolio adds a
failure mode (it forgets) and latency (extra round trips) for no benefit. Tool
calling earns its complexity when the needed data is unknown ahead of time. Here
it is known.

Sources are fetched concurrently and defensively: a dead provider becomes an
entry in `context.gaps`, which flows into the response's `data_gaps` and caps
confidence. A market-data outage degrades the answer visibly instead of
returning a 500 or, worse, a confident answer with a silent hole in it.

> **Plain-language example:** Instead of hoping the AI remembers to look up your
> portfolio, the system always fetches it automatically — like a doctor's
> assistant who always pulls your chart before the appointment. If the market
> data feed is down, the report says "market data was unavailable" rather than
> crashing or quietly making things up.

### Ownership is checked before any data is read

`assert_portfolio_owned_by` filters on `user_id` from the JWT and returns 404 —
not 403 — for a portfolio belonging to someone else, so the endpoint does not
confirm the existence of other users' ids. RAG retrieval is scoped with
`metadata_filters={"user_id": ...}` on every call, which the tests assert
directly.

This is the shape the existing portfolio *tools* are missing; see issue #1 in
[01-architecture-review.md](01-architecture-review.md). I fixed the new path
rather than refactoring sixteen callbacks here, because the registry signature
change is a wider piece of work that deserves its own review.

> **Plain-language example:** If you request portfolio 42 and it is not yours,
> you get "not found" — not "access denied." Saying "access denied" would
> confirm that portfolio 42 exists and belongs to someone, which is itself
> information leakage.

### Investment profile: typed request input, behind a seam

The profile arrives in the request body as `InvestmentProfile`. There is no user
profile table in the schema, no `alembic.ini` and no migrations directory — the
app relies on `Base.metadata.create_all` at startup — so persisting it would mean
inventing migration infrastructure as a side effect of adding an agent.

`resolve_investment_profile()` in the API layer is the seam. When a stored
profile exists, that function loads it and treats the request body as a per-call
override; nothing in the agent or the context builder changes. The profile is
also a `ContextBlock` (`PROFILE-1`) like any other source, so claims about the
user's goals are citable in the same way as claims about their holdings.

### Structured generation moved into the gateway

`AgentRouter._detect_intent` and `RAGEngine.query` both reach into
`provider._execute_generate` — a private method — to get JSON out of the model,
bypassing the gateway's metrics and error handling. Rather than adding a third
caller to that pattern, I added `generate_structured()` to the provider
interface and `generate_json()` to the gateway, which renders the prompt, tracks
metrics, and returns a parsed dict or raises. Callers get JSON or an exception,
never half-parsed text. Migrating the two existing callers is a small follow-up.

### Endpoint path

Mounted at `/api/v1/agents/investment-strategy`, matching every other router in
`main.py`. The task specifies `POST /agents/investment-strategy` literally, so
that path is also registered as an alias (`include_in_schema=False`) pointing at
the same handler. One implementation, two routes; the alias should be dropped
once clients move to the versioned path.

Composition uses FastAPI dependencies rather than module-level globals, so the
endpoint tests run with `dependency_overrides` and no database.

---

## Prompt engineering strategy

The full prompt is `agent_investment_strategy` in `app/agents/prompts.py`. Five
choices, and why each is there.

### 1. One rule, stated first, with a ranked fallback

The grounding requirement is the first content in the prompt, before role or
task. It gives three ordered options when context is missing — omit, mark as
insight, or declare a gap — because "don't hallucinate" without an alternative
leaves the model with nowhere to go, and the path of least resistance is to
generate something plausible. Naming fabricated citations as the *worst*
possible failure gives the model an explicit ordering to reason with, rather than
a prohibition it has to trade off against helpfulness.

### 2. Fact and insight are separate fields, not separate paragraphs

`grounded_findings` require refs; `generated_insights` are labelled model
interpretation. Asking for this in prose produces hedging language sprinkled
through a paragraph, which readers skim past. Making it structural means the
distinction survives into the API response and the UI, and it is machine
checkable — which is what makes the validator possible at all.

The instruction "do not put numbers here that are not in a finding above"
targets the specific failure I would expect: correctly citing 71% tech
concentration in a finding, then inventing "should be closer to 40%" in an
insight where nothing is checked.

### 3. Assumptions are demanded explicitly, not just permitted

Any reliance on something outside the context — an expected return, a
rebalancing convention, an inferred goal — must be written to `assumptions` in
plain language. Long-term planning cannot be done without assumptions; the goal
is not to eliminate them but to make them visible, so a user can disagree with
the assumption rather than with the conclusion.

### 4. Insufficiency is a designed output

The prompt states that a stated gap is a useful answer and a confident guess is
not, tells the model to lower confidence rather than fill space with generic
finance content, and pre-loads server-detected gaps under `KNOWN RETRIEVAL GAPS`
so the model cannot contradict what the server already knows is missing. Without
that section, a model told "market data unavailable" will still cheerfully
discuss the sector allocation it cannot see.

### 5. Confidence is declared as checked

The prompt tells the model that its `confidence` is verified server-side against
the citations it produced and that inflating it makes the answer look worse. This
aligns the incentive rather than relying on instruction — and the claim is true,
which is the next section.

> **Plain-language example:** The prompt tells the AI: "if you don't have the
> data, say so — a gap is a useful answer, a guess is not. And don't inflate
> your confidence score, because the server will check your citations and cap
> it if you're bluffing."

### Scope constraints

No buy/sell instructions on individual securities; changes framed as options with
trade-offs; allocation discussed in ranges rather than single "correct" numbers;
no price predictions; explanations pitched to the user's stated experience level.
The response also carries a non-advice disclaimer as a schema default, so it
cannot be omitted by a generation that forgets it.

---

## Grounding validation

The prompt is a request. `validate_against_context()` is the enforcement, and it
runs server-side on every response:

- **Fabricated refs are dropped.** A finding whose citations do not resolve to a
  real `ContextBlock` is removed from the response entirely — not reworded, not
  flagged. An unverifiable statement is what this endpoint exists to avoid.
- **Partially valid citations are narrowed.** Refs `["PORTFOLIO-1", "MADE-UP-3"]`
  become `["PORTFOLIO-1"]`; the statement survives with only the citations that
  hold up.
- **Uncited statements cannot survive.** A bare string in `grounded_findings`
  carries no ref and is dropped by construction.
- **Confidence is a ceiling, not a result.** Capped at 0.5 when citations failed,
  0.6 when a section has interpretation but no grounded finding, 0.35 when no
  portfolio data was retrieved at all. `confidence_adjusted` distinguishes honest
  low confidence from a claim that was cut down.
- **Retrieval gaps always reach the response**, merged with any the model
  declared.
- **Sources are always reported** from the context, not from the model — the
  client sees what was actually retrieved, independent of what was cited.

`ValidationReport` is populated entirely server-side and is never model output.

The tests cover each of these cases directly (`TestGroundingValidation`),
including that an empty model response degrades to a safe zero-confidence answer
rather than raising.

> **Plain-language example:** The AI writes "your portfolio is 71% tech
> [source: PORTFOLIO-1, source: MADE-UP-3]." The server checks: PORTFOLIO-1
> exists, MADE-UP-3 does not. It keeps the statement but removes the fake
> citation. If *both* citations were fake, the entire statement would be
> silently dropped from the report — like a journal editor pulling any claim
> with a fabricated footnote.

---

## What I would do next

1. Push the `ToolContext` authorization fix through the existing tool registry —
   the IDOR in the portfolio tools is the highest-priority item in the repo.
2. Migrate `AgentRouter._detect_intent` and `RAGEngine.query` onto
   `gateway.generate_json()` and delete the private-method calls.
3. Add the claim-entailment check described in
   [03-rag-review.md](03-rag-review.md) — citation resolution catches fabricated
   refs but not a real chunk cited for something it does not say.
4. Stream the structured response progressively; a full strategy generation is
   slow enough that section-by-section delivery is worth the complexity.
5. Persist request, context refs, prompt version and validation outcome for
   offline evaluation — this endpoint's output is unusually well shaped for
   building a golden set.
