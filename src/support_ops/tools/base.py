from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ToolResult(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] | None = None


class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    def execute(self, arguments: BaseModel) -> ToolResult:
        pass

    @abstractmethod
    def argument_schema(self) -> type[BaseModel]:
        pass
