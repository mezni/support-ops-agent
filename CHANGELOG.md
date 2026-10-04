# Changelog

## Version History

| Version | Feature Domain | Key Objectives |
|---|---|---|
| 0.0.8 | Memory Layer | Give the agent short-term conversation memory and per-customer long-term memory, and inject recalled customer context into the decision prompt |
| 0.0.7 | Knowledge Retrieval Layer | Add an in-memory knowledge base with a retriever and a search tool; enforce the `Tool` contract on all tools |
| 0.0.6 | Tool Registry & Documentation | Route agent actions through a pluggable tool registry; make the composition root explicit; bring both diagram documents up to date with the code |
| 0.0.5 | Structured Output & Test Packaging | Return typed agent decisions via OpenRouter structured output; make `tests` an importable package so shared fakes can be reused |
| 0.0.4 | Agent Domain & Documentation | Define the agent decision contract in the domain layer; document runtime behaviour with sequence diagrams |
| 0.0.3 | Configuration, Packaging & LLM Provider | Make the project installable and importable from any directory; load `.env` from the project root; fail fast on missing OpenRouter credentials; default to a zero-cost OpenRouter model |
| 0.0.2 | Planning & Scaffolding | Record the phased roadmap and initial project scaffold |
| 0.0.1 | Project Foundation | Establish src-layout package, domain models, and agent control loop |
| MVP v1 (pre-0.0.1) | MVP Prototype | Prove RAG, agent coordination, MCP, and workflow validation end to end |

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Project re-initialization complete.
- Focus on implementing the phased roadmap starting from Phase 0.

## [0.0.8] - 2026-10-03

This release adds the memory layer and wires it into the agent's decision step. The agent
now records each incoming ticket in short-term memory and reads the customer's facts,
preferences, and previous tickets back into the decision prompt.

### Added

- `support_ops/memory/` package:
  - `ConversationMessage` (`BaseModel`) with `role`, `content`, and a UTC `timestamp`
    defaulting to now.
  - `CustomerMemory` (`BaseModel`) with `customer_id`, `facts`, `preferences`,
    `previous_tickets`, and an `updated_at` default.
  - `ShortTermMemory`, an in-process `ConversationMessage` buffer with `add`,
    `get_messages`, and `clear`. `get_messages` returns a copy.
  - `LongTermMemory`, a per-customer store with `get`, `save`, `add_ticket`,
    `add_fact`, and `add_preference`.
  - `MemoryManager`, the facade the agent depends on. It routes each call to the
    appropriate store so callers never choose one: `remember_message` and
    `get_conversation` to short-term, `get_customer`, `remember_fact`, and
    `remember_ticket` to long-term.
- `SupportAgent.decide` now calls `memory.remember_message` and `memory.get_customer`
  before prompting the model.
- Prompt sections in `decide` for `Customer facts`, `Customer preferences`, and
  `Previous tickets`.
- `tests/memory/test_memory.py` covering short-term recording, long-term facts, and
  previous-ticket tracking.
- `docs/class-diagram.md` gained a memory-layer class diagram and a section documenting
  the layer's behavioural traps.
- `docs/sequence-diagram.md` gained a "Memory-augmented decision" sequence diagram
  covering the read and write halves of `decide`.

### Changed

- `SupportAgent.__init__` now requires a `MemoryManager` as its third argument. This is
  a breaking constructor change for any existing caller.
- `main` constructs a `MemoryManager` and injects it into `SupportAgent`.
- `tests/agent/test_agent.py` passes a real `MemoryManager`.
- The decision prompt now opens with "You are a support operations agent" and carries
  customer context. The action list and the explicit `Return JSON with exactly these
  fields` contract are unchanged.

### Known issues

These are documented rather than fixed, and are recorded here so they are not mistaken
for regressions later.

- **`decide` is not idempotent.** It writes to short-term memory on every call, so
  calling it twice on one ticket stores the description twice. Nothing de-duplicates on
  `ticket_id`. Roadmap Phase 3 calls `decide` inside a `while` loop, so a loop
  implementation would multiply entries. Recording on `run`, or guarding on `ticket_id`,
  would fix it.
