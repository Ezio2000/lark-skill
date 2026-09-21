<a id="人员选择-多选-multi_select_person"></a>
# Person select - multiple `multi_select_person`

Select multiple from candidate people. **Card 2.0**. Fields are basically the same as `select_person`, the difference is the multiple-select default value.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "multi_select_person",
  "name": "reviewers",
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
| `tag` | Yes | String | / | Fixed `multi_select_person` |
| `options` | No | Array | / | Candidate `{value: open_id}`; when empty or all invalid, the options are all members of the chat |
| `selected_values` | No | String[] | / | Array of open_ids selected by default |
| `name` | No* | String | / | Unique identifier; **required inside form and globally unique** |
| `required` | No | Boolean | false | Whether required (takes effect inside form) |
| `type` | No | String | default | `default`(with border) / `text`(plain text) |
| `placeholder` | No | Object | / | Placeholder text, plain_text |
| `width` | No | String | default | `default` / `fill` / `[100,∞)px` |
| `disabled` | No | Boolean | false | Whether disabled |
| `behaviors` | No | Array | / | `[{type:"callback", value:{...}}]` |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` |
| `margin` | No | String | 0 | Outer margin [-99,99]px |

<a id="嵌套--易错点"></a>
## Nesting / common pitfalls

- Can be nested inside column_set / form / collapsible_panel / loop container / interactive_container.
- `options[].value` only accepts **open_id**; for default selection use `selected_values` (array).
- The callback returns the multiple selected open_ids.
