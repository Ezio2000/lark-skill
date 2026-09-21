# mail +thread


Read all emails in the specified thread, sorted in ascending order by send time. Each email has the same structure as `+message`.

In terms of implementation, each `messages[]` item is constructed in the same way as `mail +message`: security metadata fields are passed through directly, while body/attachment auxiliary fields are derived by the shortcut. Each email uses a unified `attachments[]` list, covering both regular attachments and inline images.

This module corresponds to shortcut `lark-cli mail +thread`, and internally calls:
- `GET /open-apis/mail/v1/user_mailboxes/{mailbox}/threads/{thread_id}` — retrieves the full content of all emails in the thread

<a id="命令"></a>
## Command

```bash
# Read the full thread
lark-cli mail +thread --thread-id <thread-id>

# Plain text body only (smaller payload, suitable for AI processing)
lark-cli mail +thread --thread-id <thread-id> --html=false

# Specify mailbox
lark-cli mail +thread --mailbox user@example.com --thread-id <thread-id>

# JSON output
lark-cli mail +thread --thread-id <thread-id> --format json

# Dry Run
lark-cli mail +thread --thread-id <thread-id> --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Default | Description |
|------|------|--------|------|
| `--thread-id <id>` | Yes | — | Thread ID (`thread_id`) |
| `--mailbox <email>` | No | Current user | Email address (`user_mailbox_id`) |
| `--html` | No | true | Whether to return the HTML body (`false` returns plain text only, reducing bandwidth) |
| `--format <mode>` | No | json | Output format: `json` (default) / `pretty` / `table` / `ndjson` / `csv` |
| `--dry-run` | No | — | Print the request only, do not execute |

<a id="返回值"></a>
## Return Value

On success, returns a `{"ok": true, "data": ...}` structure, where the `data` field contains:

```json
{
  "thread_id":     "会话 ID",
  "message_count": 2,
  "messages": [
    { "...与 +message 输出结构相同（最早的在前）..." },
    { "......" }
  ]
}
```

Top-level fields:

| Field | Description |
|------|------|
| `thread_id` | The thread ID requested by `--thread-id` |
| `message_count` | Number of emails successfully retrieved |
| `messages` | List of emails sorted in ascending order by `internal_date` (earliest first) |

Each `messages[]` item uses the same structure as [`mail +message`](./lark-mail-message.md#返回值). For the complete field list, see [`+message` field descriptions](./lark-mail-message.md#字段说明) and [`+message` security_level](./lark-mail-message.md#security_level).

> Note: Use `--format json` to get structured output. All JSON output is uniformly wrapped in a `{"ok": true, "data": ...}` structure.

<a id="注意事项"></a>
## Notes

- **JSON output can be used directly**; it can be read directly without additional encoding conversion.
- In JSON output, `<` / `>` within `messages[].body_html` may appear as `\u003c` / `\u003e` (JSON-safe escaping; content is unchanged and `jq -r` can restore it).
- `mail +thread` no longer retrieves attachment/image download URLs when reading a thread. If subsequent steps require URLs, call the native attachment URL API for the specific `message_id` and `attachment_ids`.
- As with `+message`, both regular attachments and inline images appear in `messages[].attachments[]`, using the same `user_mailbox.message.attachments download_url` API.
- To view the raw HTML of an email:

```bash
lark-cli mail +thread --thread-id <thread_id> --format json | jq -r '.data.messages[0].body_html'
```

<a id="典型场景"></a>
## Typical Scenarios

<a id="查看会话时间线--生成摘要"></a>
### View thread timeline → generate summary

```bash
# 1. Get thread_id from an email
lark-cli mail +message --message-id <id> --html=false --format json | jq '.data.thread_id'

# 2. Read the full thread (plain text only)
lark-cli mail +thread --thread-id <thread_id> --html=false --format json

# 3. Have the LLM analyze messages[].body_plain_text and generate a thread summary
```

<a id="回复会话中最新一封邮件"></a>
### Reply to the latest email in the thread

```bash
# Get the message_id of the latest email
lark-cli mail +thread --thread-id <thread_id> --html=false --format json | \
  jq '.data.messages[-1].message_id'

# Reply
lark-cli mail +reply --message-id <last_message_id> --body "..."
```

<a id="相关命令"></a>
## Related Commands

- `lark-cli mail +message` — read a single email
- `lark-cli mail +reply` — reply to an email
- `lark-cli mail +forward` — forward an email
- `lark-cli mail user_mailbox.message.attachments download_url` — retrieve email attachment/image download URLs on demand
- `lark-cli mail user_mailbox.messages list` — list inbox emails (to get `thread_id`)
