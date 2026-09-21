# base +form-questions-create


Batch add questions to a Base form/survey. You can create new fields and use them as questions, or add existing fields to the form as questions without creating new fields.

<a id="命令"></a>
## Command

```bash
# Add a required text question
lark-cli base +form-questions-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"type":"text","title":"您的姓名是？","required":true}]'

# Add multiple questions (in order)
lark-cli base +form-questions-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"type":"text","title":"您的姓名是？","required":true},{"type":"text","title":"您的联系方式是？","required":false}]'

# Add a single-select question (with options)
lark-cli base +form-questions-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"type":"select","title":"满意度评价","required":true,"multiple":false,"options":[{"name":"非常满意","hue":"Green"},{"name":"满意","hue":"Blue"},{"name":"一般","hue":"Yellow"}]}]'

# Add a rating question
lark-cli base +form-questions-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"type":"number","title":"服务评分","style":{"type":"rating","icon":"star","min":1,"max":5}}]'
  
# Add a question with a description (plain text)
lark-cli base +form-questions-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"type":"text","title":"您的姓名","description":"请填写真实姓名"}]'
# Add a question with a description (with a link)
lark-cli base +form-questions-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"type":"text","title":"反馈建议","description":"更多详情请查看[帮助文档](https://example.com/help)"}]'  

# Add a question with a visibility rule (visible_rule): show "Invoice title" only when "Do you need an invoice?" is set to "Yes"
lark-cli base +form-questions-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"type":"select","title":"是否需要发票","required":true,"options":[{"name":"是","hue":"Blue"},{"name":"否","hue":"Gray"}]},{"type":"text","title":"发票抬头","visible_rule":{"logic":"and","conditions":[["是否需要发票","==","是"]]}}]'

# Add an existing field to the form as a question without creating a new field
lark-cli base +form-questions-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"use_existing_field":true,"field_id":"fldEmail","title":"你的邮箱","description":"用于接收回执","required":true}]'
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--base-token <token>` | Yes | Base Token (base_token) |
| `--table-id <id>` | Yes | Table ID |
| `--form-id <id>` | Yes | Form ID |
| `--questions <json>` | Yes | Question JSON array, up to 10 (see the format below) |
| `--format` | No | Output format: json (default) \| pretty \| table \| ndjson \| csv |
| `--as` | No | Identity: user (default) \| bot |
| `--dry-run` | No | Preview the API call without executing it |

<a id="--questions-格式"></a>
## `--questions` Format

`--questions` is an array of 1 to 10 question objects. Each object is one of two forms:

- New-field question: create a new field and use that field as a form question.
- Existing-field question: add an existing field to the form, changing only the field's visibility in the form without creating a field.

<a id="形态-a新建字段题目"></a>
### Form A: New-field question

A new-field question creates a new field in the table, and the returned question `id` is the `field_id` of the new field. The CLI currently requires each new-field question to explicitly pass `title` and `type`.

| Field                    | Required | Description |
|-----------------------|------|------|
| `title`               | **Yes** | Question title (field name) |
| `type`                | **Yes** | Question type: `text`, `number`, `select`, `datetime`, `user`, `attachment`, `location` |
| `description`         | No | Question description (plain text or a Markdown link, such as `[文本](https://example.com)`) |
| `required`            | No | Whether it is required (true/false) |
| `option_display_mode` | No | Option display mode (only valid for `select`): `0`=dropdown, `1`=vertical (default), `2`=horizontal |
| `multiple`            | No | Whether multiple selection is allowed (valid for `select`/`user` types, bool) |
| `options`             | No | Option list (only valid for `select`): `[{"name":"选项1","hue":"Blue"}]`, hue options: `Red`/`Orange`/`Yellow`/`Green`/`Blue`/`Purple`/`Gray` |
| `style`               | No | Field style configuration (see the description below) |
| `visible_rule`        | No | Question visibility condition (see "`visible_rule` Visibility Condition" below) |

<a id="形态-b已有字段题目"></a>
### Form B: Existing-field question

An existing-field question only adds an existing field to the form; it does not create a field or change existing record data. It is suitable for adding back questions that were previously removed from the form with `+form-questions-delete --keep-field`, or for supplementing the form with fields that already exist in the table.

