from support_ops.knowledge.document import KnowledgeDocument


class KnowledgeStore:
    def __init__(
        self,
        documents: list[KnowledgeDocument],
    ):
        self.documents = documents

    def all(self) -> list[KnowledgeDocument]:
        return self.documents