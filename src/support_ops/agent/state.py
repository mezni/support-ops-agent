from enum import Enum

from pydantic import BaseModel, Field

from support_ops.domain.ticket import IncomingTicket


class AgentStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    MAX_ITERATIONS = "max_iterations"


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict = Field(default_factory=dict)


class ToolExecution(BaseModel):
    tool_name: str
    arguments: dict = Field(default_factory=dict)
    success: bool
    result: str
    data: dict | None = None


class AgentState(BaseModel):
    ticket: IncomingTicket

    status: AgentStatus = AgentStatus.RUNNING

    iteration: int = 0
    max_iterations: int = 5

    tool_calls: list[ToolExecution] = Field(default_factory=list)

    final_response: str | None = None
    error: str | None = None
