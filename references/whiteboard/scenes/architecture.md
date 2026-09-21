<a id="系统架构图"></a>
# System Architecture Diagram

Applicable to: scenarios with clear module division, such as layered architecture diagrams, microservice architecture diagrams, and frontend-backend architecture diagrams.

<a id="content-约束"></a>
## Content Constraints

- **Fully expand**: When the user says "IM architecture", expand it to the access layer (Web/iOS/Android/desktop), gateway layer (access/routing/security), service layer (two sub-regions: core services + supporting services), and storage layer (MySQL/Redis/MongoDB + parenthetical descriptions of their purposes)
- Each layer has 3-6 nodes. If more than 6, split into two rows or divide into sub-regions (e.g., "Core Services" and "Supporting Services" each as a separate sub-frame)
- Layer labels should be short (2-4 characters), such as "Access Layer" and "Gateway Layer"
- Each node has a title + brief description (e.g., "User Service\nRegistration, login, and permission management")
- Technical components should include the tech stack in parentheses (e.g., "Message Queue\n(Kafka)")
- Storage nodes must use the `cylinder` type (fixed 16px corner radius, `fill-container` width is prohibited, use a fixed width of 120-200). Each row has at most 4 cylinders (if more than 4, wrap to a new line or merge similar items, e.g., merge multiple MySQL instances into "Relational Database\n(MySQL)")
- Sidebars (e.g., operations monitoring, infrastructure) should only be added when the user explicitly requests them, with at most 2-3 items. Do not add sidebars on your own initiative
- You can use icon+text combinations to display content more intuitively and enhance recognizability
- **Connections: Do not draw unless necessary.** The layered structure of an architecture diagram itself already expresses the call direction (upper layers call lower layers), so there is no need to connect every pair of nodes. Only draw connections when a specific call relationship needs to be emphasized, and the total should not exceed 3-5

<a id="layout-选型"></a>
## Layout Selection

| Mode                          | Applicable Conditions                                              | Characteristics                                                                                                                       |
| ----------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| **grid (layered bands)**      | Clear top-down hierarchy (access → gateway → service → storage)    | Rows = layers, each row is a horizontal frame with equally divided nodes. Left-side text labels + right-side layer frames (Label-Outside mode) |
| **grid (grid matrix)**        | Multiple modules at the same level, no clear hierarchy             | N×M grid with equal divisions, one module per cell                                                                                     |
| **Hybrid (island-style)**     | Modules interconnected in a mesh, no clear layering                | Macro `layout: "none"` + x/y positioning for each module island, micro flex layout inside each island                                    |

<a id="layout-规则"></a>
## Layout Rules

- **Root node**: Fixed width (1200), `height: "fit-content"`, `layout: "vertical"`, `gap: 20`, `padding: 24`
- **Main body two-column** (when there is a sidebar): horizontal frame, `alignItems: "stretch"`, `gap: 16`
  - Left layers-container: `width: "fill-container"`, vertical, `gap: 16`
  - Right sidebar: fixed width 160-180, `height: "fill-container"`, `justifyContent: "space-between"`
- **Single layer (Label-Outside)**: horizontal frame, left-side text label (`width: 80`, `textAlign: "right"`), right-side layer frame (`fill-container`, with borderWidth/borderRadius, `padding: 24`, `gap: 16`). **Why use Label-Outside**: Placing the label outside the frame is cleaner and avoids nesting narrow rects inside the frame, which causes vertical text and alignment issues.
- **Sub-regions**: Nest a horizontal wrapper inside the layer frame (`alignItems: "stretch"` ensures equal height in the same row), containing multiple vertical frames (each sub-region), where each sub-region has its own title text + content row. Components within a row are automatically evenly distributed by `width: "fill-container"`.
- **Sidebar**: Split into independent logical block frames (e.g., "Operations Monitoring" and "Infrastructure" separated), each block `height: "fill-container"`. The outer `justifyContent: "space-between"` ensures alignment with the left side, and `justifyContent: "center"` can be set internally to center the content.
- **Inline labels**: If a layer contains special components that span multiple columns (e.g., middleware), a horizontal layout of "small label on the left + component group on the right" can be used

