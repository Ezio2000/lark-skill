<a id="配色系统"></a>
# Color System

<a id="怎么上色最重要"></a>
## How to Apply Colors (Most Important)

Coloring steps:

1. **Identify how many groups are in the diagram** (levels, branches, categories, stages...)
2. **Choose a different color for each group** (pick 2-4 colors from the palette)
3. **Group containers** use light-colored fill — tells the reader "this block is one whole"
4. **Nodes within a group** use white fill + that group's dark borderColor — tells the reader "these belong to this group"

Specific mapping (classic palette):

| Group | Layer container fillColor | Layer container borderColor | Inner node borderColor |
|------|----------------|-------------------|---------------------|
| Group 1 | #F0F4FC (light blue) | #5178C6 | #5178C6 |
| Group 2 | #EAE2FE (light purple) | #8569CB | #8569CB |
| Group 3 | #DFF5E5 (light green) | #509863 | #509863 |
| Group 4 | #FEF1CE (light yellow) | #D4B45B | #D4B45B |
| Group 5 | #FEE3E2 (light red) | #D25D5A | #D25D5A |
| Inner node | #FFFFFF | Follows its group | — |

**How to color each type of diagram**:
- Architecture diagram with 3 layers → one color per layer, layer background uses light fill, nodes within the layer use white + dark border
- Comparison table with 3 columns → one color per column header, data cells in that column use the same color border
- Org chart with 4 departments → one color per department, sub-departments use white + same color border
- Flowchart → start/end nodes use one color, decision nodes use one color, step nodes use white

> [!IMPORTANT]
> **User color preferences take priority.** When the user specifies color values/styles, follow the user's choice. When the user provides only 1-2 color values, derive the complete palette: primary color→light background→dark border→gray-toned connector color.
> When the user has **not specified** colors, you must select colors from the palette table above; do not use self-invented color values not in the table (such as `#E8F3FF`, `#1664FF`, `#14C9C9`, etc., which are not in the palette).

---

<a id="结构规则"></a>
## Structural Rules

<a id="分组--不同层分组必须用不同颜色"></a>
### Grouping — Different layers/groups must use different colors

Choose 2-4 colors, each representing one group. Nodes in the same group must be visually identical (same fillColor, borderColor).

<a id="分层--外重内轻"></a>
### Layering — Heavy outside, light inside

- Outer layer (large sections): light-colored fill background
- Inner layer (specific nodes): white fill + group color border

<a id="清晰"></a>
### Clarity

