# mail +draft-create


Create a brand-new mail draft from scratch. Suitable for scenarios where the recipients, subject, and body are already known.

Do not use this command for reply or forward scenarios. Replies and forwards should use the corresponding dedicated shortcuts (they also create a draft by default rather than sending).

To modify an existing draft, do not use this command; use `lark-cli mail +draft-edit` instead.

**CRITICAL - Before editing mail content you MUST first use the Read tool to read [lark-mail-html.md](lark-mail-html.md), which contains the mail writing guidelines**

<a id="安全约束"></a>
## Security Constraints

This command creates a draft — it does **not** send mail. The user can open the draft in the Feishu Mail UI to view the details and confirm before proceeding to subsequent operations. Therefore:

- **Do not output the mail content as text and then request confirmation.** When the user asks to "draft"/"compose" a mail, directly call `+draft-create` to create a draft in Feishu Mail, and guide the user to open the draft in Feishu Mail.
- **Omit `--to` when no recipient is specified** — the draft will be created without recipients, and the user can add them later.
- **Only confirm when the user's request is genuinely ambiguous** (for example, when the content could be understood in multiple ways).
- **Sending** a draft is a separate operation and requires explicit user confirmation.
- **Return the open link when producing a draft** — whenever the current result is a draft rather than a direct send, show the user the draft open link. Currently, the link information returned by the create, edit, and send chain should be authoritative; do not expect `user_mailbox.drafts get` to return an open link. If the current command output contains a draft link, return it as well; if there is no link, handle it silently and do not fabricate a URL.

<a id="命令"></a>
## Command

```bash
# Create an HTML draft (recommended)
lark-cli mail +draft-create --to 'alice@example.com' --subject '周报' \
  --body '<p>本周进展：</p><ul><li>完成 A 模块</li></ul>'

# HTML draft without recipients (the user can add them later)
lark-cli mail +draft-create --subject '周报' --body '<p>草稿内容</p>'

# HTML draft with attachments and inline images (recommended: use relative paths directly, resolved automatically)
lark-cli mail +draft-create --to 'alice@example.com' --subject '预览图' --body '<p>见附件和图：<img src="./logo.png" /></p>' --attach './report.pdf'

# Plain-text draft (use only when the content is extremely simple)
lark-cli mail +draft-create --to 'alice@example.com' --subject '简短通知' --body '收到，谢谢'

# Dry Run (only print the request, do not execute)
lark-cli mail +draft-create --to 'alice@example.com' --subject '测试' --body 'test' --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--to '<email>'` | No | Full recipient list. For multiple recipients, pass `--to` repeatedly, with only one address each time, and wrap the parameter value in single quotes. Supports the `Alice <alice@example.com>` format. When omitted, the draft has no recipients (they can be added later via `+draft-edit`) |
| `--subject <text>` | Yes | Draft subject |
| `--body <text>` | Choose one | Mail body. HTML is recommended for rich-text formatting; plain text is also supported (auto-detected). Use `--plain-text` to force plain-text mode. Supports `<img src="./local.png" />` relative paths being automatically resolved to inline images (only relative paths are supported, not absolute paths). Mutually exclusive with `--body-file` |
| `--body-file <path>` | Choose one | Read the mail body HTML from a file (relative path, limited to the cwd subtree). Mutually exclusive with `--body`. File size limit 32 MB |
| `--from <email>` | No | Sender email address (EML From header). When sending with an alias (send_as), set this to the alias address and use `--mailbox` to specify the owning mailbox. When omitted, the mailbox's primary address is used |
| `--mailbox <email>` | No | Mailbox address, specifying the mailbox the draft belongs to (defaults back to `--from`, then back to `me`). Use when the sender (`--from`) differs from the mailbox, such as when sending via an alias or send_as address. Available mailboxes can be queried via `accessible_mailboxes` |
| `--cc '<email>'` | No | Full CC list. For multiple CCs, pass `--cc` repeatedly, with only one address each time, and wrap the parameter value in single quotes |
| `--bcc '<email>'` | No | Full BCC list. For multiple BCCs, pass `--bcc` repeatedly, with only one address each time, and wrap the parameter value in single quotes. Incompatible with `--event-*` (see the `+send` calendar invitation constraint) |
| `--plain-text` | No | Force plain-text mode, ignoring HTML auto-detection. Cannot be used together with `--inline`. In plain-text mode, a plain-text signature is also automatically appended (the HTML signature is converted via `PlainTextFromHTML`, and inline images are discarded) |
| `--attach '<path>'` | No | Attachment file path. For multiple attachments, pass `--attach` repeatedly, with only one relative path each time, and wrap the parameter value in single quotes; they are appended in the order passed. When attachments cause the total EML size to exceed 25 MB, the excess is automatically uploaded as large attachments (an HTML mail inserts a download card, and a plain-text mail appends a download link), with a per-file limit of 3 GB |
| `--inline '<json>'` | No | Advanced usage: manually specify the inline image CID mapping. For multiple inline images, pass `--inline` repeatedly, with only one JSON object each time, wrapped in single quotes: `'{"cid":"mycid","file_path":"./logo.png"}'`. `file_path` must be a relative path; the CID should be unique, for example a random hexadecimal string; reference it in the body with `<img src="cid:mycid">`. It is recommended to use `<img src="./path" />` directly in `--body` (resolved automatically). Cannot be used together with `--plain-text` |
| `--signature-id <id>` | No | Signature ID. Appends the mailbox signature to the end of the body. Run `mail +signature` to view available signatures. Mutually exclusive with `--no-signature` |
| `--no-signature` | No | Skip automatic appending of the default signature. Mutually exclusive with `--signature-id`; when used together, a parameter validation error is returned (exit code 2) |
| `--priority <level>` | No | Mail priority: `high`, `normal`, `low`. When omitted or set to `normal`, no priority is set |
| `--request-receipt` | No | Request a read receipt (RFC 3798 Message Disposition Notification). Writes the `Disposition-Notification-To: <sender>` header in the draft EML, taking effect when sent. The recipient's mail client may show a prompt, send automatically, or ignore it — delivery is not guaranteed |
| `--event-summary <text>` | No | Calendar title. Setting this parameter embeds a calendar invitation in the mail. `--event-start` and `--event-end` must also be set |
| `--event-start <time>` | Conditionally required | Calendar start time (ISO 8601) |
| `--event-end <time>` | Conditionally required | Calendar end time (ISO 8601) |
| `--event-location <text>` | No | Calendar location |

