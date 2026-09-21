<a id="鱼骨图因果图"></a>
# Fishbone Diagram (Cause-and-Effect Diagram)

> **You must write a script to generate the JSON.** The branch angles and cause bone coordinates of a fishbone diagram require trigonometric calculations; writing the JSON by hand directly can easily lead to node overlap and connector clipping. Please use the script template below.

<a id="content-约束"></a>
## Content Constraints

- 4-6 categories
- Causes per category ≤ 4
- Total causes ≤ 20 (if exceeded, categories must be merged)

<a id="layout-选型"></a>
## Layout Selection

- **Script-generated coordinates** (required): Use a .cjs script to calculate fishbone coordinates via trigonometric functions, output a JSON file, then call `npx -y @larksuite/whiteboard-cli@^0.2.13` to render

<a id="layout-规则"></a>
## Layout Rules

- The main spine is horizontally centered, extending from left to right
- Category nodes are arranged by spineX from left to right; odd-numbered ones (1st, 3rd, 5th...) are above, even-numbered ones (2nd, 4th...) are below
- The causes of each category are evenly spaced along the diagonal line (branch bone)
- The fish head (central problem) is on the right, using an ellipse
- The main spine connector has an arrow pointing to the fish head; branch bones and cause bone connectors use endArrow: "none"
- Cause bones extend horizontally to the right side of the cause box, with Y coordinates precisely aligned

<a id="骨架示例"></a>
## Skeleton Example

**Alternating top and bottom**: Category labels are arranged by spineX from left to right; odd-numbered ones (1st, 3rd, 5th...) are above, even-numbered ones (2nd, 4th...) are below.

**Visual same color scheme**: The category label, connector, and all cause nodes under the same branch must use the same color scheme (e.g., the same combination of background color and border color) to maintain visual consistency and logical coherence. You can predefine a set of color arrays and cycle through them by branch.

<a id="坐标计算脚本模板必须严格参照此算法生成"></a>
### Coordinate Calculation Script Template (must strictly follow this algorithm for generation)

The following Node.js script template contains a complete dynamic layout algorithm that can automatically adapt to any number of categories and causes, generating a perfectly non-overlapping fishbone diagram:

