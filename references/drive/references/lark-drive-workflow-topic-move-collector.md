<a id="主题资料收集工作流"></a>
# Topic Material Collection Workflow

Workflow id: `topic_move_collector`

Risk / Structure: `R2-R3` / `S3`

This document implements the registered topic material collection workflow. Before execution, you must first read [`lark-drive-workflow.md`](lark-drive-workflow.md) and [`../../shared/index.md`](../../shared/index.md), and follow the shared execution protocol, Artifact Contract, Workflow Loading, authentication, and write confirmation rules.

This document is responsible for defining the global constraints, state machine, and progressive loading relationships of this workflow. Specific stage rules are placed in companion documents and are only loaded when entering the corresponding state.

Companion documents are merely reference files for this workflow, not independent skills. Do not route user requests directly to a companion document.

<a id="必读上下文"></a>
## Required Context

Before executing this workflow, you must first read [`../../shared/index.md`](../../shared/index.md), which is used to handle identity, authentication, permissions, and write operation confirmation rules.

Progressively load other skills / reference documents by stage:

- Target is Wiki or personal document library: [`../../wiki/index.md`](../../wiki/index.md)
- Need to read document content: [`../../doc/index.md`](../../doc/index.md) and [`../../doc/references/lark-doc-fetch.md`](../../doc/references/lark-doc-fetch.md)
- Need to verify Sheet content: [`../../sheets/index.md`](../../sheets/index.md)
- Need Drive search: [`lark-drive-search.md`](lark-drive-search.md)
- Need resource resolution: [`lark-drive-inspect.md`](lark-drive-inspect.md)

<a id="适用范围"></a>
## Scope of Application

This workflow is used to search for related materials in Workspace resources such as cloud space / cloud drive / Wiki / spreadsheets based on the topic, keywords, or content clues provided by the user, and after user confirmation, uniformly move them to a specified Drive folder or Wiki node.

Applicable trigger phrases include:

- "Help me find documents related to a certain topic and put them in this folder"
- "Collect all materials about a certain project under a knowledge base node"
- "Find materials containing certain content, and after confirmation, move them to a newly created directory"
- "Search for materials I am responsible for by this keyword, and archive the related materials"

The default search scope is Workspace resources owned / managed by the current user, i.e., `owner_scope=mine`. Only when the user explicitly requests "unrestricted owner", "including those shared with me", "all documents I can see", or "full search" should `owner_scope=all_visible` be used to enter extended recall mode.

The user is not required to first limit the folder or knowledge base scope. Only when the user explicitly specifies a scope should `--folder-tokens`, `--space-ids`, or other explicit restrictions be used.

<a id="非目标"></a>
## Non-Goals

By default, do not generate:

- Long-form research reports
- Content summary documents
- Sheet lists or statistical dashboards
- Automated permission governance reports

By default, it is prohibited to execute:

- Creating folders or Wiki nodes before confirmation
- Moving resources before confirmation
- Deleting resources, renaming resources, or modifying public permissions
- Automatically applying for permissions in bulk
- Adding resources without permission or that cannot be verified to the move plan
- Adding resources with unknown move permission or without move eligibility to the move plan

If the user explicitly requests writing results to a Sheet / Doc, switch to the corresponding specialized capability; the default output of this workflow is the resource archiving result after moving.

<a id="agent-执行约束"></a>
## Agent Execution Constraints

After this workflow is triggered, the agent must:

1. Execute in the order of the "Execution State Machine".
2. Maintain the fields in "Runtime State".
3. Before executing a state, first read the document corresponding to that state in the `## 渐进加载关系` table of this document.
4. User-visible explanations, field descriptions, and UI copy use Chinese.
5. State names, field names, enum values, and command names retain stable English identifiers.
6. Treat `CONFIRM_CONTEXT` and `CONFIRM_EXECUTION` as strong user confirmation gates: the former confirms the topic, target location, identity, search scope, optional restrictions, and target resolution result before searching; the latter confirms the creation target and resource moves before writing.
7. Before entering `EXECUTE`, do not create the target folder / node, and do not move resources.
8. Must display the resource names in each relevance group; low-confidence groups may be collapsed but must be viewable.
9. By default, only move `high` related resources; `medium` resources must be explicitly selected by the user.
10. Even if the user-visible list is displayed with pagination, the complete internal state must be maintained.
11. `RESOURCE_RESOLVE` and `CONTENT_VERIFY` are two independent mandatory stages and must not be merged; search results, titles, or summaries must not be used to directly replace `CONTENT_VERIFY`, and you must not go directly from `RESOURCE_RESOLVE` to `RELEVANCE_CLASSIFY`.
12. After triggering, lock `workflow_id=topic_move_collector`; during execution, do not automatically switch to another workflow.
13. If you believe a workflow switch is needed, you must stop and explain the reason to the user, and wait for user confirmation.
14. `RESOURCE_RESOLVE` is the move eligibility gate; only resources that confirm `move_permission_state=movable` and `target_write_state=confirmed` can enter the default move pipeline.

