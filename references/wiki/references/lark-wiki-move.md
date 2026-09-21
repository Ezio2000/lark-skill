# wiki +move


Move an existing Wiki node within Feishu Wiki, or migrate a Drive document into Wiki. This shortcut unifies two types of flows:

- `node` mode: move an existing Wiki node, either within the same space or across spaces
- `docs_to_wiki` mode: migrate a Drive document into a target knowledge space; when necessary, a move request can be submitted, and in asynchronous task scenarios it automatically polls a limited number of times

When `docs_to_wiki` returns `task_id`, the shortcut first polls for a short period; if it is still not complete within the polling window, it returns `next_command`, letting the caller continue by executing `lark-cli drive +task_result --scenario wiki_move --task-id <TASK_ID>`.

<a id="与-wiki-move-to-drive--drive-move-的区别"></a>
## Differences from `wiki +move-to-drive` / `drive +move`

- The target of `wiki +move` is a **knowledge space or Wiki parent node**, using `--target-space-id` / `--target-parent-token`
- `wiki +move-to-drive` moves an **existing Wiki node out of the knowledge base and into a Drive folder or the root directory of "My Space"**, using `--folder-token`
- The target of `drive +move` is a **Drive folder**, using `--folder-token`
- If the source object is already a Wiki node: use `wiki +move` when the target is still Wiki; use `wiki +move-to-drive` when the target is a Drive folder or root directory
- If the source object is still a Drive document, but the user wants to "migrate it into the knowledge base" or "attach it under a certain Wiki page", `wiki +move` should also be used
- If the user merely wants to organize cloud space (cloud drive/cloud storage) folders by moving files/folders to another Drive folder, `drive +move` should be used

<a id="口语目标识别"></a>
## Colloquial target recognition

- When the user says "move to a certain knowledge base", "attach under a certain page", or "migrate into Wiki", treat it as a **Wiki target** and prefer `wiki +move`
- When the user says "move to a certain folder" or "move to the root directory of cloud space (cloud drive/cloud storage)", treat it as a **Drive folder target**; use `wiki +move-to-drive` when the source object is a Wiki node, and use `drive +move` when the source object is already in Drive
- When the user says "move to my document library", "move to my knowledge base", or "put it in my personal knowledge base", it should first be understood as a **Wiki personal knowledge base target**, rather than directly degrading to `drive +move`
- When encountering expressions like "my document library", it can be understood as: first use `my_library` to query the user's personal knowledge base, then obtain the real `space_id`
- The recommended approach is to first execute `lark-cli wiki spaces get --params '{"space_id":"my_library"}'`, retrieve the real knowledge base `space_id`, and then use this `space_id` in `wiki +move`
- The main examples in the current `wiki +move` documentation still primarily use explicit `--target-space-id` / `--target-parent-token`; if the caller only has a natural language target, do not switch to `drive +move` just because the target is temporarily unclear

<a id="命令"></a>
## Command

```bash
# Move an existing wiki node under another parent node
lark-cli wiki +move \
  --node-token <NODE_TOKEN> \
  --target-parent-token <TARGET_PARENT_TOKEN>

# Move an existing wiki node to the root directory of another knowledge space
lark-cli wiki +move \
  --node-token <NODE_TOKEN> \
  --target-space-id <TARGET_SPACE_ID>

# Migrate a Drive document to the root directory of a certain knowledge space
lark-cli wiki +move \
  --obj-type docx \
  --obj-token <DOC_TOKEN> \
  --target-space-id <TARGET_SPACE_ID>

# Migrate a Drive document under a certain parent node; if there is currently no direct move permission, submit a request
lark-cli wiki +move \
  --obj-type sheet \
  --obj-token <SHEET_TOKEN> \
  --target-space-id <TARGET_SPACE_ID> \
  --target-parent-token <TARGET_PARENT_TOKEN> \
  --apply

# Preview the underlying call chain
lark-cli wiki +move \
  --obj-type docx \
  --obj-token <DOC_TOKEN> \
  --target-space-id <TARGET_SPACE_ID> \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--node-token` | Conditionally required | The token of the Wiki node to move or the document obj_token. Once passed, the command enters `node` mode |
