<a id="布局系统"></a>
# Layout System

<a id="布局决策"></a>
## Layout Decisions

> Do not guess the layout from keywords. Analyze the information structure first, then decide on the layout strategy.
> This file explains general layout principles and skeleton templates; for field semantics see `elements/schema.md`, and for complete scenario paradigms see each `scenes/*.md`.

General principle: **Decide the main layout first, then the sub-layouts.**

**Quick judgment**:
- **Flex**: divide by layer, arrange by region
- **Dagre**: dense relationship networks, process chains dominate
- **Absolute positioning**: spatial position carries information (geographic orientation, topological coordinates, physical panels, etc.), use scripts to compute coordinates
- **Default choice**: when unsure, prefer **Flex**


**Dagre layout unification principles**:
1. Dagre solves **topological relationships**, not automatically filling the canvas.
2. When Dagre is nested as a sub-container, it is by default an opaque node (Opaque Node): it first computes its own bounding box based on its internal topology, then participates in the parent layout as an atomic node. If edges need to penetrate the boundary, you must declare `layout: "dagre"` + `layoutOptions: { isCluster: true }`.
3. In mixed layouts, Flex is better suited for partitioning and hierarchy, while Dagre is better suited for local complex relationships; but if Dagre itself is the main layout, it can also fully take on the main topology of the entire diagram.
4. Before choosing Dagre, look at three things: **the direction of the longest chain, whether branches are symmetric, and whether there are long back edges/retry loops**. Whichever one is unbalanced will skew the bounding box.
5. Relationships such as long back edges, failure retries, and cross-layer returns should be converged locally first; when necessary, split them into local process regions or side-note explanations. Do not let a single edge blow up the entire Dagre width.
6. If the Dagre output shows obvious one-sided whitespace, width-height imbalance, or content occupying only a very small portion within the parent container, you must adjust `rankdir`, restructure the topology, or add a symmetric information region at the parent level. It must not be delivered as-is.

**Reading code to draw architecture diagrams**: scan the directory structure (divided by layer → Flex; divided by functional module → look at dependency direction) → grep imports (one-way → Flex; mesh-like → Dagre or Flex + Dagre) → unsure → default to Flex.

> **`x/y` inside a flex container will be completely ignored!**

❌ Fatal error:
```json
{ "type": "frame", "layout": "vertical", "children": [
  { "type": "rect", "x": 100, "y": 0, "text": "成都" },
  { "type": "rect", "x": 540, "y": 0, "text": "康定" }
]}
```
✅ Correct: use `layout: "none"` or place it in top-level nodes with x/y.

> **A `layout: "none"` (absolute positioning) container must have an explicit fixed width and height!**

❌ Fatal error:
```json
{ "type": "frame", "layout": "none", "width": "fit-content", "height": "fit-content", "children": [
  { "type": "rect", "x": 0, "y": 0, "text": "区域A" },
  { "type": "rect", "x": 500, "y": 0, "text": "区域B" }
]}
```
✅ Correct: an absolute positioning container must be given an explicit fixed width and height:
```json
{ "type": "frame", "layout": "none", "width": 1064, "height": 680, "children": [
  { "type": "rect", "x": 0, "y": 0, "text": "区域A" },
  { "type": "rect", "x": 554, "y": 0, "text": "区域B" }
]}
```

**How to build**:

| Layout type               | Approach                                                                          |
| ---------------------- | ----------------------------------------------------------------------------- |
| Pure Flex / Dagre        | Write JSON directly                                                                   |
| Mixed layout (Flex wrapping Dagre) | Write JSON directly (the outer layer does partitioning first, and local complex relationships are handed to Dagre; if nested, it is by default an opaque node) |
| Diagrams heavily dependent on geometric coordinates   | Write a script to generate JSON (node xxx.cjs)                                                |
| Special lines requiring precise avoidance   | Script + `--layout` two-stage                                                      |

---

<a id="网格方法论"></a>
## Grid Methodology

Core idea: **Draw the grid first, then fill in the content**.

