<a id="lark-drive-权限治理-workflow"></a>
# lark-drive Permission Governance Workflow

Workflow id: `permission_governance`

Risk / Structure: `R2` / `S2`

This document implements the registered permission governance workflow. Before execution, you must first read [`lark-drive-workflow.md`](lark-drive-workflow.md) and [`../../shared/index.md`](../../shared/index.md), and follow the shared execution protocol, Artifact Contract, Workflow Loading, authentication, and write confirmation rules.

<a id="适用范围"></a>
## Scope

Use this workflow when the user requests checking or governing access permissions for Drive / Docs / Wiki assets. Typical intents include:

- Checking a single resource's public visibility, external access, company-internal link, and share / copy / download / comment settings.
- Permission risk diagnosis and permission setting checklists for multiple resources, Wiki space / node, Drive folder, or personal document library.
- Access review, low-activity high-exposure, permission requests, owner transfer, secure-label adjustment, AI Agent / RAG pre-permission governance.
- Read-only remediation dry-run, or confirmed permission tightening / permission requests / owner transfer / secure-label updates.

The target can be an explicit URL / token, a small explicit list, a Wiki space / Wiki node, or a Drive folder. Container scope must first be read-only `DISCOVER_TARGETS` and produce a coverage summary; "all documents" here only means documents enumerable by the current identity within the confirmed scope. Writes require authorization in the session for the actual target and permission scope; the same plan that has already been explicitly authorized is not confirmed again.

Single-target lightweight path: when the user only asks "is it publicly visible / externally accessible / visible via company-internal link" and the target is a single explicit URL / token, set `intent=public_exposure_check`, `target_scope=single_resource`, and take `PARSE_INTENT -> TARGET_INSPECT -> FACT_READ -> RISK_ASSESS -> DONE`. This path is the lightweight output mode of `target_count=1`, not independent judgment logic; it does not execute `DISCOVER_TARGETS` and does not generate `risk_manifest` / `risk_id`, and only outputs the conclusion, permission implications, check boundaries, and necessary next steps.

## Target Set Evaluation

This workflow does not replicate permission judgment logic by "single / multiple / container". All scopes are first normalized into a target set, then `per_target_permission_assessment` is generated for each auditable target, and finally output is aggregated by target count and risk grouping.

| target_scope | Target Collection | Output Mode |
|--------------|-------------------|-------------|
| `single_resource` | Directly resolve one URL / token | Lightweight rendering when `target_count=1`; does not generate `risk_manifest` |
| `explicit_list` | Inspect / normalize each URL / token provided by the user one by one | Render summary per target; generate stable `risk_id` when subsequent governance is needed |
| `wiki_space` / `wiki_node` / `drive_folder` | First read-only recursive discovery, then normalize into `discovered_targets` | Output coverage, risk grouping, locatable objects pending review, and artifact / dry-run CTA |

What is special is target collection and output aggregation, not permission semantics. Semantic fields such as `link_access`, `external_sharing`, `copy_scope`, `security_scope`, `comment_scope`, `sec_label`, `check_scope` must be reused across single-target, multi-target explicit lists, and container discovery targets.

<a id="非目标"></a>
## Non-Goals

This workflow does not handle:

- Directory organization, migration, archiving, or cleanup; such needs should use the knowledge organization workflow.
- Content review, stale content judgment, or knowledge quality scoring.
- Backup owner supplementation, department / project owner binding, collaborator creation / revocation, member list auditing; this workflow only supports transferring owner to a new owner explicitly specified for each target, and does not model backup owner or owner binding relationships.
- Auditing or fixing the folder's own public permissions. The folder's own permission settings can be read with `drive +permission-get-setting`; whether writes are supported must be based on the runtime schema and explicit requirements, and `patch type=folder` must not be guessed or executed.
- Complete discovery of invisible documents that the current identity cannot enumerate; only already-discovered targets or URLs / tokens explicitly provided by the user can be handled.
- Batch writes not confirmed by scope.

Collaborator list reading only covers the current target's direct collaborators / authorized members: `drive +member-list` may be used.

## Progressive Load Map

This table only specifies the additional context that needs to be loaded for each state; the available command scope is governed by `Command Map`. When specific `lark-cli` commands need to be assembled, read [`lark-drive-workflow-permission-governance-commands.md`](lark-drive-workflow-permission-governance-commands.md) on demand.

