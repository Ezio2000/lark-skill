<a id="lark-doc-画板处理指南"></a>
# lark-doc Whiteboard Handling Guide

<a id="两个-skill-的职责边界"></a>
## Responsibility Boundaries of the Two Skills

| Skill             | Core Responsibility                                                      | Constraint                              |
|-------------------|-----------------------------------------------------------|---------------------------------|
| `lark-doc`        | Identify whiteboard opportunities, use Mermaid/SVG to create diagrams, schedule SubAgent, insert simple diagrams or complex blank whiteboards | Simple diagrams can be written directly by the main Agent; complex diagrams are isolated to a SubAgent |
| `lark-whiteboard` | Query/export existing whiteboards; complex diagram generation (Mermaid/DSL/SVG routing, scenario selection, rendering validation); write to existing/blank whiteboards  | Only read by an independent SubAgent for particularly complex diagrams or updates to existing whiteboards |

<a id="画板适用规则"></a>
## Whiteboard Applicability Rules

When writing documents, content such as core processes, system architecture, solution comparisons, risk chains, milestones, metric trends, causal attribution, organizational relationships, and capability layering can be planned as whiteboards if diagrams can significantly reduce comprehension cost; content with simple structure or that is clearer as text need not be forcibly turned into a whiteboard.

A single document can have multiple whiteboards. When there are indeed multiple independent diagram points, they can be split into multiple focused whiteboards rather than cramming all information into one large diagram.

<a id="文档与画板协同流程"></a>
## Document and Whiteboard Collaboration Flow

<a id="步骤-1识别画板机会"></a>
### Step 1: Identify Whiteboard Opportunities

| Scenario                      | Entry                                                        |
|-------------------------|-----------------------------------------------------------|
| Document needs mind map, sequence diagram, class diagram, pie chart, Gantt chart | Step 2A: Use mermaid to insert diagram                                     |
| Document needs to insert other diagrams/custom graphics       | Step 2B: Use SVG to insert diagram                                        |
| Existing whiteboard needs content update              | First use `docs +fetch` to get `board_token`, skip to Step 3B |
| Only view / download existing whiteboard            | Switch to `lark-whiteboard`, do not follow this flow                               |

> [!IMPORTANT]
> ⚠️ **Decide separately for each diagram**

If there are multiple positions where diagrams need to be inserted, you need to **decide separately** for each diagram's content whether to use Step 2A or 2B. Mind maps, sequence diagrams, class diagrams, pie charts, and Gantt charts can be inserted as mermaid blocks; other types of diagrams use SVG, with simple diagrams written directly by the main Agent and complex diagrams handled by launching a SubAgent.

Simple Mermaid / SVG diagrams can be written directly into local XML by the main Agent; SVGs that require specialized visual design, have high information density, or are prone to layout failures should launch a SubAgent to produce the complete fragment.

<a id="步骤-2a-使用-mermaid-插入图表"></a>
### Step 2A: Use mermaid to insert diagram

```xml

<whiteboard type="mermaid">
    mermaid 代码...
</whiteboard>
```

If the Mermaid is already in a local file, it can be written as `<whiteboard type="mermaid" path="@./diagram.mmd"></whiteboard>`; the CLI will read the file and expand it into inline content before writing.

<a id="步骤-2b-subagent-使用-svg-插入图表"></a>
### Step 2B: SubAgent uses SVG to insert diagram

The main Agent launches a SubAgent, letting it use `docs +create` / `docs +update` to insert:

```xml

<whiteboard type="svg">
    <svg...>...
    </svg>
</whiteboard>
```

If the SVG is already in a local file, it can be written as `<whiteboard type="svg" path="@./diagram.svg"></whiteboard>`; PlantUML files likewise use `<whiteboard type="plantuml" path="@./sequence.puml"></whiteboard>`.

The Sub Agent needs to carry the following minimal context, as well as the subsequent [SVG Design Workflow] section guide:

- doc token, insertion position (heading / block_id / command)
- Diagram goal, audience, source paragraph or data
- Required to read `lark-doc-xml.md`; no need to read `lark-whiteboard`
- SVG must be fully self-contained: include the `<svg>` root node and `viewBox`, without referencing external images, scripts, or remote resources

<a id="画板-svg-设计指南"></a>
#### Whiteboard SVG Design Guide

When using SVG to insert a whiteboard, the final deliverable is **the nodes of the whiteboard after re-layout rendering** (you write SVG → whiteboard parses)
**Core mindset correction (important)**:

- Most AI, if only considering "absolutely no errors / perfect mapping", will ultimately produce a rigid card grid with an all-white background and a single layer of `<rect>`, extremely stiff and monotonous, *
  *this will be considered a failure!**
- **SVG gives you complete design freedom**, please boldly use the icon paths in your mind (`<path>`), connection guides (`流畅的 <path>`), various environmental atmosphere embellishments,
  be bold, fully trust your taste, and unleash your top-tier artistic creativity!

<a id="svg-设计-workflow"></a>
##### SVG Design Workflow

<a id="1-想清楚要画什么"></a>
###### 1. Think clearly about what to draw

- **What is the core information?** Achieve the effect of one image being worth a thousand words; absolutely do not just generate a mediocre text table, it must have a sense of design
- **Content richness**: If the user's description is sparse and brief, use your domain knowledge to expand, ensuring information dimensions and content richness, but do not over-pile, drowning out the key points
- **Visual hierarchy and metaphor**: There is no fixed form for this; you judge freely, for example: add halos to important nodes, add highlighted backgrounds; design scales or symmetrical structures for comparison items

