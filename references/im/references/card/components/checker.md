<a id="勾选器-checker"></a>
# Checker `checker`

An interactive component for task-checking scenarios, supporting configuration of callback responses. Only handwritten JSON is supported; the builder tool does not support constructing it. **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "checker",
  "name": "check_1",
  "checked": false,
  "text": { "tag": "plain_text", "content": "完成新品上市计划报告" },
  "behaviors": [{ "type": "callback", "value": { "key": "todo1" } }]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `checker` |
| `name` | No* | String | / | Unique identifier; **required within a form and globally unique** |
| `checked` | No | Boolean | false | Initial checked state |
| `text` | No | Object | / | `{tag:"plain_text"\|"lark_md", content, text_size?, text_color?, text_align?}` (for text_color see `../resource/colors.md`) |
| `overall_checkable` | No | Boolean | true | Whether the whole component has a shadow effect on hover |
| `button_area` | No | Object | / | `{pc_display_rule:"always"|"on_hover", buttons:[<=3 个 button]}` |
| `checked_style` | No | Object | / | `{show_strikethrough, opacity}`, the content style after checking |
| `disabled` / `disabled_tips` | No | Boolean/Object | false / empty | Disabled and disabled tooltip |
| `hover_tips` | No | Object | Empty | Hover tooltip; when configured together with `disabled_tips`, the latter takes effect |
| `behaviors` | No | Array | / | `[{type:"callback", value:{...}}]`; **when not configured, only the local check takes effect and no callback is triggered** |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` |
| `padding`/`margin` | No | String | 0 | [-99,99]px |

<a id="嵌套--易错点"></a>
## Nesting / common pitfalls

- Can be nested within form / interactive container / column_set / collapsible_panel.
- When `behaviors` is not configured, checking only takes effect locally on the frontend and does not trigger a server-side callback—if the business side needs to be aware of it, it must be explicitly configured.
- Callback: `action.tag="checker"` + `action.checked` (boolean value); within a form, read `form_value[name]`.
