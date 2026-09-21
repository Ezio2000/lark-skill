
# mail +triage


View inbox email summaries (date / from / subject / message_id) for quick browsing and deciding which email to read.

<a id="用法"></a>
## Usage

```bash
# Default: inbox emails (default 20 items, default table format)
lark-cli mail +triage

# View unread inbox
lark-cli mail +triage --filter '{"folder":"inbox","is_unread":true}'
lark-cli mail +triage --folder INBOX --is-unread
lark-cli mail +triage --filter is_unread

# Full-text search
lark-cli mail +triage --query "合同审批"

# Search by sender / subject
lark-cli mail +triage --filter '{"from":["boss@example.com"],"subject":"季度报告"}'

# Search by time range (e.g. "last week's emails")
lark-cli mail +triage --query "项目评审" --filter '{"time_range":{"start_time":"2026-03-16T00:00:00+08:00","end_time":"2026-03-22T23:59:59+08:00"}}'

# Specify folder
lark-cli mail +triage --filter '{"folder":"sent"}'
lark-cli mail +triage --filter folder=sent
lark-cli mail +triage --folder sent

# System labels (can be passed via folder or label, automatically converted to folder during search)
lark-cli mail +triage --filter '{"folder":"flagged"}'
lark-cli mail +triage --filter '{"label":"important"}'
lark-cli mail +triage --filter '{"label":"重要邮件"}'

# json/data format can be used with jq for processing
lark-cli mail +triage --format json | jq '.messages[].subject'

# Pagination: fetch 10 items first, then use page_token to paginate
lark-cli mail +triage --max 10 --format json
# Output includes page_token, pass it in the next request
lark-cli mail +triage --page-token 'list:FfccvoqPd...' --max 10 --format json

# --page-size is an alias for --max
lark-cli mail +triage --page-size 10
```

<a id="参数"></a>
## Parameters

| Parameter | Default | Description |
|------|------|------|
| `--filter <filter>` | — | Filter conditions (see field descriptions below) |
| `--folder <name-or-id>` | — | Filter by folder name or system folder ID; equivalent to setting `filter.folder` |
| `--folder-id <id>` | — | Filter by explicit folder ID; equivalent to setting `filter.folder_id` |
| `--is-unread` | — | Show unread only; equivalent to setting `filter.is_unread=true` |
| `--query <text>` | — | Full-text search keyword |
| `--format <mode>` | `table` | `table` / `json` / `data` (both `json` and `data` output an object containing pagination info) |
| `--max <n>` | `20` | Maximum number of results to return (1-400), internally auto-paginates |
| `--page-size <n>` | — | Alias for `--max`; when specified multiple times, the last value takes effect |
| `--page-token <token>` | — | Pagination token returned from the previous response; when passed in, fetching continues from that position. The token has a `search:` or `list:` prefix indicating the source path, and they cannot be mixed |
| `--labels` | — | In table format, additionally display the labels column |
| `--mailbox <id>` | `me` | Email address |

<a id="--filter-支持的字段"></a>
### Fields supported by `--filter`

`--filter` has three forms:

- JSON object: `--filter '{"folder":"INBOX","is_unread":true}'`, used to combine multiple fields or pass array/object fields
- Single `key=value`: `--filter folder=INBOX`, `--filter is_unread=true`
- Bare unread shortcut: `--filter is_unread`

For multiple filter conditions, use a JSON object; the comma-joined key=value form like `folder=INBOX,is_unread=true` is not supported.

| Field | Type | Description |
|------|------|------|
| `folder` | string | Folder name filter. Fixed values for system folders: `inbox`/`sent`/`draft`/`trash`/`spam`/`archive`/`priority`/`flagged`/`other`/`scheduled`, custom folder names are also supported. Subfolders must use the `parent_name/child_name` format, which can be viewed via the folder list API |
| `folder_id` | string | Folder ID, takes priority over `folder`. System values: `INBOX`/`SENT`/`DRAFT`/`TRASH`/`SPAM`/`ARCHIVED`, custom folders use numeric IDs |
| `label` | string | Custom label name filter. Sub-labels must use the `parent_name/child_name` format, which can be viewed via the label list API |
| `label_id` | string | Label ID, takes priority over `label`. Custom labels use numeric IDs |
| `is_unread` | boolean | Whether unread |
| `from` | string[] | Sender |
| `to` | string[] | Recipient |
| `subject` | string | Subject keyword |
| `has_attachment` | boolean | Whether it has attachments |
| `time_range` | object | Time range `{"start_time":"2026-01-01T00:00:00+08:00","end_time":"..."}` |

> **System label notes**: `IMPORTANT`/`FLAGGED`/`OTHER` can be passed via `folder` or `label` (Chinese aliases `重要邮件`/`已加旗标`/`其他邮件` and search names `priority`/`flagged`/`other` are also supported). During search they are automatically converted to the folder field, and during listing they are automatically converted to label_id. The label list API does not return these three system labels.
>
> **⚠️ Note**: To query unread, use `--is-unread`, `--filter is_unread`, `--filter is_unread=true`, or the JSON form `"is_unread":true`.
You can run `mail +triage --print-filter-schema` to view the complete field descriptions.

<a id="输出"></a>
## Output

### `--format json` / `--format data`

Both have the same output format, an object containing pagination info:

```json
{
  "messages": [
    {
      "message_id": "SEU2...",
      "mailbox_id": "me",
      "date": "Fri, 21 Mar 2026 11:40:00 +0800",
      "from": "Alice <alice@example.com>",
      "subject": "Weekly update",
      "labels": "INBOX,UNREAD"
    }
  ],
  "mailbox_id": "me",
  "count": 20,
  "has_more": true,
  "page_token": "list:FfccvoqPd_loLhtcRx8cx..."
}
```

- `mailbox_id`: Current mailbox identifier, used to pass to `mail +message --mailbox` to maintain shared mailbox context
- `has_more`: Whether there is a next page
- `page_token`: Pass to `--page-token` to get the next page; an empty string means the end has been reached
- Token prefix `search:` / `list:` identifies the source API path, and they cannot be mixed

<a id="table-格式"></a>
### `table` format

`page_token` information is output to stderr, automatically carrying `--query`/`--filter`/`--folder`/`--folder-id`/`--is-unread`/`--mailbox` parameters for easy continuation:
```text
15 message(s)
next page: mail +triage --query 'Contract Approval' --page-token 'search:abc123...'
tip: read full content: single message use mail +message --message-id <id>; multiple messages use mail +messages --message-ids <id1>,<id2>,<id3>
```

In shared mailbox scenarios, `--mailbox` automatically appears in the continuation and tip:
```text
next page: mail +triage --mailbox 'shared@example.com' --query 'Contract Approval' --page-token 'search:abc123...'
tip: read full content: single message use mail +message --mailbox 'shared@example.com' --message-id <id>; multiple messages use mail +messages --mailbox 'shared@example.com' --message-ids <id1>,<id2>,<id3>
```

<a id="搜索分页注意事项"></a>
### Search pagination notes

Pagination results for the search path (using `--query` or filters such as `from`/`to`/`subject`) remain consistent **within the same pagination chain** (no duplicates, no omissions). However, independent searches initiated with different `--max` values may return different orderings; this is inherent behavior of the search API. The list path (only `folder`/`label` filters) has no such limitation.

<a id="参考"></a>
## References

- [lark-mail](../index.md) — Mail domain overview
- [lark-mail-watch](lark-mail-watch.md) — Real-time monitoring of new emails
