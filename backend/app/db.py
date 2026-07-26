"""SQLite storage layer for the Task Tracker.

Kept intentionally small: plain sqlite3, no ORM. The database path is read from
the TASK_TRACKER_DB environment variable so tests can point it at a temporary
file (see backend/tests/conftest.py).
"""
import os
import sqlite3
from datetime import datetime, timezone


def db_path() -> str:
    return os.environ.get("TASK_TRACKER_DB", "task_tracker.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db() -> None:
    """Create the tasks table if it does not exist."""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status      TEXT NOT NULL DEFAULT 'todo',
                priority    TEXT NOT NULL DEFAULT 'medium',
                assignee    TEXT NOT NULL DEFAULT '',
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            )
            """
        )
        conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict:
    return {k: row[k] for k in row.keys()}
