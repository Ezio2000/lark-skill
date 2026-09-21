
<a id="drive-search云空间云盘云存储搜索扁平-flag面向自然语言场景"></a>
# drive +search (Drive/Cloud Drive/Cloud Storage search: flat flags, for natural language scenarios)


Based on the Search v2 API `POST /open-apis/search/v2/doc_wiki/search`, supports unified search of Drive (Cloud Drive/Cloud Storage) objects as **a user identity or an app identity**.

Core features:

- Flattens all common filter conditions into **independent flags** (`--edited-since`, `--created-by-me`, `--mine`, `--doc-types`, `--folder-tokens`, etc.), no longer requiring users or AI to hand-write nested `--filter` JSON
- Additionally exposes 4 "me" dimensions: `my_edit_time` (edited by me), `my_comment_time` (commented on by me), `open_time` (opened by me), `create_time` (document creation time) — directly corresponding to user natural language expressions like "recently edited by me", "commented on by me", etc.
- Automatically handles hour-level aggregation for `my_edit_time` / `my_comment_time` (server-side storage granularity): sub-hour inputs snap to the hour, with a notice printed to stderr
- `--created-by-me` fills `original_creator_ids` from the currently logged-in user's open_id with one click, matching "originally created by me"; `--mine` still fills `creator_ids`, matching owner / document owner

> **Unified resource discovery entry**: `drive +search` also returns all Drive (Cloud Drive/Cloud Storage) objects such as `SHEET` / `Base` / `FOLDER`, not just documents / Wiki. When the user says "find a spreadsheet", "find a report", "recently opened spreadsheet", also start here; after locating, switch to the corresponding business skill (e.g. `lark-sheets`) for operations within the object.

> **Identity boundary**: Explicit filters such as ordinary keywords, type, folder, Wiki space, owner/open_id support `--as user` or `--as bot`. `--mine` / `--created-by-me` rely on the currently logged-in user's open_id to auto-fill filter conditions; under app identity, if no user open_id is configured, use explicit `--creator-ids` / `--original-creator-ids` instead.

<a id="命令"></a>
## Command

> **Key constraint: search keywords must be passed via `--query`.**
> Correct: `lark-cli drive +search --query "方案"`
> Incorrect: `lark-cli drive +search 方案`
> `+search` does not accept positional arguments; an empty `--query` or omitting `--query` means browsing purely by filter (valid).
>
> **`--query` is at most 30 characters**: counted by number of characters (Unicode code points), each Chinese character counts as 1, same measure as ASCII; exceeding 30 will be rejected by the server (`99992402 field validation failed`, **it is an error, not truncation**). Long keywords must first be compressed into core entity + topic words (e.g. compress a whole-sentence question into "project name + topic" before searching), do not stuff the entire original question into `--query`.
>
> **Locating by full title:** Use `--only-title`; when the title does not exceed 30 characters, query directly; for overly long titles, use a stable fragment within the limit to recall, then strictly match against the returned title. Use the same query and filter conditions to check by `page_token`, up to 3 pages; only continue with write operations when `has_more=false` and there is exactly one strict match across pages, otherwise ask the user to narrow the scope or provide more information. `drive files list` is only used to enumerate the direct children of a known folder.
>
> **Do not force keywords into list-type requests**: if the user only requests scope browsing / summarization such as "all documents I created this month", "documents I edited in the last six months", "statistics by type", and no title fragment or business keyword is given, use `--query ""` with filter conditions such as `--created-by-me`, `--mine`, `--created-*`, `--edited-*`, `--doc-types`. Do not put action words or statistical intents such as "find", "all documents", "recently updated", "statistics by type" into `--query`, otherwise results that should have been matched by filter will be overly narrowed.
>
> **Joint search of title words + body words**: if the user gives both title keywords and body keywords and requires the same resource to satisfy both conditions, prioritize executing one ordinary joint search: `lark-cli drive +search --query "标题词 正文词"`, and in the same command stack the user-specified filter conditions such as `--folder-tokens`, `--doc-types`. Do not split this joint search into "title search + body search" and then intersect them yourself; also do not use `--only-title` or `intitle:` as the primary candidate path. Only when the user explicitly asks to search titles only, use `--only-title` or `intitle:`.
>
> When the user requests N final results, N is the output upper limit, not equal to `--page-size N`. Page by page, based on `title` and `summary_highlighted`, keep candidates that satisfy both conditions; when valid candidates are fewer than N and `has_more=true`, keep the same query and filter conditions, use `--page-token` to continue, checking up to 3 pages. When the summary is insufficient to judge body conditions, only serially read the body of candidates whose titles already match, confirm one before processing the next, and stop after finding N; do not fetch bodies concurrently. If still insufficient after checking 3 pages, return the confirmed results and suggest the user adjust the title words, body words, or search scope; do not scan unboundedly.

