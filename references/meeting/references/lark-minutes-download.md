
# minutes +download


Download the audio/video media file of a Minutes to local storage, or obtain a download link valid for 1 day. Read-only operation, supports `--as user` / `--as bot`.

This module corresponds to shortcut: `lark-cli minutes +download`.

`minute_token` is resolved under a certain identity (such as `vc +recording --as bot`): when calling this command, you must explicitly carry over the same `--as`, do not omit it and let the identity be silently replaced by the default value (for complete rules, see "Identity Continuation" in [lark-shared](../../shared/index.md)).

<a id="命令"></a>
## Command

```bash
# Download Minutes (default layout, saved to ./minutes/{minute_token}/<server-filename>)
lark-cli minutes +download --minute-tokens obcnxxxxxxxxxxxxxxxxxxxx

# Specify output file (single token, file path)
lark-cli minutes +download --minute-tokens obcnxxxxxxxxxxxxxxxxxxxx --output ./meeting.mp4

# Specify output directory (single/batch, directory path)
lark-cli minutes +download --minute-tokens obcnxxxxxxxxxxxxxxxxxxxx --output-dir ./downloads

# Only obtain the download link (valid for 1 day), do not download the file
lark-cli minutes +download --minute-tokens obcnxxxxxxxxxxxxxxxxxxxx --url-only

# Batch download multiple Minutes (default layout, each saved to ./minutes/{minute_token}/)
lark-cli minutes +download --minute-tokens obcnxxxxxxxxxxxxxxxxxxxx,obcnyyyyyyyyyyyyyyyyyyyy

# Batch download to the same specified directory
lark-cli minutes +download --minute-tokens obcnxxxxxxxxxxxxxxxxxxxx,obcnyyyyyyyyyyyyyyyyyyyy --output-dir ./downloads

# Preview API call
lark-cli minutes +download --minute-tokens obcnxxxxxxxxxxxxxxxxxxxx --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--minute-tokens <tokens>` | Yes | Minutes Token, comma-separated supports batch (up to 50) |
| `--output <path>` | No | Output file path (single token). If an existing directory is passed, equivalent to `--output-dir`. Mutually exclusive with `--output-dir` |
| `--output-dir <dir>` | No | Output directory (single/batch). Mutually exclusive with `--output` |
| `--overwrite` | No | Overwrite existing output file |
| `--url-only` | No | Only return the download link, do not download the file |
| `--dry-run` | No | Preview API call, do not execute |

> **Default location**: When `--output` / `--output-dir` is not specified, the file is saved to `./minutes/{minute_token}/<server-filename>`. The file name is inferred from the server-side Content-Disposition / Content-Type, and the Agent can read the actual path from the `saved_path` field. The recording and the `minutes +detail` transcript of the same minute_token are by default saved in the **same directory**, for easy aggregation.

<a id="核心约束"></a>
## Core Constraints

<a id="1-妙记必须已完成转写"></a>
### 1. Minutes must have completed transcription

The audio/video file can only be downloaded after the Minutes transcription is complete. If the Minutes is not yet ready, the API returns a `2091003` error.

<a id="2-下载链接有效期-1-天"></a>
### 2. Download link valid for 1 day

The link returned by `--url-only` is valid for 1 day; after expiration, it must be obtained again.

<a id="3-频率限制"></a>
### 3. Rate limit

The API is rate-limited to 5 times/second; when batch downloading, be careful to control the frequency.

<a id="4-所需权限"></a>
### 4. Required permissions

| Identity | Required permission |
|------|---------|
| user / bot | `minutes:minutes.media:export` |

<a id="输出结果"></a>
## Output

<a id="下载模式默认"></a>
### Download mode (default)

Single token:

```json
{
  "minute_token": "obcnxxxxxxxxxxxxxxxxxxxx",
  "artifact_type": "recording",
  "saved_path": "/path/to/minutes/obcnxxxxxxxxxxxxxxxxxxxx/访谈一则.m4a",
  "size_bytes": 52428800
}
```

Batch: `downloads` array, each entry has the same structure as above, failed entries carry a `error` field.

| Field | Description |
|------|------|
| `minute_token` | Minutes Token (used for Agent indexing) |
| `artifact_type` | Fixed to `"recording"` (distinguished from `"transcript"` of `minutes +detail`) |
| `saved_path` | Local path where the file is saved (absolute path) |
| `size_bytes` | File size (bytes) |

<a id="url-模式--url-only"></a>
### URL mode (--url-only)

```json
{
  "minute_token": "obcnxxxxxxxxxxxxxxxxxxxx",
  "download_url": "https://..."
}
```

| Field | Description |
|------|------|
| `minute_token` | Minutes Token |
| `download_url` | Media file download link (valid for 1 day) |

<a id="如何获取-minute_token"></a>
## How to obtain minute_token

| Source | How to obtain |
|------|---------|
| Minutes URL | Extract from the end of the URL, e.g. `https://sample.feishu.cn/minutes/obcnxxxxxxxxxxxxxxxxxxxx` → `obcnxxxxxxxxxxxxxxxxxxxx` |
| Minutes metadata query | `lark-cli minutes minutes get --params '{"minute_token": "obcn..."}'` |
| Meeting recording query | `lark-cli vc +recording --meeting-ids <id>` or `lark-cli vc +recording --calendar-event-ids <event_id>` |

<a id="常见错误与排查"></a>
## Common errors and troubleshooting

| Error symptom | Error code | Root cause | Solution |
|---------|--------|---------|---------|
| Invalid parameter | 2091001 | minute_token format is incorrect | Check whether the token is complete (24 characters) |
| Resource not found | 2091002 | token does not exist | Confirm the minute_token is correct |
| Minutes not yet ready | 2091003 | Transcription not complete | Wait for transcription to complete and retry |
| Resource deleted | 2091004 | Minutes has been deleted | Confirm the Minutes file still exists |
| Insufficient permission | 2091005 | No read permission | Check whether you have access permission for this Minutes |
| `missing required scope(s)` | — | Current identity lacks scope | `--as user`: run `auth login --scope "minutes:minutes.media:export"`; `--as bot`: use the `console_url` in the error to enable it in the developer console, **do not** execute `auth login` on the bot (see permission management in [lark-shared](../../shared/index.md)) |

<a id="提示"></a>
## Tips

- Audio/video files may be large; there is no fixed timeout limit for downloading (cancellation is controlled by the user via Ctrl+C).
- The default location `./minutes/{minute_token}/` shares the same directory as the `minutes +detail` transcript, making it easy for the Agent to aggregate the original audio/video and transcript of the same Minutes.
- In single token mode, if `--output` is passed an existing directory (such as `--output ./existing-dir`), it is equivalent to `--output-dir`, and the file is saved into that directory (cp semantics).
- In batch mode, `--output` does not accept an existing file path (it will error); use `--output-dir` instead.
- To obtain the Minutes summary content (transcript, AI summary, etc.), use [minutes +detail](lark-minutes-detail.md).

<a id="相关场景"></a>
## Related scenarios
- [Query Minutes and its artifacts](../scenes/query-minutes-and-artifacts.md)
