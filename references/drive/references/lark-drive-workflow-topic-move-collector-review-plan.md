<a id="主题资料收集工作流审核与计划"></a>
# Topic Material Collection Workflow: Review and Planning

Loaded by states `RELEVANCE_CLASSIFY`, `PLAN_MOVE`.

This document is responsible for relevance grading, review UI, move plan generation, and `MovePlanItem`. It must not re-execute resource resolution or content verification, nor create targets, move resources, or perform recovery operations.

This document serves only `topic_move_collector`. When entering this document, `workflow_id` must be `topic_move_collector`; the current task must not be re-routed to another workflow.

<a id="输入契约"></a>
## Input Contract

Before entering this document, the following must already exist:

1. `resource_items`, and each `ResourceItem` already contains a stable `resource_id`, resource type, token required for moving, structured current parent, permission status, content verification status, and evidence.
2. `content_verify_completed=true`.
3. Each resource has content evidence, a search evidence reuse note, or an explicit skip reason.

`ResourceItem` schema and field generation rules are the responsibility of [`lark-drive-workflow-topic-move-collector-resolve-verify.md`](lark-drive-workflow-topic-move-collector-resolve-verify.md). As long as the above input contract is complete, this state must not reload or execute the previous stage document for the purpose of re-reading the schema.

If input fields are missing, a resource needs re-resolution, or the user requests re-reading evidence, discard the affected relevance and plan results, return to `RESOURCE_RESOLVE` or `CONTENT_VERIFY`, and load the resource resolution and content verification document; do not guess in this state.

<a id="状态relevance_classify"></a>
## State: `RELEVANCE_CLASSIFY`

Entry conditions: `CONTENT_VERIFY` is complete, `content_verify_completed=true`, and each `ResourceItem` already has a verification status or a skip-verification reason.

Prohibited conditions:

1. Only `candidate_items`, without `resource_items`.
2. The resource has not undergone `RESOURCE_RESOLVE`.
3. The resource has no move eligibility status written by `RESOURCE_RESOLVE`.
4. The resource has no verification status or skip-verification reason written by `CONTENT_VERIFY`.
5. The last completed state is `RESOURCE_RESOLVE`, or `content_verify_completed` is not `true`.

Each resource must be assigned to exactly one group:

| Group | Description | Default move |
|-------|------|--------------|
| `high` | Movable resource, with a direct hit on the topic or content, supported by clear title / body / table / comment evidence. | Yes |
| `medium` | Movable resource, possibly relevant, but with insufficient evidence or only a weak-relevance fragment hit. | No, requires user selection |
| `low` | Movable resource, weakly relevant or noise, kept displayed but not recommended for moving. | No |
| `permission_denied` | The current identity is not authorized to read or resolve, and content cannot be verified. | No |
| `no_move_permission` | Confirmed that the current identity does not have move eligibility. | No |
| `move_permission_unknown` | Cannot confirm whether the current identity has move eligibility. | No |
| `unverifiable` | Content cannot be verified due to type or tool limitations. | No |
| `unsupported_move_target` | The target direction or resource type does not support moving. | No |

`high`, `medium`, and `low` may only contain resources that are `move_permission_state=movable` and `target_write_state=confirmed`.

Judging a resource as high relevance requires at least one strong piece of evidence:

1. An exact topic phrase appears in the title or content.
2. Multiple topic words appear simultaneously in a relevant context.
3. A Sheet / table cell clearly matches the user's topic.
4. A document name or project alias explicitly provided by the user matches.

Medium relevance examples:

1. The title contains one topic word, but the content cannot be confirmed.
2. The search snippet looks relevant, but it cannot be fully read.
3. An alias match is reasonable but the evidence is not strong enough.

<a id="审核-ui"></a>
## Review UI

The resource name in each group must be displayed.

Default display rules:

1. Expand `high` and `medium`.
2. Collapse `low`, `permission_denied`, `no_move_permission`, `move_permission_unknown`, `unverifiable`, and `unsupported_move_target`, but display the count and allow expansion.
3. For each visible resource, display the title, type, current location, evidence, and default action.
4. Do not display raw tokens unless the user requests technical details.

Example:

```text
Filter results:

Search scope: <resources owned / managed by the current user | all resources visible to the current identity>

High relevance (default move):
- Title｜Type｜Evidence｜Current location

Medium relevance (moved only after you select):
- Title｜Type｜Evidence｜Current location

Not moved by default:
- Low relevance: N items
- No permission: N items
- No move permission: N items
- Move permission unknown: N items
- Cannot verify: N items
- Move not supported: N items

You can choose to:
1. Confirm generating the move plan according to the default rules.
2. Select medium-relevance resources to add to the plan.
3. Request that certain resources be moved to other groups or removed from the plan.
4. Expand the low relevance / no permission / no move permission / move permission unknown / cannot verify / move not supported groups to view names.
```

