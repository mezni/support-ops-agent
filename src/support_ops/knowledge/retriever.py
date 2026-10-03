from dataclasses import dataclass

from support_ops.knowledge.document import KnowledgeDocument
from support_ops.knowledge.store import KnowledgeStore


@dataclass
class SearchResult:
    document: KnowledgeDocument
    score: float


class KnowledgeRetriever:
    def __init__(self, store: KnowledgeStore):
        self.store = store

    def search(
        self,
        query: str,
        limit: int = 3,
    ) -> list[SearchResult]:

        query_words = set(query.lower().split())

        results: list[SearchResult] = []

        for document in self.store.all():
            text = (
                f"{document.title} "
                f"{document.category} "
                f"{document.content}"
            ).lower()

            document_words = set(text.split())

            overlap = query_words & document_words

            score = len(overlap)

            if score > 0:
                results.append(
                    SearchResult(
                        document=document,
                        score=float(score),
                    )
                )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]