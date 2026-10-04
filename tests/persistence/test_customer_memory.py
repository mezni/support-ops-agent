from support_ops.memory.models import CustomerMemory
from support_ops.persistence.database import Database
from support_ops.persistence.models import (
    initialize_database,
)
from support_ops.persistence.repositories.customer_memory import (
    CustomerMemoryRepository,
)


def test_customer_memory_persistence(tmp_path):
    database = Database(str(tmp_path / "test.db"))

    initialize_database(database)

    repository = CustomerMemoryRepository(database)

    memory = CustomerMemory(
        customer_id="C-100",
        facts={"plan": "enterprise"},
    )

    repository.save(memory)

    loaded = repository.get("C-100")

    assert loaded is not None
    assert loaded.customer_id == "C-100"
    assert loaded.facts["plan"] == "enterprise"
