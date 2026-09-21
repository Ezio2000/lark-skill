<a id="时间选择器-picker_time"></a>
# Time Picker `picker_time`

An interactive component that provides time options and has interaction capability by default. **Card 2.0**.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "picker_time",
  "placeholder": { "tag": "plain_text", "content": "请选择" },
  "initial_time": "09:00"
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `picker_time` |
| `name` | No* | String | / | Unique identifier; **required within a form and globally unique** |
| `required` | No | Boolean | false | Whether it is required (takes effect within a form) |
| `initial_time` | No | String | / | Initial value, format `HH:mm`, overrides `placeholder` |
| `placeholder` | No | Object | / | Placeholder text, plain_text; required when `initial_time` is not set |
| `width` | No | String | default | `default`/`fill`/`[100,∞)px` |
| `disabled` | No | Boolean | false | Whether disabled (requires client version V7.4+) |
| `behaviors` | No | Array | / | `[{type:"callback", value:{...}}]` |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` |
| `margin` | No | String | 0 | [-99,99]px |

<a id="嵌套--易错点"></a>
## Nesting / Common Pitfalls

- Can be nested within column_set / form / collapsible_panel / loop container / interactive container; nesting within an interactive container is not yet supported in the builder tool.
- Remind users to pay attention to the time zone context; the server only returns the user's current time zone as a reference, which does not mean the user selected that time zone.
- Callback: `action.tag="picker_time"` + `action.option` (time string, such as `"05:05 +0800"`) + `action.timezone`; within a form, read `form_value[name]`.
