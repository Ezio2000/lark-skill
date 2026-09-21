
# drive +status


Compare a local directory with a Feishu Drive (cloud drive/cloud storage) folder by **exact SHA-256** (default) or **fast modified_time** (`--quick`), and output four categories of differences:

| Field | Meaning |
|------|------|
| `new_local` | Exists only locally |
| `new_remote` | Exists only in the cloud |
| `modified` | Exists on both sides and is judged as changed by this check: with `detection=exact`, it means the hashes differ; with `detection=quick`, it means the local mtime differs from the remote `modified_time`, or the remote timestamp is not trustworthy |
| `unchanged` | Exists on both sides and is judged as unchanged by this check: with `detection=exact`, it means the hashes match; with `detection=quick`, it means the local mtime equals the remote `modified_time` |

Read-only command:

- Default `detection=exact`: for files present on both sides, a byte stream is pulled from the cloud and hashed in memory; nothing is downloaded to disk, but large directories / large files will generate considerable network traffic.
- With `--quick`, `detection=quick`: only compares the local mtime with the remote `modified_time`, **without downloading remote file contents**; suitable for a quick pre-check first; it is best-effort and is not equivalent to a strict content consistency judgment.

<a id="远端同名文件冲突"></a>
## Remote files with the same name conflict

If multiple entries in Drive map to the same `rel_path`, `+status` fails directly before download/hash, returning a typed error envelope on stderr (`error.type=validation`, `error.subtype=failed_precondition`); the `name` of each `error.params[]` is the conflicting `rel_path`, and `reason` enumerates all colliding entries under that path (`type` + `file_token`). Do not treat this situation as an ordinary `modified`; it means the sync domain itself is ambiguous, and you need to first clean up the cloud structure, or explicitly choose a conflict strategy only for the "duplicate file" scenario in `+pull` / `+push`.

<a id="命令"></a>
## Command

```bash
# Basic usage — two required parameters
lark-cli drive +status \
  --local-dir ./repo \
  --folder-token fldcnxxxxxxxxx

# Quick mode — only compares modified_time, does not download remote file contents
lark-cli drive +status \
  --local-dir ./repo \
  --folder-token fldcnxxxxxxxxx \
  --quick

# Only show items judged as modified (exact=hash mismatch; quick=mtime mismatch) (combined with --jq filtering)
lark-cli drive +status \
  --local-dir ./repo \
  --folder-token fldcnxxxxxxxxx \
  --jq '.modified'
```

<a id="参数"></a>
## Parameters

| Flag | Required | Type | Description |
|------|------|------|------|
| `--local-dir` | Yes | path | Local root directory (**must be a relative path to cwd**; absolute paths or relative paths that escape outside cwd are rejected directly by the CLI) |
| `--folder-token` | Yes | string | Drive folder token |
| `--quick` | No | bool | Quick mode: only compares the local mtime with the remote `modified_time`, skipping remote download and SHA-256 computation; `detection` in the output becomes `quick` |

<a id="输出-schema"></a>
## Output schema

On success:

```json
{
  "detection":  "exact",
  "new_local":  [{"rel_path": "..."}],
  "new_remote": [{"rel_path": "...", "file_token": "..."}],
  "modified":   [{"rel_path": "...", "file_token": "..."}],
  "unchanged":  [{"rel_path": "...", "file_token": "..."}]
}
```

Where:

- `detection=exact`: default mode; files present on both sides have their remote byte stream downloaded and compared via SHA-256.
- `detection=quick`: `--quick` mode; only makes a best-effort judgment based on the local mtime and the remote `modified_time`.

`rel_path` always uses `/` as the separator (consistent across platforms), relative to the root of `--local-dir` or `--folder-token`. When a file exists only locally, there is no `file_token` field.

When remote files with the same name conflict:

