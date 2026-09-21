<a id="slides-history历史版本与回滚"></a>
# slides history (version history and rollback)

Used to view Slides XML presentation version history, roll back by `history_version_id`, and query rollback task status.

`entries[].edit_time` is a UTC RFC3339 time string (for example `2026-06-22T12:24:45Z`). When matching by time, first parse it into a time value, then compare the ordering relationship or time difference.

<a id="安全流程"></a>
## Safe workflow

1. First use the paginated interface `+history-list` to find the `history_version_id` of the target version.
2. If the user specifies a `revision_id`, do not assume it is unique, and do not pass `revision_id` directly to `+history-revert`. First fetch one page and filter candidates in `entries[]` that have the same `revision_id`; if no match is found and `has_more=true`, continue paging with `page_token`; if a candidate is already matched, fetch at most one additional page to fill in possible adjacent candidates that may span pages. Finally, prefer selecting the most suitable entry based on how close the user's target time is to `edit_time`, and take the `history_version_id` of that same entry; if there is no target time, or multiple candidates cannot be reliably distinguished, show the candidate versions to the user (`history_version_id`, `revision_id`, `edit_time`, `name/description`) and roll back only after confirmation.
3. If the user specifies a moment but does not specify `revision_id`, match by `entries[].edit_time`; prefer the most recent history record no later than the target moment, and if it cannot be clearly matched, first confirm the candidate version with the user.
4. Use `+history-revert` to initiate the rollback. The interface returns `task_id` immediately, and the rollback task executes asynchronously on the server side.
5. If it returns `status: running`, save `task_id`, wait according to the returned `poll_after_ms`, and then call `+history-revert-status`. After the task is created successfully, do not initiate the rollback again because a status query failed.
6. Stop polling after the status becomes `done`, `partial_failed`, or `failed`; also stop polling when the overall polling limit is reached, and return `task_id` and the current status to the user.
7. After the rollback completes, use `slides +xml-get` to read the presentation and confirm the content.

<a id="按-revision_id-或时间点回滚"></a>
## Roll back by revision_id or time point

When the user says things like "roll back to revision_id=42" or "restore to yesterday 3 PM's version", the workflow is:

1. Execute `slides +history-list --presentation <presentation>` to get the first page of history records; `+history-list` is a paginated interface, so continue passing `--page-token` to page only when `has_more=true` and more candidates are still needed.
2. If the user provides `revision_id`: first filter the current page for `entries[].revision_id == 用户给出的 revision_id`. If there is no hit and `has_more=true`, continue fetching the next page; if a candidate has already been hit, fetch at most one additional page to fill in adjacent `history_version_id` that may span pages for the same `revision_id`. If the user also provides a target time, choose the candidate whose `edit_time` is closest to the target time; if no target time is provided but there is only one candidate, it can be used directly; if multiple candidates cannot be reliably distinguished, do not choose the first one yourself, show the candidates to the user and confirm.
3. If the user provides only a time: match by `entries[].edit_time`, and choose the most recent entry before the target moment; if the user means "closest to a certain moment", choose the entry with the smallest absolute time difference.
4. Read `history_version_id` from the final matched entry. `history_version_id` corresponds to the server-side `minor_history.version`, which is the ID required by the rollback interface.
5. Execute `slides +history-revert --presentation <presentation> --history-version-id <history_version_id>`.

When confirming candidates, use a format similar to:

```text
The same revision_id matches multiple history versions. Please confirm which one to roll back to:
- history_version_id=11 revision_id=42 edit_time=2026-06-22T12:24:45Z name=...
- history_version_id=12 revision_id=42 edit_time=2026-06-22T12:25:14Z name=...
```

<a id="命令"></a>
## Commands

```bash
# List history versions
lark-cli slides +history-list --presentation "<slides_url_or_token>" --page-size 20

# Page
lark-cli slides +history-list --presentation "<slides_url_or_token>" --page-size 20 --page-token "<page_token>"

# Initiate a rollback task, returning task_id immediately
lark-cli slides +history-revert --presentation "<slides_url_or_token>" --history-version-id 42

# Query rollback task status
lark-cli slides +history-revert-status --presentation "<slides_url_or_token>" --task-id "<task_id>"
```

<a id="参数"></a>
## Parameters

| Command | Parameter | Required | Description |
|-|-|-|-|
| `+history-list` | `--presentation` | Yes | `xml_presentation_id`, Slides URL, or a wiki URL that can be resolved to Slides |
| `+history-list` | `--page-size` | No | Number of records to return, range `1-20`, default `20` |
| `+history-list` | `--page-token` | No | `page_token` returned by the previous page |
| `+history-revert` | `--presentation` | Yes | The same presentation |
| `+history-revert` | `--history-version-id` | Yes | `history_version_id` returned by `+history-list`, must be greater than 0 |
| `+history-revert-status` | `--presentation` | Yes | The same presentation |
| `+history-revert-status` | `--task-id` | Yes | `task_id` returned by `+history-revert` |

<a id="异步轮询策略"></a>
## Asynchronous polling strategy

1. After `+history-revert` returns `task_id`, consider the rollback task to have been created successfully.
2. If `status` is not `running`, do not call the status interface again.
3. If `status` is `running`, wait for the `poll_after_ms` in the response and then call `+history-revert-status`; when `poll_after_ms` is missing, is `0`, or is invalid, wait 10 seconds by default.
4. Continue polling when the status query returns `running`; stop when it returns `done`, `partial_failed`, or `failed`.
5. Unless the user requests otherwise, poll for at most 5 minutes by default. After reaching the limit, stop polling, explain to the user that the task is still running and return `task_id`, and do not describe it as a rollback failure.
6. When a temporary error occurs in the status query, retry at most 3 consecutive times at the same interval; only retry `+history-revert-status`, and do not call `+history-revert` again.
7. After `done`, read the current presentation content for verification.
8. When `partial_failed` or `failed`, display `failed_block_tokens`; unless the user explicitly confirms, do not automatically initiate the rollback again.

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

`status` may be `running`, `done`, `partial_failed`, or `failed`. When the status is `partial_failed` or `failed`, check `failed_block_tokens` first.

<a id="回滚后验证"></a>
## Post-rollback verification

After a successful rollback, you must read the current content once to confirm:

```bash
lark-cli slides +xml-get --presentation "<slides_url_or_token>" --output ./presentation.xml
```
