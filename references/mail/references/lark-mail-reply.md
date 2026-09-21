# mail +reply


Reply to a specified email, with automatic handling of:
- Subject prefix `Re: ` (not stacked again when a common reply prefix is already present)
- Default recipient is the sender of the original email
- RFC 2822 conversation headers (`In-Reply-To` / `References`) to maintain the email conversation

> **Default draft mode**: `+reply` is saved as a draft by default and is not sent immediately. To send immediately, use the `--confirm-send` parameter (requires explicit user confirmation). **Prefer using `+reply` instead of `+draft-create` to create a reply draft**, because `+reply` automatically handles the subject, recipients, and conversation headers.

This module corresponds to the shortcut: `lark-cli mail +reply`, internal steps:
1. `GET /open-apis/mail/v1/user_mailboxes/me/messages/{message_id}` — retrieve the original email metadata
2. `GET /open-apis/mail/v1/user_mailboxes/me/profile` — retrieve the primary mailbox address (`primary_email_address`, filled into the default From header)
3. `POST /open-apis/mail/v1/user_mailboxes/me/drafts` — create a draft
4. `POST /open-apis/mail/v1/user_mailboxes/me/drafts/{draft_id}/send` — send the draft (executed only when `--confirm-send` is specified)

<a id="critical--发送工作流必须遵循"></a>
## CRITICAL — Sending workflow (must be followed)

**CRITICAL - Before editing email content you MUST first use the Read tool to read [lark-mail-html.md](lark-mail-html.md), which contains the email writing guidelines**

This command by default **only saves a draft** and does not send the email. When sending is needed, there are two compliant approaches:

**Approach A (recommended)** — create a reply draft (without `--confirm-send`):
```bash
lark-cli mail +reply --message-id <邮件ID> --body '<回复正文>'
```
→ returns `draft_id`

Show the user a reply summary (target email, reply content, recipients); if the user wants to preview the result first, guide them to view the draft in Feishu Mail.

After the user explicitly agrees, send the draft:
```bash
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<Step 1 返回的 draft_id>"}'
```

**Approach B (allowed)** — when the user has already explicitly confirmed the reply target and content, you may directly use `--confirm-send` to send immediately.

**It is forbidden to execute sending without the user's explicit consent, whether sending a draft or directly using `--confirm-send`.**

<a id="命令"></a>
## Command

