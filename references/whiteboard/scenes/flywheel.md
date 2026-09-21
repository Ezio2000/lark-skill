<a id="增长飞轮图-flywheel"></a>
# Growth Flywheel Diagram (Flywheel)

> **You must write a script to generate the JSON.** The flywheel diagram requires polar coordinate calculation of stage label positions and SVG ring cutting; directly hand-writing JSON cannot correctly implement the concentric ring structure. Please use the script template below.

<a id="content-约束"></a>
## Content Constraints

- 4-6 stages, each with a short label (title + optional subtitle/desc)
- Place the flywheel theme title in the center

<a id="layout-选型"></a>
## Layout Selection

- **Script-generated coordinates** (required): Use a .cjs script to calculate stage label positions via polar coordinates and SVG ring cutting; the script outputs a JSON file, then call `npx -y @larksuite/whiteboard-cli@^0.2.13` to render

<a id="layout-规则"></a>
## Layout Rules

- Build the ring using the concentric circle masking method: large circle (base color) + small circle (white mask) + center text
- The order of the nodes array determines z-index: large circle first -> small circle -> center text -> SVG cuts -> outer cards
- Stage labels are evenly distributed around the outside of the ring, with each label at an equal distance from the circle center
- SVG polyline cuts the ring to form segments + a sense of arrow direction
- When there are many stages, dynamically enlarge the radius, reduce the arrow bend angle, and tighten the text containers

<a id="同心圆遮挡法详解"></a>
### Detailed Explanation of the Concentric Circle Masking Method

Draw a large circle (as the base color of the flywheel), then draw a small circle at its exact center (filled with white `#FFFFFF`). Set `borderWidth: 0` on both the large and small circles, forming a ring through overlay masking.

Layer order in the nodes array (must be strictly followed):

1. **Bottom large circle** (`type: 'ellipse'`, filled, `borderWidth: 0`)
2. **Masking small circle** (`type: 'ellipse'`, white fill, `borderWidth: 0`)
3. **Center text** — must be added after the two circles, otherwise it will be covered by the white small circle
4. **SVG cutting arrows** — overlaid on the ring, using white thick polyline to cut out segments
5. **Outer stage cards** — positions calculated via polar coordinates

<a id="svg-箭头线切割分段"></a>
### SVG Arrow Line Cutting Segments

By inserting a `svg` node that covers the large circle area, use polar coordinates to calculate the coordinates of each segment boundary, and use `<polyline>` to draw thick lines of the same color as the background (white, 20px+ width). The lines pass from the inner circle edge through the large circle edge, and produce a certain angle of deflection when passing through (`da` parameter), visually "cutting" the ring and creating a sense of arrow direction.

<a id="外围文字环绕布局"></a>
### Outer Text Surrounding Layout

- Use polar coordinates `x = cx + R * cos(θ)` to calculate the center angle of each segment
- Place a `frame` container at the calculated coordinate point (`layout: 'vertical'`)
- The `text` node inside the outer text container cannot use `width: 'fill-container'`; a fixed width must be specified together with `height: 'fit-content'`

<a id="动态缩放优化阶段数--8-时必须"></a>
### Dynamic Scaling Optimization (required when the number of stages >= 8)

When there are many stages (8, 12, or 16+), you must dynamically adjust:

- **Enlarge the canvas and ring radius**: The more nodes there are, the longer the circumference needed to accommodate the outer text. Appropriately increase `rOut` and `rIn` (for example, with 16 stages, `rOut` can be set to 400+), and scale up `cx`/`cy` accordingly to avoid exceeding the boundaries
- **Reduce the arrow cutting angle**: As the number of segments increases, the angle of each segment becomes smaller; keeping the default bend angle will cause gaps that are too large. Reduce `da` (for example, `da = 4`)
- **Tighten the outer text containers**: Narrow `boxWidth`, reduce the font size, and ensure adjacent text boxes do not overlap each other

<a id="骨架示例"></a>
## Skeleton Example

This scene must be generated with a .cjs script. When using it, the Agent only needs to modify the `stages` array and `centerTitle`/`centerSubtitle`; all other coordinates are calculated automatically.

