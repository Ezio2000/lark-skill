<a id="多图选择-select_img"></a>
# Image Picker `select_img`

An interactive component that uses images as options, supporting single/multiple selection (such as product images, template images, AI-generated images). Only handwritten JSON is supported; the builder tool does not support it. **Card 2.0**.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "select_img",
  "name": "select_img_1",
  "layout": "bisect",
  "aspect_ratio": "16:9",
  "options": [
    { "img_key": "img_v2_xxx", "value": "picture1" },
    { "img_key": "img_v2_yyy", "value": "picture2" }
  ]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `select_img` |
| `options` | Yes | Array | / | Options, each item `{img_key, value, disabled?, disabled_tips?, hover_tips?}` |
| `multi_select` | No | Boolean | false | Multiple selection only supports asynchronous submission, **must** be embedded in a form, otherwise an error is reported |
| `layout` | No | String | bisect | Image layout: `stretch`(fill)/`bisect`(bisect)/`trisect`(trisect) |
| `aspect_ratio` | No | String | 16:9 | `1:1`/`16:9`/`4:3` |
| `name` | No* | String | / | Unique identifier; **required within a form and globally unique** |
| `required` | No | Boolean | false | Whether it is required (takes effect within a form) |
| `can_preview` | No | Boolean | true | Whether clicking the image enlarges it in a popup (only takes effect within a form) |
| `disabled` | No | Boolean | false | Whether to disable the entire component |
| `value` | No | String/Object | / | Custom callback parameters |
| `behaviors` | Yes | Array | / | `[{type:"callback", value:{...}}]` |
| `confirm` | No | Object | / | Secondary confirmation popup `{title, text}` |

<a id="嵌套--易错点"></a>
## Nesting / Common Pitfalls

- Can be nested in the root node / column_set / form / interactive container (the builder tool does not currently support nesting interactive containers).
- **Not within a form**: only single selection is supported; clicking immediately submits and triggers the callback; multiple selection/asynchronous submission is not supported.
- **Within a form**: supports single/multiple selection + asynchronous submission (submitted together with the form).
- Callback (non-form): `action.tag="select_img"` + `action.options` (still this field for single selection); within a form, read `form_value[name]`.