<a id="自然语言--命令映射速查"></a>
### Natural language → command mapping quick reference

| User says | Command |
|---|---|
| Title contains a word and body contains a word, limited to at most N results in a folder (N is the final output upper limit; paginate and filter per the rules above, do not use as `--page-size`) | `lark-cli drive +search --query "标题词 正文词" --folder-tokens <FOLDER_TOKEN>` |
| All documents I created this month, statistics by type | `lark-cli drive +search --query "" --created-by-me --created-since "<YYYY-MM-DD>" --created-until "<YYYY-MM-DD>"` |
| Documents I edited in the last six months, see which were recently updated | `lark-cli drive +search --query "" --edited-since 6m --sort edit_time` |
| Documents I edited in the last month | `lark-cli drive +search --query "" --edited-since 1m` |
| Edited by me in the last month and commented on by me | `lark-cli drive +search --query "" --edited-since 1m --commented-since 1m` |
| Spreadsheets I opened in the last week | `lark-cli drive +search --query "" --opened-since 7d --doc-types sheet` |
| All documents I own (owner semantics, not "originally created by me") | `lark-cli drive +search --query "" --mine` |
| Documents I originally created and later transferred to Wang Wu as owner | `lark-cli drive +search --query "" --created-by-me --creator-ids ou_wangwu` |
| Documents I own, created 30-60 days ago (rough "last month", calculated by 30-day sliding window; `--mine` is owner, `--created-*` is document creation time) | `lark-cli drive +search --query "" --mine --created-since 2m --created-until 1m` |
| Documents I own, created in March 2026 (exact calendar month; same as above, owner + creation time window are two dimensions) | `lark-cli drive +search --query "" --mine --created-since 2026-03-01 --created-until 2026-04-01` |
| Keyword "budget", opened by me in the last week, sorted by edit time descending | `lark-cli drive +search --query 预算 --opened-since 7d --sort edit_time` |
| Under a certain wiki space, owned by me and created 30-60 days ago | `lark-cli drive +search --query "" --mine --space-ids space_xxx --created-since 2m --created-until 1m` |
| Documents owned by / in the charge of Zhang San (note this is owner semantics, not originally created by Zhang San) | `lark-cli drive +search --query "" --creator-ids ou_zhangsan` |
| docx I commented on in the last 3 months | `lark-cli drive +search --query "" --commented-since 3m --doc-types docx` |

<a id="更多示例"></a>
### More examples

```bash
# Pure keyword search
lark-cli drive +search --query "季度总结"

# Use server-side query advanced syntax
lark-cli drive +search --query 'intitle:方案'
lark-cli drive +search --query '"季度 总结"'
lark-cli drive +search --query '方案 OR 草稿'
lark-cli drive +search --query '方案 -草稿'

# Search only documents under a certain folder
lark-cli drive +search --query 方案 --folder-tokens fld_123456

# Search only Wiki under a certain knowledge space
lark-cli drive +search --query 研发规范 --space-ids space_1234567890fedcba

# Documents shared in a specified group
lark-cli drive +search --query 方案 --chat-ids oc_1234567890abcdef

# Search only titles / search only comments
lark-cli drive +search --query 周报 --only-title
lark-cli drive +search --query 延期原因 --only-comment

# Human-readable format
lark-cli drive +search --query OKR --format pretty

# Pagination (use --format json to get page_token first)
lark-cli drive +search --query 方案 --format json
lark-cli drive +search --query 方案 --page-token '<PAGE_TOKEN>'
```

