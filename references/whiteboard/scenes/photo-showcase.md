<a id="图片展示-photo-showcase"></a>
# Photo Showcase

Applies to: scenarios where the user **explicitly requests the use of images/illustrations/pictures** (such as "draw a travel route with illustrations" or "make a product showcase with images").

> **Note**: Enter this scenario only when the user explicitly says words like "image/illustration/picture/photo". Simply saying "travel route map" or "product showcase" does not trigger it.

> **Prerequisite**: Before entering this scenario, Step 0 (image preparation) of [`elements/image.md`](../elements/image.md) must already be completed, and all media tokens obtained.

<a id="content-约束"></a>
## Content constraints

- 3-6 images, each with a title (required) + a short description (optional, within 15 characters)
- **Each image must be a different real image** (different media token); use different keywords/URLs when downloading
- After downloading, use `ls -l` to compare file sizes to ensure no image is duplicated
- Text serves only as auxiliary explanation; images are the main body of information

<a id="layout-选型"></a>
## Layout selection

| Mode | Applicable conditions | Characteristics |
|------|---------|------|
| **Card grid (default)** | Multiple images displayed at the same level (product wall, team introduction, food recommendations) | Equal-sized image-text cards placed inside a horizontal frame |
| **Route timeline** | Has a sequential order (travel route, team-building route, project evolution) | Image-text cards + connectors linking them |
| **Hub and spoke** | One core theme + surrounding sub-items | Center title + surrounding image-text cards |

<a id="layout-规则"></a>
## Layout rules

- **Image-text card structure**: vertical frame (image on top, text below), image width = card width, height in 3:2 ratio
- **Uniform card size**: all cards have the same width and height (recommended 240×280 or 200×250)
- **Uniform image size**: all image nodes use the same width/height (recommended 240×160 or 200×133)
- **Card spacing**: gap: 24 (larger than the spacing for text-only diagrams, to let the images breathe)
- **Card style**: white background + 12px rounded corners + thin border, image has no rounded corners (flush with the top of the card)
- **For ordered routes**: connect cards with connectors, and place connectors in the top-level nodes array

<a id="骨架示例"></a>
## Skeleton example

<a id="卡片网格产品展示团队介绍美食推荐"></a>
### Card grid (product showcase/team introduction/food recommendations)

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame", "id": "grid", "layout": "vertical", "gap": 24, "padding": 32,
      "width": 840, "height": "fit-content",
      "children": [
        { "type": "text", "id": "title", "width": 776, "height": 36,
          "text": "图表标题", "fontSize": 24, "textAlign": "center" },
        {
          "type": "frame", "id": "row", "layout": "horizontal", "gap": 24, "padding": 0,
          "width": "fit-content", "height": "fit-content",
          "children": [
            {
              "type": "frame", "id": "card-1", "layout": "vertical", "gap": 8, "padding": [0, 0, 12, 0],
              "width": 240, "height": "fit-content",
              "fillColor": "#FFFFFF", "borderWidth": 1, "borderColor": "#E0E0E0", "borderRadius": 12,
              "children": [
                { "type": "image", "id": "img-1", "width": 240, "height": 160, "image": { "src": "<token_1>" } },
                { "type": "text", "id": "t-1", "text": "标题", "fontSize": 14, "width": 216, "height": 20 },
                { "type": "text", "id": "d-1", "text": "简短描述", "fontSize": 11, "textColor": "#666666", "width": 216, "height": 16 }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Each image-text card has the same structure; just copy it and replace `<token_N>`, the title, and the description. 3 cards per row; if there are more than 3, wrap to a new row (nest a second horizontal frame).

<a id="路线时间线旅行路线团建路线"></a>
### Route timeline (travel route/team-building route)

```json
{
  "version": 2,
  "nodes": [
    {
      "type": "frame", "id": "route", "layout": "vertical", "gap": 24, "padding": 32,
      "width": 1100, "height": "fit-content",
      "children": [
        { "type": "text", "id": "title", "width": 1036, "height": 36,
          "text": "路线标题", "fontSize": 24, "textAlign": "center" },
        {
          "type": "frame", "id": "stops", "layout": "horizontal", "gap": 32, "padding": 0,
          "width": "fit-content", "height": "fit-content",
          "children": [
            {
              "type": "frame", "id": "stop-1", "layout": "vertical", "gap": 8, "padding": [0, 0, 12, 0],
              "width": 240, "height": "fit-content",
              "fillColor": "#FFFFFF", "borderWidth": 1, "borderColor": "#E0E0E0", "borderRadius": 12,
              "children": [
                { "type": "image", "id": "img-1", "width": 240, "height": 160, "image": { "src": "<token_1>" } },
                { "type": "text", "id": "t-1", "text": "第1站：地点名", "fontSize": 14, "width": 216, "height": 20 }
              ]
            },
            {
              "type": "frame", "id": "stop-2", "layout": "vertical", "gap": 8, "padding": [0, 0, 12, 0],
              "width": 240, "height": "fit-content",
              "fillColor": "#FFFFFF", "borderWidth": 1, "borderColor": "#E0E0E0", "borderRadius": 12,
              "children": [
                { "type": "image", "id": "img-2", "width": 240, "height": 160, "image": { "src": "<token_2>" } },
                { "type": "text", "id": "t-2", "text": "第2站：地点名", "fontSize": 14, "width": 216, "height": 20 }
              ]
            }
          ]
        }
      ]
    },
    { "type": "connector", "id": "c1", "connector": { "from": "stop-1", "to": "stop-2", "fromAnchor": "right", "toAnchor": "left" } }
  ]
}
```

Note: connectors must be placed in the **top-level nodes array** and must not be nested inside frame.children. The connector's properties must be wrapped in the `connector` field.

<a id="图片准备检查清单"></a>
## Image preparation checklist

Before generating the DSL, confirm:

- [ ] The `image.src` of all image nodes are media tokens uploaded via `docs +media-upload --parent-type whiteboard` (not URLs, not Drive file tokens)
- [ ] All images have been uploaded to the target whiteboard (`--parent-node` set to the target whiteboard token)
- [ ] Each media token is different (corresponding to a different real image)
- [ ] All images have the same dimensions (uniform width×height within the same whiteboard)
- [ ] Image aspect ratios are reasonable (3:2 recommended, i.e., 240×160)
- [ ] After rendering the PNG, check the image content to confirm each image is relevant to the theme
- [ ] No random placeholder image service is used (an image library where keyword parameters do not affect the returned content)
