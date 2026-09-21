<a id="输入框-input"></a>
# Input `input`

Collects user text input. Often embedded within `form` together with a submit button. **Card 2.0**.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "input",
  "name": "comment",
  "placeholder": { "tag": "plain_text", "content": "请输入" },
  "label": { "tag": "plain_text", "content": "备注：" }
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `input` |
| `name` | No* | String | / | Unique identifier; **required within form and globally unique**, used to identify submitted data |
| `required` | No | Boolean | false | Whether required (only effective within form) |
| `placeholder` | No | Object | / | Placeholder text, plain_text, ≤100 characters |
| `default_value` | No | String | / | Prefilled content |
| `label` | No | Object | / | Description text, plain_text |
| `label_position` | No | String | top | `top` / `left` (automatically switches to top on narrow screens) |
| `input_type` | No | String | text | `text` / `multiline_text`(multiline, callback includes `\n`) / `password` |
| `rows` | No | Number | 5 | Default number of rows when multiline |
| `auto_resize` | No | Boolean | false | Auto-adapt height when multiline (PC only) |
| `max_rows` | No | Number | / | Maximum number of rows when `auto_resize` |
| `max_length` | No | Number | 1000 | Maximum number of characters, [1,1000] |
| `show_icon` | No | Boolean | true | Whether to show the prefix icon when password |
| `width` | No | String | default | `default` / `fill` / `[100,∞)px` |
| `disabled` | No | Boolean | false | Whether disabled (configure with `disabled_tips` plain_text) |
| `behaviors` | No | Array | / | `[{type:"callback", value:{...}}]` |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` |
| `margin` | No | String | 0 | Outer margin [-99,99]px |

<a id="嵌套--易错点"></a>
## Nesting / Common Pitfalls

- Can be nested within column_set / form / collapsible_panel / loop container / interactive_container.
- Within form it is **asynchronous submission**: all form data is only called back at once after the user finishes filling in and clicks the submit button.
- In the callback, `action.tag="input"` + `action.input_value` (user input value); for form submission the value is within `form_value`.