- **`LongTermMemory.get` mutates on read.** A getter inserts an empty `CustomerMemory`
  for an unseen customer. Since `decide` calls `get_customer` for every ticket, the
  first ticket from any new customer creates a record as a side effect of reading it.
  There is no way to ask "do I know this customer?" without creating them, so unknown
  and known-but-empty are indistinguishable, and both render as `{}`.
- **`updated_at` does not track modification.** It is set once at construction and never
  refreshed, so it records creation time rather than last modification.
- **`ShortTermMemory` is unbounded.** There is no eviction and no maximum length, so the
  buffer grows with every recorded message. Roadmap Phase 6 specifies "Last 5 exchanges".
- **Memory context reaches the model as Python `repr`, not JSON.** `decide` interpolates
  the fields directly into an f-string, so the prompt contains `{'plan': 'premium'}` with
  single quotes. Models generally handle this, but `json.dumps` would emit a valid
  literal.
- **Customer memory is never populated in the running system.** `remember_fact` and
  `remember_ticket` are only exercised by tests. Nothing extracts facts or previous
  ticket ids from resolved tickets, so in a live run every customer renders as empty
  context.
- **Memory is not persisted.** Both stores are per-process, so all context is lost on
  exit. Roadmap Phase 2 specifies SQLite.
- **Memory context is untested at the agent level.** `FakeLLM` ignores its prompt, so no
  test asserts that customer facts, preferences, or previous tickets actually reach the
  model. A regression in prompt assembly would not fail any test. The behaviour was
  verified manually with a prompt-capturing fake instead.
- **`memory/` uses relative imports** where every other package uses absolute
  `from support_ops.x import y`. Not incorrect, but inconsistent.

---
## [0.0.9] - 2026-10-04

This release adds a knowledge retrieval layer and a second tool that searches it, and
corrects the tool contract so both tools are actually constrained by `Tool`.

### Added

- `support_ops/knowledge/` package:
  - `KnowledgeDocument` (`BaseModel`) with `id`, `title`, `content`, and `category`.
  - `KnowledgeStore`, an in-memory list holder exposing `all()`.
  - `seed.default_documents()` returning four hard-coded articles covering password
    reset, duplicate billing, account lockout, and refund policy.
  - `KnowledgeRetriever.search(query, limit)` returning ranked `SearchResult` records.
  - `SearchResult` (`dataclass`) pairing a `KnowledgeDocument` with a `float` score.
- `SearchKnowledgeBaseInput` (`BaseModel`) with `query` and a `limit` bounded by
  `ge=1, le=10`, plus `SearchKnowledgeBaseTool` wrapping a `KnowledgeRetriever`.
- `tests/knowledge/test_retriever.py` covering a billing-document lookup.
- `docs/class-diagram.md` and `docs/sequence-diagram.md` extended with the knowledge
  layer, a new knowledge-retrieval sequence diagram, a registered-versus-reachable tool
  comparison, and a knowledge layer class diagram.

### Changed

- `create_default_registry` now requires a `KnowledgeRetriever` and registers
  `search_knowledge_base` alongside `create_ticket`.
- `main` builds `KnowledgeStore`, `KnowledgeRetriever`, and the registry explicitly.
- `tests/agent/test_agent.py` constructs a real retriever from `default_documents()` and
  passes it to `create_default_registry`.

### Fixed

- `TypeError: create_default_registry() missing 1 required positional argument:
  'retriever'` in `tests/agent/test_agent.py`, after the factory signature changed.
- `SearchKnowledgeBaseTool` did not subclass `Tool`. Python accepts this silently
  because annotations are unchecked at runtime, so `ToolRegistry.register(tool: Tool)`
  took the object without complaint while nothing guaranteed `execute` or
  `argument_schema` existed and `ToolRegistry.list() -> list[Tool]` was inaccurate. It
  now inherits from `Tool` with no abstract methods left unimplemented.

### Known Issues

