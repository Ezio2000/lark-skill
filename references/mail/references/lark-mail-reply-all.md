# mail +reply-all


Reply-all is handled automatically:
- Automatically aggregates the original email's sender, original To, and original Cc
- Automatically excludes the current user's address to avoid replying to yourself
- Automatically maintains conversation headers (`In-Reply-To` / `References`)

> **Default draft**: `+reply-all` saves as a draft by default and does not send immediately. To send immediately, add the `--confirm-send` parameter (use only after the user has explicitly confirmed).

This module corresponds to the shortcut: `lark-cli mail +reply-all`.

<a id="critical--发送工作流必须遵循"></a>
## CRITICAL — Sending workflow (must be followed)

**CRITICAL - Before editing email content you MUST first use the Read tool to read [lark-mail-html.md](lark-mail-html.md), which contains the email writing guidelines**

This command by default **only saves a draft** and does not send the email. Reply-all will be sent to **all** original recipients. When sending is needed, there are two compliant approaches:

**Approach A (recommended)** — Create a reply-all draft (without `--confirm-send`):
```bash
lark-cli mail +reply-all --message-id <邮件ID> --body '<回复正文>'
```
→ Returns `draft_id`

Show the user a reply summary (target email, reply content, full recipient list To/Cc); if the user wants to preview the result first, guide them to view the draft in Feishu Mail.

After the user explicitly agrees, send the draft:
```bash
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<Step 1 返回的 draft_id>"}'
```

**Approach B (allowed)** — When the user has already explicitly confirmed the full recipient list and content, you may directly use `--confirm-send` to send immediately.

**Sending is prohibited without the user's explicit consent, whether sending a draft or directly using `--confirm-send`.**

<a id="命令"></a>
## Commands

