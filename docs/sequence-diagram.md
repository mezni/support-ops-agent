# Sequence Diagrams

Diagrams of the `support-ops-agent` runtime as it exists at version **0.0.7**.

These describe **implemented** behaviour, not the target architecture in
[roadmap.md](roadmap.md). Where a code path raises `NotImplementedError`, that is shown
explicitly rather than drawn as a working step.

Companion to [class-diagram.md](class-diagram.md), which shows types and relationships.

Rendered automatically by GitHub, GitLab, and any Mermaid-capable Markdown viewer.

---

## 1. Startup and configuration resolution

Entry point `support_ops.main.main`. Configuration is resolved from the project root,
**not** the current working directory, so `python -m support_ops.main` behaves the same
from any directory.

```mermaid
sequenceDiagram
    autonumber
    participant CLI as __main__
    participant Main as main.main
    participant Settings as Settings
    participant EnvFile as .env at PROJECT_ROOT
    participant Validator as _require_credentials
    participant LLMClient as LLMClient
    participant Seed as knowledge.seed
    participant Store as KnowledgeStore
    participant Retriever as KnowledgeRetriever
    participant Registry as create_default_registry
    participant SDK as openai.OpenAI

    CLI->>Main: runpy invokes main
    Main->>Settings: Settings
    Settings->>EnvFile: read env_file absolute path
    EnvFile-->>Settings: OPENROUTER_API_KEY and OPENROUTER_MODEL
    Settings->>Validator: model_validator mode after
    alt any value empty
        Validator-->>CLI: ValidationError naming missing vars and .env path
    else both present
        Validator-->>Settings: Settings instance
    end
    Settings-->>Main: Settings
    Main->>LLMClient: LLMClient settings
    LLMClient->>SDK: OpenAI api_key and base_url openrouter
    SDK-->>LLMClient: client ready
    LLMClient-->>Main: LLMClient
    Main->>Seed: default_documents
    Seed-->>Main: 4 KnowledgeDocument
    Main->>Store: KnowledgeStore documents
    Main->>Retriever: KnowledgeRetriever store
    Main->>Registry: create_default_registry retriever
    Registry-->>Main: ToolRegistry with create_ticket and search_knowledge_base
    Main->>Main: build IncomingTicket T-001
```

Key detail: `PROJECT_ROOT` is computed as `Path(__file__).resolve().parents[2]`, so
`env_file` is absolute. An earlier relative `".env"` silently resolved against the cwd
and produced empty credentials.

`create_default_registry` is a module-level factory, **not** a method on `ToolRegistry`.
When it was nested inside the class body, its `-> ToolRegistry` annotation was evaluated
before the name existed, raising `NameError` at import. It now takes a
`KnowledgeRetriever` because `search_knowledge_base` cannot be constructed without one.

---

## 2. Full agent run (the path `main` takes)

`SupportAgent.run` is `decide` followed by `execute`. This is the complete happy path.

```mermaid
sequenceDiagram
    autonumber
    participant Main as main.main
    participant Agent as SupportAgent
    participant LLMClient as LLMClient
    participant SDK as openai.OpenAI
    participant API as OpenRouter API
    participant Registry as ToolRegistry
    participant Tool as CreateTicketTool

    Main->>Agent: run ticket
    Agent->>LLMClient: decide ticket, structured prompt and AgentDecision
    LLMClient->>SDK: chat.completions.parse response_format AgentDecision
    SDK->>API: HTTPS request
    API-->>SDK: JSON completion
    SDK-->>LLMClient: parsed AgentDecision
    LLMClient-->>Agent: AgentDecision
    Note over Agent: action chosen by the model,<br/>not by dispatch logic
    alt action equals CREATE_TICKET
        Agent->>Registry: get create_ticket
        Registry-->>Agent: CreateTicketTool
        Agent->>Tool: argument_schema then build CreateTicketInput
        Tool-->>Agent: validated CreateTicketInput
        Agent->>Tool: execute arguments
        Tool-->>Agent: ToolResult success and data
        Agent-->>Main: ToolResult
    else action equals DRAFT_RESPONSE
        Agent-->>Main: placeholder string, not implemented
    else action equals ESCALATE
        Agent-->>Main: placeholder string, not implemented
    else model returns search_knowledge_base
        Agent-->>Main: impossible, ValidationError at decide
    end
    Main->>Main: print result
```

The prompt sent in step 2 must state the JSON shape explicitly. `response_format` alone
does not constrain `poolside/laguna-s-2.1:free`, which otherwise replies with Markdown
prose such as `**Chosen action:** escalate` and causes `ValidationError: Invalid JSON`.
Adding a `Return JSON with exactly these fields` block fixed this.

**The `search_knowledge_base` tool is never reached.** The registry holds it, but
`AgentAction` has only `draft_response`, `create_ticket`, and `escalate`, so the model
cannot select knowledge search and `execute` has no branch for it. The knowledge base
therefore cannot influence the decision, even though `main` builds and injects the whole
retrieval stack. The fourth branch above is unreachable: a model that did emit
`"action": "search_knowledge_base"` would fail pydantic validation at `decide`, not at
dispatch.

---

## 3. Knowledge retrieval

Reachable today only from tests and from `main`, never through the agent. Scoring is
token-set overlap over `title + category + content`.

