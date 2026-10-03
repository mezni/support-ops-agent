from enum import StrEnum

from pydantic import BaseModel, Field


class TicketCategory(StrEnum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    SECURITY = "security"
    GENERAL = "general"


class TicketPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class SupportTicket(BaseModel):
    id: str
    customer_id: str
    subject: str
    description: str

    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus = TicketStatus.NEW

    sentiment: str | None = None


class IncomingTicket(BaseModel):
    id: str
    customer_id: str
    subject: str
    description: str


class TicketClassification(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    sentiment: str


class AgentAction(StrEnum):
    DRAFT_RESPONSE = "draft_response"
    CREATE_TICKET = "create_ticket"
    ESCALATE = "escalate"


class AgentDecision(BaseModel):
    action: AgentAction
    reason: str
