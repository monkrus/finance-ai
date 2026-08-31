# Task 1 — Architecture Review

Written as the incoming Lead AI Engineer, after reading the backend end to end.
Ordered by what I would fix first, which is not the same as what is most
interesting. The first three are things I would want closed before the next
production release; the rest are the difference between a demo and a system you
can operate.

A note on the codebase before the criticism: the bones are good. There is a real
gateway abstraction, a provider interface, a tool registry, a prompt manager and
a hybrid retriever. Most of what follows is about closing the gap between
abstractions that exist and abstractions that are actually load-bearing.

---

## 1. Tool execution has no authorization context

**Current limitation.** `app/api/v1/ai.py` is careful about identity: it
namespaces the conversation key with `scoped_session_id(user_id, session_id)`
and comments that "the client cannot forge another user's namespace." That care
stops at the gateway boundary. Every portfolio tool in `app/agents/tools.py`
takes `portfolio_id` as a model-supplied argument and queries on it directly:

```python
async def portfolio_cb(portfolio_id: int):
    async with AsyncSessionLocal() as db:
        engine = PortfolioEngine(market_data_service=md_service)
        return (await engine.get_portfolio_analytics(db, portfolio_id)).model_dump()
```

There is no `user_id` filter anywhere in that path. The argument comes from the
LLM's function call, which is a function of the user's text. So "show me
portfolio 7" reads portfolio 7 regardless of who owns it, and no jailbreak is
required — the model helpfully passing through a number the user typed is
sufficient. `SafetyFilter` will not catch it; its patterns are about prompt
injection phrasing, not authorization. The same shape applies to
`portfolio_news`, `portfolio_risk`, `portfolio_allocation`,
`portfolio_performance`, `portfolio_summary` and `portfolio_recommendations`.

This is a horizontal privilege escalation (IDOR) reachable through natural
language, in an application whose entire data set is people's finances.

**Proposed solution.** Authorization must not be an argument the model can
choose. Two layers:

1. Give the tool registry an execution context. `execute_tool(name, args)`
   becomes `execute_tool(name, args, context: ToolContext)`, where `ToolContext`
   carries the authenticated `user_id` and is constructed in the API layer from
   the JWT — never from model output. Callbacks that need identity declare it,
   and the registry injects it, stripping any `user_id` the model tried to
   supply.
2. Push ownership into the data layer as defence in depth. `PortfolioEngine`
   methods take `user_id` and filter on it, so a missed check at the call site
   returns 404 rather than someone else's holdings.

Tools can additionally be marked with a required scope (`reads_user_data`,
`writes`, `public`) so an agent's `allowed_tools` list is checked against the
caller's permissions, not just the agent's config.

The new `/agents/investment-strategy` endpoint demonstrates the target shape:
`InvestmentContextBuilder.assert_portfolio_owned_by` runs before any holding is
read, and returns 404 rather than 403 so the endpoint does not confirm the
existence of other users' portfolio ids.

**Expected benefits.** Closes the escalation path. Makes authorization
reviewable in one place instead of sixteen callbacks. Lets tools be added by
people who are not thinking about tenancy that day.

**Trade-offs.** Touches every registered tool and the registry signature —
mechanical but wide. Injected context makes callbacks marginally harder to test
in isolation, which a `ToolContext.system()` factory offsets. Some genuinely
public tools (`calculator`, `get_stock_quote`) gain a parameter they ignore;
that is a small price for a uniform signature.

---

## 2. Prompt versioning is nominal, not real

**Current limitation.** `PromptTemplate` has a `version` field and
`PromptManager.register` writes two keys for every template:

```python
self._templates[f"{template.name}:{template.version}"] = template
self._templates[template.name] = template
```

Every read path in the codebase calls `render(name)` without a version, so it
resolves the bare key — which is whatever registered last. Registration happens
at import time across several modules (`register_agent_prompts`,
`RAGEngine._register_prompts`), so the effective prompt set depends on import
order. Two templates sharing a name silently overwrite each other with no
warning. There is no way to answer "which prompt produced this output," which
means a prompt regression cannot be attributed after the fact, and a prompt
change cannot be rolled back without a deploy.

**Proposed solution.** Make the version a required part of resolution and move
prompts out of Python:

