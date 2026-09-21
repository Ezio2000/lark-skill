
# drive +task_result


Query asynchronous task results. This shortcut aggregates result queries for various asynchronous tasks, including import, export, Drive file/folder move/delete, Wiki node / document move into Wiki, Wiki node move out of Wiki, Wiki delete, and more, providing a unified interface for convenient invocation.

> [!IMPORTANT]
> For the `import` scenario, if `--as bot` is used and this query **has already obtained the final online document target** (`ready=true` and returned the final `token` / `url`), the CLI will **attempt once more to automatically grant the current CLI user `full_access` (manageable permission) for that resource**.
>
> In this case, the result will additionally return a `permission_grant` field that explicitly states the authorization result:
> - `status = granted`: the current CLI user has obtained manageable permission for the import result
> - `status = skipped`: there is no available current-user `open_id` locally, or the final result lacks an online document target that can be authorized, so no automatic authorization occurs; you may prompt the user to complete `lark-cli auth login` first, then have the AI / agent continue using the app identity (bot) to grant the current user permission
> - `status = failed`: the import result is ready, but automatically authorizing the user failed; the failure reason will be included, and you should prompt to retry later or continue handling the document using the bot identity
>
> `permission_grant.perm = full_access` indicates that the resource has been granted "manageable permission".
>
> **Do not perform owner transfer on your own initiative.** Creating or importing does not imply owner transfer; if the user has explicitly requested a transfer and the target is determined, proceed with the authorization execution.

<a id="命令"></a>
## Command

```bash
# Query import task result
lark-cli drive +task_result \
  --scenario import \
  --ticket <IMPORT_TICKET>

# Query export task result
lark-cli drive +task_result \
  --scenario export \
  --ticket <EXPORT_TICKET> \
  --file-token <SOURCE_DOC_TOKEN>

# Query Drive file/folder move/delete task status
lark-cli drive +task_result \
  --scenario task_check \
  --task-id <TASK_ID>

# Query Wiki move task result (continuation after wiki +move asynchronous timeout)
lark-cli drive +task_result \
  --scenario wiki_move \
  --task-id <TASK_ID>

# Query Wiki node move-out-of-wiki task result (continuation after wiki +move-to-drive asynchronous timeout)
lark-cli drive +task_result \
  --scenario wiki_move_to_drive \
  --task-id <TASK_ID>

# Query Wiki delete-space task result (continuation after wiki +delete-space asynchronous timeout)
lark-cli drive +task_result \
  --scenario wiki_delete_space \
  --task-id <TASK_ID>
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--scenario` | Yes | Task scenario, possible values: `import` (import task), `export` (export task), `task_check` (Drive file/folder move/delete task), `wiki_move` (Wiki move task), `wiki_move_to_drive` (Wiki node move-out-of-wiki task), `wiki_delete_space` (Wiki delete-space task), `wiki_delete_node` (Wiki delete-node task) |
| `--ticket` | Conditionally required | Asynchronous task ticket, **required for import/export scenarios** |
| `--task-id` | Conditionally required | Asynchronous task ID, **required for task_check and all wiki scenarios**; the complete ID must be passed through as-is |
| `--file-token` | Conditionally required | Source document token corresponding to the export task, **required for export scenarios** |

<a id="场景说明"></a>
## Scenario Description

| Scenario | Description | Required Parameters |
|------|------|----------|
| `import` | Document import task (e.g., importing a local file as a cloud document) | `--ticket` |
| `export` | Document export task (e.g., exporting a cloud document as PDF/Word) | `--ticket`, `--file-token` |
| `task_check` | Drive file/folder move/delete task | `--task-id` |
| `wiki_move` | Wiki move task (the docs-to-wiki asynchronous flow of `wiki +move`, used for continuation after timeout) | `--task-id` |
| `wiki_move_to_drive` | Wiki node move-out-of-wiki task (used for continuation after `wiki +move-to-drive` timeout) | `--task-id` |
| `wiki_delete_space` | Wiki delete-space task (the asynchronous flow of `wiki +delete-space`, used for continuation after timeout) | `--task-id` |
| `wiki_delete_node` | Wiki delete-node task (the asynchronous flow of `wiki +node-delete`, used for continuation after timeout) | `--task-id` |

<a id="返回结果"></a>
## Return Results

<a id="import-场景返回"></a>
### Import Scenario Return

```json
{
  "scenario": "import",
  "ticket": "<IMPORT_TICKET>",
  "type": "sheet",
  "ready": true,
  "failed": false,
  "job_status": 0,
  "job_status_label": "success",
  "job_error_msg": "success",
  "token": "<IMPORTED_DOC_TOKEN>",
  "url": "https://example.feishu.cn/sheets/<IMPORTED_DOC_TOKEN>",
  "extra": ["2000"],
  "permission_grant": {
    "status": "granted",
    "perm": "full_access",
    "member_type": "openid",
    "user_open_id": "<CURRENT_USER_OPEN_ID>",
    "message": "Granted the current CLI user full_access (可管理权限) on the new spreadsheet."
  }
}
```