<a id="用户调整规则"></a>
### User Adjustment Rules

If the user disagrees with the relevance results, `relevance_groups` must be updated based on the user's request, then the grouped results must be re-displayed and the subsequent move plan regenerated.

Typical adjustments include:

1. Remove a resource from `high`.
2. Promote a resource in `medium` to `high`.
3. Mark a resource as `low` or do not move it.
4. Request re-reading evidence or re-judging a batch of resources.
5. Request re-confirming the move permission for certain resources.

After user adjustment:

1. The old `move_plan_items` becomes invalid immediately.
2. The "adjusted relevance results" must first be output, displaying the adjusted items, the count of each group, and the names of high / medium relevance resources.
3. Do not merely reply "adjusted", and do not jump directly to `CONFIRM_EXECUTION`.
4. `PLAN_MOVE` must be re-executed based on the new `relevance_groups`.
5. Do not directly promote `no_move_permission` or `move_permission_unknown` resources to `high` / `medium`; you must first return to `RESOURCE_RESOLVE` and load [`lark-drive-workflow-topic-move-collector-resolve-verify.md`](lark-drive-workflow-topic-move-collector-resolve-verify.md) to obtain movable evidence.

<a id="调整后结果-ui"></a>
### Adjusted Result UI

```text
The relevance results have been adjusted per your request:
- <title>: <original group> -> <new group>

Adjusted groups:

Search scope: <resources owned / managed by the current user | all resources visible to the current identity>

High relevance (default move): N items
- Title｜Type｜Evidence｜Current location

Medium relevance (moved only after you select): N items
- Title｜Type｜Evidence｜Current location

Not moved by default:
- Low relevance: N items
- No permission: N items
- No move permission: N items
- Move permission unknown: N items
- Cannot verify: N items
- Move not supported: N items

The move plan will be regenerated based on these adjusted results; you can also continue adjusting.
```

<a id="状态plan_move"></a>
## State: `PLAN_MOVE`

Entry conditions: relevance grouping is ready.

Must:

1. When `target_location.create_required=true`, include the target creation plan.
2. Before generating the move plan, compare the normalized current parent with the target parent; for resources already at the target location, generate `skip_resource`, set `skip_reason=already_at_target`, and do not generate a move command.
3. By default, include all resources that are `high`, `move_permission_state=movable`, and `target_write_state=confirmed`.
4. Include resources that are `medium`, `move_permission_state=movable`, and `target_write_state=confirmed` only when the user explicitly selects them.
5. By default, exclude `low`, `permission_denied`, `no_move_permission`, `move_permission_unknown`, `unverifiable`, and `unsupported_move_target`.
6. Generate `skip_reason` for each skipped item.
7. Generate a stable `plan_id` for each plan item, and use `resource_id` to link the corresponding resource; do not guess the association by title or temporary token.
8. Save the complete, immutable `command_args` according to `command_family`; do not treat the Wiki underlying object token as the Wiki node move token.
9. For each `move_resource` item, copy the complete `rollback_input` required for pre-execution recovery, so that the confirmed plan does not depend on runtime re-querying of `ResourceItem`.
10. When the current parent cannot be structurally resolved or involves a Drive / Wiki cross-container move, set `rollback_supported=false` and an explicit `rollback_blocker`; that individual item may still enter confirmation, but the non-recoverable risk must be displayed item by item, and other independent items must not be blocked.
11. Stop and wait for the user's selection or execution intent.
12. Do not generate `move_resource` plan items for resources that are `move_permission_state!=movable` or `target_write_state!=confirmed`.

<a id="已在目标位置判定"></a>
### Already-at-Target-Location Determination

1. `drive_move` compares `current_parent_kind` with the target Drive parent, and compares the normalized `current_parent_token` / root identifier.
2. `wiki_move_node` compares `current_parent_space_id`, `current_parent_kind`, and `current_parent_token`; the Wiki space root node uses an explicit root identifier, and must not be confused with an empty string and unknown state.
3. `skip_reason=already_at_target` can be set only when the parent type, space ID (when applicable), and token are all resolved and equal; when the parent is unknown, do not guess that they are equal.

