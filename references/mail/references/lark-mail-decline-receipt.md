# mail +decline-receipt


Close the read receipt request banner for a received email, **but do not send a receipt to the sender**. **This command is only used when the other party's email requested a read receipt (`READ_RECEIPT_REQUEST` label, system ID `-607`)**. It aligns with the "Don't send" button to the right of the read receipt banner in the Feishu client.

This module corresponds to shortcut: `lark-cli mail +decline-receipt`.

<a id="使用时机"></a>
## When to use

Decision branch: when fetching mail and seeing the `READ_RECEIPT_REQUEST` label → **you must first ask the user**:

- The user is willing to tell the other party "read" → `+send-receipt`
- The user is unwilling to tell them but wants to dismiss the prompt → `+decline-receipt` (this command)
- The user neither wants to send a receipt nor cares about the banner → do nothing

<a id="命令"></a>
## Command

```bash
# Standard usage
lark-cli mail +decline-receipt --message-id <message-id>

# Specify mailbox (shared mailbox scenario)
lark-cli mail +decline-receipt --mailbox shared@example.com --message-id <message-id>

# Dry Run (no actual changes)
lark-cli mail +decline-receipt --message-id <message-id> --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Default | Description |
|------|------|------|------|
| `--message-id <id>` | Yes | — | Message ID of the original email that requested a read receipt |
| `--mailbox <email>` | No | `me` | Mailbox that owns the email |
| `--dry-run` | No | — | Only print the request, do not execute |

> Note that this command has no `--yes` — it only removes a local label and does not send any external email. Its Risk level is `write` rather than `high-risk-write`.

<a id="行为细节"></a>
## Behavior details

- First `fetchFullMessage` to fetch the original email for validation: if `label_ids` does not contain `READ_RECEIPT_REQUEST` (nor the numeric `-607`), directly return `already_cleared: true`, **without sending a request**; idempotent.
- When the label exists, call `PUT /user_mailboxes/<mailbox>/messages/<id>/modify` (`user_mailbox.message.modify`), with body `{"remove_label_ids":["READ_RECEIPT_REQUEST"]}`.
- **Does not send any outgoing email**: equivalent to the "Don't send" button in the Feishu client — it only clears the local label, and the sender receives no notification.

<a id="返回值"></a>
## Return value

Label already cleared (no side effects):

```json
{
  "ok": true,
  "data": {
    "message_id":             "原邮件 message ID",
    "decline_receipt_for_id": "原邮件 message ID",
    "declined":               false,
    "already_cleared":        true
  }
}
```

The label was actually removed this time:

```json
{
  "ok": true,
  "data": {
    "message_id":             "原邮件 message ID",
    "decline_receipt_for_id": "原邮件 message ID",
    "declined":               true
  }
}
```

<a id="典型场景"></a>
## Typical scenarios

<a id="场景-1用户选择不发回执"></a>
### Scenario 1: The user chooses not to send a receipt

```bash
# 1. Fetch the email
lark-cli mail +message --message-id msg-1 --format json | jq '.data.label_ids'
# → ["UNREAD", "READ_RECEIPT_REQUEST"]

# 2. Prompt the user:
#    "This email from alice@example.com requests a read receipt. Subject: 《Weekly Report》.
#     Would you like to reply to tell the other party you have read it?
#     You can also choose: don't send a receipt, but close this prompt."

# 3. The user chose "Don't send" →
lark-cli mail +decline-receipt --message-id msg-1
```

<a id="场景-2幂等重跑"></a>
### Scenario 2: Idempotent rerun

```bash
# Remove the label the first time
lark-cli mail +decline-receipt --message-id msg-1
# → {"declined": true}

# Run it again — it will not error, and it will not send another modify request
lark-cli mail +decline-receipt --message-id msg-1
# → {"declined": false, "already_cleared": true}
```

<a id="不要这样做"></a>
## Don't do this

- ❌ Automatically decline on the user's behalf — the mirror side of the privacy rule: the "silence" of not sending a receipt is also the user's choice
- ❌ Use `+decline-receipt` as "mark as read" — it only removes one label, `READ_RECEIPT_REQUEST`, and does not change `UNREAD`
- ❌ Call it on an email without the `READ_RECEIPT_REQUEST` label — although it idempotently returns `already_cleared`, sending an extra GET is meaningless

<a id="相关命令"></a>
## Related commands

- `lark-cli mail +send-receipt` — agree to the receipt (sends a system-style read receipt email)
- `lark-cli mail +message` — fetch a single email (check `READ_RECEIPT_REQUEST` in `label_ids`)
- `lark-cli mail +send --request-receipt` — the reverse: **request** a receipt from someone else
