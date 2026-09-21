# minutes +upload


Upload audio/video files to Feishu Minutes and generate a Minute.

This module corresponds to the shortcut: `lark-cli minutes +upload`.

<a id="典型触发表达"></a>
## Typical trigger expressions

- "Convert this audio/video file into a Minute"
- "Convert this audio/video file into meeting notes"
- "Convert this audio/video file into a verbatim transcript, text transcript, or written text"
- "Convert this audio/video file into a summary, to-dos, or chapters"

<a id="命令示例"></a>
## Command example

```bash
# Generate a Minute from a file_token already uploaded to cloud space (Drive/cloud storage)
lark-cli minutes +upload --file-token boxcnxxxxxxxxxxxxxxxx

```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token <token>` | Yes | The file_token of the audio/video file already uploaded to Feishu cloud space (Drive/cloud storage) |

<a id="支持的格式与限制"></a>
## Supported formats and limits

The original audio/video file to be uploaded to Minutes must meet the following requirements:

- Supported audio formats: `wav`, `mp3`, `m4a`, `aac`, `ogg`, `wma`, `amr`
- Supported video formats: `avi`, `wmv`, `mov`, `mp4`, `m4v`, `mpeg`, `ogg`, `flv`
- Audio/video duration must not exceed `6` hours
- File size must not exceed `6 GB`

> Note: This shortcut only accepts `file_token` and does not directly read local file contents, so these format, duration, and size limits apply to the **original uploaded file** itself. If Minute generation fails, first check back whether the source file meets the above requirements.

<a id="核心约束"></a>
## Core constraints

<a id="1-必须提供-file_token"></a>
### 1. file_token must be provided

This API does not directly handle uploading local files. You must first use `drive +upload` to upload the file to cloud space (Drive/cloud storage) to obtain `file_token`, and then call this API.

<a id="2-异步生成"></a>
### 2. Asynchronous generation

The API returns `minute_url` immediately, but the Minute may still be generating asynchronously. `minutes +upload` does not return processing status; a successful command only means the asynchronous creation request has been submitted. Only after subsequently executing `minutes +detail` and confirming readiness can you claim that the Minute artifact has been generated or is available. Upload and subsequent artifact retrieval are orchestrated by [`create-and-edit-minutes`](../scenes/create-and-edit-minutes.md); when querying the artifact immediately after upload, `minutes +detail` must use `--wait-ready`.

<a id="输出结果示例"></a>
## Output result example

```json
{
  "minute_url": "http(s)://<host>/minutes/<minute-token>",
  "minute_token": "<minute-token>"
}
```

| Field | Description |
|------|------|
| `minute_url` | The generated Minute access link |
| `minute_token` | The Minute Token extracted from `minute_url`, which can be passed directly to `minutes +detail --minute-tokens` |

<a id="常见错误与排查"></a>
## Common errors and troubleshooting

| Error symptom | Error code | Root cause | Solution |
|---------|--------|---------|---------|
| `error.subtype` = `quota_exceeded` | 2091008 | ASR/AI quota is exhausted, insufficient to transcribe this audio/video, and the Minute was not created | Have the user check the quota details on the Minute detail page; the CLI cannot supplement or increase quota, and retrying the same `--file-token` will not succeed |

<a id="相关场景"></a>
## Related scenarios
- [Generate and modify Minutes](../scenes/create-and-edit-minutes.md)
