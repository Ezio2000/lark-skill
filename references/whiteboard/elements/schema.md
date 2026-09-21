# DSL Schema

> This document only explains **what can be written in the DSL**: node types, fields, enum values, hard constraints. Layout strategies, composition methods, and the Dagre/Flex mental model are all covered in `elements/layout.md`.
> `?` indicates that the field is optional at the schema level; if stable output is needed, refer to the best practices in the corresponding scene or layout file.

**📝 Core rules of the layout engine**:
- **Basic behavior is equivalent to Flexbox**: Frame layout is based on the Yoga engine. `layout: 'horizontal'` = `flex-direction: row`, `fill-container` = `flex: 1`, `fit-content` = `width: auto`, `gap` / `padding` / `alignItems` / `justifyContent` have the same semantics.
- **Enum values have no flex- prefix**: always use `'start'` / `'end'` instead of the native CSS `'flex-start'` / `'flex-end'`.
- **Difference in default alignment**: the default value of `alignItems` is `'start'` (the native CSS default is `stretch`). So when cards in the same row need to be equal height, you **must explicitly declare** `alignItems: 'stretch'`.
- **Special characteristics of the Dagre engine**: as a dedicated topological connection engine, `layout: 'dagre'` itself does not support `fill-container` width/height; to its parent container, it is a self-adaptive (shrink-wrapping) black box.

## WBDocument

```typescript
interface WBDocument {
  version: 2;
  nodes: WBNode[];   // Top-level node. connector must be placed here, and cannot be nested in children
}
```

<a id="节点类型"></a>
## Node types

<a id="frame容器"></a>
### Frame (container)

The only type that can contain child nodes. Used for grouping, layout, and backgrounds.

```typescript
{
  type: 'frame';
  id?: string;
  x?: number; y?: number;       // Flex child nodes do not need x/y
  width: WBSizeValue;
  height: WBSizeValue;
  layout: 'horizontal' | 'vertical' | 'none' | 'dagre';  // Layout mode
  gap: number;                    // Must be written explicitly (if omitted, nodes will stick together, which easily causes bugs)
  padding: number | [number, number] | [number, number, number, number]; // Must be written explicitly (if omitted, content will stick to the edges)
  justifyContent?: 'start' | 'center' | 'end' | 'space-between' | 'space-around';
  alignItems?: 'start' | 'center' | 'end' | 'stretch';
  layoutOptions?: {                 // Only takes effect when layout is 'dagre'
    rankdir?: 'TB' | 'BT' | 'LR' | 'RL';
    nodesep?: number;
    edgesep?: number;
    ranksep?: number;
    edges?: Array<[string, string] | [string, string, string]>; // [fromId, toId, label?] The engine automatically lays out child nodes and generates Bezier curve connections
    isCluster?: boolean;            // Transparent subgraph. When true, child nodes participate in the parent-level Dagre topology computation, and connections can cross boundaries
    clusterTitle?: string;          // Floating subgraph title (automatically snaps to the top-left corner)
    clusterTitleColor?: string;     // Title color (HEX format, e.g. "#8B5CF6")
  };
  fillColor?: string;
  borderColor?: string;
  borderWidth?: number;
  borderDash?: 'solid' | 'dashed' | 'dotted';
  borderRadius?: number;
  children?: WBNode[];           // Cannot contain connector
}
```

**Dagre nested layout rules**:

1. **Opaque Node**: A child container inside Dagre, regardless of whether `layout` is `flex`, `absolute`, or `dagre`, as long as `isCluster: true` is not declared, is an opaque atomic node with a definite width and height to the outer Dagre. Outer connections cannot address its internal child nodes.
2. **Edge Redirect Fallback**: When `edges` references a child node ID inside an opaque node, the engine automatically redirects that connection endpoint to its nearest opaque ancestor node. No error is reported, and no dangling connections are produced.
3. **Compound Cluster**: When a child container declares both `layout: "dagre"` and `layoutOptions: { isCluster: true }`, it becomes a compound subgraph of the outer Dagre. Its internal child nodes directly participate in the outer topology computation, and connections can cross the subgraph boundary. The subgraph itself does not perform independent layout; its size is automatically expanded by the outer Dagre according to the bounding box of the internal nodes.

