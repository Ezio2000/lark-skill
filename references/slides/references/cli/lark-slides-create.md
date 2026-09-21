
<a id="slides-create创建飞书幻灯片"></a>
# slides +create (Create a Feishu Slides presentation)

Create a new Feishu Slides presentation, optionally adding page content in one step.

The submission source must be directly generated single-page `<slide>` XML. It is forbidden to parse, split, or re-serialize a slide array from a complete `<presentation>` XML and then submit it.

This command only creates a presentation from scratch; there is no parameter for importing a local PPT file. To turn an existing PPTX into Slides, use `drive +import --file <x.pptx> --type slides`, then edit the import result. For the workflow, see [template-editing.md](../workflow/template-editing.md).

<a id="创建方式选择"></a>
## Choosing a creation method

| Scenario | Recommended method |
|------|----------|
| No more than 10 pages | Save one XML file per page, create in one step with `slides +create --slide @page-01.xml --slide @page-02.xml ...` |
| More than 10 pages | **Two-step creation**: first use `slides +create` to create a blank PPT, then use [`+add-slide`](lark-slides-add-slide.md) to add pages one by one |
| An existing PPT to continue appending to or insert pages into | Use [`+add-slide`](lark-slides-add-slide.md), with `--before-slide-id` if necessary |

> [!IMPORTANT]
> When `slides +create` includes pages, it creates them page by page under the hood; it is not an atomic operation. If it fails midway, first record `xml_presentation_id`, read back to confirm the current state, then continue repairing or appending.

**CRITICAL — you must run layout lint before submitting**: save the `<slide>` XML to be submitted as a local file, run [`scripts/xml_lint.py`](../../scripts/xml_lint.py), and `summary.error_count` must be 0.

<a id="命令"></a>
## Command

```bash
# Create a blank PPT
lark-cli slides +create --title "项目汇报"

# Create a PPT + add pages: one XML file per page, repeat --slide; the order is the page order
lark-cli slides +create --as user --title "项目汇报" \
  --slide @.lark-slides/plan/project/slide-01.xml \
  --slide @.lark-slides/plan/project/slide-02.xml

# An already-assembled JSON array: read from a file or stdin
lark-cli slides +create --as user --title "项目汇报" --slides @./deck.json
cat deck.json | lark-cli slides +create --as user --title "项目汇报" --slides -

# Create as an app identity (automatically authorizes the current user)
lark-cli slides +create --title "项目汇报" --as bot

# Preview (do not execute)
lark-cli slides +create --title "项目汇报" --slide @./slide-01.xml --dry-run
```

<a id="返回值"></a>
## Return value

After the tool executes successfully, it returns a JSON object containing the following fields:

- **`xml_presentation_id`** (string): the unique identifier of the presentation; this ID is needed when adding pages later
- **`title`** (string): the presentation title
- **`url`** (string, optional): the online link to the presentation; if returned, be sure to show it to the user (requires drive-related permissions; if retrieval fails, this field is not returned)
- **`revision_id`** (integer): the presentation version number
- **`slide_ids`** (string[], optional): returned when creating with pages; the list of successfully added page IDs
- **`slides_added`** (integer, optional): returned when creating with pages; the number of successfully added pages
- **`images_uploaded`** (integer, optional): returned when the page XML contains the `@<本地路径>` placeholder; the number of uploaded images after deduplication
- **`permission_grant`** (object, optional): returned only with `--as bot`; indicates whether manageable permission has been automatically granted to the current CLI user

> [!IMPORTANT]
> When no page parameters are provided, `slides +create` only creates a blank presentation. After creation, use [`+add-slide`](lark-slides-add-slide.md) to add slide content page by page.
>
> When pages are provided, the CLI first creates a blank presentation, then adds pages one by one. If adding a page fails, the CLI stops and reports an error; the already-created presentation and already-added pages are retained.
>
> If the presentation is **created with an app identity (bot)**, such as `lark-cli slides +create --as bot`, the CLI will **attempt to automatically grant the current CLI user `full_access` (manageable permission) on that presentation**.
>
> When creating with an app identity, the result additionally returns the `permission_grant` field, explicitly stating the authorization result:
> - `status = granted`: the current CLI user has been granted manageable permission on the presentation
> - `status = skipped`: there is no available current user `open_id` locally, so authorization is not performed automatically
> - `status = failed`: the presentation was created successfully, but automatically authorizing the user failed
>
> **Do not perform owner transfer on your own initiative.** Creating or importing does not imply owner transfer; when the user has explicitly requested a transfer and the target is determined, proceed with the authorization.

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--title` | No | Presentation title (defaults to "Untitled" if not provided) |
| `--slide` | No | One page of `<slide>` XML, or `@路径`; can be repeated, up to 10 times. For the format, see [Page input forms](#页面输入形式) |
| `--slides` | No | A JSON string array of page XML, up to 10; supports `@文件` and `-` (stdin). For the format, see [Page input forms](#页面输入形式) |

10 pages is the CLI limit; the server only accepts one page at a time. When there are more than 10 pages, first use `+create` to create a blank PPT, then use [`+add-slide`](lark-slides-add-slide.md) to add pages one by one.

Each page in both forms is validated before the request is sent to ensure it is "a single complete `<slide>` document". A non-conforming page reports an error before the presentation is created and indicates the page number, so no empty-shell presentation is left behind.

<a id="页面输入形式"></a>
## Page input forms

Page content can be passed in two ways, `--slide` and `--slides`; choose one. Passing both at the same time reports an error.

For both forms, `@路径` must be a relative path within the CWD (such as `./slide-01.xml`); absolute paths and `../` are rejected (reporting `invalid file path`). If the XML is in another directory, first `cd` over there or copy the file into the CWD before executing.

<a id="--slide一页一个文件"></a>
### `--slide`: one file per page

Can be repeated; the number of repetitions is the number of pages, and the order of appearance is the page order. The value is one complete page of `<slide>` XML, or a `@路径` that reads that XML.

The file content is the page XML itself, with no quotes or square brackets around it:

```xml
<slide xmlns="https://www.larkoffice.com/sml/2.0">
  <data>…第1页…</data>
