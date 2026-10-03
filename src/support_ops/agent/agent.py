from support_ops.domain.ticket import (
    AgentAction,
    AgentDecision,
    IncomingTicket,
)
from support_ops.llm import LLMClient
from support_ops.tools.base import ToolResult
from support_ops.tools.registry import ToolRegistry


class SupportAgent:
    def __init__(
        self,
        llm: LLMClient,
        tools: ToolRegistry,
    ):
        self.llm = llm
        self.tools = tools

    def decide(
        self,
        ticket: IncomingTicket,
    ) -> AgentDecision:

        prompt = f"""
You are a customer support agent.

Analyze this support ticket.

Customer ID:
{ticket.customer_id}

Subject:
{ticket.subject}

Description:
{ticket.description}

Choose one action:

- draft_response
- create_ticket
- escalate

Provide a short reason.

Return JSON with exactly these fields:

{{
  "action": "draft_response|create_ticket|escalate",
  "reason": "short explanation"
}}
"""

        return self.llm.structured(
            prompt,
            AgentDecision,
        )

    def execute(
        self,
        ticket: IncomingTicket,
        decision: AgentDecision,
    ) -> ToolResult | str:

        if decision.action == AgentAction.CREATE_TICKET:
            tool = self.tools.get("create_ticket")

            arguments = tool.argument_schema()(
                customer_id=ticket.customer_id,
                subject=ticket.subject,
                description=ticket.description,
            )

            return tool.execute(arguments)

        if decision.action == AgentAction.DRAFT_RESPONSE:
            return "Response drafting will be implemented next."

        if decision.action == AgentAction.ESCALATE:
            return "Human escalation will be implemented next."

        raise ValueError(f"Unsupported action: {decision.action}")

    def run(
        self,
        ticket: IncomingTicket,
    ) -> ToolResult | str:

        decision = self.decide(ticket)

        return self.execute(ticket, decision)
