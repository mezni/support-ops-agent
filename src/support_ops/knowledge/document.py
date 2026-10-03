from pydantic import BaseModel


class KnowledgeDocument(BaseModel):
    id: str
    title: str
    content: str
    category: str