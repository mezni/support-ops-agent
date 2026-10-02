# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Project re-initialization complete.
- Focus on implementing the phased roadmap starting from Phase 0.

## [0.1.0] - 2026-10-02

This release marks the re-initialization of the project with a focus on the phased roadmap.

### Added

- Project foundation: `pyproject.toml`, `src/support_ops/`, `.env.example`.
- Basic LLM application structure (`src/support_ops/llm.py`, `src/support_ops/main.py`).
- Support-ticket domain models (`src/support_ops/domain/ticket.py`).
- Agent control loop implementation (`src/support_ops/agent/agent.py`).
- Structured agent decisions.

### Removed

- Previous codebase and implementation artifacts were removed during the cleanup phase to facilitate a fresh start based on the roadmap.

## [0.0.2] - 2026-10-01

### Added

- Project roadmap documentation (`docs/roadmap.md`).
- Initial project scaffold.

## [0.0.1] - 2026-09-04

### Added

- Initial MVP v1 prototype development:
  - RAG implementation (`Add RAG` commit).
  - LLM client integration (`Add llm client`).
  - Core agent functionalities (`Add agents`, `Add agents coordinator`).
  - MCP (Meta-Cognitive Processing) concepts (`Add MCP`).
  - Workflow validation (`Add workflow validator`).
  - Dockerization (`Add docker`).
- Updated documentation for MVP v1 (`Update docs for mvp v1`).
