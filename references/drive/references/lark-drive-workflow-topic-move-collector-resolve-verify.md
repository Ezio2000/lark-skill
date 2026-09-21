<a id="主题资料收集工作流资源解析与内容验证"></a>
# Topic Material Collection Workflow: Resource Resolution and Content Verification

Loaded by states `RESOURCE_RESOLVE`, `CONTENT_VERIFY`.

This document is responsible for resource resolution, structured parent, move eligibility, content verification, and `ResourceItem`. It must not judge relevance, generate move plans, create targets, move resources, or perform recovery operations.

This document serves only `topic_move_collector`. When entering this document, `workflow_id` must be `topic_move_collector`; the current task must not be rerouted to another workflow.

<a id="必读上下文"></a>
## Required Context

Before executing the rules in this document:

1. Handle identity, authentication, and permissions per [`../../shared/index.md`](../../shared/index.md).
2. Handle URL / token resolution per [`lark-drive-inspect.md`](lark-drive-inspect.md).
3. Use `drive metas batch_query` to fill in the Drive resource owner, title, and URL.
4. When necessary, use `drive permission.members auth` to read permission signals; this interface does not provide a direct determination of `full_access` / move permission, and `manage_public` must not be equated with movable.
5. Handle Wiki node resolution per [`../../wiki/references/lark-wiki-node-get.md`](../../wiki/references/lark-wiki-node-get.md).
6. Read document content per [`../../doc/references/lark-doc-fetch.md`](../../doc/references/lark-doc-fetch.md).
7. When Sheet content needs to be verified, execute per [`../../sheets/index.md`](../../sheets/index.md).

<a id="进入解析与验证阶段前校验"></a>
## Pre-Check Before Entering the Resolution and Verification Phase

After entering this document, if `resource_items` does not yet exist, the current state must be `RESOURCE_RESOLVE`.

It is forbidden to go directly from `candidate_items` to `CONTENT_VERIFY` or `RELEVANCE_CLASSIFY`, and it is also forbidden to go directly from `RESOURCE_RESOLVE` to `RELEVANCE_CLASSIFY`. Even if the candidate items already have titles, URLs, summaries, or tokens, `RESOURCE_RESOLVE` and `CONTENT_VERIFY` must still be executed in sequence; the two states must not be merged.

<a id="状态resource_resolve"></a>
## State: `RESOURCE_RESOLVE`

Entry condition: the candidate list is ready.

Must:

1. Generate a stable `resource_id` for each `CandidateItem`, and convert it into a normalized `ResourceItem`.
2. Resolve the canonical token, resource type, URL, structured current parent, Wiki node identity, and read permission status.
3. For Wiki resources, retain both `wiki_node_token` and `wiki_obj_token`.
4. Fill in `owner_id`, `is_owner`, `source_move_state`, `source_parent_write_state`, `target_write_state`, `move_permission_state`, and `move_permission_basis` per `move_method`.
5. Detect unsupported move directions based on `target_location`.
6. Resources that fail to resolve must still remain in the review grouping and must not be silently discarded.
7. Even if the search results already contain titles, URLs, or tokens, `ResourceItem` must still be generated through this state; it is forbidden to go directly from recall results to relevance grading.
8. Only resources confirmed to have `move_permission_state=movable` and `target_write_state=confirmed` may enter the subsequent default move chain.
9. When resolution takes longer than about 60 seconds, a progress prompt must be output, and then prompted once about every 60 seconds thereafter.

<a id="解析规则"></a>
### Resolution Rules

| Candidate Type | What the agent must do |
|----------------|---------------|
| Drive URL / token | When the token or type is uncertain, use `drive +inspect`. |
| Wiki URL / token | Use `drive +inspect` or `wiki +node-get`; retain both node identity and object identity. |
| Folder candidate | Mark as a container; do not treat it as an ordinary document for content verification. |
| Shortcut candidate | When the source resource can be resolved, resolve the source resource; at the same time retain the shortcut identity. |
| No read permission | Retain the visible metadata and set `permission_state=denied`. |
| No move permission or move permission unknown | Retain the visible metadata and recall evidence, and set the corresponding `move_permission_state`. |
| Unable to resolve the current parent | Set `current_parent_kind=unknown`, retain the known path, and set `rollback_supported=false` and an explicit blocker for subsequent plan items; do not fabricate a parent token. |

<a id="资源解析进度-ui"></a>
### Resource Resolution Progress UI

When `RESOURCE_RESOLVE` lasts longer than about 60 seconds, output the current progress:

```text
Resource resolution progress: resolved <resolved_count>/<total_count> items, confirmed movable <movable_count> items, no move permission <denied_count> items, move permission unknown <unknown_count> items, resolution failed <failed_count> items.
Current resource: <title>
Continuing resolution; no resources will be created or moved.
```

If permission or owner metadata is being processed, you may add:

```text
Current step: resolving owner / current parent / move eligibility.
```

After `RESOURCE_RESOLVE` completes, output a summary:

