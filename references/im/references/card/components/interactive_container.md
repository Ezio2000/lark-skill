<a id="交互容器-interactive_container"></a>
# Interactive Container `interactive_container`

A whole clickable area that uniformly defines the style and interactions (callback/open_url) of embedded content. Suitable for list items and clickable card blocks within a card. **Card 2.0**.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "interactive_container",
  "width": "fill",
  "has_border": true,
  "border_color": "grey",
  "corner_radius": "8px",
  "padding": "4px 12px 4px 12px",
  "behaviors": [{ "type": "callback", "value": { "key": "value" } }],
  "elements": [
    { "tag": "markdown", "content": "帮我生成一篇产品方案的框架" }
  ]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `interactive_container` |
| `elements` | Yes | Element[] | [] | Child nodes; supports all components except `form`/`table` |
| `behaviors` | Yes | Array | / | Interaction when the whole container is clicked: `callback` (callback) / `open_url` (redirect); can coexist in the same array |
| `width` | No | String | fill | `fill`/`auto`/`[16,999]px` |
| `height` | No | String | auto | `auto`/`[10,999]px` |
| `direction` | No | String | vertical | `vertical`/`horizontal` |
| `horizontal_align`/`vertical_align` | No | String | left/top | Alignment |
| `background_style` | No | String | default | `default`/`laser`/color enum/RGBA (see `../resource/colors.md`) |
| `has_border` | No | Boolean | false | Whether to show a 1px border |
| `border_color` | No | String | grey | Takes effect when `has_border` is true |
| `corner_radius` | No | String | 0px | `[0,∞]px` or `[0,100]%` |
| `padding`/`margin` | No | String | 4px,12px / 0px | Same spacing syntax |
| `disabled` / `disabled_tips` | No | Boolean/Object | false / empty | Disable the whole container and disable tooltip |
| `hover_tips` | No | Object | empty | PC hover tooltip |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` |

<a id="嵌套--易错点"></a>
## Nesting / Common Pitfalls

- Can nest all components except `form`/`table`, including nesting itself (a common pattern for list items).
- If the container contains interactive components (such as an inner `button`), the interaction of that child component is responded to first, and the container-level `behaviors` will not be triggered.
- Callback source: `card.action.trigger`; `action.tag` depends on the specific component triggered internally; when the container itself is clicked, `action.value` is the container's `behaviors.value`.
