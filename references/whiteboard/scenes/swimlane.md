<a id="泳道图swimlane"></a>
# Swimlane Diagram (Swimlane)

Applicable to: end-to-end processes across roles/systems (user/gateway/service/storage/callback), multi-swimlane collaborative processes, system interaction link diagrams.

Supports two orientations:
- **Horizontal swimlanes**: lanes are horizontal bands (arranged top to bottom), process advances from left to right
- **Vertical swimlanes**: lanes are vertical columns (arranged left to right), process advances from top to bottom

<a id="content-约束"></a>
## Content Constraints

- Number of lanes: 3-7 recommended; more than 7 significantly reduces readability; if more lanes are necessary, prioritize merging similar ones or splitting into two diagrams
- Number of stages: 4-8 recommended; if more than 8, prioritize merging adjacent stages or switching to "representative stages"
- Each stage can hold at most 1 "main step card" per lane; if multiple steps are needed in the same stage, stack them vertically within the same cell (2-3 is the upper limit)
- Node text should be 1-2 lines; use `\n` for manual line breaks with long text, to avoid a single overly long line making the card too wide
- Only draw necessary connections: the swimlane structure already expresses "which role/system it belongs to + order of occurrence"; connections are only used to express cross-lane interactions, key causal relationships, or asynchronous event flows

<a id="layout-选型"></a>
## Layout Selection

| Mode | Applicable Conditions | Characteristics |
|------|---------|------|
| **Horizontal swimlanes** | Default recommendation; process naturally advances left→right | lanes=rows, stages=columns; same stage across lanes strictly x-aligned |
| **Vertical swimlanes** | User explicitly requests portrait orientation, or canvas is better suited for vertical scrolling | lanes=columns, stages=rows; same stage across lanes strictly y-aligned |

<a id="layout-规则"></a>
## Layout Rules

<a id="通用规则两种方向都适用"></a>
### General Rules (applicable to both orientations)

1. **Grid alignment is the first priority**: the same stage across lanes must be strictly aligned (horizontal alignment x; vertical alignment y). Alignment is achieved through "shared stage ruler / stage slots", not by visual estimation, nor by arbitrarily hand-writing coordinates per node
2. **Only generate real nodes**: to ensure strict alignment of stages across lanes, all stages uniformly retain transparent **stage cells**; card nodes are only generated within cells of real stages, and mapped to corresponding slots by stage index
3. **Lane background color**: to enhance the sense of hierarchy while keeping the interface clean, **it is strongly recommended that all lane containers uniformly use an extremely light gray background** (such as `fillColor: "#F8F9FA"` or `"#FCFCFC"`). Borders use light gray thin dashed lines (`borderDash: "dashed"`, `borderWidth: 1`, `borderColor: "#DEE0E3"`) to clearly define boundaries.
4. **Step cards**: use `rect`. To establish a clear visual hierarchy, cards **must be filled with a light background color** (refer to the light palette in `elements/style.md`, such as an extremely light theme color), borders use the corresponding theme primary color (`borderWidth: 1-2`), and text uses a dark color (such as `#1F2329`) to ensure readability. Uniform corner radius; width and height prioritize readability, avoid being too narrow which causes excessive line wrapping
5. **Spacing**: whenever connector lines exist, the main-axis spacing between cards must satisfy `gap >= 40`

<a id="子节点对齐"></a>
### Child Node Alignment

- **The same stage must be strictly aligned**: all lanes reuse the same set of stage slots; alignment by the card's own width or visual estimation is not allowed
- **Consistent card width**: step cards within the same lane should maintain a uniform width; it is recommended to use a uniform fixed width, or strictly reuse the same slot width
- **Uniformly use stack containers**: stages with content uniformly use the `layout: "vertical"` stack frame (vertically stacking 1-3 cards); empty stages do not generate stacks/cards, but retain transparent cells to ensure alignment
- **Vertically centered but does not affect alignment**: stage cells default to `alignItems: "stretch"`; `justifyContent: "center"` can be used to center cards within the cell, to ensure strict alignment of left and right boundaries
- **Do not rely on background color to distinguish rows/columns**: the stage grid does not need a background color by default; if a "slight" row/column boundary hint is needed, prioritize adding a 1px thin border to the stage cell (`fillColor: "transparent"` still remains visually transparent)

