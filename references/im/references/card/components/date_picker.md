<a id="日期选择器-date_picker"></a>
# Date Picker `date_picker`

An interactive component that provides date options and has interaction capability by default (it will call back even without an explicit `behaviors`). **Card 2.0**.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "date_picker",
  "placeholder": { "tag": "plain_text", "content": "请选择" },
  "initial_date": "2024-01-01"
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `date_picker` |
| `name` | No* | String | / | Unique identifier; **required within a form and globally unique** |
| `required` | No | Boolean | false | Whether it is required (takes effect within a form) |
| `initial_date` | No | String | / | Initial value, format `yyyy-MM-dd`, overrides `placeholder` |
| `placeholder` | No | Object | / | Placeholder text, plain_text; required when `initial_date` is not set |
| `width` | No | String | default | `default`/`fill`/`[100,∞)px` |
| `disabled` | No | Boolean | false | Whether disabled (requires client version V7.4+) |
| `behaviors` | No | Array | / | `[{type:"callback", value:{...}}]` |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` |
| `margin` | No | String | 0 | [-99,99]px |

<a id="嵌套--易错点"></a>
## Nesting / Common Pitfalls

- Can be nested within column_set / form / collapsible_panel / loop container / interactive container; nesting within an interactive container is not yet supported in the builder tool.
- Remind users to pay attention to the time zone context (e.g., when booking an overseas hotel, use the hotel's local time zone); the server only returns the user's current time zone as a reference, which does not mean the user selected that time zone.
- Callback: `action.tag="date_picker"` + `action.option` (date string, e.g., `"2025-06-10 +0800"`) + `action.timezone`; within a form, read `form_value[name]`.
