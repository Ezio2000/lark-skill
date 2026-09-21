<a id="组织架构图"></a>
# Organization Chart

Applicable to: scenarios with tree-like hierarchical structures such as company organization charts, module dependency trees, and category hierarchy trees.

<a id="content-约束"></a>
## Content Constraints

- Hierarchy ≤ 4
- ≤ 5 child nodes under each parent node
- Leaf nodes must be meaningful (do not add empty nodes just to make up the count)
- For long text, use `\n` to manually wrap lines (e.g., "R&D Lead\n(CTO)")

<a id="layout-选型"></a>
## Layout Selection

| Mode | Applicable Conditions | Characteristics |
|------|---------|------|
| **tree (centered expansion)** | Hierarchical structures with clear subordinate relationships | Root node centered, child nodes arranged horizontally, expanding layer by layer. Each "parent + children" is wrapped in a vertical frame (subtree module) |
| **grid (matrix-style)** | Multiple departments at the same level, with subdivisions inside each department | Horizontally divide departments equally, with a vertical list inside each department |

<a id="layout-规则"></a>
## Layout Rules

Violating the following rules will cause connector lines to become disordered or the layout to collapse:

1. **Subtree wrapping pattern (critical)**: Each parent node and its group of child nodes are wrapped in a frame made of `layout: "vertical"` + `alignItems: "center"`. **Do not** put all parent nodes in one layer and all child nodes in another layer. *Consequence of violation: the center of the parent node and the center of the child node group become offset, orthogonal connectors cannot merge, and they split into two parallel lines.*
2. **Nodes at the same layer should preferably be equal height**: Nodes at the same layer should use a uniform `height` (e.g., 60-70) to ensure the horizontal main axis of the connectors is straight. If text lengths vary greatly, you may use `fit-content`, but make sure the number of text lines at the same layer is similar. *Consequence of violation: nodes at the same layer become uneven in height, and rightAngle connectors bend horizontally in a disordered way.*
3. **Vertical spacing >= 60**: Vertical `gap: 60` between parent and child. *Consequence of violation: the connector engine does not have enough space to bend and merge, causing connectors to clip through shapes or branch prematurely.*
4. **Even width for leaf containers**: For a horizontal frame containing leaf nodes, the width should be calculated manually (sum of child node widths + gap × (n-1)), e.g., 2 nodes of 120px + 20px gap = `width: 260`. Or use `fill-container` to divide equally automatically. *Consequence of violation: there is a pixel-level offset between the parent node center and the child node group center.*
5. **Horizontal gap between siblings at the same layer: 20-40**
6. Minimum font size 14px
7. Connectors: all parent-child connectors must be `lineShape: "rightAngle"` (bus style), `fromAnchor: "bottom"`, `toAnchor: "top"`. *Consequence of violation: loss of the bus-style visual effect unique to organization charts.*
8. The root frame width must be sufficient (e.g., 1200-1600) to avoid leaf nodes being squeezed and overlapping
9. Different layers should be progressively distinguished by fontSize, borderWidth, and color (e.g., Root dark gray → L1 light blue → L2 light green → L3 light purple)
10. For long text, use `\n` to actively wrap lines (e.g., "Infrastructure Department\n(includes cloud native)") to ensure node height is sufficient to contain it

<a id="骨架示例"></a>
## Skeleton Example

