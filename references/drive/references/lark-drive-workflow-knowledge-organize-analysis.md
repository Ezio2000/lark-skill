<a id="知识整理工作流analysis"></a>
# Knowledge Organization Workflow: Analysis

Loaded by states: `CONTENT_READ`, `ISSUE_ANALYSIS`, `RULE_GENERATION`.

This file owns low-confidence partial reads, issue analysis, classification rules, and target tree generation. It MUST NOT create execution plans, ask for execution confirmation, or perform write operations.

## Required Context

Before executing rules in this file:

1. `resource_items` MUST already exist from [`lark-drive-workflow-knowledge-organize-discovery.md`](lark-drive-workflow-knowledge-organize-discovery.md).
2. For document partial reads, follow [`../../doc/index.md`](../../doc/index.md) and [`../../doc/references/lark-doc-fetch.md`](../../doc/references/lark-doc-fetch.md).
3. For sheet / bitable down-drill, follow [`../../sheets/index.md`](../../sheets/index.md) or [`../../base/index.md`](../../base/index.md) only when title and path are insufficient.

## State: CONTENT_READ

Entry: `resource_items` exists.

MUST:

1. Build `low_confidence_items`.
2. Apply `Low-Confidence Partial Read`.
3. Read only supported docs through `lark-doc-fetch`.
4. Switch to `lark-sheets` / `lark-base` only when sheet / bitable title and path are insufficient.
5. Record read evidence for classification.
6. Continue reading low-confidence resources in internal batches until all supported low-confidence resources in the current inventory are processed or a blocker occurs.
7. Apply `Analysis Progress Reporting`.
8. Output progress / summary without asking the user to continue between batches.

Exit: low-confidence items are classified or marked `needs_review=true`.

### Low-Confidence Partial Read

Low-confidence resources include:

- Empty title
- Title is `test` / `测试` / pure numbers / meaningless short words
- Insufficient classification clues among title, path, and type
- The same title or similar titles appear in multiple candidate classifications
- The user requests classification by project / customer / business line, but the title and path do not contain a clear project / customer / business line name

| Condition | Agent MUST Do | Agent MUST NOT Do |
|-----------|---------------|-------------------|
| Title / path / type clearly determine classification | Classify directly | Do not perform content read |
| Resource is low-confidence and docs-fetch-supported | Read outline via `lark-doc-fetch` | Do not skip partial read |
| Candidate project / customer / business / document-type terms exist | After outline, run keyword partial read with candidate terms | Do not use broad generic keywords |
| Partial read returns usable block id and classification is still unclear | Read the relevant section via `lark-doc-fetch` | Do not read the full document |
| Partial read still cannot classify | Set `needs_review=true`; classify to manual confirmation target | Do not invent classification |
| Read fails or permission is insufficient | Set `needs_review=true`; record failure reason | Do not retry indefinitely |

### Partial Read Limits

| Limit | Default |
|-------|---------|
| `batch_size` | 20 resources per internal batch |
| `progress_report_interval` | 50 low-confidence resources |
| `max_attempts_per_resource` | 3 partial reads: outline, keyword, section |

Batching rules:

1. Sort low-confidence resources by impact before reading: root-level loose items, duplicated titles, project/customer ambiguity, then empty or meaningless titles.
2. Read supported low-confidence resources across internal batches without asking the user to continue after each batch.
3. Process reads in internal batches of `batch_size`; do not ask the user between internal batches unless auth, permission, or API errors block progress.
4. After each internal batch, update `low_confidence_items` with read evidence or `needs_review=true`.
5. After every `progress_report_interval` processed resources, output a progress summary and continue automatically.
6. If unread low-confidence resources remain because of auth, permission, API, unsupported type, or tool budget blockers, set `partial=true`, report unread count, and default remaining unread items to `needs_review=true` with target path set to manual confirmation target.
7. Never bypass these limits by reading full documents.

### Low-Confidence Read Start Notice

