<a id="表单容器-form"></a>
# Form container `form`

Enter multiple form items in bulk and submit them all at once: the user fills in multiple form items on the frontend, and after clicking the submit button, all values are packaged and sent back to the server in a single callback. **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "form",
  "name": "form_1",
  "elements": [
    { "tag": "input", "name": "reason", "required": true },
    {
      "tag": "button",
      "text": { "tag": "plain_text", "content": "提交" },
      "type": "primary",
      "form_action_type": "submit",
      "name": "Button_submit"
    }
  ]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `form` |
| `name` | Yes | String | / | Unique identifier of the form container, globally unique within the card, used to identify which submission the data belongs to |
| `elements` | Yes | Element[] | [] | Child nodes, supports all components except `table` and `form` |
| `direction` | No | String | vertical | `vertical` / `horizontal` |
| `horizontal_spacing`/`vertical_spacing` | No | String | 8px/12px | Spacing enum `small`(4)/`medium`(8)/`large`(12)/`extra_large`(16) or `[0,99]px` |
| `horizontal_align` | No | String | left | `left`/`center`/`right` |
| `vertical_align` | No | String | top | `top`/`center`/`bottom` |
| `padding`/`margin` | No | String | 0 | [-99,99]px, supports single-value/two-value/four-value notation |
| `element_id` | No | String | / | Unique identifier, starts with a letter, ≤20 characters |

<a id="子组件内嵌字段交互组件嵌在-form-内时生效"></a>
### Child component embedded fields (effective when an interactive component is embedded in a form)

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique identifier of the component within the form, globally unique within the card, otherwise submission fails |
| `required` | No | Whether it is required; if true and left unfilled, clicking submit is intercepted locally and no callback is initiated |
| `form_action_type` | Yes (button) | `submit` (submit) / `reset` (reset to initial values); buttons within a form do **not** use `behaviors` |

<a id="嵌套--易错点"></a>
## Nesting / common pitfalls

- `form` does not support nesting `table` and `form`; and `form` itself can only be placed under the card root node and cannot be nested by other components.
- The `name` of all interactive components within a form must be filled in and globally unique, otherwise submission fails.
- A form must contain a button with `form_action_type: submit`.
- Callback source: `card.action.trigger` with `action.tag="button"` + `action.form_value` (mapping each field value by the component's `name`).
