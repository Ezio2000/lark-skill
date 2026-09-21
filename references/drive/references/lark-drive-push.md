
# drive +push


Mirror a local directory **one-way, at file level** to a folder in Feishu Drive (cloud drive/cloud storage) (local → Drive). The command recursively lists the remote manifest under `--folder-token`, traverses all regular files under `--local-dir`, and creates, overwrites, or skips them on Drive by relative path; optionally (`--delete-remote --yes`) it deletes `type=file` that "do not exist locally" in the cloud.

> **"File-level mirror" ≠ "directory mirror".** The command only converges differences at the file dimension: if there are extra local files, they are uploaded; if local files are missing and `--delete-remote --yes` is enabled, remote files are deleted. **Empty directories that exist only remotely, and directories already deleted locally** will not be converged, and redundant structure in the cloud directory tree will not be cleaned up. If you need "directories to stay fully consistent too", you must first use `+status` yourself to find differences, then manually handle the extra directories.

Output is categorized by "action":

| Field | Meaning |
|------|------|
| `summary.uploaded` | Number of files successfully created or overwritten |
| `summary.skipped` | Number of files skipped because `--if-exists=skip` or `--if-exists=smart` hit "no transfer needed" |
| `summary.failed` | Number of entries that failed to upload / overwrite / create directory / delete; **as long as it is not 0, the command exits with a non-zero status** (the structured `items[]` is still on stdout) |
| `summary.deleted_remote` | Number of cloud files deleted when `--delete-remote --yes` is enabled |
| `summary.aborted` | `true` when a terminal error is hit and subsequent batch processing stops |
| `items[]` | Details for each entry (`rel_path` / `file_token` / `action` / `version` on overwrite / `size_bytes` / `error` on failure / `hint` / `phase` / `error_class` / `code` / `subtype` / `retryable`) |

`items[].action` values: `uploaded` / `overwritten` / `skipped` / `folder_created` / `deleted_remote` / `already_deleted` / `failed` / `delete_failed`.

> Local directories (including empty directories) are mirrored to Drive; newly created subdirectories appear in `items[]` as `action: "folder_created"`, but are **not counted** in `summary.uploaded` (that field only counts files). Existing remote directories reuse their token, will not be `create_folder` again, and will not appear in `items[]`.

<a id="远端同名文件冲突"></a>
## Remote same-name file conflicts

If multiple entries in Drive map to the same `rel_path`, the default is to fail directly (a typed error envelope on stderr: `error.type=validation`, `error.subtype=failed_precondition`, with `error.params[]` listing the conflicting `rel_path` and colliding entries one by one), and no upload, overwrite, or `--delete-remote` deletion phase is entered. Only the scenario of "multiple `type=file` with the same name" supports an explicit policy; heterogeneous conflicts such as `file-folder` always fail directly.

| Policy | Behavior |
|------|------|
| `fail` | Default. Returns complete information for all conflicting entries, writes nothing remotely |
| `newest` | Aligns the local file only with the `modified_time` latest remote file |
| `oldest` | Aligns the local file only with the `created_time` earliest remote file |

`+push` does not provide `rename`: a single local file cannot express overwriting multiple remote objects. If the user wants to keep multiple cloud copies, they should first explicitly organize the cloud files, then push again.

<a id="命令"></a>
## Command

```bash
# Basic usage — push local ./repo to cloud fldcXXX
# Default --if-exists=skip: existing remote files are left untouched; only additions, no overwrites.
lark-cli drive +push --local-dir ./repo --folder-token fldcnxxxxxxxxx

# For repeated syncs, smart can be used for incremental optimization: it skips remote files that are already aligned based on modified_time; but if the remote is older, it still continues down the overwrite path
lark-cli drive +push --local-dir ./repo --folder-token fldcnxxxxxxxxx \
  --if-exists smart

# Explicitly overwrite remote files with the same name (depends on the upload_all gradual rollout protocol field; see "Overwrite semantics" below)
lark-cli drive +push --local-dir ./repo --folder-token fldcnxxxxxxxxx \
  --if-exists overwrite

# When the cloud already has multiple binary files with the same name, explicitly choose one remote target before overwriting
lark-cli drive +push --local-dir ./repo --folder-token fldcnxxxxxxxxx \
  --if-exists overwrite --on-duplicate-remote newest

# File-level mirror sync: upload / overwrite + delete remote files that do not exist locally
# (--delete-remote must be paired with --yes, otherwise it will be rejected directly by Validate;
#   and the Validate stage dynamically checks the space:document:delete scope, so missing permission fails immediately,
#   avoiding a half-synced state where "the upload succeeded but the later deletion stage failed")
lark-cli drive +push --local-dir ./repo --folder-token fldcnxxxxxxxxx \
  --if-exists overwrite --delete-remote --yes
```