- Store templates as versioned files (`prompts/agent_investment_strategy/1.2.0.yaml`)
  with frontmatter for model constraints, expected variables and an owner.
  Load at startup; validate that declared `variables` match the placeholders in
  the body so a rename fails at boot rather than at request time.
- `register` refuses to overwrite an existing `name:version` and logs loudly on
  collision.
- Resolution goes through a pinned alias per environment (`production`,
  `canary`) rather than "latest," so shipping a prompt is a config change with
  an audit trail.
- Emit the resolved `prompt_name`, `prompt_version` and a hash of the rendered
  system text on every generation, and store them with the response record.

**Expected benefits.** Prompt changes become reviewable, attributable and
revertible without a deploy. A/B and canary comparisons become possible because
you can join outcomes to prompt versions. Removes an entire class of
"why did behaviour change" investigations.

**Trade-offs.** Prompts in files lose IDE refactoring and type checking. A
loader plus validation is real work. Pinned versions add a step to shipping a
prompt fix, which is friction exactly when someone wants to move fast — worth it,
but it needs a documented fast path for incidents.

---

## 3. No evaluation framework

**Current limitation.** There are no tests in the repository at all — the CI
workflow runs `python -m pytest` against nothing. For an LLM system that is worse
than it sounds, because the failure mode is not a crash. A prompt edit, a model
version bump on the provider side, or a retrieval tweak degrades answer quality
silently, and nobody finds out until a user complains. The financial domain
raises the stakes: a plausible, well-formatted, wrong allocation recommendation
reads exactly like a correct one.

There is also no way to justify any of the changes in this document with
evidence. "Add reranking" is an opinion until there is a number attached.

**Proposed solution.** Three tiers, cheapest first:

1. **Deterministic unit tests** over everything that is not the model: context
   assembly, citation validation, chunk boundaries, retrieval fusion, tool
   authorization. This is where most correctness actually lives and it costs
   nothing per run. (The suite added for Task 2 is the starting point — 19 tests
   covering ownership, degradation, tenant scoping and grounding validation.)
2. **A golden dataset** of 100–200 realistic queries per surface, with reference
   answers and the documents they should retrieve. Run nightly. Score retrieval
   with context precision / recall and generation with faithfulness and answer
   relevance (LLM-as-judge with a stronger model, calibrated against ~50
   human-labelled examples so the judge itself is validated).
3. **Regression gates in CI** on the fast subset: block a merge if faithfulness
   or retrieval recall drops more than a set margin against the current
   production prompt version.

Add adversarial cases deliberately: questions whose answer is not in the corpus
(the correct response is a refusal), questions where two documents disagree, and
prompt-injection strings embedded in uploaded filings.

**Expected benefits.** Turns prompt and retrieval work from opinion into
measurement. Catches provider-side model drift, which is otherwise invisible.
Makes it safe for more than one engineer to touch the prompts.

**Trade-offs.** Building and maintaining the golden set is the real cost, and it
decays as the product changes — budget for curation, not just creation.
LLM-as-judge costs money per run and has its own bias; it needs periodic
recalibration. Nightly evals against a paid API are a recurring line item.

---

## 4. Model routing is single-provider, single-model, and unaware of cost

**Current limitation.** `AIGatewayService.__init__` hardcodes
`GeminiProvider()`, and `GeminiProvider` hardcodes `gemini-2.5-flash` as
`default_model`. The `AIProviderInterface` abstraction exists but has exactly one
implementation and no selection mechanism, so it does not currently buy anything.
Every call — a two-token intent classification, a 6k-token strategy synthesis —
goes to the same model at the same settings.

Two consequences. Operationally, a Gemini outage or quota exhaustion takes down
every AI surface at once with no failover; `tenacity` retries three times against
the same endpoint, which does not help when the endpoint is the problem.
Economically, classification and synthesis have wildly different quality
requirements and are billed identically.

`AgentConfig.temperature` is set thoughtfully on all six agents (0.6 for
portfolio advisor, 0.7 for advisor) and then never read — `BaseAgent.chat` does
not pass it, and `generate_content` uses its own default of 0.7. Configuration
that looks like it works but does not is worse than no configuration.

**Proposed solution.** A routing layer inside the gateway, keyed on a declared
task profile rather than on the call site:

