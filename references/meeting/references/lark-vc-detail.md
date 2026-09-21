
# vc +detail

Get meeting details by meeting ID, including basic information, the associated Minutes ID (`note_id`), and the Minutes Token (`minute_token`). Read-only, supports `--as user` / `--as bot`.

<a id="命令"></a>
## Command

```bash
# Single / batch (comma-separated, up to 50)
lark-cli vc +detail --meeting-ids <meeting_id1>,<meeting_id2>

# App identity (can only query meetings the app has permission for)
lark-cli vc +detail --meeting-ids <meeting_id1>,<meeting_id2> --as bot
```

<a id="输出字段"></a>
## Output fields

| Field | Description |
|------|------|
| `meeting_id` | Meeting ID |
| `meeting_no` | Meeting 9-digit number |
| `topic` | Meeting topic |
| `start_time` | Start time |
| `end_time` | End time |
| `note_id` | Associated Minutes ID. |
| `minute_token` | Associated Minutes Token. |

Cross-artifact selection and subsequent command chaining are orchestrated uniformly by [`query-meeting-and-artifacts`](../scenes/query-meeting-and-artifacts.md). After `note_id` / `minute_token` are obtained by this command, subsequent `note +detail`, `minutes +detail`, and Doc read commands must explicitly use the same `--as`.

<a id="相关场景"></a>
## Related scenarios
- [Query meetings and their artifacts](../scenes/query-meeting-and-artifacts.md)
