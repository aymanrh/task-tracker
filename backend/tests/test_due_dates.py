"""Feature 1: due dates + overdue filter."""
from datetime import date, timedelta

YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()


def test_create_task_with_valid_due_date(client):
    r = client.post("/tasks", json={"title": "Ship", "due_date": TOMORROW})
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] == TOMORROW
    assert body["overdue"] is False


def test_invalid_due_date_format_is_422(client):
    r = client.post("/tasks", json={"title": "Ship", "due_date": "31-12-2026"})
    assert r.status_code == 422


def test_overdue_flag_true_for_past_due_and_not_done(client):
    r = client.post("/tasks", json={"title": "Late", "due_date": YESTERDAY})
    assert r.json()["overdue"] is True


def test_overdue_flag_false_when_done(client):
    r = client.post(
        "/tasks",
        json={"title": "Late but done", "due_date": YESTERDAY, "status": "done"},
    )
    assert r.json()["overdue"] is False


def test_overdue_filter_returns_only_overdue(client):
    client.post("/tasks", json={"title": "past", "due_date": YESTERDAY})
    client.post("/tasks", json={"title": "future", "due_date": TOMORROW})
    client.post("/tasks", json={"title": "no date"})

    overdue = client.get("/tasks", params={"overdue": "true"}).json()
    assert [t["title"] for t in overdue] == ["past"]


def test_update_due_date(client):
    task_id = client.post("/tasks", json={"title": "Move it"}).json()["id"]
    r = client.put(f"/tasks/{task_id}", json={"due_date": TOMORROW})
    assert r.status_code == 200
    assert r.json()["due_date"] == TOMORROW
