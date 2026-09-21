<a id="图片-img"></a>
# Image `img`

Displays an image. You must first call the upload image API to get `img_key`. **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "img",
  "img_key": "img_v3_xxx",
  "alt": { "tag": "plain_text", "content": "" }
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `img` |
| `img_key` | Yes | String | / | Image key, obtained from the upload image API |
| `alt` | Yes | Object | / | hover description, `{tag:"plain_text", content:""}`, do not pass an empty value |
| `title` | No | Object | / | Image title, plain_text object |
| `scale_type` | No | String | crop_center | `crop_center` / `crop_top` / `fit_horizontal` (no cropping) |
| `size` | No | String | / | Only takes effect for `crop_*`: `stretch`/`large`(160)/`medium`(80)/`small`(40)/`tiny`(16), or `"100px 100px"` |
| `corner_radius` | No | String | / | Corner radius, `[0,∞]px` or `[0,100]%` |
| `transparent` | No | Boolean | false | Whether the background is transparent |
| `preview` | No | Boolean | true | Whether clicking enlarges the image; set to false when paired with `card_link` for navigation |
| `margin` | No | String | 0 | Outer margin [-99,99]px |
| `element_id` | No | String | / | Unique identifier, starts with a letter, ≤20 characters |

<a id="易错点"></a>
## Common pitfalls

- Full-width effect: 2.0 no longer supports `size: stretch_without_padding`; use a negative `margin` instead (such as `"4px -12px"`).
- Upload specifications: ≤10M, dimensions ≤1500×3000px, height:width ≤16:9.
