<a id="重复性日程操作规范"></a>
# Recurring Event Operation Rules

Editing and deleting recurring events/exceptions must explicitly specify the operation scope. Related commands:

- `lark-cli calendar +delete` — Delete an event; recurring events/exceptions must pass `--apply-to`.
- `lark-cli calendar +update` — Update an event; recurring events/exceptions must pass `--apply-to`.

> **Destructive Confirmation Gate:** When the user has not explicitly specified the operation scope, you must first confirm with the user. Before executing `+delete`, as well as write operations in `+update` that notify attendees or are irreversible, **even if the target event_id and `--apply-to` are both already clear, the Agent must wait for user confirmation**.
>
> You may skip this only when the user explicitly states in the same conversation turn something equivalent to "just delete it / no need to ask / confirmed / stop confirming / just do it". When skipping, you must note in the final reply "Executed per user's explicit confirmation waiver" for traceability.

<a id="--apply-to-与日程类型的匹配矩阵"></a>
## Matching Matrix of `--apply-to` and Event Types

First remember the four event types: **Normal Event (Normal)**, **Recurring Event Master (Master)**, **Recurring Event Instance (Instance)**, **Recurring Event Exception (Exception)**. The allowed `--apply-to` combinations for the four types are as follows (❌ = passing it causes an error):

| Event Type | event_id Shape | `single` | `all` | `this-and-following` |
|----------|--------------|:--------:|:-----:|:--------------------:|
| Normal (Normal Event)          | `{uid}_0` (no rrule) | Implicit default | ❌ | ❌ |
| Master (Recurring Event Master)    | `{uid}_0` (has rrule) | ❌ | ✅ | ❌ |
| Instance (Recurring Event Instance)  | `{uid}_{ts>0}`, `is_exception=false` | ✅ | ✅ | ✅ |
| Exception (Recurring Event Exception)| `{uid}_{ts>0}`, `is_exception=true`  | ✅ | ✅ | ❌ (The Exception already occupies that time slot; you need to pass another Instance id that has not been individualized as the split point) |

The meaning and impact scope of the three `--apply-to` values:

| Value | Semantics | Impact Scope |
|----|------|--------|
| `single` | Operate only on this occurrence | Only modify/delete the single event_id passed in; exceptions do not affect other exceptions, and instances do not affect the entire series |
| `all` | Operate on the entire recurring series | The Master itself **and** all exceptions will be processed (when the time changes, exceptions are deleted first; other fields are synchronously PATCHed to each exception) |
| `this-and-following` | Truncate from the "starting instance" and create a new subsequent series | Use UNTIL to truncate the Master, delete all future exceptions starting from the starting instance, and create a new series starting from the starting instance's time, inheriting the Master's default fields |

<a id="关键概念"></a>
## Key Concepts

- **event_id structure**: The format of `event_id` is `{event_uid}_{originalTime}`. `originalTime = 0` indicates Master or Normal; `originalTime > 0` indicates the timestamp (Unix seconds) of a particular occurrence in the original series. Therefore `{event_uid}_0` is the `event_id` of the recurring event master.
- **Master (Recurring Event Master)**: The event master that carries `rrule`, with `event_id` in the form `{event_uid}_0`. All default properties of the series (title, time, rrule, description, attendees, etc.) are attached to the master.
- **Normal (Normal Event)**: Does not carry `rrule`; `event_id` is also `{event_uid}_0`, but there is no series concept. Only `--apply-to=single` can be used (may be omitted).
- **Instance vs Exception — these two are the most easily confused, be sure to distinguish them**:
  - **Instance**: A "virtual" occurrence expanded from the rrule, which itself is not persisted. `event_id` is in the form `{event_uid}_{originalTime}` (`originalTime > 0`), and is an addressable identifier returned from `+agenda` / `+search-event`. It has **never been individually edited**—all properties are inherited from the Master. At the API level, you can send a GET to an Instance id, but when sending a write operation to it (operating on this occurrence), it will first be "materialized" into an Exception.
  - **Exception**: An **independent event** persisted after an Instance is explicitly modified (time changed, title changed, attendees changed, etc.) or explicitly marked for deletion. `event_id` has exactly the same shape as an Instance (`{event_uid}_{originalTime}`), and **cannot** be distinguished by eye—the only reliable criterion is the `is_exception=true` returned by `calendar +get` (false for Instance). An Exception has already detached from the Master's field inheritance and is an entity that can be independently edited/deleted.
  - **One-sentence summary**: An Instance is a "placeholder" expanded from the rrule, and an Exception is "an instance that has already been individualized". To determine which kind the current event_id is, first run `+get` and check `is_exception`.
- Deleting/updating a Master does **not** cascade-process exceptions—the command internally scans and processes exceptions explicitly.

<a id="前置步骤所有范围通用"></a>
## Prerequisites (common to all scopes)

1. Locate the target event / instance via `+agenda` or `+search-event`, and obtain `event_id`.
2. Determine the event type:
   - `event_id` suffix `_0` and no `recurrence` → Normal;
   - `event_id` suffix `_0` and has `recurrence` → Master;
   - `event_id` suffix `_{数字>0}` and `is_exception=false` → Instance;
   - `event_id` suffix `_{数字>0}` and `is_exception=true` → Exception.
   - When precise determination is needed, run `calendar +get` and check the `recurrence` and `is_exception` fields.
3. **Confirm the `--apply-to` scope with the user (if unclear, always ask first; defaulting is prohibited)**.

<a id="常见命令"></a>
## Common Commands

<a id="删除"></a>
### Delete

```bash
# Delete this occurrence (exception or instance)
lark-cli calendar +delete --event-id <uid_originalTime> --apply-to single

# Delete all (master event id or any exception/instance id)
lark-cli calendar +delete --event-id <uid_originalTime> --apply-to all

# Delete this and following occurrences (must pass a specific instance id)
lark-cli calendar +delete --event-id <uid_originalTime> --apply-to this-and-following
```

<a id="更新"></a>
### Update

```bash
# Edit this occurrence (single instance / exception)
lark-cli calendar +update --event-id <uid_originalTime> --apply-to single --summary <summary>

# Edit all (master event id or any exception/instance id)
lark-cli calendar +update --event-id <uid_originalTime> --apply-to all --summary <summary>

# Edit all: change time
lark-cli calendar +update --event-id <uid_originalTime> --apply-to all --start <start> --end <end>

# Edit this and following occurrences: truncate master + delete future exceptions + create new series
lark-cli calendar +update --event-id <uid_originalTime> --apply-to this-and-following --summary <summary>
```

<a id="语义细则"></a>
## Semantic Details

- **Field propagation with `--apply-to=all`**: Only apply the flags explicitly passed by the user this time to each exception and the master event. Other fields that the exception originally customized (such as its own description) remain unchanged.
- **Field inheritance for `--apply-to=this-and-following`**: The newly created event inherits summary, description, rrule, start/end (using the starting instance's time), vchat/reminders/location/visibility from the original master event; any flags explicitly passed by the user take precedence.
- **`--start/--end` changes**: In the `all` scenario, exceptions are deleted (the original placeholders are no longer meaningful), and then the master event is PATCHed; in the `this-and-following` scenario, if `--start/--end` is passed, it is used as the time of the new series; otherwise, the starting instance's time is used.
- **Attendees**: When `this-and-following` creates a new series, if `--add-attendee-ids` is passed, attendees will additionally be added to the new series; `--remove-attendee-ids` will be removed from the new series' attendee list.
