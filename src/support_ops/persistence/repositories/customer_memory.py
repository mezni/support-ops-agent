import json

from support_ops.memory.models import CustomerMemory


class CustomerMemoryRepository:
    def __init__(self, database) -> None:
        self.database = database

    def save(
        self,
        memory: CustomerMemory,
    ) -> None:

        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO customer_memory (
                    customer_id,
                    facts,
                    preferences,
                    updated_at
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(customer_id)
                DO UPDATE SET
                    facts = excluded.facts,
                    preferences = excluded.preferences,
                    updated_at = excluded.updated_at
                """,
                (
                    memory.customer_id,
                    json.dumps(memory.facts),
                    json.dumps(memory.preferences),
                    memory.updated_at.isoformat(),
                ),
            )

            connection.commit()

    def get(
        self,
        customer_id: str,
    ) -> CustomerMemory | None:

        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    customer_id,
                    facts,
                    preferences,
                    updated_at
                FROM customer_memory
                WHERE customer_id = ?
                """,
                (customer_id,),
            ).fetchone()

        if row is None:
            return None

        return CustomerMemory(
            customer_id=row["customer_id"],
            facts=json.loads(row["facts"]),
            preferences=json.loads(row["preferences"]),
            updated_at=row["updated_at"],
        )
