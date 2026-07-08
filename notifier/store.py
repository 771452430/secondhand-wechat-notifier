from __future__ import annotations

import sqlite3
from pathlib import Path


class NotificationStore:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        db_path = Path(sqlite_path)
        if db_path.parent and str(db_path.parent) != ".":
            db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(sqlite_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sent_notifications (
              dedupe_key TEXT PRIMARY KEY,
              source_name TEXT NOT NULL,
              item_id TEXT NOT NULL,
              sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS digest_runs (
              run_date TEXT PRIMARY KEY,
              sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def has_sent(self, dedupe_key: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM sent_notifications WHERE dedupe_key = ?",
            (dedupe_key,),
        ).fetchone()
        return row is not None

    def mark_sent(self, dedupe_key: str, source_name: str, item_id: str) -> None:
        self.conn.execute(
            """
            INSERT OR IGNORE INTO sent_notifications (dedupe_key, source_name, item_id)
            VALUES (?, ?, ?)
            """,
            (dedupe_key, source_name, item_id),
        )
        self.conn.commit()

    def has_digest_run(self, run_date: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM digest_runs WHERE run_date = ?",
            (run_date,),
        ).fetchone()
        return row is not None

    def mark_digest_run(self, run_date: str) -> None:
        self.conn.execute("INSERT OR IGNORE INTO digest_runs (run_date) VALUES (?)", (run_date,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
