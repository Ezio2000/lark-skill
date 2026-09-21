<a id="漏斗图-funnel"></a>
# Funnel Chart (Funnel)

<a id="content-约束"></a>
## Content Constraints

- 3-6 stages
- One line of label + value per stage (e.g. "{{STAGE_NAME}} ({{PERCENTAGE}})")
- Keep copy as short as possible; move long copy outside next to the funnel, keeping only the core short copy inside the shape

<a id="layout-选型"></a>
## Layout Selection

Absolute positioning. Use `trapezoid` / `triangle` nodes arranged from wide to narrow, with height using `fit-content`.

<a id="layout-规则"></a>
## Layout Rules

- The outer frame uses `layout: "vertical"` + `alignItems: "center"` for center alignment
- All layers must use script-calculated widths to guarantee **absolutely perfect equal slope (straight edges)**. Never hand-write guessed widths!
- Gap between layers 0-8px (tight stacking looks better), width decreasing from top to bottom. Note that the first element of the children array is the topmost (widest) layer
- All shape nodes must set `"vFlip": false` (the engine flips upward by default, but the funnel needs to face downward)
- Note: because `vFlip: false` and it is an inverted pyramid structure, `topWidth` actually controls the **narrower bottom edge** of each funnel layer. The bottom layer can use `triangle` (`topWidth: 0`) to narrow into a point, or continue using `trapezoid` to keep a flat bottom.

> **Strict slope algorithm (must be implemented in the script)**:
> To make the sides of the funnel form a perfect straight line, **the width decrement must be strictly tied to height and gap**.
> 1. Set the overall width shrink coefficient `angleK` (recommended value 1.5 to 2.5, meaning for every 1px increase in height, the total width decreases by that many pixels).
> 2. Because it narrows from top to bottom, the formula is subtraction: `bottomWidth(即 topWidth 属性) = currentWidth - (height * angleK)`
> 3. Formula for the top width of the next layer (must account for the extra inward contraction caused by the gap): `nextLayerWidth = bottomWidth - (gap * angleK)`

<a id="脚本构建模板"></a>
## Script Construction Template

This scene must be generated with a .cjs script.

```javascript
const fs = require('fs');

// 1. Configure basic parameters
const GAP = 4;
const ANGLE_K = 2; // Slope coefficient: for every 1px drop in height, width decreases by 2px
const LAYER_HEIGHT = 80;

const data = [
  { text: "展现 (100%)", fillColor: "#F0F4FC", textColor: "#1F2329" },
  { text: "点击 (50%)", fillColor: "#EAE2FE", textColor: "#1F2329" },
  { text: "加购 (20%)", fillColor: "#DFF5E5", textColor: "#1F2329" },
  { text: "成交 (5%)", fillColor: "#1F2329", textColor: "#FFFFFF" }
];

// Calculate the initial width of the first layer (ensure the bottom layer narrows to 0 or a flat bottom)
// Reverse formula: startWidth = bottom width of the last layer + all height consumption + all gap consumption
const totalHeightLoss = data.length * LAYER_HEIGHT * ANGLE_K;
const totalGapLoss = (data.length - 1) * GAP * ANGLE_K;
// Set the bottom layer as a point (bottom width is 0)
let currentWidth = 0 + totalHeightLoss + totalGapLoss;

const children = data.map((layer, index) => {
  // 2. Calculate the bottom width of the current layer according to the formula (corresponds to the node's topWidth property)
  const currentBottomWidth = currentWidth - (LAYER_HEIGHT * ANGLE_K);
  
  const node = {
    type: currentBottomWidth <= 0 ? "triangle" : "trapezoid",
    width: currentWidth,
    // Note: in a funnel, topWidth represents the narrower edge below! If <=0, use triangle
    topWidth: Math.max(0, currentBottomWidth), 
    height: LAYER_HEIGHT,
    vFlip: false, // Must be false
    text: layer.text,
    textAlign: "center",
    fillColor: layer.fillColor,
    borderColor: layer.fillColor,
    borderWidth: 2,
    fontSize: 16,
    textColor: layer.textColor
  };

  // 3. Key: calculate the top width of the next layer. Must subtract the inward contraction of the gap!
  currentWidth = currentBottomWidth - (GAP * ANGLE_K);
  
  return node;
});

const output = {
  version: 2,
  nodes: [
    {
      type: "frame",
      layout: "vertical",
      alignItems: "center",
      gap: GAP,
      padding: 40,
      children: children
    }
  ]
};

fs.writeFileSync('diagram.json', JSON.stringify(output, null, 2));
```

<a id="陷阱"></a>
## Pitfalls

- **Do not hand-write arbitrarily decreasing widths**: this will make the funnel sides become a polyline, not straight. You must strictly use the above `angleK` formula for calculation.
- **Forgetting to account for the contraction caused by the gap**: if the next layer's `width` is simply equal to the previous layer's `topWidth`, then when there is a gap, the junction will produce a jagged corner. You must subtract `gap * angleK`.
- **vFlip not set**: forgetting `"vFlip": false` will cause the trapezoid to flip upward, resulting in a wrong funnel shape
- **Text overflowing the bottom layer**: the narrower the bottom layer, the less space there is; use `\n` for line breaks with short copy, and move long copy outside next to the funnel (wrap the outer layer in a `layout: "horizontal"` frame, with the funnel on one side and the explanatory text on the other)
