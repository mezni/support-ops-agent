# support-ops-agent

An AI agent that autonomously handles customer support tickets.

## Project Overview

This project aims to build an AI agent that can process customer support tickets by:

- Understanding the request
- Classifying the ticket
- Searching a knowledge base
- Deciding if it can resolve the issue
- Drafting a response
- Creating a support ticket when necessary
- Escalating risky/complex cases to a human
- Remembering relevant customer information
- Recording traces and evaluations

## Status

The project is currently in the documentation and planning phase. The codebase has been reset to focus on implementing the phased roadmap sequentially. The current state includes the project roadmap and foundational setup.

## Repository Structure

```
support-ops-agent/
├── docs/
│   └── roadmap.md
├── .gitignore
├── CHANGELOG.md
└── README.md
```

## Roadmap

The project follows a 12-phase roadmap, progressing from basic LLM applications to a production-ready agentic system. Key phases include:

- **Phase 0**: Project foundation
- **Phase 1**: Basic LLM application
- **Phase 2**: Structured domain with Pydantic models
- **Phase 3**: First Agent with control loop
- **Phase 4**: Tool Calling
- **Phase 5**: RAG / Knowledge Base integration
- **Phase 6**: Context and Memory
- **Phase 7**: Guardrails and Authority
- **Phase 8**: Orchestration with multiple agents
- **Phase 9**: Evaluation and metrics
- **Phase 10**: Observability and tracing
- **Phase 11**: Production Runtime infrastructure

## Getting Started

1. Clone the repository.
2. Copy `.env.example` to `.env` and configure API keys.
3. Install dependencies: `pip install -e .[dev]` (requires Poetry setup).
4. Run `pytest` to verify the setup.
5. Begin implementation following the roadmap phases.

## Documentation

For a detailed breakdown of the project plan and implementation phases, please refer to the [Roadmap](docs/roadmap.md).
