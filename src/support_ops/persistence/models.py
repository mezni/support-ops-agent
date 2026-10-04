from dataclasses import dataclass


@dataclass
class EvaluationMetrics:
    total: int = 0
    passed: int = 0

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0

        return self.passed / self.total


def calculate_accuracy(
    expected: list,
    actual: list,
) -> float:
    if not expected:
        return 0.0

    matches = sum(
        1
        for expected_value, actual_value in zip(expected, actual)
        if expected_value == actual_value
    )

    return matches / len(expected)


SCHEMA = """
CREATE TABLE IF NOT EXISTS customer_memory (
    customer_id TEXT PRIMARY KEY,
    facts TEXT NOT NULL,
    preferences TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS customer_tickets (
    customer_id TEXT NOT NULL,
    ticket_id TEXT NOT NULL,
    PRIMARY KEY (customer_id, ticket_id)
);

CREATE TABLE IF NOT EXISTS traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    iteration INTEGER,
    timestamp TEXT NOT NULL,
    data TEXT NOT NULL
);
"""


def initialize_database(database) -> None:
    with database.connect() as connection:
        connection.executescript(SCHEMA)
        connection.commit()