When `low_confidence_total > 100`, output this notice before reading:

```text
There are many low-confidence resources, <low_confidence_total> in total. I will perform lightweight reads in batches and report progress periodically; I will not read the full text, nor will I perform moves or creations.
```

### Low-Confidence Read Summary

Use this as progress / final summary output. Do not ask the user to continue unless a blocker occurs.

```text
Low-confidence content read progress

- Total low-confidence resources: <low_confidence_total>
- Read: <read_done>/<low_confidence_total>
- Evidence supplemented and classification completed: <classified_count>
- Temporarily placed in pending manual confirmation: <needs_review_count>
- Failed: <failed_count>

Continue analyzing organization issues.
```

Output this summary:

- After every 50 processed low-confidence resources.
- Once after low-confidence reading finishes.
- About every 60 seconds during long-running reads, even if fewer than 50 additional resources were processed.

### Analysis Progress Reporting

Applies to `CONTENT_READ`, `ISSUE_ANALYSIS`, and `RULE_GENERATION`.

Rules:

1. For `CONTENT_READ`, use `Low-Confidence Read Summary` as the progress report format.
2. For `ISSUE_ANALYSIS`, if analysis runs longer than about 60 seconds, output progress about every 60 seconds with current stage, processed resource count when known, detected problem type count when known, and the next analysis step.
3. For `RULE_GENERATION`, if classification rule or target-tree generation runs longer than about 60 seconds, output progress about every 60 seconds with current stage, classified item count when known, unresolved item count when known, and target category / path count when known.
4. Progress reports MUST be factual and stage-specific. Do not output generic "still running" messages without counts or the current stage.
5. Do not ask the user to continue between internal batches unless auth, permission, API, target scope, or environment blockers occur.
6. Do not expose internal chain-of-thought, raw tokens, or intermediate rule drafts.

Examples:

```text
Analysis progress: summarizing organization issues, processed <processed_count>/<resource_count> resources, identified <problem_type_count> types of issues. Continuing to generate the organization approach; will not perform moves or creations.
```

```text
Rule generation progress: generating classification rules and target directories, classified <classified_count> items, <needs_review_count> items pending manual confirmation. Continuing to generate the prerequisite data for the complete plan.
```

## State: ISSUE_ANALYSIS

Entry: `resource_items` and partial-read evidence are ready.

MUST:

1. Detect problems from organization perspective only. Do not generate research conclusions.
2. Generate an organization approach based on inventory, low-confidence read evidence, and detected problems.
3. Include how non-reused source containers will be handled after their contents are moved.
4. Apply `Analysis Progress Reporting`.
5. Output `Inventory And Organization Approach Decision`.
6. Stop and wait for the user to confirm the approach before `RULE_GENERATION`.

Problem rules:

| Problem | Detection Rule |
|---------|----------------|
| Root directory accumulation | Too many direct resources in the root directory, or exceeding an obvious proportion of total resources |
| Similar files scattered | Resources with similar titles / types are distributed across multiple unrelated paths |
| Inconsistent naming | Date, customer, and project naming formats for similar resources are obviously inconsistent |
| Too much temporary content | Title / path contains `临时`, `测试`, `tmp`, `draft`, `转移`, `未整理` |
| Empty directories | Directory-type nodes have no descendant resources |
| Duplicate directories | Directory names are identical or highly similar after normalization |
| Overly old archived content | Resources from old years are still scattered in active directories |

MUST output evidence count or example paths. Do not output only abstract judgment.

### Problem Pagination

| Output Area | Rule |
|-------------|------|
| Problem overview | Show at most 5 problem types per page |
| Problem examples | Show at most 3 example paths per problem type |
| Pagination | Affects display only; complete `issue_summary` MUST remain internal |

### Inventory And Organization Approach Decision