<a id="用户展示-ui-规则"></a>
## User-Facing UI Rules

All user-visible UI must include:

1. Key results already completed.
2. What will be done next, and whether a write operation will occur.
3. If `wait_for_user=true`, clearly tell the user which actions can be chosen.
4. If no user action is needed, clearly state that execution will continue, to avoid the user mistakenly thinking the process has stopped.

Typical actions include: confirm to continue, modify topic / target / restrictions, expand more results, adjust relevance groups, select medium-relevance resources, confirm execution, cancel execution.

<a id="职责边界"></a>
## Responsibility Boundaries

| File | Responsible for | Not responsible for |
|------|------|--------------|
| `lark-drive-workflow-topic-move-collector.md` | Trigger rules, global constraints, state machine, progressive loading relationships, command family whitelist | Specific stage rules, UI templates, execution details |
| `lark-drive-workflow-topic-move-collector-setup.md` | `PARSE_INPUT`, `RESOLVE_TARGET`, `CONFIRM_CONTEXT`, `TargetLocation` | Search execution, relevance classification, write operations |
| `lark-drive-workflow-topic-move-collector-recall.md` | `SEARCH_RECALL`, `RECALL_ENHANCE`, search query strategy, deduplication, `CandidateItem` | Resource token resolution, content verification, write operations |
| `lark-drive-workflow-topic-move-collector-resolve-verify.md` | `RESOURCE_RESOLVE`, `CONTENT_VERIFY`, permission matrix, `ResourceItem` | Relevance classification, move plan, write operations |
| `lark-drive-workflow-topic-move-collector-review-plan.md` | `RELEVANCE_CLASSIFY`, `PLAN_MOVE`, `MovePlanItem`, display grouping | Resource resolution, content verification, write operation execution, recovery |
| `lark-drive-workflow-topic-move-collector-execute.md` | `CONFIRM_EXECUTION`, `EXECUTE`, `VERIFY`, `RESTORE`, `RollbackSnapshotItem`, execution logs | Search, classification, and plan schema |

<a id="运行时状态"></a>
## Runtime State

This workflow extends the shared Artifact Contract. The agent must maintain the following specialized internal fields during a single workflow run:

| Field | Description |
|-------|------|
| `current_state` | Current state machine node. |
| `topic` | User-confirmed topic, keywords, synonyms, and exclusion terms. |
| `target_location` | Target location resolution result, see `TargetLocation` in the setup file. |
| `identity` | Execution identity; by default, prefer `--as user`. |
| `owner_scope` | Search owner scope; default is `mine`, searching only resources owned / managed by the current user; set to `all_visible` only when the user explicitly requests expansion. |
| `constraints` | Restrictions explicitly confirmed by the user, such as type, time, creator, and scope. |
| `allow_cross_container_move` | Whether cross-Drive / Wiki container moves are allowed; allowed by default, but must be shown to the user for confirmation. |
| `recall_query_states` | Pagination state, cumulative page count, `next_page_token`, `has_more`, completion or blocked status for each basic / enhanced query. |
| `candidate_items` | Search recall results, including query evidence and deduplication information. |
| `resource_items` | Parsed standard resource list. |
| `content_verify_completed` | Content verification stage completion marker; reset to `false` when `resource_items` is newly created or changed, and set to `true` only after all resources have a verification status or skip reason. |
| `relevance_groups` | High relevance, medium relevance, low relevance, no permission, no move permission, unknown move permission, unable to verify, non-movable groups. |
| `move_plan_items` | Complete move plan generated after user selection, including stable resource associations, immutable command parameters, permission snapshots, and recovery inputs. |
| `execution_journal` | Write operation log, used for verification and recovery. |
| `rollback_snapshot` | Location snapshot before write operations, used only for failure recovery or when the user requests recovery. |
| `display_page_state` | Pagination, filtering, and expansion state of the user-visible list. |

<a id="执行状态机"></a>
## Execution State Machine

