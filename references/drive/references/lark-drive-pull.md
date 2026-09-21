
# drive +pull


One-way, file-level mirroring of a folder in Feishu Drive (cloud drive/cloud storage) to a local directory (Drive → local). The command recursively lists all `type=file` files under `--folder-token`, downloads them one by one to the relative path corresponding to `--local-dir`, and automatically replicates subfolders as local directories.

> ⚠️ **Not a directory-level mirror**: `--delete-local` only deletes local "extra" regular files, not empty directories. If the entire subfolder is deleted in the cloud, the corresponding local subdirectory will be left empty (the files inside are cleared, but the directory itself is kept); if you want to sync the directory structure precisely, handle the empty shells yourself with `rmdir`.

Output is categorized by "action":

| Field | Meaning |
|------|------|
| `summary.downloaded` | Number of files successfully downloaded |
| `summary.skipped` | Number of files skipped because `--if-exists=skip` or `--if-exists=smart` matched "no download needed" |
| `summary.failed` | Number of files that failed to download or write to disk |
| `summary.deleted_local` | Number of local files deleted when `--delete-local --yes` is enabled |
| `items[]` | Details for each file (`rel_path` / `file_token` / `source_id` / `action` / `error` on failure) |

When `summary.failed > 0`, the command exits with a **non-zero status code** (`exit=1`): the same `summary + items` is written to **stdout** as a `ok:false` partial-failure envelope (fields in `data.summary` / `data.items`), and stderr no longer outputs a separate error envelope; scripts/agents can simply judge success or failure via the exit code, without needing to parse `summary.failed`.

<a id="远端同名文件冲突"></a>
## Remote files with the same name conflict

If multiple entries in Drive map to the same `rel_path`, the default is to fail directly (typed error envelope on stderr: `error.type=validation`, `error.subtype=failed_precondition`, with `error.params[]` listing each conflicting `rel_path` and the colliding entries), and no local files will be downloaded, overwritten, or deleted. Only the scenario of "multiple `type=file` with the same name" supports an explicit policy; heterogeneous conflicts such as `file-folder` always fail directly.

| Policy | Behavior |
|------|------|
| `fail` | Default. Returns complete information for all conflicting entries, without writing to disk |
| `rename` | Only applies to duplicate files. Downloads all duplicate files; the first keeps its original name, and subsequent files use a stable hash suffix to generate unique filenames; if the short-suffix target is already taken, it automatically upgrades to a stronger suffix |
| `newest` | Only downloads the remote file with the latest `modified_time` |
| `oldest` | Only downloads the remote file with the earliest `created_time` |

`rename` naming rules are stable and traceable: subsequent duplicates of `report.pdf` are written to disk as `report__lark_<hash>.pdf`, for example `report__lark_3a2f4c5d6e7f.pdf`. If this short hash target name is already taken by another remote object in the same directory, the CLI automatically switches to a longer stable hash, and appends a numeric suffix if necessary, until the target name is unique. In this mode, `items[]` no longer returns a Drive `file_token` that can be reused directly; the CLI returns a stable hash identifier in `source_id`, for use in logs, comparisons, and manual troubleshooting.

<a id="命令"></a>
## Command

```bash
# Basic usage — mirror the cloud fldcXXX to ./repo
lark-cli drive +pull --local-dir ./repo --folder-token fldcnxxxxxxxxx

# Recommended usage for repeated sync: smart will skip local files that are already aligned based on modified_time
lark-cli drive +pull --local-dir ./repo --folder-token fldcnxxxxxxxxx \
  --if-exists smart

# Existing local files are left untouched
lark-cli drive +pull --local-dir ./repo --folder-token fldcnxxxxxxxxx \
  --if-exists skip

# When there are multiple binary files with the same name in the cloud, explicitly download all of them and rename with stable hash suffixes
lark-cli drive +pull --local-dir ./repo --folder-token fldcnxxxxxxxxx \
  --on-duplicate-remote rename

# File-level mirror: download new files + delete local files that are not in the cloud (does not delete empty directories)
# (--delete-local must be paired with --yes, otherwise it will be rejected directly by Validate)
lark-cli drive +pull --local-dir ./repo --folder-token fldcnxxxxxxxxx \
  --delete-local --yes
```

<a id="参数"></a>
## Parameters

| Flag | Required | Type | Description |
|------|------|------|------|
| `--local-dir` | Yes | path | Local root directory (**must be a relative path to cwd**; absolute paths or relative paths that escape cwd will be rejected directly by the CLI) |
| `--folder-token` | Yes | string | Source Drive folder token |
| `--if-exists` | No | enum | Policy when the local file already exists: `overwrite` (**default**, used when Drive is the authoritative source) / `smart` (**recommended for repeated incremental sync**; skips download when the local mtime already matches or is newer than the remote `modified_time`) / `skip` |
| `--on-duplicate-remote` | No | enum | Policy when multiple cloud entries map to the same `rel_path`: `fail` (default); if the conflicts are all `type=file`, you can also choose `rename` / `newest` / `oldest` |
| `--delete-local` | No | bool | Delete local "regular files that are not in the cloud" (**does not delete empty directories**, so it is a file-level mirror); **must be paired with `--yes`** |
| `--yes` | No | bool | Confirm `--delete-local`; if not passed, this destructive operation is rejected during the Validate stage |

