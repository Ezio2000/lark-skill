<a id="知识整理工作流planning"></a>
# Knowledge Organization Workflow: Planning

Loaded by states: `PLAN_GENERATION`, `EXEC_CONFIRM`.

This file owns plan generation, plan revision, user-facing pagination, and execution confirmation. It MUST NOT perform write operations.

## Required Context

Before executing rules in this file:

1. `resource_items`, `classification_rules`, and `target_tree` MUST already exist.
2. Follow command syntax, scope requirements, and confirmation behavior from referenced shortcut docs.
3. Follow `Non-goals` from the main workflow entry. Do not execute excluded operations from this file.

## State: PLAN_GENERATION

Entry: `target_tree` exists after the user confirmed the organization approach.

MUST:

1. Generate complete internal `plan_items`.
2. Build `DisplayItem` only for user-facing pages.
3. Apply `Plan Generation`.
4. Apply `Plan Pagination`.
5. Set `active_plan_items` to the latest complete plan.
6. Keep complete plan internally even if only one page is displayed.
7. Apply `Plan Generation Progress Reporting`.
8. Output `Target Tree And Plan Overview` or requested plan page, then wait.

### Plan Generation

| Condition | Agent MUST Do |
|-----------|---------------|
| Target path appears in any plan item | Ensure the path exists in `target_tree` |
| Source parent and descendants share same target subtree | Move parent only; mark descendants `covered_by_parent_move=true` |
| A child target differs from parent target | Move divergent child before parent; order by `source_depth` from deep to shallow |
| Target directory / node does not exist | Add `create_folder` / `create_node` before move |
| Resource is root-level and target path differs from current path | Add a `move` plan item; do not leave root-level resources in place by default |
| Resource has `needs_review=true` because classification evidence is insufficient | Set `target_path` to manual confirmation target, set `action=move`, and preserve `needs_review_reason` |
| Top-level folder / Wiki node has descendants that share the same target subtree | Move the parent folder / node only; descendants are covered by parent move |
| Top-level folder / Wiki node has descendants with divergent target subtrees | Move divergent descendants first; then move the parent only if it still has a target path or needs manual confirmation |
| Source container is reused as a target container | Keep the container in place; do not move it as source-container cleanup |
| Non-reused source container has descendants moved elsewhere | Add an explicit folder / node move plan item after descendant moves; target defaults to the source-container cleanup target |
| Source container handling is ambiguous | Move it to the manual confirmation target or mark `needs_review=true`; do not leave it in the root by default |
| Target parent token unresolved | Keep plan item but block execution until token is resolved |
| Resource title is poor or inconsistent | Report the naming issue only; do not create rename or title-patch plan items |

### Plan Generation Progress Reporting

Plan generation can be long-running when `resource_items` is large or source-container parent / child move ordering is complex.

Rules:

1. If plan generation starts with more than 500 `resource_items`, output one concise start notice with the resource count and that no write operation is being executed.
2. If plan generation runs longer than about 60 seconds, output progress about every 60 seconds.
3. Progress reports SHOULD include only fields currently known: processed resource count, generated plan item count, create count, move count, source-container move count, review count, and current step.
4. Do not display unpaginated plan details as progress. Complete `plan_items` remain internal until the normal paginated output.
5. Do not ask the user to continue during plan generation unless auth, permission, API, target scope, or environment blockers occur.
6. Do not output filler such as "still running" without current counts or current step.

Example:

```text
Plan generation progress: processed <processed_count>/<resource_count> resources, generated <plan_item_count> plan items, of which <create_count> are creations and <move_count> are moves. Continuing to compute parent-child directory move order; no creations or moves will be executed.
```

## PlanItem

`PlanItem` is for internal execution. It may contain tokens and internal enums.

