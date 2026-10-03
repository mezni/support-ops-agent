from dataclasses import dataclass


@dataclass
class ToolResult:
    success: bool
    message: str


def create_ticket(
    customer_id: str,
    subject: str,
    description: str,
) -> ToolResult:
    """
    Simulate creating a support ticket.
    """

    return ToolResult(
        success=True,
        message=(f"Ticket created for customer {customer_id}: {subject}"),
    )
