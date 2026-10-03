from support_ops.knowledge.retriever import KnowledgeRetriever
from support_ops.tools.base import Tool
from support_ops.tools.create_ticket import CreateTicketTool
from support_ops.tools.search_knowledge_base import (
    SearchKnowledgeBaseTool,
)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError:
            raise ValueError(f"Unknown tool: {name}") from None

    def list(self) -> list[Tool]:
        return list(self._tools.values())


def create_default_registry(
    retriever: KnowledgeRetriever,
) -> ToolRegistry:

    registry = ToolRegistry()

    registry.register(CreateTicketTool())
    registry.register(SearchKnowledgeBaseTool(retriever))

    return registry
