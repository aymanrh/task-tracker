"""Task Tracker API.

Thin HTTP layer: each route delegates to the repository module for data access.
Baseline (Modules 1-3) is CRUD over tasks; the mid-course project adds due
dates (Feature 1) and tags (Feature 2). A tiny Kanban frontend in ../frontend
talks to these endpoints.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import repository as repo
from .db import init_db
from .models import Priority, Status, Task, TaskCreate, TaskUpdate


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


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: TaskCreate) -> dict:
    return repo.create(payload)


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    status: Status | None = None,
    priority: Priority | None = None,
    assignee: str | None = None,
    overdue: bool | None = None,
    tag: str | None = None,
) -> list[dict]:
    return repo.list_all(status, priority, assignee, overdue, tag)


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> dict:
    task = repo.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> dict:
    task = repo.update(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    if not repo.delete(task_id):
        raise HTTPException(status_code=404, detail="task not found")
