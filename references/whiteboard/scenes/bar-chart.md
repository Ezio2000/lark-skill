<a id="柱状图"></a>
# Bar Chart

<a id="content-约束"></a>
## Content Constraints

- Data points ≤ 12
- Use the same color for the same data series (do not use a different color for each bar)
- The Y axis must have a unit label (such as "ten thousand yuan", "person-times")

<a id="layout-选型"></a>
## Layout Selection

- **Script-generated coordinates** (recommended): Use a .cjs script to calculate bar positions and heights, have the script output a JSON file, then call `npx -y @larksuite/whiteboard-cli@^0.2.13` to render
- **Absolute positioning by hand**: Simple bar charts (≤ 5 bars) can have coordinates written by hand

<a id="layout-规则"></a>
## Layout Rules

- In the whiteboard coordinate system, the positive Y axis points downward; the chart's "bottom origin" has the largest Y value, and as bars grow upward, Y decreases
- Bars are equal in width and equally spaced, aligned at the bottom with the X axis
- Bar height: `height = (value / maxValue) * chartHeight`
- Bar Y coordinate: `y = originY - height`
- Use connector straight lines for the coordinate axes, with arrows at the ends (endArrow: "arrow")
- Use dashed connectors for grid lines (lineStyle: "dashed", endArrow: "none")
- Use short horizontal-line connectors for tick marks (endArrow: "none")
- Place value labels above the top of the bars
- Place category labels below the X axis, centered and aligned with the bars

<a id="坐标与尺寸计算指南"></a>
## Coordinate and Size Calculation Guide

In the whiteboard coordinate system, **the positive X axis points to the right, and the positive Y axis points downward**. Therefore, the chart's "bottom origin" actually has the largest Y coordinate, and as the graphic grows upward, the Y coordinate continuously decreases.

1. **Determine the chart area**:
   - Set the chart area height `chartHeight` and width `chartWidth`
   - Set the coordinate origin at the lower-left corner `(originX, originY)`
   - Example: originX=80, originY=480, chartWidth=1000, chartHeight=400
2. **Y-axis mapping (calculate height)**:
   - Find the maximum value of the data `maxValue`
   - Round maxValue up to an "integer tick" (for example, if the data maximum is 190 → maxValue becomes 200)
   - Bar height: `height = (value / maxValue) * chartHeight`
   - Bar Y coordinate: `y = originY - height`
3. **X-axis mapping (calculate width and X coordinate)**:
   - Divide chartWidth evenly by the number of data items: `slotWidth = chartWidth / barCount`
   - Set the bar gap `barGap` (recommended: 25%-30% of slotWidth)
   - Bar width: `barWidth = slotWidth - barGap`
   - X coordinate of the i-th bar: `x = originX + i * slotWidth + barGap / 2`
4. **Y-axis tick calculation**:
   - Divide 0 to maxValue evenly into 4-6 ticks
   - Y coordinate of each tick: `gridY = originY - (tickValue / maxValue) * chartHeight`
   - Tick marks: short horizontal lines from (originX-10, gridY) to (originX, gridY)
   - Grid lines: dashed lines from (originX, gridY) to (originX+chartWidth, gridY)

<a id="完整-json-示例"></a>
## Complete JSON Example

The following example: 3 bars, data [120, 200, 150], maxValue=200, originX=80, originY=480, chartWidth=900, chartHeight=400.

- slotWidth = 900 / 3 = 300
- barGap = 80, barWidth = 220
- Ticks: 0, 50, 100, 150, 200 (one grid every 50, gridInterval = 80px)

