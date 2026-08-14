# Task Tracker

A small Kanban task tracker: FastAPI + SQLite backend, static HTML/JS frontend.
Built across Modules 1-3 as a CRUD board, then extended in the mid-course
project with two features: **due dates + overdue filter** and **tags / labels**.

## Features

- Create, edit, and delete tasks on a three-column Kanban board
  (To do / In progress / Done).
- Filter by status, priority, or assignee.
- **Due dates + overdue filter** (mid-course Feature 1): optional due date per
  task, a red "Overdue" pill for past-due tasks that are not done, and an
  "Overdue only" toggle.
- **Tags / labels** (mid-course Feature 2): comma-separated tags per task, tag
  chips on cards, and a whole-tag filter.

## Requirements

- Python 3.11 or newer (developed on 3.14).

## Run the backend

```bash
cd backend
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000. Interactive docs are at
http://localhost:8000/docs. The SQLite database file (`task_tracker.db`) is
created automatically on first run and is git-ignored.

## Open the frontend

The frontend is plain HTML/CSS/JS with no build step. Serve it and open it in a
browser (opening it over `http://` avoids browser file-access restrictions):

```bash
cd frontend
python -m http.server 5500
# then open http://localhost:5500/index.html
```

It talks to the API at `http://localhost:8000` (see the `API` constant at the
top of `frontend/app.js` if you change the port).

## Run the tests

```bash
cd backend
pytest -q
```

There are 21 tests (8 baseline CRUD + 6 due-date + 7 tags). Each test runs
against a fresh temporary SQLite database (see `backend/tests/conftest.py`), so
they never touch your real `task_tracker.db` and are safe to run repeatedly.

## Project layout

```
backend/
  app/
    main.py         # FastAPI app + routes (thin)
    repository.py   # SQLite data access
    models.py       # Pydantic models + validation
    db.py           # connection + schema
  tests/            # pytest suite
frontend/
  index.html, app.js, styles.css
docs/
  midcourse/        # mid-course project documentation (see below)
```

## Mid-course project documentation

The `mid-course-project` branch adds the two features above. Full documentation
is in [`docs/midcourse/`](docs/midcourse/):

- [`user-stories.md`](docs/midcourse/user-stories.md)
- [`mini-adr.md`](docs/midcourse/mini-adr.md)
- [`prompt-log.md`](docs/midcourse/prompt-log.md)
- [`verification.md`](docs/midcourse/verification.md)
- [`reflection.md`](docs/midcourse/reflection.md)
- `screenshots/` (browser evidence)

## Final Project

Branch reviewed: `final-project`

### What this submission demonstrates

- Existing Task Tracker app still runs inside the intended course scope (no
  new product features were added; `app/` and `frontend/` are unchanged).
- CI runs the pytest suite on push and pull request
  (`.github/workflows/ci.yml`).
- A `Dockerfile`/`.dockerignore` are provided and were manually reviewed
  (non-root user, no secrets baked in), but the image has not yet been
  build- and run-verified — Docker was not available on the machine this
  pass was done on. See `docs/release-evidence.md` for the exact commands
  to run before relying on this.
- AI review, security, and ownership evidence is in [`docs/`](docs/).

### How to run locally

```bash
cd backend
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (separate terminal):

```bash
cd frontend
python -m http.server 5500
# then open http://localhost:5500/index.html
```

### How to run tests

```bash
cd backend
pytest -q
```

### How to run with Docker

```bash
docker build -t task-tracker .
docker run -d --name task-tracker -p 127.0.0.1:8000:8000 task-tracker
curl http://localhost:8000/health
docker stop task-tracker && docker rm task-tracker
```

Port is bound to loopback only (`127.0.0.1:8000:8000`, not `8000:8000`):
combined with this API's intentionally open CORS policy, a LAN-wide bind
would let any other device on the network read and write tasks with no
authentication. See `docs/final-ai-review.md` for the finding this came
from.

### Evidence files

- [`docs/release-evidence.md`](docs/release-evidence.md)
- [`docs/final-ai-review.md`](docs/final-ai-review.md)
- [`docs/ai-playbook.md`](docs/ai-playbook.md)

### AI assistance summary

AI helped draft or review: CI workflow, Dockerfile, AGENTS.md, README/docs,
a code review pass on `backend/app/repository.py`, and a security review of
the new CI/Docker files.

I verified the work by: running the full pytest suite (21 passed), starting
the API and frontend locally and exercising the create-task flow in a real
browser, checking `/health` returns 200, and manually checking git history
for committed secrets or database files.

One AI suggestion I rejected or corrected: see
[`docs/final-ai-review.md`](docs/final-ai-review.md#one-ai-output-i-rejected-or-corrected).
