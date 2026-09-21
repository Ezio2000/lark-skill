# drive +version-get


Download the file content of a specified version. This shortcut supports both `--as user` and `--as bot`; for automation scenarios, `--as bot` is recommended.

<a id="命令"></a>
## Command

```bash
lark-cli drive +version-get \
  --file-token boxcnxxxxxxxx \
  --version 7633658129540910621 \
  --as bot

lark-cli drive +version-get \
  --file-token boxcnxxxxxxxx \
  --version 7633658129540910621 \
  --as user

lark-cli drive +version-get \
  --file-token boxcnxxxxxxxx \
  --version 7633658129540910621 \
  --output ./downloads/ \
  --as bot

lark-cli drive +version-get \
  --file-token boxcnxxxxxxxx \
  --version 7633658129540910621 \
  --output ./artifact.bin \
  --overwrite \
  --as bot
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | Target file token |
| `--version` | Yes | The long numeric `version` field returned by `drive +version-history`, not `tag` |
| `--output` | No | Local save path or directory; when omitted, saves to the current directory and prefers the server-side file name |
| `--overwrite` | No | Overwrite an existing local output file |

<a id="关键行为"></a>
## Key Behaviors

- When `--output` is omitted, the CLI saves to the current directory and prefers the server-side file name
- When `--output` points to an existing directory, or ends with `/` / `\\`, the CLI saves using the remote file name
- When `--output` is a file path without an extension, the CLI attempts to infer the extension from the response headers like `docs +media-download`; if it cannot be inferred, it remains without an extension
- When the target file already exists, it is only overwritten if `--overwrite` is explicitly passed

<a id="返回值"></a>
## Return Value

Return value:

```json
{
  "ok": true,
  "identity": "bot",
  "data": {
    "file_token": "boxcnxxxxxxxx",
    "version": "7633658129540910621",
    "file_name": "artifact.bin",
    "saved_path": "/abs/path/artifact.bin",
    "size_bytes": 12345
  }
}
```

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- All commands for Drive (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
