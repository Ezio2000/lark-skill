# mail +template-update


Update an existing personal email template (full-replacement update). Supports `--inspect` read-only projection, `--print-patch-template` printing a patch skeleton, `--patch-file` structured patch, and flat `--set-*` flags.

> **⚠️ No optimistic locking on the backend → last-write-wins**. Concurrent updates may lose recent changes; the CLI prints a warning to stderr on every successful update.

To create a new template, use [`lark-cli mail +template-create`](./lark-mail-template-create.md).

<a id="工作模式"></a>
## Working modes

| Entry point | Behavior | Writes to the database |
|------|------|---------|
| `--print-patch-template` | Print the JSON skeleton for `--patch-file` | No (purely local) |
| `--inspect` | Return the full projection of the current template | No (GET only) |
| `--set-*` / `--attach` / `--inline` | Merge flat flags, then PUT | Yes |
| `--patch-file` | Merge structured patch + flat flags, then PUT | Yes |

<a id="命令"></a>
## Commands

```bash
# View current state (no modification)
lark-cli mail +template-update --as user --template-id 712345 --inspect

# Print the patch skeleton and save it
lark-cli mail +template-update --as user --print-patch-template > /tmp/tpl-patch.json

# Change subject + cc with flat flags
lark-cli mail +template-update --as user --template-id 712345 \
  --set-subject '每周五发布' \
  --set-cc 'manager@example.com'

# Perform a structured update with a patch file (supports tri-state scenarios such as flipping is_plain_text_mode back to false)
lark-cli mail +template-update --as user --template-id 712345 \
  --patch-file /tmp/tpl-patch.json

# Append a new attachment
lark-cli mail +template-update --as user --template-id 712345 \
  --attach './appendix.pdf'
```

<a id="参数"></a>
## Parameters

<a id="定位"></a>
### Targeting

| Parameter | Required | Description |
|------|------|------|
| `--template-id <id>` | Yes* | Template ID, a decimal integer string |
| `--mailbox <email>` | No | Owning mailbox, defaults to `me` |

\* Can be omitted in the `--print-patch-template` scenario.

<a id="只读--输出"></a>
### Read-only / output

| Parameter | Description |
|------|------|
| `--inspect` | GET only, no modification; returns the full template projection |
| `--print-patch-template` | Print the patch skeleton (no network access); after saving, use it as the starting point for `--patch-file` |

<a id="扁平-set--flag直接指定新值"></a>
### Flat set-* flags (directly specify new values)

| Parameter | Description |
|------|------|
| `--set-name <text>` | Replace the name, ≤100 characters |
| `--set-subject <text>` | Replace the default subject |
| `--set-template-content <html>` | Replace the body. Supports automatic upload and rewriting of `<img src="./local.png" />` relative paths |
| `--set-template-content-file <path>` | Load the replacement body from a file; mutually exclusive with `--set-template-content` |
| `--set-plain-text` | Mark as plain-text mode (set to true). **Not providing it will not set it to false**; to flip an HTML template back to false, use `{"is_plain_text_mode": false}` in `--patch-file` |
| `--set-to <emails>` | Replace the default recipient list with a single parameter value; multiple addresses are still separated by commas within that value, pass `--set-to=""` to clear it |
| `--set-cc <emails>` | Replace the default cc with a single parameter value; multiple addresses are still separated by commas within that value, pass `--set-cc=""` to clear it |
| `--set-bcc <emails>` | Replace the default bcc with a single parameter value; multiple addresses are still separated by commas within that value, pass `--set-bcc=""` to clear it |
| `--attach '<path>'` | Append a non-inline attachment without replacing existing attachments. For multiple attachments, pass `--attach` repeatedly, with only one relative path each time, and wrap the parameter value in single quotes; uploads in the order passed |
| `--inline '<json>'` | Append an inline image without replacing existing attachments. For multiple inline images, pass `--inline` repeatedly, with only one JSON object each time, wrapped in single quotes: `'{"cid":"mycid","file_path":"./logo.png"}'`; `file_path` must be a relative path; the CID should be unique, for example a random hexadecimal string; reference it in the template body with `<img src="cid:mycid">`; rejected when the final template is in plain-text mode |

<a id="结构化-patch"></a>
### Structured patch

| Parameter | Description |
|------|------|
| `--patch-file <path>` | JSON patch file. The structure is the same as the `--print-patch-template` output; any **non-empty field** overrides the corresponding field of the current template |

patch-file fields (all optional; fields not provided keep the current template's original values):

```json
{
  "name": "string (≤100 chars, optional)",
  "subject": "string (optional)",
  "template_content": "string (HTML 或纯文本；本地 <img src> 会自动上传)",
  "is_plain_text_mode": "bool (optional) — 显式 true/false 都生效",
  "tos": [{"mail_address": "...", "name": "..."}],
  "ccs": [{"mail_address": "...", "name": "..."}],
  "bccs": [{"mail_address": "...", "name": "..."}]
}
```

<a id="合并策略"></a>
## Merge strategy

1. `GET` the full current template content
2. First apply the flat `--set-*` flags (non-empty overrides)
3. Then apply `--patch-file` (non-empty fields override) — patch-file takes precedence over flat flags
4. Rescan the new body for `<img>` local paths, upload them to Drive, and rewrite them as `cid:`
5. New attachments appended by `--attach` are independently evaluated as SMALL/LARGE with a new `emlProjectedSize`
6. Deduplicate attachments by `(id, cid)`, then `PUT` the entire template

> **All existing attachments are retained**: only `--attach` new attachments are appended; to delete existing attachments, currently the only options are to rewrite the body via `template_content` in `--patch-file` to remove the corresponding `<img>` references, or to use the native API to rewrite the whole block.

<a id="dryrun-行为"></a>
## DryRun behavior

- Default: print `GET /user_mailboxes/:id/templates/:tid` + Drive upload steps (if there are `<img>`, `--attach`, or `--inline`) + `PUT` steps.
- `--inspect`: print only `GET`.
- `--print-patch-template`: print the skeleton without making any API calls.

<a id="返回值"></a>
## Return value

On success, returns:

```json
{
  "template": {
    "template_id": "712345",
    "name": "周报模板",
    "subject": "每周五发布",
    "template_content": "...",
    "is_plain_text_mode": false,
    "tos": [...],
    "attachments": [...],
    "create_time": "1714000000000"
  }
}
```

`--inspect` returns the same structure; `--print-patch-template` returns the patch JSON skeleton.

<a id="错误码速查"></a>
## Error code quick reference

| errno | HTTP | Trigger |
|-------|------|------|
| `15080201 InvalidTemplateName` | 400 | `--set-name` is empty or exceeds 100 characters |
| `15080203 TemplateContentSizeLimit` | 400 | After the update, `template_content` > 3 MB |
| `15080204 InvalidTemplateID` | 404 | `template_id` does not exist or does not belong to the current user |
| `15080207 InvalidTemplateParam` | 400 | Other parameter errors (including `template_id` failing parseInt) |

<a id="所需-scope"></a>
## Required scopes

`mail:user_mailbox.message:modify`, `mail:user_mailbox:readonly`

<a id="相关"></a>
## Related

- Create a template: [`+template-create`](./lark-mail-template-create.md)
- Send mail using a template: use `--template-id` in `+send` / `+draft-create` / `+reply` / `+reply-all` / `+forward`
- Delete a template (native API): `lark-cli mail user_mailbox.templates delete --params '{"user_mailbox_id":"me","template_id":"<id>"}'`
