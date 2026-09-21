<a id="权限治理输出模板"></a>
# Permission Governance Output Templates

This document only provides the user-visible output templates for the `permission_governance` workflow. By default, give a brief summary first; only read this document when the user requests a full table, when write confirmation is needed, or when the results are large enough to require structured presentation.

<a id="目录"></a>
## Table of Contents

- `输出策略`
- `Semantic Rendering`
- `定位与治理动作`
- `单目标公开性判断`
- `多目标明确列表诊断`
- `审计摘要`
- `容器安全诊断报告摘要`
- `可操作风险清单`
- `治理选择交互`
- `权限设置清单`
- `访问复核清单`
- `整改 dry-run`
- `批量权限申请确认`
- `owner 转移确认`
- `确认请求`
- `最终摘要`

<a id="输出策略"></a>
## Output Strategy

- For a single target, output an audit summary by default.
- For an explicit list of multiple targets, output a per-target diagnostic summary by default; do not apply the container recursive discovery report just because the number of targets is greater than 1.
- User-visible conclusions follow the user's current language by default. When the user asks in Chinese, output Chinese; when the user asks in English, output English; for mixed languages, follow the primary language.
- For single-target public-access judgment, output business phrasing by default, and do not directly show underlying field names such as `link_share_entity`, `external_access_entity`, `external_access`; only show underlying fields when the user requests raw evidence, troubleshooting, or a full list / artifact scenario.
- In Chinese user-visible output, `permission_public` / `public permission` is translated by default as "target public access and collaboration permission settings"; it may be abbreviated in the summary as "public access and collaboration settings". Prefer interpreting public access, sharing, collaborator management, security, and comment settings according to the actual returned fields; fields such as copy content, create copy, print, and download can only be judged when the current CLI schema and the actual response return them. Only command names, schema fields, raw evidence, troubleshooting information, and full artifact field names retain the original English.
- For container targets, output a security diagnostic report summary by default: a one-sentence conclusion, coverage, risk grading, priority objects to handle, recommended next steps, and remaining limitations.
- For container targets, do not mechanically sort risks by count; external public access, external sharing allowed, and missing security labels take priority over policy-dependent candidates such as copy / download / comment.
- When the user has not provided an explicit policy, use "candidate risk / pending review / pending policy confirmation", and do not write "violation / leaked / externally accessed".
- In container security diagnostics, do not abbreviate `external_access=true` / `external_access_entity=open` as "high risk" or "external leak"; the user-visible phrasing should be "external sharing is allowed and requires owner review; this does not mean external collaborators already exist".
- Risk object presentation follows progressive disclosure by scale: 1-10 objects are all shown; 11-30 objects show all high-priority pending-review objects, with medium / low priority only as grouped summaries; 31-100 objects show Top 5 and counts grouped by high-priority pending review; 100+ objects show only grouped statistics and Top samples.
- When the summary does not show all risk objects, it must clearly state "the full list contains <count> items" and provide next steps to generate a Markdown / CSV / Feishu document risk list or a remediation dry-run.
- As long as objects requiring handling are found, the final reply must give an executable next-step CTA. Do not end after only reporting risks just because the default is read-only.
- The full risk list is the input for subsequent governance choices; Markdown / CSV / Feishu document reports must use the same set of fields and a stable `risk_id`.
- Before writing, the confirmation template must be used; separately list the changes to permission requests, public access / collaboration permissions, owner, and security labels; the same explicit plan may be authorized in one go.
- The final reply must include completed items, verification results, and remaining limitations; asynchronous permission request approvals must not be described as completed authorization.

## Semantic Rendering

For user-facing main conclusions, render the semantic state in `per_target_permission_assessment` first, and use the user's current language; underlying field names are retained only in raw evidence, troubleshooting, or full lists. The table below gives the standard mapping from field values to business phrasing; other languages should express the equivalent business meaning.