| `--source-space-id` | No | Source knowledge space ID, only available in `node` mode; if not passed, it is automatically resolved based on `--node-token` |
| `--target-space-id` | Conditionally required | Target knowledge space ID. Required in `docs_to_wiki` mode; in `node` mode, if not passed, `--target-parent-token` must be passed |
| `--target-parent-token` | No | Target parent node token. When `docs_to_wiki` is not passed, it means migrating to the root directory of the target knowledge space |
| `--obj-type` | Conditionally required | Drive document type, only available in `docs_to_wiki` mode. Possible values: `doc`, `sheet`, `bitable`, `mindnote`, `docx`, `file`, `slides` |
| `--obj-token` | Conditionally required | Drive document token, only available in `docs_to_wiki` mode |
| `--apply` | No | Only available in `docs_to_wiki` mode; when the current caller cannot directly move the document, submit a move request |

<a id="模式选择与校验规则"></a>
## Mode selection and validation rules

- **`node` mode**: as long as `--node-token` is passed, it executes as "move an existing Wiki node"
- **`docs_to_wiki` mode**: when `--node-token` is not passed, it executes as "migrate a Drive document into Wiki"
- In `node` mode, `--node-token` cannot be used together with `--obj-type`, `--obj-token`, or `--apply`
- In `node` mode, `--target-parent-token` and `--target-space-id` cannot both be empty
- In `docs_to_wiki` mode, `--obj-type`, `--obj-token`, and `--target-space-id` must all be provided
- In `docs_to_wiki` mode, `--source-space-id` is invalid and can only be used in `node` mode

<a id="空间解析与一致性校验"></a>
## Space resolution and consistency validation

<a id="node-模式"></a>
### `node` mode

- **Source space resolution**: first call `GET /open-apis/wiki/v2/spaces/node_by_token` to resolve the source node; when `--source-space-id` is not passed, use the query result; when passed, validate that the two are consistent.
- **Target parent node resolution**: if `--target-parent-token` is passed, the shortcut first resolves the `space_id` to which that parent node belongs
- **Node type**: the source node and target parent node accept Wiki `node_token` or document `obj_token`; the actual move uses the `node_token` returned by the query.
- **Consistency validation**: if both `--target-space-id` and `--target-parent-token` are passed, the shortcut validates whether they belong to the same knowledge space; if inconsistent, it directly returns a validation error
- **Move to space root directory**: if only `--target-space-id` is passed, it means moving to the root directory of that knowledge space

<a id="docs_to_wiki-模式"></a>
### `docs_to_wiki` mode

- `--target-space-id` is always required
- `--target-parent-token` is optional; when not passed, it means moving to the root directory of the target knowledge space
- The request body is automatically mapped to `obj_type`, `obj_token`, `parent_wiki_token`, `apply`

<a id="行为说明"></a>
## Behavior description

- **`node` mode is a synchronous operation**: after the request succeeds, it directly returns the moved node information
- **`docs_to_wiki` may be synchronous or asynchronous**:
  - If the API directly returns `wiki_token`, the shortcut immediately returns `ready=true`
  - If the API returns `applied=true`, the shortcut returns `ready=false`, `failed=false`, `applied=true`, and `status_msg="move request submitted for approval"`
  - If the API returns `task_id`, the shortcut first enters limited polling