```text
Resource resolution complete:
- Total candidates: N items
- Eligible for content verification: N items
- No move permission: N items
- Move permission unknown: N items
- Resolution failed or no read permission: N items

The next step will perform content verification on movable resources; no resources will be created or moved.
```

<a id="资源解析出口门禁"></a>
### Resource Resolution Exit Gate

After `RESOURCE_RESOLVE` completes, you must:

1. Reset `content_verify_completed` to `false`.
2. Set the next state to `CONTENT_VERIFY`, and must not set it to `RELEVANCE_CLASSIFY` or `PLAN_MOVE`.
3. Do not generate `relevance`, `relevance_groups`, or a move plan in this state.
4. Even if the number of resources whose body can be read is 0, you must still enter `CONTENT_VERIFY`, record a skip-verification reason for each item, and output a verification summary.

<a id="移动资格判定"></a>
### Move Eligibility Determination

`owner` can only serve as partial permission evidence and must not by itself judge a resource as `movable`. `RESOURCE_RESOLVE` must first record the following independent states per `move_method`:

| Field | Description |
|------|------|
| `source_move_state` | Whether the current identity is confirmed to be able to perform the corresponding move on the source resource; Drive owner can only serve as evidence that a Drive source resource is manageable, and the owner of the underlying Wiki resource cannot prove that the Wiki node is movable. |
| `source_parent_write_state` | Whether the current identity is confirmed to be able to edit the source location; only `drive_move` must be confirmed, and other move methods are `not_required`. |
| `target_write_state` | Whether the current identity is confirmed to be able to write to the target location; for targets to be created, the creation / write permission of the parent location applies. |

<a id="按移动方式的权限矩阵"></a>
#### Permission Matrix by Move Method

| `move_method` | Evidence for `source_move_state=confirmed` | `source_parent_write_state` | `target_write_state` |
|---------------|--------------------------------------|-----------------------------|----------------------|
| `drive_move` | The current user is the reliably resolved owner of the Drive resource, or there is explicit evidence that the resource is manageable | Must be `confirmed` | Must be `confirmed` |
| `wiki_move_docs_to_wiki` | There is explicit permission to directly migrate a Drive document in; owner metadata alone is insufficient to prove direct migration is possible | `not_required` | Must confirm that the target Wiki node / space is writable |
| `wiki_move_node` | There is explicit move permission for the Wiki node / source space; it must not be inferred from the underlying resource owner | `not_required` | Must confirm that the target Wiki node / space is writable |
| `wiki_move_to_drive` | There is explicit permission to move the Wiki node out; it must not be inferred from the underlying resource owner | `not_required` | Must confirm that the target Drive folder is writable |

<a id="聚合顺序"></a>
#### Aggregation Order

1. When the target direction or resource type is unsupported, set `move_permission_state=denied`, `move_permission_basis=["unsupported_direction"]`.
2. When any required state is `denied`, set `move_permission_state=denied`, and record `source_denied`, `source_parent_denied`, or `target_denied` in `move_permission_basis`.
3. When any required state is `unknown`, set `move_permission_state=unknown`, and record the corresponding `source_unknown`, `source_parent_unknown`, or `target_unknown`.
4. Only when all required states in the permission matrix are `confirmed` may you set `move_permission_state=movable`, `move_permission_basis=["permission_matrix_confirmed"]`.

Notes:

1. `drive permission.members auth` does not provide `full_access` or `move` action; the results of `view`, `edit`, `share`, or `manage_public` must not be used to infer that the source location or target location is writable.
2. Resources with `target_write_state=unknown|denied` must not enter the high / medium relevance executable grouping or the move plan.
3. Resources with `move_permission_state=unknown` by default do not enter content verification, the high / medium relevance grouping, or the move plan.
4. When `owner_scope=mine` but the resolved owner is not the current user, treat the resource as an anomalous candidate, set `source_move_state=unknown` and `move_permission_state=unknown`, and do not add it to the move plan.

<a id="状态content_verify"></a>
## State: `CONTENT_VERIFY`

Entry condition: the resource list is ready.

Must:

1. This state cannot be skipped, and must not be merged with `RESOURCE_RESOLVE` or `RELEVANCE_CLASSIFY`; it must still be executed when there are no resources whose body can be read.
2. Only read supported content after resource resolution.
3. Limit the read scope by count, size, and type capability.
4. Combine search evidence and content evidence; unless the title is exact and sufficiently strong, do not judge high relevance based on title alone.
5. Mark unreadable resources as `unverifiable` or `permission_denied`.
6. Do not automatically request permissions.
7. Write a verification status for each resource: content evidence read, search evidence only available, no permission, no move permission, move permission unknown, unable to verify, or content verification unsupported.
8. For resources with `move_permission_state=denied|unknown`, do not read the body content further; write the skip-verification reason and retain the recall evidence; writing the skip reason is part of executing this state and does not equal skipping this state.
9. After all resources have a verification status or skip reason, set `content_verify_completed` to `true` and output a verification summary.
10. Do not enter `RELEVANCE_CLASSIFY` before `content_verify_completed=true`.

<a id="验证方式"></a>
### Verification Methods

