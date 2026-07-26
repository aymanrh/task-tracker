"""Baseline CRUD tests (Modules 1-3)."""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_task_defaults(client):
    r = client.post("/tasks", json={"title": "Write report"})
    assert r.status_code == 201
    body = r.json()
    assert body["id"] > 0
    assert body["title"] == "Write report"
    assert body["status"] == "todo"
    assert body["priority"] == "medium"
    assert body["created_at"] == body["updated_at"]


def test_create_task_rejects_blank_title(client):
    r = client.post("/tasks", json={"title": "   "})
    assert r.status_code == 422


def test_list_tasks_and_filter_by_status(client):
    client.post("/tasks", json={"title": "A", "status": "todo"})
    client.post("/tasks", json={"title": "B", "status": "done"})

    all_tasks = client.get("/tasks").json()
    assert len(all_tasks) == 2

    done = client.get("/tasks", params={"status": "done"}).json()
    assert [t["title"] for t in done] == ["B"]


def test_get_task_404(client):
    assert client.get("/tasks/999").status_code == 404


def test_update_task(client):
    task_id = client.post("/tasks", json={"title": "Draft"}).json()["id"]
    r = client.put(f"/tasks/{task_id}", json={"status": "in_progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"
    # unchanged fields survive a partial update
    assert r.json()["title"] == "Draft"


def test_delete_task(client):
    task_id = client.post("/tasks", json={"title": "Temp"}).json()["id"]
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404