| State | Protocol Step | Entry Condition | Agent Must Execute | User-Visible Output | `wait_for_user` | Next State |
|-------|---------------|-----------------|---------------|--------------------|---------------|------------|
| `PARSE_INPUT` | `route` / `scope` | Workflow is triggered | Load setup document; parse topic, target, identity, and restrictions | Clarifying questions or resolution summary | `true` when required fields are missing | `RESOLVE_TARGET` |
| `RESOLVE_TARGET` | `scope` | Topic and target have been obtained | Resolve existing target, or resolve target to be created; branch by resolution status | Target resolution result or blocker | `true` when not `resolved` | Enter `CONFIRM_CONTEXT` when `resolved`; otherwise remain in this state |
| `CONFIRM_CONTEXT` | `scope` | `target_resolve_status=resolved` | Display topic, target, identity, restrictions, and cross-container settings | Pre-search confirmation UI | `true` | `SEARCH_RECALL` |
| `SEARCH_RECALL` | `read` | User confirms context | Execute basic recall using original keywords, default owner scope, and explicit restrictions; automatically continue batches with a maximum of 5 pages per batch | Search progress / basic statistics | `true` when blocked | Enter `RECALL_ENHANCE` after all basic queries are complete |
| `RECALL_ENHANCE` | `read` | All basic queries are complete | Execute coverage enhancement queries, automatically continue batches with a maximum of 5 pages per batch, and merge results | Enhanced recall summary | `true` when blocked | Enter `RESOURCE_RESOLVE` after all enhanced queries are complete |
| `RESOURCE_RESOLVE` | `read` | Candidate list is ready | Resolve token, type, parent location, owner, and move eligibility | Resolution progress / blocker summary | `true` when blocked | `CONTENT_VERIFY` |
| `CONTENT_VERIFY` | `read` | Resource list is ready | Perform bounded content reading for supported resources, and write skip reasons for the remaining resources | Verification progress / verification summary | `true` when blocked | `RELEVANCE_CLASSIFY` |
| `RELEVANCE_CLASSIFY` | `assess` | Evidence is ready | Group by relevance and executability | Grouped result list | `false` | `PLAN_MOVE` |
| `PLAN_MOVE` | `assess` / `plan` | Grouping is complete | Generate move plan based on default rules and user-selectable options | Draft plan and selection options | `true` | `CONFIRM_EXECUTION` |
| `CONFIRM_EXECUTION` | `confirm` | User requests execution | Display creation, moves, skipped items, and risks | Write operation confirmation UI | `true` | `EXECUTE` or `PLAN_MOVE` or `DONE` |
| `EXECUTE` | `execute` | User explicitly confirms write operations | Create the target first if needed, then move confirmed resources | Execution progress | `true` when blocked | `VERIFY` or `RESTORE` |
| `VERIFY` | `verify` | Execution is complete | Verify the move results under the target location | Verification result | `true` when recovery options are provided | `DONE` or `RESTORE` |
| `RESTORE` | `recovery confirm` / `recovery execute` | User requests recovery | Recover based only on snapshots and logs | Recovery confirmation / result | `true` before write operations | `VERIFY` or `DONE` |
| `DONE` | `done` | No subsequent operations | Stop | Final reply | `false` | End |

<a id="状态跳转硬约束"></a>
### Hard Constraints on State Transitions

1. `RESOLVE_TARGET` can enter `CONFIRM_CONTEXT` only when `target_resolve_status=resolved`; `ambiguous`, `unsupported`, or `permission_denied` must remain in `RESOLVE_TARGET` and wait for the user to choose, change the target, or end.
2. `SEARCH_RECALL` can enter `RECALL_ENHANCE` only when `has_more=false` for all basic queries; when a single batch reaches 5 pages but there are still more results, batches must automatically continue, and you must not jump ahead early.
3. `RECALL_ENHANCE` can enter `RESOURCE_RESOLVE` only when `has_more=false` for all enhanced queries; you must not go directly to `RELEVANCE_CLASSIFY` or `PLAN_MOVE`.
4. `RESOURCE_RESOLVE` must generate a corresponding `ResourceItem` for each `CandidateItem`, or generate an explicit resolution failure / permission-restricted status.
5. `RESOURCE_RESOLVE` must write `move_permission_state` and `move_permission_basis` for each `ResourceItem`; after completion, set `content_verify_completed=false`, and the next state can only be `CONTENT_VERIFY`.
6. It is prohibited to go directly from `RESOURCE_RESOLVE` to `RELEVANCE_CLASSIFY`. Even if no resource has readable body content, you must still enter `CONTENT_VERIFY`, write a verification status or skip reason for each item, and output a verification summary.
7. `CONTENT_VERIFY` must write content evidence, a search evidence reuse explanation, or an unverifiable reason for each `ResourceItem`; resources with unknown move permission or no move permission may only have a skip verification reason written.
8. Only when `resource_items` is ready, each item has a verification status or skip reason, and `content_verify_completed=true`, can you enter `RELEVANCE_CLASSIFY`.
9. After the user adjusts relevance groups, you must return to `RELEVANCE_CLASSIFY` to output the adjusted grouping results, then enter `PLAN_MOVE` to regenerate the plan.