<a id="flex-栅格模式默认"></a>
### Flex Grid Mode (Default)

- lane body uses Flex layout: horizontal swimlanes use `layout: "horizontal"`, vertical swimlanes use `layout: "vertical"`
- Generate one **stage cell** (placeholder cell) for each stage; cells of empty stages are transparent but retained; within the cell, use a `layout: "vertical"` stack to hold 1-3 cards
- Unified parameters: `slotWidth: 180-220` (horizontal swimlane cell width), `slotHeight: 64-104` (vertical swimlane cell height recommended tier), `gap: 40-56` (must be ≥40 when connections exist), `stackGap: 8`, `lanePadding: 16`
- Alignment rule: all lanes reuse the same set of `slotWidth/slotHeight/gap`; the same stage uses the same cell index across lanes to ensure strict alignment
- Size semantics: lane body `width/height` uses `"fit-content"` (Yoga adaptive); cards `height: "fit-content"`; do not write child node `x/y` inside Flex containers
- Content density: card text 1-2 lines; stacking limit per stage 2-3; if exceeding the limit, prioritize splitting to adjacent stages or shortening text

<a id="跨泳道间距lanesgap"></a>
### Cross-Lane Spacing (lanesGap)

- The root container holds all lanes: horizontal swimlanes use `layout: "vertical"`, vertical swimlanes use `layout: "horizontal"`
- Reduce the cross-lane main-axis spacing `lanesGap` (recommended `16-24`), to keep the overall diagram compact. Avoid setting `lanesGap` to `0` which causes borders to overlap and become thicker, and also avoid excessive spacing which causes visual dispersion.
- Each lane serves as a child frame of the root container, internally using the aforementioned Flex grid stage cell layout
- `lanesGap` and `lanePadding/stackGap` are independent; changes in lane content should not affect cross-lane spacing
- 4px baseline alignment: `lanesGap`, `lanePadding`, cell dimensions are recommended to align to multiples of 4

<a id="水平泳道lanes行stages列"></a>
### Horizontal Swimlanes (lanes=rows, stages=columns)

- Root container: `layout: "vertical"`, `gap: lanesGap` fixed; `alignItems: "stretch"`, title at the very top
- Each lane: a visible frame (grouping container), internally split into two parts using `layout: "horizontal"`:
  - Left lane label: fixed-width text (such as 100-140), vertically centered; left-aligned (`textAlign: "left"`); title needs to be more prominent than step cards, prioritize achieving this through `fontSize: 18-20` + `fontWeight: "bold"` + `textColor` consistent with the lane border
  - Right lane body: `layout: "horizontal"`, containing the complete stage **stage cell** array; cell width fixed at `slotWidth`, spacing between adjacent cells `gap` uniform; empty stage cells transparent but retained
- Step cards: recommended uniform card width (such as 160-220), and reuse the same set of `slotWidth / gap` across all lanes, to ensure strict x-alignment of stages across lanes

<a id="垂直泳道lanes列stages行"></a>
### Vertical Swimlanes (lanes=columns, stages=rows)

- Root container: `layout: "horizontal"`, `gap: lanesGap` fixed; `alignItems: "stretch"`, title at the very top
- Each lane: a visible frame (grouping container), internally `layout: "vertical"`:
  - Top lane label: must be placed in a separate `lane label frame`; the label frame uses `width: "fill-container"`, `alignItems: "center"`, `justifyContent: "center"`, and uses `paddingTop` to leave a gap from the top of the lane (recommended `12-16`, taking values on the 4px baseline, such as `padding: [12, 8, 8, 8]`); the internal text uses `width: "fill-container"` + `textAlign: "center"`, ensuring the title is **horizontally centered** at the top of the entire lane
  - lane body: `layout: "vertical"`, containing the complete stage **stage cell** array; cell height fixed at `slotHeight`, spacing between adjacent cells `gap` uniform; empty stage cells transparent but retained
  - Content center alignment: stage cells recommended `alignItems: "center"` + `justifyContent: "center"`, to center cards horizontally/vertically within each cell; card width should not exceed `slotWidth` (or fixed width), to avoid being stretched by `"fill-container"` causing it to "look off-center"