**Minimal usage of isCluster**:
```json
{
  "type": "frame", "id": "cluster_a",
  "layout": "dagre", "layoutOptions": { "isCluster": true },
  "fillColor": "#F0FDF4", "borderColor": "#86EFAC", "borderWidth": 2, "borderDash": "dashed", "borderRadius": 16,
  "children": [
    { "type": "text", "text": "区域标题", "fontSize": 11, "textColor": "#15803D" },
    { "type": "rect", "id": "node_inside", "width": 120, "height": 40, "text": "内部节点" }
  ]
}
```
> Note: `edges` must be written in the `layoutOptions` of the **outermost root Dagre**, not inside a cluster.
**Other constraints**:
- `layout / gap / padding` is optional at the schema level, but it is recommended to write it explicitly during actual generation to avoid relying on default behavior.
- `layoutOptions` only takes effect when `layout: 'dagre'`.
- `children` cannot contain `connector`.

> **Virtual frame trap**: A frame without `fillColor`, `borderColor`, or `borderWidth` may be skipped during compilation as a pure layout container (child nodes are promoted directly to the parent). If you set `id` on such a frame and have an external connector connect to it, the frame disappears after compilation, and the connector reference becomes invalid. When you need to preserve this frame, add appearance attributes to it that will not be optimized away.

<a id="基础图形"></a>
### Basic shapes

```typescript
{
  type: 'rect' | 'ellipse' | 'cylinder' | 'diamond' | 'triangle' | 'trapezoid';
  id?: string;
  x?: number; y?: number;
  opacity?: number;              // 0-1, only affects the opacity of fillColor (invalid for frame/text/stickyNote)
  vFlip?: boolean;
  hFlip?: boolean;
  width: WBSizeValue;
  height: WBSizeValue;
  fillColor?: string;
  borderColor?: string;
  borderWidth?: number;
  borderDash?: 'solid' | 'dashed' | 'dotted';
  borderRadius?: number;
  topWidth?: number;             // Only valid for triangle / trapezoid; the top edge width of a trapezoid or the truncated width of a triangle's top vertex
  text?: string | WBTextRun[];   // Plain text or rich text
  fontSize?: number;
  textColor?: string;
  textAlign?: 'left' | 'center' | 'right';     // Shape default is 'center' (different from CSS)
  verticalAlign?: 'top' | 'middle' | 'bottom';  // Shape default is 'middle' (different from CSS)
}
```

> **cylinder constraint**: The curvature of a cylinder is fixed at 16px and does not scale with width. If the width is too large, it becomes a flat ellipse. `width: "fill-container"` is prohibited; you must use a fixed width + `height: "fit-content"`. Choose the width according to the text length, usually 120-200px.

> **Shape padding (TEXT_INSET)**: Shape nodes have mandatory padding, and fit-content compensates automatically.
> - rect / ellipse / diamond / triangle: 12px on all sides
> - cylinder: top arc 32px + bottom arc 10px (vertical +42px), 7px horizontally on each side
>
> When you need to manually calculate fixed dimensions: `实际文字宽/高 + 对应 inset`.
> Example: two lines of 14px text inside a rect are ~32px high → `height >= 32 + 24 = 56px`

<a id="image图片节点"></a>
### Image (image node)

Image nodes are used to display images on the whiteboard. Images cannot use URLs directly; they must first be uploaded to Feishu to obtain a media token.

```typescript
{
  type: 'image';
  id?: string;
  x?: number; y?: number;
  width: WBSizeValue;           // Fixed width, recommended 240 or 200
  height: WBSizeValue;          // Fixed height, recommended in a 3:2 ratio (e.g. 240×160 or 200×133)
  image: {
    src: string;                // media token (obtained by uploading via docs +media-upload --parent-type whiteboard)
  };
}
```

> **Key constraints**:
> - `image.src` must be the **media token** returned after uploading via `docs +media-upload --parent-type whiteboard --parent-node <画板token>`, and cannot be a URL or Drive file token
> - Images must be uploaded to the **target whiteboard**; tokens from a different whiteboard are not usable
> - All image nodes within the same whiteboard should use a uniform width/height to maintain visual consistency
> - The image aspect ratio is recommended to be 3:2 (e.g. 240×160) to avoid distortion
> - For the detailed upload process, see [`elements/image.md`](../elements/image.md)

<a id="text纯文本节点"></a>
### Text (plain text node)

