# base +form-detail

Read form details via a form share token. This is a read-only operation, suitable for parsing the question structure, required fields, display conditions, and the Base token needed for attachment submission before submitting a form.

<a id="何时使用"></a>
## When to use

- The user provides a `/share/base/form/{shareToken}` form share link; first extract the last segment as the `--share-token`.
- Before preparing to call `+form-submit`, you must first use `+form-detail` to read the `questions[]`.
- When you only know the share link and do not yet know the `base-token` / `table-id` / `form-id`, use `+form-detail`; only when the form is already managed inside a Base, use `+form-get`.

```bash
lark-cli base +form-detail --share-token <share_token> --format pretty
```

<a id="读取重点"></a>
## Key fields to read

Key fields returned by `+form-detail`:

| Field | Purpose |
|---|---|
| `base_token` | The Base to which the form belongs; must be passed to `+form-submit --base-token` when submitting attachments |
| `questions[].id` | Question identifier, usually corresponding to the field ID |
| `questions[].title` | Field name/question name used at submission; rely on the actual returned value |
| `questions[].type` | Determines the value format; for the submission structure, see [form-submit](lark-base-form-submit.md) |
| `questions[].required` | Determines required fields |
| `questions[].filter` | Determines whether a question is visible for the current submission; do not fill in hidden questions |

In addition to fixed fields, questions carry dynamic configuration by type, such as `select.options` / `select.multiple`, `number.style`, `datetime.style.format`, `user.multiple`, `link.link_table`, `formula.expression`, `lookup.from/select/where/aggregate`. Construct values according to the returned structure before submitting; do not guess the question type or options.

<a id="filter-显示条件"></a>
## filter display conditions

`questions[].filter` controls question display/hiding:

```json
{
  "conjunction": "and",
  "conditions": [
    {"field_name": "是否携带家属", "operator": "is", "value": ["是"]},
    {"field_name": "参与人数", "operator": "isGreater", "value": [1]}
  ]
}
```

- `conjunction` is `and` / `or`, meaning all conditions are met or any condition is met.
- `conditions[].field_name` references the `title` of another question.
- `conditions[].operator` is commonly `is`, `isNot`, `contains`, `doesNotContain`, `isEmpty`, `isNotEmpty`, `isGreater`, `isGreaterEqual`, `isLess`, `isLessEqual`.
- `isEmpty` / `isNotEmpty` do not require `value`.
- The filter for attachment questions is only suitable for `isEmpty` / `isNotEmpty`.

If the currently filled-in values do not satisfy a question's `filter`, that question is considered hidden and should not be included in `+form-submit --json.fields` or `--json.attachments`.

<a id="与-form-submit-的关系"></a>
## Relationship with form-submit

Submitting ordinary fields:

```bash
lark-cli base +form-submit \
  --share-token <share_token> \
  --json '{"fields":{"姓名":"张三","评分":5}}'
```

Submitting attachment fields:

```bash
lark-cli base +form-submit \
  --share-token <share_token> \
  --base-token <base_token_from_form_detail> \
  --json '{"fields":{"姓名":"张三"},"attachments":{"附件":["./report.pdf"]}}'
```

Attachment fields should not be written into `fields`; put them in the top-level `attachments`, with the value being an array of local file paths.
