<a id="排版规则"></a>
# Typography Rules

<a id="字号层级表"></a>
## Font Size Hierarchy Table

| Level | Font Size | Purpose | Alignment |
|------|------|------|------|
| H1 | 24-28 | Diagram title (one per diagram) | center |
| H2 | 18-20 | Section/layer label | right (side label) or center (top label) |
| H3 | 15-16 | Group title, card title | center or left |
| Body | 14 | Body text, node text | center (short labels) or left (long text) |
| Caption | 13 | Supplementary notes, annotations | left |

Rules:
- A single diagram must not exceed 3 font size levels
- Nodes at the same level must have exactly the same fontSize
- Font size difference between adjacent levels >= 4px

---

<a id="对齐规则"></a>
## Alignment Rules

Shape nodes default to `textAlign: 'center'` + `verticalAlign: 'middle'` (opposite of CSS). Left alignment must be explicitly declared if needed.

| Content Type | Alignment |
|---------|---------|
| Short text (<=15 characters) | center |
| Long text (>15 characters) | left |
| Side label (layer name, section name) | right |
| Diagram title | center |
| Multi-line description/paragraph | left |

---

<a id="图表标题"></a>
## Diagram Title

Use a standalone text node, do not use the frame's `title` property.

- Flex layout: place as the first child of the outermost frame, `width: "fill-container"`
- Absolute positioning: set width to the overall diagram width, `textAlign: "center"`

---

<a id="标题和描述拆成两个节点"></a>
## Split Title and Description into Two Nodes

When displaying a name and description within a card, use a frame to wrap two text nodes, do not cram them into the same shape:

```json
{
  "type": "frame", "layout": "vertical", "gap": 4, "padding": 12,
  "width": "fill-container", "height": "fit-content",
  "borderWidth": 2, "borderRadius": 8,
  "children": [
    { "type": "text", "width": "fill-container", "height": "fit-content",
      "text": "用户服务", "fontSize": 16 },
    { "type": "text", "width": "fill-container", "height": "fit-content",
      "text": "处理注册登录和个人信息管理", "fontSize": 13 }
  ]
}
```

---

<a id="图标文字组合"></a>
## Icon + Text Combination

When icon + text are arranged vertically: icon width and height 36-48px, text below fontSize 12-13, outer frame gap 4-8. The visual proportion is best when the icon is 2-3 times larger than the text.

---

<a id="尺寸规则"></a>
## Sizing Rules

Nodes containing text `height` must use `'fit-content'`. Hardcoding the height will truncate the text.

All nodes must explicitly declare `width` and `height`.