- Step cards: recommended uniform card height or uniform `slotHeight / gap`, to ensure strict y-alignment of stages across lanes
- The lane outer container must explicitly write `fillColor: "#F8F9FA"` (extremely light gray), `borderDash: "dashed"`, `borderWidth: 1`, `borderColor: "#DEE0E3"` (uniform light gray), otherwise it will be compiled as a virtual frame and fail to render
- Uniform height (Flex adaptive, optional): the root container uses `alignItems: "stretch"`, each lane outer frame uses `height: "fill-container"`; the lane interior still maintains the lane label + lane body structure

Example:

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame",
      "id": "lanes-root",
      "x": 40, "y": 40,
      "layout": "horizontal",
      "gap": 16,
      "alignItems": "stretch",
      "children": [
        {
          "type": "frame",
          "id": "lane-left",
          "layout": "vertical",
          "width": "fit-content",
          "height": "fill-container",
          "fillColor": "#F8F9FA",
          "borderDash": "dashed",
          "borderWidth": 1,
          "borderColor": "#DEE0E3",
          "children": [
            { "type": "frame", "id": "lane-left-label-wrap", "layout": "vertical", "width": "fill-container", "height": "fit-content",
              "alignItems": "center", "justifyContent": "center", "padding": [12, 8, 8, 8], "children": [
                { "type": "text", "id": "lane-left-label", "text": "Lane Left", "width": "fill-container", "height": "fit-content",
                  "textAlign": "center", "verticalAlign": "middle", "fontSize": 18, "fontWeight": "bold", "textColor": "#5178C6" }
              ] },
            { "type": "frame", "id": "lane-left-body", "layout": "vertical",
              "gap": 40, "padding": 16,
              "children": [
                { "type": "frame", "id": "stage-1-cell-left", "layout": "vertical", "width": 220, "height": 80, "alignItems": "center", "justifyContent": "center",
                  "children": [{ "type": "rect", "id": "c-s1", "width": 200, "height": "fit-content", "fillColor": "#E1EAFA", "borderColor": "#5178C6", "borderWidth": 2, "borderRadius": 8 }] },
                { "type": "frame", "id": "stage-2-cell-left", "layout": "vertical", "width": 220, "height": 80, "alignItems": "center", "justifyContent": "center", "children": [] }
              ] }
          ]
        },
        {
          "type": "frame",
          "id": "lane-right",
          "layout": "vertical",
          "width": "fit-content",
          "height": "fill-container",
          "fillColor": "#F8F9FA",
          "borderDash": "dashed",
          "borderWidth": 1,
          "borderColor": "#DEE0E3",
          "children": [
            { "type": "frame", "id": "lane-right-label-wrap", "layout": "vertical", "width": "fill-container", "height": "fit-content",
              "alignItems": "center", "justifyContent": "center", "padding": [12, 8, 8, 8], "children": [
                { "type": "text", "id": "lane-right-label", "text": "Lane Right", "width": "fill-container", "height": "fit-content",
                  "textAlign": "center", "verticalAlign": "middle", "fontSize": 18, "fontWeight": "bold", "textColor": "#8569CB" }
              ] },
            { "type": "frame", "id": "lane-right-body", "layout": "vertical",
              "gap": 40, "padding": 16,
              "children": [
                { "type": "frame", "id": "stage-1-cell-right", "layout": "vertical", "width": 220, "height": 80, "alignItems": "center", "justifyContent": "center", "children": [] },
                { "type": "frame", "id": "stage-2-cell-right", "layout": "vertical", "width": 220, "height": 80, "alignItems": "center", "justifyContent": "center",
                  "children": [{ "type": "rect", "id": "d-s2", "width": 200, "height": "fit-content", "fillColor": "#EAE6F3", "borderColor": "#8569CB", "borderWidth": 2, "borderRadius": 8 }] }
              ] }
          ]
        }
      ]
    },
    { "type": "connector", "connector": { "from": "c-s1", "to": "d-s2",
          "lineShape": "polyline", "lineColor": "#BBBFC4", "lineWidth": 2, "endArrow": "arrow" } }
  ]
}
```

<a id="泳道配色默认色板"></a>
### Swimlane Color Scheme (Default Palette)

- **Lane background**: all lane containers uniformly use extremely light gray (such as `fillColor: "#F8F9FA"` or `"#FCFCFC"`), to enhance the sense of hierarchy of the physical container and highlight the colored cards inside.
- **Lane border**: all lane outer containers uniformly use light gray thin dashed lines (`borderColor: "#DEE0E3"`, `borderWidth: 1`, `borderDash: "dashed"`).
- **Lane title**: assign a different theme color to each lane according to the `elements/style.md` classic palette; the lane title's `textColor` uses that theme color.
- **Content nodes (rect)**: adopt a "light background + theme color border" strategy. `fillColor` uses an extremely light color corresponding to that lane's theme color (such as light blue, light purple, etc.), `borderColor` uses the corresponding theme color, and text `textColor` uniformly uses dark color `#1F2329`.
- **Connections (connector)**: connection color is fixed to gray `#BBBFC4`, and does not change with lane colors. When a connection has text (`label`), to prevent the text from pressing on the border and being hard to read, a pure white background (`labelFillColor: "#FFFFFF"`) must be set for the connection text to mask the underlying pattern.

