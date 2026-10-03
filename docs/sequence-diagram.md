# Sequence Diagrams

Diagrams of the `support-ops-agent` runtime as it exists at version **0.0.3**.

These describe **implemented** behaviour, not the target architecture in
[roadmap.md](roadmap.md). Where a code path raises `NotImplementedError`, that is
shown explicitly rather than drawn as a working step. Two components
(`TicketClassifier`, `SupportAgent`) are not yet constructed by `main()`, so their
diagrams are marked accordingly.

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
    participant SDK as openai.OpenAI

    CLI->>Main: runpy invokes main
    Main->>Settings: Settings
    Settings->>EnvFile: read env_file absolute path
    EnvFile-->>Settings: OPENROUTER_API_KEY, OPENROUTER_MODEL
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
```

Key detail: `PROJECT_ROOT` is computed as `Path(__file__).resolve().parents[2]`, so
`env_file` is absolute. An earlier relative `".env"` silently resolved against the cwd
and produced empty credentials.

---

## 2. Inference path (fully working)

The only end-to-end path that completes today. Invoked by `main()` and exercised by
running the module.

```mermaid
sequenceDiagram
    autonumber
    participant CLI as __main__
    participant Main as main.main
    participant LLMClient as LLMClient
    participant SDK as openai.OpenAI
    participant API as OpenRouter API
    participant Model as Model poolside laguna free

    CLI->>Main: main
    Main->>LLMClient: chat user_message
    LLMClient->>SDK: chat.completions.create model and messages
    SDK->>API: HTTPS POST /api/v1/chat/completions
    API->>Model: forward request
    Model-->>API: completion
    API-->>SDK: HTTP 200 choices
    SDK-->>LLMClient: response object
    LLMClient->>LLMClient: choices[0].message.content or empty string
    LLMClient-->>Main: str
    Main->>CLI: print response
```

---

## 3. Agent tool dispatch (fully working)

`SupportAgent.execute` dispatches on `AgentDecision.action`. This is the path covered by
`tests/agent/test_agent.py`, which injects a `FakeLLM` and bypasses `decide` entirely.

```mermaid
sequenceDiagram
    autonumber
    participant Caller as Test or caller
    participant Agent as SupportAgent
    participant Decision as AgentDecision
    participant Tools as agent.tools
    participant Result as ToolResult

    Caller->>Agent: execute ticket and decision
    alt action equals CREATE_TICKET
        Agent->>Tools: create_ticket customer_id subject description
        Tools-->>Result: ToolResult success true and message
        Result-->>Caller: ToolResult
    else action equals DRAFT_RESPONSE
        Agent-->>Caller: placeholder string, not implemented
    else action equals ESCALATE
        Agent-->>Caller: placeholder string, not implemented
    else unknown action
        Agent-->>Caller: ValueError
    end
```

---

## 4. Unimplemented LLM decision paths

Both `TicketClassifier.classify` and `SupportAgent.decide` send a prompt to the model
and then **discard the response**, raising `NotImplementedError`. Dashed arrows mark the
missing parsing step.

```mermaid
sequenceDiagram
    autonumber
    participant Agent as Classifier.classify or Agent.decide
    participant LLMClient as LLMClient
    participant API as OpenRouter API
    participant Missing as Structured parsing NOT IMPLEMENTED

    Agent->>LLMClient: chat prompt requesting JSON
    LLMClient->>API: request
    API-->>LLMClient: raw JSON string
    LLMClient-->>Agent: str
    Note over Agent,Missing: result is captured then discarded.<br/>classifier.py:39 raises unconditionally.<br/>agent.py:50 raises unconditionally.
    Agent-->>Missing: NotImplementedError
```

The agent prompt at `agent.py:18-44` already requests the correct shape, and
`AgentDecision` parses it correctly when validated directly:

```
{ "action": "create_ticket", "reason": "..." }
```

So the remaining work is confined to parsing the model string into `AgentDecision` and
`TicketClassification` rather than raising.

---

## Wiring gap

`main()` constructs only `Settings` and `LLMClient`. Neither `TicketClassifier` nor
`SupportAgent` is instantiated anywhere in `src/`, and no module imports them outside
their own tests. The intended composition, per roadmap Phase 3 and 4, is roughly:

```mermaid
sequenceDiagram
    participant Main as main
    participant Classifier as TicketClassifier
    participant Agent as SupportAgent
    participant Tools as agent.tools

    Main->>Classifier: classify ticket
    Classifier-->>Main: TicketClassification
    Main->>Agent: decide ticket
    Note over Agent: blocked, NotImplementedError at agent.py:50
    Agent->>Tools: execute action
    Tools-->>Main: ToolResult
```

This composition does not exist yet and is drawn dashed in intent only — it will not run
until `decide` is implemented.

---

## Component reference

| Module | Responsibility | Status |
| --- | --- | --- |
| `config.py` | Resolve settings, validate credentials | Working |
| `llm.py` | OpenRouter transport via OpenAI SDK | Working |
| `main.py` | Entry point, single-shot chat | Working |
| `agent/tools.py` | `ToolResult`, `create_ticket` stub | Working |
| `agent/agent.py` | `execute` dispatch | Working |
| `agent/agent.py` | `decide` LLM parsing | Raises `NotImplementedError` |
| `classifier.py` | `classify` LLM parsing | Raises `NotImplementedError` |
| `domain/ticket.py` | Enums and pydantic models | Working |