| State | Required Reference |
|-------|--------------------|
| `PARSE_INTENT` | This file, [`lark-drive-workflow.md`](lark-drive-workflow.md), [`../../shared/index.md`](../../shared/index.md) |
| `TARGET_INSPECT` | [`lark-drive-inspect.md`](lark-drive-inspect.md) |
| `DISCOVER_TARGETS` | For container scope, read [`../../wiki/references/lark-wiki-node-list.md`](../../wiki/references/lark-wiki-node-list.md) or [`lark-drive-files-list.md`](lark-drive-files-list.md) |
| `FACT_READ` | `lark-cli schema drive.metas.batch_query`; use `drive +permission-get-setting` when permission setting reading is involved; read `lark-cli schema drive.file.statistics.get` and `lark-cli schema drive.file.view_records.list` when activity, access review, or lifecycle judgment is involved |
| `RISK_ASSESS` | `Risk Classification` of this file |
| `EXEC_CONFIRM` | Read [`lark-drive-apply-permission.md`](lark-drive-apply-permission.md), [`lark-drive-secure-label.md`](lark-drive-secure-label.md), or `lark-cli schema drive.permission.public.patch` / `lark-cli schema drive.permission.members.transfer_owner` only for the action selected by the user; read [`lark-drive-workflow-permission-governance-outputs.md`](lark-drive-workflow-permission-governance-outputs.md) when a confirmation template is needed |
| `EXECUTE` | Reuse the write command context already loaded and confirmed by `EXEC_CONFIRM` |
| `VERIFY` | Reuse the read schemas used in the `FACT_READ` phase |

## Runtime State Extension

This workflow extends the following field groups on top of the shared `Artifact Contract`:

| Group | Fields | Meaning |
|-------|--------|---------|
| Scope | `intent`, `target_scope`, `targets`, `discovered_targets`, `coverage_summary`, `discovery_blockers` | Record user intent, confirmed scope, direct targets, container discovery targets, and uncovered scope |
| Facts | `metadata_facts`, `public_permission_facts`, `activity_facts`, `manage_public_auth` | Record metadata, public access and collaboration permissions, access evidence, and pre-write `manage_public` validation |
| Assessment | `per_target_permission_assessments`, `risk_findings`, `unsupported_checks` | Record per-target semantic judgment, risk findings with `risk_id` / URL / owner / sec_label / evidence / action, and checks that cannot be executed |
| Governance | `risk_manifest`, `selected_risk_items`, `access_review_items`, `permission_request_candidates`, `owner_transfer_candidates` | Support the user selecting governance scope by `risk_id`, risk grouping, owner, path, URL, or artifact `selected=true`, and record owner transfer candidates |
| Execution | `remediation_plan`, `owner_transfer_plan`, `public_permission_snapshots` | Record dry-run / confirmed remediation plan, owner transfer plan, field diff, verification method, and limited public-permission rollback snapshot |

## Execution State Machine

