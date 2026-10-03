from support_ops.agent.tools import ToolResult, create_ticket
from support_ops.domain.ticket import (
    AgentAction,
    AgentDecision,
    IncomingTicket,
)
from support_ops.llm import LLMClient


class SupportAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def decide(
        self,
        ticket: IncomingTicket,
    ) -> AgentDecision:
        prompt = f"""
You are a customer support agent.

Analyze this support ticket:

Customer ID:
{ticket.customer_id}

Subject:
{ticket.subject}

Description:
{ticket.description}

Choose exactly one action:

- draft_response
- create_ticket
- escalate

Return JSON:

{{
  "action": "...",
  "reason": "..."
}}
"""

        result = self.llm.chat(prompt)

        # Temporary.
        # Structured parsing will be implemented later.
        raise NotImplementedError(f"Model decision received: {result}")

    def execute(
        self,
        ticket: IncomingTicket,
        decision: AgentDecision,
    ) -> ToolResult | str:

        if decision.action == AgentAction.CREATE_TICKET:
            return create_ticket(
                customer_id=ticket.customer_id,
                subject=ticket.subject,
                description=ticket.description,
            )

        if decision.action == AgentAction.DRAFT_RESPONSE:
            return "Response drafting will be implemented next."

        if decision.action == AgentAction.ESCALATE:
            return "Human escalation will be implemented next."

        raise ValueError(f"Unsupported action: {decision.action}")
