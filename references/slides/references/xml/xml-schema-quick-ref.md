<a id="xml-schema-快速参考"></a>
# XML Schema Quick Reference

This document is a condensed summary of [slides_xml_schema_definition.xml](slides_xml_schema_definition.xml), merged with commonly used XML format conventions; if the two are inconsistent, the original XSD text prevails.

<a id="最重要的规则"></a>
## Most Important Rules

1. The protocol-standard form should use `<presentation xmlns="https://www.larkoffice.com/sml/2.0">`; the current server-side implementation may be compatible with input that does not include `xmlns`, but this is not a protocol guarantee
2. The only direct child elements of `<presentation>` are `<title>`, `<theme>`, `<slide>`
3. The only direct child elements of `<slide>` are `<style>`, `<data>`, `<note>`
4. Text on a page is usually expressed through `<content>`, rather than attaching `<title>`, `<body>` directly under `<slide>`

<a id="最小可用示例"></a>
## Minimal Working Example

```xml
<presentation xmlns="https://www.larkoffice.com/sml/2.0" width="960" height="540">
  <slide>
    <data>
      <shape type="text" topLeftX="80" topLeftY="80" width="800" height="120">
        <content autoFit="normal-auto-fit" wrap="true" textType="title">
          <p>标题</p>
        </content>
      </shape>
    </data>
  </slide>
</presentation>
```

<a id="presentation-根元素"></a>
## presentation Root Element

| Attribute | Required | Description |
|------|------|------|
| `width` | Yes | Presentation width, positive integer; for a standard 16:9 page, `960` is recommended |
| `height` | Yes | Presentation height, positive integer; for a standard 16:9 page, `540` is recommended |
| `id` | No | Presentation identifier |

**Child elements:** `<title>?`, `<theme>?`, `<slide>+`

`<slide>` must have at least 1 page and at most 100 pages.

<a id="theme-与文本类型"></a>
## theme and Text Types

`<theme>` currently contains two parts:

- `<background>`: presentation-level background fill
- `<textStyles>`: collection of theme text styles

Optional child elements under `<textStyles>` include `<title>`, `<headline>`, `<sub-headline>`, `<body>`, `<caption>`. These elements define theme default styles, not page structure.

Common attributes:

| Attribute | Description |
|------|------|
| `fontFamily` | Font |
| `fontSize` | Font size |
| `fontColor` | Font color |

In the XSD, `title`, `headline`, `sub-headline`, `body`, `caption` mainly appear in:

- `<theme><textStyles>...</textStyles></theme>`, as theme text styles
- `<content textType="...">`, as text types for content

The schema default values for `textStyles` are as follows:

| textType | Default font size |
|----------|----------|
| `title` | 54 |
| `headline` | 38 |
| `sub-headline` | 32 |
| `body` | 16 |
| `caption` | 12 |

The default font size is the fallback font size when `fontSize` is omitted, not a recommended value. The font size must be explicitly set via the `fontSize` attribute of `<content>`; do not rely on the default font size fallback of `textType`, as these fallback values are noticeably too large.

<a id="slide-元素"></a>
## slide Element

| Attribute | Required | Description |
|------|------|------|
| `id` | No | Slide identifier |

**Child elements:**

- `<style>?` - Page style; currently can contain `<fill>`
- `<data>?` - Page element container; can contain `shape`, `line`, `polyline`, `img`, `table`, `icon`, `embed`, `chart`, `undefined`
- `<note>?` - Speaker notes; can contain `<content>` inside

This means that `<title>`, `<headline>`, `<body>`, `<caption>` cannot be placed directly under `<slide>`.

<a id="content-内容模型"></a>
## content Content Model

`<content>` can appear in `shape`, `table/td`, `note`; common attributes include:

| Attribute | Description |
|------|------|
| `textType` | `title` / `headline` / `sub-headline` / `body` / `caption` |
| `verticalAlign` | Vertical alignment |
| `textAlign` | Text alignment |
| `lineSpacing` | Line spacing; schema default `multiple:1.5` |
| `fontSize` | Font size |
| `fontFamily` | Font |
| `color` | Font color |
| `bold` / `italic` / `underline` / `strikethrough` | Content-level styles |
| `wrap` | Whether to wrap text automatically |
| `autoFit` | Whether to indent automatically |

