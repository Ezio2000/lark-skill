
# vc +meeting-leave

Leave the video meeting that the current identity is in via `meeting_id` (bot leave). This is a **write operation** that actually removes the current identity from the meeting.

This module corresponds to the shortcut: `lark-cli vc +meeting-leave` (calls `POST /open-apis/vc/v1/bots/leave`).

<a id="命令"></a>
## Command

```bash
# Leave the meeting via meeting_id
lark-cli vc +meeting-leave --as bot --meeting-id 69xxxxxxxxxxxxx28
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--meeting-id <id>` | Yes | Meeting ID (**not the 9-digit meeting number**) |
| `--dry-run` | No | Preview the API call without actually leaving the meeting; use it to confirm the request when the meeting_id or identity is uncertain |

<a id="核心约束"></a>
## Core Constraints

<a id="1-入参是-meeting_id不是会议号"></a>
### 1. The input parameter is meeting_id, not the meeting number

`--meeting-id` must be the meeting's long numeric ID, usually provided by `meeting.id` in the response body of `+meeting-join --as bot`, and can also be obtained from `meeting_id` in the response body of the app identity's `+meeting-list-active --as bot --user-id <user_open_id>`. **Passing the 9-digit meeting number will fail**.

<a id="2-优先使用-bot-身份"></a>
### 2. Prefer using the bot identity

This is the app bot's leave-meeting capability, using the same `--as bot` as joining a meeting or active meeting discovery. It can only make the current identity leave on its own; it cannot forcibly remove other participants.

<a id="3-当前身份必须在会议中"></a>
### 3. The current identity must be in the meeting

The app bot must already be in the meeting, otherwise the API will return an error. If `meeting_id` comes from `+meeting-list-active`, you must confirm that this is a meeting discovered by the app identity.

<a id="4-离会立即生效对其他参会人可见"></a>
### 4. Leaving takes effect immediately and is visible to other participants

The bot will immediately disappear from the participant list; if recording/minutes are enabled for the meeting, the bot's participation period ends here. Only call it when the user explicitly requests to exit / leave / end participation; if you need to rejoin, just run `+meeting-join` again (it is not truly "irreversible").

<a id="输出结果"></a>
## Output Result

When the API returns successfully, the default output is: `Left meeting <meeting-id> successfully.`.
`--format json` returns the standard `{ok, identity, data}` envelope, for example `{"ok":true,"identity":"bot","data":{}}`, not the raw API response body with `code` / `msg`.

<a id="如何获取输入参数"></a>
## How to Obtain Input Parameters

| Input Parameter | How to Obtain |
|---------|---------|
| `meeting-id` | `meeting.id` returned by `+meeting-join --as bot`; or `meeting_id` returned by the app identity's `+meeting-list-active --as bot --user-id <user_open_id>` |

<a id="常见错误与排查"></a>
## Common Errors and Troubleshooting

| Error Symptom | Root Cause | Solution |
|---------|---------|---------|
| `--meeting-id is required` | `--meeting-id` was not passed in | Pass in the `meeting.id` obtained from `+meeting-join --as bot`, or the `meeting_id` returned by the app identity's `+meeting-list-active` |
| `meeting not found` / `invalid meeting_id` | The 9-digit meeting number was mistakenly passed | You must use `meeting.id`, not the meeting number |
| `not in meeting` | The current identity is not in that meeting | Confirm that `+meeting-join` succeeded first |

<a id="提示"></a>
## Tips

- Only call it when the user explicitly requests to exit / leave / end participation; leaving will make the bot disappear from the participant list, visible to other participants. If you need to rejoin, just run `+meeting-join` again; it is not truly "irreversible". When unsure about the parameter format, you can optionally use `--dry-run` to preview.
- For `+meeting-leave`, prefer the `meeting.id` returned by `+meeting-join --as bot`, but it is not necessary to call leave after every join.
- If `meeting_id` comes from `+meeting-list-active`, it must come from the app identity, and confirm that the app bot is in that meeting. Do not use the 9-digit meeting number.

<a id="相关场景"></a>
## Related Scenarios
- [App bot joining a meeting and in-meeting interaction](../scenes/live-meeting-attend.md)