| Field                    | Required | Description |
|-----------------------|------|------|
| `use_existing_field`  | **Yes** | Always pass `true`, indicating that an existing field is used |
| `field_id`            | **Yes** | The ID or field name of the existing field; field ID is recommended to avoid ambiguity with fields of the same name. Reference length is 1 to 100; for longer field names, use the field ID instead |
| `title`               | No | Question title; if omitted, the field name is used |
| `description`         | No | Question description (plain text or a Markdown link, such as `[文本](https://example.com)`) |
| `required`            | No | Whether it is required (true/false), default false |
| `option_display_mode` | No | Option display mode (only valid when the existing field is `select`): `0`=dropdown, `1`=vertical (default), `2`=horizontal |
| `visible_rule`        | No | Question visibility condition (see "`visible_rule` Visibility Condition" below) |

An existing-field question must not carry field definition properties, such as `type`, `style`, `options`, `multiple`, `name`. The server uses a strict schema, and fields mistakenly passed that do not belong to this form will be rejected.

<a id="style-字段说明"></a>
### `style` Field Description

| Type | style structure | Description |
|------|------|------|
| `text` | `{"type":"plain"}` | Currently only `plain` is supported |
| `number` | `{"type":"plain","precision":2}` | precision is the number of decimal places |
| `number` (rating) | `{"type":"rating","icon":"star","min":1,"max":5}` | icon options: `star`/`heart`/`thumbsup`/`fire`/`smile`/`lightning`/`flower`/`number` |
| `datetime` | `{"format":"yyyy/MM/dd"}` | format options: `yyyy/MM/dd`, `yyyy/MM/dd HH:mm`, `MM-dd`, `MM/dd/yyyy`, `dd/MM/yyyy` |

<a id="visible_rule-显隐条件"></a>
### `visible_rule` Visibility Condition

> **Read the structure description below only when the user explicitly asks to set a visibility condition (show/hide logic) for a question; otherwise ignore this section.**

`visible_rule` controls whether a question is shown or hidden in the form: the question is shown when the condition is met and hidden when it is not; if it is not passed or `conditions` is an empty array, the question is always shown.

- **The structure is exactly the same as view filter `filter`**, that is, `{logic?, conditions?}`, sharing the same common protocol.
- The only difference from view `filter`: `field` in `conditions` references the **question name or question ID of other questions in the same form** (question ID is recommended to avoid ambiguity from duplicate names), not a table field.
- **Only preceding questions can be referenced**: conditions can only reference questions that come before the current question — at creation time, this is determined by the order of the `questions` array (you can reference an earlier new question in the same batch or an existing question in the form); circular references are not supported.
- The referenced question must actually exist, otherwise an error is reported.
- Listing questions (`+form-questions-list`) **returns `visible_rule` as-is** in each question object; questions without a visibility condition return `null` or an empty array for `conditions`.

```json
{
  "logic": "and",
  "conditions": [
    ["是否需要发票", "==", "是"],
    ["报销金额", ">=", 1000]
  ]
}
```

For the detailed `visible_rule` structure (top-level rules, operator list, and value syntax for each question type), read [lark-base-filter-condition.md](lark-base-filter-condition.md).

<a id="输出格式"></a>
## Output Format

Returns the list of successfully created questions:

```json
{
  "ok": true,
  "data": {
    "items": [
      {"id": "q_001", "title": "您的姓名是？", "required": true}
    ]
  }
}
```

<a id="工作流"></a>
## Workflow

> [!CAUTION]
> This is a **write operation** — you must confirm with the user before executing.

1. First determine the real `table_id` that the form belongs to, and reuse it throughout the entire form management workflow; call `+table-list` only when the ID is missing or the ownership is unclear.
2. Use `+form-questions-list` to view existing questions. The question `id` is the `field_id` that carries the question, not a temporary ID independent of the table.
3. When you need to add an existing field from the table to the form, first use `+field-list` to confirm the real field ID and field type, then use `use_existing_field:true` + `field_id`; if the field is already a visible question, do not create it again — use `+form-questions-update` instead.
4. Unless the user explicitly asks for an independent question with the same name, when the target title already exists, use `+form-questions-update` to update the required status, title, or description; do not create a question with the same name and then delete the old question.
5. Create questions that truly do not exist, or independent questions with the same name explicitly requested by the user, and report the IDs of the newly created questions.

`+form-questions-delete` deletes the table field that carries the question and its record data by default; if you only want to remove the question from the form while keeping the field, you must use `+form-questions-delete --keep-field`. After removal, you can add it back using the existing-field question form described in this document.

<a id="参考"></a>
## References

- [lark-base](../index.md) — all Base commands
- [lark-base-filter-condition.md](lark-base-filter-condition.md) — common protocol for `visible_rule` / `filter` condition structures
- [lark-shared](../../shared/index.md) — authentication and global parameters