<a id="参数"></a>
## Parameters

| Flag | Required | Type | Description |
|------|------|------|------|
| `--local-dir` | Yes | path | Local root directory (**must be a relative path from cwd**; absolute paths or relative paths escaping cwd are rejected directly by the CLI) |
| `--folder-token` | Yes | string | Target Drive folder token |
| `--if-exists` | No | enum | Policy when the remote file already exists: `skip` (**default**, safe) / `smart` (for repeated incremental syncs; skips upload when the remote `modified_time` already matches or is newer, otherwise continues down the overwrite path) / `overwrite` (depends on the gradual rollout backend protocol; see "Overwrite semantics") |
| `--on-duplicate-remote` | No | enum | Policy when multiple cloud entries map to the same `rel_path`: `fail` (default); if the conflicts are all `type=file`, `newest` / `oldest` are also available |
| `--delete-remote` | No | bool | Delete cloud files that do not exist locally (file-level mirror; does **not** clean up remote-only directories); **must be paired with `--yes`**, and the Validate stage dynamically checks the `space:document:delete` scope |
| `--yes` | No | bool | Confirm `--delete-remote`; if not passed, this destructive operation is rejected at the Validate stage |

<a id="上传与目录复刻范围"></a>
## Upload and directory replication scope

- **Only Drive `type=file` are uploaded / overwritten / deleted**. Online documents (`docx` / `sheet` / `bitable` / `mindnote` / `slides`) and shortcuts (`shortcut`) will not be overwritten or deleted even if they appear under the same rel_path — they have no equivalent local binary.
- **The local directory structure is mirrored as a whole**: all subdirectories (including **empty directories**) are `create_folder` on Drive as needed; remote directories with the same name reuse their token and are not recreated. Empty directories are not counted in `summary.uploaded`, but leave a trace in `items[]` in the form of `folder_created`.
- Existing remote files are decided by `--if-exists` as `overwrite` / `smart` / `skip`. Among these, `smart` is an **incremental optimization mode**: as long as the remote `modified_time` is already equal to or later than the local mtime at the same time precision, the upload is skipped; when the timestamp is missing/invalid, it falls back to the safe path and continues uploading, and will not blindly skip. **But if the remote is older, `smart` continues down the same overwrite path as `overwrite`, and therefore inherits the same rollout / version return caveat.** If you want to do something like `keep-both`, you still need to rename it yourself and push again.
- Cloud same-name conflicts fail by default; only when "all conflicts are `type=file`" and `--on-duplicate-remote newest|oldest` is passed will one remote file be selected to continue. When `--delete-remote` is enabled, unselected duplicate siblings are also deleted, so ultimately only one selected file copy remains remotely; only when `--if-exists=overwrite` succeeds can that copy's content be guaranteed to align with the local file.

<a id="覆盖语义"></a>
## Overwrite semantics

`--if-exists=overwrite` goes through `POST /open-apis/drive/v1/files/upload_all`, and includes the existing file's `file_token` in the form, so the backend updates the content in place and returns a new version number. The `items[].version` field is backfilled with that version number.

`--if-exists=smart` is an incremental optimization added for the "repeatedly run sync" scenario: when the remote `modified_time` is already equal to or later than the local mtime at the same time precision, the command counts that file as `skipped`; when the timestamp is missing, invalid, or older, it continues down the normal upload/overwrite path. **That is, as long as smart determines that "the remote is not new enough", it enters the same overwrite implementation as `--if-exists=overwrite`, so it may still fail non-zero on tenants where the version field has not been rolled out.**

> **Why the default is `skip` rather than `overwrite`:** `upload_all` accepting the `file_token` field and returning `version` in the response is the protocol specified by the design document (Drive sync folder); this backend is still in gradual rollout. On tenants where this field has not yet been enabled, `--if-exists=overwrite` will mark the corresponding file as `failed` due to "no version returned", and the entire `+push` will also exit non-zero because of this. So the default is deliberately set to `skip`: the first push into a directory that already has content will not fail the entire run just because the protocol is not in place; to actually overwrite remotely, you must explicitly pass `--if-exists overwrite`. New uploads do not depend on this field and are unaffected.

Large files (>20MB) automatically switch to the three-stage `upload_prepare` / `upload_part` / `upload_finish`; on this path `version` is not currently returned in the response, and `items[].version` will be left empty in the overwrite result, but `file_token` and `action: overwritten` are still produced correctly.

<a id="--delete-remote-的安全行为"></a>
## Safe behavior of --delete-remote

`--delete-remote` is the **only destructive flag** in the command, and it cleans up cloud copies one by one via `DELETE /open-apis/drive/v1/files/<token>?type=file` for "present remotely but not locally". By design it is strongly bound to `--yes`:

