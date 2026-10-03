from pydantic import BaseModel, Field

from support_ops.knowledge.retriever import KnowledgeRetriever
from support_ops.tools.base import Tool, ToolResult


class SearchKnowledgeBaseInput(BaseModel):
    query: str = Field(description="The question or issue to search for.")

    limit: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of results to return.",
    )


class SearchKnowledgeBaseTool(Tool):
    name = "search_knowledge_base"

    description = (
        "Search the support knowledge base for information "
        "relevant to a customer issue."
    )

    def __init__(self, retriever: KnowledgeRetriever):
        self.retriever = retriever

    def argument_schema(
        self,
    ) -> type[SearchKnowledgeBaseInput]:
        return SearchKnowledgeBaseInput

    def execute(
        self,
        arguments: SearchKnowledgeBaseInput,
    ) -> ToolResult:

        results = self.retriever.search(
            query=arguments.query,
            limit=arguments.limit,
        )

        data = [
            {
                "document_id": result.document.id,
                "title": result.document.title,
                "content": result.document.content,
                "score": result.score,
            }
            for result in results
        ]

        return ToolResult(
            success=True,
            message=f"Found {len(data)} knowledge documents.",
            data={
                "results": data,
            },
        )