```json
{
  "version": 2,
  "nodes": [
    { "type": "rect", "x": 0, "y": 0, "width": 1100, "height": 580 },

    { "type": "text", "x": 80, "y": 10, "width": 900, "height": "fit-content",
      "text": "季度销售额对比", "fontSize": 24, "textAlign": "center" },

    { "type": "text", "x": 10, "y": 40, "width": 60, "height": "fit-content",
      "text": "万元", "fontSize": 12, "textAlign": "center" },

    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 480 }, "to": { "x": 80, "y": 55 },
      "lineShape": "straight", "lineWidth": 2, "endArrow": "arrow"
    }},
    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 480 }, "to": { "x": 1000, "y": 480 },
      "lineShape": "straight", "lineWidth": 2, "endArrow": "arrow"
    }},

    { "type": "connector", "connector": {
      "from": { "x": 70, "y": 480 }, "to": { "x": 80, "y": 480 },
      "lineShape": "straight", "lineWidth": 1,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "text", "x": 20, "y": 470, "width": 50, "height": 20,
      "text": "0", "fontSize": 12, "textAlign": "right" },

    { "type": "connector", "connector": {
      "from": { "x": 70, "y": 400 }, "to": { "x": 80, "y": 400 },
      "lineShape": "straight", "lineWidth": 1,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "text", "x": 20, "y": 390, "width": 50, "height": 20,
      "text": "50", "fontSize": 12, "textAlign": "right" },
    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 400 }, "to": { "x": 980, "y": 400 },
      "lineShape": "straight", "lineWidth": 1, "lineStyle": "dashed",
      "startArrow": "none", "endArrow": "none"
    }},

    { "type": "connector", "connector": {
      "from": { "x": 70, "y": 320 }, "to": { "x": 80, "y": 320 },
      "lineShape": "straight", "lineWidth": 1,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "text", "x": 20, "y": 310, "width": 50, "height": 20,
      "text": "100", "fontSize": 12, "textAlign": "right" },
    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 320 }, "to": { "x": 980, "y": 320 },
      "lineShape": "straight", "lineWidth": 1, "lineStyle": "dashed",
      "startArrow": "none", "endArrow": "none"
    }},

    { "type": "connector", "connector": {
      "from": { "x": 70, "y": 240 }, "to": { "x": 80, "y": 240 },
      "lineShape": "straight", "lineWidth": 1,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "text", "x": 20, "y": 230, "width": 50, "height": 20,
      "text": "150", "fontSize": 12, "textAlign": "right" },
    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 240 }, "to": { "x": 980, "y": 240 },
      "lineShape": "straight", "lineWidth": 1, "lineStyle": "dashed",
      "startArrow": "none", "endArrow": "none"
    }},

    { "type": "connector", "connector": {
      "from": { "x": 70, "y": 160 }, "to": { "x": 80, "y": 160 },
      "lineShape": "straight", "lineWidth": 1,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "text", "x": 20, "y": 150, "width": 50, "height": 20,
      "text": "200", "fontSize": 12, "textAlign": "right" },
    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 160 }, "to": { "x": 980, "y": 160 },
      "lineShape": "straight", "lineWidth": 1, "lineStyle": "dashed",
      "startArrow": "none", "endArrow": "none"
    }},

    { "type": "rect", "id": "bar-0", "x": 120, "y": 240,
      "width": 220, "height": 240, "borderRadius": 4 },
    { "type": "text", "x": 120, "y": 215,
      "width": 220, "height": 20,
      "text": "120", "fontSize": 14, "textAlign": "center" },
    { "type": "text", "x": 120, "y": 490,
      "width": 220, "height": 30,
      "text": "Q1", "fontSize": 14, "textAlign": "center" },

    { "type": "rect", "id": "bar-1", "x": 420, "y": 80,
      "width": 220, "height": 400, "borderRadius": 4 },
    { "type": "text", "x": 420, "y": 55,
      "width": 220, "height": 20,
      "text": "200", "fontSize": 14, "textAlign": "center" },
    { "type": "text", "x": 420, "y": 490,
      "width": 220, "height": 30,
      "text": "Q2", "fontSize": 14, "textAlign": "center" },

    { "type": "rect", "id": "bar-2", "x": 720, "y": 180,
      "width": 220, "height": 300, "borderRadius": 4 },
    { "type": "text", "x": 720, "y": 155,
      "width": 220, "height": 20,
      "text": "150", "fontSize": 14, "textAlign": "center" },
    { "type": "text", "x": 720, "y": 490,
      "width": 220, "height": 30,
      "text": "Q3", "fontSize": 14, "textAlign": "center" }
  ]
}
```

Coordinate derivation verification:
- bar-0 (120): height = (120/200)*400 = 240, y = 480-240 = 240
- bar-1 (200): height = (200/200)*400 = 400, y = 480-400 = 80
- bar-2 (150): height = (150/200)*400 = 300, y = 480-300 = 180
- bar-0 x = 80 + 0*300 + 80/2 = 120, bar-1 x = 80 + 1*300 + 40 = 420, bar-2 x = 80 + 2*300 + 40 = 720

<a id="陷阱"></a>
## Pitfalls

- Using multiple colors for a single series (unprofessional): all bars in the same data series should use the same color
- Missing Y-axis unit labels, so readers cannot understand the meaning of the values
- Uneven bar spacing (the script needs to calculate barGap uniformly)
- Y-axis tick marks and grid lines mistakenly having arrows
- Forgetting arrows on the coordinate axes

This scenario must be generated with a .cjs script. When using it, the Agent only needs to modify the `data` array; all other coordinates and bar heights are calculated fully automatically.

```javascript
const { writeFileSync } = require('fs');
```
