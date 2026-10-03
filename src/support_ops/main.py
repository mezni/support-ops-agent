from support_ops.agent.agent import SupportAgent
from support_ops.config import Settings
from support_ops.domain.ticket import IncomingTicket
from support_ops.knowledge.retriever import KnowledgeRetriever
from support_ops.knowledge.seed import default_documents
from support_ops.knowledge.store import KnowledgeStore
from support_ops.llm import LLMClient
from support_ops.tools.registry import create_default_registry


def main() -> None:
    settings = Settings()

    llm = LLMClient(settings)

    store = KnowledgeStore(
        default_documents()
    )

    retriever = KnowledgeRetriever(store)

    tools = create_default_registry(
        retriever
    )

    agent = SupportAgent(
        llm=llm,
        tools=tools,
    )

    ticket = IncomingTicket(
        id="T-001",
        customer_id="C-001",
        subject="I was charged twice",
        description=(
            "I noticed two charges for my subscription."
        ),
    )

    result = agent.run(ticket)

    print(result)


if __name__ == "__main__":
    main()