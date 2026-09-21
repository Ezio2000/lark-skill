<a id="主题资料收集工作流召回"></a>
# Topic material collection workflow: recall

Loaded by states `SEARCH_RECALL`, `RECALL_ENHANCE`.

This document is responsible for basic search recall, coverage enhancement, query evidence, deduplication, and `CandidateItem`. It must not parse the target move token, read full document content, judge relevance, or perform write operations.

This document only serves `topic_move_collector`. When entering this document, `workflow_id` must be `topic_move_collector`; the current task must not be rerouted to another workflow.

<a id="必读上下文"></a>
## Required context

Before executing the rules in this document:

1. Handle identity, authentication, and permissions according to [`../../shared/index.md`](../../shared/index.md).
2. Handle `drive +search` syntax, filter conditions, a maximum of 5 pages per batch, and identity semantics according to [`lark-drive-search.md`](lark-drive-search.md); the full continuation rules for this workflow are described below.

<a id="搜索原则"></a>
## Search principles

1. By default, use `drive +search --mine` to recall Workspace resources owned / managed by the current user.
2. Unless the user originally requested a limited scope, do not ask the user to specify a folder or Wiki scope.
3. `SEARCH_RECALL` and `RECALL_ENHANCE` must remain independent states.
4. `SEARCH_RECALL` uses the user's original keywords, `owner_scope`, and explicit restrictions.
5. `RECALL_ENHANCE` may add expanded queries based on basic recall evidence, and must inherit the same `owner_scope`.
6. Each candidate must retain query evidence to facilitate later explanation of its source.
7. A single page or a single query batch of at most 5 pages does not represent complete coverage; when `has_more=true`, you must save `next_page_token` and automatically start the next batch until `has_more=false` or a blocker occurs.
8. Recall and enhanced recall may take a long time; when execution exceeds 60 seconds, you must output a progress notice, and then approximately once every 60 seconds thereafter.
9. Only when the user explicitly confirms `owner_scope=all_visible` in `CONFIRM_CONTEXT` is it permitted to remove `--mine`.

<a id="分页优先级与完成语义"></a>
### Pagination priority and completion semantics

1. When the user confirms entering `topic_move_collector`, it means they agree to perform a full recall for this collection task; there is no need to additionally ask the user to say "all / full / keep paging". This rule overrides the default first-screen interaction rule of `lark-drive-search.md`.
2. The limit of at most 5 pages per round in `lark-drive-search.md` is still observed. Each read of at most 5 pages forms one batch; when the batch ends and `has_more=true`, save a checkpoint and automatically start the next batch using the original query, original filter conditions, and the returned `next_page_token`.
3. Automatic batch continuation does not change the workflow state and does not trigger user confirmation. When execution exceeds approximately 60 seconds, only output progress.
4. A query is `complete` only when `has_more=false`. The end of a single batch, reaching 5 pages, or already having partial candidates does not represent completion.
5. Only after all queries in the current state are `complete` may you proceed to the next state. Authentication, permissions, invalid pagination tokens, consecutive retry failures, or insufficient tool budget are blockers; you must retain the checkpoint, report partial recall, and stop in the current state, and must not treat partial results as complete recall and continue to classification.

### QueryRecallState

Each basic / enhanced query must maintain:

```json
{
  "query_id": "稳定 query ID",
  "query": "完整 query",
  "recall_stage": "search_recall|recall_enhance",
  "page_count": 0,
  "batch_count": 0,
  "next_page_token": "下一批起点",
  "has_more": true,
  "status": "pending|running|complete|blocked",
  "blocker": "阻塞原因"
}
```

<a id="状态search_recall"></a>
## State: `SEARCH_RECALL`

Entry condition: the user has confirmed `CONFIRM_CONTEXT`.

Must:

1. Construct basic queries based on the confirmed `topic`.
2. Apply the default `owner_scope=mine` and the explicit restrictions in `constraints`.
3. Do not implicitly add `--folder-tokens` or `--space-ids`.
4. When `owner_scope=mine`, all basic queries must include `--mine`.
5. When `owner_scope=all_visible`, do not include `--mine`, and record the expanded recall risk.
6. Unless the command restrictions require a lower value, use `--page-size 20`.
7. Execute each basic query with at most 5 pages per batch; when the batch ends and there are still more results, automatically continue batches and merge all pages.
8. Record basic statistics: query, search scope, page count, batch count, collected count, duplicate count, blockers.
9. Only when `status=complete` and `has_more=false` for all basic queries may you proceed to `RECALL_ENHANCE`; when a blocker occurs, remain in `SEARCH_RECALL`.

<a id="召回进度-ui"></a>
### Recall progress UI

When `SEARCH_RECALL` or `RECALL_ENHANCE` lasts longer than approximately 60 seconds, output the current progress:

```text
Search progress: current stage <SEARCH_RECALL|RECALL_ENHANCE>, executed <query_count> queries, read <page_count> pages, collected <raw_count> candidates, <unique_count> after deduplication. Continuing the search; no resources will be created or moved.
```

If a specific query is being executed, you may add:

```text
Current query: <query>
```

<a id="基础-query-规则"></a>
### Basic query rules