```typescript
{
  type: 'text';
  id?: string;
  x?: number; y?: number;
  width: WBSizeValue;
  height: WBSizeValue;
  text?: string | WBTextRun[];
  fontSize?: number;
  textColor?: string;
  textAlign?: 'left' | 'center' | 'right';
  verticalAlign?: 'top' | 'middle' | 'bottom';
}
```

<a id="stickynote便签"></a>
### StickyNote (sticky note)

```typescript
{
  type: 'stickyNote';
  id?: string;
  x?: number; y?: number;
  width: WBSizeValue;
  height: WBSizeValue;
  fillColor?: '#FEF1CE' | '#F5D1A7' | '#DFF5E5' | '#CDF7CC' | '#C9E8EF' | '#D6DCF3' | '#D3CCEE' | '#F1C5E7' | '#F6C8C8'; // Sticky note background color (only these 9 are supported)
  text?: string | WBTextRun[];
  fontSize?: number;
  textColor?: string;
  textAlign?: 'left' | 'center' | 'right';
  verticalAlign?: 'top' | 'middle' | 'bottom';
}
```

<a id="connector连线"></a>
### Connector (connection)

Must be placed in the top-level `nodes` array, and cannot be nested in a frame's `children`.

```typescript
{
  type: 'connector';
  id?: string;
  connector: {
    from: string | { x: number; y: number };   // Node id or coordinates
    to:   string | { x: number; y: number };
    fromAnchor?: 'top' | 'right' | 'bottom' | 'left';
    toAnchor?:   'top' | 'right' | 'bottom' | 'left';
    lineShape?:  'straight' | 'polyline' | 'curve' | 'rightAngle'; // Straight line, rounded polyline, curve, right-angle polyline
    lineColor?: string;
    lineWidth?: number;
    lineStyle?: 'solid' | 'dashed' | 'dotted';
    startArrow?: 'none' | 'arrow' | 'triangle' | 'circle' | 'diamond';
    endArrow?:   'none' | 'arrow' | 'triangle' | 'circle' | 'diamond';
    waypoints?: { x: number; y: number }[];  // polyline waypoints
    label?: string;                          // Label text in the middle of the connection
    labelPosition?: number;                  // Label position, 0-1, default 0.5 (midpoint)
  };
}
```

### SVG

```typescript
{
  type: 'svg';
  id?: string;
  x?: number; y?: number;
  opacity?: number;
  width: WBSizeValue;
  height: WBSizeValue;
  svg: { code: string };         // SVG code string
}
```

<a id="渲染规范"></a>
#### Rendering specification

SVG is loaded onto the canvas via a `image/svg+xml` Blob, and is **not in the HTML DOM**, so there are strict limitations:

**Required**:
- Include the `viewBox` attribute (e.g. `viewBox="0 0 24 24"`); the engine relies on it to determine the coordinate system
- Include `xmlns="http://www.w3.org/2000/svg"` (when SVG is parsed as an independent `image/svg+xml`, the XML specification requires declaring the namespace)

**Allowed elements** (pure geometric drawing):
- Basic shapes: `<rect>` `<circle>` `<ellipse>` `<line>` `<polyline>` `<polygon>` `<path>`
- Gradients/filters: `<defs>` `<linearGradient>` `<radialGradient>` `<filter>` `<feGaussianBlur>` `<feMerge>`
- Structure: `<g>` `<clipPath>` `<mask>` `<use>`

**Prohibited elements** (fonts and external resources cannot be loaded in the Blob sandbox):
- `<text>` `<tspan>` (replace with a DSL rect node at the same level + text attribute)
- `<image>` (replace with a DSL image node at the same level)
- `<foreignObject>`
- Any attribute that references an external URL (`xlink:href` pointing to a remote resource, etc.)

<a id="两种典型用法"></a>
#### Two typical usages

**1. Background decorative SVG** (large size, same size as the frame)

Used to draw geometric backgrounds such as connections, curves, and glow effects. Text information is overlaid via rect nodes in the same frame:

```json
{
  "type": "frame", "width": 1400, "height": 680, "layout": "none",
  "children": [
    { "type": "svg", "x": 0, "y": 0, "width": 1400, "height": 680,
      "svg": { "code": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1400 680\" ...>...</svg>" } },
    { "type": "rect", "x": 100, "y": 50, "width": 200, "height": 40,
      "text": "Label", "fillColor": "transparent" }
  ]
}
```