- **`search_knowledge_base` is registered but unreachable from the agent.**
  `AgentAction` has only `draft_response`, `create_ticket`, and `escalate`, and
  `execute` has no branch resolving `"search_knowledge_base"`, so the decision schema
  cannot express a knowledge lookup. The knowledge base cannot influence any decision.
  Wiring it requires both an `AgentAction.SEARCH_KNOWLEDGE_BASE` member and an `execute`
  dispatch branch. Tests are green regardless because the agent test asserts on
  `create_ticket`.
- **Retriever scoring is naive token overlap.** `score` is the size of the intersection
  of word *sets* over lowercased `title + category + content`, with no stemming, no IDF
  weighting, no normalisation, and no multiset counting, so a repeated term cannot raise
  a score and `2.0` means literally "two shared words". It matches the seed corpus
  (`customer charged twice` to KB-002, `refund policy` to KB-004) but not natural
  customer phrasing: `can't sign in` will not match the "Account Locked" document.
- **Duplicate `ToolResult` types.** `agent/tools.py` still defines an unrelated
  `@dataclass ToolResult` and a `create_ticket` function. Nothing imports it any more, so
  it remains dead code, but `from support_ops.agent.tools import ToolResult` still
  succeeds and yields a differently-shaped object than
  `from support_ops.tools.base import ToolResult`.
- `TicketClassifier.classify` (`classifier.py:39`) still raises `NotImplementedError`
  and still calls `llm.chat` rather than `llm.structured`. Its prompt is already
  correct, so the fix is a one-line change. It is not constructed by `main`.
- `SupportAgent.execute` is partial: only `CREATE_TICKET` invokes a tool, and the
  declared return type is `ToolResult | str`, so callers must type-check before reading
  `.success`.
- **`ToolResult.data` shape is inconsistent between tools.** `create_ticket` returns
  flat keys (`ticket_id`, `customer_id`); `search_knowledge_base` returns a single
  nested `results` list of dicts. Consumers must special-case per tool.
- `CreateTicketTool` fabricates a constant ticket id `T-NEW-001` and persists nothing.
- Tools are never advertised to the model. The `AgentAction` enum and the
  `ToolRegistry` are maintained separately and can drift apart with no test failing.
- `poolside/laguna-s-2.1:free` selected `escalate` for every ticket tried, including
  unambiguous duplicate-billing cases, so `main` usually prints a placeholder string
  rather than exercising tool execution. Exercise `execute` with an explicit
  `AgentDecision` to test dispatch independently of model judgement.
- `tests/knowledge/` and `tests/tools/` have no `__init__.py`, unlike `tests/agent/` and
  `tests/domain/`. Collection works only because no other test module shares those
  basenames; a duplicate basename elsewhere would cause an import mismatch.
- `ruff check` reports 5 findings, 4 auto-fixable: unused `pydantic.Field` in
  `domain/ticket.py`, unused `IncomingTicket` in `tests/domain/test_ticket.py`, unused
  `result` local in `classifier.py`, and import sorting in `llm.py` and
  `tests/agent/test_agent.py`.

## [0.0.6] - 2026-10-02

This release introduces a pluggable tool registry that agent actions dispatch through,
makes `main` an explicit composition root, and brings both diagram documents in line
with the code.

### Added

- `support_ops/tools/` package:
  - `Tool` (ABC) declaring `name`, `description`, `execute`, and `argument_schema`.
  - `ToolResult` (`BaseModel`) with `success`, `message`, and optional `data`.
  - `ToolRegistry` with `register`, `get`, and `list`.
  - `create_default_registry()` module-level factory registering `CreateTicketTool`.
  - `CreateTicketInput` and `CreateTicketTool`, whose input fields carry `Field`
    descriptions.
- `SupportAgent.run(ticket)`, composing `decide` then `execute`.
- `docs/class-diagram.md`: class diagrams for the full type graph, the tool layer, and
  the domain layer, plus a module status table and known gaps.

### Changed

- `SupportAgent.execute` now resolves `create_ticket` through the injected
  `ToolRegistry` and builds a validated `CreateTicketInput` from
  `tool.argument_schema()`, instead of calling a module-level function directly.