```bash
# Reply-all (saved as draft by default) — HTML recommended
lark-cli mail +reply-all --message-id <邮件ID> --body '<p><b>已完成</b>，详见下方说明。</p>'

# Reply-all and append recipients/cc (draft)
lark-cli mail +reply-all --message-id <邮件ID> --body '<p>同步更新</p>' --to 'lead@example.com' --cc 'pm@example.com'

# Exclude certain addresses from the reply list (draft)
lark-cli mail +reply-all --message-id <邮件ID> --body '<p>见上</p>' --remove 'bot@example.com' --remove 'noreply@example.com'

# Insert inline images when replying all (recommended: use relative paths directly, resolved automatically)
lark-cli mail +reply-all --message-id <邮件ID> --body '<p>详见图示：<img src="./logo.png" /></p>'

# Plain-text reply-all (use only when content is extremely simple)
lark-cli mail +reply-all --message-id <邮件ID> --body '收到，已处理。'

# Confirm send (use only after the user has explicitly confirmed)
lark-cli mail +reply-all --message-id <邮件ID> --body '<p>收到，已处理。</p>' --confirm-send

# Dry Run (only prints the request, does not send)
lark-cli mail +reply-all --message-id <邮件ID> --body '测试' --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--message-id <id>` | Yes | ID of the email being replied to |
| `--body <text>` | Choose one | Reply body. HTML is recommended for rich-text formatting; plain text is also supported. HTML is auto-detected based on the reply body and the original email body. Use `--plain-text` to force plain-text mode. Supports `<img src="./local.png" />` relative paths being automatically resolved as inline images (only relative paths are supported, not absolute paths). Mutually exclusive with `--body-file` |
| `--body-file <path>` | Choose one | Read the reply body HTML from a file (relative path, limited to the cwd subtree). Mutually exclusive with `--body`. File size limit 32 MB |
| `--from <email>` | No | Sender email address (EML From header). When sending with an alias (send_as), set this to the alias address and use `--mailbox` to specify the owning mailbox. Defaults to reading the mailbox's primary address |
| `--mailbox <email>` | No | Mailbox address, specifies the mailbox the draft belongs to (defaults to falling back to `--from`, then to `me`). Used when the sender (`--from`) differs from the mailbox. Available mailboxes can be queried via `accessible_mailboxes` |
| `--to '<email>'` | No | Additional recipients. For multiple additional recipients, pass `--to` repeatedly, one address at a time, with the parameter value wrapped in single quotes; appended to the auto-aggregated result |
| `--cc '<email>'` | No | Additional cc. For multiple cc's, pass `--cc` repeatedly, one address at a time, with the parameter value wrapped in single quotes |
| `--bcc '<email>'` | No | Bcc email. For multiple bcc's, pass `--bcc` repeatedly, one address at a time, with the parameter value wrapped in single quotes. Incompatible with `--event-*` (see `+send` calendar invitation constraints) |
| `--remove '<email>'` | No | Emails to exclude from the auto-aggregated result. For multiple excluded addresses, pass `--remove` repeatedly, one address at a time, with the parameter value wrapped in single quotes; processed in the order passed |
| `--plain-text` | No | Force plain-text mode, ignoring all HTML auto-detection. Cannot be used together with `--inline`. In plain-text mode, a plain-text signature is also automatically appended (HTML signatures are converted via `PlainTextFromHTML`, inline images are discarded) |
| `--attach '<path>'` | No | Attachment file path. For multiple attachments, pass `--attach` repeatedly, one relative path at a time, with the parameter value wrapped in single quotes; appended in the order passed. When attachments cause the total EML size to exceed 25 MB, the excess is automatically uploaded as a large attachment (a download card is inserted for HTML emails, a download link is appended for plain-text emails), with a single file limit of 3 GB |
| `--inline '<json>'` | No | Advanced usage: manually specify the inline image CID mapping. For multiple inline images, pass `--inline` repeatedly, one JSON object at a time, wrapped in single quotes: `'{"cid":"mycid","file_path":"./logo.png"}'`. `file_path` must be a relative path; the CID should be unique, e.g. a random hexadecimal string; reference it in the body with `<img src="cid:mycid">`. It is recommended to use `<img src="./path" />` directly in `--body` (resolved automatically). Cannot be used together with `--plain-text` |
| `--signature-id <id>` | No | Signature ID. Appends the mailbox signature between the reply body and the quoted block. Run `mail +signature` to view available signatures. Mutually exclusive with `--no-signature` |
| `--no-signature` | No | Skip automatic appending of the default signature. Mutually exclusive with `--signature-id`; using both together returns a parameter validation error (exit code 2) |
| `--priority <level>` | No | Email priority: `high`, `normal`, `low`. When omitted or `normal`, no priority is set |
| `--event-summary <text>` | No | Calendar title. Setting this parameter embeds a calendar invitation in the email. `--event-start` and `--event-end` must also be set |
| `--event-start <time>` | Conditionally required | Calendar start time (ISO 8601) |
| `--event-end <time>` | Conditionally required | Calendar end time (ISO 8601) |
| `--event-location <text>` | No | Calendar location |
| `--confirm-send` | No | Confirm sending the reply (by default only saves a draft). Use only after the user has explicitly confirmed |
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

- If the return contains `automation_send_disable_reason` / `automation_send_disable_reference`, it means the reply-all was not actually sent but was blocked by mailbox settings. In this case, directly show the user the reason and the draft open link, and do not continue assuming the send succeeded
- If the return contains `recall_available: true`, it means the email supports recall; only when the user explicitly requests a recall, read [lark-mail-recall](lark-mail-recall.md) and execute the recall process

<a id="典型场景"></a>
## Typical scenarios

<a id="场景-1用户说帮我回复全部说同意只创建草稿"></a>
### Scenario 1: The user says "help me reply all saying I agree" (only create a draft)
```bash
lark-cli mail +reply-all --message-id <邮件ID> --body '<p>同意，没有问题。</p>'
```
→ Returns `draft_id`, telling the user the reply-all draft has been created.

