# mail +forward


Forward a specified email, with automatic handling of:
- Subject prefix `Fwd: ` (not duplicated if the prefix is already present)
- Automatic assembly of a standard "Forwarded message" block (From/Date/Subject/To + original text)
- Support for plain text and HTML forwarding

> **Draft by default**: `+forward` saves as a draft by default and does not send immediately. To send immediately, add the `--confirm-send` parameter (use only after the user has explicitly confirmed).

This module corresponds to the shortcut: `lark-cli mail +forward`.

<a id="critical--发送工作流必须遵循"></a>
## CRITICAL — Sending workflow (must be followed)

**CRITICAL - Before editing email content, you MUST first use the Read tool to read [lark-mail-html.md](lark-mail-html.md), which contains the email writing guidelines**

This command by default **only saves a draft** and does not send the email. Forwarding sends the original email content to new recipients. When sending is needed, there are two compliant approaches:

**Approach A (recommended)** — Create a forwarding draft (without `--confirm-send`):
```bash
lark-cli mail +forward --message-id <邮件ID> --to '<收件人>'
```
→ Returns `draft_id`

Show the user a forwarding summary (the forwarded email, recipients, additional notes); if the user wants to preview the result first, guide them to view the draft in Feishu Mail.

After the user explicitly agrees, send the draft:
```bash
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<Step 1 返回的 draft_id>"}'
```

**Approach B (permitted)** — When the user has already explicitly confirmed the recipients and content, you may directly use `--confirm-send` to send immediately.

**It is forbidden to send without the user's explicit consent, whether sending a draft or directly using `--confirm-send`.**

<a id="命令"></a>
## Commands

```bash
# Forward email (saved as a draft by default) — HTML recommended
lark-cli mail +forward --message-id <邮件ID> --to 'alice@example.com' --body '<p>FYI，请看下面原邮件。</p>'

# Forward with additional notes + CC (draft)
lark-cli mail +forward --message-id <邮件ID> --to 'alice@example.com' --cc 'bob@example.com' --body '<b>请参考</b>'

# Insert inline images when forwarding (recommended: use relative paths directly, resolved automatically)
lark-cli mail +forward --message-id <邮件ID> --to 'alice@example.com' --body '<p>详见图示：<img src="./logo.png" /></p>'

# Plain text forwarding (use only when the content is extremely simple)
lark-cli mail +forward --message-id <邮件ID> --to 'alice@example.com'

# Confirm sending (use only after the user has explicitly confirmed)
lark-cli mail +forward --message-id <邮件ID> --to 'alice@example.com' --confirm-send

# Dry Run (only prints the request, does not send)
lark-cli mail +forward --message-id <邮件ID> --to 'alice@example.com' --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--message-id <id>` | Yes | ID of the email to forward |
| `--to '<email>'` | Yes | Recipient email address. For multiple recipients, pass `--to` repeatedly, one address at a time, and wrap the parameter value in single quotes |
| `--body <text>` | No | Additional note text to attach when forwarding. HTML is recommended for rich text formatting; plain text is also supported. HTML is auto-detected based on the forwarding body and the original email body. Use `--plain-text` to force plain text mode. Supports `<img src="./local.png" />` relative paths being automatically resolved as inline images (only relative paths are supported, absolute paths are not). Mutually exclusive with `--body-file` |
| `--body-file <path>` | No | Read the forwarding note HTML from a file (relative path, limited to the cwd subtree). Mutually exclusive with `--body`. File size limit 32 MB |
| `--from <email>` | No | Sender email address (EML From header). When sending with an alias (send_as), set this to the alias address and use `--mailbox` to specify the mailbox it belongs to. By default, the mailbox's primary address is read |
| `--mailbox <email>` | No | Mailbox address, specifies the mailbox the draft belongs to (defaults to `--from`, then falls back to `me`). Used when the sender (`--from`) differs from the mailbox. Available mailboxes can be queried via `accessible_mailboxes` |
| `--cc '<email>'` | No | CC email address. For multiple CCs, pass `--cc` repeatedly, one address at a time, and wrap the parameter value in single quotes |
| `--bcc '<email>'` | No | BCC email address. For multiple BCCs, pass `--bcc` repeatedly, one address at a time, and wrap the parameter value in single quotes. Incompatible with `--event-*` (see the `+send` calendar invitation constraints) |
| `--plain-text` | No | Force plain text mode, ignoring all HTML auto-detection. Cannot be used together with `--inline`. In plain text mode, a plain text signature is also automatically appended (HTML signatures are converted via `PlainTextFromHTML`, and inline images are discarded) |
| `--attach '<path>'` | No | Attachment file path. For multiple attachments, pass `--attach` repeatedly, one relative path at a time, and wrap the parameter value in single quotes; they are appended after the original email's attachments in the order passed. When attachments cause the total EML size to exceed 25 MB, the excess is automatically uploaded as large attachments (a download card is inserted for HTML emails, and a download link is appended for plain text emails). Single file limit 3 GB |
| `--inline '<json>'` | No | Advanced usage: manually specify the inline image CID mapping. For multiple inline images, pass `--inline` repeatedly, one JSON object at a time, wrapped in single quotes: `'{"cid":"mycid","file_path":"./logo.png"}'`. `file_path` must be a relative path; the CID should be unique, for example a random hexadecimal string; reference it in the body with `<img src="cid:mycid">`. It is recommended to use `<img src="./path" />` directly in `--body` (resolved automatically). Cannot be used together with `--plain-text` |
| `--signature-id <id>` | No | Signature ID. Appends the mailbox signature between the forwarding body and the quoted block. Run `mail +signature` to view available signatures. Mutually exclusive with `--no-signature` |
| `--no-signature` | No | Skip automatic appending of the default signature. Mutually exclusive with `--signature-id`; using both returns a parameter validation error (exit code 2) |
| `--priority <level>` | No | Email priority: `high`, `normal`, `low`. When omitted or set to `normal`, no priority is set |
| `--event-summary <text>` | No | Calendar title. Setting this parameter embeds a calendar invitation in the email. `--event-start` and `--event-end` must also be set |
| `--event-start <time>` | Conditionally required | Calendar start time (ISO 8601) |
| `--event-end <time>` | Conditionally required | Calendar end time (ISO 8601) |
| `--event-location <text>` | No | Calendar location |
| `--confirm-send` | No | Confirm sending the forward (by default only saves a draft). Use only after the user has explicitly confirmed |

