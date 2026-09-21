# mail +thread-trash


When you already have `thread_id` and want to soft-delete emails by conversation, prefer `mail +thread-trash`. Before executing, obtain the real `thread_id` and verify the existing deletion authorization; only let the user choose when the scope is unclear.

If the target is a specific email `message_id` rather than an entire conversation, use [`mail +message-trash`](./lark-mail-message-trash.md).

<a id="命令"></a>
## Command

```bash
# Soft-delete multiple conversations
lark-cli mail +thread-trash --thread-ids <thread_id1>,<thread_id2> --yes

# Specify a public mailbox or shared mailbox
lark-cli mail +thread-trash --mailbox shared@example.com --thread-ids <thread_id> --yes

# When using bot identity, the mailbox must be explicitly specified
lark-cli mail +thread-trash --as bot --mailbox user@example.com --thread-ids <thread_id> --yes

# Dry Run: preview the request only, do not execute
lark-cli mail +thread-trash --thread-ids <thread_id1> --thread-ids <thread_id2> --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--mailbox <email>` | No | The mailbox the conversation belongs to; defaults to `me`; when using `--as bot`, the email address must be explicitly passed |
| `--thread-ids <ids>` | Yes | List of conversation IDs; supports comma separation and repeated parameters; automatically submitted in batches when more than 20 |
| `--yes` | Required at execution | Confirmation for high-risk write operations. Only add after the user confirms the deletion preview |

<a id="注意事项"></a>
## Notes

- `thread_id` must come from real query results such as `+triage`, `+message`, `+thread`, conversation lists, or search; do not use numeric primary keys or placeholders.
- Soft deletion is a high-risk write operation. First show the deletion preview using real query results, including the number of affected conversations and key email summaries; after the user confirms, execute and add `--yes`.
- The command parses comma separation and repeated flags locally, deduplicates in order of first appearance, and submits in batches of 20.
- If a single batch request fails, all `thread_id` in that batch are recorded with the same failure reason; subsequent batches continue to execute.

<a id="返回值"></a>
## Return Value

Example return:

```json
{
  "success_thread_ids": ["thread_id1"],
  "failed_thread_ids": [
    {"thread_id": "thread_id2", "reason": "api error"}
  ]
}
```

<a id="原生-api-适用场景"></a>
## When to Use the Native API

Only call `mail user_mailbox.threads batch_trash` directly when you need to precisely reproduce backend/API behavior for diagnostics. For ordinary conversation soft deletion, prefer this shortcut, because it has built-in ID validation, batching, batch output, dry-run preview, and `--yes` confirmation.

<a id="相关命令"></a>
## Related Commands

- `lark-cli mail +triage` — browse email summaries and obtain `thread_id`
- `lark-cli mail +thread` — read the full conversation
- `lark-cli mail +message-trash` — soft-delete specific emails by `message_id`
- `lark-cli mail +thread-modify` — modify conversation labels or move folders by `thread_id`
