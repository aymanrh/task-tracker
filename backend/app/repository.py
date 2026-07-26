"""Data-access layer for tasks.

All SQL lives here. Routes in main.py call these functions and never touch the
database directly. Each function returns plain dicts already enriched with the
computed `overdue` flag and a `tags` list.
"""
from datetime import date

from .db import get_conn, now_iso, row_to_dict
from .models import Priority, Status, TaskCreate, TaskUpdate


def is_overdue(due_date: str | None, status: str) -> bool:
    """A task is overdue if it has a past due date and is not done."""
    if not due_date or status == Status.done.value:
        return False
    return due_date < date.today().isoformat()


def enrich(task: dict) -> dict:
    """Turn a raw DB row into an API-shaped dict.

    Adds the computed `overdue` flag and expands the comma-separated `tags`
    column into a list.
    """
    task["overdue"] = is_overdue(task.get("due_date"), task["status"])
    raw_tags = task.get("tags") or ""
    task["tags"] = [t for t in raw_tags.split(",") if t]
    return task


def _fetch(conn, task_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return enrich(row_to_dict(row)) if row else None


def create(payload: TaskCreate) -> dict:
    ts = now_iso()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO tasks (title, description, status, priority, assignee,
                               due_date, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.title,
                payload.description,
                payload.status.value,
                payload.priority.value,
                payload.assignee,
                payload.due_date.isoformat() if payload.due_date else None,
                ",".join(payload.tags),
                ts,
                ts,
            ),
        )
        conn.commit()
        return _fetch(conn, cur.lastrowid)


def list_all(
    status: Status | None = None,
    priority: Priority | None = None,
    assignee: str | None = None,
    overdue: bool | None = None,
    tag: str | None = None,
) -> list[dict]:
    clauses, params = [], []
    if status is not None:
        clauses.append("status = ?")
        params.append(status.value)
    if priority is not None:
        clauses.append("priority = ?")
        params.append(priority.value)
    if assignee is not None:
        clauses.append("assignee = ?")
        params.append(assignee)
    if tag:
        # Match a whole tag, not a substring, by wrapping both sides in commas.
        clauses.append("(',' || COALESCE(tags, '') || ',') LIKE ?")
        params.append(f"%,{tag},%")
    if overdue:
        # Overdue = past due date and not done. Matches is_overdue().
        clauses.append("due_date IS NOT NULL AND due_date < ? AND status != ?")
        params.append(date.today().isoformat())
        params.append(Status.done.value)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT * FROM tasks{where} ORDER BY id", params
        ).fetchall()
        return [enrich(row_to_dict(r)) for r in rows]


def get(task_id: int) -> dict | None:
    with get_conn() as conn:
        return _fetch(conn, task_id)


def update(task_id: int, payload: TaskUpdate) -> dict | None:
    fields = payload.model_dump(exclude_unset=True)
    with get_conn() as conn:
        if _fetch(conn, task_id) is None:
            return None
        if fields:
            sets, params = [], []
            for key, value in fields.items():
                if isinstance(value, (Status, Priority)):
                    value = value.value
                elif isinstance(value, date):
                    value = value.isoformat()
                elif isinstance(value, list):
                    value = ",".join(value)
                sets.append(f"{key} = ?")
                params.append(value)
            sets.append("updated_at = ?")
            params.append(now_iso())
            params.append(task_id)
            conn.execute(
                f"UPDATE tasks SET {', '.join(sets)} WHERE id = ?", params
            )
            conn.commit()
        return _fetch(conn, task_id)


def delete(task_id: int) -> bool:
    with get_conn() as conn:
        if _fetch(conn, task_id) is None:
            return False
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return True
