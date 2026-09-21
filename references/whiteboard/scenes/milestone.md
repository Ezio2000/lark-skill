<a id="里程碑时间线-milestone"></a>
# Milestone Timeline (Milestone)

<a id="content-约束"></a>
## Content Constraints

- 4-8 nodes
- Each node: title + date + optional description
- Time increases from left to right

<a id="layout-选型"></a>
## Layout Selection

Choose between two approaches as needed:

1. **Horizontal timeline**: horizontal frame, nodes evenly divided
2. **Alternating above and below**: absolute positioning, nodes alternate above and below the timeline (more compact when there are many nodes)

<a id="结构特征"></a>
## Structural Features

- **Centered title**: place the chart title at the top
- **Year/time axis bars**: arrow-shaped color blocks carry the years, increasing from left to right over time
- **Milestone cards**: dashed rounded cards below carry the title and description
- **Strict alignment**: year bars are the same width as their corresponding cards, aligned left and right
- **Text hierarchy**: bold title on top, smaller and lighter description text below, center-aligned

<a id="layout-规则"></a>
## Layout Rules

- Primarily absolute positioning (`layout: "none"`), node positions carry the meaning of the time sequence
- First determine the number of milestones, then calculate an evenly spaced sequence of x coordinates
- Use a connector to run the timeline through all nodes
- Connect nodes to the timeline with short vertical lines
- Horizontal spacing between nodes is consistent
- Year bar width = card width, vertical spacing is uniform
- Reserve enough whitespace between the title and the year area

<a id="骨架示例"></a>
## Skeleton Example

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame",
      "x": 0, "y": 0,
      "width": 1200, "height": 360,
      "layout": "none",
      "children": [
        {
          "type": "text",
          "x": 300, "y": 12,
          "width": 600, "height": "fit-content",
          "text": [{ "content": "{{CHART_TITLE}}", "bold": true, "fontSize": 24 }],
          "textAlign": "center"
        },

        {
          "type": "svg",
          "x": 50, "y": 56,
          "width": 190, "height": 36,
          "svg": {
            "code": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 190 36\"><polygon points=\"0,0 170,0 190,18 170,36 0,36\"/></svg>"
          }
        },
        {
          "type": "text",
          "x": 50, "y": 64,
          "width": 190, "height": "fit-content",
          "text": "{{DATE_1}}",
          "textAlign": "center"
        },
        {
          "type": "rect",
          "x": 50, "y": 132,
          "width": 190, "height": 120,
          "borderDash": "dashed",
          "borderRadius": 8
        },
        {
          "type": "text",
          "x": 50, "y": 150,
          "width": 190, "height": "fit-content",
          "text": [{ "content": "{{MILESTONE_1_TITLE}}", "bold": true, "fontSize": 16 }],
          "textAlign": "center"
        },
        {
          "type": "text",
          "x": 50, "y": 180,
          "width": 190, "height": "fit-content",
          "text": "{{MILESTONE_1_DESC}}",
          "fontSize": 13,
          "textAlign": "center"
        },

        {
          "type": "svg",
          "x": 290, "y": 56,
          "width": 190, "height": 36,
          "svg": {
            "code": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 190 36\"><polygon points=\"0,0 170,0 190,18 170,36 0,36\"/></svg>"
          }
        },
        {
          "type": "text",
          "x": 290, "y": 64,
          "width": 190, "height": "fit-content",
          "text": "{{DATE_2}}",
          "textAlign": "center"
        },
        {
          "type": "rect",
          "x": 290, "y": 132,
          "width": 190, "height": 120,
          "borderDash": "dashed",
          "borderRadius": 8
        },
        {
          "type": "text",
          "x": 290, "y": 150,
          "width": 190, "height": "fit-content",
          "text": [{ "content": "{{MILESTONE_2_TITLE}}", "bold": true, "fontSize": 16 }],
          "textAlign": "center"
        },
        {
          "type": "text",
          "x": 290, "y": 180,
          "width": 190, "height": "fit-content",
          "text": "{{MILESTONE_2_DESC}}",
          "fontSize": 13,
          "textAlign": "center"
        }
      ]
    }
  ]
}
```

<a id="陷阱"></a>
## Pitfalls

- **Too crowded when there are too many nodes**: when there are more than 6 nodes, consider an alternating above-and-below layout or increasing the canvas width
- **Right-side nodes overlap the end of the timeline**: the last node's x + width must not exceed the canvas boundary
- **Year bars not aligned with cards**: the x and width of the year bars and cards must be exactly the same