Field source boundary: the table below covers both official OpenAPI semantics and the current / future CLI schema. Only fields and values returned by the actual response or the current schema may be rendered as definite states; fields not returned by the currently installed CLI (for example `copy_entity`, `manage_collaborator_entity`, `external_access_entity`) or enum values that do not appear may only be used when they actually appear in the raw response / schema, and when missing they must be treated as unknown / unsupported, without fabricating.

| Raw field / value | Semantic State | Chinese phrasing | English phrasing |
|-------------------|----------------|----------|------------------|
| `link_share_entity=anyone_readable` | `link_access=public_readable` | Anyone on the internet with the link can read | Anyone on the internet with the link can read |
| `link_share_entity=anyone_editable` | `link_access=public_editable` | Anyone on the internet with the link can edit | Anyone on the internet with the link can edit |
| `link_share_entity=partner_tenant_readable` | `link_access=partner_readable` | People in partner tenants with the link can read | People in partner tenants with the link can read |
| `link_share_entity=partner_tenant_editable` | `link_access=partner_editable` | People in partner tenants with the link can edit | People in partner tenants with the link can edit |
| `link_share_entity=tenant_readable` | `link_access=tenant_readable` | People in the tenant with the link can read | People in the tenant with the link can read |
| `link_share_entity=tenant_editable` | `link_access=tenant_editable` | People in the tenant with the link can edit | People in the tenant with the link can edit |
| link sharing empty / disabled | `link_access=closed` | Link sharing is disabled | Link sharing is disabled |
| `external_access_entity=open` or `external_access=true` | `external_sharing=open` | External sharing is open; this does not mean external collaborators already exist | External sharing is open; this does not mean external collaborators already exist |
| `external_access_entity=allow_share_partner_tenant` | `external_sharing=partner_only` | Sharing is allowed only with partner tenants | Sharing is allowed only with partner tenants |
| `external_access_entity=closed` or `external_access=false` | `external_sharing=closed` | External sharing is disabled | External sharing is disabled |
| `invite_external=true` | `external_invitation=enabled` | Inviting external users is enabled | Inviting external users is enabled |
| `invite_external=false` | `external_invitation=disabled` | Inviting external users is disabled | Inviting external users is disabled |
| `share_entity=anyone` | `collaborator_org_scope=all_viewers_or_editors` | All viewers or editors can view, add, and remove collaborators | All viewers or editors can view, add, and remove collaborators |
| `share_entity=same_tenant` | `collaborator_org_scope=tenant_viewers_or_editors` | Tenant viewers or editors can view, add, and remove collaborators | Tenant viewers or editors can view, add, and remove collaborators |
| `manage_collaborator_entity=collaborator_can_view` | `collaborator_permission_scope=viewer` | Collaborators with view permission can view, add, and remove collaborators | Collaborators with view permission can view, add, and remove collaborators |
| `manage_collaborator_entity=collaborator_can_edit` | `collaborator_permission_scope=editor` | Collaborators with edit permission can view, add, and remove collaborators | Collaborators with edit permission can view, add, and remove collaborators |
| `manage_collaborator_entity=collaborator_full_access` | `collaborator_permission_scope=full_access` | Collaborators with full-access permission can view, add, and remove collaborators | Collaborators with full-access permission can view, add, and remove collaborators |
| `copy_entity=anyone_can_view` | `copy_scope=viewer` | Users with view permission can copy content | Users with view permission can copy content |
| `copy_entity=anyone_can_edit` | `copy_scope=editor` | Users with edit permission can copy content | Users with edit permission can copy content |
| `copy_entity=only_full_access` | `copy_scope=full_access` | Only collaborators with full-access permission can copy content | Only collaborators with full-access permission can copy content |
| `security_entity=anyone_can_view` | `security_scope=viewer` | Users with view permission can create copies, print, and download | Users with view permission can create copies, print, and download |
| `security_entity=anyone_can_edit` | `security_scope=editor` | Users with edit permission can create copies, print, and download | Users with edit permission can create copies, print, and download |
| `security_entity=only_full_access` | `security_scope=full_access` | Only users with full-access permission can create copies, print, and download | Only users with full-access permission can create copies, print, and download |
| `comment_entity=anyone_can_view` | `comment_scope=viewer` | Users with view permission can comment | Users with view permission can comment |
| `comment_entity=anyone_can_edit` | `comment_scope=editor` | Users with edit permission can comment | Users with edit permission can comment |
| `lock_switch=true` | `lock_state=locked_not_inheriting` | The node is locked and no longer inherits parent-page permissions | The node is locked and no longer inherits parent-page permissions |
| `lock_switch=false` | `lock_state=not_locked_or_inheriting` | The node is not locked and may inherit parent-page permissions | The node is not locked and may inherit parent-page permissions |
| field absent / unsupported | `<state>=unknown` | The current schema did not return this field, so it is unknown | The current schema did not return this field, so it is unknown |
| `check_scope=current_public_permission_only` | `check_scope=current_public_permission_only` | This check covers the target's current public access and collaboration settings, not collaborator-list or historical permission-change auditing | This check covers the target's current public access and collaboration settings, not collaborator-list or historical permission-change auditing |
| `sec_label_name` missing | `sec_label=missing` | Security label is missing | Security label is missing |

