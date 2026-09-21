<a id="slides-add-slide向已有演示文稿追加插入单页"></a>
# slides +add-slide (append/insert a single page into an existing presentation)

Add **one page** to an existing presentation. This is the second step of the two-step creation flow: first `+create` to create an empty shell, then `+add-slide` page by page; it is also used to append new pages to an existing PPT.

`--presentation` accepts a token / `/slides/` URL / `/wiki/` URL (wiki is resolved automatically), `--slide` takes XML directly (supports `@file` and stdin; complex XML can go through a file to bypass shell escaping), and `<img src="@./local.png">` placeholders are automatically uploaded and replaced with `file_token`.

**CRITICAL — you must run the layout lint before submitting**: save the `<slide>` XML to be submitted as a local file, run [`scripts/xml_lint.py`](../../scripts/xml_lint.py), and `summary.error_count` must be 0.

<a id="命令"></a>
## Command

```bash
# Append to the end (XML passed directly as an argument)
lark-cli slides +add-slide --as user \
  --presentation "$PRES_ID" \
  --slide '<slide xmlns="https://www.larkoffice.com/sml/2.0"><data></data></slide>'

# Read XML from a file (recommended: avoids shell escaping and long-argument truncation)
lark-cli slides +add-slide --as user \
  --presentation "$PRES_ID" \
  --slide @page3.xml

# Read XML from stdin
cat page3.xml | lark-cli slides +add-slide --as user --presentation "$PRES_ID" --slide -

# Insert before a certain page
lark-cli slides +add-slide --as user \
  --presentation "$PRES_ID" \
  --slide @cover.xml \
  --before-slide-id "$SID"

# wiki link (the CLI automatically resolves it through the node_by_token interface and verifies obj_type=slides)
lark-cli slides +add-slide --as user \
  --presentation "https://xxx.feishu.cn/wiki/wikcnXXXXXX" \
  --slide @page3.xml

# Preview the request without actually writing
lark-cli slides +add-slide --presentation "$PRES_ID" --slide @page3.xml --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--presentation` | Yes | `xml_presentation_id`, `/slides/` URL, or `/wiki/` URL |
| `--slide` | Yes | One complete `<slide>...</slide>` document; supports a literal, `@file`, or stdin `-` |
| `--before-slide-id` | No | Insert before that `slide_id`; **if not passed, it is appended to the end** |
| `--revision-id` | No | Presentation version number, defaults to `-1` (latest); pass a specific version number for optimistic locking |
| `--dry-run` | No | Print the request that will be made (including the image upload step) without writing |

The `@file` path **must be within the CWD** (such as `@./plan/page3.xml`); absolute paths and `../` are rejected and report `unsafe file path`.

<a id="本地图片路径-占位符"></a>
## Local images: `@路径` placeholders

Write `<img src="@./chart.png" .../>` in the XML, and the CLI will: first upload each unique local file to this presentation (`parent_type=slide_file`), then replace `src` with the returned `file_token`, and only then submit the page.

Placeholder paths are resolved according to the **CWD at the time the command is executed**, regardless of the directory where `--slide @file` is located; `@./assets/x.png` looks for `$PWD/assets/x.png`.

```bash
lark-cli slides +add-slide --as user \
  --presentation "$PRES_ID" \
  --slide '<slide xmlns="https://www.larkoffice.com/sml/2.0"><data><img src="@./chart.png" topLeftX="100" topLeftY="100" width="320" height="180"/></data></slide>'
```

- If the file does not exist, is not a regular file, or exceeds 20 MB, an error is reported **before calling any interface**, leaving no partial result.
- Deduplication only takes effect **within a single call**: when multiple pages share the same image, looping page by page will re-upload it once per page. For such images, first use [`+media-upload`](lark-slides-media-upload.md) to upload it once, and write `file_token` into each page's `src`.

<a id="成功输出"></a>
## Success output

```json
{
  "xml_presentation_id": "slides_example_presentation_id",
  "slide_id": "slide_example_id",
  "revision_id": 42,
  "before_slide_id": "slide_example_target_id",
  "images_uploaded": 1,
  "issues": "[issue=unsupported_attr tag=<strong> attr=style]"
}
```

| Field | Description |
|------|------|
| `slide_id` | Unique identifier of the newly created page |
| `issues` | String, **only appears when the server has discarded content**: the page was created successfully, but the tags/attributes listed in the parentheses were not written in. If it appears, you must `+screenshot` and review it; do not ignore it as a mere warning; this field is not returned on a clean submission |

<a id="常见错误"></a>
## Common errors

| Symptom | Cause | Solution |
|------|------|------|
| `--slide is not a single complete <slide> document` | Passed the entire XML of `<presentation>`, or concatenated multiple `<slide>` together | Pass only one page at a time; the root element must be `<slide>` |
| `--slide cannot be empty` | `@file` points to an empty file, or stdin has no content | Check the file content |
| 3350001 | The XML structure/escaping has a problem; **or `--before-slide-id` is not a valid `slide_id`** | Prefer switching to `--slide @file` to bypass shell escaping; if page insertion fails, first `+xml-get` to read back and confirm `slide_id`; then troubleshoot according to [workflow/error-handling.md](../workflow/error-handling.md) |
| 1061004 / 403 | The current identity does not have edit permission for this PPT | Check whether you have the `slides:presentation:update` or `slides:presentation:write_only` scope; wiki links additionally require `wiki:node:read`, `@` placeholders additionally require `docs:document.media:upload`; `--as bot` also requires that the bot has edit permission for the target PPT |