First answer three questions:
1. **How many rows and columns does the information divide into?** Each group gets one row or one column
2. **How big is each cell?** Equal width, or with primary/secondary distinction?
3. **How large is the row/column spacing?** 24-32px between regions, 12-16px within the same region

---

<a id="布局模式选择"></a>
## Layout Mode Selection

| Mode | Applicable scenarios                     | DSL mapping                                                 |
| ---- | ---------------------------- | -------------------------------------------------------- |
| grid | Architecture diagrams, comparison tables, card walls, kanban | vertical frame nesting horizontal frame                     |
| flow | Complex flowcharts, microservice interactions       | `layout: "dagre"`, with the engine automatically computing mesh edge layout            |
| tree | Organizational structure, module dependencies           | `layout: "dagre"` with `rankdir: "TB"` or a Flex with a centered root node |
| free | Geographic layouts, physical panel restoration   | `layout: "none"` + x/y                                   |

Most diagrams use grid or flow mode. Use free only when the node coordinates themselves have strong semantics (such as a map).

> The above are all layout strategy names. The DSL's `layout` attribute value only supports four types: `'horizontal'`, `'vertical'`, `'none'`, `'dagre'`.

---

<a id="dsl-与-css-flexbox-属性映射"></a>
## DSL and CSS Flexbox Property Mapping

| DSL property                         | Corresponding CSS mental model                                | Limitation                                                                       |
| -------------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------- |
| `layout: 'horizontal'`           | `flex-direction: row`                              | Not writing layout = absolute positioning                                                     |
| `layout: 'vertical'`             | `flex-direction: column`                           | Same as above                                                                       |
| `layout: 'none'`                 | `position: absolute` (child nodes use x/y)               | Child nodes cannot use `fill-container`; the container must have a fixed width and height                          |
| `layout: 'dagre'`                | Similar to Mermaid / DOT directed graph layout                    | Width and height only support `fit-content`; compute the bounding box by topology first, then participate in the parent layout; when nested, it is by default an opaque node |
| `width/height: 'fill-container'` | `flex: 1` (main axis) / `align-self: stretch` (cross axis) | Ancestors must have a definite size                                                         |
| `width/height: 'fit-content'`    | `width/height: auto`                               | —                                                                          |
| `alignItems`                     | Same as CSS `align-items`                               | Only `'start'`/`'center'`/`'end'`/`'stretch'` (no flex- prefix)               |
| `justifyContent`                 | Same as CSS `justify-content`                           | Only `'start'`/`'center'`/`'end'`/`'space-between'`/`'space-around'`         |
| `gap`                            | Same as CSS `gap`                                       | Must be written explicitly (otherwise nodes will stick together)                                               |
| `padding`                        | Same as CSS `padding`                                   | Must be written explicitly. Supports `number` / `[v,h]` / `[t,r,b,l]`                          |

The default value of `alignItems` is `'start'` (the CSS Flexbox default is `stretch`). When you need equal-height cards, you must explicitly write `alignItems: 'stretch'`.
The DSL syntax is a strict whitelist; you cannot write native CSS properties (it does not support `alignSelf`, `flexWrap`, `margin`, etc.).

---

<a id="dsl-注意事项"></a>
## DSL Notes

1. **A frame must have the layout attribute written**, otherwise all child nodes pile up in the top-left corner.

2. **fill-container deadlock trap**: when using `fill-container`, there must be a fixed width (or height) in the ancestor chain, otherwise it forms a deadlock with `fit-content` and the size degrades to 0.
   Incorrect example:
   ```json
   { "type": "frame", "layout": "horizontal", "width": "fit-content", "children": [
     { "type": "rect", "width": "fill-container" }
   ]}
   ```
   Correct example:
   ```json
   { "type": "frame", "layout": "horizontal", "width": 1200, "children": [
     { "type": "rect", "width": "fill-container" }
   ]}
   ```
