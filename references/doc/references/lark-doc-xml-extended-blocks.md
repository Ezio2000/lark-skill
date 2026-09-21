<a id="xml-扩展块补充说明"></a>
# XML Extended Blocks Supplementary Notes

This document supplements the block XML extension capabilities. For commonly used tags and general rules, see [`lark-doc-xml.md`](lark-doc-xml.md); when other block descriptions are added later, they can continue to be appended to this document.

<a id="拓展标签"></a>
## Extended Tags
- `<bookmark name="示例站点" href="https://example.com"></bookmark>`
- `<button action="OpenLink" src="https://example.com">操作按钮</button>`: `action` can be `OpenLink`, `DuplicatePage`, or `FollowPage`; optional `background-color`, `src`.
- `<time expire-time="1775916000000" notify-time="1775912400000" should-notify="false">提醒</time>`: uses a millisecond timestamp.
- `<sheet type="blank"/>`: creates a blank table; `<sheet sheet-id="SHEET_ID" token="SPREADSHEET_TOKEN"/>`: copies an existing table.
- `<task task-id="TASK_GUID"/>`: mounts a task, `task-id` is the task GUID.
- `<chat_card chat-id="CHAT_ID"/>`: mounts a chat card.
- `<sub-page-list/>`: sub-page list block, can only be inserted in wiki documents.


## HTML5 block

1. When writing an HTML content block, save the complete single-file HTML as a local `.html` file, and write `<html5-block path="@./widget.html"/>` in the XML; when `data-ref` already exists, use it together with `--reference-map @./reference-map.json`. When reading, `<html5-block data-ref="html5_1"></html5-block>` is only a placeholder, and the HTML must be read from `document.reference_map["html5-block"]["html5_1"].data`; if the entry is `path`, read the corresponding `@./doc-fetch-resources/...html` file.
2. The format is as follows:

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="use-iframe" content="true">
  <meta name="html-box-height-mode" content="auto">
  <meta name="description" content="内容摘要，会导出为 html5-block 的 alt 属性，帮助模型理解该 HTML 块的用途">
  <title></title>
</head>
<body>
  ...
</body>
</html>
```

<a id="布局与高度"></a>
### Layout and Height

Use only `auto` or `viewport`: use `auto` when the body content needs to be fully expanded in the document; use `viewport` when the content needs to scroll or be presented on a single screen within the HTML Block. `lark-cli` writes the HTML into `reference_map` as-is and does not validate this field, so it must be explicitly declared in `<head>` before creation or update.

- `auto`: uses normal document flow, and does not set a fixed height or `overflow: hidden` on the root container. When a fixed action area is needed, set the CSS `height` and `overflow: auto` on the business container, and do not write pixel values into meta.
- `viewport`: uses `100vh` and internal scrolling, page switching, or zooming, suitable for games, slides, dashboards, and canvas editors.
- Content appended or expanded after page load will not have its height refreshed by `lark-cli`; do not invent related CLI flags.
- The common available width in documents is about `820px`; the root container uses `width: 100%`, `max-width: 100%`, `box-sizing: border-box`.

<a id="内容限制"></a>
### Content Limits

- The total HTML length limit is 500KB. Do not inline large images, Base64, fonts, long JSON/CSV, or large amounts of mock data.

## OKR block
`<okr cycle-id="CYCLE_ID"></okr>`: only root-only is supported at creation time.

OKR blocks can be fully expressed in XML format. Before creation, first refer to [`lark-okr`](../../okr/index.md) to confirm the available period; at creation time, only write root-only `<okr cycle-id="..."/>` to mount an existing OKR, and do not construct Objective/KR/Progress subtrees.

When retrieving, an example XML structure is as follows:

```xml
<okr cycle-id="" cycle-name="CYCLE_NAME" user-name="USER_NAME">
  <okr-objective objective-id="OBJECTIVE_ID" status="normal" percent="80" score="75">
    <p>O 描述</p>
    <okr-progress>
      <p>O 进展</p>
      <checkbox done="true">事项</checkbox>
      <ul><li>列表项内可包含 <a href="https://example.com">链接</a></li></ul>
    </okr-progress>
    <okr-key-result key-result-id="KEY_RESULT_ID" status="risk" percent="60" score="80">
      <p>KR 描述</p>
      <okr-progress>
        <p>KR 进展</p>
      </okr-progress>
    </okr-key-result>
  </okr-objective>
</okr>
```

- `cycle-id` is only used at creation time to mount an existing OKR for the current period; `cycle-name` and `user-name` are read-only.
- `objective-id` and `key-result-id` are read-only business IDs; keep them unchanged when updating an existing OKR.
- `okr-objective` / `okr-key-result`
  - `status`, `percent`, and `score` can be updated; `percent` / `score` take values from 0-100, and `status` takes the values `unset`/`normal`/`risk`/`extended`.
  - The objective and key-result content descriptions cannot be updated.
- `okr-progress` carries progress content and supports updates. Direct child nodes support `<p>`, `<checkbox>`, `<grid>`, `<img>`, `<source>`, `<ol>`, `<ul>`, and `<h1>` through `<h9>`.
