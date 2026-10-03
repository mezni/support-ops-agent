# support-ops-agent Roadmap

## Project Overview

Build an AI agent that receives a customer support ticket and autonomously:
- Understands the request
- Classifies the ticket
- Searches a knowledge base
- Decides whether it can resolve the issue
- Drafts a response
- Creates a support ticket when necessary
- Escalates risky/complex cases to a human
- Remembers relevant customer information
- Records traces and evaluations

This project maps naturally to the 11-architecture layers framework.

---

## Phase 0 — Project foundation

### Learn:
- Python project structure
- configuration
- environment variables
- logging
- dependency management
- testing

### Structure:
```
support-ops-agent/
├── src/
│   └── support_ops/
├── tests/
├── docs/
├── scripts/
├── .env.example
├── pyproject.toml
└── README.md
```

### Example commands:
```bash
# Initialize project
poetry init
# Or: pip install -e .

# Set up environment
cp .env.example .env

# Run tests
pytest
```

---

## Phase 1 — Basic LLM application

### Start with no agent.

```
User → Application → LLM → Response
```

### Learn:
- prompts
- system instructions
- user messages
- model calls
- structured output
- error handling

### Implementation:
```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Test:
```python
def test_basic_llm():
    response = client.chat.completions.create(...)
    assert response.choices[0].message.content is not None
```

---

## Phase 2 — Structured domain

### Introduce the support-ticket domain using Pydantic models.

```python
from pydantic import BaseModel, Field


class TicketClassification(BaseModel):
    category: str = Field(
        description="Ticket category: billing, technical, account, etc."
    )
    priority: str = Field(description="Ticket priority: low, medium, high, urgent")
    sentiment: str = Field(description="Sentiment: positive, neutral, negative")
    intent: str = Field(description="Primary intent of the ticket")
```

### The LLM should produce structured data such as:

```python
classification = classify_ticket("My payment failed twice!")
# category = "billing"
# priority = "high"
# sentiment = "negative"
```

### Now you have:
```
LLM + domain model
```

### Test:
```python
def test_structured_output():
    result = classify_ticket("Payment failed")
    assert isinstance(result, TicketClassification)
    assert result.category == "billing"
```

---

## Phase 3 — First Agent

### Turn the LLM application into an agent with a control loop.

```
Ticket → Understand → Need knowledge? → YES → search KB → draft response
                 │                              │
                 └────── NO ────────────────────┘
                           ↓
                 Can resolve? → YES → draft response
                            │
                            └── NO → create ticket
```

### The agent gets a loop:

```python
def agent_loop(ticket):
    while True:
        decision = llm.decide(ticket.context)
        if decision.is_terminal:
            break
        action = decision.action
        result = execute(action, ticket)
        ticket.context.update(result)
```

### Test:
```python
def test_agent_loop():
    ticket = Ticket(...)
    result = agent_loop(ticket)
    assert result.is_resolved
```

---

## Phase 4 — Tool Calling

### Give the agent tools:

```python
def search_knowledge_base(query: str) -> str: ...
def create_ticket(ticket_data: dict) -> Ticket: ...
def get_customer(customer_id: str) -> Customer: ...
def escalate_to_human(ticket: Ticket, reason: str) -> Escalation: ...
```

### Now the agent can interact with the outside world.

### Critical architectural principle:
> The model decides what action may be needed; the application controls whether and how that action is actually executed.

### Example agent decision flow:

```
Agent wants:    refund_customer()
    ↓
Authorization Policy
    ↓
Is agent allowed? → YES / NO
    ↓
   YES     NO
    │        │
    ▼        ▼
 Execute   Human approval
```

### Test:
```python
def test_tool_calling():
    ticket = Ticket(...)
    result = agent.handle(ticket)
    assert result.action in [Tool.SEARCH, Tool.CREATE, Tool.ESCALATE]
```

---

## Phase 5 — RAG / Knowledge

### Add a knowledge base structure:

```
knowledge/
├── password_reset.md
├── billing.md
├── refunds.md
├── account_locked.md
└── subscriptions.md
```

### Pipeline:

```
Documents → Chunking → Embeddings → Vector Store → Retriever → Agent
```

### Implementation steps:

1. **Documents**: Add markdown knowledge base files
2. **Chunking**: Split documents into overlapping chunks
3. **Embeddings**: Convert chunks to vectors using an embedding model
4. **Vector Store**: Store embeddings in a vector database (Chroma, Pinecone, etc.)
5. **Retriever**: Retrieve relevant chunks for a given query
6. **Agent**: Use retrieved context to inform responses

### Test:
```python
def test_rag_retrieval():
    results = retrieve("How do I reset my password?")
    assert len(results) > 0
    assert "password_reset" in results[0].source
