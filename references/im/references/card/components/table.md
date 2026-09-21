<a id="表格-table"></a>
# Table `table`

Multi-column data table, supporting column types such as text/number/option/person/date. **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "table",
  "columns": [
    { "name": "city", "display_name": "城市", "data_type": "text" },
    { "name": "qty", "display_name": "数量", "data_type": "number" }
  ],
  "rows": [
    { "city": "北京", "qty": 12 },
    { "city": "上海", "qty": 8 }
  ]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `table` |
| `columns` | Yes | column[] | / | Column definitions, ≤50 columns, see below |
| `rows` | Yes | Object[] | / | Row data, populated according to `列name: 值` |
| `page_size` | No | Number | 5 | Rows per page, [1,10] |
| `row_height` | No | String | low | `low`/`middle`/`high`/`auto`/`[32,124]px` |
| `row_max_height` | No | String | 124px | Maximum row height when `row_height:auto` [32,999]px |
| `freeze_first_column` | No | Boolean | false | Freeze first column |
| `header_style` | No | Object | / | Header style: `{text_align, text_size, background_style:grey\|none, text_color, bold, lines}` |
| `margin` | No | String | 0 | Outer margin [-99,99]px |

**column fields**: `name` (required, key name) / `display_name` (header name) / `data_type` (see below) / `width` (`auto`/`[80,600]px`/`%`) / `horizontal_align` / `vertical_align`; `number` columns can add `format:{precision, symbol, separator}`; `date` columns can add `date_format` (e.g. `YYYY/MM/DD`).

**data_type and row value structure**:

| data_type | Row value |
|---|---|
| `text` | `"飞书"` |
| `lark_md` | `"[链接](https://x)"` |
| `number` | `168.23` |
| `options` | `[{text:"S2", color:"blue"}]` (for color enums see `../resource/colors.md`, text should not be too long) |
| `persons` | `"ou_xxx"` or `["ou_a","ou_b"]` |
| `date` | `1699341315000` (millisecond timestamp, displayed in local time zone) |
| `markdown` | `"![img](img_key)"` full Markdown |

<a id="嵌套--易错点"></a>
## Nesting / common pitfalls

- **table can only be placed at the card root `body.elements`**: it cannot be nested inside any container, and it cannot itself contain other components.
- A single card can have at most 5 tables (5 per language for multilingual).
- The keys of `rows` must correspond to `columns[].name`.
