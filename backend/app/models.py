"""Pydantic models for the Task Tracker.

Baseline (Modules 1-3): title, description, status, priority, assignee.
"""
from datetime import date
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


MAX_TAGS = 10
MAX_TAG_LEN = 30


def _clean_str(v: str) -> str:
    return v.strip() if isinstance(v, str) else v


def _clean_tags(v):
    """Trim tags, reject blank/comma/over-long, dedupe, cap the count."""
    if v is None:
        return v
    cleaned: list[str] = []
    for tag in v:
        t = tag.strip() if isinstance(tag, str) else tag
        if not t:
            raise ValueError("tags must not be blank")
        if "," in t:
            raise ValueError("tags must not contain commas")
        if len(t) > MAX_TAG_LEN:
            raise ValueError(f"tag too long (max {MAX_TAG_LEN} chars)")
        if t not in cleaned:
            cleaned.append(t)
    if len(cleaned) > MAX_TAGS:
        raise ValueError(f"too many tags (max {MAX_TAGS})")
    return cleaned


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: Status = Status.todo
    priority: Priority = Priority.medium
    assignee: str = ""
    due_date: date | None = None
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = _clean_str(v)
        if not v:
            raise ValueError("title must not be blank")
        return v

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, v):
        return _clean_tags(v)


class TaskUpdate(BaseModel):
    """Partial update. Every field is optional; only provided fields change."""

    title: str | None = None
    description: str | None = None
    status: Status | None = None
    priority: Priority | None = None
    assignee: str | None = None
    due_date: date | None = None
    tags: list[str] | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v):
        # This validator runs only when `title` is explicitly provided (an
        # omitted field keeps its default and is skipped). So an incoming None
        # here is an explicit `"title": null`, which would violate the NOT NULL
        # column downstream -- reject it as a validation error, not a DB crash.
        if v is None:
            raise ValueError("title must not be null")
        v = _clean_str(v)
        if not v:
            raise ValueError("title must not be blank")
        return v

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, v):
        return _clean_tags(v)


class Task(BaseModel):
    id: int
    title: str
    description: str
    status: Status
    priority: Priority
    assignee: str
    due_date: date | None = None
    overdue: bool = False
    tags: list[str] = []
    created_at: str
    updated_at: str
