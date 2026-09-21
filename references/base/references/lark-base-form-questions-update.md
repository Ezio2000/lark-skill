# base +form-questions-update


Batch update question configurations (title, description, required, visibility conditions, etc.) in Base forms/surveys.

> [!CAUTION]
> `+form-questions-update` is a **full overwrite of question configuration**, not a patch. For each question passed in, attributes not carried will fall back to default values; explicitly passing an empty string / `null` / an empty array will directly write empty or clear; if you want to preserve existing attributes, you must first use `+form-questions-list` to retrieve the current state, then bring back the fields to preserve together in `--questions`.

<a id="命令"></a>
## Command

```bash
# First read the existing question configuration as the baseline for read-modify-write
lark-cli base +form-questions-list \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id>

# Update a question's title, while bringing back the required / description / visible_rule fields to preserve
lark-cli base +form-questions-update \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"id":"q_001","title":"您的真实姓名是？","description":"请填写真实姓名","required":true,"visible_rule":null}]'

# Update multiple questions at once; each object should be the target complete configuration for that question
lark-cli base +form-questions-update \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"id":"q_001","title":"姓名（必填）","required":true},{"id":"q_002","title":"联系方式","required":false}]'
  
# Update the question description (plain text), while bringing back the title / required / visible_rule to preserve
lark-cli base +form-questions-update \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"id":"q_001","title":"您的姓名","description":"请填写您的真实姓名","required":true,"visible_rule":null}]'
# Update the question description (with a link), while bringing back the title / required / visible_rule to preserve
lark-cli base +form-questions-update \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"id":"q_001","title":"反馈建议","description":"更多说明请参考[帮助文档](https://example.com/help)","required":false,"visible_rule":null}]'

# Update the question visibility condition (visible_rule), while bringing back the title / description / required to preserve
lark-cli base +form-questions-update \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"id":"q_002","title":"发票抬头","description":"","required":false,"visible_rule":{"logic":"and","conditions":[["q_001","==","是"]]}}]'

# Clear the question visibility condition (so the question is always displayed), while bringing back the title / description / required to preserve
lark-cli base +form-questions-update \
  --base-token <base_token> \
  --table-id <table_id> \
  --form-id <form_id> \
  --questions '[{"id":"q_002","title":"发票抬头","description":"","required":false,"visible_rule":null}]'
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--base-token <token>` | Yes | Base Token (base_token) |
| `--table-id <id>` | Yes | Table ID |
| `--form-id <id>` | Yes | Form ID |
| `--questions <json>` | Yes | Question update JSON array, up to 10 (see format below) |
| `--format` | No | Output format: json (default) \| pretty \| table \| ndjson \| csv |
| `--as` | No | Identity: user (default) \| bot |
| `--dry-run` | No | Preview the API call without executing |

<a id="--questions-格式"></a>
## `--questions` Format

Each question object must contain `id`. Note: the object is not an incremental patch, but the target complete configuration for that question; fields not carried will be rebuilt according to server-side default values.

| Field | Required | Description |
|------|------|------|
| `id` | **Yes** | Question ID (field_id), cannot be modified |
| `title` | No | Target question title; omitting it will fall back to the field name, passing an empty string will write an empty title (if the server allows it) |
| `description` | No | Target question description (plain text or Markdown link, such as `[文本](https://example.com)`); omitting it or passing an empty string will clear the description |
| `required` | No | Whether the target is required; omitting it will fall back to `false` |
| `option_display_mode` | No | Target option display method (only valid for `select`): `0`=dropdown, `1`=vertical (default), `2`=horizontal; omitting it will fall back to the default display method |
| `visible_rule` | No | Target question visibility condition; pass a complete `{logic, conditions}` object to overwrite, passing `null` or omitting it will clear (see explanation below) |

<a id="全量覆盖语义"></a>
## Full Overwrite Semantics

- First execute `+form-questions-list` to read the current `id`, `title`, `description`, `required`, `option_display_mode`, `visible_rule` of the question being updated.
- When constructing `--questions`, only change the fields the user explicitly requested to change; all fields that should still be preserved must be passed back together according to their current values.
- Do not update questions by "only passing the fields to change". For example, passing only `{"id":"q_002","title":"新标题"}` will cause `description` to be cleared, `required` to fall back to `false`, and `visible_rule` to be cleared.
- Only pass empty values when the user explicitly requests clearing: `description:""` clears the description, `visible_rule:null` clears the visibility condition, and `conditions:[]` also means unconditional display.

<a id="visible_rule-显隐条件"></a>
### `visible_rule` Visibility Condition

> **Only when the user explicitly requests to set or modify a question's visibility condition (show/hide logic) do you need to read the structure explanation below; otherwise ignore this section.**

`visible_rule` controls question show/hide, and its **structure is completely identical to the view filter `filter`** (`{logic?, conditions?}`), sharing the same common protocol.

- `field` in `conditions` references **the question name or question ID of other questions within the same form** (using the question ID is recommended).
- When updating, it is determined according to the **actual order** of questions in the form; you can only reference questions that come before the current question; circular references are not supported.
- Updating `visible_rule` requires passing a **complete** `{logic, conditions}` object (full overwrite); to preserve the existing visibility condition, you must bring back the current `visible_rule` as-is; passing `null`, omitting `visible_rule`, or passing an empty `conditions` will all make the question always displayed.
- Listing questions (`+form-questions-list`) will **return as-is** `visible_rule` in each question object; questions without a visibility condition set return `null` or `conditions` as an empty array.

```json
{
  "logic": "and",
  "conditions": [
    ["q_001", "==", "是"],
    ["q_003", ">=", 1000]
  ]
}
```

For the detailed `visible_rule` structure (top-level rules, operator list, value syntax for each question type), please read [lark-base-filter-condition.md](lark-base-filter-condition.md).

<a id="输出格式"></a>
## Output Format

Returns the updated question list:

```json
{
  "ok": true,
  "data": {
    "items": [
      {"id": "q_001", "title": "姓名（必填）", "required": true}
    ]
  }
}
```

<a id="工作流"></a>
## Workflow

> [!CAUTION]
> This is a **write operation** — you must confirm with the user before executing.

1. First use `+form-questions-list` to obtain the existing questions and their `id` and complete configuration.
2. Using the existing configuration as the baseline, only modify the fields the user explicitly requested to change; fields to preserve must be brought back as-is.
3. Construct the update array containing `id` and the target complete configuration.
4. Execute the command and report the update result.

<a id="参考"></a>
## References

- [lark-base](../index.md) — all Base commands
- [lark-base-filter-condition.md](lark-base-filter-condition.md) — common protocol for `visible_rule` / `filter` condition structures
- [lark-shared](../../shared/index.md) — authentication and global parameters
