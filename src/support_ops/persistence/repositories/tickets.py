class TicketRepository:
    def __init__(self, database) -> None:
        self.database = database

    def add_customer_ticket(
        self,
        customer_id: str,
        ticket_id: str,
    ) -> None:

        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO customer_tickets (
                    customer_id,
                    ticket_id
                )
                VALUES (?, ?)
                """,
                (
                    customer_id,
                    ticket_id,
                ),
            )

            connection.commit()

    def get_customer_tickets(
        self,
        customer_id: str,
    ) -> list[str]:

        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT ticket_id
                FROM customer_tickets
                WHERE customer_id = ?
                ORDER BY ticket_id
                """,
                (customer_id,),
            ).fetchall()

        return [row["ticket_id"] for row in rows]
