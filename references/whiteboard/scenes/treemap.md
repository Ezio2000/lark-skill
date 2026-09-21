<a id="矩形树图-treemap"></a>
# Treemap

<a id="content-约束"></a>
## Content Constraints

- 3-5 categories, with 2-4 sub-items under each category
- Total area proportions must be pre-calculated: each rectangle's area = parent rectangle's area * (this item's value / total value of siblings)
- Each leaf node label must include the value (e.g., "{{LABEL}} ({{VALUE}})")

<a id="layout-选型"></a>
## Layout Selection

- **Script-generated coordinates** (recommended): Treemap requires precise area proportion calculations. Use a .cjs script to recursively split rectangles, and after the script outputs a JSON file, call `npx -y @larksuite/whiteboard-cli@^0.2.13` to render
- Not suitable for manually calculating coordinates in your head

<a id="layout-规则"></a>
## Layout Rules

- Use the slice-and-dice method: odd levels split width horizontally, even levels split height vertically
- Within the parent rectangle, 30-40px of top space must be reserved for the title, and child rectangles start at y + 35
- Child nodes must fall entirely within the parent rectangle's bounds
- When splitting horizontally: child width = parent width * (child value / parent total value), and child x accumulates sequentially
- When splitting vertically: child height = (parent height - 35) * (child value / parent total value), and child y accumulates sequentially (note the 35px reserved for the parent label is deducted)

<a id="面积比例计算规则"></a>
### Area Proportion Calculation Rules

1. **Area is strictly proportional to value**: For nodes at any level, their rectangle area `width * height` must be proportional to the value
2. **Odd levels split horizontally** (e.g., the first-level categories):
   - The parent rectangle's `height` and `y` coordinates are passed to all child nodes (after deducting the space reserved for the label)
   - Split the parent rectangle's `width` according to each child node's value proportion of the parent node: `子width = 父width * (子数值 / 父总数值)`
   - Child nodes' `x` coordinates accumulate sequentially to the right
3. **Even levels split vertically** (e.g., the second-level sub-items):
   - The parent rectangle's `width` and `x` coordinates are passed to all child nodes
   - Split the parent rectangle's `height` according to each child node's value proportion of the parent node: `子height = 父height * (子数值 / 父总数值)`
   - Child nodes' `y` coordinates accumulate sequentially downward
4. **Recursion level by level**: Continuously alternate the horizontal and vertical split directions until all leaf nodes have been assigned precise coordinates and width/height

<a id="父标签预留空间"></a>
### Space Reserved for Parent Label

For every non-leaf node's rectangle, 30-40px must be reserved at the top for the category label. Child rectangles start at the parent rectangle's `y + 35`, and the available height is `父height - 35`.

Example: parent rectangle `{ x: 40, y: 40, height: 700 }`, then:
- The parent label is placed at `y: 46` (leaving a 6px top margin)
- Child rectangles start at `y: 75` (40 + 35)
- The available height for child rectangles is `700 - 35 = 665`

<a id="骨架示例"></a>
## Skeleton Example

2-level treemap: 3 categories (Hardware 40, Software 35, Services 25), each containing 2 sub-items.

Root rectangle 1100x700, the first level splits width horizontally, the second level splits height vertically.

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "rect",
      "id": "root",
      "x": 40, "y": 40,
      "width": 1100, "height": 700,
      "borderWidth": 2, "borderRadius": 6
    },
    {
      "type": "text",
      "x": 48, "y": 46,
      "width": 1084, "height": 24,
      "text": "{{ROOT_TITLE}}",
      "fontSize": 14
    },

    {
      "type": "rect",
      "id": "cat-A",
      "x": 40, "y": 75,
      "width": 440, "height": 665,
      "borderWidth": 2, "borderRadius": 6
    },
    {
      "type": "text",
      "x": 48, "y": 81,
      "width": 424, "height": 24,
      "text": "{{CAT_A}}",
      "fontSize": 14
    },
    {
      "type": "rect",
      "id": "cat-A-item-1",
      "x": 40, "y": 110,
      "width": 440, "height": 380,
      "borderRadius": 4
    },
    {
      "type": "text",
      "x": 48, "y": 116,
      "width": 424, "height": 24,
      "text": "{{ITEM_A1}} (24)",
      "fontSize": 14
    },
    {
      "type": "rect",
      "id": "cat-A-item-2",
      "x": 40, "y": 490,
      "width": 440, "height": 250,
      "borderRadius": 4
    },
    {
      "type": "text",
      "x": 48, "y": 496,
      "width": 424, "height": 24,
      "text": "{{ITEM_A2}} (16)",
      "fontSize": 14
    },

    {
      "type": "rect",
      "id": "cat-B",
      "x": 480, "y": 75,
      "width": 385, "height": 665,
      "borderWidth": 2, "borderRadius": 6
    },
    {
      "type": "text",
      "x": 488, "y": 81,
      "width": 369, "height": 24,
      "text": "{{CAT_B}}",
      "fontSize": 14
    },
    {
      "type": "rect",
      "id": "cat-B-item-1",
      "x": 480, "y": 110,
      "width": 385, "height": 380,
      "borderRadius": 4
    },
    {
      "type": "text",
      "x": 488, "y": 116,
      "width": 369, "height": 24,
      "text": "{{ITEM_B1}} (20)",
      "fontSize": 14
    },
    {
      "type": "rect",
      "id": "cat-B-item-2",
      "x": 480, "y": 490,
      "width": 385, "height": 285,
      "borderRadius": 4
    },
    {
      "type": "text",
      "x": 488, "y": 496,
      "width": 369, "height": 24,
      "text": "{{ITEM_B2}} (15)",
      "fontSize": 14
    },

    {
      "type": "rect",
      "id": "cat-C",
      "x": 865, "y": 75,
      "width": 275, "height": 665,
      "borderWidth": 2, "borderRadius": 6
    },
    {
      "type": "text",
      "x": 873, "y": 81,
      "width": 259, "height": 24,
      "text": "{{CAT_C}}",
      "fontSize": 14
    },
    {
      "type": "rect",
      "id": "cat-C-item-1",
      "x": 865, "y": 110,
      "width": 275, "height": 399,
      "borderRadius": 4
    },
    {
      "type": "text",
      "x": 873, "y": 116,
      "width": 259, "height": 24,
      "text": "{{ITEM_C1}} (15)",
      "fontSize": 14
    },
    {
      "type": "rect",
      "id": "cat-C-item-2",
      "x": 865, "y": 509,
      "width": 275, "height": 231,
      "borderRadius": 4
    },
    {
      "type": "text",
      "x": 873, "y": 515,
      "width": 259, "height": 24,
      "text": "{{ITEM_C2}} (10)",
      "fontSize": 14
    }
  ]
}
```

Area proportion verification (first level splits width horizontally):
- Hardware 40/100 * 1100 = 440, Software 35/100 * 1100 = 385, Services 25/100 * 1100 = 275
- Child rectangles start at y=75, available height 665

<a id="陷阱"></a>
## Pitfalls

- **Parent label obscured by child rectangles** (most severe): Child rectangles must start at y + 35 (relative to the parent rectangle's top) to leave space for the parent category label
- **Category label not visible**: The category label text node must be added before its child rectangle rect nodes (nodes later in z-index are on top)
- **Incorrect area proportions**: Proportions must be pre-calculated with a script; do not calculate them in your head
- **Lack of color differentiation**: Different top-level categories must use different background colors (selected from the palette), and all child nodes inherit the corresponding color scheme

This scene must be generated with a .cjs script. When using it, the Agent only needs to modify the `data` tree, and the remaining coordinates and rectangle areas are automatically calculated recursively.

```javascript
const { writeFileSync } = require('fs');
```
