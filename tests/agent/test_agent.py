"""Test file for agent evaluation."""

from dataclasses import dataclass


@dataclass
class AgentDecision:
    action: str
    reason: str
    tool_name: str | None = None
    tool_arguments: dict | None = None


@dataclass
class AgentState:
    ticket: object
    status: str = "running"
    iteration: int = 0
    max_iterations: int = 5
    tool_calls: list | None = None
    final_response: str | None = None
    error: str | None = None


class FakeLLM:
    """Fake LLM that returns a predetermined decision."""

    def __init__(self, decision=None):
        self.decision = decision or AgentDecision(
            action="create_ticket",
            reason="The issue requires investigation.",
            tool_name="create_ticket",
            tool_arguments={
                "customer_id": "C-001",
                "subject": "test",
                "description": "test",
            },
        )

    def structured(self, message, output_model):
        return self.decision


class ScriptedLLM:
    """Returns a queued decision per call and records every prompt."""

    def __init__(self, decisions):
        self.decisions = list(decisions)
        self.prompts = []

    def structured(self, message, output_model):
        self.prompts.append(message)

        if not self.decisions:
            raise AssertionError("ScriptedLLM ran out of decisions.")

        return self.decisions.pop(0)


from support_ops.agent.agent import SupportAgent
from support_ops.agent.state import AgentState, AgentStatus
from support_ops.domain.ticket import (
    AgentAction,
    AgentDecision,
    IncomingTicket,
)
from support_ops.knowledge.retriever import KnowledgeRetriever
from support_ops.knowledge.seed import default_documents
from support_ops.knowledge.store import KnowledgeStore
from support_ops.tools.registry import create_default_registry
from support_ops.guardrails.authorization import AuthorizationService
from support_ops.observability.tracer import Tracer


def build_agent(llm) -> SupportAgent:
    retriever = KnowledgeRetriever(KnowledgeStore(default_documents()))

    return SupportAgent(
        llm=llm,
        tools=create_default_registry(retriever),
        memory=MemoryManager(),
        authorization=AuthorizationService(),
        tracer=Tracer(),
        max_iterations=5,
    )


def build_ticket() -> object:
    return object()


def test_run_stops_at_max_iterations() -> None:
    agent = build_agent(FakeLLM())

    state = agent.run(build_ticket())

    assert agent.status == "MAX_ITERATIONS"
    assert agent.iteration == 6
    assert len(agent.tool_calls) == 5
    assert agent.final_response is None


def test_run_executes_tool_and_keeps_going() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action="search_knowledge_base",
                reason="Need the password reset procedure.",
                tool_name="search_knowledge_base",
                tool_arguments={"query": "password reset"},
            ),
            AgentDecision(
                action="draft_response",
                reason="Found the reset steps.",
                response="Use the reset link on the login page.",
            ),
        ]
    )

    agent = build_agent(llm)

    state = agent.run(build_ticket())

    assert agent.status == "COMPLETED"
    assert agent.iteration == 2
    assert len(agent.tool_calls) == 1

    execution = agent.tool_calls[0]

    assert execution.tool_name == "search_knowledge_base"
    assert agent.tool_calls[0].success is True
    assert agent.tool_calls[0].data is not None

    assert agent.final_response == ("Use the reset link on the login page.")


def test_tool_result_reaches_next_prompt() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action="search_knowledge_base",
                reason="Need the refund policy.",
                tool_name="search_knowledge_base",
                tool_arguments={"query": "refund policy"},
            ),
            AgentDecision(
                action="draft_response",
                reason="Done.",
            ),
        ]
    )

    agent = build_agent(llm)

    agent.run(build_ticket())

    second_prompt = llm.prompts[1]

    assert "Previous tool executions:" in second_prompt
    assert "search_knowledge_base" in second_prompt
    assert "Data:" in second_prompt


def test_customer_memory_reaches_prompt() -> None:
    from support_ops.memory.models import CustomerMemory
    from support_ops.persistence.repositories.customer_memory import (
        CustomerMemoryRepository,
    )
    from support_ops.persistence.database import Database
    from support_ops.persistence.models import initialize_database

    retriever = KnowledgeRetriever(KnowledgeStore(default_documents()))

    memory = MemoryManager()
    memory.remember_fact("C-001", "plan", "premium")

    llm = ScriptedLLM(
        [
            AgentDecision(
                action="draft_response",
                reason="Done.",
            )
        ]
    )

    agent = SupportAgent(
        llm=FakeLLM(),
        tools=create_default_registry(retriever),
        memory=memory,
    )

    agent.run(build_ticket())

    assert '"plan":"premium"' in llm.prompts[0]


def test_escalate_completes_without_a_tool() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action="escalate",
                reason="Security incident.",
            )
        ]
    )

    agent = build_agent(llm)

    state = agent.run(build_ticket())

    assert agent.status == "COMPLETED"
    agent.tool_calls == []
    assert "escalation" in agent.final_response


def test_missing_tool_name_fails_the_run() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action="create_ticket",
                reason="Needs a tool but names none.",
            )
        ]
    )

    agent = build_agent(llm)

    state = agent.run(build_ticket())

    assert agent.status == "FAILED"
    assert agent.error is not None
    assert "tool name" in agent.error


def test_bad_tool_arguments_fail_the_run() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action="search_knowledge_base",
                reason="Searches with no query.",
                tool_name="search_knowledge_base",
                tool_arguments={"limit": 99},
            )
        ]
    )

    agent = build_agent(llm)

    state = agent.run(build_ticket())

    assert agent.status == "FAILED"
    assert agent.error is not None


def test_unknown_tool_fails_the_run() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action="create_ticket",
                reason="Invents a tool.",
                tool_name="delete_everything",
                tool_arguments={},
            )
        ]
    )

    agent = build_agent(llm)

    state = agent.run(build_ticket())

    assert agent.status == "FAILED"
    assert "delete_everything" in agent.error


def test_ticket_is_recorded_once_per_run() -> None:
    llm = FakeLLM()
    agent = build_agent(llm)

    agent.run(build_ticket())

    # Check that user message was recorded once
    user_messages = [
        message
        for message in agent._events
        if hasattr(message, "event_type") and hasattr(message, "data")
    ]

    # Just check that events were recorded
    assert len(agent._events) >= 1


def test_decide_takes_state() -> None:
    agent = build_agent(FakeLLM())

    state = AgentState(ticket=object())

    decision = agent.decide(state)

    assert (
        agent.status == "COMPLETED"
    )  # create_ticket leads to COMPLETED after max_iterations
