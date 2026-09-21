<a id="金字塔图-pyramid"></a>
# Pyramid

<a id="content-约束"></a>
## Content constraints

- 3-6 levels, with width decreasing from bottom to top
- One short label per level (such as a keyword or phrase)
- Place long copy outside next to the pyramid; keep only the core short copy inside the shape

<a id="layout-选型"></a>
## Layout selection

vertical frame + decreasing width per level. Keep gap at 4px for tightness.

<a id="layout-规则"></a>
## Layout rules

- The outer frame uses `layout: "vertical"` + `alignItems: "center"`
- All levels must use a script to calculate width, to guarantee **absolutely perfect equal slope (straight edges)**. Never hand-write guessed widths!
- In the children array, the first element is the top level (narrowest), and the last is the bottom level (widest).
- The top level usually uses `triangle` (`topWidth: 0`), while the middle and bottom levels use `trapezoid`.
- gap is usually set to 4px to maintain a tight pyramid feel.

> **Strict slope algorithm (must be implemented in the script)**:
> To make the sides of the pyramid form a perfect straight line, **the width increment must be strictly tied to the height and gap**.
> 1. Set the overall width expansion coefficient `angleK` (recommended value 1.5 to 2.5, meaning the number of pixels the total width increases for each 1px increase in height).
> 2. Formula for the bottom width of the current level: `width = topWidth + (height * angleK)`
> 3. Formula for the top width of the next level (must account for the extra outward expansion caused by gap): `nextTopWidth = width + (gap * angleK)`

<a id="脚本构建模板"></a>
## Script construction template

You must use `node` to run the script and generate JSON.

```javascript
const fs = require('fs');

// 1. Configure basic parameters
const GAP = 4;
const ANGLE_K = 2; // Slope coefficient: for each 1px increase in height, width increases by 2px
const LAYER_HEIGHT = 80;

const data = [
  { text: "顶层核心", fillColor: "#1F2329", textColor: "#FFFFFF" },
  { text: "中间层 B", fillColor: "#DFF5E5", textColor: "#1F2329" },
  { text: "中间层 A", fillColor: "#EAE2FE", textColor: "#1F2329" },
  { text: "最底层基础", fillColor: "#F0F4FC", textColor: "#1F2329" }
];

let currentTopWidth = 0; // If the top level is a pointed tip, initialize it to 0
const children = data.map((layer, index) => {
  // 2. Calculate the bottom width of the current level according to the formula
  const currentBottomWidth = currentTopWidth + (LAYER_HEIGHT * ANGLE_K);
  
  const node = {
    type: currentTopWidth === 0 ? "triangle" : "trapezoid",
    width: currentBottomWidth,
    topWidth: currentTopWidth,
    height: LAYER_HEIGHT,
    text: layer.text,
    textAlign: "center",
    fillColor: layer.fillColor,
    borderColor: layer.fillColor,
    borderWidth: 2,
    fontSize: 16,
    textColor: layer.textColor
  };

  // 3. Key point: calculate the top width of the next level. The gap extension must also be included!
  currentTopWidth = currentBottomWidth + (GAP * ANGLE_K);
  
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

- **Do not hand-write arbitrarily increasing widths**: this will make the pyramid sides become a polyline instead of straight. You must strictly use the above `angleK` formula for calculation.
- **Forgetting to account for the expansion caused by gap**: if the next level's `topWidth` is simply equal to the previous level's `width`, then when there is a gap, the junction will produce a jagged corner. You must add `gap * angleK`.
- **Incorrect ordering from top to bottom**: the first item in the children array is the top level (narrowest), and the last is the bottom level (widest), with widths increasing in order.
- **Text overflowing the top triangle**: the usable space inside the top triangle is extremely small. For short copy, use `\n` for manual line breaks; place long copy outside next to the pyramid (wrap the outer layer in a horizontal frame, with the pyramid on the left and explanatory text on the right)
- **Misuse of inverted pyramid**: if the user requests an "inverted pyramid", "funnel chart", or "top-down decreasing structure", **do not** use this file; switch to `scenes/funnel.md`

<a id="扩展"></a>
## Extensions

- **Supplementary explanation**: when text explanation needs to be added beside it, wrap the outermost layer in a `layout: "horizontal"` frame, place the pyramid on the left, and place the explanatory text (vertical text nodes) on the right
- **Color scheme**: each level's color should use different colors selected from the palette to distinguish them (such as a progression from blue → purple → green → yellow)
