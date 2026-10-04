from support_ops.agent.agent import SupportAgent
from support_ops.application.service import SupportApplication
from support_ops.config import Settings
from support_ops.guardrails.authorization import AuthorizationService
from support_ops.knowledge.retriever import KnowledgeRetriever
from support_ops.knowledge.seed import seed_documents
from support_ops.knowledge.store import KnowledgeStore
from support_ops.llm import LLMClient
from support_ops.memory.manager import MemoryManager
from support_ops.observability.tracer import Tracer
from support_ops.persistence.database import Database, initialize_database
from support_ops.tools.registry import create_default_registry


def create_application(settings: Settings) -> SupportApplication:
    database = Database(settings.database_path)
    initialize_database(database)

    llm = LLMClient(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
    )

    memory = MemoryManager()

    tracer = Tracer()

    knowledge_store = KnowledgeStore()
    seed_documents(knowledge_store)

    retriever = KnowledgeRetriever(knowledge_store)

    tools = create_default_registry(retriever)

    authorization = AuthorizationService()

    agent = SupportAgent(
        llm=llm,
        tools=tools,
        memory=memory,
        authorization=authorization,
        tracer=tracer,
        max_iterations=settings.max_agent_iterations,
    )

    return SupportApplication(agent)
