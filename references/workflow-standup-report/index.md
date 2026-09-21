# Agenda and task summary

Use for a daily/weekly agenda plus incomplete tasks. This workflow uses user identity. Reuse the current login; read [authentication](../shared/index.md) only for actual auth/scope problems. Relevant scopes are `calendar:calendar.event:read` and `task:task:read`.

## Retrieve

Resolve relative dates in the user's timezone. CLI dates accept ISO 8601/date strings or supported Unix timestamps, not natural-language values such as "tomorrow".

```sh
lark-cli calendar +agenda --as user
lark-cli task +get-my-tasks --complete=false --as user
```

For a date range, use `calendar +agenda --start <start> --end <end>`. For tasks due by its end, add `--due-end <ISO-8601>`. The default task page contains at most 20 items; use `--page-all` when the requested summary needs all items. Always specify `--complete=false`: omitting it also returns completed tasks.

Do not use a due-date filter if undated tasks are in scope. For a concise summary, older undated tasks may be grouped, but label omissions and never present a limited page as an exhaustive count.

## Summarize

- Convert timestamps using the user's timezone and retain all-day semantics.
- Sort events by start time; show accepted, declined, tentative, or awaiting-response status. Declined events do not count as busy time or conflicts.
- Detect overlapping intervals, including a long event overlapping multiple shorter events; comparing only consecutive pairs can miss conflicts.
- Sort tasks by due date, flag overdue tasks, and put undated tasks last.
- Report empty sections honestly. Distinguish free time inferred from fetched events from authoritative availability.
- Use a compact agenda and task list, with counts/conflicts only when useful. Do not create a document, send a message, or create tasks unless requested.

Read [Calendar](../calendar/index.md) or [Tasks](../task/index.md) when the request needs operation-specific fields or filtering beyond these commands.