| State | Protocol Step | Agent MUST Do | User-Facing Output | wait_for_user | Next State |
|-------|---------------|---------------|--------------------|---------------|------------|
| `PARSE_INTENT` | `route` / `scope` | Parse intent, target scope, desired policy, and whether it is read-only audit, single-target public visibility judgment, permission request, owner transfer, or remediation mode; single-target public visibility judgment sets `intent=public_exposure_check`, `target_scope=single_resource` | Scope confirmation; if target, new owner, or desired action is missing, ask only one clarifying question | `true` when target / new owner / action is missing, or when container scope needs user confirmation | `TARGET_INSPECT` |
| `TARGET_INSPECT` | `scope` | Parse single resource, explicit list, Wiki space / node, Drive folder; Drive folder is parsed directly from the URL path or explicit `type=folder`, without calling `drive +inspect`; preserve the original URL, scope type, canonical token/type | Target scope table, including scope, title/type/token status | `false` unless parsing fails | `DISCOVER_TARGETS` or `FACT_READ` |
| `DISCOVER_TARGETS` | `scope` / `read` | Recursively read-only enumerate Wiki space / node or Drive folder, normalize into `discovered_targets`; record `discovery_blockers` | Discovery progress and coverage summary; do not display internal cursor/token unless the user requests it | `false` unless the discovery scope cannot be confirmed or all is blocked | `FACT_READ` |
| `FACT_READ` | `read` | Execute `drive metas batch_query` on direct targets or `discovered_targets`; execute `drive +permission-get-setting` to read their own permission settings for supported files, folders, or cloud document targets; when `intent=public_exposure_check` and `target_scope=single_resource`, reuse the title / URL / type returned by `drive +inspect` and only additionally read the target's public access and collaboration permission settings; read access statistics and access records when the user requests activity / access review / lifecycle judgment | Permission facts summary, coverage summary, activity facts, and unsupported checks | `false` unless all targets are blocked by auth | `RISK_ASSESS` |
| `RISK_ASSESS` | `assess/plan` | Generate `per_target_permission_assessment` for each auditable target and classify evidence; if the user provides a policy, compare against the policy; `public_exposure_check + single_resource` only renders the single-target conclusion and does not generate `risk_id`; the owner transfer path generates `owner_transfer_candidates` / `owner_transfer_plan`; the governance path builds a locatable risk list, access review list, dry-run remediation plan, or candidate remediation plan, and a complete list must generate a stable `risk_id` | Findings with priority, URL, risk_id, owner, sec_label, confidence, review items, suggested actions, and next-step CTA; single-target public visibility judgment only outputs the conclusion and key fields | `true` for the governance path, `false` for single-target public visibility judgment | `EXEC_CONFIRM` or `DONE` |
| `EXEC_CONFIRM` | `confirm` | Display the exact write scope, command family, target count, risk, verification method | Confirmation request | `true` | `EXECUTE` or `DONE` |
| `EXECUTE` | `execute` | Execute only the writes already confirmed in `Command Map` | Progress / result summary | `false` unless blocked | `VERIFY` |
| `VERIFY` | `verify` | Re-execute supported reads and compare with the target state | Verification table and remaining gaps | `false` | `DONE` |
| `DONE` | `done` | Stop | Final reply, including completed items, verification results, and remaining risks | `false` | End |

## Command Map

This workflow may only use the following command families:

| State | Allowed Command Families | Purpose |
|-------|--------------------------|---------|
| `TARGET_INSPECT` | `drive +inspect` | Resolve non-folder URL, type, canonical token, title, and wiki unwrap data; Drive folder does not support `+inspect` and must be parsed directly from the URL path or explicit `type=folder` |
| `DISCOVER_TARGETS` | `wiki +node-list` | Recursively discover nodes visible to the current identity under a Wiki space / node |
| `DISCOVER_TARGETS` | `drive files list` | Recursively discover files and subfolders visible to the current identity under a Drive folder |
| `FACT_READ` | `drive metas batch_query` | Read title, URL, owner, and secure-label metadata |
| `FACT_READ` | `drive permission.public get` | Read public access and collaboration permission settings for supported document types, including link sharing, external sharing, collaborator management, copy content, create copy, print, download, and comment |
| `FACT_READ` | `drive +member-list` | Read the single-target direct collaborator / authorized member list explicitly requested by the user; does not represent the complete inheritance chain or historical permission audit |
| `FACT_READ` | `drive +permission-get-setting` | Read the permission settings of supported file, folder, or cloud document types themselves, including public access, sharing, collaborator management, security, and comments |
| `FACT_READ` | `drive file.statistics get` | Read file access statistics when the user requests activity, idle exposure, lifecycle, or access review |
| `FACT_READ` | `drive file.view_records list` | Read access records when the user requests recent visitors, access review, or low-activity evidence |
| `EXEC_CONFIRM` | `drive +secure-label-list` | Resolve available secure-label IDs before proposing a label update |
| `EXEC_CONFIRM` | `drive permission.members auth` | Check `action=manage_public` before modifying target public access and collaboration permission settings |
| `EXEC_CONFIRM` | `lark-cli schema drive.permission.members.transfer_owner` | Read current fields, supported types, and high-risk write gates before owner transfer |
| `EXECUTE` | `drive +apply-permission` | Submit a view/edit access request to the owner; only single-target, small lists, or explicitly confirmed candidate lists may be executed one by one |
| `EXECUTE` | `drive permission.public patch` | Modify confirmed public/link settings; `--yes` must be passed |
| `EXECUTE` | `drive permission.members transfer_owner` | Transfer the owner of confirmed targets; `--yes` must be passed |
| `EXECUTE` | `drive +secure-label-update` | Set the confirmed secure-label ID |
| `VERIFY` | `drive metas batch_query`, `drive +permission-get-setting` | Verify supported metadata, including owner, secure-label, and target public access and collaboration permission setting changes; permission requests can only be stated as initiated |

