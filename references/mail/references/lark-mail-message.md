# mail +message


Read the full content of a specified email, including the email headers, body (plain text + optional HTML), and a unified `attachments` list (covering regular attachments and inline images).

`mail +message` is only suitable for reading one email, one `message_id`. If you already have multiple `message_id`, use `mail +messages --message-ids <id1>,<id2>,<id3>`; do not call `mail +message` in a loop.

The CLI builds the final JSON in two stages:
- Safe email metadata fields are passed through directly
- The body, attachments, and auxiliary fields are derived by the shortcut

This module corresponds to shortcut `lark-cli mail +message`, with internal steps:
1. `GET /open-apis/mail/v1/user_mailboxes/{mailbox}/messages/{message_id}` — Get the full email content

<a id="命令"></a>
## Command

```bash
# Read one email (includes HTML body by default)
lark-cli mail +message --message-id <message-id>

# Plain text body only (smaller payload, suitable for AI processing)
lark-cli mail +message --message-id <message-id> --html=false

# Specify mailbox
lark-cli mail +message --mailbox user@example.com --message-id <message-id>

# JSON output (script-friendly)
lark-cli mail +message --message-id <message-id> --format json

# Dry Run
lark-cli mail +message --message-id <message-id> --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Default | Description |
|------|------|--------|------|
| `--message-id <id>` | Yes | — | A single email ID; for multiple IDs use `mail +messages --message-ids` |
| `--mailbox <email>` | No | Current user | Email address (`user_mailbox_id`) |
| `--html` | No | true | Whether to return the HTML body (`false` returns plain text only, reducing bandwidth) |
| `--format <mode>` | No | json | Output format: `json` (default) / `pretty` / `table` / `ndjson` / `csv` |
| `--dry-run` | No | — | Print the request only, do not execute |

<a id="返回值"></a>
## Return Value

On success, returns a `{"ok": true, "data": ...}` structure, and the `data` field contains:

```json
{
  "message_id":               "邮件 ID",
  "thread_id":                "会话 ID",
  "smtp_message_id":          "RFC 2822 Message-ID",
  "subject":                  "邮件主题",
  "head_from":                {"mail_address": "alice@example.com", "name": "Alice"},
  "to":                       [{"mail_address": "bob@example.com", "name": "Bob"}],
  "cc":                       [{"mail_address": "carol@example.com", "name": "Carol"}],
  "bcc":                      [],
  "date":                     "Thu, 19 Mar 2026 16:33:02 +0800",
  "in_reply_to":              "<original@domain>",
  "reply_to":                 "reply-to@domain",
  "reply_to_smtp_message_id": "reply-to@domain",
  "references":               ["<a@domain>", "<b@domain>"],
  "internal_date":            "1748000000000",
  "date_formatted":           "2026-03-19 16:33",
  "message_state":            1,
  "message_state_text":       "received",
  "folder_id":                "INBOX",
  "label_ids":                ["UNREAD"],
  "priority_type":            "1",
  "priority_type_text":       "high",
  "security_level": {
    "is_risk": true,
    "risk_banner_level": "DANGER",
    "risk_banner_reason": "UNAUTH_EXTERNAL",
    "is_header_from_external": true,
    "via_domain": "example.com",
    "spam_banner_type": "USER_RULE",
    "spam_user_rule_id": "76180000000025388",
    "spam_banner_info": "blocked.example.com"
  },
  "body_plain_text":          "Hi Bob, ...",
  "body_preview":             "Hi Bob, ...",
  "body_html":                "<html>...</html>",
  "attachments": [
    {
      "id":              "att_xxx",
      "filename":        "report.pdf",
      "attachment_type": 1,
      "is_inline":       false
    },
    {
      "id":           "att_yyy",
      "filename":     "logo.png",
      "content_type": "image/png",
      "is_inline":    true,
      "cid":          "logo@cid"
    }
  ]
}
```

<a id="字段说明"></a>
### Field Descriptions

> Note: Use `--format json` to get structured output. All JSON output is uniformly wrapped in a `{"ok": true, "data": ...}` structure.

| Field | Description |
|------|------|
| `message_id` | Email ID |
| `thread_id` | Thread ID |
| `subject` | Email subject |
| `head_from` | Sender object: `{mail_address, name}` |
| `to` | Recipient list: `[{mail_address, name}]` |
| `cc` | CC list: `[{mail_address, name}]` |
| `bcc` | BCC list: `[{mail_address, name}]` |
| `date` | Time in the EML (milliseconds) |
| `date_formatted` | Human-readable send time, such as `"2026-03-19 16:33"` |
| `smtp_message_id` | RFC 2822-compliant SMTP Message-ID |
| `in_reply_to` | In-Reply-To email header |
| `references` | References email header, a list of ancestor SMTP message IDs |
| `internal_date` | Created/received/sent time (milliseconds) |
| `message_state` | Email status: `1` = received, `2` = sent, `3` = draft |
| `message_state_text` | `"unknown"` / `"received"` / `"sent"` / `"draft"` |
| `folder_id` | Folder ID. Values: `INBOX`, `SENT`, `SPAM`, `ARCHIVED`, `STRANGER`, or a custom folder ID |
| `label_ids` | List of label IDs |
| `priority_type` | Priority value: `0` = no priority, `1` = high, `3` = normal, `5` = low |
| `priority_type_text` | `"unknown"` / `"high"` / `"normal"` / `"low"` |
| `draft_id` | Draft ID, obtainable via the list drafts API |
| `reply_to` | Reply-To email header |
| `reply_to_smtp_message_id` | Reply-To SMTP Message-ID |
| `body_plain_text` | **The body field recommended for LLM reading**; already base64url-decoded and ANSI escape sequences cleaned |
| `body_preview` | First 100 characters of the plain text body, for quick preview |
| `body_html` | Raw HTML body; omitted when `--html=false` |
| `attachments` | Unified list of regular attachments and inline images |
| `attachments[].id` | Attachment ID (used for the download URL API) |
| `attachments[].filename` | Attachment filename |
| `attachments[].content_type` | Attachment MIME type |
| `attachments[].attachment_type` | Attachment type: `1` = regular attachment, `2` = large attachment |
| `attachments[].is_inline` | `true` = inline image, `false` = regular attachment |
| `attachments[].cid` | Content-ID of the inline image (corresponds to the `<img src="cid:...">` reference in the HTML body) |

### security_level

Returned when the server has risk metadata for this email.

| Field | Description |
|------|------|
| `is_risk` | Boolean. `true` indicates the email is flagged as risky |
| `risk_banner_level` | Risk level. Values: `WARNING`, `DANGER`, `INFO` |
| `risk_banner_reason` | Risk reason. Values: `NO_REASON`, `IMPERSONATE_DOMAIN` (similar domain impersonation), `IMPERSONATE_KP_NAME` (key person name impersonation), `UNAUTH_EXTERNAL` (unauthenticated external domain), `MALICIOUS_URL`, `MALICIOUS_ATTACHMENT`, `PHISHING`, `IMPERSONATE_PARTNER` (partner impersonation), `EXTERNAL_ENCRYPTION_ATTACHMENT` (external encrypted attachment) |
| `is_header_from_external` | Boolean. `true` indicates the sender is from an external domain |
| `via_domain` | The SPF/DKIM domain shown when the email is sent on behalf of or forged, such as `"larksuite.com"` |
| `spam_banner_type` | Spam reason. Values: `USER_REPORT` (reported by user), `USER_BLOCK` (blocked by user), `ANTI_SPAM` (system determined as spam), `USER_RULE` (matched inbox rule), `BLOCK_DOMIN` (domain blocked by user), `BLOCK_ADDRESS` (address blocked by user) |
| `spam_user_rule_id` | Matched inbox rule ID |
| `spam_banner_info` | Address or domain matching the user's blocklist, such as `"larksuite.com"` |

<a id="注意事项"></a>
## Notes

- **JSON output is directly usable** — By default it outputs valid UTF-8 JSON, which can be read directly without additional encoding conversion.
- **Dedicated to reading a single email** — `mail +message` accepts only one `message_id`. For multiple IDs use `mail +messages --message-ids <id1>,<id2>,<id3>`, avoiding calling in a loop email by email.
- In the JSON output, `<` / `>` inside `body_html` may appear as `\u003c` / `\u003e` (JSON-safe escaping, content unchanged, `jq -r` can restore it).
- `mail +message` no longer fetches attachment/image download URLs by default. This keeps email detail reading lighter, and callers can request URLs separately as needed.
- View the raw HTML:

```bash
# jq -r automatically handles JSON escaping and outputs the raw HTML
lark-cli mail +message --message-id <id> --format json | jq -r '.data.body_html'
```

<a id="典型场景"></a>
## Typical Scenarios

<a id="读取邮件--摘要--回复"></a>
### Read email → summarize → reply

```bash
# 1. Read the email (plain text only, smaller payload)
lark-cli mail +message --message-id <id> --html=false --format json