<a id="场景-2用户说回复全部说已确认需要发送"></a>
### Scenario 2: The user says "reply all saying confirmed" (needs to send)
```bash
# Approach A: Create a reply-all draft
lark-cli mail +reply-all --message-id <邮件ID> --body '<p>已确认。</p>'
# → Returns draft_id

# Confirm with the user "Recipients alice@, bob@, carol@, content 'Confirmed.' If you want to preview the result first, you can also view the draft in Feishu Mail. Confirm sending?"

# Send after the user confirms
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'

# Approach B: When the user has already explicitly confirmed, send directly
lark-cli mail +reply-all --message-id <邮件ID> --body '<p>已确认。</p>' --confirm-send
```

<a id="场景-3用户说下午-3-点回复全部说已确认定时发送"></a>
### Scenario 3: The user says "reply all at 3 PM saying confirmed" (scheduled send)
```bash
# Step 1: Create a reply-all draft
lark-cli mail +reply-all --message-id <邮件ID> --body '<p>已确认。</p>'
# → Returns draft_id

# Step 2: Confirm with the user "Reply-all draft created: recipients alice@, bob@, carol@, content 'Confirmed.' Scheduled to send at <target time>. Confirm?"

# Step 3: After the user confirms, schedule the send (send_time is a Unix timestamp, must be at least the current time + 5 minutes)
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}' --data '{"send_time":"<unix_timestamp>"}'
```

<a id="场景-4用户说等等先不回复了取消定时发送"></a>
### Scenario 4: The user says "wait, don't reply for now" (cancel scheduled send)
```bash
# Cancel scheduled send (after cancellation the email reverts to a draft)
lark-cli mail user_mailbox.drafts cancel_scheduled_send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```
→ After successful cancellation, the email reverts to draft status, and the user can re-edit or resend it later.

<a id="实现说明"></a>
## Implementation notes

- Automatic recipient rules: the original sender goes to To first, and the original To/Cc go to Cc.
- Addresses are deduplicated (case-insensitive).
- The current user's address (enterprise email) is automatically excluded, and the `--remove` rule is applied on top.
- Conversation headers are maintained via raw EML, and the original `thread_id` is reused as much as possible.

<a id="发送后跟进"></a>
## Post-send follow-up

After the reply is sent, handle two cases:

- If the return contains `automation_send_disable_reason` / `automation_send_disable_reference`: it means the send was blocked by mailbox settings; you should directly tell the user the reason and provide the draft open link, and **do not** call `send_status`
- If the user requests a recall based on the send result, first read [lark-mail-recall](lark-mail-recall.md), then execute the recall process

**1. Confirm delivery status** (required only for immediate sends that return a non-empty `message_id`)

Use the returned `message_id` to query the delivery status:

```bash
lark-cli mail user_mailbox.messages send_status --params '{"user_mailbox_id":"me","message_id":"<发送返回的 message_id>"}'
```

Status codes: 1=delivering, 2=delivery failed and retrying, 3=bounced, 4=delivered successfully, 5=pending approval, 6=approval rejected. Briefly report the delivery result to the user; abnormal statuses should be highlighted.

**1b. Scheduled send (`--send-time` specified)**

A scheduled send does not immediately produce a `message_id`, so `send_status` will return a "pending send" status after a successful scheduled send; **it is not recommended to query immediately after a scheduled send**. You can query after the scheduled send time.

To cancel a scheduled send:

```bash
lark-cli mail user_mailbox.drafts cancel_scheduled_send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```

**After cancellation the email reverts to a draft**, and you can continue editing or resend it later.

**2. Mark as read** (optional) — Ask the user whether the original email needs to be marked as read. If the user agrees:

```bash
lark-cli mail +message-modify --message-ids <原邮件ID> --remove-label-ids UNREAD
```

<a id="相关命令"></a>
## Related commands

- `lark-cli mail +reply` — Reply only to the sender
- `lark-cli mail +forward` — Forward the email
- `lark-cli mail user_mailbox.messages get` — View email details