- `--delete-remote` (without `--yes`) → Validate reports an error directly: `--delete-remote requires --yes`, and no list / upload / delete request is initiated.
- `--delete-remote --yes` → the Validate stage also **dynamically performs** a scope pre-check for `space:document:delete`: when this scope is missing, the entire run fails immediately and no upload request is sent, avoiding a half-synced state where "all uploads succeeded, but the deletion stage reports missing_scope".
- `--delete-remote --yes` (and the scope is authorized) → executes normally: first pushes local files up, then scans the remote `type=file` list again and deletes one by one those not in the local manifest. **When any upload / overwrite / directory creation fails, the entire `--delete-remote` stage is skipped** (with a notice on stderr), the command exits with a non-zero status, and the remote is not damaged.
- If during the deletion stage the server returns `1061007 file has been delete`, it means the target remote file no longer existed before this DELETE; this already satisfies the target state of `--delete-remote`, and the output records it as `action: "already_deleted"`, not counted in `summary.failed` nor in `summary.deleted_remote`.
- Remote same-name conflicts with the default `fail`, or conflicts mixed with folder / other non-`type=file` objects → fail before the upload stage, and the deletion stage does not run.
- If `--delete-remote` is not passed → `summary.deleted_remote` is always 0; the command ignores remote "extra" files.
- Online documents (docx / sheet / bitable / ...) and shortcuts will **not** enter the deletion candidates even if there is no local file with the same name at all, because they never enter the alignment domain of `summary.uploaded`.
- **Empty directories that exist only remotely, and directories already deleted locally** will also not be cleaned up — this is the semantic boundary of a "file-level mirror"; the command does not actively converge the directory structure.

Chapter 6 marks `+push --delete-remote` as `high-risk-write`; the CLI implementation here is equivalent to "reject execution when `--yes` is not passed + dynamic scope pre-check", which conforms to the spirit of that constraint.

<a id="输出-schema"></a>
## Output schema

```json
{
  "summary": {
    "uploaded": 0,
    "skipped": 0,
    "failed": 0,
    "deleted_remote": 0,
    "aborted": false
  },
  "items": [
    {"rel_path": "...", "file_token": "...", "action": "folder_created"},
    {"rel_path": "...", "file_token": "...", "action": "uploaded",       "size_bytes": 0},
    {"rel_path": "...", "file_token": "...", "action": "overwritten",    "version": "...", "size_bytes": 0},
    {"rel_path": "...", "file_token": "...", "action": "skipped",        "size_bytes": 0},
    {"rel_path": "...",                       "action": "failed",        "size_bytes": 0, "error": "...", "hint": "...", "phase": "upload", "error_class": "...", "code": 0, "subtype": "...", "retryable": false},
    {"rel_path": "...", "file_token": "...", "action": "deleted_remote"},
    {"rel_path": "...", "file_token": "...", "action": "already_deleted"},
    {"rel_path": "...", "file_token": "...", "action": "delete_failed",  "error": "...", "hint": "...", "phase": "delete", "error_class": "...", "code": 0, "subtype": "...", "retryable": false}
  ]
}
```

`rel_path` always uses `/` as the separator (consistent across platforms).

<a id="失败处理与-agent-行为"></a>
## Failure handling and agent behavior

Failed items of `+push` carry structured fields; the agent must prioritize reading `items[].error_class` / `phase` / `code`, and must not only look at the natural-language `error` text. `summary.aborted=true` means the command has already hit a terminal error and stopped subsequent batch processing; at this point **do not retry as-is**; fix the root cause first.

`retryable=true` only means that after fixing the root cause or waiting, it can be attempted again; it does not mean the entire push should be replayed immediately and indefinitely; when retrying, use bounded exponential backoff with jitter.

Common terminal errors:

