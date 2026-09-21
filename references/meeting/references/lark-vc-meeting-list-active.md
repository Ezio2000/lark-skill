# vc +meeting-list-active

List ongoing meetings, used to discover the long numeric `meeting_id` needed by `+meeting-events`.

This module corresponds to shortcut: `lark-cli vc +meeting-list-active` (calls `GET /open-apis/vc/v1/bots/user_active_meeting`).

<a id="命令"></a>
## Command

```bash
# Query the meeting that the currently logged-in user is attending
lark-cli vc +meeting-list-active --as user --format json

# Query the meeting that the specified user is currently attending and in which the app bot is also present
lark-cli vc +meeting-list-active --as bot --user-id ou_xxx --format json
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--user-id <id>` | Required for app identity | Target user open_id, in the format `ou_...`. Do not pass it for user identity; for app identity it is passed through directly to the API, and internal user_id or numeric ID is not accepted |

<a id="身份语义"></a>
## Identity semantics

Do not expose internal identity abbreviations to users; refer to them only as "user identity" or "app identity".

| Identity | Command | Return scope | Subsequent event reading |
| ---- | ---- | -------- | ------------ |
| User identity | `--as user` | Meetings that the currently logged-in user is attending | Continue with `+meeting-events --as user` |
| App identity | `--as bot --user-id <user_open_id>` | Meetings that the target user is attending and in which the app bot is also present | Continue with `+meeting-events --as bot` |

Hard rule: whichever identity path `meeting_id` was obtained through, subsequent `+meeting-events` must use the same identity. Do not switch a `meeting_id` obtained through app identity to user identity for reading events, and do not force a `meeting_id` obtained through user identity to switch to app identity.

An empty return for app identity does not mean the target user is not in any meeting; it only means that no current meeting was found in which "the target user is in the meeting and the app bot is also in the meeting".

<a id="多会议选择"></a>
## Multiple meeting selection

- If multiple meetings are returned, do not automatically pick the first one.
- Show the user each candidate's `meeting_title` / `meeting_no` / `meeting_id`, and wait for the user to choose.
- After selection, use the same identity to execute `+meeting-events` to read events.

<a id="9-位会议号匹配"></a>
## 9-digit meeting number matching

When the user provides a 9-digit meeting number but does not explicitly request the app bot to join the meeting, treat the meeting number as a filter condition for the active meeting, not as a write operation instruction.

Matching rules:

- Match `meeting_no == <9位会议号>` among the returned meetings.
- Exactly one meeting matched: take that item's long numeric `meeting_id`, then use the same identity to call `+meeting-events`.
- Multiple meetings matched: show the candidates and let the user choose.
- No match: explain that the current identity did not find an active meeting corresponding to that meeting number; do not automatically call `+meeting-join` unless the user explicitly requests the app bot to join the meeting.

<a id="常见错误与排查"></a>
## Common errors and troubleshooting

| Error symptom | Root cause | Solution |
|---------|---------|---------|
| `--user-id is required when --as bot` | App identity did not pass the target user | Pass the target user open_id |
| User identity returns an empty list | The currently logged-in user has no visible ongoing meetings | Confirm whether the user is in a meeting, or whether the wrong identity was used |
| User identity has no permission / not visible | The currently logged-in user has no visible ongoing meetings, or the current identity cannot read that meeting | Do not repeatedly execute `auth login`. Confirm whether the user is in a meeting and whether the wrong profile was used; only when the user explicitly wants to query meetings visible to the app bot, use the target user open_id to execute `+meeting-list-active --as bot --user-id <user_open_id>` |
| App identity returns an empty list | There is no current meeting satisfying "the target user is in the meeting and the app bot is also in the meeting" | First have the app bot join the meeting, or confirm `user_id` and the meeting status |
| `--user-id` format error | An internal user_id or another non-`ou_...` value was passed | Pass the target user open_id instead |
| Insufficient app identity permission | App permissions, tenant installation, or the data scope accessible with the permission is not fully configured | Do not execute `auth login`. Ask the app developer to enable `vc:meeting.bot.join:write`; then check app publishing/installation and the data scope accessible with the permission; if it still fails after correct configuration, keep the error code and `log_id`, and troubleshoot as a server-side permission exception |

<a id="相关场景"></a>
## Related scenarios
- [In-meeting events and in-meeting interactions](../scenes/live-meeting-interact.md)
- [App bot meeting participation and in-meeting interactions](../scenes/live-meeting-attend.md)
