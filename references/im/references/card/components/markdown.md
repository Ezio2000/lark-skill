<a id="富文本-markdown"></a>
# Rich Text `markdown`

Rich text supporting Markdown + some HTML. The most commonly used content component. **Card 2.0**.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "markdown",
  "content": "**标题**\n正文，<font color='red'>红字</font>，[链接](https://x)"
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `markdown` |
| `content` | Yes | String | / | Markdown text; use `\n` for line breaks in JSON |
| `text_size` | No | String | normal | `heading-0`~`heading-4` / `normal`(14px) / `notation`(12px), etc.; you can customize pc/mobile font size in `config.style.text_size` |
| `text_align` | No | String | left | `left` / `center` / `right` |
| `icon` | No | Object | / | Prefix icon (same as `div.icon`) |
| `margin` | No | String | 0 | Margin [-99,99]px |
| `element_id` | No | String | / | Unique identifier, starts with a letter, ≤20 characters |

<a id="常用语法"></a>
## Common Syntax

| Effect | Syntax |
|---|---|
| Bold / Italic / Strikethrough | `**粗**`, `*斜*`, `~~删~~` (leaving spaces before and after is more reliable) |
| Line break | `\n` within JSON; or `<br>` |
| Text link | `[文字](https://x)` (must include http/https) |
| Link with icon | `<link icon='chat_outlined' …>文案</link>` (for icon token, see `../resource/icons.md`) |
| Colored text | `<font color='red'>红字</font>` (for color enum, see `../resource/colors.md`; link text cannot be colored) |
| Tag | `<text_tag color='blue'>标签</text_tag>` (color: neutral/blue/turquoise/lime/orange/violet/indigo/wathet/green/yellow/red/purple/carmine) |
| @ person | `<at id=ou_xxx></at>`, `<at id=all></at>`, `<at ids=id1,id2></at>` |
| @all | `<at id=all></at>` (requires the group owner to grant permission, otherwise sending fails) |
| Person card | `<person id='ou_xxx' show_name=true show_avatar=true style='normal'></person>` |
| Number badge | `<number_tag>1</number_tag>` (0-99, can add background_color/font_color/url) |
| Internationalized time | `<local_datetime millisecond='' format_type='date_num'></local_datetime>` |
| Heading | `# 一级` ~ `###### 六级` (large headings look ugly; for body text, prefer bold, see Common Pitfalls) |
| List | `- 项` (unordered) / `1. 项` (ordered), 4 spaces per indent level |
| Quote | `> 引用文字` |
| Inline/block code | `` `code` `` / ```` ```go ... ``` ```` (language can be specified) |
| Divider | `<hr>` or `---` (must be on its own line) |
| Image | `![hover文案](img_key)` |
| Table | Standard MD table; at most 5 rows excluding the header (exceeding this paginates), ≤4 tables per component |
| Feishu emoji | `:DONE:`, `:OK:` |

<a id="易错点"></a>
## Common Pitfalls

- **Use large headings with caution**: `#` / `##` / `###` level-one to level-three headings have overly large font sizes and look ugly; in body text, always use `**加粗**` instead to highlight key points. The **only exception** is using `##` in a "metric card" to enlarge a value (see `../lark-im-card-style.md` visual guidelines).
- **Use `markdown`'s `margin` sparingly**: prefer delegating spacing to the parent container's `vertical_spacing` / `padding`; in most cases set `0px`; only set a non-zero value for fine-grained indentation (see `../lark-im-card-style.md` spacing discipline).
- 2.0 no longer supports the old `[xx]($urlVal)` + `href` differentiated jump syntax; use `<link>` instead.
- To display Markdown special characters (`* ~ > < [ ] ( ) # : _`, etc.), you must HTML-escape them, e.g. `<`→`&#60;`, `*`→`&#42;`.
- In `content`, pay attention to quotes and JSON escaping; using single quotes for attribute values reduces conflicts.