> **Calendar constraints**: `--event-*` and `--send-time` cannot be used together; `--to` and `--cc` recipients automatically become calendar participants (ATTENDEE), while `--bcc` recipients are not counted as participants.
| `--send-time <timestamp>` | No | Scheduled send time, Unix timestamp (seconds). Must be at least the current time + 5 minutes. Used together with `--confirm-send` to schedule email sending |
| `--request-receipt` | No | Request a read receipt (RFC 3798 Message Disposition Notification). Writes the `Disposition-Notification-To: <sender>` header in the outbound EML. The recipient's email client may show a prompt, send automatically, or ignore it — delivery is not guaranteed |
| `--dry-run` | No | Only prints the request, does not execute |

<a id="返回值"></a>
## Return values

Default (draft mode):
```json
{
  "ok": true,
  "data": {
    "draft_id": "草稿ID",
    "tip": "draft saved. To send: lark-cli mail user_mailbox.drafts send --params '{...}'"
  }
}
```

`--confirm-send` mode:
```json
{
  "ok": true,
  "data": {
    "message_id": "邮件ID",
    "thread_id": "会话ID"
  }
}
```

Optional fields:

- `automation_send_disable_reason`: the reason returned when sending is blocked by mailbox automation settings
- `automation_send_disable_reference`: the draft open link when sending is blocked
- `recall_available` / `recall_tip`: if a recall prompt is returned after a successful send, refer to [lark-mail-recall](lark-mail-recall.md) as needed

Field semantics:

- If the return contains `automation_send_disable_reason` / `automation_send_disable_reference`, it means the forward was not actually sent, but was blocked by mailbox settings. In this case, directly show the user the reason and the draft open link, and do not continue assuming the send succeeded
- If the return contains `recall_available: true`, it means the email supports recall; only when the user explicitly requests a recall, read [lark-mail-recall](lark-mail-recall.md) and execute the recall flow

<a id="典型场景"></a>
## Typical scenarios

<a id="场景-1用户说把这封邮件转发给-bob只创建草稿"></a>
### Scenario 1: The user says "forward this email to Bob" (only create a draft)
```bash
lark-cli mail +forward --message-id <邮件ID> --to 'bob@example.com' --body '<p>FYI</p>'
```
→ Returns `draft_id`, tell the user the forwarding draft has been created.

<a id="场景-2用户说转发给-bob-并发送需要发送"></a>
### Scenario 2: The user says "forward it to Bob and send it" (sending is required)
```bash
# Approach A: Create a forwarding draft
lark-cli mail +forward --message-id <邮件ID> --to 'bob@example.com' --body '<p>FYI，请查收。</p>'
# → Returns draft_id

# Confirm with the user "Recipient bob@example.com. If you want to preview the result first, you can also view the draft in Feishu Mail. Confirm sending?"

# Send after the user confirms
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'

# Approach B: When the user has already explicitly confirmed, send directly
lark-cli mail +forward --message-id <邮件ID> --to 'bob@example.com' --body '<p>FYI，请查收。</p>' --confirm-send
```

