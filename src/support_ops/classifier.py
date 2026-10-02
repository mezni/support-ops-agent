from support_ops.domain.ticket import (
    IncomingTicket,
    TicketClassification,
)
from support_ops.llm import LLMClient


class TicketClassifier:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def classify(
        self,
        ticket: IncomingTicket,
    ) -> TicketClassification:
        prompt = f"""
Classify the following customer support ticket.

Subject:
{ticket.subject}

Description:
{ticket.description}

Return JSON with exactly these fields:

{{
  "category": "billing|technical|account|security|general",
  "priority": "low|medium|high|critical",
  "sentiment": "positive|neutral|negative"
}}
"""

        result = self.llm.chat(prompt)

        # Temporary implementation.
        # We will replace this with proper structured
        # output validation in the next iteration.
        raise NotImplementedError(
            "Structured LLM parsing will be implemented next."
        )