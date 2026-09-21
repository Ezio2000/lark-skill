
<a id="docs-media-insert文档末尾插入图片文件"></a>
# docs +media-insert (insert image/file at end of document)


Combine the three steps "create empty block → upload file → set token" into a single command to insert a local image or file at the **end of the document**.

<a id="来源选择agent-必读"></a>
## Source selection (Agent must read)

> **Highest priority: if the user explicitly specifies a source, strictly follow the user's choice.** The heuristics below only apply when the user has not stated a preference.
>
> - If the user says "insert this screenshot", "use the image in the clipboard", "the one I just copied" → unconditionally use `--from-clipboard`.
> - If the user says "use `~/Downloads/foo.png`", "insert this local file", or gives a specific path → unconditionally use `--file`.
> - If the user has not made either clear → infer using the heuristics in the table below.
>
> Even if the inference seems "better" (for example, the user gave a path but you think using the clipboard is easier), **do not make the decision on your own** to switch sources. If you want to switch, ask first.

Judge in the following order, **do not do it in reverse**:

| User's image source | Command | Prohibited practice |
|----------------|------|----------|
| The image is already in the clipboard (screenshot shortcut, copied from Feishu/browser, copied from a design file) | `--from-clipboard` | ❌ Do not first save the clipboard to a local file and then use `--file`. That adds an extra file I/O step and requires cleaning up temporary files. |
| The image is a real file on disk | `--file <path>` | — |
| The image is a URL | First download to local → `--file`; or use commands related to `drive` | — |

`--from-clipboard` transfers directly through process memory and does not produce temporary files; built-in support on macOS / Windows, Linux requires any one of `xclip` or `wl-paste` or `xsel`.

<a id="剪切板为空时的-fallback"></a>
### Fallback when the clipboard is empty

When `--from-clipboard` fails (the clipboard does not contain an image / has no image / none of the three tools are installed on Linux), the command returns `clipboard contains no image data` (or a similar platform error). **This is not a reason to exit with an error, but a fallback signal.**

**The Agent's standard handling order** (proceed to the next step only after each step fails, do not do them in parallel):

1. First try once with `--from-clipboard`.
2. If it returns a "no image data" type error, **clearly explain to the user that there is no recognizable image in the clipboard**, and ask the user to provide a local file path or copy an image again.
3. After obtaining the local path, use `--file <path>` to retry **the same insert command** (keep other parameters such as `--doc` / `--align` / `--caption` unchanged).

**Prohibited practices**:
- ❌ Do not quietly treat an empty clipboard as "succeeded but nothing inserted". You must notify the user.
- ❌ Do not guess some local file path on your own after the clipboard fails (for example, the most recently modified png). You must have the user provide the path.
- ❌ Do not bypass `--from-clipboard` with the suggestion "first have the user save the clipboard to disk and then `--file`"; fall back to a local path only when the clipboard truly has no image.

<a id="命令"></a>
## Command

```bash
# 🟢 Recommended: insert directly from the clipboard (no need to save to disk first)
lark-cli docs +media-insert --doc doxcnXXX --from-clipboard

# Insert from a local file
# In addition to uploading a local file, you can also insert an image directly via a network URL during `docs +update`, without downloading it locally first:
lark-cli docs +update --doc "<doc_id>" --command block_insert_after \
  --block-id "目标 block_id" \
  --content '<img href="https://example.com/photo.png"/>'

# Insert image (default)
lark-cli docs +media-insert --doc doxcnXXX --file ./image.png

# doc supports passing a docx URL directly (automatically extracts document_id)
lark-cli docs +media-insert --doc "https://xxx.feishu.cn/docx/doxcnXXX" --from-clipboard

# If the previous step was create-doc, prefer passing the doc_id from the return value
# Do not pass a doc_url in the form /wiki/... directly to docs +media-insert
lark-cli docs +media-insert --doc doxcnReturnedByCreateDoc --file ./image.png

# Insert file (non-image)
lark-cli docs +media-insert --doc doxcnXXX --file ./spec.pdf --type file

# Image alignment and description (caption)
lark-cli docs +media-insert --doc doxcnXXX --from-clipboard --align center --caption "架构图"

# Insert image with explicit display width (height auto-computed from aspect ratio)
lark-cli docs +media-insert --doc doxcnXXX --file ./banner.png --width 800 --align center

# Insert image with explicit width and height
lark-cli docs +media-insert --doc doxcnXXX --from-clipboard --width 800 --height 447 --caption "architecture diagram"
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--doc <id>` | Yes | Document ID or docx URL (only supports automatic extraction of the `/docx/<document_id>` form; **does not support automatic extraction of `/wiki/...` URLs**) |
| `--from-clipboard` | Choose one of two | Read an image from the system clipboard (mutually exclusive with `--file`). Built-in support on macOS/Windows; Linux requires one of `xclip` / `wl-paste` / `xsel`. |
| `--file <path>` | Choose one of two | Local file path (automatically switches to chunked upload when the file is larger than 20MB) |
| `--type <type>` | No | `image` (default) or `file`. `--from-clipboard` currently only produces image. |
| `--align <align>` | No | Image only: `left` / `center` (default) / `right` |
| `--caption <text>` | No | Image only: image description |
| `--width <px>` | No | Image display width in pixels (only for `--type=image`). If `--height` is omitted, it is auto-computed from the source image aspect ratio. Supported auto-detection formats: PNG, JPEG, GIF; other formats (WebP, BMP, etc.) require both `--width` and `--height`. |
| `--height <px>` | No | Image display height in pixels (only for `--type=image`). If `--width` is omitted, it is auto-computed from the source image aspect ratio. Supported auto-detection formats: PNG, JPEG, GIF; other formats (WebP, BMP, etc.) require both `--width` and `--height`. |

> [!IMPORTANT]
> If the previous step was [`lark-doc-create`](lark-doc-create.md), and in a knowledge base/knowledge space scenario it returned a `doc_url` in the form `/wiki/...`, then when subsequently calling `docs +media-insert` you should prefer passing `doc_id`, and not pass this `doc_url` directly.

<a id="平台注意仅---from-clipboard"></a>
## Platform notes (only `--from-clipboard`)

| Platform | Dependency | Typical error |
|------|------|---------|
| macOS | osascript (built-in) | Clipboard empty / not an image → "clipboard contains no image data" |
| Windows | PowerShell + System.Windows.Forms (built-in) | Same as above |
| Linux | Any one of `xclip` or `wl-paste` or `xsel` | None installed → the error will prompt you to install using your distribution's package manager |

The command does not support reading uncommon formats such as TIFF that are not PNG/JPEG/GIF/WebP/BMP; when encountering such a clipboard it returns "contains no image data", and only then should you consider first converting it to a file using system tools and then using `--file`.

<a id="输出"></a>
## Output

After the command succeeds, it outputs JSON containing: `document_id`, `block_id`, `file_token`, `file_name` (under the clipboard path this is `clipboard.png`), `type`.

> [!CAUTION]
> This is a **write operation** (it modifies document content) — you must confirm the user's intent before executing.

<a id="参考"></a>
## References

- [lark-doc-fetch](lark-doc-fetch.md) — fetch document content (can be used to confirm the result after insertion, and to extract media tokens)
- [lark-shared](../../shared/index.md) — authentication and global parameters