Notes:

- The font size must be explicitly set via the `fontSize` attribute of `<content>`; do not rely on the default font size fallback of `textType`, as these fallback values are noticeably too large.
- For `<content>` with large numbers, large font sizes, or a lot of text, the `wrap="true" autoFit="normal-auto-fit"` attribute must be set to enable automatic wrapping and indentation, to avoid text overflow.
- Text color must use the `color` attribute of `<content>`, not the `fontColor` attribute.
- Text line spacing must set `lineSpacing="multiple:xx"` or `lineSpacing="fixed:xx"` of `<content>`, not `lineSpacing="xx"`.

The only direct child elements of `<content>` are:

- `<p>`
- `<ul>`
- `<ol>`

<a id="p-段落与内联标签"></a>
### p Paragraph and Inline Tags

`<p>` is a paragraph element and can mix plain text and inline tags:

- `<br/>`
- `<strong>`
- `<em>`
- `<u>`
- `<span>`
- `<del>`
- `<a>`
- `<shadow>`
- `<outline>`
- `<formula>`

Formula syntax:

```xml
<p>公式：<formula><latex><![CDATA[ E = mc^2 ]]></latex></formula></p>
```

`<formula>` is an inline element; currently only one `<latex>` child element is supported. LaTeX content must be placed in `CDATA`, and do not write XML escapes inside `CDATA`; for macros, only use syntax within the range supported by the server, preferring basic operators, `\frac`, `\sqrt`, `matrix`.

Example:

```xml
<content autoFit="normal-auto-fit" textType="body" textAlign="left">
  <p>正文内容 <strong>加粗</strong> <em>斜体</em> <a href="https://example.com">链接</a></p>
  <ul>
    <li><p>列表项 1</p></li>
    <li><p>列表项 2</p></li>
  </ul>
</content>
```

<a id="data-常用元素"></a>
## Common data Elements

All page elements are placed in `<data>`.

### shape

`shape` can represent a regular shape or a text box. For text boxes, `type="text"` is recommended.

```xml
<shape type="text" topLeftX="80" topLeftY="80" width="800" height="120">
  <content textType="title">
    <p>主标题</p>
  </content>
</shape>
```

```xml
<shape type="rect" topLeftX="120" topLeftY="120" width="240" height="120">
  <fill>
    <fillColor color="rgb(100, 149, 237)"/>
  </fill>
  <border color="rgb(0, 0, 0)" width="2"/>
</shape>
```
`<shape type="rect">` is only a shape, not a container; `<icon>`, `<img>`, `<shape type="text">`, and other `<shape>` must be placed at the same level as it and stacked by coordinates.


| Attribute | Required | Description |
|------|------|------|
| `type` | Yes | Shape type; `text` indicates a text box |
| `topLeftX` | Yes | X coordinate of the top-left corner |
| `topLeftY` | Yes | Y coordinate of the top-left corner |
| `width` | Yes | Width |
| `height` | Yes | Height |
| `rotation` | No | Rotation angle |
| `flipX` / `flipY` | No | Flip |
| `alpha` | No | Opacity |

Optional child elements:

- `<fill>`
- `<border>`
- `<reflection>`
- `<shadow>`
- `<content>`

Common values for `type`: `text` (text box), `rect`, `round-rect` (rounded rectangle), `ellipse` (ellipse/circle), `triangle`, `diamond`, `parallelogram`, `trapezoid`, `custom` (used with the `path` attribute to write an SVG path string). For more shapes such as arrows, stars, callout bubbles, `chevron`, `flow-chart-*`, see the XSD `ShapeType` enumeration.

Other optional attributes:

- `presetHandlers`: control points, used for rounded corners, etc. For example, `<shape type="rect" presetHandlers="60">` = a rounded rectangle with a corner radius of 60px; separate multiple control points with commas.
- `path`: used only when `type="custom"`, an SVG path string.

### line

```xml
<line startX="120" startY="120" endX="420" endY="120">
  <border color="rgb(43, 47, 54)" width="2"/>
</line>
```

`line` uses `startX` / `startY` / `endX` / `endY`, not `x1` / `y1` / `x2` / `y2`.

### polyline