```

---

## Phase 6 — Context and Memory

### Add short-term and long-term context:

**Short-term context** (current execution):
- Current conversation
- Current ticket
- Current tool results
- Current workflow state

**Long-term memory** (across sessions):
- Customer previous tickets
- Customer preferences
- Previous resolutions
- Relevant facts

### Important distinction:

| Concept | Description | Example |
|---------|-------------|---------|
| **Context** | Information supplied for current execution | Current ticket, retrieved docs |
| **State** | Current workflow/execution state | Step 3 of 5, in_progress |
| **Memory** | Conversation/session history | Last 5 exchanges |
| **Knowledge** | External information from data sources | KB articles, customer history |

### Implementation:

```python
class AgentContext:
    def __init__(
        self,
        ticket: Ticket,
        conversation: Conversation,
        retrieved_docs: List[Document],
        customer: Customer,
    ):
        self.ticket = ticket
        self.conversation = conversation
        self.retrieved_docs = retrieved_docs
        self.customer = customer
```

### Test:
```python
def test_context_building():
    ctx = build_context(ticket, conversation, retrieved_docs, customer)
    assert ctx.ticket.id == ticket.id
    assert len(ctx.retrieved_docs) > 0
```

---

## Phase 7 — Guardrails and Authority

### Make the agent safe with authorization policies:

```
Agent wants:    refund_customer(amount=$150)
    ↓
Authorization Policy
    ↓
Amount <= $100? → NO
    ↓
Human approval required
    ↓
Human: Approves/Rejects
    ↓
   Approved   → Execute refund
   Rejected   → Notify human, suggest alternative
```

### Introduce:

- Input validation
- Output validation
- Tool authorization
- Permission boundaries
- Human approval workflows
- Sensitive-operation controls

### Example guardrail:

```python
def authorize_tool(action: str, params: dict) -> bool:
    if action == "refund_customer":
        if params["amount"] > 100:
            return get_human_approval(params)
    return True
```

### Test:
```python
def test_guardrails():
    assert authorize_tool("refund_customer", {"amount": 50}) == True
    assert authorize_tool("refund_customer", {"amount": 150}) == False
```

---

## Phase 8 — Orchestration

### Introduce multiple specialized agents:

```
                    ┌── Research Agent
                    │
Request → Router ───┼── Triage Agent
                    │
                    └── Escalation Agent
```

### Learn:

- routing
- handoffs
- workflow state
- agent coordination
- sequential execution
- parallel execution
- failure recovery

### Orchestration patterns:

```python
# Sequential execution
result1 = agent1.handle(input)
result2 = agent2.handle(result1)

# Parallel execution
results = await agent1.handle(input), agent2.handle(input)

# Workflow state machine
state = WorkflowState.INITIAL
while state != WorkflowState.TERMINAL:
    state = await transition(state)
```

### Test:
```python
def test_router():
    agent = Router.route("billing issue")
    assert agent.name == "BillingAgent"
```

---

## Phase 9 — Evaluation

### Create an evaluation dataset:

```
evaluation/
├── tickets.jsonl
├── expected_categories.jsonl
└── expected_resolutions.jsonl
```

### Example evaluation data (tickets.jsonl):

```jsonl
{"id": "1", "customer_id": "c123", "subject": "Payment failed", "description": "My payment failed twice!"}
{"id": "2", "customer_id": "c456", "subject": "Account locked", "description": "I can't log in"}
```

### Evaluate metrics:

- Classification accuracy
- Retrieval quality
- Tool selection
- Response quality
- Task completion
- Safety

### Run evaluation:

```bash
python -m scripts.evaluate \
    --dataset evaluation/tickets.jsonl \
    --expected evaluation/expected_categories.jsonl
```

### Output metrics:

```
Classification accuracy: 94.2%
Retrieval MAP: 0.87
Tool selection F1: 0.91
Task success rate: 89.5%
Safety violations: 0
```

### Test as regression test:
```python
def test_evaluation_regression():
    metrics = run_evaluation()
    assert metrics.classification_accuracy > 0.90
    assert metrics.task_success_rate > 0.85
