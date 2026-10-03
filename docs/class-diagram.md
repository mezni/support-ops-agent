# Class Diagram

Static structure of `support-ops-agent` as it exists at version **0.0.8**.

Companion to [sequence-diagram.md](sequence-diagram.md), which shows runtime ordering.
This document shows types, members, and relationships. Implemented and unimplemented
members are distinguished in the [module status](#module-status).

---

## Full class diagram

```mermaid
classDiagram
    direction TB

    class Settings {
        <<PydanticSettings>>
        +str openrouter_api_key
        +str openrouter_model
        +_require_credentials() Settings
    }

    class LLMClient {
        -Settings settings
        -OpenAI client
        +chat(user_message) str
        +structured(user_message, output_model) T
    }

    class SupportAgent {
        -LLMClient llm
        -ToolRegistry tools
        -MemoryManager memory
        +decide(ticket) AgentDecision
        +execute(ticket, decision) ToolResult or str
        +run(ticket) ToolResult or str
    }

    class MemoryManager {
        -ShortTermMemory short_term
        -LongTermMemory long_term
        +remember_message(role, content) None
        +get_conversation() list
        +get_customer(customer_id) CustomerMemory
        +remember_fact(customer_id, key, value) None
        +remember_ticket(customer_id, ticket_id) None
    }

    class ShortTermMemory {
        -list _messages
        +add(role, content) None
        +get_messages() ConversationMessage
        +clear() None
    }

    class LongTermMemory {
        -dict _customers
        +get(customer_id) CustomerMemory
        +save(memory) None
        +add_ticket(customer_id, ticket_id) None
        +add_fact(customer_id, key, value) None
        +add_preference(customer_id, key, value) None
    }

    class CustomerMemory {
        <<PydanticModel>>
        +str customer_id
        +dict preferences
        +dict facts
        +list previous_tickets
        +datetime updated_at
    }

    class ConversationMessage {
        <<PydanticModel>>
        +str role
        +str content
        +datetime timestamp
    }

    class TicketClassifier {
        -LLMClient llm
        +classify(ticket) TicketClassification
    }

    class ToolRegistry {
        -dict _tools
        +register(tool) None
        +get(name) Tool
        +list() Tool
    }

    class Tool {
        <<abstract>>
        +str name
        +str description
        +execute(arguments) ToolResult
        +argument_schema() type
    }

    class CreateTicketTool {
        +str name
        +str description
        +execute(arguments) ToolResult
        +argument_schema() type
    }

    class SearchKnowledgeBaseTool {
        +str name
        +str description
        -KnowledgeRetriever retriever
        +execute(arguments) ToolResult
        +argument_schema() type
    }

    class KnowledgeRetriever {
        -KnowledgeStore store
        +search(query, limit) SearchResult
    }

    class KnowledgeStore {
        -list documents
        +all() KnowledgeDocument
    }

    class KnowledgeDocument {
        <<PydanticModel>>
        +str id
        +str title
        +str content
        +str category
    }

    class SearchResult {
        <<dataclass>>
        +KnowledgeDocument document
        +float score
    }

    class CreateTicketInput {
        <<PydanticModel>>
        +str customer_id
        +str subject
        +str description
    }

    class SearchKnowledgeBaseInput {
        <<PydanticModel>>
        +str query
        +int limit
    }

    class ToolResult {
        <<PydanticModel>>
        +bool success
        +str message
        +dict data
    }

    class IncomingTicket {
        <<PydanticModel>>
        +str id
        +str customer_id
        +str subject
        +str description
    }

    class SupportTicket {
        <<PydanticModel>>
        +str id
        +str customer_id
        +str subject
        +str description
        +TicketCategory category
        +TicketPriority priority
        +TicketStatus status
        +str sentiment
    }

    class TicketClassification {
        <<PydanticModel>>
        +TicketCategory category
        +TicketPriority priority
        +str sentiment
    }

    class AgentDecision {
        <<PydanticModel>>
        +AgentAction action
        +str reason
    }

    class TicketCategory {
        <<enumeration>>
        BILLING
        TECHNICAL
        ACCOUNT
        SECURITY
        GENERAL
    }

    class TicketPriority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
        CRITICAL
    }

    class TicketStatus {
        <<enumeration>>
        NEW
        IN_PROGRESS
        RESOLVED
        ESCALATED
    }

    class AgentAction {
        <<enumeration>>
        DRAFT_RESPONSE
        CREATE_TICKET
        ESCALATE
    }

    class FakeLLM {
        <<test double>>
        +structured(message, output_model) AgentDecision
    }

    LLMClient *-- Settings : settings
    LLMClient *-- OpenAI : client
    TicketClassifier o-- LLMClient : llm
    SupportAgent o-- LLMClient : llm
    SupportAgent o-- ToolRegistry : tools
    SupportAgent o-- MemoryManager : memory
    MemoryManager *-- ShortTermMemory : short_term
    MemoryManager *-- LongTermMemory : long_term
    ShortTermMemory o-- ConversationMessage : _messages
    LongTermMemory o-- CustomerMemory : _customers
    LongTermMemory ..> CustomerMemory : get creates and returns
    ToolRegistry o-- Tool : _tools
    Tool <|-- CreateTicketTool
    Tool <|-- SearchKnowledgeBaseTool
    SearchKnowledgeBaseTool o-- KnowledgeRetriever : retriever
    KnowledgeRetriever o-- KnowledgeStore : store
    KnowledgeStore o-- KnowledgeDocument : documents
    KnowledgeRetriever ..> SearchResult : search returns
    SearchResult --> KnowledgeDocument : document
    CreateTicketTool ..> CreateTicketInput : argument_schema
    CreateTicketTool ..> ToolResult : returns
    SearchKnowledgeBaseTool ..> SearchKnowledgeBaseInput : argument_schema
    SearchKnowledgeBaseTool ..> ToolResult : returns
    SupportAgent ..> ToolResult : create_ticket returns
    SupportAgent ..> AgentDecision : decide returns
    SupportAgent ..> IncomingTicket : consumes
    AgentDecision --> AgentAction : action
    TicketClassification --> TicketCategory : category
    TicketClassification --> TicketPriority : priority
    SupportTicket --> TicketCategory : category
    SupportTicket --> TicketPriority : priority
    SupportTicket --> TicketStatus : status
```

`*--` is composition: the owner creates the part. `o--` is aggregation: the consumer
holds a caller-supplied reference. `..>` is a dependency with no stored reference.

`SupportAgent` holds `ToolRegistry` and `MemoryManager` by aggregation rather than
composition because both are injected, which is what lets tests substitute them.

---

## Memory layer

```mermaid
classDiagram
    direction LR

    class MemoryManager {
        -ShortTermMemory short_term
        -LongTermMemory long_term
        +remember_message(role, content) None
        +get_conversation() list
        +get_customer(customer_id) CustomerMemory
        +remember_fact(customer_id, key, value) None
        +remember_ticket(customer_id, ticket_id) None
    }

    class ShortTermMemory {
        -list _messages
        +add(role, content) None
        +get_messages() ConversationMessage
        +clear() None
    }

    class LongTermMemory {
        -dict _customers
        +get(customer_id) CustomerMemory
        +save(memory) None
        +add_ticket(customer_id, ticket_id) None
        +add_fact(customer_id, key, value) None
        +add_preference(customer_id, key, value) None
    }

    class ConversationMessage {
        <<PydanticModel>>
        +str role
        +str content
        +datetime timestamp
    }

    class CustomerMemory {
        <<PydanticModel>>
        +str customer_id
        +dict preferences
        +dict facts
        +list previous_tickets
        +datetime updated_at
    }

    MemoryManager *-- ShortTermMemory
    MemoryManager *-- LongTermMemory
    ShortTermMemory o-- ConversationMessage
    LongTermMemory o-- CustomerMemory
```

`MemoryManager` is the only type the agent depends on. It owns the routing decision:
`remember_message` goes to the bounded-in-spirit short-term buffer, while
`remember_fact` and `remember_ticket` go to long-term storage. Callers never choose a
store.

Unlike the rest of the codebase, `memory/` uses **relative imports**
(`from .models import ...`) where every other package uses absolute
`from support_ops.x import y`. Not incorrect, but inconsistent.

### `LongTermMemory.get()` mutates on read

A getter that inserts:

```
before get, records: 0
after  get, records: 1   <- get() inserted an empty record
```

`SupportAgent.decide` calls `get_customer` on every ticket, so the first ticket from
any new customer creates an empty `CustomerMemory` as a side effect of reading. Two
consequences:

- There is no way to ask "do I know this customer?" without creating them, so unknown
  and known-but-empty are indistinguishable. Both render as `{}` in the prompt.
- A mistyped `customer_id` silently inserts a phantom record instead of failing.

`add_ticket` additionally guards against duplicates, so `previous_tickets` cannot
accumulate repeats; `add_fact` and `add_preference` are idempotent by dict assignment.

### `updated_at` does not track modification

`updated_at` is set once by `default_factory` at construction and never refreshed.
Verified: after `add_fact` followed by `add_ticket`, `updated_at` was unchanged. It
records creation time, not last modification, so the field name misleads.

### `ShortTermMemory` is unbounded

There is no eviction and no maximum length. A thousand `add` calls retain a thousand
messages. Roadmap Phase 6 specifies "Last 5 exchanges", so a long session grows without
limit. A `deque(maxlen=...)` would cap it. `get_messages` does return a copy, so callers
cannot mutate the buffer by accident.

### Customer context reaches the model as Python repr

`decide` interpolates the memory fields directly into an f-string, so the prompt
literally contains:

```
Customer facts:
{'plan': 'premium'}

Customer preferences:
{'contact': 'email'}

Previous tickets:
['T-000']
```

These are Python `repr` forms with single quotes, not valid JSON. Models generally
handle this, but `json.dumps` would emit a valid literal if that matters.

---

## Registered tools versus reachable tools

`ToolRegistry` holds two tools, but the agent can only reach one of them:

| Registered tool | Reachable via `execute`? | Why |
| --- | --- | --- |
| `create_ticket` | Yes | `AgentAction.CREATE_TICKET` branch |
| `search_knowledge_base` | **No** | no matching `AgentAction`, no dispatch branch |

`AgentAction` has exactly three members — `DRAFT_RESPONSE`, `CREATE_TICKET`, `ESCALATE`
— and `SupportAgent.execute` branches only on `CREATE_TICKET` before handling the two
placeholder actions. There is no `SEARCH_KNOWLEDGE_BASE` action, so the decision schema
offered to the model cannot express "look this up", and `execute` has no branch that
would call `tools.get("search_knowledge_base")`.

The knowledge layer is therefore reachable **only from tests** and from `main`, which
constructs the retriever and passes it into the registry. This is why the suite is green
despite the gap: the agent test asserts on `create_ticket`.

Wiring it requires two coordinated changes, not one:

1. Add `AgentAction.SEARCH_KNOWLEDGE_BASE` so the model can select it.
2. Add an `execute` branch resolving `"search_knowledge_base"` from the registry.

Until then the registry and the action enum are two independent lists that can drift
further apart with no test failing.

---

## Tool layer

```mermaid
classDiagram
    direction LR

    class ABC {
        <<stdlib abc>>
        +abstractmethod
    }

    class BaseModel {
        <<pydantic>>
        +model_validate(data)
        +model_dump_json() str
    }

    class Tool {
        <<abstract>>
        +str name
        +str description
        +execute(arguments) ToolResult
        +argument_schema() type
    }

    class CreateTicketTool {
        +str name
        +str description
        +execute(arguments) ToolResult
        +argument_schema() type
    }

    class SearchKnowledgeBaseTool {
        +str name
        +str description
        -KnowledgeRetriever retriever
        +execute(arguments) ToolResult
        +argument_schema() type
    }

    class ToolRegistry {
        -dict _tools
        +register(tool) None
        +get(name) Tool
        +list() Tool
    }

    ABC <|-- Tool
    Tool <|-- CreateTicketTool
    Tool <|-- SearchKnowledgeBaseTool
    BaseModel <|-- ToolResult
    BaseModel <|-- CreateTicketInput
    BaseModel <|-- SearchKnowledgeBaseInput
    ToolRegistry o-- Tool
    SearchKnowledgeBaseTool o-- KnowledgeRetriever
```

Both concrete tools subclass `Tool`. This is enforced, not incidental:
`SearchKnowledgeBaseTool` was originally declared without the base class, which Python
accepted silently because annotations are not checked at runtime. Nothing then guaranteed
`execute` or `argument_schema` existed on a registered tool, and
`ToolRegistry.list() -> list[Tool]` was inaccurate.

### The two-phase tool contract

`SupportAgent.execute` never touches a tool's internals. It asks the tool for its input
schema, builds a validated model from the ticket, then executes:

```python
tool = self.tools.get("create_ticket")
arguments = tool.argument_schema()(
    customer_id=ticket.customer_id,
    subject=ticket.subject,
    description=ticket.description,
)
return tool.execute(arguments)
```

So `argument_schema()` returning `CreateTicketInput` serves double duty: it types the
arguments, and it validates them through pydantic before the tool runs. Missing
required fields fail at the call site rather than inside tool logic.

`SearchKnowledgeBaseInput.limit` additionally carries `ge=1, le=10`, so an
out-of-range limit is rejected by pydantic at the call site.

`ToolRegistry.get` translates `KeyError` into `ValueError` with `from None`, so callers
see one exception type for "unknown tool" and "duplicate tool" regardless of which
dict operation failed.

### `ToolResult` is not a discriminated union

`execute` is declared `-> ToolResult | str`. Only `CREATE_TICKET` returns a
`ToolResult`; `DRAFT_RESPONSE` and `ESCALATE` return bare placeholder strings. Callers
must type-check before touching `.success` or `.data`, which is why `main()` can
legitimately print either a string or a pydantic model. A discriminated union or a
consistent envelope would remove the need for that check.

`ToolResult.data` is typed `dict[str, Any] | None`, and the two tools use it
inconsistently: `create_ticket` returns flat keys (`ticket_id`, `customer_id`), while
`search_knowledge_base` returns a single nested `results` list of dicts. Consumers must
special-case per tool.

---

## Knowledge layer

```mermaid
classDiagram
    direction LR

    class KnowledgeStore {
        -list documents
        +all() KnowledgeDocument
    }

    class KnowledgeRetriever {
        -KnowledgeStore store
        +search(query, limit) SearchResult
    }

    class SearchResult {
        <<dataclass>>
        +KnowledgeDocument document
        +float score
    }

    class KnowledgeDocument {
        <<PydanticModel>>
        +str id
        +str title
        +str content
        +str category
    }

    KnowledgeRetriever o-- KnowledgeStore
    KnowledgeStore o-- KnowledgeDocument
    KnowledgeRetriever ..> SearchResult
    SearchResult --> KnowledgeDocument
```

`KnowledgeStore` is an in-memory list holder with a single `all()` accessor, and
`seed.default_documents()` returns four hard-coded documents covering password reset,
duplicate billing, account lockout, and refund policy.

### Scoring is naive token overlap

`KnowledgeRetriever.search` lowercases the query and each document's
`title + category + content`, splits on whitespace, and scores the size of the
intersection of word *sets*:

```python
overlap = query_words & document_words
score = len(overlap)
```

Consequences worth knowing before relying on it:

- **No stemming or lemmatisation.** "charged" and "charge" are different tokens.
- **No IDF weighting.** A common word contributes as much as a distinctive one, so
  scores are not comparable across queries.
- **Set, not multiset.** A repeated term raises no score.
- **Scores are raw counts cast to `float`**, so `2.0` means "two shared words", not a
  normalised relevance.

Observed behaviour on the seed corpus:

| Query | Results |
| --- | --- |
| `customer charged twice` | KB-002 (2.0) |
| `locked out of my account` | KB-003 (2.0), KB-001 (1.0) |
| `refund policy` | KB-004 (2.0) |

This is lexical matching, not semantic retrieval. A query phrased the way a customer
would actually type it — "can't sign in", "double charged" — will not match
"Account Locked" or "Duplicate Billing Charge". Fine as a placeholder; it will need
stemming, IDF, or embeddings once real content is loaded.

---

## Domain layer

All four enums subclass `StrEnum`, so members compare equal to their string values.
That is what lets `response_format` accept `"create_ticket"` from a JSON payload and
bind it to `AgentAction.CREATE_TICKET`.

```mermaid
classDiagram
    direction LR

    class BaseModel {
        <<pydantic>>
    }

    class StrEnum {
        <<stdlib enum>>
    }

    BaseModel <|-- SupportTicket
    BaseModel <|-- IncomingTicket
    BaseModel <|-- TicketClassification
    BaseModel <|-- AgentDecision

    StrEnum <|-- TicketCategory
    StrEnum <|-- TicketPriority
    StrEnum <|-- TicketStatus
    StrEnum <|-- AgentAction
```

| Type | Purpose |
| --- | --- |
| `IncomingTicket` | Raw ticket as received, before classification |
| `SupportTicket` | Classified, tracked ticket with lifecycle `status` |
| `TicketClassification` | Intended output of `TicketClassifier.classify` |
| `AgentDecision` | Output of `SupportAgent.decide`, consumed by `execute` |

`IncomingTicket` and `SupportTicket` share four identical fields (`id`, `customer_id`,
`subject`, `description`) but are **not** related by inheritance. The duplication is
deliberate: incoming tickets are untrusted input parsed before validation, while
`SupportTicket` requires `category` and `priority`. Factoring the shared fields into a
base model would couple the trusted and untrusted shapes. Worth revisiting if a third
ticket shape appears.

---

## Duplicate `ToolResult` types

There are currently **two** distinct classes named `ToolResult`:

| Location | Kind | Fields | Used by |
| --- | --- | --- | --- |
| `tools/base.py` | `pydantic.BaseModel` | `success`, `message`, `data` | `Tool`, `CreateTicketTool`, `SupportAgent` |
| `agent/tools.py` | `@dataclass` | `success`, `message` | nothing |

They are unrelated classes; `tools.base.ToolResult is agent.tools.ToolResult` is
`False`. `agent/tools.py` is **dead code** — nothing in `src/` or `tests/` imports it
after the tool registry refactor. It still exposes a `create_ticket` function, so both
these imports would succeed and return differently-shaped objects:

```python
from support_ops.tools.base import ToolResult  # pydantic, has .data
from support_ops.agent.tools import ToolResult  # dataclass, no .data
```

Deleting `agent/tools.py` would remove the ambiguity. It is kept in this diagram only
to document the duplication.

---

## Test doubles

`FakeLLM` in `tests/agent/fakes.py` deliberately does **not** subclass `LLMClient`:

```python
class FakeLLM:
    def structured(self, message: str, output_model: type):
        return AgentDecision(...)
```

`SupportAgent.__init__` annotates `llm: LLMClient`, so a static type checker flags
`SupportAgent(llm=FakeLLM(), ...)` even though it works at runtime. The coupling is
structural, not nominal. Two consequences:

1. `FakeLLM` must implement every method the agent calls. Renaming `structured` on
   `LLMClient` will not fail at import, only when the agent path runs.
2. There is no shared interface or `Protocol` to catch drift at type-check time.

A `SupportsStructuredLLM` `Protocol` would make the contract explicit. Not done here
because it is a design change rather than a documentation fix.

---

## Generics

`LLMClient.structured` is generic:

```python
T = TypeVar("T", bound=BaseModel)


def structured(self, user_message: str, output_model: type[T]) -> T: ...
```

The return type tracks the model passed in, so `structured(prompt, AgentDecision)` is
typed as `AgentDecision` rather than `BaseModel`. That is what lets `SupportAgent.decide`
declare `-> AgentDecision` with no cast.

---

## Module status

| Module | Types | Status |
| --- | --- | --- |
| `config.py` | `Settings` | Working |
| `llm.py` | `LLMClient` | Working against the current default model |
| `domain/ticket.py` | 4 enums, 4 models | Working |
| `knowledge/document.py` | `KnowledgeDocument` | Working |
| `knowledge/store.py` | `KnowledgeStore` | Working, in-memory only |
| `knowledge/seed.py` | `default_documents` | Working, 4 hard-coded documents |
| `knowledge/retriever.py` | `KnowledgeRetriever`, `SearchResult` | Working, naive scoring |
| `tools/base.py` | `Tool` (ABC), `ToolResult` | Working |
| `tools/create_ticket.py` | `CreateTicketInput`, `CreateTicketTool` | Working, stubbed persistence |
| `tools/search_knowledge_base.py` | `SearchKnowledgeBaseInput`, `SearchKnowledgeBaseTool` | Working, **unreachable from agent** |
| `tools/registry.py` | `ToolRegistry`, `create_default_registry` | Working, now requires a retriever |
| `memory/models.py` | `ConversationMessage`, `CustomerMemory` | Working |
| `memory/short_term.py` | `ShortTermMemory` | Working, unbounded |
| `memory/long_term.py` | `LongTermMemory` | Working, `get` mutates |
| `memory/manager.py` | `MemoryManager` | Working, no return type on `get_conversation` |
| `agent/agent.py` | `decide`, `execute`, `run` | Working; 2 of 3 actions placeholders |
| `main.py` | module function only | Working composition root |
| `agent/tools.py` | `ToolResult`, `create_ticket` | **Dead code**, superseded by `tools/` |
| `classifier.py` | `TicketClassifier.classify` | Raises `NotImplementedError` |
| `tests/agent/fakes.py` | `FakeLLM` | Test only |

---

## Known gaps

- **`decide` is not idempotent.** It records the ticket description to short-term
  memory on every call, so calling it twice on one ticket stores the message twice. The
  roadmap Phase 3 agent loop calls `decide` inside a `while`, so a loop implementation
  would multiply entries. Recording on `run` instead, or de-duplicating by `ticket_id`,
  would fix it.
- **Memory context is untested.** The agent test uses `FakeLLM`, which ignores its
  prompt, so nothing asserts that customer facts, preferences, or previous tickets
  actually reach the model. A silent regression in prompt assembly would not fail any
  test.
- **`search_knowledge_base` is unreachable from the agent.** It is registered, but
  `AgentAction` has no matching member and `execute` has no dispatch branch, so the
  decision schema cannot express a knowledge lookup. See
  [registered versus reachable](#registered-tools-versus-reachable-tools).
- **`TicketClassifier.classify` is unimplemented.** It calls `llm.chat`, discards the
  result, and raises `NotImplementedError`. It should call `llm.structured` with
  `TicketClassification`, which is the pattern `SupportAgent.decide` already uses.
- **Duplicate `ToolResult`.** See below; `agent/tools.py` should be deleted.
- **`execute` is partial.** `CREATE_TICKET` invokes a real tool; `DRAFT_RESPONSE` and
  `ESCALATE` return placeholder strings, and `CreateTicketTool` fabricates a constant
  ticket id `T-NEW-001` rather than persisting anything.
- **Retriever scoring is naive.** Token-set overlap with no stemming, IDF, or
  normalisation. It matches the seed corpus but not natural customer phrasing.
- **Memory layer traps.** `LongTermMemory.get` inserts on read, `updated_at` does not
  track modification, and `ShortTermMemory` is unbounded. See
  [memory layer](#memory-layer).
- **Model choice drives the demo.** `poolside/laguna-s-2.1:free` selected `escalate` for
  every ticket tried, including unambiguous duplicate-billing cases. `main()` therefore
  usually prints a placeholder string rather than exercising tool execution. Test
  `execute` with an explicit `AgentDecision` to exercise dispatch independently of
  model judgement.
- **No tool-exposure to the model.** Tools are never advertised to the LLM; the action
  enum and the tool registry are maintained separately and can drift.
- **Unused import.** `domain/ticket.py` imports `pydantic.Field` without using it.