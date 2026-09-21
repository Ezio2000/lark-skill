<a id="slides-update-slide整页更新已有页面"></a>
# slides +update-slide (full-page update of an existing page)

Hand an entire page of XML to an existing page, and the page becomes what `--content` describes. `slide_id` and the page order stay unchanged.

<a id="命令"></a>
## Command

```bash
# Standard usage: read the full-page XML from a file (recommended: avoids shell escaping and long-argument truncation)
lark-cli slides +update-slide --as user \
  --presentation "https://xxx.larkoffice.com/slides/SCtZ...ynae" \
  --slide-id "piy" \
  --content @page.xml

# Read XML from stdin
cat page.xml | lark-cli slides +update-slide --as user \
  --presentation "$PRES" --slide-id "$SLIDE" --content -

# Pass the wiki link directly (the CLI resolves it automatically and validates obj_type=slides)
lark-cli slides +update-slide --as user \
  --presentation "https://xxx.larkoffice.com/wiki/wikcn..." \
  --slide-id "piy" --content @page.xml

# Preview the request without actually writing
lark-cli slides +update-slide --as user \
  --presentation "$PRES" --slide-id "$SLIDE" --content @page.xml --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--presentation` | Yes | `xml_presentation_id`, `/slides/` URL, or `/wiki/` URL |
| `--slide-id` | Yes | The page `slide_id` to replace in full |
| `--content` | Yes | The complete target XML for this page, a single `<slide>` root; supports a literal, `@file`, and stdin `-`. Aliases: `--xml` / `--slide-xml` / `--slide-content` / `--content-xml` |
| `--revision-id` | No | Defaults to `-1` (latest). It only selects the snapshot on which the server-side execution is based; it is not an optimistic lock that "rejects if the page has new edits". Passing an old version number rebuilds the page from the old snapshot and discards any edits made after it |
| `--tid` | No | A task/transaction identifier provided by the caller, passed through by the CLI as-is; used to associate the same editing task or retries, it is not equivalent to a version precondition and cannot by itself guarantee that writes are rejected on concurrent conflicts. Generally left empty |

Like `+xml-get --output`, `@file` **only accepts relative paths under the current directory**; absolute paths are rejected.
Command alias: `slides +update` (hidden).

If the requirement is "once the page changes after reading, do not write again", you cannot rely on passing only `--revision-id` or `--tid`. Before writing, you must read back the latest version again with `+xml-get` and compare whether anything changed during the read; if there is a change, first re-merge this modification based on the latest version, then perform the full-page write-back. The current shortcut does not provide a strict compare-and-swap guarantee.

<a id="语义--content-就是这一页的最终状态"></a>
## Semantics: `--content` is the final state of this page

**Anything not written into `--content` disappears from the page.** This is not a patch; it is a full-page overwrite.

| How you write it in `--content` | Result on the page |
|---|---|
| An element carries its original `id` | Update this element according to the new XML |
| An element does not carry `id` | Insert it as a new element at its position |
| An element that existed before but is not in `--content` | **Delete** |
| `<style>` changed | Page styles such as the background change accordingly |
| `<note>` not written | Speaker notes are cleared |

A single request can simultaneously change styles, insert, delete, change notes, and change the background—something `+replace-slide` per-element part cannot do (it cannot address the background, and it has no move operation).

<a id="本地图片路径-占位符"></a>
## Local images: `@路径` placeholder

Write `<img src="@./chart.png" .../>` in the XML of `--content`, and the CLI will: first upload each unique local file to this presentation (`parent_type=slide_file`), then replace `src` with the returned `file_token`, and only then write back the full page.

Placeholder paths are resolved relative to the **CWD at the time the command is executed**, regardless of the directory where `--content @file` is located; `@./assets/x.png` looks for `$PWD/assets/x.png`.

```bash
lark-cli slides +update-slide --as user \
  --presentation "$PRES" --slide-id "$SLIDE" \
  --content '<slide xmlns="https://www.larkoffice.com/sml/2.0"><data><img src="@./chart.png" topLeftX="100" topLeftY="100" width="320" height="180"/></data></slide>'
```

- If the file does not exist, is not a regular file, or exceeds 20 MB, an error is reported **before calling any API**, leaving no half-finished result.
- Deduplication only takes effect **within a single call**: when multiple pages share the same image, updating page by page re-uploads it once per page. For such images, first upload it once with [`+media-upload`](lark-slides-media-upload.md), and write `file_token` into the `src` of each page.
- The entire page is sent as a single part, so uploading is the **only irreversible half** of this command: the image first lands in the presentation's media store, and if the subsequent replace fails, the error hint will tell you how many images have already been uploaded, and retrying directly will upload another copy. Running `--dry-run` first lets you see `images_to_upload` and the upload steps in advance.

<a id="标准读-改-写流程"></a>
## Standard read-modify-write flow

```bash
# 1. Read back the current page (to get the complete XML with ids)
lark-cli slides +xml-get --as user \
  --presentation "$PRES" --slide-id "$SLIDE" --output page.xml

# 2. Edit page.xml — keep the ids of elements you want to keep, delete entire sections you do not want, and do not write ids for new elements

# 3. Write back the full page
lark-cli slides +update-slide --as user \
  --presentation "$PRES" --slide-id "$SLIDE" --content @page.xml
```

