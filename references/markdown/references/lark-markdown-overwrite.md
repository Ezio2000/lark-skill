# markdown +overwrite


Overwrite an existing native Markdown file in Drive and return the new version number after overwriting.

<a id="命令"></a>
## Command

```bash
# Overwrite with inline content
lark-cli markdown +overwrite \
  --file-token boxcnxxxx \
  --content '# Updated'

# Overwrite with a local .md file
lark-cli markdown +overwrite \
  --file-token boxcnxxxx \
  --file ./README.md

# Explicitly specify a new file name while overwriting content
lark-cli markdown +overwrite \
  --file-token boxcnxxxx \
  --name NEW-README.md \
  --content '# Updated'

# Use --content to read from a local file
lark-cli markdown +overwrite \
  --file-token boxcnxxxx \
  --content @./README.md

# Overwrite with stdin
printf '# Updated\n' | \
  lark-cli markdown +overwrite \
    --file-token boxcnxxxx \
    --content -

# Preview the underlying request
lark-cli markdown +overwrite \
  --file-token boxcnxxxx \
  --content '# Updated' \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | Target Markdown file token |
| `--name` | No | Explicitly specify the file name after overwriting; must have the `.md` suffix. When passed, it takes precedence |
| `--content` | Conditionally required | New Markdown content; mutually exclusive with `--file`; supports passing a string directly, `@file`, `-` (stdin) |
| `--file` | Conditionally required | Local `.md` file path; mutually exclusive with `--content` |

<a id="关键约束"></a>
## Key Constraints

- Exactly one of `--content` and `--file` must be provided
- If `--name` is passed, use it directly as the file name after overwriting
- If `--name` is not passed and `--content` is used, keep the original remote file name by default
- If `--name` is not passed and `--file` is used, use the local file name by default
- The local file name pointed to by `--file` must have the `.md` suffix
- After a successful overwrite, `version` **must** be returned

<a id="返回值"></a>
## Return Value

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "file_token": "boxcnxxxx",
    "file_name": "README.md",
    "version": "7633658129540910621",
    "size_bytes": 2048
  }
}
```

Where:

- `version` is the new version number after overwrite writing
- `size_bytes` is the content size after this overwrite

<a id="参考"></a>
## References

- [lark-markdown](../index.md) — Markdown domain overview
- [lark-shared](../../shared/index.md) — Authentication and global parameters