<a id="workflow-切换门禁"></a>
### Workflow Switch Gate

A workflow switch may be considered only in the following situations:

1. The user explicitly says they will no longer do topic material collection, and instead will organize the entire directory structure or generate an inventory plan.
2. The current workflow clearly cannot cover the user's new goal.
3. What the user requests is directory structure governance, rather than finding topic-related materials and moving them.

Even if the above conditions are met, you must not switch automatically; you must first explain the reason to the user and wait for confirmation.

<a id="渐进加载关系"></a>
## Progressive Loading Relationships

| State | Required Documents |
|-------|---------------|
| `PARSE_INPUT` / `RESOLVE_TARGET` / `CONFIRM_CONTEXT` | [`lark-drive-workflow-topic-move-collector-setup.md`](lark-drive-workflow-topic-move-collector-setup.md) |
| `SEARCH_RECALL` / `RECALL_ENHANCE` | [`lark-drive-workflow-topic-move-collector-recall.md`](lark-drive-workflow-topic-move-collector-recall.md) |
| `RESOURCE_RESOLVE` / `CONTENT_VERIFY` | [`lark-drive-workflow-topic-move-collector-resolve-verify.md`](lark-drive-workflow-topic-move-collector-resolve-verify.md) |
| `RELEVANCE_CLASSIFY` / `PLAN_MOVE` | [`lark-drive-workflow-topic-move-collector-review-plan.md`](lark-drive-workflow-topic-move-collector-review-plan.md) |
| `CONFIRM_EXECUTION` / `EXECUTE` / `VERIFY` / `RESTORE` | [`lark-drive-workflow-topic-move-collector-execute.md`](lark-drive-workflow-topic-move-collector-execute.md) |

<a id="命令映射"></a>
## Command Mapping

| State | Allowed Command Families | Purpose |
|-------|--------------------------|---------|
| `RESOLVE_TARGET` | `drive +inspect`, `wiki +node-get`, `wiki +space-list`, `drive +search` used only for finding folder candidates | Resolve target location |
| `SEARCH_RECALL` / `RECALL_ENHANCE` | `drive +search` | Search recall and coverage enhancement |
| `RESOURCE_RESOLVE` | `drive +inspect`, `wiki +node-get`, `drive metas batch_query`, `drive permission.members auth` when necessary | Resolve standard tokens, owner, permission signals, and move eligibility |
| `CONTENT_VERIFY` | `docs +fetch`, `sheets +cells-get`, `sheets +cells-search`, `drive +preview` when necessary | Verify content evidence |
| `EXECUTE` | `drive +create-folder`, `wiki +node-create`, `drive +move`, `wiki +move`, `wiki +move-to-drive`, `drive +task_result` | Execute confirmed write operations |
| `VERIFY` | `drive files list`, `wiki +node-list`, `wiki +node-get`, `drive +inspect`, `drive +task_result` | Verify execution results |
| `RESTORE` | `drive +move`, `wiki +move`, `drive +delete`, `wiki +node-delete`, `drive +task_result` | Recover confirmed resources and clean up targets newly created in this run |

<a id="引用文档"></a>
## Reference Documents

- [Input and Target Confirmation](lark-drive-workflow-topic-move-collector-setup.md)
- [Recall](lark-drive-workflow-topic-move-collector-recall.md)
- [Resource Resolution and Content Verification](lark-drive-workflow-topic-move-collector-resolve-verify.md)
- [Review and Planning](lark-drive-workflow-topic-move-collector-review-plan.md)
- [Execution](lark-drive-workflow-topic-move-collector-execute.md)
- [lark-drive-search](lark-drive-search.md)
- [lark-drive-inspect](lark-drive-inspect.md)
- [lark-drive-move](lark-drive-move.md)
- [lark-drive-create-folder](lark-drive-create-folder.md)
- [lark-drive-delete](lark-drive-delete.md)
- [lark-wiki-move](../../wiki/references/lark-wiki-move.md)
- [lark-wiki-move-to-drive](../../wiki/references/lark-wiki-move-to-drive.md)
- [lark-wiki-node-create](../../wiki/references/lark-wiki-node-create.md)
- [lark-wiki-node-delete](../../wiki/references/lark-wiki-node-delete.md)