<a id="定位与治理动作"></a>
## Locating and Governance Actions

Risk objects must allow the user to directly locate and handle them:

- Each priority object to handle in the summary must include `risk_id`, `path/title`, `URL`, `type`, owner, sec_label, risk reason, key evidence, and recommended action.
- The full list, access review list, remediation dry-run, and write confirmation must all include the URL. When the URL is missing, show the token / node_token and explain that the URL could not be obtained.
- Documents with the same name, shortcuts, or copies must be distinguished by path + URL; do not output only the title.
- Each record in the full risk list must have a stable `risk_id`, in the format `PG-001`, `PG-002`. `risk_id` remains unchanged across the same diagnosis and subsequent dry-run / confirmation / verification.
- Even if the summary only shows Top samples, stable `risk_id` must be assigned to the samples; do not output a title list that cannot be selected.
- Recommended actions must be bound to the risk type: for internet-public links, prioritize recommending disabling link sharing or tightening it to within the tenant; for external sharing allowed, prioritize recommending owner review or disabling external sharing; for missing security labels, prioritize recommending completing the security label; for copy / download / comment scope, only recommend tightening when the user's policy is explicit.
- Write actions may only appear as next-step options or confirmation requests. Do not imply in the diagnostic summary that permission reduction has already been executed.

<a id="单目标公开性判断"></a>
## Single-Target Public-Access Judgment

Use this template when `intent=public_exposure_check` and `target_scope=single_resource`. By default, render `target_count=1`'s `per_target_permission_assessment`, following the user's current language, without directly showing underlying field names; when the user requests raw evidence, append the field evidence.

Chinese template:

```text
Conclusion: <not publicly external / internet public link exists / external sharing allowed>.

Target: <title>
URL: <url-or-token-if-url-unavailable>
Type: <type>

Current link access scope: <render link_access>
External sharing: <render external_sharing>
External invitation: <render external_invitation or omit if unknown because field is absent>
Collaborator management (tenant dimension): <render collaborator_org_scope>
Collaborator management (permission dimension): <render collaborator_permission_scope or omit if unknown because field is absent>
Copy content: <render copy_scope or omit if unknown because field is absent>
Create copy / print / download: <render security_scope>
Comment: <render comment_scope>
Wiki inheritance restriction: <render lock_state or omit if unknown because field is absent>

Check boundary: <render check_scope>
```

English template:

```text
Conclusion: <Not publicly accessible on the internet / A public internet link is enabled / External sharing is enabled>.

Target: <title>
URL: <url-or-token-if-url-unavailable>
Type: <type>

Current link access: <render link_access>
External sharing: <render external_sharing>
External invitations: <render external_invitation or omit if unknown because field is absent>
Collaborator management by tenant: <render collaborator_org_scope>
Collaborator management by permission: <render collaborator_permission_scope or omit if unknown because field is absent>
Copy content: <render copy_scope or omit if unknown because field is absent>
Create copies / print / download: <render security_scope>
Comments: <render comment_scope>
Wiki inheritance lock: <render lock_state or omit if unknown because field is absent>

Check boundary: <render check_scope>
```

