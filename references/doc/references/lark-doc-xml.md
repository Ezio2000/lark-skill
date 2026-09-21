<a id="飞书-xml-语法"></a>
# Feishu XML Syntax

**The syntax uses HTML-like tags, and rendering uses a vertical block-level document flow: top-level Blocks are arranged vertically in document order, and blocks support rich text and nested child blocks. The default width is about 820 px, and wide mode is about 1020 px**

The following are XML syntax examples; replace the example values when using them. Attributes must be written as `name="value"`; omitting quotation marks is prohibited.

<a id="常用标签"></a>
## Common Tags

- `p, h1-h9, blockquote, hr, img, b, em, u, del, br, span` semantics are unchanged. For ordinary documents, it is recommended to use only `h1-h6`; use `h7-h9` only when a deeper level is truly needed.
- `<a type="url-preview" href="URL">链接标题</a>`
- `<latex>E = mc^2</latex>`: suitable for inline formulas, and also for superscript and subscript notation.
- `<ol><li>第一项<ul><li>子项</li></ul></li><li>第二项</li></ol>`: child lists go inside `<li>`; new list items must go inside `<ul>` or `<ol>`.
- `<pre lang="go" caption="示例"><code>fmt.Println(&quot;hello&quot;)</code></pre>`: code must go inside `<code>`; placing it directly under `<pre>` is prohibited; `caption` may be omitted.
- `<img path="@./photo.png"/>`: upload a local image in the current working directory. You can also use `<img href="URL"/>` to upload a public HTTP(S) web image, or use `<img src="token"/>` to copy the original image; choose one of the three, with optional `width`, `height`, `caption`, `name`. When using `href`, the CLI converts the remote image into a local resource and completes the upload; the response must be PNG, JPEG, GIF, or WebP, and a single image must not exceed 20MiB. Images on internal networks must first be downloaded locally before using `path`.
- `<source path="@./report.pdf" name="报告.pdf"/>`: upload a local attachment; you can also use `<source token="token" name="xx"/>` to copy an existing attachment. It can be used independently, placed inside `<p>` as an inline attachment, or written as `<figure view-type="Card|Preview"><source/></figure>`;
- `<checkbox done="true|false">todo</checkbox>`
- `p, h1-h9, li, checkbox, title` supports the optional attribute `align`, with optional values `left`, `center`, `right`, for example `<p align="center">居中正文</p>`.

<a id="标题与列表编号"></a>
## Headings and List Numbering

- A complete document starts with a unique `<title>`; body headings use `<h1>` through `<h9>`, and levels must be consecutive without skipping, for example after `<h1>` you cannot directly use `<h3>`; `<h2>` must appear first. When automatic numbering is needed, set `seq="auto"`, and the system generates and increments Arabic numeral numbering according to heading levels, for example a level-one heading is `1`, and a level-two heading is `1.1`.
- Ordered list: the default attribute is `seq="auto"`; when starting from a specified number, set the corresponding value, such as `seq="3"`.

<a id="表格"></a>
## Tables

- `<table><thead><tr><th><p>表头</p></th></tr></thead><tbody><tr><td><p>内容</p></td></tr></tbody></table>`
- `<colgroup><col /></colgroup>` immediately follows `<table>` to define column width; `width` indicates column width, and optional `span` indicates the number of consecutive columns affected.
- `<th>` / `<td>` support `background-color`, `vertical-align`, `colspan`, `rowspan`; `vertical-align`: `top | middle | bottom`; `background-color` supports basic hues, `light-{色相}`, `medium-gray`; table headers should preferentially use `light-gray` or `medium-gray`, and colored cells should be used only to express status or classification. Merged cells are no longer written.

<a id="扩展标签"></a>
## Extended Tags

- `<cite type="user" user-id="ou_xxx"/>`: @person, rendered as a user avatar; the user `open_id` must be explicitly passed, and a plain-text name must not be used to impersonate an @person.
- `<cite type="doc" doc-id="DOC_TOKEN"/>`: @document, rendered as the document title.
- `<cite type="citation"><a href="URL" url-type="N"></a></cite>`: reference container, containing only multiple `<a>`. `url-type` identifies the link type: `5` (WebURL) must fill in the rendered title in `<a></a>`; `1` (Docx), `6` (Minutes), `12` (Base), `13` (Sheet) may be left empty.
- `<whiteboard></whiteboard>`: choose one of `type | src`. `type=blank` means create new; when `type=mermaid|plantuml|svg`, it supports `path=@./file` import, and also supports writing content directly inside the tag; `src=token` means copying an existing whiteboard. For complex diagrams, read [`lark-doc-whiteboard.md`](lark-doc-whiteboard.md);
- `<grid><column width-ratio="0.5"><p>左栏</p></column><column width-ratio="0.5"><p>右栏</p></column></grid>`: the sum of each column's `width-ratio` is 1.
- `<callout emoji="💡" background-color="light-*" border-color="*"><p>高亮块内容</p></callout>`: child blocks support only `p`, `ol`, `ul`, `checkbox`, and inline tags; `<table>`, `<img>`, `<pre>`, `<hr>`, `<grid>`, `<whiteboard>`, and other block-level tags or resource blocks are prohibited. Optional `text-color`.
- Other extended tags `html5-block`, `bookmark`, `button`, `time`, `sheet`, `task`, `chat_card`, `sub-page-list`, `okr` are described in [`lark-doc-xml-extended-blocks.md`](lark-doc-xml-extended-blocks.md).

<a id="颜色"></a>
## Colors

Colors are used to express semantics and remain consistent throughout the document; by default, keep neutral-color typography and avoid coloring merely for decoration.

- **Valid values**: hues are `red, orange, yellow, green, blue, purple, gray`; `text-color`, `border-color` use basic hues; `<span>`, `<th>`, `<td>`, `<button>` backgrounds support basic hues, `light-{色相}`, `medium-gray`; highlight block backgrounds support `gray`, `light-{色相}`, `medium-{色相}`.
- **Highlight blocks**: by default use `light-*` background and the default text color; use `medium-*` only for strong reminders, and colored text only emphasizes phrases.
- **Tables**: table headers should preferentially use `light-gray` or `medium-gray`; colored cells express only status or classification, and avoid coloring the entire table.

<a id="转义规则"></a>
## Escaping Rules

Escaping the tags themselves is prohibited; escape only the text content inside tags.

- Text escaping: `<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;`, newline character `\n` → `<br/>`.
- Incorrect: `&lt;p&gt;内容&lt;/p&gt;`
- Correct: `<p>A &amp; B 的对比：1 &lt; 2</p>`
