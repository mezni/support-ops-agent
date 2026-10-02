import pytest
from pydantic import ValidationError

from support_ops.domain.ticket import (
    IncomingTicket,
    SupportTicket,
    TicketCategory,
    TicketPriority,
)


def test_create_support_ticket() -> None:
    ticket = SupportTicket(
        id="T-001",
        customer_id="C-001",
        subject="Billing issue",
        description="I was charged twice.",
        category=TicketCategory.BILLING,
        priority=TicketPriority.HIGH,
    )

    assert ticket.category == TicketCategory.BILLING
    assert ticket.priority == TicketPriority.HIGH


def test_invalid_category() -> None:
    with pytest.raises(ValidationError):
        SupportTicket(
            id="T-001",
            customer_id="C-001",
            subject="Test",
            description="Test",
            category="something_invalid",
            priority=TicketPriority.LOW,
        )