| Field | Meaning |
|-------|---------|
| `plan_id` | Stable unique ID for plan / verification, such as `P001` |
| `source_path` | Current path |
| `title` | Resource title |
| `type` | Resource type |
| `source_token` | Drive token or normal resource token |
| `source_node_token` | Wiki node token; empty for non-Wiki resources |
| `source_parent_token` | Current parent folder token or parent Wiki node token |
| `source_depth` | Original depth in source tree |
| `target_path` | Target path |
| `target_parent_path` | Target parent path |
| `target_parent_token` | Target parent token; may be empty during planning, MUST be resolved before execution |
| `action` | Internal enum: `keep` / `create_folder` / `create_node` / `move` |
| `covered_by_parent_move` | Whether an ancestor move already covers this item |
| `reason` | Classification reason |
| `evidence_paths` | Evidence paths |
| `evidence_count` | Evidence count or hit count |
| `confidence` | Internal enum: `high` / `medium` / `low` |
| `needs_review` | Whether human review is required |
| `needs_review_reason` | Reason requiring human review |
| `rollback_origin_kind` | Internal recovery origin marker: `drive_folder` / `drive_root` / `wiki_node` / `wiki_space_root` / `unknown` |
| `rollback_origin_token` | Original parent token when applicable; empty for root markers |
| `rollback_origin_space_id` | Original Wiki space ID when `rollback_origin_kind=wiki_space_root` |
| `rollback_supported` | Whether this move item can be restored automatically if recovery is requested |
| `rollback_blocker` | Internal reason when `rollback_supported=false` |

### Rollback Origin Readiness

This is an internal execution-safety rule. Do not expose rollback readiness on the normal user-facing execution confirmation path.

Rules:

1. `action=move` items entering execution SHOULD have `rollback_origin_kind`.
2. `rollback_origin_kind` can be:
   - `drive_folder`: original Drive parent folder token is known.
   - `drive_root`: original location is the Drive root.
   - `wiki_node`: original Wiki parent node token is known.
   - `wiki_space_root`: original location is the Wiki space root and `rollback_origin_space_id` is known.
3. If `rollback_origin_kind` is missing or `unknown`, the agent MUST try to resolve it before execution from `ResourceItem.parent_token`, traversal context, `source_path`, `space_id`, or `wiki +node-get` for Wiki resources.
4. If the origin is still unresolved, set `rollback_supported=false` and `rollback_blocker`, but do not block the entire execution solely because recovery is unsupported.
5. Target resolution remains mandatory: a move item with unresolved `target_parent_token` MUST NOT execute.
6. Internal recovery metadata MUST NOT change `DisplayItem` output on the normal successful path.

## DisplayItem

`DisplayItem` is for user-facing output. It MUST NOT expose raw internal enum values.

| Display Field | Source |
|---------------|--------|
| `序号` | Page-local row number |
| `当前位置` | `source_path` |
| `标题` | `title` |
| `类型` | Human-readable `type` when possible; raw type is acceptable only when there is no clearer label |
| `目标位置` | `target_path` |
| `动作` | Convert from `action` using action display map |
| `原因` | `reason` |
| `置信度` | Convert from `confidence` using confidence display map |
| `待确认原因` | `needs_review_reason` |

Action display map:

| Internal Enum | User-Facing Label |
|---------------|-------------------|
| `keep` | Keep unchanged |
| `create_folder` | Create folder |
| `create_node` | Create Wiki node |
| `move` | Move to target directory |

`needs_review=true` is a review state, not an action. A review item MUST still use `action=move` when its target is the manual confirmation target.

### Manual Confirmation Target

Resources with insufficient classification evidence MUST be moved to the manual confirmation target after the user confirms execution.

Rules:

1. The target tree MUST include `待人工确认` or an equivalent user-specified manual confirmation path.
2. For Drive scopes, the manual confirmation target is a Drive folder.
3. For Wiki scopes, the manual confirmation target is a Wiki node.
4. Plan items for these resources MUST set `needs_review=true`, preserve `needs_review_reason`, set `target_path` to the manual confirmation target, and set `action=move`.
5. Do not leave these items in their original location by default.

Confidence display map:

| Internal Enum | User-Facing Label |
|---------------|-------------------|
| `high` | High, evidence is clear |
| `medium` | Medium, has basis but confirmation is recommended |
| `low` | Low, requires manual confirmation |

### Plan Pagination

| Output Area | Rule |
|-------------|------|
| Plan details | Show at most 20 plan items per page |
| Plan item count > 20 | MUST paginate; do not output all details at once |
| Plan item count > 500 | First response MUST show overview and filters only; no detail rows until user asks |
| Pagination | Affects display only; complete `plan_items` MUST remain internal |

### Target Tree And Plan Overview

```text
Suggested target directory structure

<target_tree>

Move / create plan overview

This plan has <total_count> items in total:
- Directories / nodes to create: <create_count> items
- Resources to move: <move_count> items (of which source container bodies: <source_container_move_count> items)
- Keep unchanged: <keep_count> items
- Pending manual confirmation: <review_count> items
- High confidence: <high_count> items
- Medium confidence: <medium_count> items
- Low confidence: <low_count> items

You can choose:
1. View page 1 details
2. View only directories / nodes to be created
3. View only items pending manual confirmation
4. View only high-confidence move items
5. Proceed to the next step: confirm the execution plan
```

