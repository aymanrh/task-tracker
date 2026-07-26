# Prompt Log

A selection of the prompts I used with the AI assistant (Claude, in Claude
Code), what it returned, and what I accepted, edited, or rejected. It includes
one weak prompt rewritten into a stronger one.

## Feature 1: Due dates + overdue filter

### Prompt 1.1 (planning, constrained)
> "Add an optional due_date to the Task model. Use Pydantic's date type so a bad
> format returns 422 automatically. Keep it optional. Do not add any stored
> 'overdue' column, I want overdue computed on read."

Returned: model changes plus a stored `overdue` boolean column anyway, arguing
it would be faster to query.
Decision: **edited / partially rejected.** I kept the `due_date` field and the
Pydantic validation, but removed the stored `overdue` column. A stored flag
goes stale the moment a date passes. I told it to compute overdue on read.

### Prompt 1.2 (the overdue rule)
> "Write the overdue rule. A task is overdue only if its due date is strictly in
> the past AND its status is not 'done'. Give me the helper function and a
> matching SQL WHERE clause so the API response and the ?overdue filter agree."

Returned: an `is_overdue()` helper and a SQL clause. The first version did not
exclude `done` tasks.
Decision: **edited.** I added the `status != 'done'` condition in both the
helper and the SQL, then added a test (`test_overdue_flag_false_when_done`) so
the two paths can never drift.

### Prompt 1.3 (weak prompt, then rewritten)
Weak version:
> "add due dates to the frontend"

That produced a date input dropped into the modal but no card display, no
overdue styling, and it hardcoded today's date as the default value.

Rewritten (stronger) version:
> "In the frontend, add a due-date field to the task modal that is empty by
> default and pre-fills when editing an existing task. On each card, show a
> pill: a blue 'Due <date>' pill normally, and a red 'Overdue <date>' pill when
> the task's overdue flag is true. Add an 'Overdue only' toggle in the toolbar
> that sets ?overdue=true and keeps all three columns visible."

Returned: the modal field, the two pill styles, and the toggle, matching the
acceptance criteria.
Decision: **accepted** with a small edit to the pill CSS colors.

## Feature 2: Tags / labels

### Prompt 2.1 (planning, constrained)
> "Add tags to tasks. Store them as a single comma-separated column, not a
> normalized table, this is a small board. Expose them as a list in the API.
> Validate: trim each tag, reject blank tags, reject a tag containing a comma,
> cap at 30 chars and 10 tags, and dedupe."

Returned: it first proposed a normalized `tags` + `task_tags` schema with
foreign keys.
Decision: **rejected the schema.** I restated the constraint (comma-separated,
in scope) and it produced the single-column version with a `_clean_tags`
validator shared by create and update, which I accepted.

### Prompt 2.2 (the tag filter bug)
> "Add GET /tasks?tag=... to filter by a tag."

Returned: `WHERE tags LIKE '%' || :tag || '%'`.
Decision: **edited after testing.** I wrote a test that filtering by `end` must
not match `backend`, and it failed. I changed the query to a comma-wrapped
match, `(',' || tags || ',') LIKE '%,tag,%'`, so it matches whole tags only.
This became Break Test 2 in verification.md.

### Prompt 2.3 (frontend chips + filter)
> "In the frontend, add a comma-separated tags input to the modal (pre-filled
> when editing), render each tag as a chip on the card, and add a 'Filter by
> tag' search box in the toolbar that reloads the board with ?tag=."

Returned: the input, chips, and search box wired to the existing filter object.
Decision: **accepted**, after confirming in the browser that chips render and
the filter narrows the board while keeping empty columns visible.

## Cross-cutting

### Prompt X.1 (the modal bug, found in the browser)
> "The modal shows on page load and blocks clicks on the board even though the
> backdrop has the `hidden` attribute. Diagnose and fix."

Returned: correct diagnosis. The `.modal-backdrop { display: flex }` rule
overrides the `hidden` attribute's `display: none`. Fix: add
`[hidden] { display: none !important; }`.
Decision: **accepted.** This was caught only by opening the page in a real
browser, not by the pytest suite. See verification.md.