Reminder: avoid creating "virtual frames" (see the explanation in `elements/schema.md`). The lane outer layer must have visible properties to avoid being skipped during compilation.


<a id="连线规则强制参考-connectorsmd"></a>
## Connection Rules (mandatory reference to connectors.md)

The selection and writing of all connections in the swimlane diagram must strictly follow `elements/connectors.md`, especially:
- `connector` must be placed at the top level of `WBDocument.nodes`, and cannot be nested inside `children`
- By default, prioritize automatic routing: `lineShape: "polyline"` / `"rightAngle"`, and do not write `waypoints`
- When `lineShape` is not specified, `"rightAngle"` is used by default
- Only force anchor direction when necessary; anchor selection must be consistent with the relative position of the nodes
- When connections exist, card spacing must satisfy `gap >= 40`; if the connection contains text (`label`), the main-axis spacing must be `gap >= 64`
- Connections with text must set `labelFillColor: "#FFFFFF"` to mask the underlying pattern

Implementation constraints in the swimlane diagram context:
- **By default, do not write anchors**, leave it to the engine to infer automatically; only write them when it is necessary to force "left→right progression / top→bottom progression"
- When it is necessary to express "asynchronous/event flow/push" (such as SSE/Chunk): use `lineStyle: "dashed"` together with `label` to explain the semantics; other parameters still follow connectors.md
- Avoid connecting to "virtual frames that are only used for layout and may be optimized away"; try to connect to the node ids of specific step cards (refer to the virtual frame trap in `elements/schema.md`)

<a id="骨架示例"></a>
## Skeleton Example

> The example demonstrates the structure and alignment method of the layout; for the actual node styles, refer to `elements/style.md` provided that they satisfy the current layout rules

