# mail sent_messages recall


Recall a sent email and query the asynchronous recall result.

<a id="何时使用"></a>
## When to use

After a successful send, if the send response contains `recall_available: true`, it means the email supports recall (typically emails delivered within 24 hours).

- Only perform this when the user explicitly requests a recall.
- If the response has no `recall_available` field, do not proactively mention recall.
- Emails that are scheduled to send and have not actually been sent yet cannot be recalled; use `user_mailbox.drafts cancel_scheduled_send` to cancel the scheduled send instead.
- Recall is an asynchronous operation. A successful return from `recall` only means the request has been accepted; the actual result must be queried via `get_recall_detail`.

<a id="命令"></a>
## Commands

```bash
# Initiate recall
lark-cli mail user_mailbox.sent_messages recall --as user \
  --params '{"user_mailbox_id":"me","message_id":"<message_id>"}'

# Query recall progress
lark-cli mail user_mailbox.sent_messages get_recall_detail --as user \
  --params '{"user_mailbox_id":"me","message_id":"<message_id>"}'
```

<a id="返回值解读"></a>
## Interpreting return values

`recall` returns:

- `recall_status: available` — the recall request has been accepted; query the progress later.
- `recall_status: unavailable` — cannot be recalled; check `recall_restriction_reason`.

`get_recall_detail` returns:

- `recall_status: in_progress` — recall in progress; you can query again later.
- `recall_status: done` — recall complete; check `recall_result` and the details for each recipient.

For specific fields and enums, refer to the schema:

```bash
lark-cli schema mail.user_mailbox.sent_messages.get_recall_detail
```

<a id="典型流程"></a>
## Typical workflow

```bash
# 1. Confirm from the send result that recall is possible
# data.recall_available == true

# 2. Initiate after the user confirms they want to recall
lark-cli mail user_mailbox.sent_messages recall --as user \
  --params '{"user_mailbox_id":"me","message_id":"<message_id>"}'

# 3. Query the final result
lark-cli mail user_mailbox.sent_messages get_recall_detail --as user \
  --params '{"user_mailbox_id":"me","message_id":"<message_id>"}'
```

<a id="相关命令"></a>
## Related commands

- `lark-cli mail +send --confirm-send` — send a new email; the response may contain `recall_available`.
- `lark-cli mail +reply --confirm-send` — send a reply; the response may contain `recall_available`.
- `lark-cli mail +forward --confirm-send` — send a forward; the response may contain `recall_available`.
- `lark-cli mail user_mailbox.messages send_status` — query the send delivery status.