Polyline / curve connector, positioned using its bounding rectangle (`topLeftX` / `topLeftY` / `width` / `height`), not endpoint coordinates; `<border>` is required (invisible without a border). `type` defaults to `bent-connector2` (optional `bent-connector2-5` polyline / `curved-connector2-5` curve).

```xml
<polyline topLeftX="120" topLeftY="120" width="200" height="100">
  <border color="rgb(43, 47, 54)" width="2"/>
</polyline>
```

### img

```xml
<img src="file_token_或_@本地路径" topLeftX="80" topLeftY="120" width="320" height="180"/>
```

`img` uses `topLeftX` / `topLeftY`, not `x` / `y`.

`src` only supports: the `file_token` returned by `slides +media-upload`, or the `@<本地路径>` placeholder (`+create --slides` and `+add-slide` will be automatically uploaded and replaced). **Using http(s) external link URLs is prohibited**—the Feishu slides rendering side will not proxy external images, and external src usually does not display in the PPT. For local images, see [lark-slides-create.md](../cli/lark-slides-create.md#本地图片path-占位符) / [lark-slides-media-upload.md](../cli/lark-slides-media-upload.md).

Two approaches for local images:

- Creating a new PPT with images: write `src="@./pic.png"` directly in `+create --slides`; the CLI automatically uploads and replaces the token after creating a blank PPT and before adding slides
- Adding a new page with images to an existing PPT: write `src="@./pic.png"` directly in the XML of `+add-slide --slide`; the CLI uploads, replaces the token, and then submits the page

> **Note**: `width`/`height` are the **cropped** display dimensions. When the aspect ratio does not match the original image, it will be automatically cropped (this cannot be disabled via attributes); to avoid cropping, make `width:height` match the original image's aspect ratio.

### icon

```xml
<icon iconType="iconpark/Charts/chart-line.svg" topLeftX="80" topLeftY="120" width="32" height="32">
  <fill>
    <fillColor color="rgba(37, 99, 235, 1)"/>
  </fill>
</icon>
```

Icons must be filled with color and have sufficient contrast with the background.

Do not blindly guess iconType; you must first search IconPark, then write `<icon iconType="...">`. For search methods and more rules, see [iconpark.md](iconpark.md).


### table

The table structure is:

- The only direct child elements of `<table>` are `<colgroup>` and `<tr>`; `width` and `height` represent the table's target total width and total height, respectively.
- The only direct child element of `<colgroup>` is `<col width="...">`; width defines the column width, default 110.
- The only direct child element of `<tr height="...">` is `<td>`; height defines the row height, default 37.
- The only direct child elements of `<td>` are `<fill>` (background), `<content>` (text), and border configuration (generally not used); `<shape>`, `<img>`, `<icon>` cannot be nested.
- Merged cells: use `colspan` (column span, default 1) and `rowspan` (row span, default 1) on `<td>`; cells covered by a merge no longer write the corresponding `<td>`.

The default white background with white text for table headers has an extremely poor visual effect; background and text colors must be set, and `<fill>` must be added to each `<td>` in the first row (together with `bold` and a contrasting text color) to distinguish it from body rows.

Text in tables is center-aligned by default; `textAlign` can be set to adjust the alignment.

Table width and height settings:

- Explicitly set column widths and row heights are retained with priority; unset column widths and row heights will use the table's target total width and total height to allocate the remaining space
- **You must set `width` and `height` of `<table>` to fix the table size, and at the same time set `width` of `<col>` and `height` of `<tr>` for the columns or rows whose widths or heights need to be retained; the rest are allocated automatically.**

Row height reference for different font sizes:

| `fontSize` | Number of content lines | Compact `height` | Moderate `height` | Loose `height` |
|------|------|------|------|------|
| 10 | Single line | 16 | 20 | 24 |
| 12 | Single line | 20 | 24 | 28 |
| 10 | Double line | 32 | 36 | 42 |
| 12 | Double line | 36 | 42 | 48 |

Example:

```xml
<table topLeftX="80" topLeftY="140" width="520" height="52">
  <colgroup>
    <col width="160"/>
    <col width="120"/>
    <col />
  </colgroup>
  <tr height="28">
    <td>
      <fill><fillColor color="rgba(30,60,114,1)"/></fill>
      <content textType="body" fontSize="12" bold="true" color="rgba(255,255,255,1)" textAlign="center"><p>项目</p></content>
    </td>
    <td>
      <fill><fillColor color="rgba(30,60,114,1)"/></fill>
      <content textType="body" fontSize="12" bold="true" color="rgba(255,255,255,1)" textAlign="right"><p>营收</p></content>
    </td>
    <td>
      <fill><fillColor color="rgba(30,60,114,1)"/></fill>
      <content textType="body" fontSize="12" bold="true" color="rgba(255,255,255,1)" textAlign="left"><p>备注说明</p></content>
    </td>
  </tr>
  <tr>
    <td><content textType="body" fontSize="10" textAlign="center"><p>线上业务</p></content></td>
    <td><content textType="body" fontSize="10" textAlign="right"><p>195</p></content></td>
    <td><content textType="body" fontSize="10" textAlign="left"><p>同比增长 8%，主要来自新客</p></content></td>
  </tr>
</table>
```

### chart

Chart syntax is very complex; you must read [slides_chart_demo.xml](slides_chart_demo.xml) and directly copy the bar, horizontal bar, line, area, pie (donut), radar, and combination charts in it.

The direct child elements of `<chart>` must include `<chartPlotArea>` (plot area) and `<chartData>` (data); `<chartTitle>`, `<chartSubTitle>`, `<chartStyle>`, `<chartLegend>`, `<chartTooltip>` are optional; if you do not want to display the title, subtitle, legend, or tooltip, simply omit the corresponding element tags.

Common child elements of `<chartStyle>`:

- `<chartBackground>`: when `color` is omitted, the rendering side decides the default background; for fully transparent, explicitly write `color="rgba(0, 0, 0, 0)"`
- `<chartBorder>`: for no border, write `width="0"`, or simply do not write the `<chartBorder>` element

<a id="图表渐变---"></a>
#### Chart Gradients `<fillGradient>` / `<strokeGradient>`

Charts support gradient fills/strokes; `<fillGradient>` is used for area, bar, data point, and sector fills, and `<strokeGradient>` is used for lines, data point borders, and bar borders. Gradients can only be attached at the series level or single-element level, not at the `<chartPlot>` global level.

Attachable locations:

- Series level: `<chartBars>` / `<chartPoints>` support `<fillGradient>` and `<strokeGradient>`; `<chartLine>` only supports `<strokeGradient>`; `<chartArea>` / `<chartSectors>` only support `<fillGradient>`
- Single-element level: `<chartBar index="...">` / `<chartPoint index="...">` / `<chartSector index="...">` only support `<fillGradient>`
- Global level: `<chartLines>` / `<chartAreas>` / `<chartBars>` / `<chartPoints>` under `<chartPlot>` do not support gradients

Structural points: `type` is required and can be `linear` or `radial`; `linear` uses `x0` / `y0` / `x1` / `y1`, and `radial` uses `r0` / `r1`; `<stops>` must contain at least 2 `<stop>`, and the values of `offset` and `opacity` are both `[0, 1]`.

```xml
<chartSeries index="1">
  <chartBars>
    <fillGradient type="linear" x0="0" y0="0" x1="0" y1="1">
      <stops>
        <stop offset="0" color="rgb(28, 71, 120)"/>
        <stop offset="1" color="rgb(28, 71, 120)" opacity="0.3"/>
      </stops>
    </fillGradient>
  </chartBars>
</chartSeries>
```

Hiding the legend of `<chart>` can only be achieved by not writing or deleting `<chartLegend>`; `<chartLegend>` does not support `position="none"`.

For detailed usage, see [slides_xml_schema_definition.xml](slides_xml_schema_definition.xml).

### embed

Embedded content container: the outer `<embed>` carries the Slides placement and effect attributes (`topLeftX`/`topLeftY`/`width`/`height` are required, `rotation`/`flipX`/`flipY`/`alpha` are optional), and the inner layer carries external standard content. Currently the inner content is standard SVG; `<svg>` must use the `http://www.w3.org/2000/svg` namespace, and only describes the embedded content itself, not carrying Slides layout attributes.

```xml
<embed topLeftX="80" topLeftY="120" width="200" height="120">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 120">
    <circle cx="100" cy="60" r="40" fill="rgba(37, 99, 235, 1)"/>
  </svg>
</embed>
```

The direct child elements of `<embed>` are one `<svg>` (required), plus optional `<reflection>` (reflection) and `<shadow>` (shadow).

<a id="颜色与样式"></a>
## Colors and Styles

### fill

```xml
<fill>
  <fillColor color="rgb(255, 0, 0)"/>
</fill>
```

### border

```xml
<border color="rgb(43, 47, 54)" width="2" dashArray="solid"/>
```

<a id="颜色格式"></a>
### Color Format

```xml
<fillColor color="rgb(255, 0, 0)"/>
<fillColor color="rgba(255, 0, 0, 0.5)"/>
<fillColor color="linear-gradient(90deg, rgb(255,0,0) 0%, rgb(0,0,255) 100%)"/>
<fillColor color="radial-gradient(circle at 50% 50%, rgb(255,0,0) 0%, rgb(0,0,255) 100%)"/>
```

> **Note**: Gradient colors must use the `rgba()` format with percentage stops, for example `linear-gradient(135deg,rgba(30,60,114,1) 0%,rgba(59,130,246,1) 100%)`. Using `rgb()` or omitting stops will cause the server to fall back to white. This rule applies to both page backgrounds and shape fills.

<a id="页面背景"></a>
### Page Background

```xml
<!-- Solid background -->
<slide>
  <style>
    <fill>
      <fillColor color="rgb(245, 245, 245)"/>
    </fill>
  </style>
</slide>

<!-- Gradient background (must use rgba + percentage stops) -->
<slide>
  <style>
    <fill>
      <fillColor color="linear-gradient(135deg,rgba(30,60,114,1) 0%,rgba(59,130,246,1) 100%)"/>
    </fill>
  </style>
</slide>
```

<a id="备注示例"></a>
## Notes Example

```xml
<note>
  <content autoFit="normal-auto-fit" textType="body">
    <p>这是演讲者备注。</p>
  </content>
</note>
```

<a id="完整示例"></a>
## Complete Example

```xml
<presentation xmlns="https://www.larkoffice.com/sml/2.0" width="960" height="540">
  <title>季度报告</title>
  <theme>
    <textStyles>
      <title fontFamily="思源黑体" fontSize="54" fontColor="rgba(0, 0, 0, 1)"/>
      <body fontFamily="思源黑体" fontSize="18" fontColor="rgba(43, 47, 54, 1)"/>
    </textStyles>
  </theme>
  <slide>
    <style>
      <fill>
        <fillColor color="rgb(245, 245, 245)"/>
      </fill>
    </style>
    <data>
      <shape type="text" topLeftX="80" topLeftY="72" width="760" height="100">
        <content textType="title">
          <p>2024 年第一季度报告</p>
        </content>
      </shape>
      <shape type="text" topLeftX="80" topLeftY="200" width="520" height="180">
        <content textType="body">
          <p>核心指标</p>
          <ul>
            <li><p>用户增长：+25%</p></li>
            <li><p>收入增长：+30%</p></li>
            <li><p>市场份额：15%</p></li>
          </ul>
        </content>
      </shape>
      <shape type="rect" topLeftX="660" topLeftY="180" width="180" height="140">
        <fill>
          <fillColor color="rgba(100, 149, 237, 0.25)"/>
        </fill>
        <border color="rgb(100, 149, 237)" width="2"/>
      </shape>
    </data>
    <note>
      <content textType="body">
        <p>讲到增长率时补充样本范围。</p>
      </content>
    </note>
  </slide>
</presentation>
```

<a id="最佳实践"></a>
## Best Practices

1. Always include the namespace `xmlns="https://www.larkoffice.com/sml/2.0"`
2. Use `shape type="text"` + `content` to express page text
3. Use attribute names defined in the schema, such as `topLeftX` / `topLeftY`, `startX` / `startY`
4. Prefer the `rgb` / `rgba` color format; gradients must use `rgba()` with percentage stops
5. Escape special characters according to XML rules
6. For standard 16:9 pages, it is recommended to use `width="960"` and `height="540"`

<a id="详细参考"></a>
## Detailed Reference

- [slides_xml_schema_definition.xml](slides_xml_schema_definition.xml)
- [slides_chart_demo.xml](slides_chart_demo.xml)

<a id="schema-版本信息"></a>
## Schema Version Information

- **Version**: 2.0.0
- **Namespace**: https://www.larkoffice.com/sml/2.0
- **Release Date**: 2025-11-03
