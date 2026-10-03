from support_ops.knowledge.retriever import KnowledgeRetriever
from support_ops.knowledge.seed import default_documents
from support_ops.knowledge.store import KnowledgeStore


def test_search_finds_billing_document() -> None:
    store = KnowledgeStore(default_documents())

    retriever = KnowledgeRetriever(store)

    results = retriever.search("customer charged twice")

    assert len(results) > 0

    assert results[0].document.id == "KB-002"
