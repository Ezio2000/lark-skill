<a id="连线系统"></a>
# Connector System

<a id="连线策略"></a>
## Connector Strategy

| Number of connectors | Strategy |
|--------|------|
| ≤8 | Draw one by one |
| 9-15 | Representative connectors (select 1-2 nodes per layer to connect to the next layer) |
| >15 | Layer-to-layer connectors, or fall back to simplified grouping |

When a node has 3+ connectors: incoming lines from top, outgoing lines from bottom, and multiple lines on the same side are spread out using different directions.

---

<a id="connector-必须放根-nodes-数组"></a>
## connector must be placed in the root nodes array

```typescript
// Wrong: connector placed inside frame children
{ type: 'frame', children: [
  { type: 'connector', ... }  // Will cause a Schema error or fail to connect!
]}

// Correct: connector placed in the root nodes array
const doc: WBDocument = {
  version: 2,
  nodes: [
    { type: 'frame', id: 'box', ... },
    { type: 'connector', ... },  // Must be at the same level as the top-level frame
  ],
};
```

---

<a id="箭头默认值"></a>
## Arrow Defaults

- When `endArrow` is omitted, it defaults to `'arrow'` (i.e., the end of the connector has an arrow by default).
- When `startArrow` is omitted, it defaults to `'none'` (i.e., the start of the connector has no arrow by default).

---

<a id="连线技巧"></a>
## Connector Techniques

```typescript
// Automatic routing (recommended): only need to specify node ids (the engine can automatically infer the optimal outgoing direction), and use polyline or rightAngle shapes
// As long as waypoints are not passed, the engine will attempt to automatically avoid obstacles and generate polylines.
{ type: 'connector', connector: {
  from: 'a', to: 'b', // fromAnchor and toAnchor can also be omitted, letting the engine find the shortest path itself
  lineShape: 'polyline', lineColor: '#000000', lineWidth: 2, endArrow: 'arrow' }}

// Precise coordinates (for annotation arrows)
{ type: 'connector', connector: {
  from: { x: 150, y: 200 }, to: 'b', toAnchor: 'left',
  lineShape: 'curve', lineColor: '#BBBFC4', lineWidth: 2,
  lineStyle: 'dashed', endArrow: 'triangle' }}

// Manually control waypoints (only used when a fixed route must be enforced, or when automatic routing does not meet expectations)
// Note: once waypoints are provided, the engine will strictly respect these points and will no longer perform automatic obstacle avoidance.
{ type: 'connector', connector: {
  from: { x: 300, y: 140 }, to: { x: 300, y: 340 },
  waypoints: [{ x: 350, y: 140 }, { x: 350, y: 340 }],
  lineShape: 'polyline', lineColor: '#000000', lineWidth: 2, endArrow: 'arrow' }}

// Drawing coordinate axes/number lines (must use straight, to prevent tick labels from triggering automatic obstacle avoidance and causing lines to bend)
{ type: 'connector', connector: {
  from: { x: 100, y: 400 }, to: { x: 600, y: 400 },
  lineShape: 'straight', lineColor: '#000000', lineWidth: 2, endArrow: 'arrow' }}
```

> [!IMPORTANT]
> **1. Shape selection requirements (core)**, you need to clearly specify the `lineShape` type:
> - **`'polyline'` (rounded polyline)**: **default first choice**. Suitable for the vast majority of scenarios such as flowcharts and architecture diagrams. Supports the engine's **automatic routing and obstacle avoidance** features (only need to specify `from` and `to`).
> - **`'rightAngle'` (right-angle polyline)**: Suitable for scenarios that explicitly require "bus/right-angle conventions" and strictly aligned tree hierarchies; also supports **automatic routing and obstacle avoidance**.
> - **`'straight'` (straight line)**: Not affected by the automatic obstacle avoidance mechanism; suitable for scenarios such as **coordinate axes, number lines, geometric figure borders, direct pointing relationships** that require lines to be absolutely straight and not allow any detours or bends.
> - **`'curve'` (curve)**: Suitable for elegant cross-layer connectors (S-shaped bends), freely diverging mind map branches, or annotation arrows.
> - **Note**: You need to choose the most appropriate `lineShape` based on the type of diagram currently being drawn and the context. Do not blindly use `polyline` for everything; for example, when drawing a coordinate system you must actively switch to `straight`.
> **2. Spacing requirements**: The gap between cards with connector lines must be ≥ 40, otherwise the arrows will be squeezed into the gap and be hard to see.
> **3. Top-level constraint**: `connector` must be placed directly in `WBDocument.nodes`, and is **strictly prohibited** from being nested inside `children`. It is recommended to declare connectors uniformly at the end of the data.
>
> [!TIP]
> **Automatic routing vs manual control**
> - **Prefer relying on automatic routing**: For `'polyline'` and `'rightAngle'`, the engine will automatically plan the path and attempt to avoid obstacles (`fromAnchor` and `toAnchor` can also be omitted, and the engine will automatically infer the optimal outgoing direction); this is the most recommended approach.
> - **When to manually calculate waypoints**: **Only when necessary** (for example, when automatic routing does not meet expectations, or when a specific shape must be enforced to bypass specific elements), should you manually take over the coordinate sequence via `waypoints`.
>
> **Connector labels**
> - **Connector text descriptions**: When a text description is needed, you can annotate it with `label`.

---

<a id="锚点方向规则"></a>
## Anchor Direction Rules

An anchor (top/right/bottom/left) indicates which edge of the node the connector starts from; the direction meaning is the same as the four sides of a CSS border.

**Note: Since the current automatic routing feature supports omitting anchors and letting the engine infer them automatically, the following rules mainly apply to scenarios where you want to forcibly control the outgoing direction, or when using straight lines/curves.**

When choosing anchors, base it on the relative positions of the two nodes: if the target is below, use `fromAnchor: 'bottom'` + `toAnchor: 'top'`; if the target is on the right, use `fromAnchor: 'right'` + `toAnchor: 'left'`. If anchors are manually specified, they must match the actual relative positions of the nodes; otherwise the connector may route in the opposite direction.

**Common paradigms for anchor binding**:
- **Same-layer horizontal progression** (target is directly to the right): `fromAnchor: "right"` -> `toAnchor: "left"`
- **Vertical downward progression** (target is directly below): `fromAnchor: "bottom"` -> `toAnchor: "top"`
- **Cross-layer diagonal progression** (target is at lower-left or lower-right): prefer **`fromAnchor: "bottom"` -> `toAnchor: "top"`**. Since the line segment itself has a gravitational tendency, exiting from the bottom and then curving into the top of the next layer perfectly matches the S-shaped large bend of a pipeline, producing the most elegant and smooth cross-layer curve. **Avoid** using left and right anchors to cross-connect with each other.
- **Reverse flow retrieval** (bottom diverges back to point to the top origin): prefer **`fromAnchor: "top"` -> `toAnchor: "bottom"`** combined with `lineStyle: "dashed"`.
