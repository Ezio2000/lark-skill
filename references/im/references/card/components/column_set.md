<a id="分栏-column_set--column"></a>
# Columns `column_set` + `column`

Horizontal multi-column layout container. `column_set` holds several `column`, and each `column` contains further components. **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "column_set",
  "flex_mode": "none",
  "columns": [
    { "tag": "column", "width": "weighted", "weight": 1,
      "elements": [{ "tag": "markdown", "content": "左列" }] },
    { "tag": "column", "width": "weighted", "weight": 1,
      "elements": [{ "tag": "markdown", "content": "右列" }] }
  ]
}
```

<a id="column_set-字段"></a>
## column_set fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `column_set` |
| `columns` | Yes | column[] | / | Column array; child nodes can only be `column` |
| `flex_mode` | No | String | none | Narrow-screen adaptation: `none` (compress proportionally) / `stretch` (stack vertically) / `flow` (wrap automatically) / `bisect` (split into two equal parts) / `trisect` (split into three equal parts) |
| `horizontal_spacing` | No | String | 8px | `small`(4)/`medium`(8)/`large`(12)/`extra_large`(16) or `[0,99]px` |
| `horizontal_align` | No | String | left | `left` / `center` / `right` |
| `background_style` | No | String | default | `default` or a color enum/RGBA (see `../resource/colors.md`); when nested, the upper layer overrides the lower layer |
| `action` | No | Object | / | Click the whole block to jump to `{ multi_url:{url,pc_url,ios_url,android_url} }` |
| `margin` | No | String | 0 | Outer margin [-99,99]px |

<a id="column-字段"></a>
## column fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `column` |
| `elements` | No | Element[] | / | Components inside the column; **cannot contain `form` or `table`**, but can contain `column_set` |
| `width` | No | String | auto | Takes effect only for `flex_mode:none`: `auto` / `weighted` (with weight) / `[16,600]px` |
| `weight` | No | Number | 1 | Width proportion when `width:weighted`, an integer from 1 to 5 |
| `vertical_align` | No | String | top | `top` / `center` / `bottom` |
| `direction` | No | String | vertical | `vertical` / `horizontal` |
| `horizontal_spacing`/`vertical_spacing` | No | String | 8px | Same spacing enum as above or `[0,99]px` |
| `padding` | No | String | 0 | Inner padding [0,99]px |
| `margin` | No | String | 0 | Outer margin [-99,99]px |
| `background_style` | No | String | default | Same as above |
| `action` | No | Object | / | Click the column to jump, same as column_set.action |

<a id="嵌套--易错点"></a>
## Nesting / common pitfalls

- **The direct child nodes of column_set can only be `column`**; it cannot be `column_set → column_set`. For second-level columns, use `column_set → column → column_set`.
- A column can contain all components except `form` / `table`.
- Nesting is limited to 5 levels; going deeper compresses the display space.