```text
Inventory and organization approach

Inventory results:
| Metric | Count |
|------|------|
| Total resources |  |
| Resources by type |  |
| Number of first-level directories |  |
| Direct resources in root directory |  |
| Number of empty directories |  |
| Number of low-confidence resources |  |
| Low-confidence reads completed |  |
| Pending manual confirmation |  |
| partial |  |

<problem_type_count> types of issues were found in total; currently showing page <page>/<total_pages>.

| Problem | Evidence Count | Example Paths | Description |
|------|----------|----------|------|

Organization approach:
- <approach item 1>
- <approach item 2>
- Place resources with insufficient evidence, read failures, or insufficient permissions into "pending manual confirmation"
- If there are source directories that will no longer be reused, after their contents are moved out, collect the directory itself into `待人工确认/待清理旧目录`, to avoid the first-level directories still being cluttered after organization
- Do not delete, do not rename, do not modify permissions

Generate the target directories and the move / create plan based on this organization approach?

You can choose:
1. Generate the target directories and plan based on this approach
2. Adjust the organization approach
3. View problem details
4. Cancel this organization
```

## State: RULE_GENERATION

Entry: user confirms the organization approach.

MUST:

1. Generate `classification_rules`.
2. Generate `target_tree`.
3. Generate `target_tree` to at least two levels; include third level when needed for project / customer / document-type grouping.
4. Reuse existing clear structure when possible.
5. Identify reused top-level containers and non-reused source containers, and set `source_container_disposition`.
6. For non-reused source containers, ensure `target_tree` includes a source-container cleanup target, defaulting to `待人工确认/待清理旧目录`, unless the user explicitly asks to keep source containers in place.
7. Ensure target tree can contain every planned `target_path`.
8. Ensure the target tree contains a manual confirmation target named `待人工确认` unless the user explicitly provides an equivalent name.
9. Apply `Analysis Progress Reporting`.
10. Continue to `PLAN_GENERATION` without a separate target-tree-only confirmation.

### Classification

| Condition | Agent MUST Do |
|-----------|---------------|
| Existing structure is clear | Reuse existing directory names and hierarchy |
| Title / path / type is enough | Classify without content read |
| Item remains uncertain after mandatory partial read | Put into manual confirmation target and set `needs_review=true` |
| Item is temporary / test / draft | Prefer temporary / test target |
| Root has many loose resources | Prefer organizing root-level obvious items first |
| User asks project / customer grouping | Use project / customer names from title, path, and partial read evidence |
| Naming is inconsistent | Report the issue with examples only; do not generate rename actions |

### Adaptive Classification

The agent MUST NOT start from a fixed default category list. A fixed taxonomy can bias classification and confuse users when category names or numeric prefixes do not match their resources.

Derive categories from the current `resource_items` and partial-read evidence:

1. First group resources by clear signals from title, current path, type, and mandatory partial-read evidence.
2. Prefer category names that appear in the user's own content, such as project names, customer names, business lines, document types, years, or existing folder / Wiki node names.
3. Create a category only when there is enough evidence for at least one resource.
4. Do not create generic buckets such as archive, temporary, test, meeting, dashboard, or operations unless the current resources contain matching evidence.
5. Do not add numeric prefixes to category names unless the user explicitly asks for ordered naming.
6. Always keep a manual confirmation target named `待人工确认` or an equivalent user-specified name for unresolved items.

### Target Tree

`target_tree` is generated in this state but shown together with the move / create plan in `PLAN_GENERATION`. Do not stop after displaying a target tree alone.

## Analysis Failure Handling

| Failure / Blocker | Agent MUST Do | Agent MUST NOT Do |
|-------------------|---------------|-------------------|
| Missing API scope | Follow `lark-shared` permission handling and stop | Do not retry the same command repeatedly |
| Resource access denied | Stop and follow the main workflow `Permission Request Gate` | Do not request permission automatically or in batch |
| Partial document read fails for a low-confidence item | Mark item `needs_review=true`, record reason, and route to manual confirmation target | Do not classify by guessing |
| Item remains ambiguous after partial read | Mark `needs_review=true` and route to manual confirmation target | Do not invent classification |