- `SupportAgent.__init__` now requires `tools: ToolRegistry`.
- `main` builds the registry and agent explicitly, making it the composition root.
- The `decide` prompt now states the expected JSON shape with an explicit
  `Return JSON with exactly these fields` block, matching the pattern already used in
  `classifier.py`.
- `tests/agent/test_agent.py` constructs the agent with `create_default_registry()` and
  asserts on `result.data["customer_id"]` rather than `result.message`, since
  `CreateTicketTool` reports the customer in `data` and a constant ticket id in
  `message`.
- `docs/sequence-diagram.md` rewritten for the registry-based flow: full agent run, tool
  dispatch detail, the structured output contract including its failure branches, and
  the composition root.

### Fixed

- `NameError: name 'ToolRegistry' is not defined` on import of
  `support_ops.tools.registry`. `create_default_registry` was indented inside the class
  body, so its `-> ToolRegistry` return annotation was evaluated before the name was
  bound. It is now a module-level function, matching the call site in `main`.
- `ValidationError: Invalid JSON` from `SupportAgent.decide` against the live API. The
  prompt asked only for "a short reason" and did not state the JSON contract, so
  `poolside/laguna-s-2.1:free` replied with Markdown prose (`**Chosen action:**
  escalate`). `response_format` alone does not constrain this model.

### Known Issues

- **Duplicate `ToolResult` types.** `agent/tools.py` still defines an unrelated
  `@dataclass ToolResult` and a `create_ticket` function, while `tools/base.py` defines
  the pydantic `ToolResult` actually in use. The two are different classes; nothing
  imports `agent/tools.py` any more, so it is dead code that makes
  `from support_ops.agent.tools import ToolResult` succeed with a different shape than
  `from support_ops.tools.base import ToolResult`.
- `TicketClassifier.classify` (`classifier.py:39`) still raises `NotImplementedError`
  and still calls `llm.chat` rather than `llm.structured`. Its prompt is already
  correct, so the fix is a one-line change. It is not constructed by `main`.
- `SupportAgent.execute` is partial: only `CREATE_TICKET` invokes a tool.
  `DRAFT_RESPONSE` and `ESCALATE` return placeholder strings, and the declared return
  type is `ToolResult | str`, so callers must type-check before reading `.success`.
- `CreateTicketTool` fabricates a constant ticket id `T-NEW-001` and persists nothing.
- Tools are never advertised to the model. The `AgentAction` enum and the
  `ToolRegistry` are maintained separately and can drift apart. See 0.0.7, where
  registering a second tool made the drift concrete.
- `poolside/laguna-s-2.1:free` selected `escalate` for every ticket tried, including
  unambiguous duplicate-billing cases, so `main` usually prints a placeholder string
  rather than exercising tool execution. Exercise `execute` with an explicit
  `AgentDecision` to test dispatch independently of model judgement.
- `ruff check` reports 5 findings, 4 auto-fixable: unused `pydantic.Field` in
  `domain/ticket.py`, unused `IncomingTicket` in `tests/domain/test_ticket.py`, unused
  `result` local in `classifier.py`, and import sorting in `llm.py` and
  `tests/agent/test_agent.py`.

## [0.0.5] - 2026-10-02

This release replaces the placeholder agent decision with real structured output from
OpenRouter, and makes `tests` an importable package so test doubles can be shared.

### Added

- `LLMClient.structured(user_message, output_model)`, generic over
  `TypeVar("T", bound=BaseModel)`. Calls `chat.completions.parse` with
  `response_format=output_model` and raises `ValueError` when the model returns no
  parsed object.
- `tests/__init__.py`, `tests/agent/__init__.py`, and `tests/domain/__init__.py`,
  making `tests` a regular package.
- `tests/agent/fakes.py` with a `FakeLLM` test double implementing `structured`, so
  agent tests do not require network access.

### Changed

- `SupportAgent.decide` now returns a typed `AgentDecision` via `llm.structured`
  instead of raising `NotImplementedError`. The prompt no longer requests raw JSON
  directly, relying on `response_format` for schema enforcement.
