# Mini ADR: implementing due dates and tags

Status: accepted. Date: 2026-07-26. Branch: `mid-course-project`.

This note records the design decisions for the two features, the alternatives
the AI suggested, and what I rejected as too complex or out of scope.

## Context

The baseline Task Tracker (Modules 1-3) is a FastAPI + SQLite backend with a
static Kanban frontend. Tasks had title, description, status, priority, and
assignee. I added two scoped features end to end, keeping each small enough to
finish and verify.

## Decision 1: due dates and overdue

- `due_date` is an optional `date` on the task. I let Pydantic's `date` type do
  the format validation, so a bad format returns 422 for free.
- `overdue` is a computed field, not a stored column. It is `true` when the due
  date is in the past AND the task is not `done`. Computing it means it can
  never drift out of sync with the date or status.
- I compute overdue on the backend, both in the response (`is_overdue`) and in
  the `?overdue=true` SQL filter, so the two always agree.

Alternatives the AI suggested and I rejected:
- Storing `overdue` as a boolean column. Rejected: it would go stale the moment
  a date passes or a task is completed, and would need a background job to
  refresh. Computing on read is simpler and always correct.
- Computing overdue only in the frontend. Rejected: it would not be testable
  with pytest and would differ between clients.

## Decision 2: tags

- Tags are stored as a single comma-separated `TEXT` column and exposed in the
  API as a list. The brief explicitly allows a list or a normalized
  comma-separated field.
- Validation lives in one shared `_clean_tags` helper used by both create and
  update: trim, reject blank, reject commas inside a tag, cap length at 30 and
  count at 10, and dedupe while preserving order.
- The tag filter matches a whole tag by wrapping both the stored value and the
  query in commas: `(',' || tags || ',') LIKE '%,tag,%'`.

Alternatives the AI suggested and I rejected:
- A normalized `tags` table plus a `task_tags` join table. This is the textbook
  relational answer and would help if we needed tag rename, tag analytics, or
  autocomplete across the whole board. I rejected it as out of scope: it adds
  two tables, join queries, and cascade handling for a board that just needs to
  label and filter cards. YAGNI.
- A naive `tags LIKE '%tag%'` filter. Rejected because it matches substrings
  (`end` would match `backend`). The comma-wrapped match fixes this and is
  covered by a test.

## Decision 3: a small refactor after the features worked

Once both features passed, all SQL had piled up inside the route handlers in
`main.py`. I extracted it into `app/repository.py` so `main.py` is just thin
routes that translate a `None`/`False` result into a 404. The full test suite
passed identically before and after (see verification.md), which is the whole
point of having the tests: the refactor changed structure, not behavior.

## Consequences

- The app stays a single small backend module plus one data module, no ORM, no
  migrations. Easy for a reviewer to run and read.
- If tags ever need rename or global analytics, the comma-separated choice will
  have to be revisited. That trade is deliberate and documented here.