```mermaid
sequenceDiagram
    autonumber
    participant Tool as SearchKnowledgeBaseTool
    participant Input as SearchKnowledgeBaseInput
    participant Retriever as KnowledgeRetriever
    participant Store as KnowledgeStore
    participant Result as SearchResult

    Tool->>Input: validated query and limit
    Tool->>Retriever: search query and limit
    Retriever->>Store: all
    Store-->>Retriever: list of KnowledgeDocument
    loop for each document
        Retriever->>Retriever: lowercase and split title category content
        Retriever->>Retriever: score equals size of word set intersection
    end
    Retriever->>Retriever: sort by score descending and truncate to limit
    Retriever-->>Tool: list of SearchResult
    Tool->>Tool: flatten to dicts with document_id title content score
    Tool-->>Tool: ToolResult data results
```

`limit` is bounded by pydantic at the call site (`ge=1, le=10`), so an out-of-range
value raises before the search runs. Documents scoring zero are dropped entirely, so an
unmatched query returns an empty list rather than low-scoring noise.

Scoring has no stemming, no IDF, and no normalisation: a repeated term cannot raise the
score because sets deduplicate, and `2.0` means literally "two shared words". Matches the
seed corpus, but a customer phrasing like "can't sign in" will not match the
"Account Locked" document.

---

## 4. Tool dispatch detail

The two-phase tool contract inside `execute`. The agent asks the tool for its input
schema, builds a validated model, then executes. It never touches tool internals.

```mermaid
sequenceDiagram
    autonumber
    participant Agent as SupportAgent
    participant Registry as ToolRegistry
    participant Tool as Tool instance
    participant Input as CreateTicketInput

    Agent->>Registry: get create_ticket
    alt name not registered
        Registry-->>Agent: ValueError Unknown tool
    else name registered
        Registry-->>Agent: Tool
    end
    Agent->>Tool: argument_schema
    Tool-->>Agent: type CreateTicketInput
    Agent->>Input: construct with customer_id subject description
    alt required field missing
        Input-->>Agent: ValidationError
    else valid
        Input-->>Agent: CreateTicketInput
        Agent->>Tool: execute arguments
        Tool-->>Agent: ToolResult success message data
    end
```

`ToolRegistry.get` converts `KeyError` to `ValueError` with `from None`, so callers see
one exception type for both unknown-tool and duplicate-tool. `register` raises
`ValueError` on a duplicate name, which is why `create_default_registry` can only be
called once per registry.

---

## 5. Unimplemented classifier path

`TicketClassifier.classify` sends a prompt and then **discards** the response, raising
`NotImplementedError`. It is not constructed by `main`, so this path is unreachable in
normal operation.

```mermaid
sequenceDiagram
    autonumber
    participant Caller as Unreachable caller
    participant Classifier as TicketClassifier
    participant LLMClient as LLMClient
    participant API as OpenRouter API
    participant Missing as Parsing NOT IMPLEMENTED

    Caller->>Classifier: classify ticket
    Classifier->>LLMClient: chat prompt requesting JSON
    LLMClient->>API: request
    API-->>LLMClient: JSON string
    LLMClient-->>Classifier: str
    Note over Classifier,Missing: result captured then discarded.<br/>Uses llm.chat, not llm.structured.
    Classifier-->>Missing: NotImplementedError
```

The prompt here already contains a correct `Return JSON with exactly these fields`
block, so the fix is a one-line change to call
`self.llm.structured(prompt, TicketClassification)` instead of `self.llm.chat(prompt)`.

---

## 6. Structured output contract

`LLMClient.structured` is generic over pydantic models and is the single place where
model output becomes a typed value.

```mermaid
sequenceDiagram
    autonumber
    participant Caller as Agent or Classifier
    participant LLMClient as LLMClient
    participant SDK as openai.OpenAI
    participant API as OpenRouter API

    Caller->>LLMClient: structured prompt and output_model type T
    LLMClient->>SDK: chat.completions.parse model messages response_format T
    SDK->>API: HTTPS request
    alt model returns valid JSON
        API-->>SDK: content matching schema
        SDK-->>LLMClient: message.parsed instance of T
        LLMClient-->>Caller: T
    else model returns prose or malformed JSON
        API-->>SDK: non JSON content
        SDK-->>LLMClient: ValidationError Invalid JSON
        LLMClient-->>Caller: ValidationError propagates
    else no parsed object
        SDK-->>LLMClient: message.parsed is None
        LLMClient-->>Caller: ValueError Model returned no structured output
    end
```

The middle branch is the one that bit this project: the failure surfaced as a pydantic
`ValidationError` from inside the OpenAI SDK, not as an application-level error, so the
fix belonged in the prompt rather than in the transport.

---

## Component reference

| Module | Responsibility | Status |
| --- | --- | --- |
| `config.py` | Resolve settings, validate credentials | Working |
| `llm.py` | OpenRouter transport, plain and structured | Working |
| `main.py` | Composition root, single ticket run | Working |
| `domain/ticket.py` | Enums and pydantic models | Working |
| `knowledge/document.py` | `KnowledgeDocument` schema | Working |
| `knowledge/store.py` | In-memory document list | Working |
| `knowledge/seed.py` | Hard-coded seed corpus | Working |
| `knowledge/retriever.py` | Token-overlap search | Working, naive scoring |
| `tools/base.py` | `Tool` ABC and `ToolResult` | Working |
| `tools/create_ticket.py` | `CreateTicketInput`, `CreateTicketTool` | Working, stubbed persistence |
| `tools/search_knowledge_base.py` | `SearchKnowledgeBaseInput`, `SearchKnowledgeBaseTool` | Working, **unreachable from agent** |
| `tools/registry.py` | `ToolRegistry` and default factory | Working |
| `agent/agent.py` | `decide`, `execute`, `run` | Working; 2 of 3 actions placeholders |
| `agent/tools.py` | Legacy `ToolResult`, `create_ticket` | **Dead code**, superseded by `tools/` |
| `classifier.py` | `classify` LLM parsing | Raises `NotImplementedError` |