```javascript
const fs = require('fs');

const nodes = [];

// 1. Data definition (fill in according to user requirements)
const categories = [
  { id: "c0", text: "前端代码", reasons: ["未压缩资源", "冗余请求", "超大图片未懒加载"] },
  { id: "c1", text: "后端服务", reasons: ["数据库慢查询", "缓存失效", "并发量过大"] },
  { id: "c2", text: "网络环境", reasons: ["CDN配置错误", "DNS解析缓慢", "带宽限制", "网络抖动"] }
];

// 2. Dynamic layout calculation
const catWidth = 120;
const catHeight = 40;
const reasonWidth = 140; // Adjust cause box width to accommodate long text
const reasonHeight = 32;
const lineLength = 20; // Horizontal extension length of the cause bone connector
const paddingX = 40; // Horizontal safety spacing between nodes on the same side

// Predefined branch color scheme array (branch bone category and specific causes maintain the same color scheme)
const branchColors = [
  { fill: "#E8F3FF", stroke: "#1664FF" }, // Blue color scheme
  { fill: "#E6FFED", stroke: "#00B42A" }, // Green color scheme
  { fill: "#FFF7E8", stroke: "#FF7D00" }, // Orange color scheme
  { fill: "#FFECE8", stroke: "#F5319D" }, // Pink color scheme
  { fill: "#F2E8FF", stroke: "#722ED1" }, // Purple color scheme
  { fill: "#E8FFFF", stroke: "#14C9C9" }  // Cyan color scheme
];

let maxSpineY_up = 0;
let maxSpineY_down = 0;

// Step 1: Calculate the internal dimensions and relative bounding box of each category
categories.forEach((cat, index) => {
  const isTop = index % 2 === 0;
  const numReasons = cat.reasons.length;

  // Dynamically calculate branch height to ensure cause bones do not overlap vertically
  // Each cause requires reasonHeight + top/bottom spacing (approximately 16)
  const requiredY = (numReasons + 1) * (reasonHeight + 16);
  const branchDY = Math.max(160, requiredY);
  const branchDX = -branchDY * 0.7; // Maintain a fixed tilt angle extending to the left

  cat.isTop = isTop;
  cat.branchDX = branchDX;
  cat.branchDY = branchDY;

  // Record the maximum branch height, used to calculate background height and main spine Y coordinate
  if (isTop) maxSpineY_up = Math.max(maxSpineY_up, branchDY + catHeight + 40);
  else maxSpineY_down = Math.max(maxSpineY_down, branchDY + catHeight + 40);

  // Calculate the extremes of the relative bounding box for this category (relative to the spineX anchor point)
  // The leftmost side may be determined by the category box or the cause box
  cat.minX = Math.min(branchDX - catWidth / 2, branchDX - lineLength - reasonWidth);
  // The rightmost side is the main spine attachment point 0 or the right side of the category box
  cat.maxX = Math.max(0, branchDX + catWidth / 2);
});

// Step 2: Calculate the absolute X coordinate (spineX) of each category on the main spine
let currentSpineX = 100; // Initial offset
for (let i = 0; i < categories.length; i++) {
  const cat = categories[i];
  let startX = currentSpineX;

  // Must maintain distance from the previous category on the same side to prevent horizontal overlap
  if (i >= 2) {
    const prevSameSideCat = categories[i - 2];
    const requiredX = prevSameSideCat.spineX + prevSameSideCat.maxX - cat.minX + paddingX;
    startX = Math.max(startX, requiredX);
  }

  // Ensure the longest branch on the left does not exceed the left boundary of the canvas
  if (startX + cat.minX < 50) {
    startX = 50 - cat.minX;
  }

  cat.spineX = startX;
  // Advance slightly forward each time to ensure nodes on opposite sides are also slightly offset
  currentSpineX = startX + 80;
}

// Step 3: Calculate global canvas dimensions
const lastCat = categories[categories.length - 1];
const spineY = maxSpineY_up + 50; // Dynamically derive the main spine Y coordinate
const totalWidth = lastCat.spineX + 350; // Reserve space on the right for the fish head
const totalHeight = spineY + maxSpineY_down + 50;

// 4. Generate node data
// Background
nodes.push({ type: "rect", x: 0, y: 0, width: totalWidth, height: totalHeight, fillColor: "#FFFFFF", borderWidth: 0 });

// Fish head
const headWidth = 180;
const headHeight = 80;
const headX = totalWidth - headWidth - 40;
const headY = spineY - headHeight / 2;
nodes.push({ type: "ellipse", id: "head", x: headX, y: headY, width: headWidth, height: headHeight, text: "核心问题" });

// Main spine connector
const firstSpineX = categories[0].spineX + categories[0].minX;
nodes.push({
  type: "connector",
  connector: { from: { x: firstSpineX, y: spineY }, to: "head", toAnchor: "left", lineShape: "straight", endArrow: "arrow" }
});

// Iterate to generate categories and cause bones
categories.forEach((cat, index) => {
  const isTop = cat.isTop;
  const branchDY = cat.branchDY;
  const branchDX = cat.branchDX;
  const color = branchColors[index % branchColors.length];

  // Category label
  const catX = cat.spineX + branchDX - catWidth / 2;
  const catY = spineY + (isTop ? -branchDY - catHeight : branchDY);

  nodes.push({
    type: "rect", id: cat.id, x: catX, y: catY, width: catWidth, height: catHeight, text: cat.text,
    fillColor: color.fill, strokeColor: color.stroke
  });
  // Branch bone connector
  nodes.push({
    type: "connector",
    connector: { from: { x: cat.spineX, y: spineY }, to: cat.id, toAnchor: isTop ? "bottom" : "top", lineShape: "straight", endArrow: "none", lineColor: color.stroke }
  });

  // Cause bone
  cat.reasons.forEach((reason, rIndex) => {
    // Linear interpolation, evenly distributed along the branch bone
    const t = (rIndex + 1) / (cat.reasons.length + 1);
    const attachX = cat.spineX + branchDX * t;
    const attachY = spineY + (isTop ? -branchDY : branchDY) * t;

    // Key alignment: Ensure the cause box is entirely to the left of the connector, and the Y coordinate center is precisely aligned
    const boxX = attachX - lineLength - reasonWidth;
    const boxY = attachY - reasonHeight / 2;

    const rId = `${cat.id}-r${rIndex}`;
    nodes.push({
      type: "rect", id: rId, x: boxX, y: boxY, width: reasonWidth, height: reasonHeight, text: reason,
      fillColor: color.fill, strokeColor: color.stroke
    });
    // Cause bone connector
    nodes.push({
      type: "connector",
      connector: { from: { x: attachX, y: attachY }, to: rId, toAnchor: "right", lineShape: "straight", endArrow: "none", lineColor: color.stroke }
    });
  });
});

fs.writeFileSync('diagram.json', JSON.stringify({ version: 2, nodes }, null, 2));
```