<a id="列表--统计型请求的执行步骤"></a>
### Execution steps for list / statistics-type requests

For requests such as "all documents", "statistics by type", "recently updated", do not just run one search and answer directly. Standard process:

1. First break the natural language into filter conditions: original creator (`--created-by-me` / `--original-creator-ids`), ownership (`--mine` / `--creator-ids`), time dimension (`--created-*` / `--edited-*` / `--opened-*` / `--commented-*`), type (`--doc-types`), space or folder scope.
2. When there is no real business keyword, keep `--query ""`; do not put "all documents", "statistics", "recently updated" into query.
3. Check whether the returned results' `doc_type` / `result_meta.doc_types`, creation/edit time, and URL/token are consistent with the filter target; do not count obviously non-matching results in the answer.
4. When the user requests "all / full / statistics", paginate by `has_more` and accumulate with deduplication; do not infer the total from only the first page. The `total` in the response body is unreliable; statistics must be based on the actual deduplicated results.
5. When summarizing, group by the actual returned fields, e.g. count DOCX, SHEET, BITABLE, WIKI, FILE, etc. by `doc_type`; do not guess the type from the title.

<a id="内容检索型请求的-query-扩展"></a>
### Query expansion for content retrieval-type requests

When the user asks content questions such as reasons, conclusions, plans, comparisons, `--query` should retain business keywords, but do not use only the whole original question. First search with core entity + topic words, then adjust based on results:

- "Why are Southeast Asia server costs more expensive than other regions" → first search `"东南亚 服务器 成本"`, if recall is insufficient, then search `"服务器 成本 区域"`, `"非洲 欧洲 服务器 成本"`, `"机房 成本 费用"` and other same-topic expansion words.
- "Key points of a certain project launch event" → first search project name + "launch event" + "key points/features/overview", then judge from titles and summaries whether to search only titles or expand to bodies.

Each round of expansion must retain non-polluting, explainable evidence (URL/token/title/summary); do not skip evidence verification just because some expansion word found a highly similar title.
When expanding query, prioritize retaining the space, folder, group chat, personnel, time, and type filters already specified by the user; if the search scope truly needs to be relaxed, first explain the reason to the user and obtain confirmation.

<a id="参数"></a>
## Parameters

<a id="核心"></a>
### Core

| Parameter | Required | Description |
|---|---|---|
| `--query <text>` | No | Search keywords; supports server-side advanced syntax (`intitle:`, `""`, `OR`, `-`). Empty string or omission means browsing purely by filter. **Length limit 30 characters (counted by Unicode code points, each Chinese character counts as 1, same measure as ASCII); exceeding 30 the server directly reports `99992402 field validation failed`, no truncation** |
| `--page-size <n>` | No | Number per page, default 15, maximum 20. Exceeding 20 is automatically clamped; non-positive (≤0) falls back to 15; **non-numeric values directly return a validation error** |
| `--page-token <token>` | No | The `page_token` from the previous response, used for pagination |
| `--format` | No | `json` (default) / `pretty` |

<a id="身份维度"></a>
### Identity dimensions

> **Semantic note (important)**: Although the field name of `creator_ids` (including `--mine` / `--creator-ids`) is "creator", the server actually matches by **owner (document owner / person in charge)** semantics, **not "original creator"**. The true original creator uses `original_creator_ids` (CLI is `--created-by-me` / `--original-creator-ids`).

| Parameter | Mapping | Description |
|---|---|---|
| `--mine` | `creator_ids = [当前用户 open_id]` | bool. One-click "owned by me" (**not** "originally created by me"); resolves open_id from the currently logged-in user identity (`runtime.UserOpenId()`), errors directly if it cannot be obtained (prompts to run `lark-cli auth login`) |
| `--creator-ids ou_x,ou_y` | `creator_ids = [...]` | Explicit open_id list, comma-separated, matched by **owner**; **mutually exclusive with `--mine`** |
| `--created-by-me` | `original_creator_ids = [当前用户 open_id]` | bool. One-click "originally created by me"; resolves open_id from the currently logged-in user identity, errors directly if it cannot be obtained |
| `--original-creator-ids ou_x,ou_y` | `original_creator_ids = [...]` | Explicit open_id list, comma-separated, matched by **original creator**; **mutually exclusive with `--created-by-me`** |