If `total_count > 500`, say:

```text
The plan is large, so I will show only the overview first.
```

### Plan Revision Protocol

When the user corrects or adjusts the plan in `PLAN_GENERATION` or `EXEC_CONFIRM`, the agent MUST treat it as a full-plan revision unless the user explicitly asks to execute only the corrected items.

Revision triggers include:

- Adjusting classification rules.
- Adjusting target folder / Wiki node structure.
- Changing one or more resources' target paths.
- Excluding resources from movement.
- Restricting execution to high-confidence items.
- Moving a whole category to another target.
- Changing manual confirmation handling.
- Changing source container cleanup or retention handling.

Internal rules:

1. Record the user correction in `last_user_correction`.
2. Mark the previous `plan_items` as stale.
3. Recompute `classification_rules`, `target_tree`, and complete `plan_items` when needed.
4. Increment `plan_version`.
5. Set `active_plan_items` to the complete revised plan.
6. Append a short internal summary to `plan_revision_history`.
7. Do not execute stale `plan_items`.
8. Do not execute only the delta unless the user explicitly asks for partial execution.

User-facing output:

```text
The complete plan has been regenerated according to your changes.

Applied changes:
- <correction item 1>
- <correction item 2>

Current complete plan:
- Directories / nodes to create: <create_count> items
- Resources to move: <move_count> items
- Keep unchanged: <keep_count> items
- Pending manual confirmation: <review_count> items

Note: subsequent execution is based on this complete revised plan by default, not only the changes just made.

You can choose:
1. View the revised plan overview
2. View the resources involved in this change
3. Proceed to the next step: confirm the execution plan
4. Continue adjusting
```

If the user explicitly asks to execute only the corrected items, ask for confirmation before execution:

```text
You explicitly requested to execute only the <count> items involved in this change. The remaining plan items will not be executed.
Please confirm whether to execute only these items?
```

### Plan Detail Page

```text
Move / create plan, page <page>/<total_pages>, 20 items per page

| No. | Current Location | Title | Type | Target Location | Action | Reason | Confidence | Reason Pending Confirmation |
|------|----------|------|------|----------|------|------|--------|------------|

<remaining_pages> more pages are not displayed.

You can reply:
1. Continue to the next page
2. View only items pending manual confirmation
3. View only low-confidence items
4. Proceed to the next step: confirm the execution plan
```

## State: EXEC_CONFIRM

Entry: user asks to view execution confirmation or continue toward execution.

MUST:

1. Show write-operation summary:
   - Which directories / nodes will be created
   - Which resources will be moved
   - Which source container bodies will be moved (if any)
   - Which resources still require manual confirmation
   - Estimated impact scope
2. Use `active_plan_items` from the latest complete plan.
3. Show `Permission Inheritance Notice`.
4. Ask for execution scope using `Execution Confirmation`.
5. Reference `Non-goals` for operations excluded from this workflow.
6. Wait for explicit confirmation.

### Permission Inheritance Notice

Before execution confirmation, MUST show this notice:

```text
Permission notice: after resources are moved, resource permissions may change with the target location, and the visible scope or collaboration permissions may change. This workflow will not automatically modify permissions.
```

### Execution Confirmation

When the user wants execution, ask for execution scope:

Execution confirmation options MUST be numbered by currently available choices. Do not show disabled choices, and do not ask the user to reply with skipped numbers.

If a plan detail page is currently active:

```text
Please confirm the execution scope:

1. Execute the complete plan: <total_count> items
2. Execute only the current page: <current_page_count> items
3. Execute only high-confidence items: <high_confidence_count> items
4. Do not execute for now; keep only the plan

This workflow only executes creations, moves, and necessary single-resource permission requests within the confirmed scope; it will not rename any resource.
```

If no plan detail page is currently active:

```text
Please confirm the execution scope:

1. Execute the complete plan: <total_count> items
2. Execute only high-confidence items: <high_confidence_count> items
3. Do not execute for now; keep only the plan

If you need to execute only a certain page, please view the plan detail page first.

This workflow only executes creations, moves, and necessary single-resource permission requests within the confirmed scope; it will not rename any resource.
```

If there is no pagination, still state the total number of plan items covered by confirmation.
