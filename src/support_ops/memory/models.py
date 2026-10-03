from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CustomerMemory(BaseModel):
    customer_id: str

    preferences: dict[str, str] = Field(default_factory=dict)
    facts: dict[str, str] = Field(default_factory=dict)

    previous_tickets: list[str] = Field(default_factory=list)

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
