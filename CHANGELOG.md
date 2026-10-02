# Changelog

## Version History

| Version | Feature Domain | Key Objectives |
|---|---|---|
| 0.0.3 | Configuration, Packaging & LLM Provider | Make the project installable and importable from any directory; load `.env` from the project root; fail fast on missing OpenRouter credentials; default to a zero-cost OpenRouter model |
| 0.0.2 | Planning & Scaffolding | Record the phased roadmap and initial project scaffold |
| 0.0.1 | Project Foundation | Establish src-layout package, domain models, and agent control loop |
| MVP v1 (pre-0.0.1) | MVP Prototype | Prove RAG, agent coordination, MCP, and workflow validation end to end |

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Project re-initialization complete.
- Focus on implementing the phased roadmap starting from Phase 0.

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

### Known Issues

- `ruff check` reports 3 pre-existing findings unrelated to this release: an unused
  `pydantic.Field` import in `domain/ticket.py`, an unused `IncomingTicket` import in
  `tests/domain/test_ticket.py`, and an unused `result` local in
  `src/support_ops/classifier.py`.

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
