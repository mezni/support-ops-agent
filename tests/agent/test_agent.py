from support_ops.agent.agent import SupportAgent
from support_ops.domain.ticket import IncomingTicket

from tests.agent.fakes import FakeLLM


def test_agent_decides_and_executes() -> None:
    agent = SupportAgent(FakeLLM())

    ticket = IncomingTicket(
        id="T-001",
        customer_id="C-001",
        subject="Cannot access account",
        description="My account is locked.",
    )

    decision = agent.decide(ticket)

    assert decision.action.value == "create_ticket"

    result = agent.execute(ticket, decision)

    assert result.success is True
    assert "C-001" in result.message