Raw evidence, only when requested:

```text
Evidence fields:
- link_share_entity=<value>
- external_access_entity=<value>
- external_access=<value>
- invite_external=<value>
- share_entity=<value>
- manage_collaborator_entity=<value>
- copy_entity=<value>
- security_entity=<value>
- comment_entity=<value>
- lock_switch=<value>
```

<a id="多目标明确列表诊断"></a>
## Multi-Target Explicit List Diagnosis

Use this template when `target_scope=explicit_list`. This scenario does not perform container recursive discovery; for each URL / token provided by the user, generate `per_target_permission_assessment` one by one, then aggregate by risk group. Permission semantics are fully reused from single-target and container diagnostics, with no new judgment model added.

```text
Completed the read-only permission diagnosis, without making any permission changes.

One-sentence conclusion: among <N> targets, <risk_count> have pending-review permission risks; <internet_public_count> have internet-public link candidates, <external_access_count> allow external sharing, and <unknown_count> cannot be fully judged.

Coverage:
- User-provided targets: <input_target_count>; successfully resolved: <resolved_count>
- Successfully read target public access and collaboration permission settings: <permission_checked_count>; read failed / unsupported / no permission: <failed_or_unsupported_count>

Per-target results (1-10 targets are all shown by default; when more than 10, show by `摘要清单展开规则` and prompt to generate a full risk list):

- <risk_id-or-item_id> <path-or-title> (<type>)
  URL: <url-or-token-if-url-unavailable>
  Conclusion: <not_public / public_link_enabled / external_sharing_enabled / policy_review / unknown>
  Key permissions: <render link_access>; <render external_sharing>; <render security_scope>; <render comment_scope>
  Security label: <sec_label_name-or-missing-or-unknown>
  Pending-review reason: <risk reason or none>
  Recommended action: <recommended action or no action>

Grouped summary:
- Internet-public link candidates: <count>; external sharing allowed: <count>; tenant link accessible / editable: <count>
- Copy / download / print / comment pending policy confirmation: <count>; cannot judge: <count and reason summary>

Recommended next steps:
- For explicit <risk_id>, first generate a read-only dry-run.
- Generate a full risk list artifact; subsequently, the governance scope can be selected by `risk_id`, risk group, URL, or `selected=true`; when only looking at permission settings, use `权限设置清单` instead.
```

<a id="摘要清单展开规则"></a>
## Summary List Expansion Rules

The container security diagnostic summary must balance readability and governability. Do not replace an actionable list with a fixed Top N.

| Number of risk objects | Default summary display | Next step that must be provided |
|------------|--------------|------------------|
| `0` | Show only coverage, uncovered capabilities, and remaining limitations | If a more detailed audit is needed, a permission settings list can be generated |
| `1-10` | Show all risk objects | A dry-run or write confirmation can be generated directly by `risk_id` |
| `11-30` | Show all high-priority pending-review objects; medium / low priority as grouped summaries | Generate a full risk list artifact, or generate a dry-run by risk group |
| `31-100` | For each high-priority pending-review group, show Top 5 with the number not shown | Generate a full Markdown / CSV / Feishu document risk list |
| `100+` | Show only grouped statistics, Top samples, and coverage limitations, without inlining long tables | Strongly recommend generating a structured risk list before selecting the governance scope |

High-priority pending-review objects include: internet-public links, external sharing allowed, external sharing allowed with missing / below-policy security labels, and tenant-editable links. A broad collaborator management scope is classified as medium-priority pending review by default; only when the user's policy explicitly requires strict collaborator management should the priority be raised. Copy / download / print and comment scope are classified as "pending policy confirmation" when the user has not provided an explicit policy, and must not crowd out the high-priority list.