- `tests/agent/test_agent.py` uses the shared `FakeLLM` and now exercises
  `decide` in addition to `execute`.

### Fixed

- `ModuleNotFoundError: No module named 'tests'` during collection. `tests` had no
  `__init__.py`, so the dotted `tests.agent.fakes` import could not resolve.

### Known Issues

- **The agent decision path fails against the live API.** Verified against
  `poolside/laguna-s-2.1:free`: `SupportAgent.decide` raises
  `ValidationError: Invalid JSON: expected value at line 1 column 1` because the model
  returns Markdown prose (`**Action:** create_ticket ...`) instead of JSON. The unit
  test passes only because `FakeLLM` bypasses the transport entirely, so this is not
  covered by CI.
- Root cause is the prompt: `agent.py:19-40` no longer states the expected JSON shape.
  Re-adding an explicit `Return JSON with exactly these fields` block made the same
  live call succeed and return a validated `AgentAction.DRAFT_RESPONSE`. Relying on
  `response_format` alone is not sufficient for this model.
- `TicketClassifier.classify` (`classifier.py:39`) still raises
  `NotImplementedError` unconditionally and still calls `llm.chat` rather than
  `llm.structured`, so it is subject to the same failure above.
- `docs/sequence-diagram.md` was **stale** at this release: it stated that
  `SupportAgent.decide` raises `NotImplementedError` and that only `execute` is
  functional. Both were true at 0.0.4 but no longer hold. Corrected in 0.0.6.
- `ruff check` reports 3 pre-existing findings unrelated to this release: an unused
  `pydantic.Field` import in `domain/ticket.py`, an unused `IncomingTicket` import in
  `tests/domain/test_ticket.py`, and an unused `result` local in
  `src/support_ops/classifier.py`.

## [0.0.4] - 2026-10-02

This release adds the missing agent decision types to the domain layer and documents
the runtime with sequence diagrams.

### Added

- `AgentAction` (`StrEnum`) with `DRAFT_RESPONSE`, `CREATE_TICKET`, and `ESCALATE`,
  matching the action strings requested by the agent prompt in `agent.py`.
- `AgentDecision` (pydantic model) with `action: AgentAction` and `reason: str`.
  Verified that `AgentDecision.model_validate` parses the raw model string
  `"create_ticket"` into the enum and serializes back to JSON unchanged.
- `docs/sequence-diagram.md`: Mermaid sequence diagrams for configuration resolution,
  the inference path, agent tool dispatch, the unimplemented decision paths, and the
  outstanding wiring gap, plus a per-module status table.

### Fixed

- `ImportError: cannot import name 'AgentAction'` raised during test collection of
  `tests/agent/test_agent.py`. `agent.py` and the test both imported `AgentAction` and
  `AgentDecision` from `support_ops.domain.ticket`, but neither type existed anywhere in
  the repository, so the agent package could not be imported at all.

### Known Issues

- `TicketClassifier.classify` (`classifier.py:39`) still raises `NotImplementedError`
  unconditionally. See 0.0.6 for the live-API structured output failure that affected
  it once implemented.
- `ruff check` reports 3 pre-existing findings unrelated to this release: an unused
  `pydantic.Field` import in `domain/ticket.py`, an unused `IncomingTicket` import in
  `tests/domain/test_ticket.py`, and an unused `result` local in
  `src/support_ops/classifier.py`.

## [0.0.3] - 2026-10-02

This release makes the project properly installable, hardens configuration loading so
it works from any working directory, and switches local development to a zero-cost
OpenRouter model.

### Added

- `Settings._require_credentials` validator that raises an actionable error naming the
  missing variables and the resolved `.env` path, instead of letting an empty value
  reach the OpenAI client as `Missing credentials`.
- Version History table summarizing each release by feature domain and key objectives.
- `[build-system]` using `hatchling`, plus `[tool.hatch.build.targets.wheel]` with
  `packages = ["src/support_ops"]`, so uv installs the project as an editable package
  instead of a dependency-only virtual project.
