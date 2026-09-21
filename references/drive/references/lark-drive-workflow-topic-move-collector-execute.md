<a id="主题资料收集工作流执行"></a>
# Topic Material Collection Workflow: Execution

Loaded by states `CONFIRM_EXECUTION`, `EXECUTE`, `VERIFY`, `RESTORE`.

This document is responsible for final write operation confirmation, target creation, resource movement, verification, recovery behavior, `RollbackSnapshotItem`, and execution logs. It must not modify search, recall, classification rules, or the plan schema.

This document serves only `topic_move_collector`. When entering this document, `workflow_id` must be `topic_move_collector`; the current task must not be rerouted to another workflow.

<a id="必读上下文"></a>
## Required Context

Before executing the rules in this document:

1. Handle write operation confirmation, high-risk operations, identity, authentication, and permissions according to [`../../shared/index.md`](../../shared/index.md).
2. Create Drive folders according to [`lark-drive-create-folder.md`](lark-drive-create-folder.md).
3. Execute Drive moves according to [`lark-drive-move.md`](lark-drive-move.md).
4. Create Wiki nodes according to [`../../wiki/references/lark-wiki-node-create.md`](../../wiki/references/lark-wiki-node-create.md).
5. Execute Wiki moves and Drive document moves to Wiki according to [`../../wiki/references/lark-wiki-move.md`](../../wiki/references/lark-wiki-move.md).
6. Move Wiki nodes out to Drive folders according to [`../../wiki/references/lark-wiki-move-to-drive.md`](../../wiki/references/lark-wiki-move-to-drive.md).
7. Delete Drive folders newly created by this workflow according to [`lark-drive-delete.md`](lark-drive-delete.md).
8. Delete Wiki nodes newly created by this workflow according to [`../../wiki/references/lark-wiki-node-delete.md`](../../wiki/references/lark-wiki-node-delete.md).
9. When polling asynchronous tasks is needed, execute according to [`lark-drive-task-result.md`](lark-drive-task-result.md).
10. The `MovePlanItem` schema is defined by [`lark-drive-workflow-topic-move-collector-review-plan.md`](lark-drive-workflow-topic-move-collector-review-plan.md); this file only consumes the confirmed plan.

<a id="状态confirm_execution"></a>
## State: `CONFIRM_EXECUTION`

Entry condition: The move plan is ready and the user requests execution.

Must:

1. Display all write operation categories before execution.
2. Display target creation and resource movement separately.
3. Display the high-relevance resources included by default.
4. If there are medium-relevance resources selected by the user, display those as well.
5. Display skipped groups and reasons.
6. Clearly display cross-container moves.
7. Display the number of resources with no move permission and with unknown move permission.
8. Request explicit confirmation from the user.
9. Before confirmation, verify that each `move_resource` item contains complete `command_family`, `command_args`, permission snapshot, and `rollback_input`; if missing, must return to `PLAN_MOVE` to regenerate the plan, and must not guess during the execution phase.
10. Only plan items with `move_permission_state=movable` and `target_write_state=confirmed` may be listed under "will move".
11. For each `rollback_supported=false` plan item, display the title, current location, target location, non-recoverable reason, and impact item by item; do not display only the count.

<a id="确认-ui"></a>
### Confirmation UI

```text
Please confirm whether to execute the following write operations:

Search scope for this run: <resources owned / managed by the current user | all resources visible to the current identity>

Will create:
- Target name | Parent location | Target type

Will move:
- Title | Type | Current location | Target location | Reason

Will not move:
- Medium relevance not selected: N items
- Low relevance: N items
- No permission: N items
- No move permission: N items
- Move permission unknown: N items
- Cannot verify: N items
- Move not supported: N items

Risk notice:
- Cannot be automatically recovered: N items
- Title | Current location | Target location | Non-recoverable reason | Impact: After a successful move, the workflow cannot automatically move it back to the original location and requires manual handling
- If the search scope is all resources visible to the current identity, items with unknown move permission will not be moved.

Targets will be created and resources will be moved only after confirmation.

If there are no non-automatically-recoverable items, reply "confirm execution" to start write operations.
If there are non-automatically-recoverable items, reply "confirm execution, including non-automatically-recoverable items"; a plain "confirm execution" does not satisfy this risk confirmation.
You may also reply "adjust plan" to return to resource selection, or reply "cancel" to end the process.
```

If the user modifies selections or relevance grouping, discard the current `move_plan_items` and return to `PLAN_MOVE` to regenerate the plan; do not directly make partial edits to the plan in `CONFIRM_EXECUTION`.

<a id="状态execute"></a>
## State: `EXECUTE`

Entry condition: The user explicitly confirms the write operations; when there are `rollback_supported=false` plan items, the user has explicitly confirmed including non-automatically-recoverable items.

Must:

