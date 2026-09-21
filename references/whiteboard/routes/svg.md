<a id="svg-路径"></a>
# SVG Paths

You are designing a professional infographic—substantive in content, beautiful and attractive, with a sense of design and visual tension, not a dull layout and pile of text. **Do not make it look like an ordinary web page or a cookie-cutter template.**
The final deliverable is **a whiteboard node that spans re-layout rendering** (you write SVG → the whiteboard parses it)

**Core mindset correction (important)**:

- If most AI only consider "absolutely no errors / perfect mapping," the final result is all plain white backgrounds with a single layer of `<rect>` in a rigid card grid—extremely stiff and monotonous. **This will be considered a failing grade!**
- **SVG gives you complete design freedom.** Boldly use the icon paths in your mind (`<path>`), connecting guides (`流畅的 <path>`), and various ambient embellishments. Be bold, fully trust your taste, and unleash your top-tier artistic creativity!

## Workflow

<a id="1-想清楚要画什么"></a>
### 1. Think clearly about what to draw

- **What is the core message?** Aim to make one image worth a thousand words. Absolutely do not just generate a bland text table—have a sense of design.
- **Content richness**: If the user's description is sparse and brief, use your domain knowledge to expand it, ensuring information dimensions and content richness, but do not over-pile so as to drown out the key points.
- **Visual hierarchy and metaphor**: There is no fixed form for this; judge freely. For example: add a halo or highlighted background to important nodes; design a balance scale or symmetrical structure for comparison items.

<a id="2-写-svg"></a>
### 2. Write SVG

[!IMPORTANT] Layout, color scheme, information density, decorations—**all judged by you**. Break out of the monotonous `<rect>` cage. It is strictly forbidden to fob off the user with rectangles and text throughout.

Operational boundary constraints:

- **Language follows the user**: The language of the diagram text must match the user's prompt. Use industry-standard wording for technical terms; do not mechanically translate.
- Use `<text>` for text (not `<path>`), and leave enough container width—the whiteboard re-layouts at CJK ≈ 1em / Latin ≈ 0.6em.
- Use orthogonal polylines instead of diagonal straight lines for connections (`<polyline>` with horizontal/vertical bend points) for better visual effect.
- You may freely use `translate`, `rotate`, `scale`, but please try to avoid using `skewX` / `skewY` / `matrix(...)` to cause spatial distortion.

<a id="3-渲染审查"></a>
### 3. Render review

```
Create directory   ./diagrams/YYYY-MM-DDTHHMMSS/         (example: ./diagrams/2026-04-15T143022/)
Write file   <dir>/diagram.svg
Render     npx -y @larksuite/whiteboard-cli@^0.2.13 -i <dir>/diagram.svg -o <dir>/diagram.png -f svg
Check     npx -y @larksuite/whiteboard-cli@^0.2.13 -i <dir>/diagram.svg -f svg --check
Export     npx -y @larksuite/whiteboard-cli@^0.2.13 -i <dir>/diagram.svg -f svg --to openapi --format json > <dir>/diagram.json
```

`npx -y @larksuite/whiteboard-cli@^0.2.13 --check` detects `text-overflow` and `node-overlap`, and adjusts based on visual effect (view the PNG)

<a id="画板怎么处理-svg"></a>
## How the whiteboard handles SVG

The whiteboard's svg-parser converts recognizable elements into editable nodes, and degrades the rest into embedded images (rendering is fine; although not editable, they display normally); however, decorative features such as `<filter>` / `<clipPath>` not used for shadows are not supported by the whiteboard (see ⚠️ below)
**Not all elements need to be editable, but you must avoid using unsupported decorative features, and balance editability with beauty.**

**Recognizable elements**

- Shapes: `<rect>` / `<circle>` / `<ellipse>` / `<polygon>`
- Connections: `<line>` / `<polyline>` / `<path>` (automatically recognized as straight lines / polylines / curves)
- Text: `<text>` / `<tspan>` The whiteboard hardcodes Noto Sans SC. **Text must use `<text>`**
- Grouping: `<g>` / `<a>` / `<use>` referencing `<symbol>`
- Transforms: `translate` / `rotate` / `scale` work normally; `skewX` / `skewY` / `matrix(...)` are degraded
- Shadows: placing `<feDropShadow>` or a standard drop/inner primitive chain (`<feGaussianBlur in="SourceAlpha">` + `<feOffset>` + `<feFlood>` + `<feComposite>` + `<feMerge>`) inside `<filter>` will be recognized as node shadows; at most 1 drop and at most 1 inner; other filter effects are not recognized
- Gradients: `<linearGradient>` / `<radialGradient>` defined in `<defs>` and referenced via `fill="url(#id)"` (carriers limited to `<rect>` / `<circle>` / `<ellipse>` / `<polygon>` / `<path>`); at least 2 `<stop>` are required; `gradientUnits` only supports the default `objectBoundingBox` (just omit it);

> [!IMPORTANT]
> ⚠️ **Unsupported decorative features**

- `<pattern>` / `<clipPath>` / `<mask>` / `<filter>` not used for shadows (blur / hue-rotate / composite blending / `flood-color=url(...)` / multiple `<feDropShadow>`, etc.) → not supported by the whiteboard. **Please avoid using them, otherwise they will cause whiteboard rendering problems.**
- Gradient boundaries: `gradientUnits="userSpaceOnUse"` / `spreadMethod="reflect|repeat"` / fewer than 2 stops / complex `gradientTransform` will become non-editable images—visually correct but losing editability. If unnecessary, please stick with the default `objectBoundingBox`.
