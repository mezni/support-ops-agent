import json


class TraceRepository:
    def __init__(self, database) -> None:
        self.database = database

    def save(self, event) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO traces (
                    run_id,
                    event_type,
                    iteration,
                    timestamp,
                    data
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event.run_id,
                    event.event_type.value,
                    event.iteration,
                    event.timestamp.isoformat(),
                    json.dumps(event.data),
                ),
            )

            connection.commit()

    def get_run(
        self,
        run_id: str,
    ) -> list[dict]:

        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    run_id,
                    event_type,
                    iteration,
                    timestamp,
                    data
                FROM traces
                WHERE run_id = ?
                ORDER BY id
                """,
                (run_id,),
            ).fetchall()

        return [dict(row) for row in rows]