**2. Inline icon SVG** (24-48px, Feather/Lucide style)

Used for small icons in cards/buttons, pure stroke lines:

```json
{ "type": "svg", "width": 32, "height": 32,
  "svg": { "code": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#3B82F6\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"12\" cy=\"12\" r=\"10\"/><polyline points=\"12 6 12 12 16 14\"/></svg>" } }
```

<a id="icon内置图标"></a>
### Icon (built-in icon)

References an icon from the whiteboard's built-in icon library. Simpler than hand-writing SVG—you only need to specify `name`.

```typescript
{
  type: 'icon';
  id?: string;
  x?: number; y?: number;
  width?: WBSizeValue;          // Default 48
  height?: WBSizeValue;         // Default 48, keep it square
  name: string;                 // Icon name, selected from the output of npx -y @larksuite/whiteboard-cli@^0.2.13 --icons
  color?: string;               // Optional color override, hex format such as '#FF6600'
}
```

**Get available icons**: After planning the content and layout, run the following command to view all available icon names, and select from them:
```bash
npx -y @larksuite/whiteboard-cli@^0.2.13 --icons
```

Usage:
```json
{ "type": "icon", "id": "db", "name": "database", "width": 48, "height": 48 }
```

**Usage suggestions**:
- When nodes in the diagram represent concrete things (servers, users, databases, etc.), using icons is more intuitive than plain text boxes
- 3-8 icons per diagram is appropriate; add icons for key components and use ordinary shapes for secondary nodes
- Use `color` to specify a suitable color for the icon, for example matching the color scheme of its container
- Icons can be placed in frame child elements to participate in flex layout, and connections can connect to icons via id
- Icon + text combination: place icon + text in a frame(vertical) to form a rich component

```json
{
  "type": "frame", "layout": "vertical", "gap": 8, "padding": 12,
  "alignItems": "center", "fillColor": "#F0F5FF", "borderColor": "#ADC6FF",
  "children": [
    { "type": "icon", "id": "db-icon", "name": "database", "width": 36, "height": 36 },
    { "type": "text", "text": "PostgreSQL", "fontSize": 12, "width": "fit-content", "height": "fit-content" }
  ]
}
```

---

<a id="富文本-wbtextrun"></a>
## Rich text WBTextRun

The `text` field can be a plain string or an array of `WBTextRun[]`. Similar to HTML inline styles: bold corresponds to `<b>`, italic corresponds to `<i>`, and listType corresponds to `<ol>/<ul>`. Each run is a segment of styled text:

```typescript
interface WBTextRun {
  content: string;               // Text content, may contain \n line breaks
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  strikeThrough?: boolean;
  fontSize?: number;
  color?: string;                // Text color
  backgroundColor?: string;     // Text highlight background
  hyperlink?: string;
  listType?: 'none' | 'ordered' | 'unordered';
  indent?: number;               // Indent level
  quote?: boolean;               // Blockquote
}
```

Example:

```json
{
  "text": [
    { "content": "标题文字\n", "bold": true, "fontSize": 16 },
    { "content": "正文内容，", "fontSize": 14 },
    { "content": "高亮部分", "backgroundColor": "#FEF1CE", "fontSize": 14 }
  ]
}
```

Double quotes appearing in `text` and `content` must be written as `\"`; this is required by the JSON specification. Use `\n` for line breaks (written as `"第一行\n第二行"` in JSON, do not double-escape it as `\\n`).

---

<a id="尺寸值-wbsizevalue"></a>
## Size value WBSizeValue

| Value                    | Meaning                        | Note                                   |
| --------------------- | --------------------------- | -------------------------------------- |
| `number`              | Fixed pixels                    | Any scenario                               |
| `'fit-content'`       | Size determined by content              | Parent needs Flex layout                     |
| `'fit-content(N)'`    | Same as above, fallback N when there is no content   | Same as above                                   |
| `'fill-container'`    | Fill the parent's remaining space            | Parent needs Flex layout, and the ancestor chain has a fixed width |
| `'fill-container(N)'` | Same as above, fallback N when there is no Flex | —                                      |

`fill-container` is invalid under `layout: 'none'` (absolute positioning). `fit-content` can still be used for nodes containing text (the engine measures text size via Yoga measureFunc).