<a id="骨架示例"></a>
## Skeleton Examples

<a id="分层条带label-outside--侧边栏"></a>
### Layered Bands (Label-Outside + Sidebar)

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame",
      "id": "root",
      "x": 0, "y": 0,
      "width": 1200,
      "height": "fit-content",
      "layout": "vertical",
      "gap": 20,
      "padding": 24,
      "children": [
        {
          "type": "text",
          "id": "title",
          "width": "fill-container",
          "height": "fit-content",
          "text": "[图表标题]",
          "fontSize": 24,
          "textAlign": "center",
          "verticalAlign": "middle"
        },
        {
          "type": "frame",
          "id": "main-container",
          "width": "fill-container",
          "height": "fit-content",
          "layout": "horizontal",
          "alignItems": "stretch",
          "gap": 16,
          "padding": 0,
          "children": [
            {
              "type": "frame",
              "id": "layers-container",
              "width": "fill-container",
              "height": "fit-content",
              "layout": "vertical",
              "alignItems": "stretch",
              "gap": 16,
              "padding": 0,
              "children": [
                {
                  "type": "frame",
                  "id": "row-layer-1",
                  "width": "fill-container",
                  "height": "fit-content",
                  "layout": "horizontal",
                  "gap": 24,
                  "padding": 0,
                  "alignItems": "center",
                  "children": [
                    {
                      "type": "text",
                      "id": "label-1",
                      "width": 80,
                      "height": "fit-content",
                      "text": "[层标签]",
                      "fontSize": 20,
                      "textAlign": "right"
                    },
                    {
                      "type": "frame",
                      "id": "layer-1",
                      "width": "fill-container",
                      "height": "fit-content",
                      "borderWidth": 2,
                      "borderRadius": 8,
                      "layout": "horizontal",
                      "gap": 16,
                      "padding": 24,
                      "alignItems": "stretch",
                      "children": [
                        { "type": "rect", "id": "n-1-1", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                        { "type": "rect", "id": "n-1-2", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                        { "type": "rect", "id": "n-1-3", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" }
                      ]
                    }
                  ]
                },
                {
                  "type": "frame",
                  "id": "row-layer-2",
                  "width": "fill-container",
                  "height": "fit-content",
                  "layout": "horizontal",
                  "gap": 24,
                  "padding": 0,
                  "alignItems": "center",
                  "children": [
                    {
                      "type": "text",
                      "id": "label-2",
                      "width": 80,
                      "height": "fit-content",
                      "text": "[层标签]",
                      "fontSize": 20,
                      "textAlign": "right"
                    },
                    {
                      "type": "frame",
                      "id": "layer-2",
                      "width": "fill-container",
                      "height": "fit-content",
                      "borderWidth": 2,
                      "borderRadius": 8,
                      "layout": "vertical",
                      "gap": 16,
                      "padding": 24,
                      "alignItems": "stretch",
                      "children": [
                        {
                          "type": "frame",
                          "id": "subareas-wrapper",
                          "width": "fill-container",
                          "height": "fit-content",
                          "layout": "horizontal",
                          "alignItems": "stretch",
                          "gap": 16,
                          "padding": 0,
                          "children": [
                            {
                              "type": "frame",
                              "id": "subarea-a",
                              "width": "fill-container",
                              "height": "fit-content",
                              "layout": "vertical",
                              "gap": 8,
                              "padding": 12,
                              "borderRadius": 8,
                              "borderWidth": 2,
                              "children": [
                                { "type": "text", "id": "title-a", "width": "fill-container", "height": "fit-content", "text": "[子区域名]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                                {
                                  "type": "frame",
                                  "id": "row-a-1",
                                  "width": "fill-container",
                                  "height": "fit-content",
                                  "layout": "horizontal",
                                  "gap": 8,
                                  "padding": 0,
                                  "children": [
                                    { "type": "rect", "id": "sa-1", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                                    { "type": "rect", "id": "sa-2", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" }
                                  ]
                                }
                              ]
                            },
                            {
                              "type": "frame",
                              "id": "subarea-b",
                              "width": "fill-container",
                              "height": "fit-content",
                              "layout": "vertical",
                              "gap": 8,
                              "padding": 12,
                              "borderRadius": 8,
                              "borderWidth": 2,
                              "children": [
                                { "type": "text", "id": "title-b", "width": "fill-container", "height": "fit-content", "text": "[子区域名]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                                {
                                  "type": "frame",
                                  "id": "row-b-1",
                                  "width": "fill-container",
                                  "height": "fit-content",
                                  "layout": "horizontal",
                                  "gap": 8,
                                  "padding": 0,
                                  "children": [
                                    { "type": "rect", "id": "sb-1", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                                    { "type": "rect", "id": "sb-2", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" }
                                  ]
                                }
                              ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  "type": "frame",
                  "id": "row-layer-3",
                  "width": "fill-container",
                  "height": "fit-content",
                  "layout": "horizontal",
                  "gap": 24,
                  "padding": 0,
                  "alignItems": "center",
                  "children": [
                    {
                      "type": "text",
                      "id": "label-3",
                      "width": 80,
                      "height": "fit-content",
                      "text": "[层标签]",
                      "fontSize": 20,
                      "textAlign": "right"
                    },
                    {
                      "type": "frame",
                      "id": "layer-3",
                      "width": "fill-container",
                      "height": "fit-content",
                      "borderWidth": 2,
                      "borderRadius": 8,
                      "layout": "horizontal",
                      "gap": 0,
                      "padding": 24,
                      "justifyContent": "space-around",
                      "children": [
                        { "type": "cylinder", "id": "db-1", "width": 140, "height": "fit-content", "text": "[存储名]", "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                        { "type": "cylinder", "id": "db-2", "width": 140, "height": "fit-content", "text": "[存储名]", "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "type": "frame",
              "id": "right-sidebar-wrapper",
              "width": 180,
              "height": "fill-container",
              "layout": "vertical",
              "alignItems": "stretch",
              "justifyContent": "space-between",
              "gap": 16,
              "padding": 0,
              "children": [
                {
                  "type": "frame",
                  "id": "side-block-1",
                  "width": "fill-container",
                  "height": "fill-container",
                  "layout": "vertical",
                  "alignItems": "stretch",
                  "justifyContent": "center",
                  "gap": 12,
                  "padding": 16,
                  "borderRadius": 8,
                  "borderWidth": 2,
                  "children": [
                    { "type": "text", "id": "side-title-1", "width": "fill-container", "height": "fit-content", "text": "[侧边栏模块名]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                    {
                      "type": "frame",
                      "id": "side-items-1",
                      "width": "fill-container",
                      "height": "fit-content",
                      "layout": "vertical",
                      "gap": 8,
                      "padding": 0,
                      "children": [
                        { "type": "rect", "id": "s-1", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                        { "type": "rect", "id": "s-2", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" }
                      ]
                    }
                  ]
                },
                {
                  "type": "frame",
                  "id": "side-block-2",
                  "width": "fill-container",
                  "height": "fill-container",
                  "layout": "vertical",
                  "alignItems": "stretch",
                  "justifyContent": "center",
                  "gap": 12,
                  "padding": 16,
                  "borderRadius": 8,
                  "borderWidth": 2,
                  "children": [
                    { "type": "text", "id": "side-title-2", "width": "fill-container", "height": "fit-content", "text": "[侧边栏模块名]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                    {
                      "type": "frame",
                      "id": "side-items-2",
                      "width": "fill-container",
                      "height": "fit-content",
                      "layout": "vertical",
                      "gap": 8,
                      "padding": 0,
                      "children": [
                        { "type": "rect", "id": "s-3", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
                        { "type": "rect", "id": "s-4", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

<a id="岛屿式网状互联"></a>
### Island-Style (Mesh Interconnection)

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame",
      "id": "root",
      "x": 0, "y": 0,
      "width": 1200,
      "height": 800,
      "layout": "none",
      "padding": 24,
      "children": [
        {
          "type": "text",
          "id": "title",
          "x": 0, "y": 0,
          "width": 1152,
          "height": "fit-content",
          "text": "[图表标题]",
          "fontSize": 24,
          "textAlign": "center",
          "verticalAlign": "middle"
        },
        {
          "type": "frame",
          "id": "island-a",
          "x": 40, "y": 60,
          "width": 320,
          "height": "fit-content",
          "layout": "vertical",
          "gap": 12,
          "padding": 20,
          "borderWidth": 2,
          "borderRadius": 8,
          "children": [
            { "type": "text", "id": "island-a-title", "width": "fill-container", "height": "fit-content", "text": "[模块名]", "fontSize": 16, "textAlign": "center", "verticalAlign": "middle" },
            { "type": "rect", "id": "ia-1", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
            { "type": "rect", "id": "ia-2", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" }
          ]
        },
        {
          "type": "frame",
          "id": "island-b",
          "x": 440, "y": 60,
          "width": 320,
          "height": "fit-content",
          "layout": "vertical",
          "gap": 12,
          "padding": 20,
          "borderWidth": 2,
          "borderRadius": 8,
          "children": [
            { "type": "text", "id": "island-b-title", "width": "fill-container", "height": "fit-content", "text": "[模块名]", "fontSize": 16, "textAlign": "center", "verticalAlign": "middle" },
            { "type": "rect", "id": "ib-1", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" },
            { "type": "rect", "id": "ib-2", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" }
          ]
        },
        {
          "type": "frame",
          "id": "island-c",
          "x": 240, "y": 340,
          "width": 320,
          "height": "fit-content",
          "layout": "vertical",
          "gap": 12,
          "padding": 20,
          "borderWidth": 2,
          "borderRadius": 8,
          "children": [
            { "type": "text", "id": "island-c-title", "width": "fill-container", "height": "fit-content", "text": "[模块名]", "fontSize": 16, "textAlign": "center", "verticalAlign": "middle" },
            { "type": "rect", "id": "ic-1", "width": "fill-container", "height": "fit-content", "text": "[节点名]", "borderRadius": 8, "borderWidth": 2, "fontSize": 14, "textAlign": "center", "verticalAlign": "middle" }
          ]
        }
      ]
    },
    { "type": "connector", "connector": { "from": "ia-1", "to": "ib-1", "fromAnchor": "right", "toAnchor": "left", "lineShape": "straight", "lineWidth": 2, "endArrow": "arrow" } },
    { "type": "connector", "connector": { "from": "island-a", "to": "ic-1", "fromAnchor": "bottom", "toAnchor": "top", "lineShape": "rightAngle", "lineWidth": 2, "endArrow": "arrow" } },
    { "type": "connector", "connector": { "from": "island-b", "to": "ic-1", "fromAnchor": "bottom", "toAnchor": "top", "lineShape": "rightAngle", "lineWidth": 2, "endArrow": "arrow" } }
  ]
}
```

<a id="陷阱"></a>
## Pitfalls

- **Using layered bands for all architecture diagrams**: When multiple modules are at the same level and interconnected in a mesh, island-style should be chosen; when there is no clear hierarchy, grid matrix should be chosen. Determine the information structure first, then choose the layout.
- **Too many connections causing crossings**: Do not draw connections in architecture diagrams unless necessary. The layered structure itself already expresses the call direction, so there is no need to connect every pair of nodes. If connections must be drawn, at most 3-5 critical paths.
- **Using frame title for layer labels (unreadable)**: Layer labels must use independent text nodes placed outside the frame (Label-Outside mode), not embedded inside the frame.
- **Using fill-container width for cylinder**: The cylinder corner radius is fixed at 16px and does not scale with width, so a fixed width (120-200) must be used.
- **Mixing sidebar logic**: "Operations Monitoring" and "Infrastructure" must be independent frames and cannot be merged into one long strip.
- **Root node without fixed width**: The root frame must have an explicit width (e.g., 1200), otherwise the `fill-container` of child nodes cannot be calculated.
