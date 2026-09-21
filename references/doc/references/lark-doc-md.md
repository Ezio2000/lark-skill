<a id="markdown-格式参考"></a>
# Markdown Format Reference

Applies when `docs +fetch` / `docs +create` / `docs +update` use `--doc-format markdown`; the `--doc-format im-markdown` of fetch is only used to retrieve content and then use it in the `lark-im` scenario, and is not used as the write format for create/update.

<a id="转义规则"></a>
## Escaping Rules

> **⚠️ When the text contains the following characters and you do not want to trigger Markdown syntax**, you need to escape them with the `\` prefix. Escaping is divided into two categories: **unconditional escaping** (takes effect anywhere within a line) and **position-sensitive escaping** (only needed in specific positions).

<a id="无条件转义行内生效任何位置都要转义"></a>
### Unconditional Escaping (takes effect within a line, must be escaped in any position)

| Symbol | Markdown syntax purpose | Escape form | Example |
|------|-------------------|----------|------|
| `\` | The escape character itself | `\\` | `C:\\Users` → C:\Users |
| `` ` `` | Inline code | `` \` `` | `` 用 \` 包裹 `` |
| `*` | Italic / bold | `\*` | `3 \* 5 = 15` → 3 \* 5 = 15 |
| `_` | Italic / bold | `\_` | `foo\_bar\_baz` → foo\_bar\_baz |
| `[` `]` | Link text | `\[` `\]` | `\[非链接\]` |
| `$` | Math formula delimiter | `\$` | `价格 \$100` |
| `~` | Strikethrough (GFM `~~text~~`) | `\~` | `a\~\~b\~\~c` → a~~b~~c |
| `<` | XML tag start (`<b>`, `<img>`, etc. will be parsed as tags and take effect) | `\<` | The literal `<b>` must be written as `\<b>`; `a < b` is recommended to be written as `a \< b` |

<a id="位置敏感转义仅在特定位置才需要转义"></a>
### Position-Sensitive Escaping (only needs escaping in specific positions)

| Symbol | Markdown syntax purpose | Escape condition | Example |
|------|-------------------|----------|------|
| `#` | Heading | **Only at line start** (after removing leading whitespace) | At line start `\# 这不是标题`; inline `A # B` does not need escaping |
| `+` | Unordered list | **Only at line start** (after removing leading whitespace) | At line start `\+ item`; inline `1 + 2` does not need escaping |
| `-` | Unordered list / horizontal rule | **Only at line start** (after removing leading whitespace) | At line start `\- item`; inline `A - B` does not need escaping |
| `>` | Blockquote | **Only at line start** (after removing leading whitespace) | At line start `\> 不是引用`; inline `a > b` does not need escaping |
| `\|` | Table cell separator | **Only within a GFM table cell** | Within a cell `A \| B`; inline normal text `a \| b` does not need escaping |

**Scenarios where escaping is not needed:**
- Within `` ` `` inline code or ` ``` ` code blocks, all symbols are literals and do not need escaping
- Inside `$...$` math formulas, symbols are LaTeX syntax and are not affected by Markdown escaping

**Export is already escaped, do not unescape:**
In content exported by `docs +fetch --doc-format markdown`, special characters **have already been escaped** (for example `\[`, `\|`, `\\`, etc.). These `\` are meaningful—removing them will cause the characters to be swallowed by Markdown syntax in subsequent writes. **Do not unescape or remove `\`.**

**Escaping is required when writing:**
When writing content using `docs +create` or `docs +update`'s `--doc-format markdown`, special characters in literal text must likewise be escaped. In the `--pattern` parameter, the escaped form must also be used to match correctly.

**Export → Update workflow example:**

1. `docs +fetch` export yields `C:\\Users\\test\[1\]`
2. Use `str_replace --pattern 'C:\\Users\\test\[1\]'` to match (directly use the exported escaped form)
3. The replacement content in `--content` must also remain escaped: `C:\\Users\\prod\[2\]`

When constructing Markdown content yourself for writing, the same applies: for example, the literal text `a]b` should be written as `a\]b`, and `C:\Users` should be written as `C:\\Users`.

<a id="shell-传参"></a>
## Shell Argument Passing
- **File argument passing preferred**: `--content` supports `@./path/to/file.md` (read file) and `-` (read stdin), completely bypassing shell escaping; strongly recommended for multi-line, special-character-containing, and long text. When a literal starts with `@`, use `@@` to escape (`--pattern` does not support `@file`)
- **⚠️ `@file` path restriction**: `@file` only accepts relative paths under the current working directory; passing an absolute path (such as `@/tmp/xxx.md`) will report `unsafe file path`. When you need to write to disk, write the file under cwd (such as `./_content.md`), and clean it up yourself after use.
- **Use single quotes `'...'` by default**: fully literal, `$`, `` ` ``, `\`, `>`, `\<b>`, etc. are all preserved as-is
- **Double quotes `"..."`**: will expand `$变量`, backticks, and `$(...)` command substitution; `\` still participates in escaping, easy to trip up
- **`$'...'` ANSI-C quoting**: parsed according to C escapes, `\n`=newline, `\\`=single `\`; **under zsh, the `\` of unknown escapes (such as `\<`) will be swallowed**, to preserve a literal `\` you must write `\\`. Only use when you actually need `\n`/`\t`
- **Multi-line content**: use `<<'EOF'` heredoc; EOF must be quoted, otherwise `$` will still be expanded
- **`\n` is a literal in both `'...'` and `"..."`**, not a newline; for a real newline use `$'...\n...'` or a heredoc

<a id="图片语法"></a>
## Image Syntax

Markdown format supports inserting online images via URL; images will be automatically downloaded over HTTP:
```markdown
![alt text](https://example.com/photo.png)
```
- `alt text` is the image description (optional, may be left empty)
- URL supports the `http://` and `https://` protocols
- The corresponding XML format is: `<img href="https://example.com/photo.png"/>`

For local images use `![alt](@./images/photo.png)` (when the path contains spaces, write it as `![alt](<@./images/product shot.png>)`); the path must be within the current working directory, and `alt` will be used as the caption. For attachments use `<source path="@./files/report.pdf"/>`

Currently, passing a Base64 Data URI (such as `data:image/png;base64,...`) directly as a Markdown image address is not supported; if you only have Base64 data, first decode it into a local image file, then upload using the above `@./...` path.

<a id="markdown-不支持的-block-类型"></a>
## Block Types Not Supported by Markdown

Content that is not native Markdown syntax (such as underline, Callout, checkbox, Base, whiteboard, mind map, spreadsheet, grid layout, mentions (@document/@person), button, date reminder, inline file, text color/background color, synced block, etc.) is represented using XML syntax; see [`lark-doc-xml.md`](lark-doc-xml.md) for details.
> **⚠️ XML tags will be parsed and take effect**: even under `--doc-format markdown`, XML tags such as `<b>`, `<u>`, `<img>` will be recognized as the corresponding rich text nodes and will **not** be displayed as literals. If you need to output text wrapped in angle brackets literally (for example `<tag>` in the example), you must escape the left angle bracket: `\<b>`, `\<img>`.

<a id="参考"></a>
## Reference

- [`lark-doc-xml.md`](lark-doc-xml.md) — XML syntax specification
