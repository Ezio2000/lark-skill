# calendar +update


Update existing calendar event fields, or independently add/remove attendees and meeting rooms incrementally.

`+update` supports three mutually independent actions: updating event fields, adding attendees/meeting rooms, and removing attendees/meeting rooms. They can be executed separately or combined in the same command.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Update title, description, time
lark-cli calendar +update \
  --event-id "<EVENT_ID>" \
  --summary "产品评审" \
  --description "评审需求范围、排期与风险" \
  --start "2026-03-12T14:00+08:00" \
  --end "2026-03-12T15:00+08:00"

# Incrementally add attendees and meeting rooms
lark-cli calendar +update \
  --event-id "<EVENT_ID>" \
  --add-attendee-ids "ou_aaa,ou_bbb,omm_room"

# Remove attendees and meeting rooms
lark-cli calendar +update \
  --event-id "<EVENT_ID>" \
  --remove-attendee-ids "ou_aaa,omm_room"

# Simultaneously update event information, remove old meeting rooms, and add new meeting rooms
lark-cli calendar +update \
  --event-id "<EVENT_ID>" \
  --summary "产品评审" \
  --start "2026-03-12T15:00+08:00" \
  --end "2026-03-12T16:00+08:00" \
  --remove-attendee-ids "omm_old_room" \
  --add-attendee-ids "omm_new_room"
```

Parameters:

| Parameter | Required | Description |
|------|------|------|
| `--event-id <id>` | Yes | The event ID to update. For recurring events, choose the ID based on the operation scope; see [Recurring Event Operation Guidelines](lark-calendar-recurring.md) |
| `--calendar-id <id>` | No | Calendar ID (if omitted, `primary` is used) |
| `--summary <text>` | No | New event title. Only updated when `--summary` is explicitly passed; if an empty string is passed, the title will be cleared |
| `--description <markdown>` | No | New event description, always use this field, format is **Markdown** (bold, italic, underline `<u>...</u>`, strikethrough, link `[文本](url)`, heading `# `~`### ` (up to three levels), quote `> `, ordered/unordered lists, GFM table `\| 列1 \| 列2 \|` + separator row `\| --- \| --- \|`, and images `![图片名](图片URL)` (standard Markdown image syntax: remote URLs are used as-is; **local image paths** (relative paths within the current working directory) are automatically uploaded to Drive and rendered inline on the client—absolute paths or paths outside the working directory will error; images already on the client are read back as Markdown images). Feishu document URLs (bare links or `[文本](url)`) are automatically resolved as inline documents, and the document title is displayed on the client. Supports `@文件路径` or `-` (stdin) for reading. Only updated when explicitly passed; passing an empty string `""` will clear the description. **Do not** use `***文本***` to represent bold+italic simultaneously (it will leave residual `*` on the client); instead nest them, e.g. `**<u>*~~文本~~*</u>**` or `*<u>**~~文本~~**</u>*`. |
| `--start <time>` | No | New start time (ISO 8601, **must include timezone offset**, e.g. `2026-03-12T14:00+08:00`; without an offset it will be parsed in the process timezone causing a shift). When updating event time, `--end` must also be passed |
| `--end <time>` | No | New end time (ISO 8601, **must include timezone offset**). When updating event time, `--start` must also be passed |
| `--rrule <rrule>` | No | New recurrence rule (RFC5545). **Do not use COUNT; if a count limit is needed, convert to UNTIL after calculation** |
| `--add-attendee-ids <id_list>` | No | Incrementally add attendees/meeting rooms, comma-separated. Supports users `ou_`, groups `oc_`, meeting rooms `omm_` |
| `--remove-attendee-ids <id_list>` | No | Incrementally remove attendees/meeting rooms, comma-separated. Supports users `ou_`, groups `oc_`, meeting rooms `omm_` |
| `--notify` | No | Whether to send update notifications, default `true`. Use `--notify=false` for silent update |
| `--dry-run` | No | Preview the API call without executing |

At least one action must be provided: `--summary`, `--description`, `--start/--end`, `--rrule`, `--add-attendee-ids`, or `--remove-attendee-ids`.

<a id="使用规则"></a>
## Usage rules

