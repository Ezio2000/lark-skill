<a id="dsl-路径"></a>
# DSL Path

> **This is a whiteboard, not a webpage.** A whiteboard is about freely placing elements on an infinite canvas; flex layout is an optional enhancement.

## Workflow

```
Step 1: Route & read knowledge
  - Read the corresponding scene guide — understand structural characteristics and layout strategy
  - Determine the layout strategy (see quick judgment below) and the construction method
  - Read the core modules under elements/ — syntax, layout, color scheme, typography, connectors

Step 2: Generate the complete DSL (including colors)
  - Plan the amount of information and grouping according to content.md
  - Choose the layout mode and spacing according to layout.md
  - It is recommended to use icons to make the diagram more intuitive; run `npx -y @larksuite/whiteboard-cli@^0.2.13 --icons` to view available icons
  - Apply colors according to style.md (use the default classic palette when the user has not specified one)
  - Output the complete JSON according to the syntax in schema.md
  - For connectors refer to connectors.md; for typography refer to typography.md

  Note: Some graphics (fishbone/flywheel/bar/line, etc.) require writing a CommonJS script to generate JSON according to the script template in the scene guide:
    1. Create the artifact directory ./diagrams/YYYY-MM-DDTHHMMSS/
    2. Save the script as diagram.gen.cjs (the .cjs suffix is required; write the script using require(), as .js will crash under an ESM project), and run node diagram.gen.cjs to produce diagram.json
    3. Use the produced diagram.json to proceed to Step 3

Step 3: Render & review → deliver
  - Self-check before rendering (see checklist below)
  - Render PNG (for preview verification only, not the final artifact): npx -y @larksuite/whiteboard-cli@^0.2.13 -i diagram.json -o diagram.png
  - Check: Is the information complete? Is the layout reasonable? Is the color scheme harmonious? Is any text truncated? Do any connectors cross?
  - If there are problems → fix according to the symptom table → re-render (at most 2 rounds)
  - If serious problems remain after 2 rounds → consider falling back to the Mermaid path
  - Write to the whiteboard: use whiteboard-cli to convert diagram.json to OpenAPI format and pipe it to +update:
      npx -y @larksuite/whiteboard-cli@^0.2.13 -i diagram.json --to openapi --format json \
        | lark-cli whiteboard +update --whiteboard-token <board_token> \
            --source - --input_format raw --idempotent-token <时间戳+标识> --as user
      → For the complete dry-run / confirmation flow, see [§ Write to whiteboard](../references/lark-whiteboard-workflow.md#写入画板)
  - Deliver: report to the user that the board_token was written successfully
```

**Quick judgment of layout strategy** (see `elements/layout.md` for details):

First determine the **primary layout**, then the sub-layout: for **structured information** prefer Flex, for **relationship chains** prefer Dagre, and for **flexible positioning** use absolute layout.

> **The construction method is a hard constraint**: when the scene guide requires "script generation", you must first write a script (`.cjs`, CommonJS) and execute it with `node` to produce the JSON file.

<a id="模块索引"></a>
## Module Index

<a id="核心参考必读"></a>
### Core References (required reading)

| Module          | File                         | Description                            |
| --------------- |----------------------------| ------------------------------- |
| DSL Syntax      | `elements/schema.md`       | Node types, properties, size values          |
| Content Planning| `elements/content.md`    | Information extraction, density decisions, connector pre-judgment    |
| Layout System   | `elements/layout.md`     | Grid methodology, Flex mapping, spacing rules |
| Typography Rules| `elements/typography.md` | Font size hierarchy, alignment, line spacing            |
| Connector System| `elements/connectors.md` | Topology planning, anchor selection              |
| Color System    | `elements/style.md`      | Multiple palettes, visual hierarchy                |

<a id="场景指南按类型选读一个"></a>
### Scene Guides (choose one to read by type)

| Diagram Type    | File                     | Applicable Scenarios                               |
| ----------- | ------------------------ | -------------------------------------- |
| Architecture Diagram      | `scenes/architecture.md` | Layered architecture, microservice architecture                   |
| Organization Chart  | `scenes/organization.md` | Company organization, tree hierarchy                     |
| Swimlane Diagram      | `scenes/swimlane.md`     | Cross-role processes, cross-system interaction processes             |
| Comparison Diagram      | `scenes/comparison.md`   | Solution comparison, feature matrix                     |
| Fishbone Diagram      | `scenes/fishbone.md`     | Causal analysis, root cause analysis                     |
| Bar Chart      | `scenes/bar-chart.md`    | Bar chart, horizontal bar chart                         |
| Line Chart      | `scenes/line-chart.md`   | Line chart, trend chart                         |
| Treemap      | `scenes/treemap.md`      | Rectangular treemap, hierarchical proportion                     |
| Funnel Chart      | `scenes/funnel.md`       | Conversion funnel, sales funnel                     |
| Pyramid Chart    | `scenes/pyramid.md`      | Hierarchical structure, hierarchy of needs                     |
| Cycle/Flywheel Diagram | `scenes/flywheel.md`     | Growth flywheel, closed-loop chain                     |
| Milestone      | `scenes/milestone.md`    | Timeline, version evolution                       |
| Flowchart      | `scenes/flowchart.md`    | Business flow, state machine, chains with conditional judgment       |

<a id="插入-用户提及--图片"></a>
### Insert @user mentions / images

| Current content contains | Required reading |
|---|---|
| @user mention | [`../scenes/mention.md`](../scenes/mention.md) |
| Image / illustration | [`../scenes/photo-showcase.md`](../scenes/photo-showcase.md) |

<a id="渲染前自查"></a>
## Self-check before rendering

- [ ] Do different groups use different colors? Are nodes in the same group completely consistent in style?
- [ ] Outer layer with light background, inner layer with white nodes?
- [ ] Do all nodes have borders (borderWidth=2)? Is the text clearly readable on the background?
- [ ] Do connectors use gray (#BBBFC4) rather than color?
- [ ] Do all frames have the layout property written? Are gap and padding both explicitly set?
- [ ] Do nodes containing text use fit-content for height? Are connectors in the top-level nodes array?

<a id="症状修复表"></a>
## Symptom → Fix Table

| Problem observed         | What to change                              |
| ------------------ | ----------------------------------- |
| Text is truncated         | Change height to fit-content             |
| Text overflows the right side of the container   | Increase width, or shorten the text              |
| Nodes overlap and stick together       | Increase gap                            |
| Nodes are crammed together       | Increase padding and gap                 |
| Connectors pass through nodes       | Adjust fromAnchor/toAnchor or increase spacing |
| Large blank areas         | Reduce the outer frame width                 |
| Text and background color are too close | Adjust fillColor or textColor         |
| The layout as a whole leans left/right  | Adjust the x coordinate of absolute positioning to center the content     |

<a id="关键约束速查"></a>
## Key Constraints Quick Reference

1. **The height of nodes containing text must use `'fit-content'`** — hardcoding a numeric value will truncate the text
2. **`fill-container` only takes effect in a flex parent container** — under `layout: 'none'`, the width degenerates to 0
3. **The container of `layout: 'none'` must have fixed width and height** — do not write it as `fit-content`
4. **connector must be placed in the top-level nodes array** — it cannot be nested inside frame children
5. **x/y inside a flex container are completely ignored** — use `layout: 'none'` when free positioning is needed
6. **Dagre sub-containers are opaque nodes by default** — declare `layout: "dagre"` + `layoutOptions: { isCluster: true }` when pass-through is needed