> **Calendar constraints**: `--event-*` and `--send-time` cannot be used at the same time; `--to` and `--cc` recipients automatically become calendar participants (ATTENDEE), while `--bcc` recipients are not counted as participants.

| `--format <mode>` | No | Output format: `json` (default) / `pretty` / `table` / `ndjson` / `csv` |
| `--dry-run` | No | Only print the request, do not execute |

<a id="返回值"></a>
## Return Value

On success:

```json
{
  "ok": true,
  "data": {
    "draft_id": "草稿ID"
  }
}
```

Optional fields:

- `reference`: Draft open link. **Only appears when the current creation chain actually returns it.**

If the creation result includes `reference`, return the draft open link to the user together with `draft_id`; if there is currently no link, handle it silently.

<a id="典型场景"></a>
## Typical Scenarios

<a id="撰写新邮件--创建草稿--预览--发送"></a>
### Compose a new mail → create a draft → preview → send

```bash
# 1. Create a draft
lark-cli mail +draft-create --to 'alice@example.com' --subject 'Q1 报告' --body '请查收附件中的报告。' --attach './q1-report.pdf' --format json

# 2. Send the draft
lark-cli mail user_mailbox.drafts send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```

<a id="创建带内嵌图片的-html-草稿"></a>
### Create an HTML draft with inline images

> **Recommended approach:** Use `<img src="./logo.png" />` (relative path) directly in the `--body` HTML, and the system will automatically create the inline MIME part and replace it with a `cid:` reference. Only relative paths are supported (such as `./logo.png`), not absolute paths (such as `/tmp/logo.png`).

```bash
# Recommended: use relative paths directly, resolved automatically to inline images
lark-cli mail +draft-create \
  --to 'alice@example.com' \
  --subject '通讯稿' \
  --body '<h1>你好</h1><img src="./banner.png" />'

# Advanced usage: manually specify the CID (the CID is a unique identifier; a random hexadecimal string can be used)
lark-cli mail +draft-create \
  --to 'alice@example.com' \
  --subject '通讯稿' \
  --body '<h1>你好</h1><img src="cid:c7d8e9f0a1b2c3d4e5f6">' \
  --inline '[{"cid":"c7d8e9f0a1b2c3d4e5f6","file_path":"./banner.png"}]'
```

<a id="相关命令"></a>
## Related Commands

- `lark-cli mail +draft-edit` — Edit an existing draft
- `lark-cli mail user_mailbox.drafts send` — Send an existing draft
- `lark-cli mail user_mailbox.drafts get` — Get draft content
- `lark-cli mail +reply` / `+reply-all` / `+forward` — Create reply/forward drafts (default), or add `--confirm-send` to send
