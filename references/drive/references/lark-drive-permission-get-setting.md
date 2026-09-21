<a id="drive-permission-get-setting查询权限设置"></a>
# drive +permission-get-setting (query permission settings)

This module corresponds to shortcut: `lark-cli drive +permission-get-setting`. It reads the public access, sharing, collaborator management, security, and comment permission settings of a single Drive resource itself, and does not recursively read sub-resources within a folder.

<a id="命令"></a>
## Command

```bash
# Automatically infer type from URL
lark-cli drive +permission-get-setting \
  --token 'https://example.feishu.cn/drive/folder/<folder_token>' \
  --as user --format json

# Explicitly specify type via bare token
lark-cli drive +permission-get-setting \
  --token '<folder_token>' \
  --type folder \
  --as user --format json
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--token` | Yes | bare token or full URL. URL paths support `/folder/`, `/docx/`, `/doc/`, `/sheets/`, `/base/`, `/bitable/`, `/wiki/`, `/file/`, `/mindnotes/`, `/slides/`, `/minutes/`, `/page/`. |
| `--type` | Required for bare token | Target type: `doc` / `sheet` / `file` / `wiki` / `bitable` / `docx` / `mindnote` / `minutes` / `slides` / `folder` / `apps`. URL can be automatically inferred; if both a URL and a conflicting `--type` are passed, the CLI will reject it. |
| `--dry-run` | No | Only print the request, do not call the API. |

<a id="输出"></a>
## Output

The `data.permission_public` in the JSON output is the target's current permission settings; when the server does not return this field, the command reports a response structure error rather than disguising other fields as permission settings.

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "permission_public": {}
  }
}
```

`--format pretty` will display the complete `permission_public` object, including fields that the server may add in the future.

<a id="行为说明"></a>
## Behavior notes

- **Identity support**: Both `--as user` and `--as bot` are available.
- **Required scope**: `docs:permission.setting:read`.
- **Single-target read**: The command only reads the permission settings of the resource itself pointed to by `--token`; `--type folder` does not recursively read sub-resources.
