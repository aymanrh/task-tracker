# Verification

Evidence that the workflow was followed: a baseline check, backend test
results, manual browser checks, the behavior contract across the refactor, and
Break Test evidence for two tests. Screenshots are in `screenshots/`.

## 1. Baseline check (before any feature work)

On a clean baseline (Modules 1-3), before branching, the suite was green:

```
7 passed, 1 warning in 0.11s
```

Tests use a fresh temporary SQLite database per test (see
`backend/tests/conftest.py`), so results do not depend on any local data.

## 2. Backend test results (after both features)

Full suite on the `mid-course-project` branch, 20 tests:

```
tests/test_due_dates.py ......   (6)
tests/test_tags.py .......       (7)
tests/test_tasks.py .......      (7)
======================== 20 passed in ~0.3s ========================
```

- Baseline CRUD: 7 tests (`test_tasks.py`).
- Feature 1 (due dates + overdue): 6 tests (`test_due_dates.py`).
- Feature 2 (tags): 7 tests (`test_tags.py`).

That is 13 new tests on top of the baseline 7, well above the required minimum
of 4 new tests.

## 3. Manual browser checks

Run with the backend on `http://localhost:8000` and the frontend served
statically, then driven in a real browser.

| Check | Result | Evidence |
|-------|--------|----------|
| Board renders three columns with counts and empty states | Pass | `screenshots/f2-board-with-tags.png` |
| Due date field appears in the modal | Pass | `screenshots/f1-modal-due-date-after-fix.png` |
| Overdue task shows a red "Overdue <date>" pill | Pass | `screenshots/f2-board-with-tags.png` |
| Upcoming task shows a blue "Due <date>" pill | Pass | (verified in board view) |
| "Overdue only" toggle narrows the board, columns stay visible | Pass | (verified live) |
| Tags render as chips on cards | Pass | `screenshots/f2-board-with-tags.png` |
| "Filter by tag" narrows the board to a whole tag | Pass | `screenshots/f2-tag-filter-backend.png` |

### Bug found only in the browser

On first load the modal was displayed over the board and intercepted all
clicks, even though its backdrop had the `hidden` attribute. Cause: the CSS
rule `.modal-backdrop { display: flex }` overrode the browser's default
`[hidden] { display: none }`. The pytest suite could not catch this: it is
pure CSS/DOM behavior. Fix: `[hidden] { display: none !important; }`.
Before/after: `screenshots/f1-modal-bug-before-fix.png` (modal wrongly open)
versus `screenshots/f1-modal-due-date-after-fix.png` (modal opens only on
click, with the due-date field present).

## 4. Behavior contract: before and after the refactor

The refactor moved all SQL from `main.py` into `app/repository.py`. I saved the
verbose test output before the refactor, ran the same suite after, and diffed
the per-test outcomes:

```
=== DIFF before vs after (test outcomes) ===
IDENTICAL: behavior contract preserved
```

20 passed before, 20 passed after, same tests, same outcomes. The refactor
changed structure, not behavior.

## 5. Break Test evidence

A Break Test deliberately breaks the implementation to prove the test actually
fails when the behavior is wrong (a test that passes no matter what is
worthless).

### Break Test 1: overdue comparison operator

Change in `repository.is_overdue`:
`return due_date < today` becomes `return due_date > today`.

Result: the due-date tests caught it.

```
FAILED tests/test_due_dates.py::test_overdue_flag_true_for_past_due_and_not_done
FAILED tests/test_due_dates.py::test_create_task_with_valid_due_date
=================== 2 failed, 4 passed ====================
```

Reverted, suite green again.

### Break Test 2: tag filter substring match

Change in `repository.list_all`:
the comma-wrapped `(',' || tags || ',') LIKE '%,tag,%'` becomes a naive
`tags LIKE '%tag%'`.

Result: the whole-word test caught it (filtering by `end` now wrongly matches
`backend`).

```
FAILED tests/test_tags.py::test_filter_by_tag_is_whole_word_not_substring
=================== 1 failed, 6 passed ====================
```

Reverted, suite green again.

## 6. Final state

```
20 passed, 1 warning
```

(The single warning is a Starlette deprecation notice about the test client and
does not affect results.)
