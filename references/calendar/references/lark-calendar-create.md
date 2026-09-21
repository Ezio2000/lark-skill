
# calendar +create


Create a calendar event and invite attendees as needed.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Create a calendar event + invite attendees (ISO 8601 time)
lark-cli calendar +create \
  --summary "产品评审" \
  --start "2026-03-12T14:00+08:00" \
  --end "2026-03-12T15:00+08:00" \
  --attendee-ids ou_aaa,ou_bbb

# No attendees
lark-cli calendar +create \
  --summary "午餐" \
  --start "2026-03-12T12:00+08:00" \
  --end "2026-03-12T13:00+08:00"

# Specify a calendar
lark-cli calendar +create --summary "..." --start "..." --end "..." \
  --calendar-id cal_xxx
```

Parameters:

| Parameter | Required | Description |
|------|------|------|
| `--summary <text>` | No | Event title. Note: the title should not contain time, location, or person information |
| `--start <time>` | Yes | Start time (ISO 8601, **must include a timezone offset**, e.g. `2026-03-12T14:00+08:00`; without an offset it will be parsed according to the process timezone, causing an offset) |
| `--end <time>` | Yes | End time (ISO 8601, **must include a timezone offset**) |
| `--description <markdown>` | No | Event description, always use this field, in **Markdown** format. Provide the meeting agenda, activity content, notes, or links, etc. Supports bold, italic, underline (`<u>...</u>`), strikethrough, links `[文本](url)`, headings (`# ` to `### `, up to three levels), quotes (`> `), ordered/unordered lists, GFM tables (`\| 列1 \| 列2 \|` + separator row `\| --- \| --- \|`), and images `![图片名](图片URL)` (standard Markdown image syntax: remote URLs are used as-is; **local image paths** (relative paths located within the current working directory) are automatically uploaded to Drive and rendered inline on the client—absolute paths or paths outside the working directory will error; images already on the client are read back as Markdown images). Feishu document URLs (paste the bare link directly, or write it as `[文本](url)`) are automatically resolved as inline documents, and the client displays the document title instead of the bare link. Supports `@文件路径` or `-` (stdin) for reading. **Do not** use `***文本***` to represent bold+italic at the same time (the client will leave residual `*`); instead nest them, e.g. `**<u>*~~文本~~*</u>**` or `*<u>**~~文本~~**</u>*`.|
| `--attendee-ids <id_list>` | No | List of attendee IDs (comma-separated). Supports users (`ou_`), groups (`oc_`), and meeting rooms (`omm_`). When AI extracts these, be sure to preserve the corresponding prefix. A bot can be a valid attendee and does not need to be removed |
| `--calendar-id <id>` | No | Calendar ID (if omitted, the primary calendar is used) |
| `--rrule <rrule>` | No | Recurrence rule for a recurring event; for how to set the rule, refer to rfc5545. Example value: "FREQ=DAILY;INTERVAL=1;UNTIL=<specific date>" |
| `--meeting-owner-id <ou_>` | No | Set the VC meeting owner. Only takes effect when operating on an app calendar with an app (bot) identity (requires `--as bot`); the owner must be the open_id (`ou_`) of a user identity in this tenant |
| `--dry-run` | No | Preview the API call without executing it |

> When the user expresses 'every week on X', 'repeat weekly', or 'for N consecutive weeks', you must use rrule to create a recurring event, rather than creating multiple independent events
> When a `--description` line is both bold and italic at the same time, **do not** write `***文本***` (the client will leave residual `*`); you must let `**` and `*` each be nested in pairs, for example `**<u>*~~文本~~*</u>**` or `*<u>**~~文本~~**</u>*`.
> Automatically set `attendee_ability: "can_modify_event"`, so attendees can see each other and edit the event.
> Automatically set `free_busy_status: "busy"`, with the default event busy/free status set to busy.
> Automatically set `reminders: [{"minutes": 5}]`, with a reminder 5 minutes before the event starts by default.
> Automatically set `vchat: {"vc_type": "vc"}`, with the event including a Feishu video meeting by default. If you need another video meeting type or no video meeting, use the full API command.
> Failure protection: if adding attendees fails (e.g. an incorrect open_id), the CLI automatically deletes the empty event that was just created (rollback, without notifying attendees).
> Meeting room approval: `+create` does not expose the low-frequency field `attendees[].approval_reason`. If a meeting room requires approval, first create the event using a user identity, then use the full API `calendar event.attendees create --as user` to add the meeting room and pass `approval_reason`.

<a id="高级用法完整-api-命令"></a>
## Advanced usage (full API command)

> Preferred strategy: for creating events, prefer `+create`. When encountering advanced parameters not supported by `+create` (such as `location` (geographic location, excluding meeting room location), `visibility` (event visibility), custom `reminders` (reminder settings), custom `attendee_ability` (attendee permissions), custom `free_busy_status` (event busy/free status), attendee optional participation status, or all-day events, etc.), **prefer to first create successfully with `+create`, then use the full API update to edit and fill in these fields**, rather than switching entirely to the full API to create from scratch.

**Note**:
- For an all-day event, the start date and end date must be the first day the event starts and the last day it ends, respectively. If it is only one day, the start date and end date are the same.

```bash
## Add a meeting room that requires approval (approval_reason max 200 characters)
lark-cli calendar event.attendees create \
  --as user \
  --params '{"calendar_id":"<CALENDAR_ID>","event_id":"<EVENT_ID>"}' \
  --data '{"attendees": [{"type": "resource", "room_id": "omm_xxx", "approval_reason": "申请原因"}]}'
```

Key differences and handling strategies for the full API command:
- The time parameter is a **Unix seconds string** (not ISO 8601). When converting, **do not rely on the container's default timezone** (often UTC, which causes an 8-hour offset); you must explicitly specify the target timezone.
- For an all-day event, the start date and end date must be the first day the event starts and the last day it ends, respectively; for a single-day all-day event, the two are the same.
- When manually splitting into the two steps of "create event + add attendees", if the second step fails, it is recommended to delete the empty event that was just created, to avoid leaving behind an event with no attendees.

<a id="参会人类型"></a>
## Attendee types

| `type` | `user_id` format | Description |
|--------|---------------|------|
| `user` | `ou_xxx` (open_id) | Feishu user |
| `group` | `oc_xxx` | Feishu group |
| `resource` | `omm_xxx` | Meeting room |
| `third_party` | Email address | External attendee |

> [!CAUTION]
> This is a **write operation** -- you must confirm the user's intent before executing.

<a id="参考"></a>
## References

- [lark-calendar](../index.md) -- skill entry point and routing
- [lark-calendar-suggestion](lark-calendar-suggestion.md) -- recommend multiple available time block options based on an unspecified time or a time range
