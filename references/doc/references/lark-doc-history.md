<a id="docs-history历史版本与回滚"></a>
# docs history (historical versions and rollback)

Used to view Docx historical versions, roll back by `history_version_id`, and query rollback task status.

`entries[].edit_time` is an RFC3339 time string (for example `2026-06-22T12:24:45Z`). When matching by time, first parse it into a time value, then compare the ordering relationship or time difference.

<a id="安全约束"></a>
## Safety constraints

- `overwrite` rebuilds the body and block IDs, and cannot guarantee preservation of non-body objects such as comments. When the user asks to preserve these objects, first explain the limitation and confirm.
- When `overwrite` returns a warning or `partial_success`, first verify the latest content. If verification fails or a revision conflict occurs, stop and do not overwrite again.
- Permission, network, or temporary system errors should retain their original error classification and must not be interpreted as the target version not existing.

<a id="按-revision_id-或时间点回滚"></a>
## Roll back by revision_id or time point

1. Use `+history-list` to locate the target record. When more candidates are needed, paginate according to `has_more` and `page_token`.
   - User specifies `revision_id`: filter page by page for records with the same `revision_id`. If there is no hit, you must continue paginating until `has_more=false` before entering fallback; if the hit is at the end of a page, continue reading the next page to collect adjacent candidates with the same `revision_id`. When there are multiple records, choose based on `edit_time`; if they cannot be distinguished, ask the user to confirm.
   - User specifies a time: choose the most recent record not later than the target time; when the user explicitly requests "closest", choose the record with the smallest time difference.
2. After finding the target record, use that record's `history_version_id` to call `+history-revert`. Do not pass `revision_id` to the rollback interface. When `running` is returned, use `+history-revert-status` to query; only `done` indicates success, and all other terminal states should stop and be reported.
3. When there is no target record but the user specified `revision_id`, you may read the target version and restore the body:
   - Use `docs +fetch --doc "<doc>" --revision-id <revision_id> --scope full --detail full --format json` to read the target version. Confirm the document is consistent, the returned `revision_id` matches the target, and `content` is not `<fragment>`.
   - Use `docs +fetch --doc "<doc>" --scope full --detail full --format json` to read the current complete document; its `content` likewise must not be `<fragment>`. If the target and current response have the same `revision_id`, end directly without executing `overwrite`. Otherwise remove the old block IDs from the target `content`, write the body to a relative path under the task directory, then execute `docs +update --doc "<doc>" --command overwrite --revision-id <current_revision_id> --content @target.xml` only once, where `current_revision_id` comes from the current document response. When the target response contains a non-empty JSON object form of `reference_map`, write it to a relative path and append `--reference-map @target-reference-map.json`; otherwise omit that parameter. `+update` does not support `--yes`.
   - Use `docs +fetch --doc "<doc>" --scope full --detail full --format json` to read the latest complete document and verify. Ignore the regenerated block IDs; the body structure, text, links, and referenced resources should match the target version.
4. When the target version is clearly unreadable, stop and report.

When confirming candidates, use a format similar to:

```text
The same revision_id matches multiple historical versions; please confirm which one to roll back to:
- history_version_id=11 revision_id=42 edit_time=2026-06-22T12:24:45Z name=...
- history_version_id=12 revision_id=42 edit_time=2026-06-22T12:25:14Z name=...
```

<a id="命令"></a>
## Commands

```bash
# List historical versions
lark-cli docs +history-list --doc "<docx_url_or_token>" --page-size 20

# Paginate
lark-cli docs +history-list --doc "<docx_url_or_token>" --page-size 20 --page-token "<page_token>"

# Roll back to the specified history_version_id (default wait 30000ms)
lark-cli docs +history-revert --doc "<docx_url_or_token>" --history-version-id 42

# Only initiate the task, do not wait
lark-cli docs +history-revert --doc "<docx_url_or_token>" --history-version-id 42 --wait-timeout-ms 0

# Query rollback task status
lark-cli docs +history-revert-status --doc "<docx_url_or_token>" --task-id "<task_id>"
```

<a id="参数"></a>
## Parameters

| Command | Parameter | Required | Description |
|-|-|-|-|
| `+history-list` | `--doc` | Yes | Docx URL/token, or a wiki URL resolvable to Docx |
| `+history-list` | `--page-size` | No | Number of records to return, range `1-20`, default `20` |
| `+history-list` | `--page-token` | No | `page_token` returned from the previous page |
| `+history-revert` | `--doc` | Yes | Docx URL/token, or a wiki URL resolvable to Docx |
| `+history-revert` | `--history-version-id` | Yes | `history_version_id` returned by `+history-list`, must be greater than 0 |
| `+history-revert` | `--wait-timeout-ms` | No | Number of milliseconds to wait for rollback completion, range `0-30000`, default `30000` |
| `+history-revert-status` | `--doc` | Yes | The same document |
| `+history-revert-status` | `--task-id` | Yes | `task_id` returned by `+history-revert` |

<a id="返回值要点"></a>
## Key return values

`+history-list` returns:

```json
{
  "entries": [
    {
      "revision_id": 42,
      "history_version_id": "11",
      "edit_time": "2026-06-22T12:24:45Z",
      "type": 1,
      "name": "版本名",
      "description": "版本说明",
      "editor_ids": ["ou_xxx"]
    }
  ],
  "has_more": true,
  "page_token": "page_token"
}
```

`+history-revert` returns:

```json
{
  "task_id": "task_xxx",
  "status": "running",
  "history_version_id": "11",
  "poll_after_ms": 10000
}
```

`+history-revert-status` returns:

```json
{
  "status": "partial_failed",
  "history_version_id": "11",
  "failed_block_tokens": ["blk_xxx"]
}
```

`status` may be `running`, `done`, `partial_failed`, `failed`. When the status is `partial_failed` or `failed`, check `failed_block_tokens` first.