1. Execute only the confirmed `MovePlanItem.command_family` and `command_args`; do not re-query `ResourceItem` to fill in or rewrite command parameters.
2. When there is a `MovePlanItem` of `action_type=create_target`, create the target first.
3. After target creation, record the returned token; only resolve `created_by_plan:<create_target plan_id>` references to that token and write the resolved actual parameters into `execution_journal`. Do not re-search or guess the target.
4. After the target token reference is successfully resolved, move the resources that depend on that target; if resolution fails, stop the moves that depend on that created target and record a blocker, and do not substitute another target.
5. Before executing any write operation, generate `rollback_snapshot` based on the `rollback_input` of each confirmed plan item. A snapshot with `rollback_supported=false` and an already explicit `rollback_blocker` is considered a complete risk snapshot and does not block other items.
6. Before executing any write operation, initialize `execution_journal`.
7. Record `execution_journal` after each write operation attempt.
8. After a single item fails, mutually independent moves may continue; if target creation fails, must stop.
9. Must not move `permission_denied`, `no_move_permission`, `move_permission_unknown`, `unverifiable`, `low`, or `unsupported_move_target` items.
10. Must not move resources of `move_permission_state!=movable` or `target_write_state!=confirmed`.
11. If a move command returns a permission error, record the failure reason, do not automatically request permissions, and do not automatically retry the same move.
12. If `rollback_supported=true` but `rollback_input` lacks the fields required for recovery, mark that plan item as `failed` / `plan_snapshot_incomplete` and skip it; do not silently downgrade it to a non-recoverable item without re-confirming the risk, and do not block other independent items.

<a id="移动方式选择"></a>
### Move Method Selection

| Source -> Target | Move Method |
|------------------|-------------|
| Drive resource -> Drive folder | `drive +move` |
| Drive document-like resource -> Wiki target | docs-to-wiki mode of `wiki +move`; not automatically recoverable by default |
| Wiki node -> Wiki target | `wiki +move --node-token` |
| Wiki node -> Drive folder | `wiki +move-to-drive` |

<a id="执行顺序"></a>
### Execution Order

1. If there are `create_target` items, execute them first.
2. Execute `move_resource` items in the confirmed plan order.
3. If a command returns a task ID, perform asynchronous task polling.
4. Output the write operation execution summary.

<a id="进度-ui"></a>
### Progress UI

When the batch is large, report progress by count:

```text
Execution progress: completed <done_count>/<total_count>, succeeded <success_count>, failed <failed_count>.
Current operation: <title>
Continuing execution; no action needed from you. If a failure requiring confirmation is encountered, it will be prompted separately.
```

<a id="状态verify"></a>
## State: `VERIFY`

Entry condition: Execution is complete.

Must:

1. If a target was created, verify that the target exists.
2. When capabilities support it, verify that moved resources are visible at the target location.
3. Compare actual locations with `move_plan_items`.
4. Mark a verification status for each item.
5. Provide recovery options only when there has already been a successful move and there is a serious inconsistency or failure.
6. When outputting verification results, must state that the user can next end the process, view failed items, or choose recovery when recoverable.
7. If `async_pending` occurs, first use `drive +task_result` polling to confirm; only after exceeding the polling limit report a pending blocker.

<a id="验证结果"></a>
### Verification Results

| Status Value | Description |
|--------|------|
| `verified` | The resource is visible at the target location. |
| `not_found` | The resource was not found at the target location. |
| `permission_unknown` | The current identity cannot confirm the result. |
| `async_pending` | The asynchronous task has not yet completed and requires continued polling. |
| `failed` | The move command failed or the result does not match the plan. |

<a id="状态restore"></a>
## State: `RESTORE`

Entry condition: Failure, inconsistency, or the user explicitly requests recovery.

Must:

1. Generate the recovery plan based only on `rollback_snapshot` and `execution_journal`.
2. Display recoverable items and non-recoverable items.
3. Request explicit confirmation before executing recovery write operations; the confirmation content must include reverse moves and deletion of targets newly created by this workflow.
4. Recover only resources that were moved by this workflow.
5. Recover only move items with `rollback_supported=true` and `rollback_eligible=true`.
6. Items with `rollback_supported=false`, such as Drive / Wiki cross-container moves and missing original parent tokens, must not be reverse-moved, and documents after migration must not be deleted.
7. Target folders or Wiki nodes successfully created by this workflow must be included in the cleanup plan.
8. When deleting Wiki target nodes newly created by the workflow, must use `wiki +node-delete --include-children=false --yes`, so that direct child documents already migrated in are retained at that node's parent level.
9. Before deleting a Drive folder newly created by the workflow, must first recover or move out the resources placed in it by this workflow; if it cannot be confirmed that the folder is safe to delete, report a cleanup blocker, and must not use folder deletion to delete user resources.

<a id="恢复顺序"></a>
### Recovery Order