Run `--dry-run` first to see the request, and execute only after confirming it is correct.

> ⚠️ **Do not add `--remove-attr-id` in step 1.** That parameter strips the `id` from all elements; if you then hand it to `+update-slide`, every element will be treated as a new element to insert and all the originals will be deleted—the page will look the same, but all elements will have new ids, and comments and block direct links anchored to the old ids will all become invalid, and **no error will be reported**. `--remove-attr-id` is only for read-only viewing.

<a id="命令校验与空页限制"></a>
## Command validation and empty-page restriction

| Situation | Error |
|---|---|
| The root element is not `<slide>` (for example, `<shape>` was given directly) | `--content root must be <slide>` → to change a single element, use `+replace-slide` |
| The root `id` and `--slide-id` do not match | Rejected. This usually means the XML of page A is about to be written to page B — it would destroy page B |
| The root `id` is missing | Automatically add `--slide-id`, no error |
| The root tag has a namespace prefix (`<sml:slide>`) | Rejected. The page id cannot be attached to a prefixed tag; write `<slide>`, and if a namespace is needed, use the default `xmlns` |
| There is a second root element or extra text after `<slide>` | Rejected. Server-side parsing would silently drop them |
| Invalid XML | Rejected, with the error location |
| `<slide/>` (self-closing, empty page) | The command itself can parse it, but the mandatory layout lint before submission reports `blank_slide`; according to this module, do not call the API to submit an empty page |

Cases marked "rejected" are intercepted by command validation and **no request is sent**; an empty page must be intercepted by the mandatory layout lint before calling the command.

<a id="什么时候不要用它"></a>
## When not to use it

- **Changing only one element** → use [`+replace-slide`](lark-slides-replace-slide.md); a single `block_replace` part is more economical and does not require carrying the whole page
- **Changing multiple pages** → run this command once for each page
- **Creating a new page** → `slides +create` or `slides +add-slide`

<a id="提交前与写入后验证"></a>
## Pre-submission and post-write verification

As with other full-page writes, save `--content` to a local file and run the layout lint first. First obtain the parent directory of the currently loaded `lark-slides/index.md`, recorded as `<lark-root>/references/slides`; do not guess the global installation path:

```bash
uv run python "<lark-root>/references/slides/scripts/xml_lint.py" --input page.xml
```

`summary.error_count` must be 0 before calling the API; when it is `warning_count > 0`, take a screenshot for review after writing.

After a successful write, you must read back the latest XML of the entire presentation, rather than trusting only the success response of the write API:

```bash
lark-cli slides +xml-get --as user \
  --presentation "$PRES" --output readback.xml
```

Complete verification according to [validation-xml.md](../workflow/validation-xml.md) pointed to by the currently loaded `lark-slides/index.md`: check the total page count, the target page, and key elements (including IDs, text, background, and notes that need to be preserved), and run the same layout lint on the read-back XML; if a discrepancy is found, stop subsequent writes first and reprocess based on the latest version.

<a id="成功输出"></a>
## Success output

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "xml_presentation_id": "slides_example_presentation_id",
    "slide_id": "piy",
    "revision_id": 43
  }
}
```

| Field under `data` | Description |
|------|------|
| `xml_presentation_id` | The presentation ID actually written to |
| `slide_id` | Same as passed in—a full-page overwrite does not change the page id |
| `revision_id` | The new version number after writing |
| `images_uploaded` | Appears only when `--content` carries the `@` placeholder: the number of images actually uploaded after deduplication in this call |

When the server rejects this write (`failed_reason` is non-empty), it **does not** return a success output; instead it reports an error with the reason—a single part carries the entire page, so any failure means the page was not written.

- If the reason contains `not found`: first check `--presentation` and `--slide-id`, then use `slides +xml-get` to read back the current page ID. The page may have been deleted, or the ID may come from another presentation.
- Other invalid-parameter errors: check `--content` for unsupported elements, `<shape>` missing `<content/>`, and coordinates exceeding 960×540.

<a id="常见错误"></a>
## Common errors

| Symptom | Cause | Solution |
|------|------|------|
| 3350001, reason contains `not found` | `--presentation` does not match, or the page corresponding to `--slide-id` has been deleted | Check `--presentation` and `--slide-id`, then use `slides +xml-get` to read back the current page ID |
| 3350001, other invalid param | The XML structure of `--content` has a problem (such as `<shape>` missing `<content/>`, or containing elements unsupported by the server) | Check the XML structure of `--content` according to [error-handling.md](../workflow/error-handling.md) |
| 3350002 not found | `--revision-id` passed a version number that does not exist | Use `-1` or a real existing `revision_id` |
| 1061004 / 403 | The current identity does not have edit permission for this PPT | Check whether it has the `slides:presentation:update` or `slides:presentation:write_only` scope; a wiki link additionally requires `wiki:node:read`, the `@` placeholder additionally requires `docs:document.media:upload`; `--as bot` also requires that the bot has edit permission for the target PPT |
