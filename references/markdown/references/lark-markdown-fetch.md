# markdown +fetch


Read the content of a native Markdown file in Drive; also supports saving the content locally.

<a id="命令"></a>
## Command

```bash
# Return Markdown text directly
lark-cli markdown +fetch --file-token boxcnxxxx

# Save locally
lark-cli markdown +fetch \
  --file-token boxcnxxxx \
  --output ./README.md

# When a directory is passed, save to that directory using the remote file name
lark-cli markdown +fetch \
  --file-token boxcnxxxx \
  --output ./downloads/

# Overwrite an existing file
lark-cli markdown +fetch \
  --file-token boxcnxxxx \
  --output ./README.md \
  --overwrite

# Preview the underlying request
lark-cli markdown +fetch \
  --file-token boxcnxxxx \
  --output ./README.md \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | Target Markdown file token |
| `--output` | No | Local save path; you can pass either a specific file name or a directory path. When a directory is passed, the remote file name is used for saving; when omitted, the Markdown content is returned directly |
| `--overwrite` | No | Overwrite an existing local output file; takes effect only when `--output` is passed |

<a id="返回值"></a>
## Return Value

When `--output` is not passed:

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "file_token": "boxcnxxxx",
    "file_name": "README.md",
    "content": "# Hello\n",
    "size_bytes": 8
  }
}
```

When `--output` is passed:

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "file_token": "boxcnxxxx",
    "file_name": "README.md",
    "saved_path": "/abs/path/README.md",
    "size_bytes": 8
  }
}
```

<a id="参考"></a>
## References

- [lark-markdown](../index.md) — Markdown domain overview
- [lark-shared](../../shared/index.md) — Authentication and global parameters
