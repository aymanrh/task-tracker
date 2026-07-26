"""Pydantic models for the Task Tracker.

Baseline (Modules 1-3): title, description, status, priority, assignee.
"""
from enum import Enum

from pydantic import BaseModel, field_validator


class Status(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


def _clean_str(v: str) -> str:
    return v.strip() if isinstance(v, str) else v


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: Status = Status.todo
    priority: Priority = Priority.medium
    assignee: str = ""

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = _clean_str(v)
        if not v:
            raise ValueError("title must not be blank")
        return v


class TaskUpdate(BaseModel):
    """Partial update. Every field is optional; only provided fields change."""

    title: str | None = None
    description: str | None = None
    status: Status | None = None
    priority: Priority | None = None
    assignee: str | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v):
        if v is None:
            return v
        v = _clean_str(v)
        if not v:
            raise ValueError("title must not be blank")
        return v


class Task(BaseModel):
    id: int
    title: str
    description: str
    status: Status
    priority: Priority
    assignee: str
    created_at: str
    updated_at: str
