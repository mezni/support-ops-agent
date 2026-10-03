# Changelog

## Version History

| Version | Feature Domain | Key Objectives |
|---|---|---|
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
  `ToolRegistry` are maintained separately and can drift apart.
- `poolside/laguna-s-2.1:free` selected `escalate` for every ticket tried, including
  unambiguous duplicate-billing cases, so `main` usually prints a placeholder string
  rather than exercising tool execution. Exercise `execute` with an explicit
  `AgentDecision` to test dispatch independently of model judgement.
- `tests/tools/` has no `__init__.py`, unlike `tests/agent/` and `tests/domain/`.
  Collection works only because no other test module shares the basename
  `test_create_ticket`; a duplicate basename elsewhere would cause an import mismatch.
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
