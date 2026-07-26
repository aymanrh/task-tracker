"""Task Tracker API (baseline, Modules 1-3).

CRUD over tasks, backed by SQLite. A tiny Kanban frontend in ../frontend
talks to these endpoints.
"""
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .db import get_conn, init_db, now_iso, row_to_dict
from .models import Status, Priority, Task, TaskCreate, TaskUpdate


def is_overdue(due_date: str | None, status: str) -> bool:
    """A task is overdue if it has a past due date and is not done."""
    if not due_date or status == Status.done.value:
        return False
    return due_date < date.today().isoformat()


def enrich(task: dict) -> dict:
    """Add computed fields (overdue) to a raw task row."""
    task["overdue"] = is_overdue(task.get("due_date"), task["status"])
    return task


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Task Tracker", version="1.0.0", lifespan=lifespan)

# The static frontend is opened straight from the filesystem, so allow any
# origin for these local, non-sensitive endpoints.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _fetch_task(conn, task_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return enrich(row_to_dict(row)) if row else None


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: TaskCreate) -> dict:
    ts = now_iso()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO tasks (title, description, status, priority, assignee,
                               due_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.title,
                payload.description,
                payload.status.value,
                payload.priority.value,
                payload.assignee,
                payload.due_date.isoformat() if payload.due_date else None,
                ts,
                ts,
            ),
        )
        conn.commit()
        return _fetch_task(conn, cur.lastrowid)


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    status: Status | None = None,
    priority: Priority | None = None,
    assignee: str | None = None,
    overdue: bool | None = None,
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


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> dict:
    with get_conn() as conn:
        task = _fetch_task(conn, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> dict:
    fields = payload.model_dump(exclude_unset=True)
    with get_conn() as conn:
        existing = _fetch_task(conn, task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="task not found")
        if fields:
            sets, params = [], []
            for key, value in fields.items():
                if isinstance(value, (Status, Priority)):
                    value = value.value
                elif isinstance(value, date):
                    value = value.isoformat()
                sets.append(f"{key} = ?")
                params.append(value)
            sets.append("updated_at = ?")
            params.append(now_iso())
            params.append(task_id)
            conn.execute(
                f"UPDATE tasks SET {', '.join(sets)} WHERE id = ?", params
            )
            conn.commit()
        return _fetch_task(conn, task_id)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    with get_conn() as conn:
        existing = _fetch_task(conn, task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="task not found")
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