| Resource Type | Verification Method |
|---------------|---------------------|
| `docx` / `doc` | Use `docs +fetch --api-version v2` when allowed. |
| `sheet` | Use `sheets +cells-search` to look up keyword evidence, or use `sheets +cells-get` to read a bounded range. |
| `bitable` | Verify only when necessary and Base capability has been loaded. |
| `slides` | Unless slide reading capability is available, use metadata / preview / title evidence. |
| `file` | Use title, metadata, preview, or exported text only when supported. |
| `wiki` node | Verify the underlying object per `obj_type`; the node itself is not a content token. |
| `folder` | Unless the user explicitly wants to move the container, it is usually not moved as topic evidence. |

<a id="内容验证完成-ui"></a>
### Content Verification Complete UI

After completing `CONTENT_VERIFY`, you must output:

```text
Content verification complete:
- Content evidence read: N items
- Search evidence reused only: N items
- Skipped due to no permission or move eligibility: N items
- Unable to verify or verification unsupported: N items

The next step will perform relevance grouping based on the above evidence; no resources will be created or moved.
```

If no resource's body can be read, this summary must still be output, and it must clearly state the search evidence or skip reason adopted for all resources.

<a id="内容验证出口门禁"></a>
### Content Verification Exit Gate

After `CONTENT_VERIFY` completes, you must:

1. Confirm `content_verify_completed=true`, and that every `ResourceItem` already has a verification status or skip reason.
2. Set the next state to `RELEVANCE_CLASSIFY`.
3. Load [`lark-drive-workflow-topic-move-collector-review-plan.md`](lark-drive-workflow-topic-move-collector-review-plan.md).
4. Do not go directly to `PLAN_MOVE`.

## ResourceItem

```json
{
  "resource_id": "稳定资源 ID",
  "title": "资源标题",
  "resource_type": "doc|docx|sheet|bitable|file|folder|wiki|slides|shortcut",
  "url": "资源链接",
  "canonical_token": "标准资源 token",
  "wiki_node_token": "Wiki 节点 token",
  "wiki_obj_token": "Wiki 底层对象 token",
  "wiki_obj_type": "Wiki 底层对象类型",
  "space_id": "知识空间 ID",
  "current_parent_kind": "drive_folder|drive_root|wiki_node|wiki_space_root|unknown",
  "current_parent_token": "当前父级 token",
  "current_parent_space_id": "当前父级 Wiki space_id",
  "current_path": "用于展示的当前位置",
  "owner_id": "资源 owner open_id",
  "is_owner": "true|false|unknown",
  "permission_state": "readable|denied|unknown",
  "source_move_state": "confirmed|unknown|denied",
  "source_parent_write_state": "confirmed|unknown|denied|not_required",
  "move_permission_state": "movable|denied|unknown",
  "move_permission_basis": ["权限矩阵证据或阻塞原因"],
  "target_write_state": "confirmed|unknown|denied",
  "item_resolve_status": "resolved|partial|failed",
  "content_verify_state": "verified|search_evidence_only|skipped_by_move_permission|permission_denied|unverifiable|unsupported",
  "content_evidence": ["证据"],
  "relevance": "high|medium|low|permission_denied|no_move_permission|move_permission_unknown|unverifiable|unsupported_move_target"
}
```

| Field | Description |
|-------|------|
| `canonical_token` | The canonical token used for content reading, Drive object operations, or underlying object operations; this field must not be used for Wiki node moves. |
| `resource_id` | A stable ID generated during resource resolution, used to connect `ResourceItem` and `MovePlanItem`. |
| `wiki_node_token` | Wiki node identity, used for Wiki node moves. |
| `wiki_obj_token` | The real document token behind the Wiki node. |
| `current_parent_kind` / `current_parent_token` / `current_parent_space_id` | The structured pre-execution parent, used for `already_at_target` determination and recovery; unknown values must not be guessed. |
| `current_path` | The current location for user display only, and must not replace the parent token. |
| `owner_id` | Resource owner; for Drive resources it preferentially comes from `drive metas batch_query`, and for Wiki nodes it preferentially comes from `wiki +node-get`. |
| `is_owner` | Whether the current user is the resource owner. |
| `permission_state` | Read permission status under the current identity. |
| `source_move_state` | Whether the current identity is confirmed to be able to perform the selected `move_method` on the source resource; it must be determined per the permission matrix. |
| `source_parent_write_state` | Source location edit status required for in-Drive moves; non-`drive_move` is `not_required`. |
| `move_permission_state` | Permission matrix aggregation result; only when `movable` and the target write status is `confirmed` may it enter the default move chain. |
| `move_permission_basis` | The basis for the move eligibility determination, used to explain why it is included or excluded. |
| `target_write_state` | Whether the target location is confirmed writable. |
| `item_resolve_status` | Resource item resolution status; do not confuse it with `TargetLocation.target_resolve_status`. |
| `content_verify_state` | Content verification status or skip-verification reason. |
| `content_evidence` | Hit evidence supporting the relevance judgment. |
| `relevance` | Relevance and executability grouping. |