## Command Patterns

This entry point does not inline command examples. When specific `lark-cli` commands need to be assembled, read [`lark-drive-workflow-permission-governance-commands.md`](lark-drive-workflow-permission-governance-commands.md) according to the current state. Whether a command is allowed to execute is still governed by `Command Map` and the write rules.

## Discovery Rules

Container scope can only perform read-only discovery and coverage summary first, and must not execute permission requests, permission patches, or secure-label updates during the discovery phase.

General rules:

1. "All documents" only means documents enumerable by the current identity within the confirmed scope. Parts that are invisible, unauthorized, not returned by the API, or beyond the tool budget must enter `discovery_blockers` or `unsupported_checks`.
2. The discovery phase must generate a stable `path`. Do not save only the title; documents with the same name must be distinguishable by path or token.
3. Permission setting reading uses `drive +permission-get-setting`, and target types include `doc`, `sheet`, `file`, `wiki`, `bitable`, `docx`, `mindnote`, `minutes`, `slides`, `folder`, `apps`; future new types are governed by shortcut and OpenAPI metadata.
4. `minutes` can only serve as a `partial_public_permission` target: the ability to read / modify public permissions and transfer owner is governed by the runtime schema, but `drive metas batch_query` currently does not support `minutes`, and metadata such as URL, owner, and secure-label may enter `unsupported_checks`.
5. When `folder` is used as a recursive container, enumerate sub-resources first; if the user explicitly wants to query the folder's own permission settings, `drive +permission-get-setting --token <folder_token> --type folder` may be executed separately on that folder. Do not execute raw `permission.public patch type=folder` unless both the schema and the requirement explicitly support it. `shortcut`, `catalog`, or entries lacking a stable token/type must be recorded as unsupported, unless a subsequent API explicitly resolves them into supported targets.
6. When outputting progress for large-scope targets, only display the number of containers scanned, targets discovered, targets audited, and remaining queue or blockers; do not display internal page token / cursor by default.

Wiki space / node discovery:

1. `/wiki/space/<space_id>` is parsed directly as `target_scope=wiki_space`. Do not stop just because `drive +inspect` returns not found for that URL.
2. Use `wiki +node-list --space-id <space_id>` to read the root node; when the node `has_child=true`, use that node's `node_token` to continue recursively reading child nodes.
3. Wiki nodes must preserve `node_token`, `obj_token`, and `obj_type` at the same time. For permission reading, prefer `type=wiki` + `node_token` to express Wiki node permissions; for metadata supplementation, `obj_type` + `obj_token` may be used.
4. If a node only has `obj_token` / `obj_type`, but the Wiki node permission token cannot be confirmed, keep that target as partial and explain in `unsupported_checks` that only the underlying object can be read or the Wiki node permission cannot be fully judged.

Drive folder discovery:

1. `/drive/folder/<folder_token>` resolves to `target_scope=drive_folder`. By default, continue enumerating its sub-documents; only when the user explicitly requests the folder's own permission settings, additionally call `drive +permission-get-setting --token <folder_token> --type folder` to read the folder's own settings.
2. Recursively process `data.files`, `has_more`, and `next_page_token` according to [`lark-drive-files-list.md`](lark-drive-files-list.md). Do not treat the first page count as the complete scope.
3. Only continue recursing on `folder` in the returned items; normalize sub-documents to `discovered_targets` by `type + token`.
4. If a directory pagination fails, has no continuation token, has insufficient permissions, or the API errors, only block that directory branch and record it in `discovery_blockers`; continue processing other enumerable branches.

## Fact Read Rules

