# wiki +move-to-drive


Move an existing Wiki node out of the knowledge base and into a specified Drive folder; when the target folder is omitted, it is placed in the "My Space" root directory of the current calling identity. This operation always creates an asynchronous task, and the shortcut automatically performs a limited number of polling attempts.

<a id="何时使用"></a>
## When to use

| Source object | Target location | Command |
|--------|----------|------|
| Wiki node | Wiki space or Wiki parent node | `wiki +move` |
| Drive document | Wiki space or Wiki parent node | `wiki +move` |
| Wiki node | Drive folder or "My Space" root directory | `wiki +move-to-drive` |
| Drive file / folder | Drive folder or root directory | `drive +move` |

`--node-token` must be a Wiki node token, not the `obj_token` of the underlying document. When unable to determine, first run `wiki +node-get --node-token <URL_OR_TOKEN>`.

<a id="命令"></a>
## Command

```bash
# Move to a specified Drive folder
lark-cli wiki +move-to-drive \
  --node-token <WIKI_NODE_TOKEN> \
  --folder-token <TARGET_FOLDER_TOKEN> \
  --as user

# Move to the "My Space" root directory of the current calling identity
lark-cli wiki +move-to-drive \
  --node-token <WIKI_NODE_TOKEN> \
  --as user

# Preview the two-step requests of submitting the task and polling the task
lark-cli wiki +move-to-drive \
  --node-token <WIKI_NODE_TOKEN> \
  --folder-token <TARGET_FOLDER_TOKEN> \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--node-token` | Yes | The Wiki node token to move out of the knowledge base |
| `--folder-token` | No | The target Drive folder token; when omitted, it is moved to the "My Space" root directory of the current calling identity |

<a id="异步协议与续跑"></a>
## Asynchronous protocol and resumption

The shortcut executes according to the following protocol:

1. `POST /open-apis/wiki/v2/nodes/{node_token}/move_wiki_to_docs`, obtaining a complete, indivisible `task_id`.
2. `GET /open-apis/wiki/v2/tasks/{task_id}?task_type=move_wiki_to_docs`.
3. Read `data.task.move_wiki_to_docs_result`: `status=1` indicates processing, `status=0` indicates success, `status=-1` indicates failure.

Task queries must use `task_type=move_wiki_to_docs`, `move_wiki_to_docs_result`, and numeric status; do not fall back to other task types, result fields, or string statuses.

- Poll at most 30 times, with an interval of 2 seconds each time.
- On success within the polling window, return `ready=true`, and return `obj_token`, `obj_type`, and `url` where possible.
- When still processing, return `ready=false`, `timed_out=true`, the complete `task_id`, and `next_command`; a timeout does not mean the task failed.
- When the task enters a failed state, return a structured error.
- `task_id` is a server-signed opaque ID and may contain multiple hyphens; it must be saved as-is and must not be split on your own.
- Resumption must maintain the same `--profile` and `--as user|bot` identity as the initial move, otherwise a permission error may be received; the `next_command` returned by the shortcut preserves both.

Manual resumption command:

```bash
lark-cli drive +task_result \
  --scenario wiki_move_to_drive \
  --task-id <COMPLETE_TASK_ID> \
  --as user
```

<a id="典型返回"></a>
## Typical responses

Success:

```json
{
  "node_token": "wikcnXXX",
  "folder_token": "fldcnXXX",
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

Polling window timeout:

```json
{
  "node_token": "wikcnXXX",
  "folder_token": "",
  "task_id": "<OPAQUE_TASK_ID>",
  "ready": false,
  "failed": false,
  "status": 1,
  "status_msg": "processing",
  "timed_out": true,
  "next_command": "lark-cli drive +task_result --scenario wiki_move_to_drive --task-id <OPAQUE_TASK_ID> --as user"
}
```

<a id="权限与影响"></a>
## Permissions and impact

- CLI write operation pre-checks use `space:document:move`, and task polling uses `wiki:space:read`.
- The caller must be able to move the source Wiki node and write to the target Drive folder.
- After success, the source node disappears from the Wiki tree, and the target document switches to the permission model of the target Drive location; the original Wiki hierarchy inherited permissions are no longer retained.
- When `--folder-token` is omitted, the "root directory" belongs to the current `--as` identity, and the visible resource scope of user and bot may differ.

> [!CAUTION]
> This is a **write operation** that changes document ownership and permission inheritance. Before execution, you must confirm the source Wiki node, the target Drive location, and the calling identity.

<a id="参考"></a>
## References

- [lark-wiki](../index.md) -- all knowledge base commands
- [wiki +move](lark-wiki-move.md) -- moving within Wiki and migrating Drive documents into Wiki
- [drive +task_result](../../drive/references/lark-drive-task-result.md) -- task resumption after timeout
- [lark-shared](../../shared/index.md) -- authentication and global parameters
