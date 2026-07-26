"""Feature 2: tags / labels."""


def test_create_task_with_tags(client):
    r = client.post("/tasks", json={"title": "Design", "tags": ["ui", "urgent"]})
    assert r.status_code == 201
    assert r.json()["tags"] == ["ui", "urgent"]


def test_tags_are_trimmed_and_deduped(client):
    r = client.post("/tasks", json={"title": "T", "tags": [" ui ", "ui", "api"]})
    assert r.json()["tags"] == ["ui", "api"]


def test_reject_blank_tag(client):
    r = client.post("/tasks", json={"title": "T", "tags": ["ok", "   "]})
    assert r.status_code == 422


def test_filter_by_tag(client):
    client.post("/tasks", json={"title": "A", "tags": ["backend"]})
    client.post("/tasks", json={"title": "B", "tags": ["frontend"]})
    client.post("/tasks", json={"title": "C", "tags": ["backend", "urgent"]})

    backend = client.get("/tasks", params={"tag": "backend"}).json()
    assert sorted(t["title"] for t in backend) == ["A", "C"]


def test_filter_by_tag_is_whole_word_not_substring(client):
    # "end" must not match a task tagged "backend".
    client.post("/tasks", json={"title": "A", "tags": ["backend"]})
    assert client.get("/tasks", params={"tag": "end"}).json() == []


def test_tags_preserved_after_unrelated_update(client):
    task_id = client.post(
        "/tasks", json={"title": "Keep tags", "tags": ["keep"]}
    ).json()["id"]
    r = client.put(f"/tasks/{task_id}", json={"priority": "high"})
    assert r.status_code == 200
    assert r.json()["tags"] == ["keep"]
    assert r.json()["priority"] == "high"


def test_update_tags(client):
    task_id = client.post("/tasks", json={"title": "Retag"}).json()["id"]
    r = client.put(f"/tasks/{task_id}", json={"tags": ["new", "set"]})
    assert r.json()["tags"] == ["new", "set"]
