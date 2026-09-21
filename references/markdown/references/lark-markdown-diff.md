# markdown +diff


Compare two historical versions of native Markdown in Drive, or compare remote Markdown with a local `.md` draft. When you need a historical version number, first use [`drive +version-history`](../../drive/references/lark-drive-version-history.md) to obtain `version`, do not use `tag`.

<a id="命令"></a>
## Command

```bash
# Compare two remote versions
lark-cli markdown +diff \
  --file-token boxcnxxxx \
  --from-version 7633658129540910621 \
  --to-version 7633658129540910628

# Compare a historical version with the remote latest version
lark-cli markdown +diff \
  --file-token boxcnxxxx \
  --from-version 7633658129540910621

# Compare the remote latest version with a local draft
lark-cli markdown +diff \
  --file-token boxcnxxxx \
  --file ./draft.md \
  --format pretty

# Compare a specified remote version with a local draft
lark-cli markdown +diff \
  --file-token boxcnxxxx \
  --from-version 7633658129540910621 \
  --file ./draft.md

# Preview the underlying request
lark-cli markdown +diff \
  --file-token boxcnxxxx \
  --from-version 7633658129540910621 \
  --to-version 7633658129540910628 \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | Target Markdown file token |
| `--from-version` | No | Base remote version; required when `--file` is not passed, when `--file` is passed, omitting it means "remote latest vs local file" |
| `--to-version` | No | Target remote version; requires passing `--from-version` at the same time, and cannot be used together with `--file`. When omitted, it means the remote latest version |
| `--file` | No | Local `.md` file path; after passing it, enters "remote vs local" comparison mode |
| `--context-lines` | No | Number of context lines to keep before and after each hunk in the unified diff, default `3` |
| `--format` | No | Only supports `json` (default) and `pretty` |

<a id="关键行为"></a>
## Key behaviors

- When `--file` exists:
  - Omitting `--from-version` = compare "remote latest version vs local file"
  - Passing `--from-version` = compare "specified remote version vs local file"
- `--to-version` can only be used for "remote version vs remote version", and cannot appear together with `--file`
- `--format pretty` outputs a colored unified diff; `--format json` returns a structured summary and the complete diff text
- When there is no difference:
  - In the `json` output, `changed=false`
  - The `pretty` output is fixed as `No differences.`

<a id="返回值"></a>
## Return value

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "changed": true,
    "mode": "remote_vs_remote",
    "file_token": "boxcnxxxx",
    "from_version": "7633658129540910621",
    "to_version": "7633658129540910628",
    "from_label": "a/boxcnxxxx@version:7633658129540910621",
    "to_label": "b/boxcnxxxx@version:7633658129540910628",
    "added_lines": 3,
    "deleted_lines": 2,
    "context_lines": 3,
    "hunks": [
      {
        "header": "@@ -1,6 +1,7 @@",
        "old_start": 1,
        "old_lines": 6,
        "new_start": 1,
        "new_lines": 7
      }
    ],
    "diff": "--- a/boxcnxxxx@version:7633658129540910621\n+++ b/boxcnxxxx@version:7633658129540910628\n@@ -1,2 +1,2 @@\n..."
  }
}
```

Complete field descriptions:

| Field | Level | Meaning |
|------|------|------|
| `ok` | Top level | CLI general success flag; `true` indicates the command executed successfully |
| `identity` | Top level | The identity used for this execution, usually `user` or `bot` |
| `data` | Top level | The business result object of this diff |
| `changed` | `data` | Whether a difference exists; `true` indicates the two sides differ, `false` indicates they are completely identical |
| `mode` | `data` | Comparison mode; `remote_vs_remote` = remote to remote, `remote_vs_local` = remote to local |
| `file_token` | `data` | Token of the remote Markdown file being compared |
| `from_version` | `data` | Base remote version number; may be an empty string for remote latest vs local |
| `to_version` | `data` | Target remote version number; usually an empty string when the target side is the remote latest version or a local file |
| `from_label` | `data` | Label name for the base side of the unified diff, which appears directly in the `---` header of the `diff` text |
| `to_label` | `data` | Label name for the target side of the unified diff, which appears directly in the `+++` header of the `diff` text |
| `added_lines` | `data` | Count of added lines |
| `deleted_lines` | `data` | Count of deleted lines |
| `context_lines` | `data` | Number of context lines kept before and after each hunk, corresponding to the passed `--context-lines` |
| `hunks` | `data` | Structured array of change block summaries; each element corresponds to one `@@ ... @@` section in the patch |
| `diff` | `data` | Complete unified diff text; best suited for direct reading or saving |
| `local_file` | `data` | Appears only in `remote_vs_local` mode; the value is exactly the local Markdown path passed to `--file` |

Label field notes:

- `from_label` / `to_label` are only used to identify the two sides of the diff, and do not represent additional API fields
- `from_label` indicates the base side, `to_label` indicates the target side
- Remote versions are usually in the form `a/<file_token>@version:<version>`, `b/<file_token>@version:<version>`
- When the target side is the remote latest version, `to_label` is in the form `b/<file_token>@latest`
- When the target side is a local file, `to_label` is in the form `b/./draft.md`

`hunks` subfield descriptions:

| Field | Meaning |
|------|------|
| `header` | Original hunk header, for example `@@ -3,1 +3,1 @@` |
| `old_start` | The line number where the old content starts |
| `old_lines` | How many lines this section of old content covers |
| `new_start` | The line number where the new content starts |
| `new_lines` | How many lines this section of new content covers |

Additional notes:

- `hunks` is suitable for agents or scripts to quickly locate the scope of changes; the complete line-by-line content is still based on the `diff` field
- When `changed=false`, `hunks` is usually an empty array, and `diff` is usually an empty string; if `--format pretty` is used, the terminal output will be `No differences.`

When comparing remote vs local, an additional field is returned:

```json
{
  "local_file": "./draft.md"
}
```

- `local_file`
  - Returned only when `--file` is passed and "remote vs local" mode is entered
  - The value is exactly the local Markdown path actually compared by this command, that is, the path you passed to `--file`
  - It represents the "target-side local file", not a temporary downloaded file, and not a remote file name
  - If this field is absent, it means this run is "remote version vs remote version"

<a id="参考"></a>
## References

- [lark-markdown](../index.md) — Markdown domain overview
- [lark-drive-version-history](../../drive/references/lark-drive-version-history.md) — Obtain historical version numbers usable for diff
- [lark-shared](../../shared/index.md) — Authentication and global parameters
