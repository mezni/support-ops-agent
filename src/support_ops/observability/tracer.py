from __future__ import annotations


class TraceEvent:
    """Represents a single event in the agent's execution trace."""

    def __init__(
        self,
        event_type: str,
        run_id: str,
        iteration: int | None = None,
        data: dict | None = None,
        timestamp: str | None = None,
    ) -> None:
        self.event_type = event_type
        self.run_id = run_id
        self.iteration = iteration
        self.data = data or {}
        self.timestamp = timestamp or ""


class Tracer:
    """Collects execution events for observability.

    Can be used with or without a repository for persistence.
    Tests can use Tracer() without a repository,
    while production can use Tracer(repository=TraceRepository(Database())).
    """

    def __init__(self, repository=None) -> None:
        self._events: list = []
        self.repository = repository

    def record(
        self,
        event_type: str,
        run_id: str,
        iteration: int | None = None,
        data: dict | None = None,
    ) -> None:
        """Record an execution event.

        Args:
            event_type: Type of event (e.g., "decide", "execute_decision", "draft_response")
            run_id: Unique identifier for the current run
            iteration: Current iteration number (optional)
            data: Additional data about the event (optional)
        """
        event = TraceEvent(
            event_type=event_type,
            run_id=run_id,
            iteration=iteration,
            data=data or {},
        )

        self._events.append(event)

        if self.repository is not None:
            self.repository.save(event)

    @property
    def events(self) -> list:
        """Get all recorded events."""
        return self._events


class TraceRepository:
    """Persists trace events to a database."""

    def __init__(self, database) -> None:
        self.database = database

    def save(self, event: TraceEvent) -> None:
        """Save a trace event to the database."""
        from support_ops.persistence.database import Database

        if not isinstance(self.database, Database):
            raise TypeError("database must be a Database instance")

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
                    event.event_type,
                    event.iteration,
                    event.timestamp,
                    json.dumps(event.data),
                ),
            )

            connection.commit()

    def get_run(self, run_id: str) -> list[dict]:
        """Get all events for a specific run.

        Args:
            run_id: The run identifier to fetch events for

        Returns:
            List of event dictionaries
        """
        from support_ops.persistence.database import Database

        if not isinstance(self.database, Database):
            raise TypeError("database must be a Database instance")

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