| `error_class` | Common `code` | Meaning | Agent response |
|---|---:|---|---|
| `app_scope_missing` | `99991672` | The app identity lacks Drive / folder-related scopes | Stop retrying; guide the user to enable the app identity permissions listed in the error, such as `space:folder:create` or `drive:drive` |
| `user_scope_missing` | `99991679` | The user identity lacks authorization | Stop retrying; use `lark-cli auth login --scope ...` to add the scopes listed in the error |
| `permission_denied` | `1061004` / HTTP 403 | The current identity is not authorized to operate on the target resource | Stop retrying; check the target folder permissions, identity type (user / bot), and resource visibility |
| `invalid_api_parameters` | `1061002` | API parameters were rejected by the server | Stop retrying; check `--folder-token`, overwrite mode, `file_token`, file names, and upload parameters; do not batch-retry the same parameter combination |
| `parent_node_missing` | `1061044` | The parent folder used for upload / directory creation does not exist or is not visible to the current identity | Stop retrying; check whether `--folder-token` still exists, whether there is permission, and whether the parent directory was deleted during the push; do not continue uploading the same directory tree |
| `parent_sibling_limit` | `1062507` | The number of single-level child nodes in the target parent folder exceeds the limit | Stop retrying; clean up the target directory, switch to another `--folder-token`, or split the uploaded content into multiple subdirectories |
| `quota_exceeded` | `1061101` / `1061061` | The Drive capacity quota for the tenant or current user is full | Stop retrying; free up capacity, adjust the target location, or expand capacity before running push again |
| `rate_limited` | `99991400` | Rate limiting triggered | Stop the current batch and retry after backoff |
| `conflict` | `1061045` | Resource contention occurred on the same target | Stop the current batch, avoid concurrent operations on the same target; retry a limited number of times after backoff |
| `server_error` | `1663` / `1061001` / `2200` / HTTP 5xx | Drive server or gateway exception | Stop the current batch and retry a limited number of times later |

Non-terminal but needs-explanation statuses:

- `file_size_limit` / `1061043`: The file exceeds the Drive upload limit. Do not keep trying the same file; split it or switch storage method.
- `upload_size_mismatch` / `1062009`: The local file changed during upload, or the declared size does not match the actual read size. Rescan local files before pushing again.
- `remote_not_found` / `1061007`: Generally means the remote file no longer exists. `1061007` in the deletion stage is treated as a `already_deleted` success item; other stages need to re-list to confirm remote status.

<a id="性能注意"></a>
## Performance notes

- Under the default `skip`, existing remote files are never touched; under `overwrite`, repeated runs re-upload all matching same-name files; under `smart`, already-aligned remote files are skipped based on `modified_time`, but files where "the remote is older" still enter the overwrite path, so what it reduces is **unnecessary re-uploads**, not a complete removal of overwrite risk.
- To control transfer volume more precisely, you can first use `+status` to find `new_local` and `modified`, then upload / overwrite only those files individually; or directly use `--if-exists smart` when syncing the whole directory.
- Large files use three-stage chunked upload (the entire body is not read into memory), but local disk and upstream bandwidth need to be sufficient.

<a id="所需-scope"></a>
## Required scopes

| Operation | scope | Pre-declared on the command |
|------|-------|-------------------|
| List folders / subdirectories | `drive:drive.metadata:readonly` | ✅ Pre-declared |
| Upload / overwrite files | `drive:file:upload` | ✅ Pre-declared |
| Create subdirectories (`create_folder`) | `space:folder:create` | ✅ Pre-declared |
| Delete files (only `--delete-remote --yes`) | `space:document:delete` | ⚙️ Not in the command's default Scopes, but dynamically pre-checked by Validate when `--delete-remote --yes` |

`drive:drive` is disabled by policy in some enterprises, so +push deliberately declares only the fine-grained scopes above.

> **About `space:document:delete`:** The framework's scope pre-check (`runner.go: checkShortcutScopes`) checks all scopes declared on the command before `Validate` and `--dry-run`; if the delete scope were also pre-declared, **ordinary uploads or dry-runs** would be blocked for lacking delete permission. So this item is not placed in the command's default Scopes, but is **conditionally triggered** in Validate: only when `--delete-remote --yes` are both enabled does it call `runtime.EnsureScopes([]string{"space:document:delete"})` to perform a dynamic pre-check. This preserves the convenience of "ordinary uploads do not need delete permission", while exposing missing scopes before actually performing mirror deletions, avoiding a half-synced state of "upload succeeded → deletion stage failed".
>
> To fill in permissions all at once: `lark-cli auth login --scope "drive:drive.metadata:readonly drive:file:upload space:folder:create space:document:delete"`.

<a id="范围限制"></a>
## Scope limits

`--local-dir` only accepts relative paths within cwd. The CLI first `EvalSymlinks` the entire path, then determines whether it still falls within cwd — **symbolic links pointing outside cwd are also rejected**; the shortcut of "placing a symlink inside cwd that points outside" does not work and will directly hit `unsafe file path`.

If the user wants to push a directory outside cwd, **do not have the agent `cd` to bypass it**. Options: have the user switch the agent working directory to the target's ancestor externally and restart the session; or physically move / copy the target as a whole into cwd (not a symlink); or simply give up this sync and use another method.

<a id="参考"></a>
## References

- [lark-drive](../index.md) —— all commands for Drive (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) —— authentication and global parameters
- [lark-drive-status](lark-drive-status.md) —— check differences before uploading (avoid full write-back)
- [lark-drive-pull](lark-drive-pull.md) —— the symmetric command for Drive → local
- [lark-drive-upload](lark-drive-upload.md) —— on-demand single-file upload
