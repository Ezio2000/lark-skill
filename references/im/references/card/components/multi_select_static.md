<a id="下拉多选-multi_select_static"></a>
# Multi-select dropdown `multi_select_static`

Dropdown multi-select. **Card 2.0**. Fields are basically the same as `select_static`, with the difference being the multi-select default value.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "multi_select_static",
  "name": "tags",
  "placeholder": { "tag": "plain_text", "content": "请选择" },
  "options": [
    { "text": { "tag": "plain_text", "content": "选项1" }, "value": "1" },
    { "text": { "tag": "plain_text", "content": "选项2" }, "value": "2" }
  ]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `multi_select_static` |
| `options` | No | Array | / | Option `{text:{plain_text}, value, icon?}`, `value` cannot be duplicated |
| `selected_values` | No | String[] | / | Array of values selected by default |
| `name` | No* | String | / | Unique identifier; **required within form and globally unique** |
| `required` | No | Boolean | false | Whether required (takes effect within form) |
| `type` | No | String | default | `default`(with border) / `text`(plain text) |
| `placeholder` | No | Object | / | Placeholder text, plain_text |
| `width` | No | String | default | `default`(with border, fixed 282px) / `fill` / `[100,∞)px` |
| `disabled` | No | Boolean | false | Whether disabled |
| `behaviors` | No | Array | / | `[{type:"callback", value:{...}}]` |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` |
| `margin` | No | String | 0 | Outer margin [-99,99]px |

<a id="嵌套--易错点"></a>
## Nesting / Common pitfalls

- Can be nested within column_set / form / collapsible_panel / loop container / interactive_container.
- Option `value` must be unique; use `selected_values` (array) for default selection rather than the single-select `initial_*`.
- The callback returns the multiple selected values.
