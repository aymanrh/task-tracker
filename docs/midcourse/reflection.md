# Reflection

For this sprint I used Claude (inside Claude Code) as my main coding assistant,
and Playwright driving a real browser to check the frontend. I split the work
by what each tool is good at. Claude did the planning conversations, drafted the
model and route changes, wrote first passes of the tests, and explained trade
offs when I pushed back. Playwright was my reality check: after every frontend
change I loaded the actual page, took a screenshot, and confirmed the behavior
instead of trusting that the code "should" work. pytest was the safety net that
let me refactor without fear.

The clearest moment the AI helped was the tag filter. I asked for a filter by
tag and it gave me a working endpoint in seconds, including the SQL. That saved
real time. But the same feature is also where it slowed me down, or rather where
it would have if I had trusted it. Its filter used `tags LIKE '%tag%'`, which
looks right and passes a casual glance. It quietly matches substrings, so
filtering by `end` would return everything tagged `backend`. I only caught it
because I had written a test for exactly that case first. That is the lesson I
keep relearning: AI output that reads as correct is not the same as correct, and
the cheapest place to prove it is a test.

The place my own review changed the result was the overdue rule. The AI's first
version treated any past due date as overdue, including finished tasks. Logically
a completed task cannot be late, so I added the condition that overdue excludes
`done` tasks, in both the response helper and the SQL filter, and wrote a test
to pin it down. A second review moment was rejecting the AI's normalized tags
schema. It proposed a proper join table, which is the textbook answer, but it
was far more than a small board needs. I kept a comma-separated column and wrote
down why in the ADR.

The single most useful habit was opening the page in a browser. The pytest suite
was fully green while the app was actually broken: the modal was covering the
whole board because a CSS `display: flex` rule beat the `hidden` attribute. No
backend test could have found that. Seeing it in Playwright, then fixing it with
one CSS line, was the moment the "inspect, run, verify" loop paid for itself.

If I did this again, I would write the failing test before asking the AI to
implement, every time, not just for the tricky cases. When I did that, the AI's
mistakes surfaced immediately. When I did not, I had to notice them myself, which
is slower and easier to miss. The tools are fast, but ownership still means I run
it, I test it, and I decide what ships.
