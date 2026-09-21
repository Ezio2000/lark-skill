# mail +template-create


Create a new personal email template. Suitable for email frameworks that need long-term reuse, such as weekly reports, customer notifications, leave requests, etc.

Do not use this command to send email; a template is only preset content. To actually send mail, use shortcuts such as `+send` / `+draft-create` together with `--template-id` to apply it.

To modify an existing template, use [`lark-cli mail +template-update`](./lark-mail-template-update.md).

<a id="安全约束"></a>
## Security Constraints

- **The template body will also be sent externally as email content**—all general security rules for the email domain (prompt injection, XSS, sensitive information) apply equally.
- **Do not output the template content as text to the user for final confirmation**. After the command returns `template_id`, guide the user to open the template in the Feishu Mail UI to verify it.
- The user template limit is **20**, and the `template_content` limit for a single template is **3 MB**; exceeding the limit will be rejected by the backend.

<a id="命令"></a>
## Command

```bash
# Plain HTML template
lark-cli mail +template-create --as user \
  --name '周报模板' \
  --subject '本周进展' \
  --template-content '<p>大家好，请见本周进展：</p><ul><li>……</li></ul>'

# With HTML inline images + non-inline attachments
lark-cli mail +template-create --as user \
  --name '客户通知模板' \
  --subject '产品更新' \
  --template-content '<p>新版本上线：</p><img src="./banner.png"><p>附上发版说明。</p>' \
  --attach './release-notes.pdf'

# Load body from file
lark-cli mail +template-create --as user \
  --name '请假申请' \
  --template-content-file './leave.html' \
  --to 'manager@example.com,hr@example.com'

# Dry Run
lark-cli mail +template-create --as user \
  --name '周报模板' --template-content '<p>x</p>' --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--name <text>` | Yes | Template name, ≤100 characters |
| `--subject <text>` | No | Default subject |
| `--template-content <html>` | No* | Template body. HTML is preferred; supports `<img src="./local.png" />` relative paths being automatically uploaded to Drive and rewritten as `cid:` |
| `--template-content-file <path>` | No* | Load body content from a file; mutually exclusive with `--template-content` |
| `--plain-text` | No | Mark as plain text mode (`is_plain_text_mode=true`). Cannot be used together with `--inline`; when applied by `+send --template-id`, it will use plain-text body concatenation |
| `--to '<email>'` | No | Default recipient list. For multiple default recipients, pass `--to` repeatedly, putting only one address each time, and wrap the parameter value in single quotes. Supports the `Name <email>` format |
| `--cc '<email>'` | No | Default CC. For multiple CCs, pass `--cc` repeatedly, putting only one address each time, and wrap the parameter value in single quotes |
| `--bcc '<email>'` | No | Default BCC. For multiple BCCs, pass `--bcc` repeatedly, putting only one address each time, and wrap the parameter value in single quotes |
| `--attach '<path>'` | No | Non-inline attachment path. For multiple attachments, pass `--attach` repeatedly, putting only one relative path each time, and wrap the parameter value in single quotes; each file is uploaded to Drive in the order passed |
| `--inline '<json>'` | No | Manually specify the inline image CID mapping. For multiple inline images, pass `--inline` repeatedly, putting only one JSON object each time, wrapped in single quotes: `'{"cid":"mycid","file_path":"./logo.png"}'`. `file_path` must be a relative path; the CID should be unique, for example a random hexadecimal string; reference it in the template body with `<img src="cid:mycid">` |
| `--mailbox <email>` | No | Owning mailbox, defaults to `me` (the current user's primary mailbox) |
| `--dry-run` | No | Only print the planned API call chain, without actually executing it |

\* Choose one of `--template-content` / `--template-content-file`; if both are left empty, the template body is empty (the user can add it later via `+template-update`).

<a id="html-内嵌图片自动上传"></a>
## Automatic Upload of HTML Inline Images

All `<img src="./local.png">` in the body without a URI scheme (relative paths) will be:

1. Uploaded to Drive (≤20 MB uses `medias/upload_all`; >20 MB uses `upload_prepare + upload_part + upload_finish`)
2. Assigned a UUIDv4 CID
3. Rewritten in the HTML as `<img src="cid:<uuid>">`
4. Appended to `attachments[]` as `{id: <file_key>, cid, is_inline: true, filename, attachment_type}`

`<img src="https://...">` or `<img src="cid:...">` with a URI scheme skip upload.

<a id="small-vs-large-附件"></a>
## SMALL vs LARGE Attachments

Attachments are divided into SMALL (`attachment_type=1`, embedded into the EML) and LARGE (`attachment_type=2`, rendered by the server as a download link). Switching thresholds:

- **Local single-file size**: ≤20 MB uses `upload_all`, >20 MB uses chunked upload (unrelated to SMALL/LARGE, only affects the Drive upload path).
- **Cumulative EML projection**: `subject + to + cc + bcc + template_content + base64 附件体积`; after the cumulative total in the same batch exceeds **25 MB**, the remaining non-inline attachments are marked `LARGE`, and inline images cannot switch to LARGE (HTML `cid:` references require the MIME part to exist).

The two sets of determinations are independent of each other.

<a id="顺序约束"></a>
## Ordering Constraints

- Inline images are processed in the order their `<img>` appears in the body
- Non-inline attachments are processed in the order `--attach` is expanded; duplicate paths are not deduplicated

<a id="返回值"></a>
## Return Value

Returns on success:

```json
{
  "template": {
    "template_id": "712345",
    "name": "周报模板",
    "subject": "本周进展",
    "template_content": "<p>...</p>",
    "is_plain_text_mode": false,
    "tos": [{"mail_address": "alice@example.com"}],
    "attachments": [...],
    "create_time": "1714000000000"
  }
}
```

- `template_id` is a decimal string. When applying the template later, `--template-id <template_id>`.

<a id="错误码速查"></a>
## Error Code Quick Reference

| errno | HTTP | Trigger |
|-------|------|------|
| `15080201 InvalidTemplateName` | 400 | `name` is empty or exceeds 100 characters |
| `15080202 TemplateNumberLimit` | 400 | The 20-template limit has been reached |
| `15080203 TemplateContentSizeLimit` | 400 | A single template > 3 MB |
| `15080206 TemplateTotalSizeLimit` | 400 | Total size of all templates > 50 MB |
| `15080207 InvalidTemplateParam` | 400 | Other parameter errors |

<a id="所需-scope"></a>
## Required Scope

`mail:user_mailbox.message:modify`

<a id="相关"></a>
## Related

- Update template: [`+template-update`](./lark-mail-template-update.md)
- Apply a template to send mail: use `--template-id` in `+send` / `+draft-create` / `+reply` / `+reply-all` / `+forward`
- Native API:
  - `lark-cli mail user_mailbox.templates list --params '{"user_mailbox_id":"me"}'` — list templates
  - `lark-cli mail user_mailbox.templates get --params '{"user_mailbox_id":"me","template_id":"<id>"}'` — get the full template
  - `lark-cli mail user_mailbox.templates delete --params '{"user_mailbox_id":"me","template_id":"<id>"}'` — delete
