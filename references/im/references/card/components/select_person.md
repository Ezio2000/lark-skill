<a id="人员选择-单选-select_person"></a>
# Person select - single select `select_person`

Select a single person from the candidate list. **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "select_person",
  "placeholder": { "tag": "plain_text", "content": "请选择" },
  "options": [
    { "value": "ou_xxx" },
    { "value": "ou_yyy" }
  ]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `select_person` |
| `options` | No | Array | / | Candidates, each item `{value: open_id}`; **when empty or all invalid, the candidates are all members in the conversation** |
| `name` | No* | String | / | Unique identifier; **required within a form and globally unique** |
| `required` | No | Boolean | false | Whether it is required (takes effect within a form) |
| `type` | No | String | default | `default`(with border) / `text`(plain text) |
| `placeholder` | No | Object | / | Placeholder text, plain_text |
| `initial_option` | No | String | / | Initially selected open_id, must be within options |
| `width` | No | String | default | `default` / `fill` / `[100,∞)px` |
| `disabled` | No | Boolean | false | Whether disabled |
| `behaviors` | No | Array | / | `[{type:"callback", value:{...}}]` |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` |
| `margin` | No | String | 0 | Outer margin [-99,99]px |

<a id="嵌套--易错点"></a>
## Nesting / Common pitfalls

- Can be nested within column_set / form / collapsible_panel / loop container / interactive_container.
- `options[].value` only accepts **open_id**.
- Callback `action.tag="select_person"` + `action.option` (the open_id of the selected person).