| User input | Basic query |
|------------|----------------|
| A single keyword | Use directly as `--query`. |
| Multiple keywords forming one phrase | Prefer executing as the phrase entered by the user. |
| Explicit exact phrase | Preserve quotation marks. |
| Explicit exclusion terms | Preserve negative terms. |
| No real keywords, only filter conditions | Use `--query ""` with filter conditions. |

In `SEARCH_RECALL`, do not add synonyms, title-only search, comment-only search, or OR expansion.

<a id="基础召回输出"></a>
### Basic recall output

```text
Basic recall complete:
- Queries used:
- Search scope:
- Applied restrictions:
- Candidates collected:
- Candidates after deduplication:
- Blockers:

Next step: continue executing coverage enhancement; no action is needed from you; no resources will be created or moved.
```

<a id="状态recall_enhance"></a>
## State: `RECALL_ENHANCE`

Entry condition: basic recall is complete.

Must:

1. Generate enhanced queries based on the confirmed topic and basic recall evidence.
2. Ensure enhanced queries are explainable and do not introduce obvious contamination.
3. Each enhanced query must inherit `owner_scope`; when `owner_scope=mine`, it must include `--mine`.
4. Each query must handle pagination with at most 5 pages per batch, and automatically continue batches until `has_more=false`.
5. When a stable deduplication key exists, merge candidates by the stable deduplication key.
6. Retain `source_queries` and hit evidence for each candidate.
7. Stop enhancement when a query no longer produces new candidates, or when a tool budget / API blocker occurs.

<a id="召回阶段退出门禁"></a>
### Recall stage exit gate

After `RECALL_ENHANCE` is complete, you must:

1. Confirm that `status=complete` and `has_more=false` for all basic and enhanced queries, then finalize the complete `candidate_items`, including deduplication results, `source_queries`, `match_channels`, `snippets`, and `dedupe_status`.
2. Set `current_state` to `RESOURCE_RESOLVE`.
3. Load [`lark-drive-workflow-topic-move-collector-resolve-verify.md`](lark-drive-workflow-topic-move-collector-resolve-verify.md).
4. Hand the complete `candidate_items` to `RESOURCE_RESOLVE`.
5. Do not directly proceed to `RELEVANCE_CLASSIFY`, `PLAN_MOVE`, or display relevance results.
6. Do not directly generate high / medium / low relevance groups from search titles, summaries, or query hits.

<a id="增强策略"></a>
### Enhancement strategies

| Strategy | Description |
|----------|------|
| Exact phrase | Use `"..."` for explicit phrases to improve exact hits. |
| `intitle:` | Perform title recall for topics with strong title characteristics, such as project names, customer names, policy names, and report names. |
| `--only-title` | Use when title hits are more reliable. |
| `--only-comment` | Use when the topic may only appear in comment discussions. |
| Type splitting | Search by type for `docx`, `sheet`, `bitable`, `slides`, `file`, etc., to reduce server-side ranking bias. |
| Synonyms / aliases | Use business-explicit synonyms, abbreviations, English names, and Chinese names. |
| OR expansion | Perform OR expansion on aliases of the same entity. |
| Negative terms | Use `-term` for obvious noise, but do not exclude topic terms that may be relevant. |

<a id="query-证据"></a>
### Query evidence

Each candidate must record:

| Field | Description |
|-------|------|
| `source_queries` | List of queries that hit this resource. |
| `match_channels` | Hit location, such as title, body, comment, metadata. |
| `snippets` | Summary or snippet returned by search. |
| `query_rank` | Relative position of the resource in each query. |
| `recall_stage` | `search_recall` or `recall_enhance`. |

<a id="去重规则"></a>
## Deduplication rules

Must:

1. When the search response provides a canonical token, prefer the canonical token.
2. For Wiki results, do not deduplicate only by object token; the same object may appear in multiple Wiki nodes.
3. When a token is missing, use the URL as a fallback.
4. When merging duplicates, retain all query evidence.
5. If it cannot be determined whether deduplication is stable, retain the item and set `dedupe_status=uncertain`.

## CandidateItem

```json
{
  "title": "资源标题",
  "url": "资源链接",
  "raw_type": "搜索返回类型",
  "source_queries": ["query"],
  "match_channels": ["title|body|comment|metadata"],
  "snippets": ["命中片段"],
  "page_rank": 1,
  "dedupe_key": "候选去重键",
  "dedupe_status": "stable|fallback|uncertain",
  "recall_stage": "search_recall|recall_enhance"
}
```

| Field | Description |
|-------|------|
| `title` | Search result title. |
| `url` | Resource access link. |
| `raw_type` | Original type returned by search. |
| `source_queries` | Search queries that hit this resource. |
| `match_channels` | Hit location. |
| `snippets` | Summary or hit snippet. |
| `page_rank` | Ranking position under the current query. |
| `dedupe_key` | Candidate deduplication key. |
| `dedupe_status` | Deduplication confidence. |
| `recall_stage` | Recall stage in which the resource first entered the candidate set. |

<a id="阻塞项"></a>
## Blockers

When authentication / scope is missing, `drive +search` returns a permission or policy blocker, the pagination token is invalid, pagination still cannot continue after retries, or the tool budget is insufficient to complete all pages, you must set the corresponding `QueryRecallState.status` to `blocked`, retain accumulated candidates, page count, and `next_page_token`, stop, and report. After the blocker is resolved, resume from the checkpoint; before all queries are complete, do not proceed to the resource parsing or classification stage.