<a id="时间维度每个维度一对-sinceuntil"></a>
### Time dimensions (each dimension has a pair of since/until)

| Parameter | Mapped API field | Hour snap? |
|---|---|---|
| `--edited-since` / `--edited-until` | `my_edit_time.start` / `.end` | ✅ start rounds down, end rounds up |
| `--commented-since` / `--commented-until` | `my_comment_time.start` / `.end` | ✅ same as above |
| `--opened-since` / `--opened-until` | `open_time.start` / `.end` | ❌ passed through as-is |
| `--created-since` / `--created-until` | `create_time.start` / `.end` | ❌ passed through as-is (document creation time, not "me" semantics) |

<a id="作用域"></a>
### Scope

| Parameter | Mapping | Description |
|---|---|---|
| `--doc-types docx,sheet` | `doc_types` | Comma-separated. Allowed values: `doc,sheet,bitable,mindnote,file,wiki,docx,folder,catalog,slides,shortcut` |
| `--folder-tokens fld_a,fld_b` | `folder_tokens` (doc_filter only) | When present, only sends `doc_filter`; **mutually exclusive with `--space-ids`** |
| `--space-ids sp_x` | `space_ids` (wiki_filter only) | When present, only sends `wiki_filter`; **mutually exclusive with `--folder-tokens`** |
| `--chat-ids oc_x` | `chat_ids` | Comma-separated |
| `--sharer-ids ou_x` | `sharer_ids` | Comma-separated, open_id |

<a id="其他"></a>
### Others

| Parameter | Mapping | Description |
|---|---|---|
| `--only-title` | `only_title: true` | bool |
| `--only-comment` | `only_comment: true` | bool |
| `--sort <value>` | `sort_type` (converted to uppercase enum) | Allowed values: `default, edit_time, edit_time_asc, open_time, create_time` |

> `--sort`: The CLI only exposes the 5 values **officially supported** by the server. In the server enum, `CREATE_TIME_ASC` is marked in the protocol as "not yet supported", and `ENTITY_CREATE_TIME_ASC` / `ENTITY_CREATE_TIME_DESC` are deprecated; the CLI simply does not expose them, and passing them will be rejected by cobra enum validation.

<a id="时间值格式"></a>
## Time value formats

All `--*-since` / `--*-until` share:

| Input | Meaning |
|---|---|
| `7d` / `30d` | The current moment N days ago |
| `1m` | 30 days ago (fixed 30 days, **not** a calendar month) |
| `3m` / `6m` | 90 / 180 days ago |
| `1y` | 365 days ago |
| `2026-04-01` | Local timezone 00:00:00 |
| `2026-04-01 10:00:00` / `2026-04-01T10:00:00` | Specific moment in local timezone |
| `2026-04-01T10:00:00+08:00` | RFC3339 with timezone |
| `1743523200` (≥ 10 pure digits) | Unix seconds passed through directly |

> `m` binds month (30 days), does not support minute — because `my_edit_time` / `my_comment_time` are hour-aggregated on the server, minute granularity is meaningless.

<a id="小时聚合my_edit_time--my_comment_time"></a>
## Hour aggregation (my_edit_time / my_comment_time)

The server aggregates these two fields by the hour; sub-hour inputs are aligned to the hour by the CLI:

```text
start: floor to the hour   16:23:45 → 16:00:00
end:   ceil  to the hour   16:23:45 → 17:00:00
```

When alignment occurs, a notice is printed to stderr, for example:

```text
notice: my_edit_time has hour-level granularity server-side;
        start 2026-04-22 16:23:00 → 2026-04-22 16:00:00
        end   2026-04-22 16:28:00 → 2026-04-22 17:00:00
```

The JSON output on stdout is unaffected. `open_time` / `create_time` do not perform snapping.

<a id="输出"></a>
## Output

- `--format json` (default): `{ total, has_more, page_token, results: [...] }`; all `*_time` fields are recursively filled with `*_time_iso`
- `--format pretty`: 4-column table —— `type | title | edit_time | url`
- `title_highlighted` / `summary_highlighted` may contain `<h>` / `<hb>` highlight tags; the client must strip them before comparison