- Horizontal swimlane example:

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame",
      "id": "lanes-root",
      "x": 40,
      "y": 40,
      "layout": "vertical",
      "gap": 16,
      "alignItems": "stretch",
      "padding": 0,
      "width": "fit-content",
      "height": "fit-content",
      "children": [
        {
          "type": "frame",
          "id": "lane-a",
          "layout": "horizontal",
          "gap": 40,
          "padding": 16,
          "width": "fit-content",
          "height": "fill-container",
      "fillColor": "#F8F9FA",
      "borderDash": "dashed",
      "borderWidth": 1,
      "borderColor": "#DEE0E3",
          "children": [
        {
          "type": "text",
          "id": "lane-a-label",
          "text": "Lane A",
          "width": 120,
          "height": "fit-content",
          "textAlign": "left",
          "verticalAlign": "middle",
          "fontSize": 18,
          "fontWeight": "bold",
          "textColor": "#5178C6"
        },
        {
          "type": "frame",
          "id": "stage-1-cell-a",
          "layout": "vertical",
          "gap": 8,
          "padding": 0,
          "width": 200,
          "height": "fit-content",
          "fillColor": "transparent",
          "alignItems": "stretch",
          "justifyContent": "center",
          "children": [
                {
                  "type": "rect",
                  "id": "a-s1",
                  "width": "fill-container",
                  "height": "fit-content",
                  "fillColor": "#E1EAFA",
                  "borderColor": "#5178C6",
                  "borderWidth": 2,
                  "borderRadius": 8,
                  "text": "[阶段 1 节点]",
                  "fontSize": 14,
                  "textColor": "#1F2329",
                  "textAlign": "center",
                  "verticalAlign": "middle"
                }
              ]
            },
        {
          "type": "frame",
          "id": "stage-2-cell-a",
          "layout": "vertical",
          "gap": 8,
          "padding": 0,
          "width": 200,
          "height": "fit-content",
          "fillColor": "transparent",
          "alignItems": "stretch",
          "justifyContent": "center",
          "children": []
        }
          ]
        },
        {
          "type": "frame",
          "id": "lane-b",
          "layout": "horizontal",
          "gap": 40,
          "padding": 16,
          "width": "fit-content",
          "height": "fill-container",
      "fillColor": "#F8F9FA",
      "borderDash": "dashed",
      "borderWidth": 1,
      "borderColor": "#DEE0E3",
          "children": [
        {
          "type": "text",
          "id": "lane-b-label",
          "text": "Lane B",
          "width": 120,
          "height": "fit-content",
          "textAlign": "left",
          "verticalAlign": "middle",
          "fontSize": 18,
          "fontWeight": "bold",
          "textColor": "#8569CB"
        },
        {
          "type": "frame",
          "id": "stage-1-cell-b",
          "layout": "vertical",
          "gap": 8,
          "padding": 0,
          "width": 200,
          "height": "fit-content",
          "fillColor": "transparent",
          "alignItems": "stretch",
          "justifyContent": "center",
          "children": []
        },
        {
          "type": "frame",
          "id": "stage-2-cell-b",
          "layout": "vertical",
          "gap": 8,
          "padding": 0,
          "width": 200,
          "height": "fit-content",
          "fillColor": "transparent",
          "alignItems": "stretch",
          "justifyContent": "center",
          "children": [
                {
                  "type": "rect",
                  "id": "b-s2",
                  "width": "fill-container",
                  "height": "fit-content",
                  "fillColor": "#EAE6F3",
                  "borderColor": "#8569CB",
                  "borderWidth": 2,
                  "borderRadius": 8,
                  "text": "[阶段 2 节点]",
                  "fontSize": 14,
                  "textColor": "#1F2329",
                  "textAlign": "center",
                  "verticalAlign": "middle"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "connector",
      "connector": {
        "from": "a-s1",
        "to": "b-s2",
        "lineShape": "polyline",
        "lineColor": "#BBBFC4",
        "lineWidth": 2,
        "endArrow": "arrow",
        "label": "[跨泳道交互]",
        "labelFillColor": "#FFFFFF"
      }
    }
  ]
}
```

- Vertical swimlane example: see "Vertical Swimlanes" above

- All lanes uniformly use `slotWidth/slotHeight/gap`, and generate a placeholder **stage cell** for each stage (empty stage cells transparent but retained)
- Do not write child node `x/y` inside Flex containers; alignment is achieved through cell index and uniform dimensions
- Only real stages generate cards within the corresponding cell; empty stages do not generate cards but retain cells to ensure grid completeness
- Connections must be placed at the top level of `nodes`, and connect to specific step card ids, do not connect to layout containers such as `lane-*-body`
- **Horizontal swimlanes**: root container uses `layout: "vertical"` with fixed `lanesGap`; lane body uses `layout: "horizontal"`; cell fixed width `slotWidth`; main axis `gap` uniform
- **Vertical swimlanes**: root container uses `layout: "horizontal"` with fixed `lanesGap`; lane body uses `layout: "vertical"`; cell fixed height `slotHeight`; main axis `gap` uniform
- **Lane title**: title is more prominent than step cards, but still only emphasized through font size, font weight, and text color; do not add an extra background bar to the lane title

<a id="陷阱"></a>
## Pitfalls

- **Inconsistent stage slots reused across lanes**: causes misalignment of the same stage; `slotWidth / slotHeight / gap` must be uniform across all lanes
- **Putting connector inside children**: causes schema errors or inability to connect (see connectors.md)
- **Drawing auxiliary containers as visible elements**: lane body or other supporting frames must remain `fillColor: "transparent"`; do not add extra borders except for the lane grouping container
- **Hand-writing waypoints too early**: let the engine route automatically first; only take over through waypoints when necessary
- **Too many connections**: downsample according to the connection count strategy in connectors.md, otherwise cross-lane lines will obscure each other and become unreadable
