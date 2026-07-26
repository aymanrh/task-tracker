"""Shared pytest fixtures.

Each test gets a fresh SQLite database in a temp directory, so tests never
touch the real task_tracker.db and stay isolated from one another.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("TASK_TRACKER_DB", str(db_file))

    from app.db import init_db

    init_db()

    from app.main import app

    with TestClient(app) as c:
        yield c
