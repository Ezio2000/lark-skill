<a id="折叠面板-collapsible_panel"></a>
# Collapsible Panel `collapsible_panel`

Collapse secondary content (notes, long text); click the title to expand/collapse. **Card 2.0**.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "collapsible_panel",
  "expanded": false,
  "header": { "title": { "tag": "plain_text", "content": "面板标题" } },
  "elements": [{ "tag": "markdown", "content": "折叠的内容" }]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `collapsible_panel` |
| `header` | Yes | Object | / | Title area, see below |
| `elements` | No | Array | / | Components inside the panel; **cannot contain `form`** |
| `expanded` | No | Boolean | false | Whether expanded by default |
| `background_color` | No | String | Transparent | Panel background, color enum (see `../resource/colors.md`) |
| `border` | No | Object | / | `{ color, corner_radius }` |
| `direction` | No | String | vertical | `vertical` / `horizontal` |
| `vertical_spacing`/`horizontal_spacing` | No | String | 8px | Spacing enum or [0,99]px |
| `padding` | No | String | 0 | Padding [0,99]px |
| `margin` | No | String | 0 | Margin [-99,99]px |

**header fields**:

| Field | Required | Description |
|---|---|---|
| `title` | No | `{tag:"plain_text"\|"markdown", content}` |
| `background_color` | No | Title area background, color enum |
| `width` | No | `fill` / `auto` / `auto_when_fold` (auto-fit when collapsed) |
| `vertical_align` | No | `top`/`center`/`bottom` |
| `icon` | No | Icon `{tag, token, color, size}` (same as `div.icon`, plus `size`) |
| `icon_position` | No | `left` / `right` / `follow_text` |
| `icon_expanded_angle` | No | Icon rotation angle when expanded: `-180`/`-90`/`90`/`180` |

<a id="嵌套--易错点"></a>
## Nesting / Common Pitfalls

- `form` is not supported inside; containers can be nested up to 5 levels.
- Only JSON writing is supported; the builder tool does not support it.
