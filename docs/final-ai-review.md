# Final AI Review and Ownership Evidence

## AGENTS.md guardrails

- Repo-specific stack and commands included: yes (Python 3.12/FastAPI stack,
  exact run/test/Docker commands)
- Docs-first/read-first guardrail included: yes (README → docs/midcourse →
  the file being touched, in that order)
- Unexpected app/frontend edits rule included: yes (`app/` and `frontend/`
  marked protected; any change must be explained in this file)

## AI code review mini-log

Reviewed file: `backend/app/repository.py` (the SQLite data-access layer).

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| `list_all()`'s `overdue` query param: `if overdue:` treats an explicit `overdue=false` the same as omitting the param entirely (both skip the filter and return all tasks), which could surprise a caller expecting `false` to mean "only non-overdue." | Useful | Confirmed by reading `test_due_dates.py` — only `overdue=true` is ever tested; the `false` case is genuinely undocumented behavior, not a false alarm. | Did not change the behavior (changing filter semantics is a feature change, out of scope for a hardening pass per `AGENTS.md`). Documented as a known limitation here instead of silently leaving it unexplained. |
| `update()` does 3 DB round trips (existence check, `UPDATE`, re-`SELECT`) where 1–2 would suffice. | Noise | SQLite here is an embedded, local, single-process file DB — the extra round trip has no measurable latency impact, and collapsing the existence check into the `UPDATE` would make the 404-vs-no-op-update logic harder to read. Not worth the churn under "no new product features / small board." | No change. |
| The dynamic `f"SELECT * FROM tasks{where} ORDER BY id"` in `list_all()` is a SQL injection risk because it's built with an f-string. | Wrong | Read the surrounding code: `where` is assembled only from a fixed set of hardcoded clause strings (`"status = ?"`, `"tag(...)  LIKE ?"`, etc.) chosen from a closed set of query params; every actual value goes through `params` and sqlite3's parameterized `execute(conn, sql, params)`, never into the SQL text. The AI comment pattern-matched "f-string near SQL" without tracing where user-controlled values actually flow. | Rejected as stated; no change needed. Logged here as an example of an AI review claim that didn't survive verification. |

## AI security mini-review

