<a id="对比图--矩阵图"></a>
# Comparison Diagram / Matrix Diagram

Applicable to: scenarios comparing multiple options across multiple dimensions, such as solution comparison, feature matrices, and technology selection.

<a id="content-约束"></a>
## Content Constraints

- **Each cell's content must be substantial**: Do not write just a keyword; give specific explanations (e.g., "MVCC multi-version concurrency control, supports row-level locking" rather than just "supported")
- Cell content may vary in length across different cells, but each cell must not exceed 5 lines
- For long text (over 15 characters), use `textAlign: "left"` (do not center)
- The first row is the header row (object names), and the first column is the dimension label column
- At least 4 dimensions, fully expanding the comparison dimensions

<a id="layout-选型"></a>
## Layout Selection

| Mode | Applicable Conditions | Characteristics |
|------|---------|------|
| **Strict grid (default)** | All comparison scenarios | Header row + data rows, each row a horizontal frame, rects within a row equally divided |
| **Card-style comparison (alternative)** | Fewer dimensions (2-3) | Each object gets an independent card, with dimensions listed vertically within the card. Cards equally divided horizontally: outer `layout: "horizontal"`, each card `width: "fill-container"` |

<a id="layout-规则"></a>
## Layout Rules

- Outermost frame: `layout: "vertical"`, fixed `width` (e.g., 1000), `height: "fit-content"`
- Each row: horizontal frame, `width: "fill-container"`, `alignItems: "stretch"`
- All cells within a row use `width: "fill-container"` to equally divide the column width
- Between rows `gap >= 12` (do not use 8, too tight)
- Between columns within a row `gap: 8-12`
- Header row: dark background with white text (specific colors controlled by style)
- Borders of the same color per column to maintain visual consistency
- Cells `height: "fit-content"`, do not write a fixed height

<a id="骨架示例"></a>
## Skeleton Example

<a id="3-列-4-行表格"></a>
### 3-column 4-row table

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame",
      "width": 1000,
      "height": "fit-content",
      "layout": "vertical",
      "gap": 12,
      "padding": 0,
      "children": [
        {
          "type": "text",
          "id": "title",
          "width": "fill-container",
          "height": "fit-content",
          "text": "[对比图标题]",
          "fontSize": 24,
          "textAlign": "center",
          "verticalAlign": "middle"
        },
        {
          "type": "frame",
          "id": "header-row",
          "width": "fill-container",
          "height": "fit-content",
          "layout": "horizontal",
          "gap": 8,
          "padding": 0,
          "alignItems": "stretch",
          "children": [
            { "type": "rect", "id": "h-dim", "width": "fill-container", "height": "fit-content", "text": "[维度]", "fontSize": 15, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 0, "borderWidth": 2 },
            { "type": "rect", "id": "h-col-1", "width": "fill-container", "height": "fit-content", "text": "[对象A]", "fontSize": 15, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "h-col-2", "width": "fill-container", "height": "fit-content", "text": "[对象B]", "fontSize": 15, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "h-col-3", "width": "fill-container", "height": "fit-content", "text": "[对象C]", "fontSize": 15, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 }
          ]
        },
        {
          "type": "frame",
          "id": "data-row-1",
          "width": "fill-container",
          "height": "fit-content",
          "layout": "horizontal",
          "gap": 8,
          "padding": 0,
          "alignItems": "stretch",
          "children": [
            { "type": "rect", "id": "d1-dim", "width": "fill-container", "height": "fit-content", "text": "[维度1]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "d1-c1", "width": "fill-container", "height": "fit-content", "text": "[...]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "d1-c2", "width": "fill-container", "height": "fit-content", "text": "[...]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "d1-c3", "width": "fill-container", "height": "fit-content", "text": "[...]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 }
          ]
        },
        {
          "type": "frame",
          "id": "data-row-2",
          "width": "fill-container",
          "height": "fit-content",
          "layout": "horizontal",
          "gap": 8,
          "padding": 0,
          "alignItems": "stretch",
          "children": [
            { "type": "rect", "id": "d2-dim", "width": "fill-container", "height": "fit-content", "text": "[维度2]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "d2-c1", "width": "fill-container", "height": "fit-content", "text": "[...]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "d2-c2", "width": "fill-container", "height": "fit-content", "text": "[...]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "d2-c3", "width": "fill-container", "height": "fit-content", "text": "[...]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 }
          ]
        },
        {
          "type": "frame",
          "id": "data-row-3",
          "width": "fill-container",
          "height": "fit-content",
          "layout": "horizontal",
          "gap": 8,
          "padding": 0,
          "alignItems": "stretch",
          "children": [
            { "type": "rect", "id": "d3-dim", "width": "fill-container", "height": "fit-content", "text": "[维度3]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "d3-c1", "width": "fill-container", "height": "fit-content", "text": "[...]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "d3-c2", "width": "fill-container", "height": "fit-content", "text": "[...]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 },
            { "type": "rect", "id": "d3-c3", "width": "fill-container", "height": "fit-content", "text": "[...]", "fontSize": 14, "textAlign": "center", "verticalAlign": "middle", "borderRadius": 8, "borderWidth": 2 }
          ]
        }
      ]
    }
  ]
}
```

<a id="陷阱"></a>
## Pitfalls

- **Row spacing of 8px is too tight**: The gap between rows should be at least 12; 8 will make rows visually stick together.
- **Center-aligning long text**: Text longer than one line should be changed to `textAlign: "left"`; centered multi-line text has poor readability.
- **Too many columns making each column too narrow**: It is recommended to have ≤ 5 columns for comparison objects (including the dimension column); when exceeded, merge dimensions or split into multiple tables.
- **Unequal column widths**: All data columns must use `width: "fill-container"` to divide equally; do not write a fixed width for any column.
- **Unequal row heights**: Each row frame must `alignItems: "stretch"`, otherwise cells in the same row will be uneven in height due to different numbers of text lines.
- **Forgetting the dimension label column**: Put dimension names in the first column, and use a different visual treatment for the header row (dimension column) than for the data columns.
- **Using a fixed height for cells**: Cells must `height: "fit-content"`; a fixed height will cause text truncation.
