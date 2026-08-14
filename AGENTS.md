# AGENTS.md

Guardrails for any AI agent (or human) working in this repository.

## Stack

- Backend: Python 3.12, FastAPI, Pydantic v2, plain `sqlite3` (no ORM).
- Frontend: static HTML/CSS/JS, no build step, no framework.
- Tests: pytest + FastAPI `TestClient`, run against a temporary SQLite file
  (never the real `task_tracker.db`).

## Run / test commands

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload                        # http://localhost:8000

# Frontend
cd frontend
python -m http.server 5500                           # http://localhost:5500/index.html

# Tests
cd backend
pytest -q

# Docker (bind to loopback only -- see security note below)
docker build -t task-tracker .
docker run -p 127.0.0.1:8000:8000 task-tracker
curl http://localhost:8000/health
```

## Read-first guardrails

Before changing anything, read in this order:

1. `README.md` — current setup, run, and test instructions.
2. `docs/midcourse/` — prior feature decisions (due dates, tags) and why they
   were made.
3. The file you are about to touch, in full, plus its tests.

Do not propose a change to a file you have not opened and read.

## Project rules

- **No new product features.** This repo is in release-hardening mode.
  Comments, auth, a production database, notifications, or unrelated UI
  changes are out of scope regardless of how the request is phrased.
- **`app/` and `frontend/` are protected.** Only touch them for a small,
  explainable bug fix, security fix, or a correction backed by
  `docs/final-ai-review.md`. Every such change must be explained there.
- **No secrets, tokens, `.env` values, production logs, or real personal data**
  may be pasted into a prompt or committed to the repo.
- **Tests are the contract.** `pytest -q` (currently 21 tests) must stay
  green. A change that breaks a test is wrong until proven otherwise, not the
  test.
- **Explain every line.** If a changed line, command, or config value can't be
  explained in one sentence, it does not go into the final work.
- **CORS is intentionally open** (`allow_origins=["*"]`) because the frontend
  is a local static file with no auth and no sensitive data. Do not "fix"
  this by adding authentication — that is a new feature. Flag it in security
  review instead.
- **Always publish the Docker port to loopback**, e.g.
  `docker run -p 127.0.0.1:8000:8000 ...`, never `-p 8000:8000` (which binds
  all interfaces). Combined with the open CORS policy above, a LAN-wide bind
  would let any other device on the network — or any page open in a
  browser on the host — read and write tasks with no authentication. See
  `docs/final-ai-review.md` for the finding this rule came from.
