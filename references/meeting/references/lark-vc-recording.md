
# vc +recording


Query the corresponding minute_token by meeting_id or calendar_event_id. This is the bridge command between the VC domain and the Minutes domain. Read-only operation.

> **Boundary reminder:** If the user explicitly wants "Minutes info", "Minutes details", "Minutes link", "minute_token", "title", "duration", "owner", or similar Minutes metadata, first use this command to get the `minute_token`, then call `minutes minutes get`. Do not switch directly to `minutes +detail`; `minutes +detail` is only used for Minutes content and transcripts.

This module corresponds to shortcut: `lark-cli vc +recording`.

<a id="命令"></a>
## Command

```bash
# Query by meeting ID (comma-separated supports batch, up to 50)
lark-cli vc +recording --meeting-ids 69xxxxxxxxxxxxx28
lark-cli vc +recording --meeting-ids 69xxxxxxxxxxxxx28,69xxxxxxxxxxxxx29

# Query by calendar event ID
lark-cli vc +recording --calendar-event-ids xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx_0

# Output format
lark-cli vc +recording --meeting-ids 69xxxxxxxxxxxxx28 --format json

# Preview API call
lark-cli vc +recording --meeting-ids 69xxxxxxxxxxxxx28 --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--meeting-ids <ids>` | Choose one | Meeting ID, comma-separated supports batch |
| `--calendar-event-ids <ids>` | Choose one | Calendar event ID, comma-separated supports batch |
| `--format <fmt>` | No | Output format: json (default) / pretty / table / ndjson / csv |
| `--dry-run` | No | Preview API call, do not execute |

<a id="核心约束"></a>
## Core constraints

<a id="1-两种参数互斥"></a>
### 1. The two parameters are mutually exclusive

Only one input method can be specified at a time. Passing both will cause an error.

<a id="2-身份支持"></a>
### 2. Identity support

`--meeting-ids` and `--calendar-event-ids` both support `--as user` / `--as bot`. User identity can only query recordings the user has permission for; app identity can only query recordings the app has permission for. After obtaining the `minute_token`, when passing it to `minutes minutes get`, `minutes +detail`, or `minutes +download`, you must explicitly use the same `--as`.

<a id="3-批量上限"></a>
### 3. Batch limit

A maximum of 50 IDs can be passed per call.

<a id="4-录制必须已完成"></a>
### 4. Recording must be completed

The recording must be fully generated before it can be queried. Recordings with a duration < 5 seconds may not generate a file.

<a id="输出结果"></a>
## Output result

Returns a `recordings` array, where each record contains:

| Field | Description |
|------|------|
| `meeting_id` | Meeting ID |
| `calendar_event_id` | Calendar event ID (only for the `--calendar-event-ids` path) |
| `minute_token` | Minutes Token parsed from the recording URL |
| `recording_url` | Recording URL |
| `duration` | Recording duration (milliseconds) |
| `error` | Error message (only present when the query fails) |

<a id="如何获取输入参数"></a>
## How to obtain input parameters

| Input parameter | How to obtain |
|---------|---------|
| `meeting_id` | Use `lark-cli vc +search` to search historical meetings, and take the `id` field from the result |
| `calendar_event_id` | Use `lark-cli calendar +agenda` to view the calendar, and take the `event_id` field from the result |

<a id="常见错误与排查"></a>
## Common errors and troubleshooting

| Error symptom | Root cause | Solution |
|---------|---------|---------|
| `exactly one of ... is required` | No parameter passed or multiple types passed at the same time | Specify only one input method |
| `no recording available` | The meeting has no recording or the recording is not complete | Confirm the meeting has ended and recording was enabled |
| `121005 no permission` | No permission to view the meeting recording | Confirm you are a meeting participant or have recording permission |
| `124002 recording generating` | The recording file is still being generated | Wait for the recording to complete and retry |
| `missing required scope(s)` | Insufficient permissions | `--as user`: follow the prompt to run `auth login --scope`; `--as bot`: use the `console_url` in the error to enable it in the developer console, and **do not** execute `auth login` on the bot (see permission management in [lark-shared](../../shared/index.md)) |

<a id="提示"></a>
## Tips

- By default, `--format json` output is used; Agents are better at parsing JSON data.
- When troubleshooting parameters and request structure, prefer `--dry-run`.
- `minute_token` is parsed from the tail segment of the recording URL (`https://meetings.feishu.cn/minutes/{minute_token}`).
- After obtaining the `minute_token`, if you want basic Minutes information, prefer passing it to `minutes minutes get`; if you want to download media files, pass it to `minutes +download`; if you want transcripts, summaries, todos, or chapters, then pass it to `minutes +detail --minute-tokens`.

<a id="相关场景"></a>
## Related scenarios
- [Query meetings and their artifacts](../scenes/query-meeting-and-artifacts.md)