- `[tool.pytest.ini_options]` with `testpaths = ["tests"]`.
- `[tool.ruff]` with `src = ["src", "tests"]`.

### Changed

- `Settings.model_config.env_file` now resolves to the project root via
  `Path(__file__).resolve().parents[2]` rather than the current working directory, so
  configuration loads correctly when invoked from `src/` or any other directory.
- `OPENROUTER_MODEL` defaults to `poolside/laguna-s-2.1:free` in `.env` and
  `.env.example`. OpenRouter free models require the `:free` suffix; verified
  `cost: 0`. Rejected alternatives: `google/gemma-4-*:free` (429, free tier at
  capacity), `thinkingmachines/inkling:free` (403, agentic harnesses only),
  `nvidia/nemotron-3-super-120b-a12b:free` (consumes `max_tokens` on reasoning,
  returning `content: null`).

### Fixed

- Resolved `ValidationError` for `openrouter_api_key` / `openrouter_model` when the
  working directory was not the project root.
- `ModuleNotFoundError: No module named 'support_ops'` during test collection and from
  the project root. Without a build backend the package was never installed into the
  venv, so imports only resolved when the working directory happened to be `src/`.

## [0.0.2] - 2026-10-01

### Added

- Project roadmap documentation (`docs/roadmap.md`).
- Initial project scaffold.

## [0.0.1] - 2026-10-02

This release establishes the project foundation: the src-layout package, the
support-ticket domain models, and the agent control loop.

### Added

- Project foundation: `pyproject.toml`, `src/support_ops/`, `.env.example`.
- Basic LLM application structure (`src/support_ops/llm.py`, `src/support_ops/main.py`).
- Support-ticket domain models (`src/support_ops/domain/ticket.py`).
- Agent control loop implementation (`src/support_ops/agent/agent.py`).
- Structured agent decisions.

### Removed

- Previous codebase and implementation artifacts were removed during the cleanup phase to facilitate a fresh start based on the roadmap.

## MVP v1 (pre-0.0.1) - 2026-09-04

Prototype work that preceded the current codebase. Retained for reference; the
implementation was later removed during the cleanup phase recorded in 0.0.1.

### Added

- Initial MVP v1 prototype development:
  - RAG implementation (`Add RAG` commit).
  - LLM client integration (`Add llm client`).
  - Core agent functionalities (`Add agents`, `Add agents coordinator`).
  - MCP (Meta-Cognitive Processing) concepts (`Add MCP`).
  - Workflow validation (`Add workflow validator`).
  - Dockerization (`Add docker`).
- Updated documentation for MVP v1 (`Update docs for mvp v1`).

## [0.0.9] - 2026-10-04 (evaluation architecture)

This release adds the evaluation architecture for regression testing agent behavior.

### Added

- `support_ops/evaluation/` package:
  - `__init__.py` — exports `EvaluationCase`, `EVALUATION_CASES`, `EvaluationMetrics`, `calculate_accuracy`, `EvaluationRunner`
  - `cases.py` — `EvaluationCase` dataclass and golden dataset of 4 tickets (duplicate_billing, account_locked, security_incident, general_question)
  - `metrics.py` — `EvaluationMetrics` dataclass with `total`, `passed`, `accuracy` property; `calculate_accuracy(expected, actual)` helper
  - `runner.py` — `EvaluationRunner` class that runs `agent.run(ticket)` against cases and counts passed cases
- `tests/evaluation/` package:
  - `test_cases.py` — 7 tests: dataset non-empty, case fields, metrics total/accuracy, calculate_accuracy (perfect/partial/empty)
  - `test_metrics.py` — 3 tests: perfect accuracy, partial accuracy, empty accuracy
- Evaluation architecture documentation in `docs/class-diagram.md` and `docs/sequence-diagram.md`
- Separation of concerns: production agent (`agent/agent.py`) is decoupled from evaluation logic; `EvaluationRunner` takes an `agent` argument

### Changed

- (no changes from previous 0.0.9 entry)

### Known Issues

- (no new issues from evaluation architecture)