</slide>
```

The file content does not need escaping: quotes, newlines, and Chinese are written as-is.

<a id="--slides一个-json-数组"></a>
### `--slides`: one JSON array

The value is a JSON string array, where each element is a full page of XML; supports `@文件` and `-` (stdin).

The file content is a JSON document, with the XML appearing as JSON strings, where `"` is written as `\"` and newlines are written as `\n`:

```json
[
  "<slide xmlns=\"https://www.larkoffice.com/sml/2.0\"><data>…第1页…</data></slide>",
  "<slide xmlns=\"https://www.larkoffice.com/sml/2.0\"><data>…第2页…</data></slide>"
]
```

The array elements are the raw page XML; request wrapping and page-by-page submission are handled by `+create`.

> [!WARNING]
> The risk of `--slides '[...]'` lies mainly in shell argument passing, not simply the number of pages. Even with only 1 page, as long as the XML is complex enough, it is recommended to switch to `--slide @page-01.xml` to pass files page by page.

<a id="本地图片path-占位符"></a>
<a id="本地图片-占位符"></a>
## Local images: the `@<path>` placeholder

If the `src` attribute of a `<img>` element starts with `@`, the CLI treats it as a local file path, automatically uploads it to the current presentation, and replaces the placeholder with the returned `file_token`.

`slide-01.xml`:

```xml
<slide xmlns="https://www.larkoffice.com/sml/2.0">
  <data>
    <img src="@./assets/chart.png" topLeftX="100" topLeftY="100" width="320" height="180"/>
  </data>
</slide>
```

```bash
lark-cli slides +create --as user --title "图测试" --slide @./slide-01.xml
```

Behavior:

- Paths are resolved relative to the **current working directory** (CWD); **must be a relative path within the CWD** (such as `./pic.png`, `./assets/x.png`)
- When the same image is referenced multiple times, it is **uploaded only once** (deduplicated by path)
- `src` that does not start with `@` is kept as-is, but **only `file_token` obtained from `slides +media-upload` may be written**; **writing http(s) external link URLs is forbidden**: the Feishu slides rendering side does not proxy external images, and external src usually shows a broken image. To use an online image, you must first download it into the CWD, then go through the upload flow
- A single image is at most 20 MB (media upload does not support multipart)
- During the validation stage, the existence and size of all placeholder files are checked; a missing file or an over-limit file reports an error directly, and no blank PPT placeholder is created
- Create blank PPT → upload all images → replace tokens → create slides page by page, executed in this order

> [!IMPORTANT]
> **The path must be within the CWD**: `@/abs/path/x.png` or `@../up/x.png` will be rejected by the CLI (reporting `unsafe file path`). If the assets are in another directory, first `cd` over there before executing.

<a id="创建后续步骤"></a>
## Follow-up steps after creation

When creating a blank PPT, the `xml_presentation_id` returned by `slides +create` is used for subsequent operations:

```bash
# Step 1: Create a blank PPT
PRES_ID=$(lark-cli slides +create --title "项目汇报" --jq '.data.xml_presentation_id')

# Step 2: Add page by page (--slide supports @file; for complex XML, prefer files)
lark-cli slides +add-slide --as user \
  --presentation "$PRES_ID" \
  --slide @.lark-slides/plan/<deck>/page1.xml
```

<a id="常见错误"></a>
## Common errors

| Error code | Meaning | Solution |
|--------|------|----------|
| 400 | Parameter error | Check whether the parameter format is correct |
| 403 | Insufficient permission | Check whether you have the `slides:presentation:create` and `slides:presentation:write_only` scopes |

<a id="相关命令"></a>
## Related commands

- [slides +add-slide](lark-slides-add-slide.md) — append/insert a single page (the second step of two-step creation)
- [slides +xml-get](lark-slides-xml-presentations-get.md) — read PPT content and save it to a local file