> **Note**: The `total` field in the response body is not accurate enough (officially confirmed, for reference only). For scenarios requiring precise counts, deduplicate and accumulate based on the actual `results`; do not treat `total` as a promised result count.

<a id="决策规则"></a>
## Decision Rules

- **Identity shortcuts**: When the user says documents "I created / I newly created / I originally created", use `--created-by-me`; when the user says documents "mine / I'm responsible for / I own", use `--mine`. `--mine` has owner semantics: documents transferred away do not count, documents transferred to me do count.
- **Time dimension selection**:
  - "I edited", "I modified" → `--edited-since` / `--edited-until`
  - "I commented on", "I replied to" → `--commented-since` / `--commented-until`
  - "I viewed", "I opened", "recently viewed" → `--opened-since` / `--opened-until`
  - "created on", "newly created" (document-wide dimension, unrelated to "me") → `--created-since` / `--created-until`
- **Scope selection**:
  - "under a certain folder" → `--folder-tokens` (doc-only)
  - "under a certain wiki space" → `--space-ids` (wiki-only)
  - The two cannot be used simultaneously; mixing them will cause an error
- **Identity flags are mutually exclusive**: Do not pass `--mine` and `--creator-ids` at the same time; do not pass `--created-by-me` and `--original-creator-ids` at the same time. The owner dimension and the original creator dimension can be combined, e.g. "I created it then transferred ownership to Wang Wu" uses `--created-by-me --creator-ids ou_wangwu`.
- **Entity completion**:
  - When the user says "in a certain group", first use `lark-im` to look up `chat_id`
  - When the user says "someone's responsible/owned / someone's created / someone's shared" (not oneself), first use `lark-contact` to look up the open_id, then fill in `--creator-ids` / `--original-creator-ids` / `--sharer-ids` according to the semantics
- **Query semantics pushdown**: `--query` supports server-side advanced syntax (`intitle:`, `""`, `OR`, `-`); prefer using it rather than doing a fuzzy search first and then filtering again on the client.
- **Query field boundaries**: Only title fragments, business terms, project names, meeting names, and file content keywords should go into `--query`. Words that merely describe actions, time ranges, ownership, or counting methods are not keywords; keep `--query ""` and rely on filters.
- **Evidence verification**: List/statistics answers must come from the actual URL/token and type/time fields in the search results; content Q&A must be able to point out which non-polluted candidates were used. When there are no verifiable candidates, first broaden the query or paginate; do not directly fabricate a summary.
- **Time expressions**:
  - Vague relative times ("last half year", "past 30 days", "last week") → `--*-since 6m` / `--*-since 30d` / `--*-since 7d`, do not expand into ISO times
  - **Calendar expressions** ("last month", "last week", "this month", "the year before last", "March this year", etc. with explicit calendar units) → **must compute absolute `YYYY-MM-DD` boundaries** (e.g. "last month" = the 1st of the previous calendar month → the 1st of the current month), **do not approximate as `1m`/`2m`**: in the CLI, `m` is a fixed 30 days and `y` is a fixed 365 days, which differs from the calendar by 0-3 days, and is especially prone to drifting off at month boundaries
  - `"<YYYY-MM-DD>"` in the documentation is a runtime placeholder: compute and replace it based on the current date before executing the command. For example, "this month" should be replaced with the first day of this month and the first day of next month; do not hardcode the month from when the example was generated into the answer
  - Absolute dates → directly `YYYY-MM-DD` or RFC3339
- **Pagination strategy**: By default, only return the first page, and explain `has_more` and the next-page command. When the user explicitly asks for "all / full / keep paginating", continue; when a combined search of title words + body words has not yet found enough valid Top N candidates, check at most 3 pages per the rules above. In other scenarios, the single-round pagination limit is 5 pages.
- **Raw response**: When the user requests "raw data" or "API response", use `--format json`, without client-side precise filtering or summary rewriting.

<a id="权限"></a>
## Permissions