Each pending-review object in the summary must include `risk_id`, path/title, URL, type, owner, sec_label, risk reason, key evidence, and recommended action. For multiple Wiki entries or shortcuts of the same underlying document, they must be distinguished by URL; if combined governance is recommended, explain in the recommended action that they point to the same underlying object.

<a id="审计摘要"></a>
## Audit Summary

```text
Target: <title> (<type>)
URL: <url-or-token-if-url-unavailable>
Conclusion: <compliant / risk pending confirmation / cannot fully determine>
Evidence:
- link_share_entity=<value>
- external_access_entity=<value>
- external_access=<value>
- invite_external=<value>
- share_entity=<value>
- manage_collaborator_entity=<value>
- copy_entity=<value>
- security_entity=<value>
- comment_entity=<value>
- lock_switch=<value>
- sec_label_name=<value-or-missing>
Limitations: <unsupported_checks or none>
Recommended action: <read-only next step or proposed remediation>
```

<a id="容器安全诊断报告摘要"></a>
## Container Security Diagnostic Report Summary

```text
Read-only security diagnosis completed; no permission changes were made.

One-sentence conclusion: <no internet public link found / internet public link candidate risk exists>; <external_access_count> documents allow external sharing, <missing_label_count> documents lack a security label. Recommend prioritizing review of <top_priority_group_or_paths>.

Coverage:
- Targets visible to the current identity: <visible_count>
- Successfully checked target public access and collaboration permission settings: <permission_checked_count>
- Read failures / deleted / no permission: <failed_count>
- Uncovered capabilities: <collaborator_list / inheritance / audit_log / view_records / none>

Risk levels:
- High-priority pending review: <internet_public_count> internet-public-link candidates; <external_access_count> allow external sharing; of these, <external_without_label_count> also lack a security label.
- Medium-priority pending review: <tenant_link_count> accessible/editable to anyone in the company with the link; <wide_share_count> have a broad collaborator management scope.
- Pending policy confirmation: <security_count> copy/download/print scopes pending review; <comment_count> comment scopes pending review.
- Cannot determine: <unsupported_or_unverified_summary>.

Level meanings:
- Internet public link: anyone who obtains the link may access it; highest priority.
- Allow external sharing: external sharing capability is enabled and requires owner review; it does not mean external collaborators already exist.
- Company-internal link accessible: not publicly external, but the spread scope within the organization is broad.
- Copy/download/print/comment: whether tightening is needed depends on business policy and document security label.

High-priority pending review list:
> Displayed by `摘要清单展开规则`. Each object must include `risk_id` and URL; when URL is missing, display token / node_token and the reason. If there are no high-priority objects, display only the medium-priority or pending-policy-confirmation group summary.

- <risk_id> <path-or-title> (<type>)
  URL: <url-or-token-if-url-unavailable>
  Owner: <owner-or-unknown>
  Security label: <sec_label_name-or-missing-or-unknown>
  Reason pending review: <why high priority>
  Evidence: <short user-language evidence, e.g. 对外分享=已开启；链接分享=未开启互联网公开链接>
  Recommended action: <recommended action>

Not fully expanded:
- The complete risk list contains <risk_manifest_count> entries; this summary has displayed <shown_count> entries and has not displayed <hidden_count> entries.
- Groups not displayed: <risk_group=count summary or none>

Recommended next steps:
- Generate a complete risk list artifact, including `risk_id`, URL, owner, security label, evidence fields, recommended action, and `selected` columns.
- Generate a read-only remediation dry-run based on risk_id, risk group, owner, path, URL, or rows in the artifact with `selected=true`.
- Handle only the targets and permission changes selected by the user, such as closing public links or tightening sharing; verify session authorization and do not repeatedly confirm an already explicit plan.
- Generate a review checklist by owner / security label.
- Continue reading access records to determine low activity with high exposure.

Remaining limitations:
- <do not claim collaborator-list verification if unsupported>
- <external_access_entity=open or external_access=true only means sharing outside is allowed, not that external collaborators exist>
- <missing view_records / DLP / AI index status / audit log limitations>
```