Ran a focused, read-only security review (via the project's `security-review`
skill, scoped to the new `Dockerfile`, `.dockerignore`,
`.github/workflows/ci.yml`, `AGENTS.md`, and their interaction with the
existing `backend/app/` code).

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| The documented Docker run command (`-p 8000:8000`) binds the API to all host network interfaces. Combined with the app's `CORSMiddleware(allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])`, any other device on the same LAN, or any web page open in the host's browser, could read/write/delete every task with no authentication. | `Dockerfile` (EXPOSE 8000, uvicorn `--host 0.0.0.0`); `backend/app/main.py:28-33` (CORS config); `AGENTS.md` (the run example that published the port) | Valid | Confirmed by reading the actual Dockerfile CMD, the CORS middleware config, and the exact `docker run` example that was about to ship in `AGENTS.md`/`README.md`. This is a concrete, low-effort exploit path (`curl -X DELETE` from any LAN host, or a malicious page's `fetch()` from the host browser), not theoretical. | **Fixed.** Changed the documented run command in `AGENTS.md` and `README.md` from `-p 8000:8000` to `-p 127.0.0.1:8000:8000` (loopback-only), and added an explicit rule + explanation to `AGENTS.md` so this doesn't regress. |
| `CORSMiddleware(allow_origins=["*"])` in `backend/app/main.py` allows any origin to call every endpoint, including the state-changing ones. | `backend/app/main.py:28-33` (pre-existing code, not part of this change) | Valid, but out of scope | This is a real weakness in isolation, but the app has no authentication at all — fixing CORS alone wouldn't close the actual gap, and adding auth is explicitly a new product feature forbidden by the final-project ground rules. It's also pre-existing `app/` code, which the ground rules say to leave alone absent a small, explainable bug/security fix. | Not fixed. Documented as an accepted, intentional risk in `AGENTS.md` so a future maintainer doesn't "fix" it in isolation and get a false sense of security — mitigated in the meantime by keeping the port loopback-only (see finding above). |
| `update()` in `repository.py` builds `f"{key} = ?"` for each field to update, where `key` comes from `payload.model_dump(exclude_unset=True)` — dynamic column names built from a dict, which superficially resembles a SQL-injection-by-column-name pattern. | `backend/app/repository.py:101-124`; `backend/app/models.py` (`TaskUpdate` field list) | False Positive | `TaskUpdate` is a closed Pydantic model with a fixed set of declared fields (`title`, `description`, `status`, `priority`, `assignee`, `due_date`, `tags`). `model_dump()` can only ever return keys from that fixed set — there is no path for a client-supplied string to become a column name. Verified by reading the model definition, not just the call site. | No action needed. |

## Manual security check

I checked, independent of any AI tool, whether a real database file,
`.env` value, or credential-shaped string had ever been committed to this
repo — including in history, not just the current working tree (an AI
review pass typically only sees the current diff/working tree, so this is a
gap it would not catch on its own):

```
git ls-files | grep -iE "\.db$|\.env|secret|credential|token"      -> no matches
git log --all --diff-filter=A --name-only | grep -iE "\.db$|\.env" -> no matches
git grep -niE "api[_-]?key|secret|password|BEGIN (RSA|PRIVATE)" -- backend frontend -> no matches
```

Result: clean. No database file, `.env` file, or obviously secret-shaped
string has ever been added to this repository, in any commit on any branch.
This matters because the final-project ground rules explicitly forbid real
secrets or personal data in the repo, and "check the current files" is not
the same guarantee as "check the whole history" — a secret committed and
later deleted still lives in git history and is still a leak.

## One AI output I rejected or corrected

Described above in the code review mini-log: the AI flagged the
f-string-built `SELECT ... {where} ...` in `list_all()` as a SQL injection
risk. I rejected this as stated after tracing the actual data flow —
`where` is built only from a fixed set of hardcoded clause templates chosen
by which query parameters are present, and every real value is passed
through parameterized `?` placeholders via `params`, never interpolated
into the SQL string. Accepting the comment at face value would have meant
either (a) rewriting working, safe query-building code for no security
benefit, or (b) reporting a non-issue as a finding, which would have
undermined the credibility of the findings that are real (like the Docker
port-binding issue above). I kept the code as-is and recorded why.

## Three AI usage rules

1. **Never paste**: `.env` values, credentials, tokens, production logs, or
   real personal/customer data into an AI tool or into this repo — this
   project has none, and prompts were written without needing any.
2. **Always verify**: run it before believing it. Every AI-suggested change
   in this pass was checked against something real — `pytest -q` (21
   passed), a live `curl /health`, a real browser session against the
   running frontend, or a manual `git log`/`git grep` pass, not just a
   read-through of the diff.
3. **Record AI contributions by**: naming the exact file, comment, and grade
   in this document (Useful/Noise/Wrong, Valid/False Positive/Noise) instead
   of a blanket "AI helped" note — every finding above traces to a specific
   line and a specific reason it was accepted, rejected, or deferred.

## Ownership statement

I'm comfortable submitting this repo as my own work because every file in
it traces back to a decision I can explain: the app and its tests are
unchanged from the mid-course project I built and documented in
`docs/midcourse/`; the CI, Docker, and AGENTS.md files added for this pass
were drafted with AI assistance but reviewed line-by-line before anything
ran; and the one real security finding this process turned up (the
LAN-exposed, auth-less Docker port) was fixed, not just logged, before this
document was written. I rejected an AI review comment that didn't hold up
under inspection and documented a security finding (open CORS) that I
deliberately did not fix, because fixing it correctly would have meant
adding a feature this checkpoint explicitly forbids — I'd rather ship an
honestly-scoped repo with a documented, deliberate limitation than a
"fixed" repo that quietly grew scope. Nothing here was accepted because it
looked plausible; everything was run, read, or traced back to its source
first.
