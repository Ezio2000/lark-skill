<a id="日期时间选择器-picker_datetime"></a>
# Date Time Picker `picker_datetime`

An interactive component that provides date + time options, with interaction capability by default. **Card 2.0**.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "picker_datetime",
  "placeholder": { "tag": "plain_text", "content": "请选择" },
  "initial_datetime": "2024-01-01 08:00"
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `picker_datetime` |
| `name` | No* | String | / | Unique identifier; **required within form and globally unique** |
| `required` | No | Boolean | false | Whether required (takes effect within form) |
| `initial_datetime` | No | String | / | Initial value, format `yyyy-MM-dd HH:mm`, overrides `placeholder` |
| `placeholder` | No | Object | / | Placeholder text, plain_text; required when `initial_datetime` is not set |
| `width` | No | String | default | `default`/`fill`/`[100,∞)px` |
| `disabled` | No | Boolean | false | Whether disabled (requires client version V7.4+) |
| `behaviors` | No | Array | / | `[{type:"callback", value:{...}}]` |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` |
| `margin` | No | String | 0 | [-99,99]px |

<a id="嵌套--易错点"></a>
## Nesting / Common Pitfalls

- Can be nested within column_set / form / collapsible_panel / loop container / interactive container; nesting within an interactive container is not yet supported in the builder tool.
- Remind users to pay attention to the time zone context; the server only returns the user's current time zone as a reference, which does not mean the user selected that time zone.
- Callback: `action.tag="picker_datetime"` + `action.option` (e.g. `"2025-06-10 19:19 +0800"`) + `action.timezone`; within form, read `form_value[name]`.
