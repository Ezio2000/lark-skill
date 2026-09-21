<a id="下拉单选-select_static"></a>
# Dropdown single select `select_static`

Dropdown menu single select. **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "select_static",
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
| `tag` | Yes | String | / | Fixed `select_static` |
| `options` | No | Array | / | Options, see below |
| `options[].text` | Yes | Object | / | Option name, plain_text |
| `options[].value` | Yes | String | / | Option callback value, **must be unique within the same component** |
| `options[].icon` | No | Object | / | Option prefix icon (same as `div.icon`) |
| `name` | No* | String | / | Unique identifier; **required within a form and globally unique** |
| `required` | No | Boolean | false | Whether required (takes effect within a form) |
| `type` | No | String | default | `default` (with border) / `text` (plain text) |
| `placeholder` | No | Object | / | Placeholder text, plain_text |
| `initial_option` | No | String | / | Initially selected content (overrides placeholder and initial_index) |
| `initial_index` | No | Int | / | Initial selected index, 0=not selected, 1=first |
| `width` | No | String | default | `default` / `fill` / `[100,∞)px` |
| `disabled` | No | Boolean | false | Whether disabled |
| `behaviors` | No | Array | / | `[{type:"callback", value:{...}}]` |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` |
| `margin` | No | String | 0 | Outer margin [-99,99]px |

<a id="嵌套--易错点"></a>
## Nesting / Common pitfalls

- Can be nested within column_set / form / collapsible_panel / loop container / interactive_container.
- Option `value` must be unique, otherwise interaction will be abnormal and the server cannot distinguish which one was selected.
- Callback `action.tag="select_static"` + `action.option` (the value of the selected option).
