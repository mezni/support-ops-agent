import pytest
from pydantic import ValidationError

from support_ops.tools.create_ticket import (
    CreateTicketInput,
    CreateTicketTool,
)


def test_create_ticket_tool() -> None:
    tool = CreateTicketTool()

    arguments = CreateTicketInput(
        customer_id="C-001",
        subject="Billing problem",
        description="I was charged twice.",
    )

    result = tool.execute(arguments)

    assert result.success is True
    assert result.data is not None
    assert result.data["customer_id"] == "C-001"


def test_create_ticket_requires_customer_id() -> None:
    with pytest.raises(ValidationError):
        CreateTicketInput(
            subject="Billing problem",
            description="I was charged twice.",
        )
