from support_ops.agent.agent import SupportAgent
from support_ops.domain.ticket import (
    AgentAction,
    AgentDecision,
    IncomingTicket,
)


class FakeLLM:
    def chat(self, message: str) -> str:
        return """
        {
            "action": "create_ticket",
            "reason": "The issue requires investigation."
        }
        """


def test_agent_can_execute_create_ticket() -> None:
    agent = SupportAgent(FakeLLM())

    ticket = IncomingTicket(
        id="T-001",
        customer_id="C-001",
        subject="Cannot access account",
        description="My account is locked.",
    )

    decision = AgentDecision(
        action=AgentAction.CREATE_TICKET,
        reason="The issue requires investigation.",
    )

    result = agent.execute(ticket, decision)

    assert result.success is True
    assert "C-001" in result.message