```json
{
  "ok": false,
  "identity": "user",
  "error": {
    "type": "validation",
    "subtype": "failed_precondition",
    "message": "1 rel_path(s) map to multiple Drive entries",
    "hint": "resolve the duplicate remote files first: re-run +pull with --on-duplicate-remote=rename (downloads each with a hashed suffix), or use --on-duplicate-remote=newest|oldest (supported by +pull/+sync/+push) to pick one, or delete the extra remote files; a plain retry will not help",
    "params": [
      {
        "name": "dup.txt",
        "reason": "2 Drive entries collide here: file <full_file_token>, folder <folder_token>"
      }
    ]
  }
}
```

<a id="比较范围"></a>
## Comparison scope

- **Only compares binary files in Drive `type=file`**. Online documents (`docx` / `sheet` / `bitable` / `mindnote` / `slides`) and shortcuts (`shortcut`) are all skipped — they have no equivalent local binary to align with, otherwise they would produce a large number of false positives in `new_remote`.
- Subfolders are traversed recursively; rel_path looks like `sub1/sub2/file.txt`.
- When multiple remote entries map to the same rel_path, no implicit choice is made; it fails by default.
- On the local side, only regular files are compared; symbolic links, device files, etc. are ignored.
- In `--quick` mode, files present on both sides are compared only at **remote time precision** for `modified_time` / local mtime: only if equal is it recorded as `unchanged`, otherwise it is recorded as `modified`; when the remote timestamp is missing or invalid, the conservative path is taken and it is recorded as `modified`, and it will not blindly judge `unchanged`.

<a id="范围限制"></a>
## Scope limits

The local side of `+status` only accepts relative paths under cwd. If the directory the user wants to compare is outside cwd, **do not have the agent `cd` on its own to bypass this**; have the user restart the agent in a suitable ancestor directory and then run it. Note: symlinking the target into cwd **also does not work** — path validation first `EvalSymlinks` and then determines whether it is out of bounds; if the real directory the link ultimately points to is outside cwd, it will still be rejected by `unsafe file path`. The CLI will report an error directly when the path is out of bounds; there is no need to manually validate in advance at the skill layer.

<a id="典型用法"></a>
## Typical usage

Treat +status as a read-only probe to "first look at the differences, then decide how to sync." Common connection scenarios:

- Want to know what content exists in the cloud but not locally → look at `new_remote`, and selectively pull as needed (`drive +download --file-token <token>`).
- Want to push newly added local content to the cloud → look at `new_local`, then `drive +upload --file <path> --folder-token <parent>` (note that +upload does not accept 0-byte files).
- Want to know which files were modified in the cloud by colleagues → look at `modified`, and check content differences one by one with `drive +download`.

<a id="性能注意"></a>
## Performance notes

- Under the default `detection=exact`, the total bytes of `unchanged` + `modified` = the traffic that needs to be downloaded from the cloud this time. 100GB of content shared on both sides means 100GB of network round trips.
- Under `--quick` / `detection=quick`, the remote contents of files present on both sides are not downloaded, and execution time is closer to `O(文件数量)` rather than `O(总文件大小)`.
- Files present on only one side are not downloaded.
- In default mode, hash computation is streamed in memory (io.Copy → sha256.New), and cloud files are not written to disk.

<a id="所需-scope"></a>
## Required scopes

| Operation | scope |
|------|-------|
| List folders / subdirectories | `drive:drive.metadata:readonly` |
| Download and hash files | `drive:file:download` |

By default, `drive:drive.metadata:readonly` is required first. Under the `detection=exact` path (default, without passing `--quick`), the CLI additionally requires `drive:file:download`; when `--quick` is passed, the download scope is not required. If the current token lacks the scope required for this execution path, the command reports `missing_scope` and prompts to log in again. `drive:drive` is disabled by policy in some enterprises, so +status deliberately depends only on the fine-grained scopes above.

<a id="参考"></a>
## References

- [lark-drive](../index.md) — all commands for Drive (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) — authentication and global parameters
- [lark-drive-upload](lark-drive-upload.md) / [lark-drive-download](lark-drive-download.md) — connect +status output to push/pull actions