- `--add-attendee-ids` is **incremental addition**, not replacing the final attendee list. Do not use it to express "keep only these people".
- For `--summary` and `--description`, the CLI determines whether to update based on "whether the flag is explicitly passed", not on "whether the value is empty"; if an empty string is explicitly passed, the corresponding field will be cleared.
- Event descriptions always go through `--description` (processed as Markdown rich text).
- When applying both bold and italic inline, **do not** write `***文本***` (it will leave residual `*` on the client); `**` and `*` must each be paired and nested, e.g. `**<u>*~~文本~~*</u>**` or `*<u>**~~文本~~**</u>*`.
- When only adding or removing attendees or meeting rooms, there is no need to also pass event fields such as `--summary`, `--start`, `--end`.
- When only modifying the title, description, time, or recurrence rule, there is no need to also pass `--add-attendee-ids` or `--remove-attendee-ids`.
- To replace an attendee, group, or meeting room, use `--remove-attendee-ids <旧ID>` + `--add-attendee-ids <新ID>`.
- A bot can be added as a valid attendee without needing to be excluded.
- A meeting room is a resource attendee and must be added to the attendee list using the `omm_` ID; it cannot be booked independently of an event.
- When updating a recurring event, the operation scope must first be determined (this instance only/all/this and following), then follow the [Recurring Event Operation Guidelines](lark-calendar-recurring.md).
- When multiple actions are combined in the same command, the execution order is "event fields -> remove attendees -> add attendees". If a failure occurs midway, successfully completed steps will not be automatically rolled back; the error message will indicate which steps were completed.
**⚠️ High-risk operation**: When modifying time, you must first read the original event duration and calculate the new end. If the end is calculated incorrectly, the event duration will change, which the user will directly perceive; do not arbitrarily change the original event duration.
**Do not arbitrarily append `--skip-room-check` retry**: Pass the error message (including meeting room ID and reason) through to the user as-is, explain that this update will cause the meeting room booking to fail, and explicitly ask whether to continue; after user confirmation, re-execute with `--skip-room-check`.

Pre-check failures (such as API 404 or returned errors) will degrade to allow-through: print a warning to stderr and continue execution, to avoid blocking normal updates due to new API instability.

<a id="高级用法完整-api-命令"></a>
## Advanced usage (full API command)

`+update` only covers title, description, time, recurrence rule, and incremental addition or removal of attendees/meeting rooms.

To update `location` (location, excluding meeting room location), `visibility` (event visibility), custom `reminders` (reminder settings), custom `attendee_ability` (attendee permissions), custom `free_busy_status` (event busy/free status), `color` (color), attachments, video conference information, all-day events, or advanced parameters such as configuring optional attendance status when adding attendees, use the full API command instead. It is recommended to first view the full parameter definitions via `lark-cli schema calendar.events.patch`, `lark-cli schema calendar.event.attendees.create`, `lark-cli schema calendar.event.attendees.batch_delete`.

> The time parameters of the full API command are **Unix second strings** (not ISO 8601). When converting, **do not rely on the container default timezone** (often UTC, which causes an 8-hour shift); the target timezone must be explicitly specified.

<a id="预约改约会议室场景"></a>
## Booking/rescheduling meeting room scenarios

If the user wants to "change meeting time", "switch meeting rooms", or "add a meeting room to an existing event", you must first read [`lark-calendar-schedule-meeting.md`](lark-calendar-schedule-meeting.md) and handle it according to the workflow therein:

- Clear time and meeting room needed: first `+room-find`, then `+freebusy` as needed, and after user confirmation `+update`.
- Vague time or no time: first `+suggestion`, then batch `+room-find` if a meeting room is needed, and after user confirmation `+update`.
- When facing a choice of time options or meeting room options, you must first present the candidate options and wait for user confirmation.

<a id="参会人类型"></a>
## Attendee types

| Prefix | Type | Description |
|------|------|------|
| `ou_` | user | Feishu user open_id |
| `oc_` | chat | Feishu group |
| `omm_` | resource | Meeting room |

> [!CAUTION]
> This is a **write operation**. Before executing, you must confirm the user's intent, especially when removing attendees/meeting rooms or moving meeting time.

<a id="参考"></a>
## References

- [lark-calendar](../index.md) -- skill entry and routing
- [lark-calendar-schedule-meeting](lark-calendar-schedule-meeting.md) -- booking/rescheduling meetings and meeting room workflow
- [lark-calendar-room-find](lark-calendar-room-find.md) -- find available meeting rooms
