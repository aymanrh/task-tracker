# Release Evidence

## Baseline

- Branch: `final-project`
- Date: 2026-08-14
- Local app run command: `cd backend && uvicorn app.main:app --reload`
- `/health` result: `GET http://localhost:8000/health` → `200 {"status":"ok"}`
- Frontend check: served with `python -m http.server 5500` from `frontend/`,
  opened `http://localhost:5500/index.html` in Chrome. The three-column
  Kanban board (To do / In progress / Done) rendered, and the "+ New task"
  modal was used to create a real task ("Verify final project baseline"),
  which appeared on the To do column immediately. The test task was deleted
  afterward via `DELETE /tasks/1` to leave the dev database clean.
- Test command: `cd backend && pytest -q`
- Test result: `21 passed, 1 warning in 1.16s` (warning is a
  `StarletteDeprecationWarning` about `httpx`/`TestClient`, unrelated to app
  behavior — pre-existing, not introduced by final-project work). Note: the
  local `.venv` had to be rebuilt from scratch because the checked-in one had
  a `pydantic_core` binary mismatched to the active Python version; this was
  a local environment issue, not a repo issue (`.venv` is git-ignored).

## CI evidence

- Workflow file: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)
- Latest run link or note: workflow created in this final-project pass; will
  run automatically on the next push to `final-project` / pull request.
  [Update this line with the Actions run URL after the first push.]
- Test command used by CI: `pytest -q` (run from the `backend/` working
  directory, after `pip install -r requirements.txt`), pinned to Python 3.12.
- Shortcut check: no `continue-on-error`, no `|| true`, pytest is not
  skipped, Python version is pinned (not "latest"), dependency install step
  is present before the test step.

## Docker evidence

- Build command: `docker build -t task-tracker .`
- Run command: `docker run -d --name task-tracker -p 127.0.0.1:8000:8000 task-tracker`
- `/health` check: **NOT RUN.** Docker is not installed on the machine this
  final-project pass was done on, so the image has not actually been built
  or started, and `/health` has not been hit inside a real container. The
  `Dockerfile` and `.dockerignore` below were written and manually reviewed
  (base image, non-root user, files copied, no secrets in the build
  context) but this is a documented gap, not a substitute for running it.
  Before submitting, install Docker Desktop and run:
  ```
  docker build -t task-tracker .
  docker run -d --name task-tracker -p 127.0.0.1:8000:8000 task-tracker
  curl -i http://localhost:8000/health
  docker exec task-tracker whoami
  docker stop task-tracker && docker rm task-tracker
  ```
  and replace this line with the actual status code, body, and `whoami`
  output.
- Non-root check: the Dockerfile creates and switches to an unprivileged
  `appuser` (`USER appuser`) before `CMD` runs.
- No-baked-secrets check: the image only copies `backend/requirements.txt`
  and `backend/app/` (see `Dockerfile`); `.dockerignore` excludes `.env`,
  `**/*.db`, `.git`, `docs/`, and `frontend/`. `TASK_TRACKER_DB` defaults to
  a path created fresh inside the container at runtime — no database file is
  baked into the image.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README claims `GET /health` works and the API runs at `http://localhost:8000` | Started the API with the documented command, ran `curl http://localhost:8000/health` | Confirmed — returned `200 {"status":"ok"}` | None |
| README claims "There are 20 tests" | Ran `pytest -q` from `backend/` and counted `def test_` in each test file | Mismatch — actual count is 21 (8 baseline CRUD + 6 due-date + 7 tags), not 20. The `fix: reject explicit null title on update with 422` commit added a test after that README line was written | Corrected the line in `README.md` from "20 tests (7 baseline CRUD...)" to "21 tests (8 baseline CRUD...)" |
| README claims the frontend "talks to the API at `http://localhost:8000`" and the Kanban board is usable | Served frontend on port 5500, opened it in a real browser, created and deleted a task through the UI | Confirmed — task appeared on the board after creation, matching the API response | None |
| `models.py` docstring/behavior: `TaskUpdate` rejects an explicit `"title": null` with a validation error instead of a DB crash (per commit `27291f1`) | Read `backend/app/models.py` `TaskUpdate.title_not_blank` validator and the corresponding test | Confirmed — validator raises `ValueError` on `None`, FastAPI turns that into HTTP 422 | None |
