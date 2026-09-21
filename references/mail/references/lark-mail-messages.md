# mail +messages


Read the full content of multiple emails at once by passing a comma-separated list of `message_id`.

More than 20 IDs can be passed directly to the CLI; the CLI automatically splits them into batches of 20 and merges the output, so there is no need to split batches manually, and do not call `+message` in a per-email loop.

This shortcut is the batch version of `mail +message`. Each returned `messages[]` item uses the same normalized structure as `+message`: safe metadata fields are passed through directly, while the body and auxiliary fields are derived by the shortcut.

Prefer this shortcut because:
- The body field is already base64url-decoded
- The output structure of each email is already normalized
- Unavailable message IDs are explicitly listed

This module corresponds to shortcut `lark-cli mail +messages`; each returned email is normalized and output using the same rules as `+message`.

<a id="命令"></a>
## Command

```bash
# Read multiple emails (includes HTML body by default)
lark-cli mail +messages --message-ids <id1>,<id2>,<id3>

# Plain text body only (smaller payload, suitable for AI processing)
lark-cli mail +messages --message-ids <id1>,<id2>,<id3> --html=false

# Specify mailbox
lark-cli mail +messages --mailbox user@example.com --message-ids <id1>,<id2>

# JSON output
lark-cli mail +messages --message-ids <id1>,<id2> --format json

# Dry Run
lark-cli mail +messages --message-ids <id1>,<id2> --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Default | Description |
|------|------|--------|------|
| `--message-ids <id1>,<id2>,<id3>` | Yes | — | Comma-separated list of email IDs; when there are more than 20 IDs, the CLI automatically splits into batches of 20 and merges the output |
| `--mailbox <email>` | No | Current user | Email address (`user_mailbox_id`) |
| `--html` | No | true | Whether to return the HTML body (`false` returns plain text only, reducing bandwidth) |
| `--format <mode>` | No | json | Output format: `json` (default) / `pretty` / `table` / `ndjson` / `csv` |
| `--dry-run` | No | — | Print the request only, do not execute |

<a id="返回值"></a>
## Return Value

On success, returns a `{"ok": true, "data": ...}` structure, where the `data` field contains:

```json
{
  "messages": [
    { "...与 +message 输出结构相同..." }
  ],
  "total": 1,
  "unavailable_message_ids": ["msg-2"]
}
```

Top-level fields:

| Field | Description |
|------|------|
| `messages` | The returned email list, in the same order as the requested `--message-ids`, excluding IDs not returned by the API |
| `total` | The number of emails successfully returned |
| `unavailable_message_ids` | The list of IDs that were requested but for which the Mail API did not return details |

Each `messages[]` item uses the same structure as [`mail +message`](./lark-mail-message.md#返回值). For the full field list, see [`+message` field descriptions](./lark-mail-message.md#字段说明) and [`+message` security_level](./lark-mail-message.md#security_level).

> Note: Use `--format json` to get structured output. All JSON output is uniformly wrapped in a `{"ok": true, "data": ...}` structure.

<a id="注意事项"></a>
## Notes

- **JSON output can be used directly** and can be read directly without additional encoding conversion.
- When you only need to read a single email, use `+message`.
- The CLI splits into one call per 20 IDs and merges the output, so there is no need to manually split requests for large lists.
- In JSON output, `<` / `>` within `messages[].body_html` may appear as `\u003c` / `\u003e` (JSON-safe escaping; the content is unchanged and `jq -r` can restore it).
- `mail +messages` returns attachment metadata only. If a later step needs a download URL, call the native attachment URL API for the specific `message_id` and `attachment_ids`.
- As with `+message`, both regular attachments and inline images appear in `messages[].attachments[]`, using the same `user_mailbox.message.attachments download_url` API.

<a id="典型场景"></a>
## Typical Scenarios

<a id="批量摘要多封已知邮件"></a>
### Batch-summarize multiple known emails

```bash
# Read multiple emails at once
lark-cli mail +messages --message-ids <id1>,<id2>,<id3> --html=false --format json

# Have the LLM analyze .data.messages[].body_plain_text and generate a grouped summary
```

<a id="对比多封邮件内容后决策"></a>
### Make a decision after comparing the content of multiple emails

```bash
# Get the normalized output of multiple emails
lark-cli mail +messages --message-ids <id1>,<id2> --html=false --format json

# Check subject/from/body_preview or body_plain_text to compare intent and next actions
```

<a id="相关命令"></a>
## Related Commands

- `lark-cli mail +message` — Read a single email
- `lark-cli mail +thread` — Read all emails in a conversation
- `lark-cli mail +reply` — Reply to an email
- `lark-cli mail +forward` — Forward an email
- `lark-cli mail user_mailbox.message.attachments download_url` — Get email attachment/image download URLs on demand