1. First recover move items with `rollback_supported=true` and `rollback_eligible=true`.
2. For all items with `rollback_supported=false`, only record "keep at the current target location, do not migrate back, do not delete" and the corresponding blocker.
3. Then clean up the target containers of `created_by_workflow=true`.
4. Wiki newly created target cleanup uses `--include-children=false`; Drive newly created target cleanup is performed only when it will not delete user resources.

<a id="恢复-ui"></a>
### Recovery UI

```text
You can attempt to recover the resources moved in this run:

Recoverable:
- Title | Current location | Original location

Not automatically recoverable:
- Title | Current location | Original location | Reason | Impact: Manual recovery is required

Targets newly created in this run that will be cleaned up:
- Name | Type | Cleanup method

Cross-container migrated documents that will be kept at the current target location:
- Title | Current location | Retention result

Execute recovery?
```

## RollbackSnapshotItem

```json
{
  "snapshot_id": "稳定快照行 ID",
  "plan_id": "对应 MovePlanItem.plan_id",
  "resource_id": "对应 MovePlanItem.resource_id",
  "source_kind": "drive|wiki",
  "title": "资源标题",
  "resource_type": "Drive 恢复命令需要的资源类型",
  "original_token": "原始 Drive token",
  "original_node_token": "原始 Wiki node token",
  "original_parent_kind": "drive_folder|drive_root|wiki_node|wiki_space_root|unknown",
  "original_parent_token": "原始父级 token",
  "original_space_id": "原始 Wiki space_id",
  "original_path": "执行前路径",
  "planned_target_parent_token": "计划目标父级 token",
  "rollback_supported": "是否支持自动恢复",
  "rollback_blocker": "不可自动恢复原因"
}
```

| Field | Description |
|-------|------|
| `snapshot_id` | Stable snapshot row ID. |
| `plan_id` | Corresponds to `MovePlanItem.plan_id`, used to connect the plan, snapshot, and execution log. |
| `resource_id` | Corresponds to the stable resource ID, used to audit the plan source. |
| `resource_type` | The `--type` that must be passed in when recovering `drive +move`; non-Drive recovery also retains the original resource type. |
| `original_token` / `original_node_token` | Source resource identity before execution. |
| `original_parent_kind` / `original_parent_token` | Parent location before execution. |
| `rollback_supported` | Whether automatic recovery is supported. |
| `rollback_blocker` | Reason automatic recovery is not possible. |

<a id="执行日志"></a>
## Execution Log

Each write operation attempt must append an internal log entry:

```json
{
  "journal_id": "稳定日志行 ID",
  "plan_id": "对应 MovePlanItem 的 plan_id",
  "time": "ISO-8601",
  "action_type": "create_target|move_resource|restore_resource|cleanup_target",
  "operation": "create_folder|create_node|move_drive|move_wiki_node|move_wiki_to_drive|restore_drive|restore_wiki_node|delete_folder|delete_wiki_node",
  "command_family": "drive +move|wiki +move|wiki +move-to-drive|drive +create-folder|wiki +node-create|drive +delete|wiki +node-delete",
  "resolved_command_args": {"<arg>": "实际发送的参数"},
  "title": "资源或目标名称",
  "resource_type": "资源类型",
  "input_token": "命令输入 token",
  "input_node_token": "命令输入 Wiki node token",
  "input_parent_token": "已知源父级 token",
  "target_parent_token": "目标父级 token",
  "returned_token": "命令返回 token",
  "returned_node_token": "命令返回 Wiki node token",
  "returned_parent_token": "返回父级 token",
  "task_id": "异步任务 ID",
  "next_command": "异步继续命令",
  "created_by_workflow": "是否由本次 workflow 创建",
  "rollback_eligible": "是否可进入自动恢复计划",
  "status": "success|failed|pending",
  "error": "失败原因"
}
```

Field descriptions:

| Field | Description |
|------|------|
| `journal_id` | Stable log row ID. |
| `plan_id` | Corresponds to `MovePlanItem`, used to match the log entry back to the original plan. |
| `operation` | Subdivided operation type, used to distinguish creation, movement, and recovery. |
| `resolved_command_args` | The actual parameters sent, parsed from the confirmed plan; used to audit the only runtime substitution of `created_by_plan:<plan_id>`. |
| `resource_type` | The resource type actually used for the move / recovery. |
| `input_token` / `input_node_token` | The resource token actually input to the command. |
| `input_parent_token` | The source parent token known before execution. |
| `target_parent_token` | The target parent token input to the command. |
| `returned_token` / `returned_node_token` | The resource token returned by the command, used as the current source during recovery. |
| `returned_parent_token` | The current parent token returned by the command. |
| `task_id` / `next_command` | Asynchronous task tracking information. |
| `created_by_workflow` | Whether it was created by this workflow, used for subsequent cleanup decisions. |
| `rollback_eligible` | Whether it can enter the automatic recovery plan. |
| `status` | Write operation status; when asynchronous and incomplete, it is `pending`. |

Unless the user requests to view technical debugging details, do not display the full raw command output.