<a id="可操作风险清单"></a>
## Actionable Risk List

The complete risk list is used to let users select the subsequent governance scope. Markdown / CSV / Feishu document reports must all include the following fields; if a format cannot fully display nested evidence, use a short text summary and preserve `risk_id` and URL.

```text
Scope: <explicit_list / wiki_space / wiki_node / drive_folder> <name-or-id>
Generated at: <timestamp>
Purpose: users can select governance targets by risk_id, priority, risk_group, owner, path, URL, or selected=true.

| risk_id | priority | Path | URL | Type | Owner | sec_label | risk_group | evidence | recommended_action | current_setting | target_setting | selected | decision | status | skip_reason |
|---------|----------|------|-----|------|-------|-----------|------------|----------|--------------------|-----------------|----------------|----------|----------|--------|-------------|
| PG-001 | P1 | <path> | <url-or-token> | <type> | <owner-or-unknown> | <sec-label-or-missing> | <risk_group> | <short evidence> | <recommended-action> | <field=value> | <field=value-or-owner-review> | false | undecided | pending | <none-or-reason> |
```

Field rules:

- `risk_id` is generated with stable sorting by priority, risk_group, normalized path, URL, and canonical token / node_token; when URL is missing, token / node_token must be used as the tie-breaker. Documents with the same name, same path, shortcut, or multiple Wiki entries cannot be numbered by path alone; they must not be duplicated within the same diagnosis.
- `priority` uses `P0`, `P1`, `P2`, `PolicyReview`, `Unknown`; when displayed to users, they may be translated as "highest priority / high-priority pending review / medium-priority pending review / pending policy confirmation / cannot determine".
- `selected` defaults to `false`; users can change it to `true` in CSV / Feishu document tables, or directly say "handle PG-001, PG-003" in chat.
- `decision` indicates the user decision: `undecided`, `keep`, `dry_run`, `confirm_write`, `skip`.
- `status` indicates the execution status: `pending`, `dry_run_ready`, `confirmed`, `executed`, `verified`, `failed`, `skipped`.
- `target_setting` is the recommended target state and does not mean it has been executed; when there is no explicit policy, only owner review / policy review can be written.

<a id="治理选择交互"></a>
## Governance Selection Interaction

When the user continues governance based on the complete risk list, the Agent must first parse the selection scope, then generate a read-only dry-run:

```text
Acceptable user selections:
- Handle PG-001, PG-003, PG-008, and close the internet public links.
- First handle all risk_group=internet_public_link, and do not handle external_access_only.
- Generate a remediation dry-run for rows in CSV / Feishu documents with selected=true.
- Skip PG-003 for now, and handle only PG-001.

The Agent must reply:
- Number of selected objects: <count>
- Selection source: <risk_id list / risk_group / selected=true / URL / path>
- Next step to execute: generate dry-run; do not execute writes
- Objects that need to be skipped or reconfirmed: <missing risk_id / unsupported / changed_since_report / no manage_public>
```

If the user's selection comes from an old report or external artifact, the current permissions of the selected targets must be re-read before generating the dry-run. When the current settings are inconsistent with the report snapshot, mark it as `changed_since_report` and do not directly reuse old fields for execution.

<a id="权限设置清单"></a>
## Permission Settings List

```text
Scope: <explicit_list / wiki_space / wiki_node / drive_folder> <name-or-id>

| Path | URL | Type | link_share_entity | external_access_entity / external_access | invite_external | share_entity | manage_collaborator_entity | copy_entity | security_entity | comment_entity | lock_switch | sec_label_name | Recommended action | Limitation |
|------|-----|------|-------------------|------------------------------------------|-----------------|--------------|----------------------------|-------------|-----------------|----------------|-------------|----------------|----------|------|
| <path> | <url-or-token> | <type> | <value> | <value> | <value-or-unknown> | <value> | <value-or-unknown> | <value-or-unknown> | <value> | <value> | <value-or-unknown> | <value-or-missing> | <recommended-action> | <unsupported-or-none> |
```