- Each call declares its requirements (`task=classification|synthesis|extraction`,
  latency budget, whether tools or JSON are needed). A routing policy maps that
  to a concrete `(provider, model, params)` tuple from config.
- Fallback chains per task: primary → secondary provider → cached or degraded
  response. Circuit-break a provider after N consecutive failures instead of
  retrying into a wall.
- Honour `AgentConfig.temperature` — either wire it through `BaseAgent.chat` or
  delete the field. Live configuration should be one or the other.
- Route the cheap paths cheaply: intent classification is a Flash-class job or,
  better, a small classifier that does not need an LLM round trip at all.

**Expected benefits.** Survives a single-provider outage. Cuts spend on
high-volume low-difficulty calls. Makes "should we use a bigger model here" an
experiment rather than a rewrite.

**Trade-offs.** Multi-provider means normalising tool-calling semantics, token
accounting and safety behaviour across APIs that differ in all three —
the abstraction leaks and maintaining it is ongoing work. Behaviour becomes less
predictable when the same prompt can hit different models, which makes evals
(#3) a prerequisite rather than a nice-to-have.

---

## 5. Observability is log lines, not telemetry

**Current limitation.** `MetricsTracker` accumulates counters on an instance
attribute and writes a log line per call. Because gateways are constructed at
module import (`api/v1/ai.py`, `api/v1/documents.py`), the counters are
per-process and per-instance, they reset on restart, they are not aggregated
across workers, and nothing reads them. `COST_PER_1K` has one hardcoded entry.
Tool latency is tracked in `chat` but not in `chat_stream`, and the streaming
path never calls `metrics.track` at all, so streamed traffic is invisible in
both token and cost terms.

There is no request correlation: a single user turn can fan out to an intent
classification, a generation, several tool calls and a RAG query, and there is no
id tying those together. When a user says "the assistant gave me a strange
answer at 14:20," reconstructing what happened means grepping.

**Proposed solution.** Structured traces over counters:

- OpenTelemetry spans for the whole turn, with child spans for classification,
  retrieval, each tool call and each generation. Attributes: `trace_id`,
  `user_id` (hashed), `agent`, `prompt_name`, `prompt_version`, `model`,
  `tokens_in/out`, `latency`, `finish_reason`, `retrieval_hit_count`,
  `grounding_ratio`.
- Export cost as a first-class metric derived from per-model pricing held in
  config, not in a dict in the code, with per-user and per-agent dimensions.
- Persist a sampled record of `(prompt version, retrieved chunk ids, response,
  validation outcome)` for offline analysis — this doubles as the raw material
  for the golden dataset in #3.
- Alert on the things that actually signal AI failure: grounding ratio dropping,
  refusal rate spiking, retrieval returning zero chunks, p95 latency, cost per
  user per day.

**Expected benefits.** Makes individual bad answers debuggable after the fact.
Turns cost from a monthly surprise into a monitored metric with attribution.
Provides the evidence base for every other optimisation here.

**Trade-offs.** Tracing adds per-call overhead and a collector to operate.
Storing prompts and responses for analysis is a privacy decision, not just an
engineering one — it needs field-level redaction, a retention policy and a
lawful basis, particularly for financial data.

---

## 6. Conversation memory truncates instead of remembering

**Current limitation.** `MemoryManager.compress_context_if_needed` is named for
compression but implements truncation: when the window exceeds 4000 tokens it
`ltrim`s to the most recent messages that fit. The older turns are gone from
Redis permanently, not summarised. In a long financial planning conversation
this is precisely backwards — the user's goals, constraints and risk tolerance
are stated early and referenced throughout, so the first thing dropped is the
context that matters most for the rest of the session.

Token estimation tries `tiktoken` (not in `requirements.txt`, so it always
raises) and falls back to `len(text) // 4`, which is a rough approximation for a
Gemini tokenizer. The 4000-token ceiling is also very conservative against
current context windows.

`BaseAgent._get_namespaced_session` prefixes memory keys with the agent name, so
switching agents mid-conversation silently starts a fresh history — the router
can hand you to a different agent between turns and the new one has no idea what
you just said.

**Proposed solution.** Layered memory:

- **Working memory**: recent turns verbatim, as now.
- **Summary memory**: when the window fills, summarise the evicted turns into a
  running digest and prepend it, rather than deleting them.
- **Profile memory**: extract durable facts (risk tolerance, horizon, goals,
  constraints) into a structured per-user record that is injected into every
  session regardless of window pressure. In this product that record is also the
  investment profile the strategy agent needs, which is why the Task 2 endpoint
  takes it as typed input rather than hoping it survived in the chat window.
- Share conversation history across agents within a session and scope only the
  agent-specific scratch space, so routing is invisible to the user.
- Use the provider's real token counter, and pin the ceiling to the model's
  context window from config.

**Expected benefits.** Long conversations stop losing their premise. Cross-agent
handoff becomes coherent. Structured profile facts are reusable outside chat.

**Trade-offs.** Summarisation costs an extra LLM call at eviction time and can
itself introduce errors — a summary that drops a stated constraint is a
grounding failure with a long half-life. Durable per-user profile storage is
personal financial data with retention, correction and deletion obligations.

---

## 7. Semantic caching (cost, with a caveat)

**Current limitation.** Nothing is cached. Identical or near-identical questions
regenerate from scratch — "explain diversification" from a hundred users is a
hundred paid generations of substantially the same answer. Market-data providers
are called per holding per request with no memoisation, so a portfolio review
re-fetches the same profiles and ratios every time.

**Proposed solution.** Cache by layer, because the layers have different
invalidation rules:

- **Exact-match cache** on `(prompt_version, model, normalised input, tool
  results)` for deterministic paths — cheap and safe.
- **Semantic cache** for educational content: embed the query, return a cached
  answer above a similarity threshold. Restrict it to the tutor/education
  surfaces where answers are user-independent.
- **Do not semantically cache anything user-scoped or market-dependent.** A
  strategy grounded in one user's holdings must never be served to another, and
  a near-miss on a ticker is a wrong answer, not a slightly stale one. This is
  the caveat that matters more than the feature.
- Cache the provider layer separately with short TTLs keyed by data volatility:
  company profiles for hours, quotes for seconds.

Key every entry on prompt version and model so a prompt change invalidates
cleanly.

**Expected benefits.** Meaningful cost and latency reduction on the highest
volume, lowest-value traffic. Reduced market-data provider spend and rate-limit
pressure.

**Trade-offs.** Semantic caching trades correctness for cost at the threshold,
and the failure mode is a confidently wrong answer to a subtly different
question — in finance that is a serious risk, which is why the scope above is
narrow. Cache infrastructure and invalidation are real complexity. Cached
responses complicate evaluation and tracing unless explicitly marked.

---

## 8. Guardrails are regex, and the output side is empty

**Current limitation.** `SafetyFilter.validate_input` matches four literal
phrases (`ignore previous instructions`, `system prompt`, ...). It blocks the
naive attack and nothing else — any rephrasing, encoding, or non-English
equivalent passes. Meanwhile `system prompt` as a banned substring will reject
legitimate questions from developers testing the product.

More importantly it filters the wrong channel. The dangerous injection surface
here is not the chat box; it is the document upload. Uploaded filings are
chunked, embedded, retrieved and pasted into the model's context, and they are
never checked. An instruction embedded in a PDF is a direct path into the prompt.

`validate_output` only substitutes a message for empty text. There is no check
that financial advice carries disclosure, no PII leak check on the way out, no
grounding check. For a regulated domain that is the side that matters most.

**Proposed solution.**

- Treat retrieved content as untrusted data, always. Delimit it structurally,
  instruct the model that context is data and never instruction, and scan chunks
  at ingestion for injection patterns — quarantine rather than index on a hit.
- Replace phrase matching with a layered input check: cheap heuristics first,
  then a small classifier for adversarial intent, with the decision logged and
  reviewable rather than a hard 403 the user cannot appeal.
- Build the output guardrails that are currently missing: grounding validation
  (does every factual claim resolve to retrieved context?), PII egress scanning,
  required-disclosure checks on advice-shaped output, and a
  prohibited-claims check for guarantees or price predictions.
- Make refusal a designed response, not an exception. The current behaviour
  raises a 403 with "Unsafe input detected," which is hostile when the trigger is
  a false positive.

The Task 2 endpoint implements the grounding half of this concretely:
`validate_against_context` drops findings whose citations do not resolve, and
caps the reported confidence when it has to. See
[03-rag-review.md](03-rag-review.md).

**Expected benefits.** Closes the realistic injection path (documents). Reduces
false-positive rejections of ordinary questions. Provides evidence of controls,
which for financial advice is a compliance requirement rather than a preference.

**Trade-offs.** Classifier-based filtering adds latency and cost to every
request, and has its own error rate in both directions. Output validation can
suppress correct answers when the validator is wrong, so it needs its own
metrics. Guardrails are an ongoing arms race, not a milestone.

---

## 9. Composition by module-level import

**Current limitation.** `api/v1/documents.py` constructs a gateway, vector
store, embedder, retriever, RAG engine, parser and chunker at import time.
`api/v1/ai.py` constructs a second gateway and a market data service at import
time, then does `from app.api.v1.documents import rag_engine` to borrow the
first module's object. `AgentRouter` instantiates all agents in its constructor,
and `register_all_tools` runs as an import side effect.

Consequences: two `GeminiProvider` instances with independent metrics; the
in-memory vector store is process-local, so uploads land in one worker and are
invisible from the others; import order is load-bearing; nothing can be
substituted in a test without monkeypatching module globals; and a failure
during service construction is an import error at startup rather than a handled
condition.

**Proposed solution.** Move construction into FastAPI's dependency system with
lifespan-scoped singletons — one gateway per process, injected explicitly, with
`app.dependency_overrides` available for tests. Replace the in-memory vector
store with a real backing store (see [03-rag-review.md](03-rag-review.md)) so
multi-worker deployment stops being incidentally broken. The new agents router
shows the pattern with `get_investment_strategy_agent` as an overridable
dependency, which is how its endpoint tests run without touching the DB.

**Expected benefits.** Testability, honest metrics, correct behaviour under
multiple workers, and startup failures that surface as health-check failures
rather than import tracebacks.

**Trade-offs.** Refactoring the existing routers touches most of the API layer.
Explicit dependency wiring is more verbose than module globals.

---

## 10. Agent orchestration is a single classification hop

**Current limitation.** `AgentRouter._detect_intent` makes an LLM call per turn
to pick one of six agents, then hands off completely. That costs a full round
trip of latency before any useful work begins, and it is brittle: on any
exception, or confidence below 0.5, everything falls back to
`RESEARCH_ASSISTANT` — the weakest agent, with the vaguest prompt.

The chosen agent then gets one shot. `AIGatewayService.chat` executes one round
of tool calls and re-prompts once; if the model needs a second round (look up a
ticker, then fetch its filings) it cannot. Multi-step financial reasoning is
exactly the case that needs iteration.

`PortfolioAdvisorAgent` illustrates the drift this permits: `allowed_tools=[]`
and a prompt reading "Portfolio data integration is coming later, so rely on
theoretical allocation best practices for now" — while six working portfolio
tools sit registered in `tools.py`. An agent is confidently giving portfolio
advice with no access to the portfolio, and nothing in the system notices.

**Proposed solution.**

- Replace the LLM classification hop with an embedding-based classifier over
  labelled examples: much cheaper, lower latency, and improvable with data
  rather than prompt fiddling. Keep an LLM tiebreak for genuinely ambiguous
  input only.
- Give the gateway a bounded tool-calling loop (max iterations, max wall clock,
  max cost) instead of a single re-prompt.
- Make agent capability declarative and validated at startup: an agent whose
  prompt claims a capability must declare the tools that back it, and a config
  referencing an unregistered tool fails the boot.
- Audit the six existing agents against their prompts — `PortfolioAdvisorAgent`
  should either get the portfolio tools or be removed.

**Expected benefits.** Lower latency and cost per turn. Multi-step questions get
answered instead of half-answered. Capability drift becomes a startup failure
rather than a plausible-sounding wrong answer.

**Trade-offs.** A trained classifier needs labelled data and a retraining path.
Iterative tool loops need hard budget limits or they will occasionally run away
— cost ceilings become a correctness concern.

---

## Sequencing

If I could only do three before the release: **#1** (authorization — it is a
live vulnerability), **#3** (evaluation — nothing else is verifiable without it)
and **#5** (observability — nothing else is debuggable without it). #2 and #9
are cheap and unblock the rest. #4, #6, #7, #8 and #10 are the following
quarter's work, and #4 in particular should not ship before #3 exists to measure
it.