<a id="树形展开子树包裹模式"></a>
### Tree Expansion (Subtree Wrapping Pattern)

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame",
      "width": 1200,
      "height": "fit-content",
      "layout": "vertical",
      "gap": 48,
      "padding": 40,
      "alignItems": "center",
      "children": [
        {
          "type": "text",
          "id": "title",
          "width": "fill-container",
          "height": "fit-content",
          "text": "[图表标题]",
          "fontSize": 24,
          "textAlign": "center",
          "verticalAlign": "middle"
        },
        {
          "type": "rect",
          "id": "root-node",
          "width": 240,
          "height": "fit-content",
          "borderWidth": 3,
          "borderRadius": 8,
          "text": "[根节点名]",
          "fontSize": 18,
          "padding": 12
        },
        {
          "type": "frame",
          "width": "fill-container",
          "height": "fit-content",
          "layout": "horizontal",
          "gap": 40,
          "padding": 0,
          "alignItems": "stretch",
          "children": [
            {
              "type": "frame",
              "width": "fill-container",
              "height": "fit-content",
              "layout": "vertical",
              "gap": 48,
              "padding": 0,
              "alignItems": "center",
              "children": [
                {
                  "type": "rect",
                  "id": "child-a",
                  "width": 200,
                  "height": "fit-content",
                  "borderWidth": 2,
                  "borderRadius": 8,
                  "text": "[子节点名]",
                  "fontSize": 16,
                  "padding": 10
                },
                {
                  "type": "frame",
                  "width": "fill-container",
                  "height": "fit-content",
                  "layout": "horizontal",
                  "gap": 40,
                  "padding": 0,
                  "alignItems": "stretch",
                  "children": [
                    { "type": "rect", "id": "leaf-a1", "width": "fill-container", "height": "fit-content", "borderWidth": 1, "borderRadius": 8, "text": "[叶节点名]", "fontSize": 14, "padding": 8 },
                    { "type": "rect", "id": "leaf-a2", "width": "fill-container", "height": "fit-content", "borderWidth": 1, "borderRadius": 8, "text": "[叶节点名]", "fontSize": 14, "padding": 8 }
                  ]
                }
              ]
            },
            {
              "type": "frame",
              "width": "fill-container",
              "height": "fit-content",
              "layout": "vertical",
              "gap": 48,
              "padding": 0,
              "alignItems": "center",
              "children": [
                {
                  "type": "rect",
                  "id": "child-b",
                  "width": 200,
                  "height": "fit-content",
                  "borderWidth": 2,
                  "borderRadius": 8,
                  "text": "[子节点名]",
                  "fontSize": 16,
                  "padding": 10
                },
                {
                  "type": "frame",
                  "width": "fill-container",
                  "height": "fit-content",
                  "layout": "horizontal",
                  "gap": 40,
                  "padding": 0,
                  "alignItems": "stretch",
                  "children": [
                    { "type": "rect", "id": "leaf-b1", "width": "fill-container", "height": "fit-content", "borderWidth": 1, "borderRadius": 8, "text": "[叶节点名]", "fontSize": 14, "padding": 8 },
                    { "type": "rect", "id": "leaf-b2", "width": "fill-container", "height": "fit-content", "borderWidth": 1, "borderRadius": 8, "text": "[叶节点名]", "fontSize": 14, "padding": 8 }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    { "type": "connector", "connector": { "from": "root-node", "to": "child-a", "fromAnchor": "bottom", "toAnchor": "top", "lineShape": "rightAngle", "lineWidth": 2 } },
    { "type": "connector", "connector": { "from": "root-node", "to": "child-b", "fromAnchor": "bottom", "toAnchor": "top", "lineShape": "rightAngle", "lineWidth": 2 } },
    { "type": "connector", "connector": { "from": "child-a", "to": "leaf-a1", "fromAnchor": "bottom", "toAnchor": "top", "lineShape": "rightAngle", "lineWidth": 2 } },
    { "type": "connector", "connector": { "from": "child-a", "to": "leaf-a2", "fromAnchor": "bottom", "toAnchor": "top", "lineShape": "rightAngle", "lineWidth": 2 } },
    { "type": "connector", "connector": { "from": "child-b", "to": "leaf-b1", "fromAnchor": "bottom", "toAnchor": "top", "lineShape": "rightAngle", "lineWidth": 2 } },
    { "type": "connector", "connector": { "from": "child-b", "to": "leaf-b2", "fromAnchor": "bottom", "toAnchor": "top", "lineShape": "rightAngle", "lineWidth": 2 } }
  ]
}
```

<a id="陷阱"></a>
## Pitfalls

- **Separating parent and child layers (fatal error)**: Do not put all parent nodes at the same level in one horizontal frame and all child nodes in another. You must use a vertical frame with `alignItems: "center"` to wrap each parent node together with its child nodes.
- **Nodes at the same layer uneven in height**: Nodes at the same layer should have the same height (or a similar number of text lines), otherwise rightAngle connectors bend horizontally in a disordered way.
- **Insufficient vertical spacing**: The gap between parent and child must be >= 60. If it is not enough, the connector engine cannot bend and merge. Also do not use 80; 3-4 layers will stretch vertically too much.
- **Making it a linear chain instead of a tree expansion**: The child nodes of each parent node must expand horizontally; do not make a single chain.
- **Mixing straight connectors**: All parent-child connectors must be `lineShape: "rightAngle"`, `fromAnchor: "bottom"`, `toAnchor: "top"`.
- **Leaf node font size 12px is illegible**: Minimum font size 14px.
- **All nodes have the same size and style**: Different layers must be distinguished by fontSize, borderWidth, and color (root > child > leaf).
