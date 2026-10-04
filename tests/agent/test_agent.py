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
from tests.agent.fakes import ScriptedLLM


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


def build_ticket() -> IncomingTicket:
    return IncomingTicket(
        id="T-001",
        customer_id="C-001",
        subject="Cannot access account",
        description="My account is locked.",
    )


def test_run_stops_at_max_iterations() -> None:
    agent = build_agent(FakeLLM())

    state = agent.run(build_ticket())

    assert state.status == AgentStatus.MAX_ITERATIONS
    assert state.iteration == 6
    assert len(state.tool_calls) == 5
    assert state.final_response is None


def test_run_executes_tool_and_keeps_going() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action=AgentAction.SEARCH_KNOWLEDGE_BASE,
                reason="Need the password reset procedure.",
                tool_name="search_knowledge_base",
                tool_arguments={"query": "password reset"},
            ),
            AgentDecision(
                action=AgentAction.DRAFT_RESPONSE,
                reason="Found the reset steps.",
                response="Use the reset link on the login page.",
            ),
        ]
    )

    agent = build_agent(llm)

    state = agent.run(build_ticket())

    assert state.status == AgentStatus.COMPLETED
    assert state.iteration == 2
    assert len(state.tool_calls) == 1

    execution = state.tool_calls[0]

    assert execution.tool_name == "search_knowledge_base"
    assert execution.success is True
    assert execution.data is not None

    assert state.final_response == (
        "Use the reset link on the login page."
    )


def test_tool_result_reaches_next_prompt() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action=AgentAction.SEARCH_KNOWLEDGE_BASE,
                reason="Need the refund policy.",
                tool_name="search_knowledge_base",
                tool_arguments={"query": "refund policy"},
            ),
            AgentDecision(
                action=AgentAction.DRAFT_RESPONSE,
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
    retriever = KnowledgeRetriever(KnowledgeStore(default_documents()))

    memory = MemoryManager()
    memory.remember_fact("C-001", "plan", "premium")

    llm = ScriptedLLM(
        [
            AgentDecision(
                action=AgentAction.DRAFT_RESPONSE,
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
                action=AgentAction.ESCALATE,
                reason="Security incident.",
            )
        ]
    )

    agent = build_agent(llm)

    state = agent.run(build_ticket())

    assert state.status == AgentStatus.COMPLETED
    assert state.tool_calls == []
    assert "escalation" in state.final_response


def test_missing_tool_name_fails_the_run() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action=AgentAction.CREATE_TICKET,
                reason="Needs a tool but names none.",
            )
        ]
    )

    agent = build_agent(llm)

    state = agent.run(build_ticket())

    assert state.status == AgentStatus.FAILED
    assert state.error is not None
    assert "tool name" in state.error


def test_bad_tool_arguments_fail_the_run() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action=AgentAction.SEARCH_KNOWLEDGE_BASE,
                reason="Searches with no query.",
                tool_name="search_knowledge_base",
                tool_arguments={"limit": 99},
            )
        ]
    )

    agent = build_agent(llm)

    state = agent.run(build_ticket())

    assert state.status == AgentStatus.FAILED
    assert state.error is not None


def test_unknown_tool_fails_the_run() -> None:
    llm = ScriptedLLM(
        [
            AgentDecision(
                action=AgentAction.CREATE_TICKET,
                reason="Invents a tool.",
                tool_name="delete_everything",
                tool_arguments={},
            )
        ]
    )

    agent = build_agent(llm)

    state = agent.run(build_ticket())

    assert state.status == AgentStatus.FAILED
    assert "delete_everything" in state.error


def test_ticket_is_recorded_once_per_run() -> None:
    llm = FakeLLM()
    agent = build_agent(llm)

    agent.run(build_ticket())

    messages = agent.memory.get_conversation()

    user_messages = [
        message
        for message in messages
        if message.role == "user"
    ]

    assert len(user_messages) == 1


def test_decide_takes_state() -> None:
    agent = build_agent(FakeLLM())

    state = AgentState(ticket=build_ticket())

    decision = agent.decide(state)

    assert decision.action == AgentAction.CREATE_TICKET