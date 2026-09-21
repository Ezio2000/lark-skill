<a id="折叠按钮组-overflow"></a>
# Overflow button group `overflow`

Collapse multiple option buttons, click to expand. Suitable for scenarios with many actions. **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "overflow",
  "options": [
    { "text": { "tag": "plain_text", "content": "选项A" }, "value": "a" },
    { "text": { "tag": "plain_text", "content": "选项B" }, "value": "b" }
  ]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `overflow` |
| `options` | Yes | Array | / | Option buttons, see below |
| `options[].text` | No | Object | / | `{tag:"plain_text", content}`, ≤100 characters |
| `options[].value` | No | String | / | Value returned on click, used to distinguish which option was clicked (callback `action.option`) |
| `options[].multi_url` | No | Object | / | Jump link `{url, pc_url, ios_url, android_url}` |
| `behaviors` | No | Array | / | Additional return: `[{type:"callback", value:{...}}]` |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` (both plain_text) |
| `width` | No | String | default | `default` / `fill` / `[100,∞)px` |
| `margin` | No | String | 0 | Outer margin [-99,99]px |
| `element_id` | No | String | / | Unique identifier, starts with a letter, ≤20 characters |

<a id="嵌套--易错点"></a>
## Nesting / common pitfalls

- Can be nested inside form / collapsible_panel / loop container / interactive_container / column_set.
- When there are multiple buttons, be sure to give each one a `options[].value`, otherwise the callback cannot distinguish which one was clicked.
- Clicking triggers `card.action.trigger`, returning `action.tag = "overflow"` + `action.option`.
