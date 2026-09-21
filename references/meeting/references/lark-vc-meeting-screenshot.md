# `vc +meeting-screenshot`

Get a video meeting screenshot and save it as JPEG.

<a id="常用用法"></a>
## Common Usage

Take a screenshot using the current user identity, with the file written to the default directory:

```bash
lark-cli vc +meeting-screenshot --as user --meeting-id <long_meeting_id>
```

Take a screenshot using the bot identity and specify the output path:

```bash
lark-cli vc +meeting-screenshot --as bot --meeting-id <long_meeting_id> --output ./meeting-screenshots/current.jpg
```

<a id="参数"></a>
## Parameters

| Flag | Meaning and Usage |
| --- | --- |
| `--as <identity>` | Choose the `user` or `bot` identity. Use the same identity as when discovering `meeting_id`: `user` requires the current user to be in the meeting; `bot` requires the bot to have joined the meeting and have in-meeting read permission. |
| `--meeting-id <meeting_id>` | Required. Long numeric meeting ID; a 9-digit meeting number is not accepted; if you only have the meeting number, first call `vc +meeting-list-active` with the same identity to obtain it. |
| `--output <relative-path>` | Optional. Specify the JPEG file name or a relative path containing subdirectories; relative to the current working directory when the command is executed. |
| `--overwrite` | Optional. Allow overwriting when the target file already exists; if not passed, the command fails and keeps the original file. |

<a id="文件路径与结果"></a>
## File Path and Result

- When `--output` is not specified, the default is to write to `meeting-screenshots/<meeting_id>-<UTC timestamp>.jpg` under the current working directory.
- `--output` can be just a file name, or it can contain multiple levels of subdirectories; parent directories are created automatically.
- Absolute paths are not accepted, nor are `..` or symbolic link paths that resolve outside the current working directory.
- A successful result includes the absolute file path, byte count, JPEG content type, SHA-256, and the server-side `log_id`.
- The server determines the screenshot content and verifies whether the meeting meets the conditions; the caller cannot specify the area to capture or the shared content. A failure does not overwrite an existing file.