1. `drive metas batch_query` reads at most 200 `request_docs` per call; when `targets` or `discovered_targets` exceeds 200, you must read in batches and merge the results.
2. `drive +permission-get-setting` has no batch read interface; read each supported target individually. When a single target fails, record `unsupported_checks` or `partial`, and do not block other targets.
3. For Wiki discovery targets, prefer `type=wiki` + `node_token` for public permission reads; for metadata, you may use `obj_type` + `obj_token` to supplement title, owner, URL, and `sec_label_name`.
4. When the intent is `list_permission_settings`, only output the permission settings list and coverage limitations; do not proactively generate a remediation plan.
5. Single-target, explicit multi-target list, and container discovery targets must all reuse the same per-target fact reading and semantic normalization logic; the differences only appear in target source, coverage summary, and output aggregation.
6. The user-visible meaning of `permission_public` is "target public access and collaboration permission settings"; the semantics are based on the official OpenAPI field descriptions, while also being compatible with the fields returned by the current CLI schema: prefer `external_access_entity`, and only when it is missing use the `external_access` boolean mapped to `open` / `closed`; when fields such as `manage_collaborator_entity`, `copy_entity`, `lock_switch` are missing, mark them as unknown, do not fabricate; unrecognized fields are retained in raw evidence / partial note.
7. `drive file.statistics get` and `drive file.view_records list` are only executed when the user requests recent access, activity level, idle exposure, access review, or when the policy provided by the user explicitly depends on activity level; do not read access records by default for ordinary permission audits.
8. Access statistics / access records are currently only handled as supported types for `doc`, `docx`, `sheet`, `bitable`, `mindnote`, `wiki`, `file`. Other types must go into `unsupported_checks`, and activity level must not be inferred.
9. `view_records` is access evidence, not a permission list. When no access records are returned, it can only be stated as "no recent access evidence obtained" or "low-activity candidate", and must not be stated as "no one has permission".

## Risk Classification

Risk labels can only serve as evidence labels. Unless the user provides an explicit policy, do not state them as absolute violations, confirmed leaks, or confirmed external access.

The default priority is oriented toward user decision-making, not creating a sense of alarm:

- `P0`: `link_share_entity=anyone_readable/anyone_editable`, candidate risk of internet-public links.
- `P1`: `external_access_entity=open` / `external_access=true`, affiliated organization access, company-internal link editable, or external sharing with missing / below-policy sensitivity labels.
- `P2`: company-internal anyone-with-link can read, collaborator management scope is relatively broad.
- `PolicyReview`: settings such as copy, create copy, print, download, comment that depend on policy; when there is no explicit policy, do not call them high risk.
- `Unknown`: read failure, deleted, no permission, API unsupported, collaborator list / inheritance chain / DLP / AI index / audit log not covered.

Every auditable target must first be normalized to `per_target_permission_assessment`, then rendered according to `Semantic Rendering` in [`lark-drive-workflow-permission-governance-outputs.md`](lark-drive-workflow-permission-governance-outputs.md). `public_exposure_check` is only a lightweight rendering mode of `target_count=1`; it reuses the same set of semantic fields and risk classification as multi-target and container diagnostics. This judgment only covers the current target's public access and collaboration permission settings, and does not audit collaborator lists, historical permission changes, complete inheritance chains, or audit logs.

`AI 检索暴露候选风险` is only a proxy label based on permissions and labels. Unless another tool explicitly returns index status, do not claim that a document has been indexed by an Agent, Copilot, or RAG.

<a id="写入规则"></a>
## Write Rules