**Field descriptions:**
- `ready`: whether the import has completed, and `token` / `url` can be used directly
- `failed`: whether it has failed
- `job_status`: the raw status code returned by the server
- `job_status_label`: a human-readable status label, for example `success` / `processing`
- `token`: the document token after import
- `url`: the document link after import
- `permission_grant`: returned only for `--as bot` and when this query has already obtained the final online document target, used to indicate whether manageable permission has been automatically granted to the current CLI user; if it is still `ready=false`, this field will not be returned

<a id="export-场景返回"></a>
### Export Scenario Return

```json
{
  "scenario": "export",
  "ticket": "<EXPORT_TICKET>",
  "ready": true,
  "failed": false,
  "file_extension": "pdf",
  "type": "doc",
  "file_name": "docName",
  "file_token": "<EXPORTED_FILE_TOKEN>",
  "file_size": 34356,
  "job_error_msg": "success",
  "job_status": 0,
  "job_status_label": "success"
}
```

**Field descriptions:**
- `ready`: whether the export has completed, and `file_token` can be used directly
- `failed`: whether it has failed
- `job_status`: the raw status code returned by the server
- `job_status_label`: a human-readable status label, for example `success` / `processing`
- `file_token`: the token of the exported file, used for download
- `file_extension`: the exported file extension
- `file_size`: the exported file size (bytes)

<a id="task_check-场景返回"></a>
### Task_check Scenario Return

```json
{
  "scenario": "task_check",
  "task_id": "<TASK_ID>",
  "status": "success",
  "ready": true,
  "failed": false
}
```

**Field descriptions:**
- `status`: task status, `success`=success, `failed`=failed, `pending`=processing
- `ready`: whether it has completed
- `failed`: whether it has failed

<a id="wiki_move-场景返回"></a>
### Wiki_move Scenario Return

```json
{
  "scenario": "wiki_move",
  "task_id": "<TASK_ID>",
  "ready": true,
  "failed": false,
  "status": 0,
  "status_msg": "success",
  "wiki_token": "wikcnXXX",
  "node_token": "wikcnXXX",
  "space_id": "<TARGET_SPACE_ID>",
  "obj_token": "<OBJ_TOKEN>",
  "obj_type": "docx",
  "parent_node_token": "",
  "node_type": "origin",
  "origin_node_token": "",
  "title": "项目计划",
  "has_child": false,
  "node": {
    "space_id": "<TARGET_SPACE_ID>",
    "node_token": "wikcnXXX",
    "obj_token": "<OBJ_TOKEN>",
    "obj_type": "docx",
    "parent_node_token": "",
    "node_type": "origin",
    "origin_node_token": "",
    "title": "项目计划",
    "has_child": false
  },
  "move_results": [
    {
      "status": 0,
      "status_msg": "success",
      "node": { "...": "同上" }
    }
  ]
}
```

**Field descriptions:**
- `ready`: `true` when all `move_results[].status` are `0`
- `failed`: `true` when any `move_results[].status` is less than `0`
- `status` / `status_msg`: the status code / label of the first move_result (falls back to `1` / `processing` when there is no result)
- `wiki_token` / `node_token`: the target node token after moving into Wiki (mirrored to the top level when the first result has `node.node_token`, for ease of use by downstream scripts)
- `space_id`, `obj_token`, `obj_type`, `title`, etc.: flattened from the first `move_results[0].node` to the top level, for convenient direct reference
- `move_results`: retains the complete list (suitable for scenarios where one task moves multiple documents)

<a id="wiki_move_to_drive-场景返回"></a>
### Wiki_move_to_drive Scenario Return

```json
{
  "scenario": "wiki_move_to_drive",
  "task_id": "<OPAQUE_TASK_ID>",
  "ready": true,
  "failed": false,
  "status": 0,
  "status_msg": "success",
  "obj_token": "doxcnXXX",
  "obj_type": "docx",
  "url": "https://example.feishu.cn/docx/doxcnXXX"
}
```

**Field descriptions:**
- `ready`: `true` when `move_wiki_to_docs_result.status=0`
- `failed`: `true` when `status<0`; `status=1` indicates it is still processing
- `status` / `status_msg`: the numeric status and readable message returned by the protocol; do not parse the string status as a success value
- `obj_token` / `obj_type` / `url`: resource information of the new Drive document after success
- `task_id`: a signed opaque ID that may contain multiple hyphens; falls back to the complete ID from the request when the server response omits `task.task_id`

<a id="wiki_delete_space-场景返回"></a>
### Wiki_delete_space Scenario Return

```json
{
  "scenario": "wiki_delete_space",
  "task_id": "<TASK_ID>",
  "ready": true,
  "failed": false,
  "status": "success",
  "status_msg": "success"
}
```

**Field descriptions:**
- `ready`: `true` when `status=success`
- `failed`: `true` when `status=failure` or `failed`; unknown non-success statuses (such as `processing`) are treated as in progress
- `status`: the raw `delete_space_result.status` returned by the server
- `status_msg`: prefer `delete_space_result.status_msg`, otherwise fall back to `status`, then fall back to `processing`

<a id="使用场景"></a>
## Usage Scenarios

<a id="配合-import-使用"></a>
### Used with +import

