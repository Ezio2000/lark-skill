
# vc +meeting-join

Use a 9-digit meeting number to have the app bot join an ongoing video meeting. This is a **write operation** that actually makes the app bot join the meeting.

This module corresponds to the shortcut: `lark-cli vc +meeting-join` (calls `POST /open-apis/vc/v1/bots/join`).

> **Do not equate a 9-digit meeting number with an intent to join.** When the user provides a 9-digit meeting number and asks "what was discussed in the meeting / check in-meeting events", first use `vc +meeting-list-active` to look up current active meetings and match by `meeting_no`; only call this command when the user explicitly requests "join the meeting / have the app bot listen in / attend on my behalf".

<a id="命令"></a>
## Command

```bash
# Specify only the meeting number (no password)
lark-cli vc +meeting-join --as bot --meeting-number 123456789

# Start a scheduled meeting (app identity only)
lark-cli vc +meeting-join --as bot --meeting-number 123456789 --action start
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--meeting-number <no>` | Yes | Meeting number, must be **9 pure digits** |
| `--password <pw>` | No | Meeting password, passed only when the meeting has a join password set |
| `--call-id <id>` | No | The `call_id` passed through from the `vc.bot.meeting_invited_v1` invitation event; just pass it back as-is. Do not pass it when the Agent actively joins a meeting or there is no invitation event source |
| `--action join\|start` | No | Defaults to `join`, keeping the normal join path; `start` is a parameter exclusive to scheduled-meeting initiation, using the same `bots/join` API to start a meeting, and must `--as bot` |
| `--dry-run` | No | Preview the API call without actually joining the meeting; use it first to confirm the request when the meeting number or identity is uncertain |

<a id="核心约束"></a>
## Core Constraints

<a id="1-使用应用身份"></a>
### 1. Use app identity

This is an app bot meeting-join capability, using `--as bot`. Do not attempt to have the app bot join a meeting using the currently logged-in user identity.

By default, `join` does not write the `action` field into the request body, nor does it enter scheduled-meeting initiation filtering. Only `--action start` writes `action: 2`, entering scheduled-meeting initiation filtering and validation separately.

<a id="2-会议号格式严格校验"></a>
### 2. Strict meeting number format validation

`--meeting-number` must be 9 pure digits, otherwise local validation fails immediately:
`--meeting-number must be exactly 9 digits`.

Common sources of error:
- Pasting the entire meeting link (only the trailing 9 digits should be taken)
- Passing `meeting_id` (a long numeric ID) as the meeting number (the two are not the same thing)

<a id="3-会议必须已开始且允许入会"></a>
### 3. The meeting must have started and allow joining

- `--action join` requires the meeting to be **in progress**; `--action start` is used to start a qualifying scheduled meeting.
- If the meeting has a **waiting room / join approval** set, the app bot may need the host to admit it before it actually joins.
- If `HTTP 403: no permission` is returned (error code `121003`), do not interpret it merely as "the account has no permission". The more common cause of this type of error is that the meeting parameters or meeting control configuration currently do not satisfy the join conditions, for example: the meeting number is wrong, the password is not passed or is incorrect, the meeting has not yet started, the waiting room / join approval has not admitted it, the meeting prohibits external/specific identities from joining, etc. Confirm these configuration items first, then retry.

<a id="4-机器人入会后对其他参会人可见"></a>
### 4. After the bot joins, it is visible to other participants

This is a real join operation; the bot will immediately appear in the participant list, be visible to other participants, and generate a meeting log. The social cost of mistakenly joining the wrong meeting is higher than the technical cost—before executing, confirm the source of the 9-digit meeting number (user input / end of the meeting link) first; do not make it up. If you have questions about the parameter format, you can use `--dry-run` to preview the request body.

<a id="输出结果"></a>
## Output

The API returns basic meeting information; the fields depend on the specific response. Common fields:

| Field | Description |
|------|------|
| `meeting.id` | Meeting ID (can later be passed to `+meeting-leave --as bot --meeting-id`) |
| `meeting.meeting_no` | Meeting number (consistent with the input parameter) |
| `meeting.topic` | Meeting topic |
| `meeting.start_time` | Meeting start time |

> **Important**: Once you get `meeting.id`, be sure to keep it; leaving the meeting (`+meeting-leave`) requires using it, not the meeting number.

<a id="如何获取输入参数"></a>
## How to obtain input parameters

| Input parameter | How to obtain |
|---------|---------|
| `meeting-number` | The meeting number is shared by the host; it can also be parsed as the 9 digits at the end of the meeting link |
| `password` | If the meeting has a join password set, it is provided by the host |
| `call-id` | Carried by the `call_id` field of the `vc.bot.meeting_invited_v1` invitation event, passed through when the Agent receives the event; do not pass it in scenarios without an invitation event (such as the Agent actively joining a meeting) |

<a id="常见错误与排查"></a>
## Common errors and troubleshooting

| Error symptom | Root cause | Solution |
|---------|---------|---------|
| `--meeting-number must be exactly 9 digits` | The meeting number is not 9 pure digits | Check whether a meeting link or meeting_id was mistakenly passed |
| Incorrect meeting password | `--password` is wrong or not provided | Confirm the meeting password with the host |
| Meeting does not exist / has ended | The meeting number is wrong or the meeting is not in progress | Confirm the meeting is in progress; when starting a scheduled meeting, use `--action start` instead |
| `HTTP 403: no permission` / `121003` | Join preconditions are not satisfied; usually not a simple scope issue | Confirm in order: 1) the meeting allows agents to join; 2) the meeting number is correct; 3) if there is a password, it has been correctly passed in `--password`; 4) the meeting has started; 5) the waiting room / join approval has admitted it; 6) the meeting does not prohibit the current identity from joining (e.g., restricting external, restricting app bots, only specific members may join); after confirming, retry |
| Insufficient app identity permissions | App permissions, tenant installation, or the data scope accessible by permissions is not fully configured | Do not execute `auth login`. Use the metadata / error envelope returned by the CLI to accurately confirm the missing permission; check app publishing/installation, and the open platform's "data scope accessible by permissions": select "filter by condition", with the condition "meeting owner contains matches the app's available scope"; if it still fails after correct configuration, keep the error code and `log_id`, and troubleshoot as a server-side permission anomaly |
| Join rejected | Waiting room / join approval / restriction on external joining | Contact the host to admit it or adjust the meeting settings |

<a id="提示"></a>
## Tips

- Use only when the Agent needs to **actually join** a meeting (e.g., a participant bot, in-meeting assistant); merely pulling meeting data does not require joining.
- Joining will make the bot immediately appear in the participant list; if the user requests to exit / leave / end participation, directly use `+meeting-leave --as bot --meeting-id <meeting.id>`. If the parameter format is uncertain, you may optionally use `--dry-run` to preview, but it is not a required step.
- After successful execution, immediately record the returned `meeting.id` for subsequent `+meeting-leave` / `+meeting-events`.

<a id="相关场景"></a>
## Related scenarios
- [App bot meeting participation and in-meeting interaction](../scenes/live-meeting-attend.md)
