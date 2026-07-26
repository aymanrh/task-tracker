# Task Tracker

A small Kanban task tracker: FastAPI + SQLite backend, static HTML/JS frontend.
Built across Modules 1-3 as a CRUD board, then extended in the mid-course
project with due dates and tags.

## Run the backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000 (interactive docs at `/docs`).

## Open the frontend

Open `frontend/index.html` in a browser (double-click, or serve the folder with
`python -m http.server` from `frontend/`). It talks to the API at
`http://localhost:8000`.

## Run the tests

```bash
cd backend
pytest -q
```

Tests use a fresh temporary SQLite database per test, so they never touch your
real `task_tracker.db`.