<a id="访问复核清单"></a>
## Access Review List

```text
Scope: <wiki_space / wiki_node / drive_folder / explicit_list> <name-or-id>
Number of review objects: <count>

| Owner | Path | URL | Type | Security label | Risk tag | Current permission summary | Recent access evidence | Recommended action |
|-------|------|-----|------|------|----------|--------------|--------------|----------|
| <owner-or-unknown> | <path> | <url-or-token> | <type> | <sec-label-or-missing> | <labels> | <link/external/share/security/comment> | <uv/pv/last_view_or_unknown> | <keep / tighten / owner review / unsupported> |

Limitation: <unsupported_checks / discovery_blockers / none>
```

<a id="整改-dry-run"></a>
## Remediation Dry-run

```text
A remediation plan will be generated; no writes will be executed:
- Scope: <scope>
- Selection source: <risk_id list / risk_group / selected=true artifact / URL list>
- Number of candidate targets: <count>
- Planned execution command: <command family>
- Re-read: current permissions have been re-read for the selected targets; changed_since_report=<count>
- Field changes:
  - <risk_id> <path> (<url-or-token>): <field> <old> -> <new>
- Skipped items: <unsupported / no manage_public / unsupported type / missing policy>
- Verification method: re-read <metadata / target public access and collaboration permission settings> after execution
- Limited rollback scope: <target public access and collaboration permission settings snapshot fields / not applicable>

Please confirm whether to proceed to write confirmation.
```

<a id="批量权限申请确认"></a>
## Batch Permission Request Confirmation

```text
<view / edit> permission requests will be initiated one by one:
- Number of candidate targets: <count>
- Command type: drive +apply-permission
- Risk: write; each request will notify the owner
- Execution method: call one by one in candidate list order; failed items will be recorded separately

Candidate examples:
- <risk_id> <title> (<type>, <url-or-token>): <reason>

Please confirm whether to initiate permission requests for the above candidate targets.
```

<a id="owner-转移确认"></a>
## Owner Transfer Confirmation

```text
Owner will be transferred one by one:
- Number of candidate targets: <count>
- Command type: drive permission.members transfer_owner
- Risk: high-risk-write; will change the document owner and may affect the original owner's permissions and the document's location
- New owner mapping: <same_new_owner / per_target_new_owner>
- Global new owner: <member_id> (<member_type>); displayed only when all candidate targets have the same new owner, otherwise omitted
- Notify new owner: <need_notification>
- Original owner permissions: <remove_old_owner=true / old_owner_perm>
- Personal space location: <stay_put>
- Execution method: call one by one in candidate list order; failed items will be recorded separately
- Verification method: re-read metadata owner after execution; types not supported by metadata are marked as partial
- Rollback boundary: no automatic rollback; if the owner needs to be restored, a separate reverse owner transfer confirmation must be initiated

Candidate examples:
- <risk_id> <title> (<type>, <url-or-token>): current owner=<owner-or-unknown> -> new owner=<member_id> (<member_type>)

Please confirm whether to transfer owner for the above candidate targets.
```

<a id="确认请求"></a>
## Confirmation Request

```text
<operation> will be executed:
- Target: <risk_id> <title> (<type>, <url-or-token>)
- Command type: <command family>
- Risk: <risk_level>
- Field changes:
  - <field>: <old> -> <new>
- Verification method: re-read <metadata / target public access and collaboration permission settings> after execution
- Limited rollback material: <target public access and collaboration permission settings snapshot / not applicable>

Please confirm whether to execute.
```

<a id="最终摘要"></a>
## Final Summary

```text
Completed: <read checks / writes>
Verification: <fresh read result or async permission-request approval note>
List status: <risk_id status updates / not applicable>
Rollback material: <target public access and collaboration permission settings snapshot / not applicable>
Remaining limitations: <unsupported_checks / partial facts / approvals>
```
