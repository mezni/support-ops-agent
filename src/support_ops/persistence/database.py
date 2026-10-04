import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: str = "data/support_ops.db") -> None:
        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
        )

        connection.row_factory = sqlite3.Row

        return connection