| Operation | Required scope |
|---|---|
| Search cloud space (cloud drive/cloud storage) objects (document / Wiki / Sheets and other resource discovery) | `search:docs:read` |

<a id="常见错误"></a>
## Common Errors

| code | Meaning | Handling |
|---|---|---|
| `99992351` | An open_id in `--creator-ids` / `--original-creator-ids` / `--sharer-ids` is outside the **app's contact visibility scope**, and the server refuses to recognize it | Have the administrator add these users to the app's "contact visibility" authorization in the developer console; or remove the out-of-scope open_id from the parameters. This is not the same as the `search:docs:read` scope —— it is about "which people the app can see" rather than "which API the app can call" |

<a id="时间范围自动裁剪--opened--专有"></a>
## Automatic Time Range Trimming (`--opened-*` only)

The server supports **at most a 3-month** (90-day) window per request for `open_time` filtering. The other three time dimensions (`--edited-*` / `--commented-*` / `--created-*`) are **unaffected**.

Before sending the request, the CLI checks the span from `--opened-since` to the effective `--opened-until` (if not passed, `now` is used):

| Span | Behavior |
|---|---|
| ≤ 90 days | Passed through as-is |
| 91 ~ 365 days | **Automatically trimmed** to the "most recent 90-day slice", and a notice is printed to stderr listing the `--opened-since` / `--opened-until` parameter values for all remaining slices |
| > 365 days | Directly reports a validation error, requiring the range to be narrowed or split into multiple queries manually |

Notice example (the user originally asked for "the past 8 months", which will be split into 3 slices):

```text
notice: --opened-* window spans 240 days (~8 months), exceeds the server-side 3-month (90-day) limit.
        this query was narrowed to the most recent slice; 3 slices total:
          [slice 1/3 current] --opened-since 2026-01-24T21:54:02+08:00 --opened-until 2026-04-24T21:54:02+08:00
          [slice 2/3]         --opened-since 2025-10-26T21:54:02+08:00 --opened-until 2026-01-24T21:54:02+08:00
          [slice 3/3]         --opened-since 2025-08-27T21:54:02+08:00 --opened-until 2025-10-26T21:54:02+08:00
        pagination: paginate within a slice via --page-token using that slice's --opened-since / --opened-until values verbatim (NOT the original relative time like '1y' / '8m' — relative times re-resolve against time.Now() and would mismatch the page_token); switch to the next slice's --opened-* flags only after has_more=false, and do not carry --page-token across slices.
```

<a id="agent-看到-notice-时的处理"></a>
### How the Agent Should Handle the Notice

**Standard flow (order of pagination × slice):**

1. **Run slice 1** (this request has already been automatically trimmed to this window), and present the results to the user
2. **First paginate within the current slice**: when `has_more = true` is returned and the user wants to see more, change `--opened-since` / `--opened-until` to the **specific time values** given in the `[slice 1/N current]` line of the notice (**do not keep using the original relative value like `--opened-since 1y`** —— the CLI recalculates the window based on `time.Now()` on every call, and running a relative value together with `--page-token` will bind the page_token to a drifting window, causing silent result distortion), add `--page-token` and continue paginating until `has_more = false`
3. **Then switch to the next slice**: after the current slice is fully paginated, if the user still wants "older" results, use the `--opened-since` / `--opened-until` values of slice 2 listed in the notice, **keep all other flags (`--query`, `--doc-types`, `--page-size`, `--sort`……) unchanged, and do not carry `--page-token`**, and send a new request
4. **Proceed in sequence**: after slice 2 is fully paginated, switch to slice 3, and so on
5. When the user is only interested in the most recent period, skip step 3 and beyond —— to avoid meaningless API calls

> `--page-token` is only valid within a single-slice context; when switching slices, do not carry over the `page_token` from the previous slice.

<a id="注意事项"></a>
### Notes

- `--sort` is correct **within a single slice**. Global sorting across slices (e.g. "what I opened in the past year, sorted by edit_time desc") is not guaranteed by the CLI; the agent needs to pull all slices and re-sort on the client before presenting
- Trimming only changes the `open_time` range sent in the request; `--query` / other filters are untouched
- The last (oldest) slice is often less than 90 days, which is normal truncation
