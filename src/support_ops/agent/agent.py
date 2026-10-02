import json

from support_ops.domain.ticket import AgentAction, AgentDecision, AgentActionResult, IncomingTicket


class SupportAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def decide(self, ticket: IncomingTicket) -> AgentDecision:
        response_str = self.llm_client.structured(
            f"Given the incoming ticket: {ticket.subject} - {ticket.description}, what action should the agent take? Respond in JSON format with 'action' (from {list(AgentAction)}) and 'reason'.",
            AgentDecision
        )
        return response_str

    def execute(self, ticket: IncomingTicket, decision: AgentDecision) -> AgentActionResult:
        # Placeholder implementation for now
        # This will be refined as the agent's logic is developed
        if decision.action == AgentAction.CREATE_TICKET:
            return AgentActionResult(success=True, message=f"Ticket created for customer {ticket.customer_id}")
        return AgentActionResult(success=False, message="Unknown action")
