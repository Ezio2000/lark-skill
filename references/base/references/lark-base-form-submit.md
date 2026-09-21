# base +form-submit


Fill in and submit a Base form via a form share link. Only share mode (share_token) is supported; supports filling in regular field values and uploading local files as attachments.

> **⚠️ High-risk write operation (high-risk-write):** This command writes and submits data to a form, which is a high-risk write operation. You must additionally pass `--yes` to confirm, otherwise it returns a `confirmation_required` error and exits. When the user explicitly requests submission and the target form is unambiguous, attach `--yes` directly without asking again.

<a id="填写前必读先获取表单详情"></a>
## Must-read before filling in: first get the form details

**Before calling `+form-submit`, you must first use `+form-detail` to get the form details.** Reasons:

1. **Field type matching**: Each question's `type` determines the value format (text, number, option, person, date, etc.); the value in `fields` must be constructed correctly according to the type
2. **Required validation**: Use `questions[].required` to determine which questions are required, to avoid omissions
3. **Display condition filtering**: Some questions have `filter` (show/hide logic); you must determine whether the question should appear based on the values the user has filled in for other questions — **questions hidden by a filter should not be filled in**
4. **Get base_token (required for attachment scenarios)**: The `data.base_token` returned by `+form-detail` is the identifier of the Base that the form belongs to. When the form contains attachment fields, this value must be passed via `--base-token` at submission time, because attachments need to be uploaded to that Base's Drive Media

Typical flow:

```bash
# 1️⃣ First get the form details to understand all questions
lark-cli base +form-detail --share-token <share_token>

# 2️⃣ Based on the returned questions list, format values by type, check required, and evaluate filter conditions

# 3️⃣ Then submit (high-risk write operation, must include --yes)
lark-cli base +form-submit \
  --share-token <share_token> \
  --json '{"fields":{...}}' \
  --yes
```

In the return of `+form-detail`, focus on reading `questions[].type`, `questions[].required`, the question `filter`, and the `data.base_token` required for attachment scenarios.

<a id="命令"></a>
## Command

```bash
# Basic submission (fill in regular fields)
lark-cli base +form-submit \
  --share-token <share_token> \
  --json '{"fields":{"服务评分":5,"评价内容":"服务态度好"}}' \
  --yes

# Submission with attachments (requires additionally providing --base-token)
lark-cli base +form-submit \
  --share-token <share_token> \
  --base-token <base_token> \
  --json '{
    "fields": {"服务评分": 5, "评价内容": "好"},
    "attachments": {
      "附件字段名": ["./report.pdf", "./photo.png"],
      "另一个附件字段": ["./doc.docx"]
    }
  }' \
  --yes

# Use app identity (bot)
lark-cli base +form-submit \
  --share-token <share_token> \
  --json '{"fields":{...}}' \
  --as bot \
  --yes

# Preview the API call (does not actually execute; dry-run does not require --yes)
lark-cli base +form-submit \
  --share-token <share_token> \
  --json '{"fields":{...}}' \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--share-token <token>` | Yes | Form share Token (required), extracted from the form share link |
| `--base-token <token>` | Conditionally required | Base token; **must be provided when `--json` contains `attachments`**, used to upload attachments to Base Drive Media |
| `--json <json>` | Yes | JSON object containing `"fields"` (regular field values) and `"attachments"` (attachment uploads); see the description below for details |
| `--yes` | Yes | Confirm the high-risk write operation. This command is high-risk-write; without `--yes` it returns `confirmation_required` |
| `--format` | No | Output format: json (default)\| pretty \| table \| ndjson \| csv |
| `--as` | No | Identity: user (default)\| bot |
| `--dry-run` | No | Preview the API call without executing |

<a id="--json-结构说明"></a>
### --json structure description

`--json` is a JSON object containing two parts:

<a id="fields普通字段"></a>
#### fields (regular fields)

Common cell values in `fields` are constructed as in the examples below (consistent with the main skill):

```json
{
  "文本字段": "Hello World",
  "电话字段": "13800000000",
  "超链接字段": "https://example.com",
  "数字字段": 12.5,
  "单选字段": "选项A",
  "多选字段": ["选项A", "选项B"],
  "时间字段": "2026-04-27 14:30:00",
  "复选框字段": true,
  "人员字段": [{ "id": "ou_7094d131420c8749632145f08fbf114a" }],
  "关联字段": [{ "id": "recXXXXXXXXXXXX" }],
  "地理位置字段": { "lng": 116.397428, "lat": 39.90923 }
}
```

> **Note: Do not put attachment-type fields in `fields`.** `fields` does not include attachments; attachments have a separate way of being filled in, see the "attachments (attachment upload)" section below.

> System fields such as auto-number, formula, created/modified by, and created/modified time are filled in automatically and do not need to be passed manually.

<a id="attachments附件上传"></a>
#### attachments (attachment upload)

**The way attachment fields are filled in is completely different from regular cells in `fields`**; you cannot pass `file_token` or other attachment formats in `fields`. Attachment fields must be placed separately in the top-level `attachments` object of `--json`, with the value being an **array of local file paths** (not tokens):

```json
{
  "attachments": {
    "附件字段名": ["./report.pdf", "./photo.png"],
    "另一个附件字段": ["./doc.docx"]
  }
}
```

After receiving the paths, the CLI automatically completes the following flow:
1. Validate all files (existence, size ≤2GB, regular files)
2. Upload in parallel to Base Drive Media (concurrency limit 5; duplicate paths across fields are automatically deduplicated)
3. After obtaining `file_token`, merge into the final form submission content

> When writing a Record, attachments use the separate `+record-upload-attachment` command; `+form-submit` instead passes local paths in `attachments`, and the CLI uploads them automatically.

<a id="从分享链接提取-share-token"></a>
### Extract share-token from the share link

When the user provides a form share link in a format such as the following:

```
https://www.example.com/share/base/form/shrbcvST8eZy0vk8zjVZ1CAXNye
```

**Extraction method:** Take the last segment of the URL path as `--share-token`.

Taking the above link as an example:

- `share-token` = `shrbcvST8eZy0vk8zjVZ1CAXNye`

```bash
lark-cli base +form-submit \
  --share-token shrbcvST8eZy0vk8zjVZ1CAXNye \
  --json '{"fields":{...}}' \
  --yes
```

<a id="输出格式"></a>
## Output format

| Field | Type | Description |
|------|------|------|
| `can_submit_again` | bool | Whether it can be filled in again |

```json
{
  "ok": true,
  "data": {
    "can_submit_again": true
  }
}
```

<a id="提示"></a>
## Tips

- **This command is a high-risk write operation (high-risk-write) and must additionally pass `--yes` to confirm**, otherwise it returns `confirmation_required` and exits with a non-zero code; `--dry-run` preview is the exception
- This command only supports submission via a form share link (share_token); it does not support submission via base_token + table_id + view_id
- **When `--json` contains `attachments`, `--base-token` must additionally be provided**, because uploading attachments to Base Drive Media requires specifying the target Base
- Attachment fields only need to provide local paths in `--json.attachments`; the CLI automatically completes validation, parallel upload, Token acquisition, and merged writing
- Rate limits: 20 QPS per app, 5 QPS per user
- Permission requirements: `base:form:update`; when using attachments, `docs:document.media:upload` is also required

<a id="参考"></a>
## References

- [lark-base](../index.md) — all Base commands
- [lark-shared](../../shared/index.md) — authentication and global parameters
