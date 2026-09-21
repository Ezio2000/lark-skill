# calendar +transfer

Transfer the **organizer** of an event to another user or bot. Users and bots can be transferred between each other in any direction.

<a id="命令"></a>
## Command

```bash
# Transfer to someone (the original organizer is retained as an attendee)
lark-cli calendar +transfer --event-id <event_id> --to-user-id ou_xxx --yes

# Transfer and remove the original organizer from the attendees
lark-cli calendar +transfer --event-id <event_id> --to-user-id ou_xxx --remove-original-organizer --yes

# Specify the calendar
lark-cli calendar +transfer --calendar-id <calendar_id> --event-id <event_id> --to-user-id ou_xxx --yes

# Recurring event: the transfer of the entire series together must be explicitly confirmed
lark-cli calendar +transfer --event-id <event_id> --to-user-id ou_xxx --transfer-series --yes

# Preview the request without actually executing it
lark-cli calendar +transfer --event-id <event_id> --to-user-id ou_xxx --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--event-id <id>` | **Yes** | Event ID (in the form `uid_originalTime`) |
| `--to-user-id <ou_...>` | **Yes** | Recipient open_id, who becomes the new organizer; can be a user or a bot |
| `--calendar-id <id>` | No | ID of the calendar the event is on (if omitted, the primary calendar is used) |
| `--remove-original-organizer` | No | Remove the original organizer from the attendees after the transfer; retained by default. When the event is on a shared calendar, the server will always remove them |
| `--transfer-series` | No | Confirm that the entire recurring series is transferred together; required for recurring events |
| `--yes` | **Yes** (non dry-run) | High-sensitivity write operation confirmation |
| `--dry-run` | No | Preview the API call without executing it |

<a id="转让方向"></a>
## Transfer direction

The transferor and the recipient are two **mutually independent** parameters, and all four combinations are supported:

- The **transferor** is determined by `--as` and must be the identity of the event's **current organizer**. For events organized by a bot, use `--as bot`; for a user's own events, use `--as user`. Calling with a non-organizer identity returns 403.
- The **recipient** is determined by `--to-user-id`; whoever's open_id is passed is the one it is transferred to, and whether it is a person or a bot does not affect how the command is written.

| Direction | Command |
|------|------|
| user → user | `--as user --to-user-id <对方用户 open_id>` |
| user → bot | `--as user --to-user-id <bot 的 open_id>` |
| bot → user | `--as bot --to-user-id <用户 open_id>` |
| bot → bot | `--as bot --to-user-id <另一个 bot 的 open_id>` |

**Getting the recipient's open_id**:

```bash
# User
lark-cli contact +search-user --query <姓名> --as user
# Bot: get the open_id from bots[] in the member list of the group it belongs to
lark-cli im +chat-members-list --chat-id <chat_id> --member-types bot
```

A bot's open_id also starts with `ou_`; do not pass an app_id starting with `cli_`, which is an application ID, not an event attendee identity.

Regardless of the direction, the transfer requires the transferor and the recipient to be **in the same tenant**, and the recipient must pass the collaboration check in high-sensitivity mode.

<a id="重复性日程"></a>
## Recurring events

The backend locates the event by `uid`, ignores `original_time`, and **cannot transfer only a single instance**. Therefore, passing the `event_id` of any instance or exception will transfer the entire series (including all exceptions) together.

If it is a recurring event and `--transfer-series` is not added, the command fails directly (`failed_precondition`) and no transfer request is sent. When you receive this error, **first confirm with the user that "the entire recurring event will be transferred"**, and after confirmation rerun with `--transfer-series`; do not retry automatically. When it has already been confirmed, adding `--transfer-series` skips this pre-read.

<a id="返回中的-original_organizer_removed"></a>
## `original_organizer_removed` in the response

**A shared calendar does not belong to any organizer, and during a transfer the server forcibly removes the original organizer from the event; for the primary calendar, the original organizer is retained as an attendee.** The transfer API does not return this result on success, so the command only outputs this field when it can be determined:

| Case | Response |
|------|------|
| With `--remove-original-organizer` | `original_organizer_removed: true` |
| `--calendar-id` omitted (primary calendar) | `original_organizer_removed: false` |
| `--calendar-id` passed and `--remove-original-organizer` not passed | **This field is not returned**; stderr gives a note explaining that a shared calendar forces removal |

When the field is missing, **do not** tell the user that "the original organizer has been retained as an attendee", and do not assert that they have been removed. If you need to confirm, read the event once after the transfer to check the attendees, or explicitly pass `--remove-original-organizer` from the start.

<a id="提示"></a>
## Tips

- A transfer is irreversible, and it hands over the meeting minutes, notes, and attachments on the event to the new organizer as well.
- Requires the `calendar:calendar.event:transfer` permission; the recurring pre-read before the transfer requires `calendar:calendar.event:read` (not read when `--transfer-series` is present).

<a id="参考"></a>
## References

- [lark-calendar](../index.md) -- skill entry point and routing
- [Recurring event operation guidelines](lark-calendar-recurring.md)
