<a id="多图混排-img_combination"></a>
# Image Combination `img_combination`

Multiple images arranged according to a preset layout. **Card 2.0**.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "img_combination",
  "combination_mode": "double",
  "img_list": [{ "img_key": "img_v3_a" }, { "img_key": "img_v3_b" }]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `img_combination` |
| `combination_mode` | Yes | String | / | `double`(≤2) / `triple`(≤3) / `bisect`(two columns, ≤6) / `trisect`(three columns, ≤9) |
| `img_list` | Yes | Array | / | Each item is `{ img_key }`; the order is the arrangement order |
| `combination_transparent` | No | Boolean | false | Whether the background is transparent |
| `corner_radius` | No | String | / | Corner radius, `[0,∞]px` or `[0,100]%` |
| `margin` | No | String | 0 | Outer margin [-99,99]px |
| `element_id` | No | String | / | Unique identifier, starts with a letter, ≤20 characters |

<a id="易错点"></a>
## Common Pitfalls

- If the number of images exceeds the mode limit: only the leading ones are displayed and the rest are discarded; if there are too few, blank space is left.
- Upload specifications: ≤10M, ≤1500×3000px, height:width ≤16:9.