<a id="连线格式与注意点"></a>
## Connector Format and Notes

All connectors use the `{ "type": "connector", "connector": { ... } }` format.
**Note: Except for the main spine, all other connectors (branch bones, cause bones) must set `"endArrow": "none"`, otherwise they will have arrows by default, causing directional confusion.**

Branch bone: from the absolute coordinate point on the main spine → category label node:

```json
{
  "version": 2,
  "nodes": [
    { "type": "rect", "x": 0, "y": 0, "width": "__totalWidth__", "height": "__totalHeight__" },

    { "type": "ellipse", "id": "head", "x": "__headX__", "y": "__headY__",
      "width": 180, "height": 80, "text": "[中心问题]" },

    { "type": "connector", "connector": {
      "from": { "x": "__spineStartX__", "y": "__spineY__" },
      "to": "head", "toAnchor": "left",
      "lineShape": "straight", "endArrow": "arrow"
    }},

    { "type": "rect", "id": "c0", "x": "__catX__", "y": "__catY__",
      "width": 120, "height": 40, "text": "[分类A]" },
    { "type": "connector", "connector": {
      "from": { "x": "__spineX0__", "y": "__spineY__" },
      "to": "c0", "toAnchor": "bottom",
      "lineShape": "straight", "endArrow": "none"
    }},

    { "type": "rect", "id": "c0-r0", "x": "__reasonX__", "y": "__reasonY__",
      "width": 140, "height": 32, "text": "[原因1]" },
    { "type": "connector", "connector": {
      "from": { "x": "__attachX__", "y": "__attachY__" },
      "to": "c0-r0", "toAnchor": "right",
      "lineShape": "straight", "endArrow": "none"
    }}
  ]
}
```

The above skeleton demonstrates a pattern with one category (above) + one cause. A complete fishbone diagram repeats this pattern, alternating top and bottom. Each category can have multiple causes, evenly interpolated along the branch bone.

<a id="陷阱"></a>
## Pitfalls

- **Code generation**: You must use a script with a dynamic anti-overlap algorithm to calculate coordinates and output JSON.
- **Branch bone anti-overlap**: Adjacent branch bones and cause boxes on the same side must not have any crossing.
- **Adaptive height**: When there are many causes, the branch bone automatically lengthens to accommodate all bones.
- **Cause bone horizontal**: The attachment point on the right side of the cause box must have the same Y coordinate as the connector start point.
- **No arrows**: All category branch connectors and bone connectors must have arrows disabled.
- **Same color scheme**: The same branch bone, category label node, cause bone nodes, and connectors must use the same color scheme to maintain visual coherence.
