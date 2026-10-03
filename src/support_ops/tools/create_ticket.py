from pydantic import BaseModel, Field

from support_ops.tools.base import Tool, ToolResult


class CreateTicketInput(BaseModel):
    customer_id: str = Field(description="The customer identifier.")

    subject: str = Field(description="Short description of the support issue.")

    description: str = Field(description="Detailed description of the support issue.")


class CreateTicketTool(Tool):
    name = "create_ticket"

    description = "Create a support ticket for an unresolved customer issue."

    def argument_schema(self) -> type[CreateTicketInput]:
        return CreateTicketInput

    def execute(
        self,
        arguments: CreateTicketInput,
    ) -> ToolResult:

        ticket_id = "T-NEW-001"

        return ToolResult(
            success=True,
            message=f"Support ticket {ticket_id} created.",
            data={
                "ticket_id": ticket_id,
                "customer_id": arguments.customer_id,
            },
        )
