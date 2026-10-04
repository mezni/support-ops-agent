from dataclasses import dataclass

from support_ops.domain.ticket import (
    AgentAction,
    TicketCategory,
    TicketPriority,
)


@dataclass(frozen=True)
class EvaluationCase:
    name: str
    customer_id: str
    subject: str
    description: str

    expected_category: TicketCategory | None = None
    expected_priority: TicketPriority | None = None
    expected_action: AgentAction | None = None


EVALUATION_CASES = [
    EvaluationCase(
        name="duplicate_billing",
        customer_id="C-001",
        subject="Charged twice",
        description=("I was charged twice for the same subscription."),
        expected_category=TicketCategory.BILLING,
        expected_priority=TicketPriority.MEDIUM,
        expected_action=AgentAction.SEARCH_KNOWLEDGE_BASE,
    ),
    EvaluationCase(
        name="account_locked",
        customer_id="C-002",
        subject="Cannot access my account",
        description=("My account is locked and I cannot sign in."),
        expected_category=TicketCategory.ACCOUNT,
        expected_priority=TicketPriority.HIGH,
        expected_action=AgentAction.SEARCH_KNOWLEDGE_BASE,
    ),
    EvaluationCase(
        name="security_incident",
        customer_id="C-003",
        subject="Possible account compromise",
        description=("I believe someone gained unauthorized access to my account."),
        expected_category=TicketCategory.SECURITY,
        expected_priority=TicketPriority.CRITICAL,
        expected_action=AgentAction.ESCALATE,
    ),
    EvaluationCase(
        name="general_question",
        customer_id="C-004",
        subject="Question about the service",
        description=("Can you tell me more about your service?"),
        expected_category=TicketCategory.GENERAL,
        expected_priority=TicketPriority.LOW,
        expected_action=AgentAction.DRAFT_RESPONSE,
    ),
]