```

---

## Phase 10 — Observability

### Add tracing for each request:

```
Request
  │
  ├── Agent
  │    ├── LLM call (latency, tokens, cost)
  │    ├── Retrieval (results, relevance score)
  │    ├── Tool call (which tools, success/failure)
  │    └── Decision (what was decided, why)
  │
  └── Final response
```

### Track metrics:

- Latency (per step, overall)
- Token usage (per model call, total)
- Cost (per request, per month)
- Errors (tool failures, LLM errors)
- Tool calls (count, types, outcomes)
- Retrieval results (relevant, irrelevant)
- Agent decisions (what, when, outcome)
- Successful/failed tasks

### Example tracing output:

```json
{
  "request_id": "req-12345",
  "timestamp": "2024-01-15T10:30:00Z",
  "steps": [
    {
      "name": "classify_ticket",
      "latency_ms": 120,
      "llm_call": {
        "model": "gpt-4o-mini",
        "tokens": {"prompt": 15, "completion": 5},
        "cost_usd": 0.0015
      },
      "decision": "classify",
      "output": {"category": "billing", "priority": "high"}
    },
    {
      "name": "search_knowledge_base",
      "latency_ms": 230,
      "retrieval": {
        "query": "billing payment failed",
        "results": 3,
        "top_result_relevance": 0.92
      },
      "decision": "proceed",
      "output": "Found 3 relevant articles"
    }
  ],
  "final_outcome": "resolved",
  "total_latency_ms": 890,
  "total_tokens": 120,
  "total_cost_usd": 0.008
}
```

### Visualize with:

- **Traces**: Interactive execution flow
- **Metrics**: Grafana/dashboards
- **Logs**: Structured JSON logging
- **Eval datasets**: Regression testing

---

## Phase 11 — Production Runtime

### Add production infrastructure:

```
                    Load Balancer
                         │
                         ▼
                    API Service
                         │
                    ┌────┴────┐
                    ▼         ▼
                 Agent      Queue
                 Worker      │
                    │        ▼
                    └────→ Workers
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
         PostgreSQL   Vector DB   Object Storage
```

### Add:

- **Docker** (containerization)
- **PostgreSQL** (ticket database, customer data)
- **Redis/queue** (task queue, e.g., BullMQ, RQ)
- **Background workers** (agent execution)
- **Migrations** (database schema changes)
- **Secrets** (API keys, passwords via env or secret manager)
- **CI/CD** (GitHub Actions, GitLab CI for deployment)
- **Health checks** (liveness, readiness probes)
- **Retries** (transient failure handling)
- **Timeouts** (prevent hanging operations)
- **Deployment** (staging → production pipeline)

### Docker Compose example:

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://...
      - VECTOR_DB_URL=...
    depends_on:
      - postgres
      - redis
      - vector-db

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=support_ops
      - POSTGRES_USER=...
      - POSTGRES_PASSWORD=...

  redis:
    image: redis:7

  vector-db:
    image: redis:7  # or Chroma/Pinecone
```

### CI/CD pipeline (GitHub Actions):

```yaml
name: CI/CD

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e ".[test]"
      - run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t support-ops-agent:latest .
      - run: docker compose up -d
```

### Health check endpoint:

```python
@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

---

## The Learning Progression

```
LLM
 ↓
Structured LLM
 ↓
Agent
 ↓
Tool-using Agent
 ↓
RAG Agent
 ↓
Memory-enabled Agent
 ↓
Guardrailed Agent
 ↓
Multi-Agent System
 ↓
Evaluated Agent
 ↓
Observable Agent
 ↓
Production Agentic System
```

## Roadmap

See the full progression above, from Phase 0 (foundation) through Phase 11 (production runtime).

Each phase builds on the previous one, gradually transforming a simple LLM application into a production-grade agentic AI system that follows the 11-layer architecture.

---

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -e ".[dev]"`
3. Copy `.env.example` to `.env` and configure API keys
4. Run `pytest` to verify the setup
5. Start with Phase 1 and work through each phase sequentially

## Next Steps

- [ ] Phase 0: Set up project structure and dependencies
- [ ] Phase 1: Basic LLM application
- [ ] Phase 2: Structured domain with Pydantic models
- [ ] Continue through all 11 phases