<a id="比较与下载范围"></a>
## Comparison and download scope

- **Only downloads Drive `type=file` binary files**. Online documents (`docx` / `sheet` / `bitable` / `mindnote` / `slides`) and shortcuts (`shortcut`) are skipped — they have no equivalent local binary that can be written to disk, otherwise they would become noisy "fake" downloads.
- Subfolders are traversed recursively; rel_path looks like `sub1/sub2/file.txt`, and missing local parent directories are created automatically.
- Existing local files are handled according to `--if-exists` as `overwrite` / `smart` / `skip`. Among these, **`smart` is the recommended repeated sync mode**: as long as the local mtime is already equal to or later than the remote `modified_time` at the remote's time precision, the download is skipped; when the timestamp is missing/invalid, it falls back to the safe path and continues downloading, rather than blindly skipping. If you want something like `keep-both`, you still need to rename it yourself and then pull.
- Cloud conflicts with the same name fail by default; it only continues when "all conflicts are `type=file`" and `--on-duplicate-remote rename|newest|oldest` is passed.

<a id="--delete-local-的安全行为"></a>
## Safe behavior of --delete-local

`--delete-local` is the **only destructive flag** in the command, and it cleans up local regular files based on "present locally but not in the cloud". By design it is tightly bound to `--yes`, and is linked to failures during the download stage:

- `--delete-local` (without `--yes`) → Validate reports an error directly: `--delete-local requires --yes`, and no download, list request, or deletion occurs.
- `--delete-local --yes`, **and the download stage fully succeeds** → scan all regular files under `--local-dir`, and `os.Remove` each one that is not in the cloud manifest. **Only regular files are deleted, not directories**: after a remote folder is deleted, the corresponding local directory is left as an empty shell.
- `--delete-local --yes`, **but any entry fails during the download stage** → **skip the entire deletion stage**, and the command exits non-zero with a `ok:false` partial-failure result. Design intent: avoid a half-synced state where "downloads fail earlier and local files continue to be deleted afterward"; the operator can rerun after fixing the download errors.
- Remote files with the same name conflict and the default `fail` is used → it fails before the download stage, and the deletion stage does not run.
- `--delete-local` is not passed → `summary.deleted_local` is always 0; the command ignores local "extra" files.

In Chapter 6, `+pull --delete-local` is marked `high-risk-write`; the CLI implementation here is equivalent to "refuse to execute when `--yes` is not passed", which conforms to the spirit of that constraint.

<a id="输出-schema"></a>
## Output schema

```json
{
  "summary": {
    "downloaded": 0,
    "skipped": 0,
    "failed": 0,
    "deleted_local": 0
  },
  "items": [
    {"rel_path": "...", "file_token": "...", "action": "downloaded"},
    {"rel_path": "...", "source_id": "hash_3a2f4c5d6e7f", "action": "downloaded"},
    {"rel_path": "...", "source_id": "hash_3a2f4c5d6e7f", "action": "failed", "error": "..."},
    {"rel_path": "...", "action": "deleted_local"},
    {"rel_path": "...", "action": "delete_failed", "error": "..."}
  ]
}
```

`rel_path` always uses `/` as the separator (consistent across platforms). Deletion entries (`deleted_local` / `delete_failed`) have no `file_token`. In `rename` mode, duplicate file entries return `source_id` instead of the real `file_token` that can be used to call the API; other modes still return the real `file_token`.

<a id="性能注意"></a>
## Performance notes

- Under the default `overwrite`, repeated runs will re-download all matching files with the same name; under `skip`, existing files are not touched at all; **only under `smart` will it skip local files that are already aligned based on `modified_time`**, which is suitable for repeated incremental sync.
- To control the download volume more precisely, you can first use `+status` to find `new_remote` and `modified`, then `+download` only those files individually; or directly use `--if-exists smart` when syncing the entire directory.
- Large files use the SDK's streaming download (it does not read the entire body into memory), but local disk space must be sufficient.

<a id="所需-scope"></a>
## Required scopes

| Operation | scope |
|------|-------|
| List folders / subdirectories | `drive:drive.metadata:readonly` |
| Download files | `drive:file:download` |

If the current token lacks these scopes, the command reports `missing_scope` directly and prompts you to log in again. `drive:drive` is disabled by policy in some enterprises, so +pull deliberately declares only the two fine-grained scopes above.

<a id="范围限制"></a>
## Scope limits

`--local-dir` only accepts relative paths within cwd. The CLI first `EvalSymlinks` the entire path, then determines whether it still falls within cwd — **symbolic links pointing outside cwd are also rejected**; the shortcut of "placing a symlink inside cwd that points outside" does not work, and will directly hit `unsafe file path`.

If the user wants to pull to a directory outside cwd, **do not have the agent `cd` to bypass it**. Options: have the user switch the agent's working directory to an ancestor of the target externally and restart the session; or physically move/copy the target as a whole into cwd (not a symlink); or simply give up this sync and use another method.

<a id="参考"></a>
## References

- [lark-drive](../index.md) —— all commands for Drive (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) —— authentication and global parameters
- [lark-drive-status](lark-drive-status.md) —— check differences before downloading
- [lark-drive-download](lark-drive-download.md) —— pull a single file on demand