```bash
# Reply to an email (saved as a draft by default, returns draft_id) — HTML recommended
lark-cli mail +reply --message-id <邮件ID> --body '<p><b>已收到</b>，稍后跟进。</p>'

# Reply and append recipients/CC (saved as a draft)
lark-cli mail +reply --message-id <邮件ID> --body '<p>已处理</p>' --to 'lead@example.com' --cc 'colleague@example.com'

# Insert inline images when replying (recommended: use relative paths directly, resolved automatically)
lark-cli mail +reply --message-id <邮件ID> --body '<p>详见图示：<img src="./logo.png" /></p>'

# Plain text reply (use only when the content is extremely simple)
lark-cli mail +reply --message-id <邮件ID> --body '收到，谢谢！'

# Specify the sender address
lark-cli mail +reply --message-id <邮件ID> --body '收到' --from me@example.com

# Confirm sending the reply (use after explicit user confirmation)
lark-cli mail +reply --message-id <邮件ID> --body '<p>收到，谢谢！</p>' --confirm-send

# Dry Run (only prints the request, does not execute)
lark-cli mail +reply --message-id <邮件ID> --body '<p>测试</p>' --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--message-id <id>` | Yes | ID of the email being replied to |
| `--body <text>` | Choose one of two | Reply body. HTML is recommended for rich text formatting; plain text is also supported. HTML is auto-detected based on the reply body and the original email body. Use `--plain-text` to force plain text mode. Supports `<img src="./local.png" />` relative paths automatically resolved as inline images (only relative paths are supported, absolute paths are not). Mutually exclusive with `--body-file` |
| `--body-file <path>` | Choose one of two | Read the reply body HTML from a file (relative path, limited to the cwd subtree). Mutually exclusive with `--body`. File size limit 32 MB |
| `--from <email>` | No | Sender email address (EML From header). When sending with an alias (send_as), set this to the alias address and use `--mailbox` to specify the mailbox it belongs to. Defaults to reading the primary mailbox address |
| `--mailbox <email>` | No | Mailbox address, specifies the mailbox the draft belongs to (defaults back to `--from`, then back to `me`). Used when the sender (`--from`) differs from the mailbox. Available mailboxes can be queried via `accessible_mailboxes` |
| `--to '<email>'` | No | Additional recipients. For multiple additional recipients, pass `--to` repeatedly, one address at a time, wrapping the parameter value in single quotes; appended to the original sender |
| `--cc '<email>'` | No | CC email addresses. For multiple CCs, pass `--cc` repeatedly, one address at a time, wrapping the parameter value in single quotes |
| `--bcc '<email>'` | No | BCC email addresses. For multiple BCCs, pass `--bcc` repeatedly, one address at a time, wrapping the parameter value in single quotes. Incompatible with `--event-*` (see `+send` calendar invitation constraints) |
| `--plain-text` | No | Force plain text mode, ignoring all HTML auto-detection. Cannot be used together with `--inline`. In plain text mode, a plain text signature is also automatically appended (HTML signatures are converted via `PlainTextFromHTML`, inline images are discarded) |
| `--attach '<path>'` | No | Attachment file paths. For multiple attachments, pass `--attach` repeatedly, one relative path at a time, wrapping the parameter value in single quotes; appended in the order passed. When attachments cause the total EML size to exceed 25 MB, the excess is automatically uploaded as large attachments (a download card is inserted for HTML emails, a download link is appended for plain text emails), with a single file limit of 3 GB |
| `--inline '<json>'` | No | Advanced usage: manually specify the inline image CID mapping. For multiple inline images, pass `--inline` repeatedly, one JSON object at a time, wrapping it in single quotes: `'{"cid":"mycid","file_path":"./logo.png"}'`. `file_path` must be a relative path; the CID should be unique, e.g. a random hexadecimal string; reference it in the body with `<img src="cid:mycid">`. It is recommended to use `<img src="./path" />` directly in `--body` (resolved automatically). Cannot be used together with `--plain-text` |
| `--signature-id <id>` | No | Signature ID. Appends the mailbox signature between the reply body and the quoted block. Run `mail +signature` to view available signatures. Mutually exclusive with `--no-signature` |
| `--no-signature` | No | Skip automatic appending of the default signature. Mutually exclusive with `--signature-id`; using both together returns a parameter validation error (exit code 2) |
| `--priority <level>` | No | Email priority: `high`, `normal`, `low`. When omitted or `normal`, no priority is set |
| `--event-summary <text>` | No | Calendar title. Setting this parameter embeds a calendar invitation in the email. `--event-start` and `--event-end` must also be set |
| `--event-start <time>` | Conditionally required | Calendar start time (ISO 8601) |
| `--event-end <time>` | Conditionally required | Calendar end time (ISO 8601) |
| `--event-location <text>` | No | Calendar location |
| `--confirm-send` | No | Confirm sending the reply (by default only saves a draft). Use only after explicit user confirmation |
| `--send-time <timestamp>` | No | Scheduled send time, Unix timestamp (seconds). Must be at least the current time + 5 minutes. Use with `--confirm-send` to schedule email sending |
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

`--confirm-send` mode (sent successfully):
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
- `recall_available` / `recall_tip`: after a successful send, if a recall hint is returned, refer to [lark-mail-recall](lark-mail-recall.md) as needed

Field semantics:

- If the return contains `automation_send_disable_reason` / `automation_send_disable_reference`, it means the reply was not actually sent but was blocked by mailbox settings. In this case, directly show the user the reason and the draft open link, and do not continue assuming the send succeeded
- If the return contains `recall_available: true`, it means the email supports recall; only when the user explicitly requests a recall, read [lark-mail-recall](lark-mail-recall.md) and execute the recall flow

<a id="典型场景"></a>
## Typical scenarios

<a id="场景-1用户说帮我写个回复草稿只创建草稿"></a>
### Scenario 1: The user says "help me write a reply draft" (only create a draft)
```bash
lark-cli mail +reply --message-id <邮件ID> --body '<p>收到，谢谢！</p>'
```
→ returns `draft_id`, tell the user the reply draft has been created. **Note: use `+reply` instead of `+draft-create`**, so the draft automatically associates the original email's subject, recipients, and conversation headers.

<a id="场景-2用户说回复这封邮件说已处理需要发送"></a>
### Scenario 2: The user says "reply to this email saying it's handled" (needs sending)
```bash
# Approach A: create a reply draft
lark-cli mail +reply --message-id <邮件ID> --body '<p>已处理，谢谢。</p>'
# → returns draft_id

# Confirm with the user "Reply to alice@example.com, content 'Handled, thanks.' If you want to preview the result first, you can also view the draft in Feishu Mail. Confirm sending?"

# Send after the user confirms
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'

# Approach B: when the user has already explicitly confirmed, send directly
lark-cli mail +reply --message-id <邮件ID> --body '<p>已处理，谢谢。</p>' --confirm-send
```

