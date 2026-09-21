<a id="折线图"></a>
# Line Chart

<a id="content-约束"></a>
## Content Constraints

- Data points ≤ 15
- The Y axis must have a unit label (such as "ten thousand yuan", "%")
- Line series ≤ 3 (more than that is too dense to read clearly)

<a id="layout-选型"></a>
## Layout Selection

- **Script-generated coordinates** (recommended): Use a .cjs script to calculate data point coordinates and line paths, then after the script outputs a JSON file, call `npx -y @larksuite/whiteboard-cli@^0.2.13` to render

<a id="layout-规则"></a>
## Layout Rules

- In the whiteboard coordinate system, the positive Y axis points downward; the chart's "bottom origin" has the largest Y value, and as data points are distributed upward, Y decreases
- Data points are marked with small ellipses (width: 12, height: 12)
- Lines use connector straight to connect adjacent data points, endArrow: "none"
- Axes use connector straight lines with an arrow at the end (endArrow: "arrow")
- Grid lines use dashed connector (lineStyle: "dashed", endArrow: "none")
- Tick marks use short horizontal line connector (endArrow: "none")
- Numeric labels are placed above the data points
- Category labels are placed below the X axis, center-aligned with the data points

<a id="坐标与尺寸计算指南"></a>
## Coordinate and Size Calculation Guide

In the whiteboard coordinate system, **the positive X axis points to the right, and the positive Y axis points downward**. The chart's "bottom origin" has the largest Y coordinate, and as data points are distributed upward, the Y coordinate decreases.

1. **Determine the chart area**:
   - Set the chart area height `chartHeight` and width `chartWidth`
   - Set the coordinate origin at the lower-left corner `(originX, originY)`
   - Example: originX=80, originY=480, chartWidth=900, chartHeight=400
2. **Adaptive Y-axis range**:
   - Find the data minimum `dataMin` and maximum `dataMax`
   - yMin is not necessarily 0: if the data is concentrated in 80-120, starting the Y axis from 0 will squeeze the line into a small area at the top
   - Recommended: yMin = round down to a suitable tick (such as dataMin=82 → yMin=80), yMax = round up (such as dataMax=118 → yMax=120)
   - When data fluctuation is extremely small (such as 98-102), appropriately expand the range to avoid the line being too flat
3. **Data point coordinate calculation**:
   - X coordinate: evenly distributed within the available width. `pointX = originX + (i / (pointCount - 1)) * chartWidth`
   - Y coordinate: proportionally mapped to the height. `pointY = originY - ((value - yMin) / (yMax - yMin)) * chartHeight`
   - ellipse positioning: `ellipseX = pointX - 6, ellipseY = pointY - 6` (center aligned with the data point)
4. **Connection logic**:
   - Use connector straight to connect adjacent data points
   - `from` = point[i]'s (pointX, pointY), `to` = point[i+1]'s (pointX, pointY)
   - startArrow: "none", endArrow: "none"
5. **Y-axis tick calculation**:
   - Divide yMin to yMax equally into 4-5 ticks
   - Y coordinate of each tick: `gridY = originY - ((tickValue - yMin) / (yMax - yMin)) * chartHeight`

<a id="完整-json-示例"></a>
## Complete JSON Example

The following example: 4 data points, data [120, 200, 150, 180], yMin=100, yMax=220, originX=80, originY=480, chartWidth=900, chartHeight=400.

- Ticks: 100, 130, 160, 190, 220 (one every 30)
- Point 0 (120): pointX=80, pointY=480-((120-100)/120)*400=480-66.7=413
- Point 1 (200): pointX=80+300=380, pointY=480-((200-100)/120)*400=480-333.3=147
- Point 2 (150): pointX=80+600=680, pointY=480-((150-100)/120)*400=480-166.7=313
- Point 3 (180): pointX=80+900=980, pointY=480-((180-100)/120)*400=480-266.7=213