```javascript
const { writeFileSync } = require('fs');

// ══════════════════════════════════════════════════════════════
// Only modify here -- fill in the stage data and center title requested by the user
// ══════════════════════════════════════════════════════════════

const centerTitle = '{{CENTER_TITLE}}';
const centerSubtitle = '{{CENTER_SUBTITLE}}'; // Optional; leave as an empty string if not needed

const stages = [
  { title: '{{STAGE_1}}', subtitle: '{{SUB_1}}', desc: '{{DESC_1}}' },
  { title: '{{STAGE_2}}', subtitle: '{{SUB_2}}', desc: '{{DESC_2}}' },
  { title: '{{STAGE_3}}', subtitle: '{{SUB_3}}', desc: '{{DESC_3}}' },
  { title: '{{STAGE_4}}', subtitle: '{{SUB_4}}', desc: '{{DESC_4}}' },
];

// ══════════════════════════════════════════════════════════════
// The following is automatic calculation logic and does not need to be modified
// ══════════════════════════════════════════════════════════════

// --- Layout parameters ---
const numSegments = stages.length;
const cx = 600, cy = 450; // Canvas center
const rOut = 240, rIn = 160; // Inner and outer circle radii
const textDist = rOut + 40; // Distance of text from circle center
const boxWidth = 220; // Width of outer text cards
const boxHeight = 80; // Estimated height (used for offset calculation)
const da = 8; // Arrow bend angle

const nodes = [];

// --- Layer 1: Bottom large circle (ring base color) ---
nodes.push({
  type: 'ellipse',
  x: cx - rOut, y: cy - rOut,
  width: rOut * 2, height: rOut * 2,
  borderWidth: 0,
});

// --- Layer 2: Masking small circle (white) ---
nodes.push({
  type: 'ellipse',
  x: cx - rIn, y: cy - rIn,
  width: rIn * 2, height: rIn * 2,
  borderWidth: 0,
});

// --- Layer 3: Center text (must be after the two circles) ---
nodes.push({
  type: 'text',
  x: cx - rIn, y: cy - (centerSubtitle ? 30 : 20),
  width: rIn * 2, height: 'fit-content',
  text: [{ content: centerTitle, bold: true, fontSize: 32 }],
  textAlign: 'center',
});
if (centerSubtitle) {
  nodes.push({
    type: 'text',
    x: cx - rIn, y: cy + 20,
    width: rIn * 2, height: 'fit-content',
    text: [{ content: centerSubtitle, fontSize: 18 }],
    textAlign: 'center',
  });
}

// --- Layer 4: SVG cutting arrows ---
let svg = `<svg viewBox="0 0 ${rOut * 2} ${rOut * 2}" xmlns="http://www.w3.org/2000/svg">`;
for (let i = 0; i < numSegments; i++) {
  const a = -90 + i * (360 / numSegments);
  const rad = (a * Math.PI) / 180;
  const radMid = ((a + da) * Math.PI) / 180;
  const R1 = rIn - 5, R2 = rOut + 5, Rm = (rIn + rOut) / 2;
  const x1 = rOut + R1 * Math.cos(rad), y1 = rOut + R1 * Math.sin(rad);
  const x2 = rOut + Rm * Math.cos(radMid), y2 = rOut + Rm * Math.sin(radMid);
  const x3 = rOut + R2 * Math.cos(rad), y3 = rOut + R2 * Math.sin(rad);
  svg += `<polyline points="${x1},${y1} ${x2},${y2} ${x3},${y3}" stroke="#FFFFFF" stroke-width="20" fill="none" stroke-linejoin="round" stroke-linecap="round" />`;
}
svg += `</svg>`;
nodes.push({
  type: 'svg',
  x: cx - rOut, y: cy - rOut,
  width: rOut * 2, height: rOut * 2,
  svg: { code: svg },
});

// --- Layer 5: Outer stage cards (positions calculated via polar coordinates) ---
for (let i = 0; i < numSegments; i++) {
  const stage = stages[i];
  const a = -90 + (360 / numSegments) / 2 + i * (360 / numSegments);
  const rad = (a * Math.PI) / 180;
  const tx = cx + textDist * Math.cos(rad);
  const ty = cy + textDist * Math.sin(rad);

  // Dynamic offset: push the text box outward according to the angle
  let offsetX = 0, offsetY = 0;
  if (Math.cos(rad) > 0.1) offsetX = 0;
  else if (Math.cos(rad) < -0.1) offsetX = -boxWidth;
  else offsetX = -boxWidth / 2;
  if (Math.sin(rad) > 0.1) offsetY = 0;
  else if (Math.sin(rad) < -0.1) offsetY = -boxHeight;
  else offsetY = -boxHeight / 2;

  const textW = boxWidth - 24; // Card padding 12 * 2
  nodes.push({
    type: 'frame',
    x: tx + offsetX, y: ty + offsetY,
    width: boxWidth, height: 'fit-content',
    layout: 'vertical', gap: 8, padding: 12,
    alignItems: 'start',
    borderWidth: 2, borderRadius: 8,
    children: [
      { type: 'text', width: textW, height: 'fit-content',
        text: [{ content: stage.title, bold: true, fontSize: 18 }], textAlign: 'left' },
      { type: 'text', width: textW, height: 'fit-content',
        text: [{ content: stage.subtitle, fontSize: 14 }], textAlign: 'left' },
      { type: 'text', width: textW, height: 'fit-content',
        text: [{ content: stage.desc, fontSize: 12 }], textAlign: 'left' },
    ],
  });
}

// --- Chart title ---
nodes.push({
  type: 'text',
  x: cx - rOut - 100, y: 30,
  width: (rOut + 100) * 2, height: 'fit-content',
  text: [{ content: centerTitle, bold: true, fontSize: 24 }],
  textAlign: 'center',
});

writeFileSync('diagram.json', JSON.stringify({ version: 2, nodes }, null, 2));
```

<a id="陷阱"></a>
## Pitfalls

- **Center text obscured by SVG**: The center text node must be added after the large and small circles and before the SVG to ensure the correct z-index
- **Missing directional arrows**: The SVG polyline cutting lines must have an angle deflection (da parameter) to create a clockwise/counterclockwise arrow feel
- **Asymmetric label positions**: Outer cards must be evenly distributed using the polar coordinate formula `x = cx + R * cos(θ)`; do not place them manually
- **Outer text container deadlock**: The text node inside the `layout: 'vertical'` frame cannot use `width: 'fill-container'`; a fixed width must be specified