# 2. Have the LLM analyze body_plain_text and draft a reply

# 3. Send the reply
lark-cli mail +reply --message-id <id> --body "..."
```

<a id="按需获取附件或内嵌图片下载-url"></a>
### Fetch attachment or inline image download URLs on demand

```bash
# 1. Read the email, get attachment IDs from .data.attachments[]
lark-cli mail +message --message-id <id> --format json

# 2. Fetch download URLs only for the IDs you need
lark-cli schema mail.user_mailbox.message.attachments.download_url
lark-cli mail user_mailbox.message.attachments download_url \
  --params '{"user_mailbox_id":"me","message_id":"<id>","attachment_ids":["att_xxx","att_yyy"]}'
```

Regular attachments and inline images use the same `user_mailbox.message.attachments download_url` native API (no shortcut wrapper); just pass `attachments[].id`.

<a id="日程邀请邮件"></a>
## Calendar Invitation Emails

When an email contains a calendar invitation (`text/calendar`), the output includes a `calendar_event` object:

```json
{
  "calendar_event": {
    "method": "REQUEST",
    "uid": "abc123",
    "summary": "产品评审",
    "start": "2026-04-20T14:00:00+08:00",
    "end": "2026-04-20T15:00:00+08:00",
    "location": "5F-大会议室",
    "organizer": "sender@example.com",
    "attendees": ["alice@example.com", "bob@example.com"]
  }
}
```

Field descriptions:

- `method`: ICS `METHOD`, usually `REQUEST` / `REPLY` / `CANCEL`.
- `uid`: Calendar UID.
- `summary`: Calendar title.
- `start` / `end`: Start / end time (RFC 3339 UTC).
- `location`: Location (may be empty).
- `organizer`: Organizer email.
- `attendees`: List of attendee emails.

<a id="相关命令"></a>
## Related Commands

- `lark-cli mail +thread` — Read all emails in a thread
- `lark-cli mail +reply` — Reply to an email
- `lark-cli mail +forward` — Forward an email
- `lark-cli mail user_mailbox.message.attachments download_url` — Fetch email attachment/image download URLs on demand
- `lark-cli mail user_mailbox.messages list` — List inbox emails (to get `message_id`)
