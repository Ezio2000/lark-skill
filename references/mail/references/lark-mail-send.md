# mail +send


Send a new email, supporting:
- Plain text or HTML body
- Cc/Bcc
- Local file attachments (`--attach`)
- Inline images (`--inline`, CID can be a random string)

This module corresponds to the shortcut: `lark-cli mail +send`.

<a id="critical--发送工作流必须遵循"></a>
## CRITICAL — Sending workflow (must follow)

For complex HTML, inline images, or template layout, read the [HTML reference](lark-mail-html.md); for ordinary plain text, there is no need to load the HTML writing instructions.

This command by default **only saves a draft** and does not send the email. When you need to send, there are two compliant ways:

**Method A** — Create a draft when the user requests review or when the draft workflow is appropriate:
```bash
lark-cli mail +send --to '<收件人>' --subject '<主题>' --body '<正文>'
```
→ Returns `draft_id`

Show the user an email summary (recipients, subject, body preview); if the user wants to see the result first, guide them to open the draft in Feishu Mail to view the details.

Send the actual returned draft when sending is authorized. Reuse an existing explicit send request if the recipients, content, timing, and effects are unchanged; ask only for missing information or a materially changed action:
```bash
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<Step 1 返回的 draft_id>"}'
```

**Method B** — When the user's request already authorizes sending to the specified recipients with the specified content, use `--confirm-send` to send immediately:
```bash
lark-cli mail +send --to '<收件人>' --subject '<主题>' --body '<正文>' --confirm-send
```

**Writing or reviewing a draft does not authorize sending. An explicit request to send does; do not demand another confirmation phrase for the same action.** After sending, check the returned status using [send status](lark-mail-send-status.md); do not infer delivery from draft creation or a blocked send response.

<a id="命令"></a>
## Commands

```bash
# Save as draft (default behavior, does not send) — HTML format recommended
lark-cli mail +send --to 'alice@example.com' --subject '周报' \
  --body '<p>本周进展：</p><ul><li>完成 A 模块</li><li>修复 3 个 bug</li></ul>'

# Save as draft and Cc
lark-cli mail +send --to 'alice@example.com' --cc 'bob@example.com' --subject '状态更新' --body '<b>已完成</b>'

# Confirm sending (use only after the user explicitly confirms)
lark-cli mail +send --to 'alice@example.com' --subject '周报' \
  --body '<p>本周进展如下...</p>' --confirm-send

# Save a draft with attachments
lark-cli mail +send --to 'alice@example.com' --subject '请查收' --body '<p>见附件</p>' --attach './report.pdf' --attach './logs.zip'

# Save a draft with inline images (recommended: use relative paths directly, automatically resolved)
lark-cli mail +send --to 'alice@example.com' --subject '预览图' --body '<img src="./logo.png" />'

# Plain text email (use only when the content is extremely simple)
lark-cli mail +send --to 'alice@example.com' --subject '确认' --body '收到，谢谢'

# Dry Run (only prints the request, does not execute)
lark-cli mail +send --to 'alice@example.com' --subject '测试' --body '<p>test</p>' --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--to '<email>'` | Yes | Recipient email. For multiple recipients, pass `--to` repeatedly, with only one address each time, and wrap the parameter value in single quotes |
| `--subject <text>` | Yes | Email subject |
| `--body <text>` | Choose one of two | Email body. HTML is recommended for rich text layout; plain text is also supported (auto-detected). Use `--plain-text` to force plain text mode. Supports automatic resolution of `<img src="./local.png" />` relative paths as inline images (only relative paths are supported, absolute paths are not). Mutually exclusive with `--body-file` |
| `--body-file <path>` | Choose one of two | Read the email body HTML from a file (relative path, limited to the cwd subtree). Mutually exclusive with `--body`. File size limit 32 MB |
| `--from <email>` | No | Sender email address (EML From header). When sending with an alias (send_as), set it to the alias address and use `--mailbox` to specify the mailbox it belongs to. By default, reads the mailbox's primary address |
| `--mailbox <email>` | No | Mailbox address, specifying the mailbox the draft belongs to (defaults back to `--from`, then back to `me`). Used when the sender (`--from`) differs from the mailbox. Available mailboxes can be queried via `accessible_mailboxes` |
| `--cc '<email>'` | No | Cc email. For multiple Cc recipients, pass `--cc` repeatedly, with only one address each time, and wrap the parameter value in single quotes |
| `--bcc '<email>'` | No | Bcc email. For multiple Bcc recipients, pass `--bcc` repeatedly, with only one address each time, and wrap the parameter value in single quotes |
| `--plain-text` | No | Force plain text mode, ignoring HTML auto-detection. Cannot be used together with `--inline`. In plain text mode, a plain text signature is also automatically appended (the HTML signature is converted via `PlainTextFromHTML`, and inline images are discarded) |
| `--attach '<path>'` | No | Attachment file path. For multiple attachments, pass `--attach` repeatedly, with only one relative path each time, and wrap the parameter value in single quotes; appended in the order passed. When attachments cause the total EML size to exceed 25 MB, the excess is automatically uploaded as large attachments (HTML emails insert a download card, plain text emails append a download link), with a single file limit of 3 GB |
| `--inline '<json>'` | No | Advanced usage: manually specify the inline image CID mapping. For multiple inline images, pass `--inline` repeatedly, with only one JSON object each time, wrapped in single quotes: `'{"cid":"mycid","file_path":"./logo.png"}'`. `file_path` must be a relative path; the CID should be unique, for example a random hexadecimal string; reference it in the body with `<img src="cid:mycid">`. It is recommended to use `<img src="./path" />` directly in `--body` (automatically resolved). Cannot be used together with `--plain-text` |
| `--signature-id <id>` | No | Signature ID. Appends the mailbox signature to the end of the body. Run `mail +signature` to view available signatures. Mutually exclusive with `--no-signature` |
| `--no-signature` | No | Skip automatic appending of the default signature. Mutually exclusive with `--signature-id`; using both together returns a parameter validation error (exit code 2) |
| `--priority <level>` | No | Email priority: `high`, `normal`, `low`. When omitted or `normal`, no priority is set |
| `--event-summary <text>` | No | Calendar title. Setting this parameter embeds a calendar invitation (text/calendar) in the email. `--event-start` and `--event-end` must also be set |
| `--event-start <time>` | Conditionally required | Calendar start time (ISO 8601, e.g. `2026-04-20T14:00+08:00`) |
| `--event-end <time>` | Conditionally required | Calendar end time (ISO 8601) |
| `--event-location <text>` | No | Calendar location |
| `--confirm-send` | No | Confirm sending the email (by default only saves a draft). Use only after the user explicitly confirms the recipients and content |
| `--send-time <timestamp>` | No | Scheduled send time, Unix timestamp (seconds). Must be at least the current time + 5 minutes. Use with `--confirm-send` to schedule email sending |
| `--request-receipt` | No | Request a read receipt (RFC 3798 Message Disposition Notification). Writes the `Disposition-Notification-To: <sender>` header in the outbound EML. The recipient's email client **may** pop up a prompt asking whether to send a receipt, may send it automatically, or may ignore it — delivery is not guaranteed |
| `--dry-run` | No | Only prints the request, does not execute |

