# slides +screenshot

<a id="用途"></a>
## Purpose

Capture a screenshot of a slide page and save it as a local image file. By default it is used to screenshot an existing PPT page; when `--content` is passed, it is used to directly render a preview of a single `<slide>` XML fragment. This shortcut decodes and writes the file within the CLI process; stdout returns only metadata such as the file path, size, and page ID, avoiding outputting the image Base64 to the model.

If the screenshot fails, it degrades to non-screenshot check paths such as XML read-back and structural lint.

<a id="命令"></a>
## Command

```bash
lark-cli slides +screenshot --as user \
  --presentation '<xml_presentation_id 或 slides/wiki URL>' \
  --slide-number 1
```

Render local XML content:

```bash
lark-cli slides +screenshot --as user \
  --content @slide.xml
```

<a id="截图全部页面"></a>
## Screenshot all pages

Enumerate the `slide_id` or page numbers of all pages, group them into batches of at most 10 pages each, and call `slides +screenshot` serially, reusing the same `--output-dir`; record failed batches, and do not re-execute completed batches.

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--presentation` | Required in list mode | `xml_presentation_id`, `/slides/` URL, or a `/wiki/` URL that resolves to slides. Cannot be used when `--content` is passed |
| `--slide-id` | Choose one of list mode and `--slide-number` | Page short ID; cannot be used together with `--slide-number`; for multi-page screenshots, pass it repeatedly, or pass multiple at once separated by commas (e.g. `--slide-id slide_1,slide_2`); at most 10 IDs at a time |
| `--slide-number` | Choose one of list mode and `--slide-id` | Page number; cannot be used together with `--slide-id`; for multi-page screenshots, pass it repeatedly, or pass multiple at once separated by commas (e.g. `--slide-number 1,2,3`); at most 10 page numbers at a time |
| `--content` | Required in render mode | The `<slide>` XML fragment to render directly; supports passing the value directly, `@file`, or `-` stdin. Once passed, `--slide-id` / `--slide-number` cannot be passed at the same time |
| `--output` | No | The desired relative output path for a single screenshot; the extension may be omitted, and explicit extensions only support `.png`, `.jpg`, `.jpeg`. Only one page can be selected, and it cannot be used together with `--output-dir` / `--output-name`; the final path is subject to the returned `output` |
| `--output-dir` | No | Output directory, defaults to `.lark-slides/screenshots`; must be a relative path within the current directory |
| `--output-name` | No | Only used in `--content` render mode to set the output filename stem. Passing this parameter for a normal page screenshot returns `validation/invalid_argument` (`param: --output-name`) and prompts to use `--output` instead |

<a id="示例"></a>
## Examples

<a id="单页截图并固定路径"></a>
### Single-page screenshot with a fixed path

```bash
lark-cli slides +screenshot --as user \
  --presentation slides_example_presentation_id \
  --slide-number 1 \
  --output .lark-slides/screenshots/example-deck-task/page-01
```

When selecting a single page by `slide_id`, `--output` is likewise used:

```bash
lark-cli slides +screenshot --as user \
  --presentation slides_example_presentation_id \
  --slide-id slide_example_id \
  --output .lark-slides/screenshots/example-deck-task/page-01
```

<a id="多页截图"></a>
### Multi-page screenshot

Do not exceed 10 pages at a time; if more pages are needed, call in batches. You can pass the parameter repeatedly, or pass multiple at once separated by commas:

```bash
lark-cli slides +screenshot --as user \
  --presentation slides_example_presentation_id \
  --slide-number 1 \
  --slide-number 2 \
  --output-dir .lark-slides/screenshots/example-deck-task
```

<a id="渲染-xml-预览"></a>
### Render XML preview

```bash
lark-cli slides +screenshot --as user \
  --content @.lark-slides/out/demo/slide.xml \
  --output .lark-slides/screenshots/example-deck-task/preview
```

<a id="返回值"></a>
## Return value

The returned JSON does not contain Base64 image content:

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "xml_presentation_id": "slides_example_presentation_id",
    "output": "/abs/path/.lark-slides/screenshots/example-deck-task/page-01.jpg",
    "screenshots": [
      {
        "slide_id": "slide_example_id",
        "slide_number": 1,
        "format": "jpeg",
        "path": "/abs/path/.lark-slides/screenshots/example-deck-task/page-01.jpg",
        "size": 12345
      }
    ]
  }
}
```

<a id="注意事项"></a>
## Notes

1. Prefer using `slides +screenshot` to save local images; do not print the image Base64 to stdout.
2. When screenshotting an existing PPT page, do not pass `--content`; use `--presentation` + `--slide-id` or `--slide-number`.
3. For local XML preview, pass `--content @file` or `--content -`, and the content should be a single `<slide>` XML fragment; at this time do not pass `--presentation` / `--slide-id` / `--slide-number`.
4. `slide_id` is the page short ID; for page numbers use `--slide-number`.
5. In list mode, `--slide-id` and `--slide-number` must be chosen one of the two; at most 10 selectors of the same type can be passed at a time, and for more pages, screenshot in batches.
6. Use `--output` for a single image and `--output-dir` for multiple images; the CLI generates filenames based on page information. When creating or substantially rewriting a Deck, the screenshot directory reuses the `<deck-or-task-id>` from the planning stage; when an existing Deck has no task ID, use the presentation ID as the directory name.
7. The CLI does not convert image formats, nor does it require the model to predict the server-side format. When no extension is written, the real extension is automatically appended; when the requested extension does not match the real format, the directory and name are kept and the extension is corrected, for example, when `slide3.png` is requested but the server returns JPEG, it is actually saved as `slide3.jpg`.
8. When extension correction or same-name avoidance occurs, the original `requested_output`, the actual absolute path `output`, and `output_adjusted: true` are returned; subsequently, `output` / `screenshots[].path` must be used, and do not continue guessing the requested path.
9. In list mode, the default filename includes the presentation ID, page number, and/or slide ID.
10. Screenshots come from server-side rendering results and are suitable for verifying after creation/replacement whether a page is blank, has broken images, or has obviously abnormal layout.
