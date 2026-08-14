# My AI Playbook

Revised after the final project, building on the habits from the mid-course
sprint (see [`docs/midcourse/reflection.md`](midcourse/reflection.md) and
[`prompt-log.md`](midcourse/prompt-log.md)).

## When I reach for AI first

- Scaffolding a well-specified piece I can describe precisely: a CI workflow,
  a Dockerfile, a Pydantic model, a first draft of tests for a rule I can
  state in one sentence.
- A first pass at a SQL query or filter when I already know the exact
  behavior I want (e.g. "overdue = past due date and not done") and can write
  the test before I ask.
- Explaining an error message or an unfamiliar stack trace, and drafting
  docs/boilerplate (README sections, this playbook) that I then edit down.

## When I do not reach for AI first

- Schema and scope decisions. Twice in the mid-course sprint the AI proposed
  the "textbook" answer (a stored `overdue` column, a normalized tags table)
  when a simpler, purpose-fit answer was correct for a small board. I decide
  the shape of the data myself and tell the AI to implement that shape.
- Anything touching `app/` or `frontend/` during the final project — that's
  explicitly protected scope now, so I write the request as a constraint
  ("small bug fix only, explain it in docs/final-ai-review.md") rather than
  an open-ended one.
- Frontend behavior I can eyeball. pytest stayed green while the app was
  visibly broken (the CSS `display: flex` bug covering the whole board) — a
  green suite is not proof the UI works, so I open the browser myself before
  I believe it.

## My non-negotiables

- Never paste `.env` values, real credentials, tokens, or production data
  into a prompt. This repo has none, and it stays that way.
- Every AI-suggested change gets run, not just read: `pytest -q`, then the
  browser, then a manual look at the diff.
- I write the test for the behavior I want *before* asking the AI to
  implement it when the behavior is easy to pin down (the overdue rule, the
  whole-tag-match filter). It's the fastest way I've found to catch a wrong
  first draft.
- If I can't explain a changed line or config value in one sentence, it
  doesn't ship.

## My review rules

- Read the whole diff, not just the parts that changed the most lines.
- Treat "it reads correctly" as worthless on its own — `tags LIKE '%tag%'`
  read correctly and was still wrong (matched substrings). I check edge
  cases the code implies, not just the happy path.
- Grade AI review/security comments individually (Useful / Noise / Wrong,
  Valid / False Positive / Noise) instead of accepting a finding list
  wholesale. A finding that pattern-matches "f-string near SQL" without
  checking whether the interpolated part is user-controlled is wrong, and
  I say so with the reason, not just the verdict.
- Prefer the smaller, boring fix over the "textbook" one when the project
  doesn't need the textbook version yet.

## What I am still figuring out

- Where the line is between "small bug fix" and "new feature" when a
  security review turns up something like the wide-open CORS policy — it's
  a real finding, but fixing it properly (auth, allow-listed origins) is
  clearly out of scope for a hardening pass. I'm still refining how to
  document "valid finding, deliberately not fixed" versus "valid finding,
  fixed now."
- How much CI/Docker hardening is enough for a project this size before it
  becomes premature infrastructure for a board with no users yet.

## Decision Card

| Situation | My one rule |
|---|---|
| New feature | Write the constraint before the prompt (data shape, scope, what NOT to add), same as the tags/due-date prompts. |
| Code review | Grade every AI comment Useful/Noise/Wrong with a reason — never copy the list straight into the PR. |
| Debugging | Reproduce it myself first (run it, open the browser) before asking the AI to diagnose; I get a better answer once I can describe the actual symptom. |
| Infrastructure (CI/Docker) | AI drafts it, I read every line before it runs anywhere, and I verify the actual behavior (`/health` returns 200) instead of trusting the file looks right. |
| Never paste | Credentials, `.env` values, tokens, production logs, real personal or customer data — into a prompt or into this repo. |
| One rule | A green test suite or a plausible-looking diff is a claim, not proof — I still run it. |
