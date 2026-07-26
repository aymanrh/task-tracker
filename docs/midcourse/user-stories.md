# User Stories

Two features were added on the `mid-course-project` branch:
Feature 1 (due dates + overdue filter) and Feature 2 (tags / labels).
Each story lists acceptance criteria. AI assumptions I had to correct are
called out explicitly.

## Feature 1: Due dates + overdue filter

### F1-1: Set an optional due date
As a user, I want to give a task an optional due date so I know when it is due.

Acceptance criteria:
- Creating a task with a valid `due_date` (YYYY-MM-DD) returns 201 and echoes
  the date back.
- Creating a task with no `due_date` still works (the field is optional).
- The date shows on the card and in the edit modal.

### F1-2: See overdue tasks at a glance
As a user, I want overdue tasks visually flagged so I can spot what is late.

Acceptance criteria:
- A task with a past due date that is not `done` shows an `overdue` flag of
  `true` and a red "Overdue" pill on the card.
- A task whose due date is today or later is not overdue.

### F1-3: A finished task is never "overdue"
As a user, I do not want completed tasks nagging me as overdue.

Acceptance criteria:
- A task with a past due date but `status = done` returns `overdue = false`.

> **AI assumption I corrected.** The AI's first draft computed `overdue`
> purely as "due_date is in the past" and would have shown done-but-late tasks
> as overdue. I corrected the rule to exclude `done` tasks, and added
> `test_overdue_flag_false_when_done` to lock it in. The AI had also leaned
> toward computing overdue in the frontend; I moved it to the backend so the
> flag is consistent for any client and testable with pytest.

### F1-4: Filter to only overdue tasks
As a user, I want to filter the board to overdue tasks so I can triage.

Acceptance criteria:
- `GET /tasks?overdue=true` returns only overdue tasks.
- The "Overdue only" toggle filters the board and keeps all three columns
  visible with their empty states.

### F1-5: Reject invalid dates
As a user, I want a malformed date rejected so bad data never lands on a card.

Acceptance criteria:
- Posting `due_date = "31-12-2026"` (wrong format) returns 422.

## Feature 2: Tags / labels

### F2-1: Tag a task
As a user, I want to attach one or more tags to a task to categorize it.

Acceptance criteria:
- Creating a task with `tags = ["ui", "urgent"]` returns 201 and the tags list.
- Tags render as chips on the card and are editable in the modal.

### F2-2: Clean tag input
As a user, I want messy tag input cleaned up so my labels stay tidy.

Acceptance criteria:
- Tags are trimmed of surrounding whitespace.
- Duplicate tags are collapsed (`[" ui ", "ui", "api"]` becomes `["ui","api"]`).
- A blank or whitespace-only tag is rejected with 422.
- A tag longer than 30 characters, or more than 10 tags, is rejected.

> **AI assumption I corrected.** The AI proposed a fully normalized schema: a
> separate `tags` table plus a `task_tags` join table with foreign keys. That
> is the "correct" database answer but far more than this board needs. I
> rejected it as out of scope and kept a single comma-separated column, which
> is exactly what the brief allows. See the mini-ADR for the full reasoning.

### F2-3: Filter by tag
As a user, I want to filter the board to one tag so I can focus.

Acceptance criteria:
- `GET /tasks?tag=backend` returns only tasks carrying the whole tag `backend`.
- Filtering by `end` must NOT match a task tagged `backend` (whole tag, not
  substring).

> **AI assumption I corrected.** The AI's first filter used
> `tags LIKE '%backend%'`, which also matches substrings, so filtering by
> `end` would wrongly return `backend` tasks. I changed it to a comma-wrapped
> match, `(',' || tags || ',') LIKE '%,tag,%'`, and wrote
> `test_filter_by_tag_is_whole_word_not_substring` to guard it. This is one of
> the two Break Tests in verification.md.

### F2-4: Tags survive unrelated edits
As a user, I want my tags kept when I change something else on the task.

Acceptance criteria:
- Updating only `priority` on a tagged task leaves its tags unchanged.

### F2-5: Retag a task
As a user, I want to replace a task's tags later.

Acceptance criteria:
- `PUT /tasks/{id}` with a new `tags` list replaces the old set.