3. **Do not wrap Dagre in an outer frame with fixed width and height**: the size of the Dagre output is determined by the topology and cannot be known in advance. The parent container should use `fit-content` to adapt automatically, or simply let Dagre be the top-level container; do not box it in with fixed pixels.
4. **A `layout: 'none'` container must have a fixed width and height**; do not write it as `fit-content`, otherwise the absolute positioning of child nodes is prone to disorder.
5. **For nodes containing text, use fit-content for height**; the engine does not support overflow, and hard-coding the height will truncate the text.
6. **Shape nodes have padding**: rect/ellipse/diamond/triangle have 12px on each side; cylinder has +42px vertically.
7. **flex-wrap is not supported**; when line wrapping is needed, simulate it with nested frames.
8. **Layer order**: the later a node appears in the array, the higher its layer. When you need overlay annotations, place them at the end of the array.

---

<a id="布局选择指南"></a>
## Layout Selection Guide

| Relationship you want to express             | How to arrange                   | DSL syntax                                                                     |
| -------------------------- | ------------------------ | ---------------------------------------------------------------------------- |
| Sequence, hierarchy from top to bottom     | Vertical stacking                 | `layout: 'vertical'`                                                         |
| Parallel, equally important, comparable     | Horizontal equal division                 | `layout: 'horizontal'` + `alignItems: 'stretch'` + `width: 'fill-container'` |
| A region has a name, with the name on the side     | Side label + content side by side        | horizontal frame: [text(label), frame(content)]                                        |
| Multiple large regions, each independent       | Regions arranged vertically             | vertical frame wrapping multiple colored frames                                                  |
| Does not fit in one row, needs line wrapping       | Nested horizontal frames to simulate line wrapping  | vertical frame wrapping multiple horizontal frames                                                  |
| Complex mesh relationships, topology diagrams     | **Dagre directed graph automatic layout** | `layout: 'dagre'` + `layoutOptions.edges`                                    |
| Node positions themselves are meaningful (maps) | Absolute positioning                 | `layout: 'none'` + x/y                                                       |

These can be freely nested and combined. For example: vertical stacking (title) + regions arranged vertically (multiple layers) + horizontal equal division within each layer (nodes).

---

<a id="布局示例"></a>
## Layout Examples

<a id="纵向堆叠标题--内容"></a>
### Vertical Stacking (Title + Content)

```json
{
  "type": "frame", "layout": "vertical", "gap": 28, "padding": 32,
  "width": 1200, "height": "fit-content",
  "children": [
    { "type": "text", "width": "fill-container", "height": "fit-content",
      "text": "图表标题", "fontSize": 24, "textAlign": "center" },
    ...内容...
  ]
}
```

<a id="横向等分并列元素"></a>
### Horizontal Equal Division (Parallel Elements)

```json
{
  "type": "frame", "layout": "horizontal", "gap": 16, "padding": 0,
  "width": "fill-container", "height": "fit-content",
  "alignItems": "stretch",
  "children": [
    { "type": "rect", "width": "fill-container", "height": "fit-content",
      "textAlign": "center", "verticalAlign": "middle", "text": "A" },
    { "type": "rect", "width": "fill-container", "height": "fit-content",
      "textAlign": "center", "verticalAlign": "middle", "text": "B" }
  ]
}
```

`alignItems: 'stretch'` + `width: 'fill-container'` = equal width and equal height.

<a id="侧标签--内容"></a>
### Side Label + Content

```json
{
  "type": "frame", "layout": "horizontal", "gap": 24, "padding": 0,
  "width": "fill-container", "height": "fit-content",
  "alignItems": "center",
  "children": [
    { "type": "text", "width": 160, "height": "fit-content",
      "text": "区域名称", "fontSize": 20, "textColor": "#1F2329", "textAlign": "right" },
    { "type": "frame", "width": "fill-container", "height": "fit-content",
      ...区域内容...
    }
  ]
}
```

Do not use a frame's `title` attribute as a label—it renders as an extremely small title bar and is unreadable.

<a id="分区纵向排列"></a>
### Regions Arranged Vertically

Divide the content into several large regions, each distinguished by a different color (choose colors from the palette in the style file):

```json
{
  "type": "frame", "layout": "vertical", "gap": 28, "padding": 0,
  "width": "fill-container", "height": "fit-content",
  "children": [
    { "type": "frame", "borderRadius": 8,
      "layout": "horizontal", "gap": 16, "padding": 20, ...区域1... },
    { "type": "frame", "borderRadius": 8,
      "layout": "horizontal", "gap": 16, "padding": 20, ...区域2... }
  ]
}
```

