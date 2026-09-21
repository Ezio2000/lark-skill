# mail +thread-modify


If the operation target is a specific email `message_id`, not an entire thread, use [`mail +message-modify`](./lark-mail-message-modify.md).

<a id="命令"></a>
## Command

```bash
# Add the unread label to multiple threads
lark-cli mail +thread-modify --thread-ids <thread_id1>,<thread_id2> --add-label-ids unread

# Remove the starred label
lark-cli mail +thread-modify --thread-ids <thread_id> --remove-label-ids FLAGGED

# Archive threads
lark-cli mail +thread-modify --thread-ids <thread_id> --add-folder archive

# Specify a public mailbox or shared mailbox
lark-cli mail +thread-modify --mailbox shared@example.com --thread-ids <thread_id> --add-folder folder_xxx

# When using the bot identity, the mailbox must be explicitly specified
lark-cli mail +thread-modify --as bot --mailbox user@example.com --thread-ids <thread_id> --add-folder archive

# Dry Run: preview the request only, do not execute
lark-cli mail +thread-modify --thread-ids <thread_id> --add-label-ids custom_label_id --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--mailbox <email>` | No | The mailbox the thread belongs to; defaults to `me`; when using `--as bot`, the email address must be explicitly passed |
| `--thread-ids <ids>` | Yes | List of thread IDs; supports comma separation and repeated arguments; automatically submitted in batches when more than 20 |
| `--add-label-ids <ids>` | No | Label ID to add. For system labels, pass `unread` / `important` / `other` / `flagged`; for custom labels, pass the label ID |
| `--remove-label-ids <ids>` | No | Label ID to remove. Must not pass duplicate labels with `--add-label-ids` |
| `--add-folder <id>` | No | Folder to move to. For system folders, pass `inbox` / `sent` / `spam` / `archive` / `archived`; for custom folders, pass the folder ID |

At least one of `--add-label-ids`, `--remove-label-ids`, `--add-folder` must be passed.

`TRASH` is not allowed to be passed as the target folder through this shortcut. To soft-delete a thread, use [`mail +thread-trash`](./lark-mail-thread-trash.md), and add `--yes` to execute after user confirmation.

`READ_RECEIPT_REQUEST` / `read_receipt_request` are not allowed to be added or removed through this shortcut. A read receipt request must first read the specific message, confirm the user's intent, and then use [`mail +send-receipt`](./lark-mail-send-receipt.md) or [`mail +decline-receipt`](./lark-mail-decline-receipt.md).

<a id="注意事项"></a>
## Notes

- `thread_id` must come from real query results such as `+triage`, `+message`, `+thread`, thread lists, or search; do not use numeric primary keys or placeholders.
- The command parses comma-separated and repeated flags locally, deduplicates in order of first appearance, and submits in batches of 20.
- When a single batch request fails, all `thread_id` in that batch are recorded with the same failure reason; subsequent batches continue to execute.

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
## Native API Use Cases

Only call `mail user_mailbox.threads batch_modify` directly when you need to precisely reproduce backend/API behavior for diagnosis, or when you need a request structure not exposed by the shortcut. For ordinary thread organization, prefer this shortcut, because it has built-in ID validation, batching, batch output, and dry-run preview.

<a id="相关命令"></a>
## Related Commands

- `lark-cli mail +triage` — Browse email summaries, obtain `thread_id`
- `lark-cli mail +thread` — Read the full thread
- `lark-cli mail +message-modify` — Modify a specific email by `message_id`
- `lark-cli mail +thread-trash` — Soft-delete a thread by `thread_id`