- Modifying target public access and collaboration permission settings (`drive permission.public patch`) is a high-risk write. Before requesting confirmation, you must show the target title, token, current setting, desired setting, and exact field changes.
- If `manage_public_auth.auth_result=false`, patching is prohibited. Tell the user that a user with manage-public permission is required, or that the owner must perform the operation.
- Permission setting reads use `drive +permission-get-setting`; a bare token must be passed as `--type`, while a URL can be inferred automatically. Writes still use `drive permission.public patch`, and only patch types and fields that have been resolved and are explicitly supported by the schema; do not automatically extrapolate `folder` supported for reads as writable.
- Do not patch fields not supported by the resolved type. For wiki targets, you must omit fields that the schema explicitly marks as unsupported for wiki.
- The plan must separately list changes to sensitivity labels and public access/collaboration permissions; the user can authorize the complete plan at once, with no need to split the same plan into repeated inquiries.
- `drive +apply-permission` is not executed in batches by default; each call sends a notification to the owner.
- `permission_request_candidates` can come from targets directly provided by the user, an explicit list, or container discovery targets; as long as a token, type, permission type, and request reason can be constructed, it can enter the candidate set. Do not reject a single-target / small-list permission request just because the target is not in `discovered_targets`.
- "Unified permission request" within a container scope must first produce `permission_request_candidates`. Before showing the candidate targets, count, permission types, and owner notification impact, calling `drive +apply-permission` is prohibited.
- After the user explicitly confirms a batch permission request, you must still call `drive +apply-permission` sequentially target by target, and in the results distinguish between requests initiated, failures, requests that could not be constructed, and targets not found.
- `drive permission.members transfer_owner` is a high-risk owner transfer write. You must first confirm the target, current owner, new owner's `member_id` / `member_type`, `need_notification`, `remove_old_owner`, `old_owner_perm`, `stay_put`, execution order, and verification method; do not guess the new owner from name alone.
- Owner transfer has no equivalent precheck to `permission.members auth`. Before execution, you can only plan using the schema and current metadata; after execution, you must verify the owner with a `drive metas batch_query` fresh read; for types not supported by metadata, the verification must be marked as partial.
- Batch owner transfer must be executed sequentially one by one; failed items go into the result list, and do not re-execute targets that already succeeded. Downgrades of `remove_old_owner=true` or `old_owner_perm` must be highlighted separately in the confirmation.
- When the user requests "generate a remediation plan / dry-run / first see what would change", only generate `remediation_plan`, and do not execute any write commands. The dry-run must include target count, field changes, skip reasons, verification method, and limited rollback scope.
- When the user selects objects based on a complete risk list, you must first resolve `risk_id`, risk groups, URLs, or the lines of `selected=true` in the artifact, and generate `selected_risk_items`. Selections that cannot be matched to the current `risk_manifest` must require the user to reconfirm or re-read the list.
- Before generating a dry-run for `selected_risk_items`, you must re-read the `drive +permission-get-setting` of the selected targets; if the current settings differ from the list snapshot, mark it as `changed_since_report` and skip or require the user to confirm the updated plan.
- Before executing `drive permission.public patch`, you must save the fields that will be changed in the current `public_permission_facts` as `public_permission_snapshots`. This snapshot is only used for limited rollback instructions for target public access and collaboration permission setting fields, and does not cover collaborators, owner, inherited permissions, or sensitivity labels.
- If the user requests batch permission tightening, you must execute sequentially one by one according to risk tier and target order; failed items go into the result list, and do not re-execute targets that already succeeded because of a single failure.
- When encountering secure-label downgrade error `1063013`, stop retrying and tell the user that approval must be completed in the document UI.

<a id="未来扩展边界"></a>
## Future Extension Boundaries

The following capabilities already have partial CLI surface or user value, but must not be directly called as executable branches in the current workflow:

- `drive permission.members create` can create collaborator permissions, but the current workflow does not perform collaborator grant / update / revoke; in the future, authorization object resolution, least privilege, confirmation templates, and verification methods need to be defined separately.
- backup owner and department / project owner binding have no executable write surface in the current workflow; if the user wants to implement them as owner transfer, an explicit target and new owner must first be provided, and the owner-transfer confirmation of this workflow must be followed.
- `wiki +member-list` can serve as a read-side source of truth for Wiki space member governance; the current workflow only governs permissions of discoverable documents under documents / nodes / folders, and does not perform space member governance.
- `drive +member-list` can read direct collaborators/authorized members of a single target; the current CLI still lacks complete inheritance chains, DLP scans, AI index status, audit logs, and cross-platform permission facts. When encountering these needs, they must be recorded as `unsupported_checks` or a new independent workflow must be suggested.

<a id="输出策略"></a>
## Output Strategy

- Default summary-first: single-target outputs a brief audit summary; explicit multi-target list outputs a per-target summary; container target outputs a security diagnostic report summary, without stacking field counts.
- Single-target `public_exposure_check` renders `per_target_permission_assessment` according to the `Semantic Rendering` of outputs, outputting user-language conclusions and inspection boundaries; by default, do not show underlying field names, risk lists, or remediation CTAs.
- Container security diagnostics must include a one-sentence conclusion, coverage status, risk grading, locatable objects pending review, recommended next steps, and remaining limitations.
- Objects pending review must include a stable `risk_id`, path/title, URL, type, owner, sec_label, risk reason, evidence, and recommended action; when URL is missing, show token / node_token and the reason.
- Container summaries use progressive disclosure by scale, and must not use a fixed Top N; when not fully expanded, you must state the total count of the complete list and provide CTAs such as generating an artifact / dry-run / owner review list.
- For user-facing output, prefer business language and "candidate risk / pending review / pending policy confirmation"; underlying fields serve only as evidence. Read the complete template on demand from [`lark-drive-workflow-permission-governance-outputs.md`](lark-drive-workflow-permission-governance-outputs.md).
- Do not create files, Feishu documents, or long tables by default; the final reply must include completed items, verification results, and remaining limitations. Asynchronous permission request approvals can only be stated as "request initiated".