<a id="模拟换行"></a>
### Simulating Line Wrapping

When it does not fit in one row, split it into multiple horizontal frames:

```json
{
  "type": "frame", "layout": "vertical", "gap": 8, "padding": 0,
  "children": [
    { "type": "frame", "layout": "horizontal", "gap": 8, "padding": 0,
      "children": [item1, item2, item3, item4] },
    { "type": "frame", "layout": "horizontal", "gap": 8, "padding": 0,
      "children": [item5, item6] }
  ]
}
```

<a id="复杂拓扑混合布局-dagre--flex"></a>
## Complex Topology Mixed Layout (Dagre + Flex)

When you are dealing with **topology diagrams / link flowcharts / complex architecture diagrams with many edges and messy relationships**, you do not need to manually compute the coordinates of each node; prioritize the **Flex + Dagre mixed layout strategy**. This mainly includes two dimensions of nesting:

* **Outer Dagre + inner Flex (complex nodes)**: **This is the most recommended way to draw complex architectures**. The overall diagram topology is automatically computed and smoothly routed by `layout: "dagre"`, while the nodes in the diagram are no longer just monotonous rectangles; they can be complex `frame` cards freely assembled with Flex (including icons, primary/secondary titles, status, etc.), allowing nodes to carry richer information.
* **Outer Flex + inner Dagre (local process)**: The outer layer uses Flex or absolute positioning to divide large business regions, while a specific region contains a `layout: "dagre"` container responsible for handling the local business flow.
  * **Do a width pre-check before nesting**: Dagre will freely stretch its bounding box to both sides according to the topology. If it may span across and cause overflow, prioritize changing `rankdir` to `TB`, shortening the text, reducing `nodesep/ranksep`, and when necessary splitting the overly long chain into stepwise regions.

```json
{
  "type": "frame", "id": "arch_root",
  "layout": "dagre", "padding": 40,
  "width": "fit-content", "height": "fit-content",
  "layoutOptions": {
    "rankdir": "LR", "nodesep": 60, "ranksep": 100,
    "edges": [
      ["client", "auth_svc", "request"],
      ["auth_svc", "order_svc"],
      ["order_svc", "order_db"]
    ]
  },
  "children": [
    {
      "type": "frame", "id": "client",
      "layout": "vertical", "gap": 6, "padding": [12, 16],
      "alignItems": "center",
      "fillColor": "#F8FAFC", "borderColor": "#CBD5E1", "borderWidth": 2, "borderRadius": 10,
      "children": [
        { "type": "text", "text": "Client App", "fontSize": 14, "textColor": "#0F172A" },
        { "type": "text", "text": "React 18", "fontSize": 10, "textColor": "#64748B" }
      ]
    },
    {
      "type": "frame", "id": "cluster_gateway",
      "layout": "dagre", "layoutOptions": { "isCluster": true, "clusterTitle": "Gateway Tier", "clusterTitleColor": "#15803D" },
      "fillColor": "#F0FDF4", "borderColor": "#86EFAC",
      "borderWidth": 2, "borderDash": "dashed", "borderRadius": 16,
      "children": [
        { "type": "rect", "id": "auth_svc", "width": 120, "height": 40, "text": "Auth Service", "fillColor": "#DCFCE7", "borderColor": "#86EFAC", "borderWidth": 1, "borderRadius": 6, "fontSize": 12 },
        { "type": "rect", "id": "order_svc", "width": 120, "height": 40, "text": "Order Service", "fillColor": "#DCFCE7", "borderColor": "#86EFAC", "borderWidth": 1, "borderRadius": 6, "fontSize": 12 }
      ]
    },
    {
      "type": "frame", "id": "order_db",
      "layout": "vertical", "gap": 4, "padding": [10, 14],
      "alignItems": "center",
      "fillColor": "#FFFFFF", "borderColor": "#FECACA", "borderWidth": 2, "borderRadius": 10,
      "children": [
        { "type": "cylinder", "width": 50, "height": 36, "fillColor": "#FCA5A5", "borderColor": "#DC2626", "borderWidth": 1 },
        { "type": "text", "text": "Order DB", "fontSize": 12, "textColor": "#7F1D1D" }
      ]
    }
  ]
}
```

