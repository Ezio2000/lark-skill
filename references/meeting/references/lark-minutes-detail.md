
# minutes +detail

Query Minutes details via `minute_token`, and retrieve AI outputs (summary/todos/chapters/transcript/keywords) as needed. Read-only, supports `--as user` / `--as bot`.

When `minute_token` is obtained by a certain identity, this command and the subsequent `note +detail`, `docs +fetch` must all explicitly use the same `--as`.

> `--summary` / `--todo` / `--chapter` / `--keyword` / `--transcript` are all optional; when requesting the corresponding output, it must be explicitly passed in. When no output flag is passed, only basic information (such as `title`) is returned, and no AI output fields will appear. To retrieve all outputs at once: `--summary --todo --chapter --keyword --transcript`.

<a id="命令"></a>
## Command

```bash
# Basic information only
lark-cli minutes +detail --as <source_identity> --minute-tokens obcxxxxxxxxxx

# Batch (comma-separated, up to 50)
lark-cli minutes +detail --as <source_identity> --minute-tokens obcxxx,obcyyy --summary --todo

# All outputs
lark-cli minutes +detail --as <source_identity> --minute-tokens obcxxx --summary --todo --chapter --keyword --transcript

# Transcript only, overwrite existing file, specify output directory
lark-cli minutes +detail --as <source_identity> --minute-tokens obcxxx --transcript --overwrite --output-dir ./out
```

<a id="输出"></a>
## Output

Each entry in the `minutes` array contains `minute_token`, `title`, `note_id`, `artifacts`. `note_id` is returned only when the Minutes is associated with meeting notes, and can be passed directly to [`note +detail`](lark-note-detail.md) to get the notes document token, without going back to `vc +detail`. `artifacts` **contains only the outputs requested this time**:

| Field | Type | Description |
|------|------|------|
| `artifacts.summary` | string | AI summary. |
| `artifacts.todos` | array | Todo list. |
| `artifacts.chapters` | array | Chapter list. |
| `artifacts.keywords` | array | Keyword list. |
| `artifacts.transcript_file` | string | Local file path of the transcript. |

The transcript is saved by default to `./minutes/{minute_token}/transcript.txt`, in the same directory as `minutes +download` for easy aggregation. When `--output-dir <dir>` is specified, it is written to `<dir>/artifact-{title}-{minute_token}/transcript.txt` instead.

<a id="minute_token-来源"></a>
## minute_token sources

| Source | Value field |
|------|---------|
| Minutes URL `https://*.feishu.cn/minutes/obcxxx` | Take the last segment of the path `obcxxx` |
| `vc +detail --meeting-ids` | `minute_token` |
| `vc +recording --meeting-ids` | `minute_token` |
| `minutes +search` | `minute_token` |

`minute_token` should not be passed directly to `note +detail`: when a Note needs to be associated, first read `note_id` from the result of this command. Cross-output workflows are orchestrated by [`query-minutes-and-artifacts`](../scenes/query-minutes-and-artifacts.md).

<a id="相关场景"></a>
## Related scenarios
- [Query Minutes and its outputs](../scenes/query-minutes-and-artifacts.md)