<a id="场景-3用户说下午-3-点回复这封邮件说已处理定时发送"></a>
### Scenario 3: The user says "reply to this email at 3 PM saying it's handled" (scheduled send)
```bash
# Step 1: create a reply draft
lark-cli mail +reply --message-id <邮件ID> --body '<p>已处理，谢谢。</p>'
# → returns draft_id

# Step 2: confirm with the user "Reply draft created: reply to alice@example.com, content 'Handled, thanks.' Scheduled to send at <target time>. Confirm?"

# Step 3: after the user confirms, schedule the send (send_time is a Unix timestamp, must be at least the current time + 5 minutes)
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}' --data '{"send_time":"<unix_timestamp>"}'
```

<a id="场景-4用户说等等先不回复了取消定时发送"></a>
### Scenario 4: The user says "wait, don't reply for now" (cancel scheduled send)
```bash
# Cancel the scheduled send (after cancellation the email reverts to a draft)
lark-cli mail user_mailbox.drafts cancel_scheduled_send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```
→ after successful cancellation the email reverts to draft status, and the user can re-edit or resend it later.

<a id="实现说明"></a>
## Implementation notes

<a id="会话维护"></a>
### Conversation maintenance

This shortcut sends via raw EML, including standard RFC 2822 conversation headers:

```
In-Reply-To: <原邮件smtp_message_id>
References:  <原邮件references + smtp_message_id>
```

If the original email has `thread_id`, it is also passed in when sending, ensuring the reply is grouped into the same conversation.

<a id="收件人与引用"></a>
### Recipients and quoting

- By default, reply to the sender of the original email (`head_from`)
- `--to` appends on top of the default recipients
- Automatically concatenates a quoted block (plain text or HTML)

<a id="发送后跟进"></a>
## Post-send follow-up

After the reply is sent, handle two cases:

- If the return contains `automation_send_disable_reason` / `automation_send_disable_reference`: it means the send was blocked by mailbox settings; directly tell the user the reason and provide the draft open link, and do **not** call `send_status`
- If the user requests a recall based on the send result, first read [lark-mail-recall](lark-mail-recall.md), then execute the recall flow

**1. Confirm delivery status** (required only for immediate sends that return a non-empty `message_id`)

Use the returned `message_id` to query the delivery status:

```bash
lark-cli mail user_mailbox.messages send_status --params '{"user_mailbox_id":"me","message_id":"<发送返回的 message_id>"}'
```

Status codes: 1=delivering, 2=delivery failed and retrying, 3=bounced, 4=delivered successfully, 5=pending approval, 6=approval rejected. Briefly report the delivery result to the user; abnormal statuses should be highlighted.

**1b. Scheduled send (`--send-time` specified)**

A scheduled send does not immediately produce a `message_id`, so `send_status` returns a "pending send" status after a successful scheduled send; **it is not recommended to query immediately after scheduling**. You can query after the scheduled send time.

To cancel a scheduled send:

```bash
lark-cli mail user_mailbox.drafts cancel_scheduled_send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```

**After cancellation the email reverts to a draft**, and you can continue editing or resend it later.

**2. Mark as read** (optional) — ask the user whether the original email should be marked as read. If the user agrees:

```bash
lark-cli mail +message-modify --message-ids <原邮件ID> --remove-label-ids UNREAD
```

<a id="编辑回复草稿"></a>
## Editing a reply draft

The draft body created by `+reply` contains a quoted area (the quoted block of the original email). If you need to edit the body of a reply draft, you **must use the `set_reply_body` op via `--patch-file`**, which only replaces the user-written part and automatically preserves the quoted area. Pass only the new user-written content as the value, without including the quoted area.

```bash
# Edit the reply draft body (automatically preserves the quoted area)
cat > ./patch.json << 'EOF'
{ "ops": [{ "op": "set_reply_body", "value": "<p>修改后的回复内容</p>" }] }
EOF
lark-cli mail +draft-edit --draft-id <draft_id> --patch-file ./patch.json
```

If the user wants to modify the content of the quoted area or remove it, use `set_body` for a full replacement.

<a id="注意事项"></a>
## Notes

- Requires being logged in (`lark-cli auth login --scope "mail:user_mailbox.message:modify mail:user_mailbox.message:readonly mail:user_mailbox:readonly"`) and having write/read mail permissions
- The email ID can be obtained from `lark-cli mail user_mailbox.messages list`
- `--bcc` only takes effect in the sending pipeline and is usually not visible to the recipient

<a id="相关命令"></a>
## Related commands

- `lark-cli mail user_mailbox.messages list` — list emails
- `lark-cli mail user_mailbox.messages get` — read email details
- `lark-cli mail +reply-all` — reply all
- `lark-cli mail +forward` — forward email