<a id="2-写-svg"></a>
###### 2. Write SVG

> [!IMPORTANT]
> Layout, color scheme, information density, decorations——**all judged by you**, break out of the monotonous `<rect>` cage, strictly forbidden to use rectangles and text throughout to deal with the user
> Operational boundary constraints:

- **Language follows the user**: The language of the diagram text stays consistent with the user's prompt; technical terms use industry-standard conventions, not mechanical translation
- Text uses `<text>` (not `<path>`), leave enough container width——the whiteboard re-layouts at CJK ≈ 1em / Latin ≈ 0.6em
- Connections use orthogonal polylines instead of diagonal straight lines (`<polyline>` with horizontal/vertical breakpoints) for better visual effect
- You may freely use `translate`, `rotate`, `scale` but please try to avoid using `skewX` / `skewY` / `matrix(...)` which cause spatial distortion

<a id="画板怎么处理-svg"></a>
###### How the Whiteboard Handles SVG

The whiteboard's svg-parser converts recognizable elements into editable nodes, and the rest are downgraded to embedded images (rendering is fine, and although not editable, they can display normally); but decorative features such as `<filter>` / `<pattern>` / `<clipPath>` / `<mask>` not used for shadows are not supported by the whiteboard (see ⚠️ below)
**Not all elements need to be editable, but you must avoid using unsupported decorative features, and balance editability with aesthetics**

**Recognizable elements**

- Shapes: `<rect>` / `<circle>` / `<ellipse>` / `<polygon>`
- Connections: `<line>` / `<polyline>` / `<path>` (automatically recognized as straight lines / polylines / curves)
- Text: `<text>` / `<tspan>` whiteboard hardcodes Noto Sans SC **text must use `<text>`**
- Grouping: `<g>` / `<a>` / `<use>` referencing `<symbol>`
- Transforms: `translate` / `rotate` / `scale` normal; `skewX` / `skewY` / `matrix(...)` downgraded
- Shadows: placing `<feDropShadow>` inside `<filter>` or a standard drop/inner primitive chain (`<feGaussianBlur in="SourceAlpha">` + `<feOffset>` + `<feFlood>` + `<feComposite>` + `<feMerge>`) will be recognized as node shadows, at most 1 drop, at most 1 inner; other filter effects are not recognized
- Gradients: `<linearGradient>` / `<radialGradient>` defined in `<defs>`, referenced via `fill="url(#id)"` (carriers limited to `<rect>` / `<circle>` / `<ellipse>` / `<polygon>` / `<path>`), requiring at least 2 `<stop>`, `gradientUnits` only supports the default `objectBoundingBox` (just omit it)

> [!IMPORTANT]
> ⚠️ **Unsupported decorative features**

- `<pattern>` / `<clipPath>` / `<mask>` / `<filter>` not used for shadows (blur / hue-rotate / composite blending / `flood-color=url(...)` / multiple `<feDropShadow>`, etc.) → not supported by the whiteboard, **please avoid using them, otherwise it will cause whiteboard rendering issues**
- Gradient boundaries: `gradientUnits="userSpaceOnUse"` / `spreadMethod="reflect|repeat"` / fewer than 2 stops / complex `gradientTransform` will become non-editable images, visually correct but losing editability; if unnecessary, please use the default `objectBoundingBox`

<a id="3插入后审查"></a>
###### 3. Review after insertion

After inserting the whiteboard, you can use the lark-cli command from the return value to export the whiteboard content as a png
image. If you are dissatisfied with the design, you can modify it and then delete the original whiteboard and re-insert it, or call [
`../../whiteboard/index.md`](../../whiteboard/index.md) to edit.

```bash
lark-cli whiteboard +export \
  --whiteboard-token "wbcnxxxxxxxx" \
  --output-type preview \
  --output ./preview.png
```

<a id="步骤-3b编辑已有画板--启动-lark-whiteboard-subagent"></a>
### Step 3B: Edit existing whiteboard — launch lark-whiteboard SubAgent

Complex diagrams and updates to existing whiteboards must launch a SubAgent. The main Agent only passes minimal context and does not directly execute the rendering and writing flow of `lark-whiteboard`.

Minimal context for the complex diagram SubAgent:

- board_token
- Diagram goal, recommended whiteboard type, audience
- Source paragraph or data directly related to the diagram
- Required to read [`../../whiteboard/index.md`](../../whiteboard/index.md), and write to that board_token following its complete flow

When multiple whiteboards are independent of each other, multiple SubAgents can be launched in parallel; each SubAgent is responsible for only one whiteboard or one SVG insertion point, and contexts must not be reused between them.

<a id="步骤-4完成校验"></a>
### Step 4: Completion validation

- Mermaid: Confirm that what was inserted is `<whiteboard type="mermaid">`, and that the content's mermaid syntax is complete
- SVG: Confirm that what was inserted is `<whiteboard type="svg">`, and that the content is a complete `<svg ...>...</svg>`
- Do not keep blank placeholder whiteboards; a complex path with only a blank whiteboard and no content is considered an incomplete task

---

---

<a id="关联参考"></a>
## Related References

- Whiteboard query/creation/modification/rendering write: [`../../whiteboard/index.md`](../../whiteboard/index.md)