<a id="场景-3用户说下午-3-点转发给-bob定时发送"></a>
### Scenario 3: The user says "forward it to Bob at 3 PM" (scheduled send)
```bash
# Step 1: Create a forwarding draft
lark-cli mail +forward --message-id <邮件ID> --to 'bob@example.com' --body '<p>FYI，请查收。</p>'
# → Returns draft_id

# Step 2: Confirm with the user "Forwarding draft created: recipient bob@example.com, scheduled to send at <Target time>. Confirm?"

# Step 3: After the user confirms, schedule the send (send_time is a Unix timestamp and must be at least the current time + 5 minutes)
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}' --data '{"send_time":"<unix_timestamp>"}'
```

<a id="场景-4用户说等等先不转发了取消定时发送"></a>
### Scenario 4: The user says "wait, don't forward it for now" (cancel the scheduled send)
```bash
# Cancel the scheduled send (after cancellation, the email reverts to a draft)
lark-cli mail user_mailbox.drafts cancel_scheduled_send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```
→ After successful cancellation, the email reverts to draft status, and the user can edit it again or resend it later.

<a id="转发整个会话"></a>
## Forwarding an entire conversation

`+forward` operates on a single email (`--message-id`), but when forwarding an entire conversation you should forward **the last message in the conversation**, because email clients nest the complete reply chain in the latest message. Typical flow:

```bash
# 1. Use +triage or +thread to find the conversation
lark-cli mail +thread --thread-id <THREAD_ID> --html=false --format json

# 2. Take the message_id of the last message
#    messages are sorted in ascending time order, so the last one = messages[-1].message_id

# 3. Forward that message
lark-cli mail +forward --message-id <最后一条的message_id> --to 'recipient@example.com' --body '请过目'
```

<a id="实现说明"></a>
## Implementation notes

- Automatically fetches the original email and then builds the forwarding content.
- In plain text mode, a standard forwarding header block is generated with the original text appended.
- In HTML mode, a structured forwarding block is generated and the original HTML body is preserved as much as possible.

<a id="发送后跟进"></a>
## Post-send follow-up

After a forward is sent, handle two cases:

- If the return contains `automation_send_disable_reason` / `automation_send_disable_reference`: it means the send was blocked by mailbox settings; directly tell the user the reason and provide the draft open link, and do **not** call `send_status`
- If the user requests a recall based on the send result, first read [lark-mail-recall](lark-mail-recall.md), then execute the recall flow

**1. Confirm delivery status** (required only for immediate sends that return a non-empty `message_id`)

Use the returned `message_id` to query the delivery status:

```bash
lark-cli mail user_mailbox.messages send_status --params '{"user_mailbox_id":"me","message_id":"<发送返回的 message_id>"}'
```

Status codes: 1=delivering, 2=delivery failed and retrying, 3=bounced, 4=delivered successfully, 5=pending approval, 6=approval rejected. Briefly report the delivery result to the user, and highlight abnormal statuses.

**1b. Scheduled send (`--send-time` specified)**

A scheduled send does not immediately produce `message_id`, so `send_status` will return a "pending send" status after a successful scheduled send, and **it is not recommended to query immediately after scheduling**. You can query after the scheduled send time.

To cancel a scheduled send:

```bash
lark-cli mail user_mailbox.drafts cancel_scheduled_send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```

**After cancellation, the email reverts to a draft**, and you can continue editing it or resend it later.

**2. Mark as read** (optional) — ask the user whether they want to mark the original email as read. If the user agrees:

```bash
lark-cli mail +message-modify --message-ids <原邮件ID> --remove-label-ids UNREAD
```

<a id="编辑转发草稿"></a>
## Editing a forwarding draft

The draft body created by `+forward` contains a quoted section (the quoted block of the original email). If you need to edit the body of a forwarding draft, you **must use the `set_reply_body` op via `--patch-file`**, which only replaces the user-written part and automatically preserves the quoted section. Pass only the new user-written content as the value, and do not include the quoted section.

```bash
# Edit the forwarding draft body (automatically preserves the quoted section)
cat > ./patch.json << 'EOF'
{ "ops": [{ "op": "set_reply_body", "value": "<p>修改后的转发附言</p>" }] }
EOF
lark-cli mail +draft-edit --draft-id <draft_id> --patch-file ./patch.json
```

If the user wants to modify the content of the quoted section or remove it, use `set_body` for a full replacement.

<a id="相关命令"></a>
## Related commands

- `lark-cli mail +send` — Send a new email
- `lark-cli mail +reply` — Reply to an email
- `lark-cli mail user_mailbox.messages get` — View email details