**Example key points**:
- `client` and `order_db` are **Flex composite nodes** (opaque nodes), internally using a vertical layout to combine multiple rows of information; to the outer Dagre they are atoms with fixed width and height.
- `cluster_gateway` is a **transparent subgraph** (`layout: "dagre"` + `isCluster: true`); external edges can cross the boundary and reach `auth_svc` and `order_svc` directly.
- All `edges` are written uniformly in the `layoutOptions` of the outermost root Dagre.

**Dagre nested layout rules**:

1. **Opaque Node**: A sub-container inside Dagre, regardless of whether its internal layout is flex, absolute, or dagre, as long as it does not declare isCluster: true, is an opaque atomic node with a definite width and height to the outer Dagre. Outer edges cannot address its internal child nodes.
2. **Edge Redirect Fallback**: When edges reference a child node ID inside an opaque node, the engine automatically redirects that edge endpoint to its nearest opaque ancestor node. It does not error and does not produce dangling edges.
3. **Compound Cluster**: When a sub-container declares both `layout: "dagre"` and `layoutOptions: { isCluster: true }`, it becomes a compound subgraph of the outer Dagre. Its internal child nodes directly participate in the outer topology computation, and edges can cross the subgraph boundary. The subgraph itself does not perform independent layout; its size is automatically expanded by the outer Dagre according to the bounding box of its internal nodes.

---

<a id="绝对定位"></a>
## Absolute Positioning

Use absolute positioning when node positions themselves are meaningful (topology diagrams, maps, timeline axes). Most diagrams should prioritize Flex.

<a id="混合布局"></a>
### Mixed Layout

Use Flex for automatic layout inside modules, and absolute positioning for freely placing modules relative to each other. Note: the `layout: "none"` parent container that holds these modules must first be given a **fixed width and height**, and then the child modules are placed inside it.

```json
{
  "type": "frame", "layout": "none", "width": 1200, "height": 800,
  "children": [
    {
      "type": "frame", "id": "module-a", "x": 100, "y": 100,
      "width": 300, "height": "fit-content",
      "layout": "vertical", "gap": 8, "padding": 16,
      "children": [
        { "type": "rect", "width": "fill-container", "height": "fit-content", "text": "内容1" },
        { "type": "rect", "width": "fill-container", "height": "fit-content", "text": "内容2" }
      ]
    }
  ]
}
```

<a id="两阶段绘图"></a>
### Two-Stage Drawing

First produce a skeleton diagram and export the coordinates, then add edges and annotations based on the coordinates:

```bash
npx -y @larksuite/whiteboard-cli@^0.2.13 -i skeleton.json -o step1.png -l coords.json
```

`coords.json` contains the precise coordinates of each node with an id (absX, absY, width, height).

---

<a id="常用间距和尺寸"></a>
## Common Spacing and Sizes

| Parameter             | Common range    | Description         |
| ---------------- | ----------- | ------------ |
| Overall diagram width         | 1000-1400px | —            |
| Spacing between regions     | 24-32px     | —            |
| Spacing between nodes within the same region | 12-16px     | —            |
| Spacing between nodes with edges | >= 40px     | Leave space for arrows |
| Region padding       | 16-24px     | —            |
| Side label width       | 120-180px   | —            |

---

<a id="等大卡片"></a>
## Equal-Size Cards

When a row of cards needs equal width and equal height, do not write fixed pixels:

```json
{
  "type": "frame", "layout": "horizontal", "gap": 16, "padding": 0,
  "alignItems": "stretch",
  "children": [
    { "type": "rect", "width": "fill-container", "height": "fit-content", "text": "A" },
    { "type": "rect", "width": "fill-container", "height": "fit-content", "text": "B" }
  ]
}
```

`alignItems: 'stretch'` + `width: 'fill-container'` = equal width and equal height.
