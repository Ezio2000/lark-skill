<a id="图表-chart"></a>
# Chart `chart`

VChart-based visualization charts (line/bar/pie/word cloud, etc.). **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "chart",
  "chart_spec": {
    "type": "line",
    "title": { "text": "趋势" },
    "data": { "values": [
      { "time": "周一", "value": 8 },
      { "time": "周二", "value": 14 }
    ] },
    "xField": "time",
    "yField": "value"
  }
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `chart` |
| `chart_spec` | Yes | Object | / | VChart chart definition, see below |
| `aspect_ratio` | No | String | 16:9(PC)/1:1(mobile) | `1:1` / `2:1` / `4:3` / `16:9` |
| `color_theme` | No | String | brand | `brand` / `rainbow` / `complementary` / `converse` / `primary`; if a style is declared in chart_spec, this item is invalid |
| `height` | No | String | auto | `auto`(by aspect ratio) or `[1,999]px` (if a fixed height is set, aspect_ratio becomes invalid) |
| `preview` | No | Boolean | true | Whether it can be viewed in an independent window/full screen |
| `margin` | No | String | 0 | Outer margin [-99,99]px |
| `element_id` | No | String | / | Unique identifier, starts with a letter, ≤20 characters |

<a id="chart_spec-常用类型"></a>
## Common chart_spec types

`chart_spec` is a standard VChart spec. Core fields: `type`, `data.values` (data array), `xField`/`yField` (axis fields), `seriesField` (grouping), `title.text`, `legends`.

| Chart | type | Key fields |
|---|---|---|
| Line | `line` | `xField`, `yField` |
| Area | `area` | `xField`, `yField` |
| Column | `bar` | `xField`, `yField`, add `seriesField` for grouping |
| Bar (horizontal) | `bar` | `direction:"horizontal"`, `xField`=value, `yField`=category |
| Pie/Donut | `pie` | `valueField`, `categoryField`, add `innerRadius` for donut charts |
| Scatter | `scatter` | `xField`, `yField` |
| Word cloud | `wordCloud` | `nameField`, `valueField` |

For complete properties, refer to the [VChart official documentation](https://www.visactor.io/vchart/option/barChart).

<a id="易错点"></a>
## Common pitfalls

- JavaScript syntax is not supported; `chart_spec` must be pure JSON.
- A single card is recommended to have ≤5 charts.
- Some VChart properties are not supported on mobile (texture, conical gradient, grid word cloud layout, etc.); using them will cause loading failure on mobile.
- The platform appends media query responsiveness to chart_spec by default; to control it yourself, set `"media": []`.