- All nodes have borders (borderWidth=2)
- Spacing must not stick together (gap >= 8, >= 40 when connectors are present)
- Text must be clearly readable on the background (fontSize >= 14). Text-to-background contrast should be sufficient (refer to WCAG 2.1: at least 4.5:1 for body text, at least 3:1 for headings)
- Do not rely on color alone to distinguish information — also use borders, shapes, or text labels to assist, ensuring users with color vision deficiency can also understand
- Connectors use gray (#BBBFC4), not competing with nodes for attention

<a id="统一参数"></a>
### Unified Parameters

| Parameter | Value | Why |
|------|---|--------|
| borderWidth | 2 | Makes borders clearly visible |
| borderRadius | 8 | Unified rounded corners, neat |
| gap (minimum) | 8 | Elements do not stick together |
| padding (minimum) | 8 | Content does not touch edges |
| gap (when connectors are present) | 40 | Leaves space for arrows |
| fontSize (body) | >= 14 | Readable |
| fontSize (heading) | >= 24 | Eye-catching |
| fontSize (auxiliary) | >= 13 | Easy on the eyes |

---

<a id="色板选择指南"></a>
## Palette Selection Guide

Choose the appropriate palette based on the user's keywords or scenario. When unspecified, use the "Classic" palette by default.

| Palette | Applicable Scenarios | Keywords |
|------|---------|-------|
| Classic | General diagrams, documentation | default, general |
| Business | Reports, enterprise architecture, formal documents | professional, formal, for the boss |
| Tech | Technical architecture, DevOps, monitoring | technical, cool, dark |
| Fresh | Flowcharts, user journeys, tutorials | fresh, natural, relaxed |
| Minimal | Paper illustrations, academic reports | academic, minimal, black and white |

---

<a id="预设色板"></a>
## Preset Palettes

Each palette defines colors for 7 roles. **The connector color is part of the palette**; different palettes have different connector colors.

<a id="经典"></a>
### Classic

| Role | fillColor | borderColor | textColor |
|------|-----------|-------------|-----------|
| Section background | #F0F4FC | #5178C6 | #1F2329 |
| Group heading | #EAE2FE | #8569CB | #1F2329 |
| Content node | #FFFFFF | #5178C6 | #1F2329 |
| Second group | #DFF5E5 | #509863 | #1F2329 |
| Third group | #FEF1CE | #D4B45B | #1F2329 |
| Fourth group | #FEE3E2 | #D25D5A | #1F2329 |
| Emphasis/header | #1F2329 | #1F2329 | #FFFFFF |
| Connector | -- | -- | #BBBFC4 |

<a id="商务"></a>
### Business

| Role | fillColor | borderColor | textColor |
|------|-----------|-------------|-----------|
| Section background | #EDF2F7 | #4A6FA5 | #1A202C |
| Group heading | #D4E0ED | #4A6FA5 | #1A202C |
| Content node | #FFFFFF | #718BAE | #1A202C |
| Second group | #E8EDF3 | #5A7B9A | #1A202C |
| Third group | #F0F0F0 | #8895A7 | #1A202C |
| Emphasis/header | #2D4A7A | #2D4A7A | #FFFFFF |
| Connector | -- | -- | #718BAE |

<a id="科技"></a>
### Tech

| Role | fillColor | borderColor | textColor |
|------|-----------|-------------|-----------|
| Canvas/section background | #0F172A | #1E293B | #E2E8F0 |
| Group heading | #1E293B | #3B82F6 | #E2E8F0 |
| Content node | #1E293B | #334155 | #E2E8F0 |
| Second group | #1E293B | #8B5CF6 | #E2E8F0 |
| Third group | #1E293B | #10B981 | #E2E8F0 |
| Emphasis | #2563EB | #3B82F6 | #FFFFFF |
| Connector | -- | -- | #475569 |

<a id="清新"></a>
### Fresh

| Role | fillColor | borderColor | textColor |
|------|-----------|-------------|-----------|
| Section background | #F0FDF4 | #86EFAC | #14532D |
| Group heading | #DCFCE7 | #4ADE80 | #14532D |
| Content node | #FFFFFF | #86EFAC | #14532D |
| Second group | #ECFDF5 | #6EE7B7 | #14532D |
| Third group | #F0FDFA | #5EEAD4 | #134E4A |
| Emphasis | #16A34A | #16A34A | #FFFFFF |
| Connector | -- | -- | #86EFAC |

<a id="极简"></a>
### Minimal

| Role | fillColor | borderColor | textColor |
|------|-----------|-------------|-----------|
| Section background | #F8F9FA | #DEE2E6 | #212529 |
| Group heading | #E9ECEF | #ADB5BD | #212529 |
| Content node | #FFFFFF | #CED4DA | #212529 |
| Second group | #F1F3F5 | #868E96 | #212529 |
| Third group | #F8F9FA | #ADB5BD | #212529 |
| Emphasis/header | #495057 | #495057 | #FFFFFF |
| Connector | -- | -- | #ADB5BD |

---

<a id="各元素怎么画"></a>
## How to Draw Each Element

> The following examples use the Classic palette. If you choose another palette, simply replace the corresponding colors; the structure remains unchanged.

<a id="图表标题"></a>
### Diagram Title

Tells the reader "what this diagram is about". Large dark text, centered.

```json
{ "type": "text", "fontSize": 24, "textColor": "#1F2329", "textAlign": "center" }
```

<a id="分区背景"></a>
### Section Background

Encloses related content together, telling the reader "these belong to the same major category". Use a light color as fillColor and the corresponding dark color as borderColor. Place white nodes inside.

```json
{ "fillColor": "#F0F4FC", "borderColor": "#5178C6", "borderWidth": 2, "borderRadius": 8, "padding": 20 }
```

<a id="分区标签"></a>
### Section Label

Give the section a name. Use an independent text node; do not use the frame's `title` property (it will be rendered as a tiny title bar).

**All section labels uniformly use dark text `#1F2329`**; do not use a different color for each label — color differentiation is expressed through the layer container background and border, while label text color remains consistent.

```json
{ "type": "text", "width": 180, "height": "fit-content", "text": "Access layer", "fontSize": 20, "textColor": "#1F2329", "textAlign": "right" }
```

<a id="分组标题"></a>
### Group Heading

Tells the reader "what this sub-group is called". Palette color fill + dark border of the same color family.

```json
{ "fillColor": "#EAE2FE", "borderColor": "#8569CB", "borderWidth": 2, "borderRadius": 8, "fontSize": 14, "textColor": "#1F2329" }
```

<a id="内容节点"></a>
### Content Node

A specific information item. White fill, border color follows its group.

```json
{ "fillColor": "#FFFFFF", "borderColor": "#5178C6", "borderWidth": 2, "borderRadius": 8, "fontSize": 14, "textColor": "#1F2329" }
```

The borderColor of a white node depends on the group it belongs to:
```
Belongs to blue group: fillColor="#FFFFFF"  borderColor="#5178C6"  borderWidth=2
Belongs to purple group: fillColor="#FFFFFF"  borderColor="#8569CB"  borderWidth=2
Independent node:     fillColor="#FFFFFF"  borderColor="#DEE0E3"  borderWidth=2
```
(Note: the above are values from the Classic palette; other palettes replace the corresponding borderColor)

<a id="表头"></a>
### Table Header

Tells the reader "what dimension this column/row represents". Dark fill + white text.

```json
{ "fillColor": "#1F2329", "borderColor": "#1F2329", "borderWidth": 2, "borderRadius": 0, "fontSize": 15, "textColor": "#FFFFFF", "textAlign": "center" }
```

<a id="图标组件"></a>
### Icon Component

A combined card of icon + text. The icon's `color` follows its group's borderColor, visually consistent with other nodes.

```json
{
  "type": "frame", "layout": "vertical", "gap": 4, "padding": 12,
  "alignItems": "center", "fillColor": "#FFFFFF", "borderColor": "#5178C6", "borderWidth": 2, "borderRadius": 8,
  "children": [
    { "type": "icon", "name": "server", "width": 36, "height": 36, "color": "#5178C6" },
    { "type": "text", "width": "fit-content", "height": "fit-content", "text": "应用服务器", "fontSize": 12 }
  ]
}
```

icon color needs to be chosen appropriately based on context, for example: use the borderColor of its group

<a id="textcolor-规则"></a>
### textColor Rules

```
- Body text: #1F2329 (dark, clear on white/light backgrounds)
- Auxiliary notes: #646A73 (subdued, does not compete for attention)
- On dark backgrounds: #FFFFFF (inverted, clearly readable)
(The above are values from the Classic palette; other palettes refer to the corresponding textColor column)
```

<a id="辅助说明"></a>
### Auxiliary Notes

Supplementary information that does not compete for the main subject's attention. Small gray text.

```json
{ "fontSize": 13, "textColor": "#646A73" }
```

<a id="连线"></a>
### Connectors

Express relationships or flow between elements. Use the connector color from the palette.

```json
{ "lineColor": "#BBBFC4", "lineWidth": 2 }
```

<a id="布局容器"></a>
### Layout Container

A frame used purely for layout; the reader cannot see it. Do not set fillColor or borderColor.

```json
{ "type": "frame", "layout": "vertical", "gap": 28, "padding": 32 }
```

<a id="分组容器"></a>
### Group Container

Use a dashed border to enclose a set of nodes; lighter weight than a section background.

```json
{ "borderColor": "#DEE0E3", "borderWidth": 2, "borderDash": "dashed", "borderRadius": 8 }
```

---

<a id="常见错误"></a>
## Common Mistakes

Mistake: one color per node -> the reader cannot tell who belongs with whom
```json
{ "fillColor": "#8569CB" }, { "fillColor": "#5178C6" }, { "fillColor": "#509863" }
```
Correct: nodes in the same group are visually identical -> the reader sees the relationship at a glance
```json
{ "fillColor": "#FFFFFF", "borderColor": "#8569CB" }, { "fillColor": "#FFFFFF", "borderColor": "#8569CB" }
```

Mistake: both inner and outer layers use heavy colors -> the reader does not know where to look first
```json
{ "type": "frame", "fillColor": "#5178C6", "children": [{ "fillColor": "#8569CB" }] }
```
Correct: outer layer light, inner layer white -> the reader sees structure first, then details
```json
{ "type": "frame", "fillColor": "#F0F4FC", "children": [{ "fillColor": "#FFFFFF", "borderColor": "#5178C6" }] }
```

Mistake: connectors use the same bright colors as nodes -> competes with node colors for attention
```json
{ "connector": { "lineColor": "#5178C6" } }
```
Correct: connectors use the connector color from the palette -> sets off the nodes
```json
{ "connector": { "lineColor": "#BBBFC4" } }
```

Mistake: nodes have no border -> blends into the background, boundaries unclear
```json
{ "fillColor": "#FFFFFF" }
```
Correct: nodes have borders -> clear boundaries
```json
{ "fillColor": "#FFFFFF", "borderColor": "#DEE0E3", "borderWidth": 2 }
```

Mistake: the whole diagram is black, white, and gray with no color differentiation -> the reader cannot quickly identify groups
```json
{ "fillColor": "#FFFFFF", "borderColor": "#DEE0E3" }
```
Correct: different groups use different colors -> structure is visible at a glance (blue group + purple group)
```json
{ "fillColor": "#F0F4FC", "borderColor": "#5178C6" }
{ "fillColor": "#EAE2FE", "borderColor": "#8569CB" }
```
