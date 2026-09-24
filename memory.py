import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import DB_PATH


class Memory:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def set(self, key: str, value: str) -> None:
        self.conn.execute(
            """
            INSERT INTO memory(key, value, updated_at)
            VALUES(?, ?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
            """,
            (key, value, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get(self, key: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT value FROM memory WHERE key = ?",
            (key,),
        ).fetchone()
        return row[0] if row else None

    def add_history(self, user_message: str, assistant_message: str) -> None:
        self.conn.execute(
            "INSERT INTO history(user_message, assistant_message, created_at) VALUES(?, ?, ?)",
            (user_message, assistant_message, datetime.now().isoformat()),
        )
        self.conn.commit()

    def recent_history(self, limit: int = 5):
        rows = self.conn.execute(
            "SELECT user_message, assistant_message FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return list(reversed(rows))

    def close(self) -> None:
        self.conn.close()