- **Limited polling window**: fixed at a maximum of `30` polls, with an interval of `2` seconds each time
- **Polling timeout is not failure**: if the task is still being processed when the polling window ends, it returns `task_id`, `status`, `status_msg`, `ready=false`, `timed_out=true`, and `next_command`
- **Continue querying**: after seeing `next_command`, switch to `lark-cli drive +task_result --scenario wiki_move --task-id <TASK_ID>` to continue querying
- **Task failure reports an error directly**: if the task enters a failed state during polling, the shortcut directly returns an error and no longer outputs `ready=false` results
- **When all polling requests fail, it also reports an error directly**: if the task has been created but every subsequent status query fails, the shortcut returns an error with a hint and provides a command to continue querying

<a id="返回结果"></a>
## Return results

<a id="node-模式典型返回"></a>
### Typical return in `node` mode

```json
{
  "mode": "node",
  "source_space_id": "space_src",
  "target_space_id": "space_dst",
  "space_id": "space_dst",
  "node_token": "wikcnode_xxx",
  "obj_token": "doccn_xxx",
  "obj_type": "docx",
  "parent_node_token": "wikcparent_xxx",
  "node_type": "origin",
  "origin_node_token": "",
  "title": "项目计划",
  "has_child": false
}
```

<a id="docs_to_wiki-异步超时返回"></a>
### Asynchronous timeout return in `docs_to_wiki` mode

```json
{
  "mode": "docs_to_wiki",
  "obj_type": "docx",
  "obj_token": "doccn_xxx",
  "target_space_id": "space_xxx",
  "target_parent_token": "wikcparent_xxx",
  "task_id": "7500000000000000001",
  "ready": false,
  "failed": false,
  "status": 1,
  "status_msg": "processing",
  "timed_out": true,
  "next_command": "lark-cli drive +task_result --scenario wiki_move --task-id 7500000000000000001"
}
```

**Output field descriptions:**

- `mode`: the current execution mode, with a value of `node` or `docs_to_wiki`
- `ready`: whether the task has already completed and the result can be used directly
- `failed`: whether the task has failed
- `task_id`: asynchronous task ID, returned only in asynchronous scenarios
- `status` / `status_msg`: the primary status code and readable status of the asynchronous task
- `wiki_token`: the Wiki node token returned after docs-to-wiki succeeds; it is also mirrored to `node_token`
- `space_id`, `node_token`, `obj_token`, `obj_type`, `parent_node_token`, `title`, etc.: returned when node information is successfully obtained, making it convenient for downstream calls to continue

<a id="dry-run-编排"></a>
## dry-run orchestration

- In `node` mode, dry-run displays a call chain of 1 to 3 steps depending on whether the source node / target parent node needs to be resolved
- In `docs_to_wiki` mode, dry-run displays two steps:
  1. `POST /open-apis/wiki/v2/spaces/{target_space_id}/nodes/move_docs_to_wiki`
  2. `GET /open-apis/wiki/v2/tasks/{task_id}?task_type=move`

<a id="权限说明"></a>
## Permission description

Before execution, the CLI performs a local scope pre-check; the permissions declared by the current shortcut are `wiki:node:move`, `wiki:node:read`, and `wiki:space:read` (covering the move write operation, node resolution read operation, and asynchronous task polling read operation respectively). If the local token has recorded scopes and any permission is missing, the command directly prompts to re-execute `lark-cli auth login --scope ...`.

After an asynchronous task times out, subsequent `lark-cli drive +task_result --scenario wiki_move --task-id <TASK_ID>` only requires the `wiki:space:read` permission.

> [!CAUTION]
> `wiki +move` is a **write operation**. Before execution, the user's intent must be confirmed, as well as whether the target node / target knowledge space is clear.

<a id="参考"></a>
## References

- [lark-wiki](../index.md) -- all knowledge base commands
- [lark-shared](../../shared/index.md) -- authentication and global parameters
- [wiki +move-to-drive](lark-wiki-move-to-drive.md) -- move a Wiki node out of the knowledge base and into Drive
- [drive +task_result](../../drive/references/lark-drive-task-result.md) -- the continuation query command for docs-to-wiki asynchronous tasks