<a id="移动-token-选择"></a>
### Move Token Selection

| `command_family` | `command_args` must contain |
|------------------|---------------------------|
| `drive +move` | `file_token`, `type`, `folder_token`; when moving to Drive root, explicitly record that `folder_token` is empty and the target type is root. |
| `wiki +move` (node) | `node_token`, and `target_space_id` or `target_parent_token`; optional `source_space_id`. Do not use `wiki_obj_token` in place of `node_token`. |
| `wiki +move` (docs-to-wiki) | `obj_type`, `obj_token`, `target_space_id`, optional `target_parent_token`, and explicitly save `apply=false`. |
| `wiki +move-to-drive` | `node_token`, `folder_token`; when moving to Drive root, explicitly record that `folder_token` is empty. |
| `drive +create-folder` | `name`, parent `folder_token`; when creating at Drive root, explicitly record that the parent is empty. |
| `wiki +node-create` | `space_id`, `title`, `obj_type`, optional `parent_node_token`. |
| `none` | Do not execute a command; retain `skip_reason`. |

When the target is created by this workflow, the corresponding target parameter saves the `created_by_plan:<create_target plan_id>` reference. `EXECUTE` is only allowed to replace that reference with the token returned by the corresponding creation plan; do not re-search or guess the target.

<a id="计划-ui"></a>
### Plan UI

```text
Move plan generated:
- High relevance to be moved by default: N items
- Medium relevance you have selected: N items
- Of which non-auto-recoverable: N items
- Already at target location: N items
- Will not be moved: N items
- No move permission: N items
- Move permission unknown: N items

You can reply "confirm execution", or continue adjusting groups, adding or removing medium-relevance resources, or cancel this move.
```

## MovePlanItem

```json
{
  "plan_id": "稳定计划项 ID",
  "resource_id": "对应 ResourceItem.resource_id；create_target 为空",
  "action_type": "create_target|move_resource|skip_resource|unsupported",
  "title": "资源或目标名称",
  "resource_type": "源资源类型",
  "move_method": "drive_move|wiki_move_node|wiki_move_docs_to_wiki|wiki_move_to_drive|none",
  "command_family": "具体 shortcut 命令或 none",
  "command_args": {
    "<arg>": "按 command_family 参数表保存的完整、类型明确的参数"
  },
  "source_path": "用户确认时展示的源位置",
  "target_path": "用户确认时展示的目标位置",
  "move_permission_state": "movable|denied|unknown|not_required",
  "target_write_state": "confirmed|unknown|denied",
  "reason": "纳入或跳过原因",
  "skip_reason": "already_at_target 或其他跳过原因",
  "rollback_input": {
    "source_kind": "drive|wiki",
    "original_token": "原始 Drive / obj token",
    "original_node_token": "原始 Wiki node token",
    "resource_type": "恢复命令需要的资源类型",
    "original_parent_kind": "drive_folder|drive_root|wiki_node|wiki_space_root|unknown",
    "original_parent_token": "原始父级 token",
    "original_space_id": "原始 Wiki space_id",
    "original_path": "执行前路径"
  },
  "rollback_supported": "是否支持自动恢复",
  "rollback_blocker": "不可自动恢复原因",
  "execution_status": "pending|success|failed|skipped"
}
```

| Field | Description |
|-------|------|
| `plan_id` | Stable plan item ID, used to link the plan, snapshot, and execution log. |
| `resource_id` | Stable resource ID, used to link the confirmed plan and resolution results; `create_target` is empty. The execution stage must not rely on this association to re-query mutable parameters. |
| `action_type` | Plan action type. |
| `move_method` | The move method actually used. |
| `command_family` / `command_args` | The complete write command and parameter snapshot confirmed by the user; remains immutable after confirmation. When the target is pending creation, only the `created_by_plan:<plan_id>` reference may be used. |
| `move_permission_state` / `target_write_state` | Permission gate snapshot at the time of user confirmation; `move_resource` must respectively be `movable` / `confirmed`. The move permission for `create_target` is `not_required`, but the parent write permission must still be `confirmed`. |
| `rollback_input` | The complete recovery input copied from `ResourceItem`; only `move_resource` is required, and after the confirmation plan is generated, it must not be re-queried or guessed. |
| `rollback_supported` | Whether automatic recovery is supported. |
| `rollback_blocker` | Reason for non-auto-recoverability; use `cross_container_permission_model_not_losslessly_restorable` for cross-container moves, and `original_parent_token_unavailable` when the original parent token is missing. |
| `execution_status` | Execution status. |