```bash
# 1. Create an import task
lark-cli drive +import --file ./data.xlsx --type sheet
# If the task completes quickly: return token / url directly
# If the built-in polling times out: return ready=false, ticket, and next_command

# 2. Poll the import result
lark-cli drive +task_result --scenario import --ticket <IMPORT_TICKET>
# If ready=true is returned here and --as bot is used, the result will also include permission_grant
```

<a id="配合-move-使用"></a>
### Used with +move

```bash
# 1. Move a folder (asynchronous operation)
lark-cli drive +move --file-token <FOLDER_TOKEN> --type folder --folder-token <TARGET_FOLDER_TOKEN>
# If it completes within the polling window: return ready=true directly
# If the built-in polling ends and it is still not complete: return ready=false, task_id, and next_command

# 2. Poll the move result
lark-cli drive +task_result --scenario task_check --task-id <TASK_ID>
```

<a id="配合-wiki-move-使用"></a>
### Used with wiki +move

```bash
# 1. Move a Drive document into Wiki (the asynchronous task may return task_id)
lark-cli wiki +move --obj-type docx --obj-token <DOC_TOKEN> --target-space-id <TARGET_SPACE_ID>
# If it completes within the built-in polling window: return ready=true and wiki_token directly
# If the polling window ends and it is still not complete: return ready=false, task_id, timed_out=true, and next_command

# 2. Continue querying the Wiki move result (next_command is the following command)
lark-cli drive +task_result --scenario wiki_move --task-id <TASK_ID> --as user
```

> **Keep the identity consistent**: the `--as` of the continuation command must match the original `wiki +move` call; the `next_command` of `wiki +move` already automatically carries the correct `--as`.

<a id="配合-wiki-move-to-drive-使用"></a>
### Used with wiki +move-to-drive

```bash
# 1. Move a Wiki node to a Drive folder; omitting --folder-token means the "My Space" root directory of the current identity
lark-cli wiki +move-to-drive \
  --node-token <WIKI_NODE_TOKEN> \
  --folder-token <TARGET_FOLDER_TOKEN> \
  --as user
# If it completes within the polling window: return ready=true, obj_token, obj_type, and url directly
# If the polling window ends and it is still not complete: return ready=false, the complete task_id, timed_out=true, and next_command

# 2. Continue using the complete task_id and the same identity
lark-cli drive +task_result \
  --scenario wiki_move_to_drive \
  --task-id <COMPLETE_TASK_ID> \
  --as user
```

> **Both the invocation context and the ID must be kept as-is**: the `--profile` and `--as` of the continuation must match the initial move; `task_id` may contain multiple hyphens, so do not split or truncate it. The `next_command` returned by `wiki +move-to-drive` will preserve the profile and identity.

<a id="配合-wiki-delete-space-使用"></a>
### Used with wiki +delete-space

```bash
# 1. Delete a wiki space (a high-risk write operation, must explicitly include --yes; the API may return an empty task_id synchronously, or may return an asynchronous task_id)
lark-cli wiki +delete-space --space-id <SPACE_ID> --yes
# If returned synchronously: ready=true directly
# If the polling window ends and it is still not complete: return ready=false, task_id, timed_out=true, and next_command

# 2. Continue querying the Wiki delete result (next_command is the following command)
lark-cli drive +task_result --scenario wiki_delete_space --task-id <TASK_ID> --as user
```

<a id="配合-export-使用"></a>
### Used with +export

```bash
# 1. Initiate the export
lark-cli drive +export --token <SOURCE_DOC_TOKEN> --doc-type docx --file-extension pdf
# If it completes within the polling window: download the local file directly
# If the built-in polling ends and it is still not complete: return ready=false, ticket, and next_command

# 2. Continue querying the export result
lark-cli drive +task_result --scenario export --ticket <EXPORT_TICKET> --file-token <SOURCE_DOC_TOKEN>

# If rate_limit / 99991400 is returned: wait at least 1 minute before retrying the same +task_result;
# If still rate-limited, continue exponential backoff starting from 1 minute.

# 3. Download after obtaining file_token
lark-cli drive +export-download --file-token <EXPORTED_FILE_TOKEN>
```

<a id="权限要求"></a>
## Permission Requirements

| Scenario | Required scope |
|------|-----------|
| import | `drive:drive.metadata:readonly` |
| export | `drive:drive.metadata:readonly` |
| task_check | `drive:drive.metadata:readonly` |
| wiki_move | `wiki:space:read` |
| wiki_move_to_drive | `wiki:space:read` |
| wiki_delete_space | `wiki:space:read` |
| wiki_delete_node | `wiki:space:read` |

> [!NOTE]
> In the `import` scenario, when `--as bot` and the task is finally ready, an additional collaborator authorization attempt may be made; if `permission_grant.status = failed`, check based on the failure information whether the app has the corresponding document collaborator authorization capability.

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for cloud space (Drive/cloud storage)
- [wiki +move-to-drive](../../wiki/references/lark-wiki-move-to-drive.md) -- move a Wiki node out of the wiki and into Drive
- [lark-shared](../../shared/index.md) -- authentication and global parameters