<a id="日程邀请约束"></a>
### Calendar invitation constraints

When using `--event-*`, the following conditions must be met:

- `--event-summary`, `--event-start`, and `--event-end` must all appear together or all be absent
- Mutually exclusive with `--send-time` and cannot be used together (calendar invitations must be sent immediately, otherwise recipients may receive them only after the calendar starts)
- Cannot be used together with `--bcc`: calendar attendees (ATTENDEE) come only from To and Cc; Bcc recipients are not in the attendee list and cannot RSVP, and this combination will cause email sending to fail. To invite someone to a calendar, use `--to` or `--cc`; if you only want to inform them without inviting, send a separate email with no calendar

<a id="返回值"></a>
## Return values

**Draft mode (default):**

```json
{
  "ok": true,
  "data": {
    "draft_id": "草稿ID",
    "tip": "draft saved. To send: lark-cli mail user_mailbox.drafts send --params '{...}'"
  }
}
```

In draft mode, as long as the result is not a direct send but produces a draft, you should show the user the draft open link. Currently, the link information returned by the `create` / `edit` / `send` chain should be used as the source of truth; do not treat `user_mailbox.drafts get` as the source for obtaining the draft open link. If the return includes `reference`, return the link together with `draft_id`; when there is currently no link, handle it silently and do not fabricate a link.

**Send mode (`--confirm-send`):**

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

- `automation_send_disable_reason`: The reason returned when sending is intercepted by mailbox automation settings
- `automation_send_disable_reference`: The draft open link when sending is intercepted
- `recall_available` / `recall_tip`: After a successful send, if a recall prompt is returned, refer to [lark-mail-recall](lark-mail-recall.md) as needed

Field semantics:

- If the return includes `automation_send_disable_reason` / `automation_send_disable_reference`, it means the email was not actually sent, but was intercepted by mailbox settings. In this case, directly show the user the reason and the draft open link, and do not continue assuming the send succeeded
- If the return includes `recall_available: true`, it means the email supports recall; only when the user explicitly requests recall, read [lark-mail-recall](lark-mail-recall.md) and execute the recall process

<a id="典型场景"></a>
## Typical scenarios