```json
{
  "version": 2,
  "nodes": [
    { "type": "rect", "x": 0, "y": 0, "width": 1100, "height": 580 },

    { "type": "text", "x": 80, "y": 10, "width": 900, "height": "fit-content",
      "text": "季度销售额趋势", "fontSize": 24, "textAlign": "center" },

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
      "text": "100", "fontSize": 12, "textAlign": "right" },

    { "type": "connector", "connector": {
      "from": { "x": 70, "y": 380 }, "to": { "x": 80, "y": 380 },
      "lineShape": "straight", "lineWidth": 1,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "text", "x": 20, "y": 370, "width": 50, "height": 20,
      "text": "130", "fontSize": 12, "textAlign": "right" },
    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 380 }, "to": { "x": 980, "y": 380 },
      "lineShape": "straight", "lineWidth": 1, "lineStyle": "dashed",
      "startArrow": "none", "endArrow": "none"
    }},

    { "type": "connector", "connector": {
      "from": { "x": 70, "y": 280 }, "to": { "x": 80, "y": 280 },
      "lineShape": "straight", "lineWidth": 1,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "text", "x": 20, "y": 270, "width": 50, "height": 20,
      "text": "160", "fontSize": 12, "textAlign": "right" },
    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 280 }, "to": { "x": 980, "y": 280 },
      "lineShape": "straight", "lineWidth": 1, "lineStyle": "dashed",
      "startArrow": "none", "endArrow": "none"
    }},

    { "type": "connector", "connector": {
      "from": { "x": 70, "y": 180 }, "to": { "x": 80, "y": 180 },
      "lineShape": "straight", "lineWidth": 1,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "text", "x": 20, "y": 170, "width": 50, "height": 20,
      "text": "190", "fontSize": 12, "textAlign": "right" },
    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 180 }, "to": { "x": 980, "y": 180 },
      "lineShape": "straight", "lineWidth": 1, "lineStyle": "dashed",
      "startArrow": "none", "endArrow": "none"
    }},

    { "type": "connector", "connector": {
      "from": { "x": 70, "y": 80 }, "to": { "x": 80, "y": 80 },
      "lineShape": "straight", "lineWidth": 1,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "text", "x": 20, "y": 70, "width": 50, "height": 20,
      "text": "220", "fontSize": 12, "textAlign": "right" },
    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 80 }, "to": { "x": 980, "y": 80 },
      "lineShape": "straight", "lineWidth": 1, "lineStyle": "dashed",
      "startArrow": "none", "endArrow": "none"
    }},

    { "type": "connector", "connector": {
      "from": { "x": 80, "y": 413 }, "to": { "x": 380, "y": 147 },
      "lineShape": "straight", "lineWidth": 3,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "connector", "connector": {
      "from": { "x": 380, "y": 147 }, "to": { "x": 680, "y": 313 },
      "lineShape": "straight", "lineWidth": 3,
      "startArrow": "none", "endArrow": "none"
    }},
    { "type": "connector", "connector": {
      "from": { "x": 680, "y": 313 }, "to": { "x": 980, "y": 213 },
      "lineShape": "straight", "lineWidth": 3,
      "startArrow": "none", "endArrow": "none"
    }},

    { "type": "ellipse", "id": "pt-0", "x": 74, "y": 407,
      "width": 12, "height": 12 },
    { "type": "text", "x": 55, "y": 383,
      "width": 50, "height": 20,
      "text": "120", "fontSize": 14, "textAlign": "center" },
    { "type": "text", "x": 50, "y": 490,
      "width": 60, "height": 30,
      "text": "Q1", "fontSize": 14, "textAlign": "center" },

    { "type": "ellipse", "id": "pt-1", "x": 374, "y": 141,
      "width": 12, "height": 12 },
    { "type": "text", "x": 355, "y": 117,
      "width": 50, "height": 20,
      "text": "200", "fontSize": 14, "textAlign": "center" },
    { "type": "text", "x": 350, "y": 490,
      "width": 60, "height": 30,
      "text": "Q2", "fontSize": 14, "textAlign": "center" },

    { "type": "ellipse", "id": "pt-2", "x": 674, "y": 307,
      "width": 12, "height": 12 },
    { "type": "text", "x": 655, "y": 283,
      "width": 50, "height": 20,
      "text": "150", "fontSize": 14, "textAlign": "center" },
    { "type": "text", "x": 650, "y": 490,
      "width": 60, "height": 30,
      "text": "Q3", "fontSize": 14, "textAlign": "center" },

    { "type": "ellipse", "id": "pt-3", "x": 974, "y": 207,
      "width": 12, "height": 12 },
    { "type": "text", "x": 955, "y": 183,
      "width": 50, "height": 20,
      "text": "180", "fontSize": 14, "textAlign": "center" },
    { "type": "text", "x": 950, "y": 490,
      "width": 60, "height": 30,
      "text": "Q4", "fontSize": 14, "textAlign": "center" }
  ]
}
```

Coordinate derivation verification:
- Point 0 (Q1, 120): pointX = 80 + (0/3)*900 = 80, pointY = 480 - ((120-100)/120)*400 = 413
- Point 1 (Q2, 200): pointX = 80 + (1/3)*900 = 380, pointY = 480 - ((200-100)/120)*400 = 147
- Point 2 (Q3, 150): pointX = 80 + (2/3)*900 = 680, pointY = 480 - ((150-100)/120)*400 = 313
- Point 3 (Q4, 180): pointX = 80 + (3/3)*900 = 980, pointY = 480 - ((180-100)/120)*400 = 213
- ellipse positioning: ellipseX = pointX - 6, ellipseY = pointY - 6

<a id="陷阱"></a>
## Pitfalls

- Unreasonable Y-axis range: if the data is concentrated in 80-120, setting the Y axis from 0 to 120 will squeeze the line into a small area at the top; yMin should be set close to the data minimum
- Missing Y-axis unit label, so readers cannot understand the meaning of the values
- When data points are too dense, labels obscure each other (if there are more than 10 points, consider labeling every other point)
- Forgetting to set endArrow: "none" on line segments, which have arrows by default
- With multiple series, similar line colors are hard to distinguish; use different color families with high contrast

This scenario must be generated with a .cjs script. When using it, the Agent only needs to modify the `data` array; all other coordinates and line generation are calculated fully automatically.

```javascript
const { writeFileSync } = require('fs');
```
