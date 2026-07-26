"""Task Tracker API (baseline, Modules 1-3).

CRUD over tasks, backed by SQLite. A tiny Kanban frontend in ../frontend
talks to these endpoints.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .db import get_conn, init_db, now_iso, row_to_dict
from .models import Status, Priority, Task, TaskCreate, TaskUpdate


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
    return row_to_dict(row) if row else None


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: TaskCreate) -> dict:
    ts = now_iso()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO tasks (title, description, status, priority, assignee,
                               created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.title,
                payload.description,
                payload.status.value,
                payload.priority.value,
                payload.assignee,
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
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT * FROM tasks{where} ORDER BY id", params
        ).fetchall()
        return [row_to_dict(r) for r in rows]


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