<a id="场景-1用户说帮我写一封邮件给-alice只创建草稿"></a>
### Scenario 1: The user says "help me write an email to Alice" (only create a draft)
```bash
lark-cli mail +send --to 'alice@example.com' --subject '周报' --body '<p>本周进展如下...</p>'
```
→ When returning the draft result, if the output includes a draft open link, show it to the user as well; if the current output has no link, handle it silently. If the user wants to see the result first, they can open the draft in the Feishu Mail UI to view the details.

<a id="场景-2用户说发邮件给-alice-说收到了需要发送"></a>
### Scenario 2: The user says "send an email to Alice saying I received it" (sending required)
```bash
# Method A: Create a draft
lark-cli mail +send --to 'alice@example.com' --subject '收到' --body '<p>已收到，谢谢！</p>'
# → Returns draft_id

# The user's explicit send request already authorizes this exact action.

# Send the actual returned draft without asking for the same authorization again
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'

# Method B: When the user has already explicitly confirmed, send directly
lark-cli mail +send --to 'alice@example.com' --subject '收到' --body '<p>已收到，谢谢！</p>' --confirm-send
```

<a id="场景-3用户说下午-3-点给-alice-发一封周报定时发送"></a>
### Scenario 3: The user says "send Alice a weekly report at 3 PM" (scheduled send)
```bash
# Step 1: Create a draft (scheduled sending also goes through the draft process)
lark-cli mail +send --to 'alice@example.com' --subject '周报' --body '<p>本周进展如下...</p>'
# → Returns draft_id

# Step 2: Resolve the intended time and any missing content. Reuse the user's authorization when the scheduled send is already fully specified.

# Step 3: Schedule the authorized send (send_time is a Unix timestamp and must be at least the current time + 5 minutes)
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}' --data '{"send_time":"<unix_timestamp>"}'
```

<a id="场景-4用户说等等先不发那封邮件了取消定时发送"></a>
### Scenario 4: The user says "wait, don't send that email for now" (cancel scheduled send)
```bash
# Cancel scheduled send (after cancellation, the email reverts to a draft)
lark-cli mail user_mailbox.drafts cancel_scheduled_send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```
→ After successful cancellation, the email reverts to draft status, and the user can edit it again or resend it later.

<a id="发送后跟进"></a>
## Post-send follow-up

After the email is sent, handle it in two cases:

- If the return includes `automation_send_disable_reason` / `automation_send_disable_reference`: it means sending was intercepted by mailbox settings, and you should directly tell the user the reason and provide the draft open link; **do not** call `send_status`

<a id="立即发送无---send-time"></a>
### Immediate send (no `--send-time`)

If a non-empty `message_id` is returned, call:

```bash
lark-cli mail user_mailbox.messages send_status --params '{"user_mailbox_id":"me","message_id":"<发送返回的 message_id>"}'
```

Status codes: 1=delivering, 2=delivery failed and retrying, 3=bounced, 4=delivered successfully, 5=pending approval, 6=approval rejected. Briefly report the delivery result for each recipient to the user, and highlight abnormal statuses.

<a id="定时发送指定了---send-time"></a>
### Scheduled send (`--send-time` specified)

Scheduled sending does not immediately produce `message_id`, so `send_status` will return a "pending send" status after a successful scheduled send; **it is not recommended to query immediately after a scheduled send**. You can query the delivery status after the scheduled send time.

If you need to cancel a scheduled send, you can call the cancel interface before the scheduled time:

```bash
lark-cli mail user_mailbox.drafts cancel_scheduled_send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```

**After cancellation, the email reverts to a draft**, and you can continue editing it or resend it later.

<a id="实现说明"></a>
## Implementation notes

- Use the EML builder to generate a complete MIME email, base64url-encode it, and then send it.
- `--attach` is added as a regular attachment. For multiple attachments, pass `--attach` repeatedly, with only one relative path each time.
- When `--inline` manually specifies inline images, for multiple images pass `--inline` repeatedly, with only one JSON object each time. Each item must provide `cid` (a unique identifier, which can be a random hexadecimal string) and `file_path` (a relative path), embedded in the email as an inline part.
- **Large attachments**: When attachments cause the total EML size (headers + body + inline images + attachments, after base64 encoding) to exceed 25 MB, the excess files are automatically uploaded to the cloud via the `medias/upload_*` API. HTML emails insert a download card consistent with the Feishu client; plain text emails append a text block containing the file name, size, and download link. A single file limit is 3 GB, and the total number of attachments is limited to 250.

<a id="相关命令"></a>
## Related commands

- `lark-cli mail +reply` — Reply to an email
- `lark-cli mail +reply-all` — Reply all
- `lark-cli mail +forward` — Forward an email
- `lark-cli mail user_mailbox.messages list` — List emails
