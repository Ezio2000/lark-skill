<a id="普通文本-div"></a>
# Plain Text `div`

A styled text block that supports prefix icons and label-value field pairs. **Card 2.0**. For rich text, use the `markdown` component.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "div",
  "text": { "tag": "plain_text", "content": "示例文本" }
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `div` |
| `text` | No | Object | / | Text object, see below |
| `text.tag` | Yes | String | plain_text | `plain_text` or `lark_md` (partial Markdown, see `markdown.md` for syntax) |
| `text.content` | Yes | String | / | Text content |
| `text.text_size` | No | String | normal | `heading-0`~`heading-4` / `normal`(14px) / `notation`(12px), etc.; you can customize different font sizes for pc/mobile in `config.style.text_size` |
| `text.text_color` | No | String | default | Color enum (see `../resource/colors.md`), only takes effect for `plain_text` |
| `text.text_align` | No | String | left | `left` / `center` / `right` |
| `text.lines` | No | Int | / | Maximum number of displayed lines; content beyond `...` is truncated with an ellipsis |
| `icon` | No | Object | / | Prefix icon, see below |
| `icon.tag` | No | String | / | `standard_icon` (use `token`+`color`, for tokens see `../resource/icons.md`) or `custom_icon` (use `img_key`) |
| `width` | No | String | fill | `fill` / `auto` / `[16,999]px` |
| `margin` | No | String | 0 | Margin [-99,99]px |
| `element_id` | No | String | / | Unique identifier, starts with a letter, ≤20 characters; during streaming updates, `text.element_id` specifies the text |

> `fields` field (multi-column label-value): an array, each item is `{ is_short, text:{tag,content} }`, and `is_short:true` can be placed side by side.

<a id="易错点"></a>
## Common Pitfalls

- `text_color` only takes effect when `text.tag` is `plain_text`; for `lark_md`, use inline `<font color=red>` for coloring.
