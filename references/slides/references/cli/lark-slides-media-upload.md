<a id="slides-media-upload上传本地图片到飞书幻灯片"></a>
# slides +media-upload (Upload a local image to Lark Slides)

Upload a local image to the drive media library of a specified presentation, returning `file_token`. **Put the returned token as the value of `<img src="...">` into the slide XML to display the image.**

<a id="命令"></a>
## Command

```bash
# Pass xml_presentation_id directly
lark-cli slides +media-upload --as user \
  --file ./pic.png \
  --presentation slidesXXXXXXXXXXXXXXXXXXXXXX

# Passing a slides URL also works
lark-cli slides +media-upload --as user \
  --file ./chart.png \
  --presentation "https://xxx.feishu.cn/slides/slidesXXXXXXXXXXXXXXXXXXXXXX"

# Pass a wiki URL (the CLI automatically resolves the real token via the node_by_token API and validates obj_type=slides)
lark-cli slides +media-upload --as user \
  --file ./pic.png \
  --presentation "https://xxx.feishu.cn/wiki/wikcnXXXXXX"

# Preview (no actual upload)
lark-cli slides +media-upload --file ./pic.png --presentation $PRES_ID --dry-run
```

<a id="返回值"></a>
## Return Value

```json
{
  "file_token": "boxcnXXXXXXXXXXXXXXXXXXXXXX",
  "file_name": "pic.png",
  "size": 12345,
  "presentation_id": "slidesXXXXXXXXXXXXXXXXXXXXXX"
}
```

- **`file_token`**: write it into `<img src="...">`
- **`file_name` / `size`**: uploaded file metadata
- **`presentation_id`**: the resolved real `xml_presentation_id` (it changes after a wiki URL is resolved)

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file` | Yes | Local image path, **must be a relative path within the CWD** (e.g. `./pic.png`). **Maximum 20 MB** (media upload does not support chunking). **Only png / jpeg / gif / bmp / tiff / webp are supported** |
| `--presentation` | Yes | `xml_presentation_id`, `/slides/<token>` URL, or `/wiki/<token>` URL |

> [!IMPORTANT]
> **The path must be within the CWD**: `--file /abs/path/x.png` or `--file ../up/x.png` will be rejected by the CLI (reporting `unsafe file path`). If the asset is in another directory, `cd` there first before running.

<a id="使用流程"></a>
## Usage Flow

> Creating a new PPT ([`+create --slides`](lark-slides-create.md)) or adding a new page to an existing PPT ([`+add-slide`](lark-slides-add-slide.md)) does not require a separate upload: write `<img src>` as `@<本地路径>` in the XML, and the CLI will automatically upload and replace it with `file_token`.
> This command is for adding an image to an **existing page**, or for scenarios where you need to assemble XML yourself with `file_token`.

<a id="给已有-ppt-的已有页加图"></a>
### Add an image to an existing page of an existing PPT

After obtaining `file_token`, use `block_insert` of [`+replace-slide`](lark-slides-replace-slide.md); no need to move the original XML, change `slide_id`, or disturb the page order:

```bash
PRES_ID=xxx
SID=yyy       # The page to add the image to

# 1) Upload the image to get the file_token
TOKEN=$(lark-cli slides +media-upload --as user \
  --file ./pic.png --presentation $PRES_ID --jq '.data.file_token')

# 2) block_insert to the end of the page (or use insert_before_block_id to specify the insertion position)
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --parts "$(jq -n --arg token "$TOKEN" \
    '[{action:"block_insert",insertion:("<img src=\""+$token+"\" topLeftX=\"500\" topLeftY=\"100\" width=\"200\" height=\"150\"/>")}]')"
```

Notes:

1. **`<img>` coordinates should avoid existing elements** — first read the bbox of existing elements to pick a blank area; if there is not enough space, first use `block_replace` to move/shrink existing elements before placing the image
2. **`width:height` of `<img>` should match the original image's aspect ratio** — a mismatched ratio will be cropped; see the `<img>` description in [xml-schema-quick-ref.md](../xml/xml-schema-quick-ref.md)

<a id="上传约束"></a>
## Upload Constraints

`+media-upload` handles the media ownership parameters required by Slides; the caller only needs to pass `--file` and `--presentation`. A single image is at most 20 MB.

<a id="常见错误"></a>
## Common Errors

| Error Code | Meaning | Solution |
|--------|------|----------|
| 1061002 | params error / unsupported parent_type | Use `+media-upload`; it adopts the `parent_type` required by Slides |
| 1061004 | forbidden: the current identity has no edit permission on this presentation | Confirm that the current identity (user or bot) has edit permission on the target PPT. A common cause in bot mode: the PPT was not created by that bot — you can create a new one with `+create --as bot`, or run `lark-cli drive +member-add --as user --token "$PRES_ID" --type slides --member-id "$BOT_OPEN_ID" --member-type openid --perm full_access --yes` as a user to grant the bot authorization |
| 1061044 | parent node not exist | The token given by `--presentation` is incorrect, or it is not of slides type |
| 403 | Insufficient permission | Check the `docs:document.media:upload` scope; a wiki URL also requires `wiki:node:read` |

<a id="相关命令"></a>
## Related Commands

- [+create](lark-slides-create.md) — Create a new PPT (supports automatic image upload via the `@` placeholder)
- [+replace-slide](lark-slides-replace-slide.md) — Add an image to / replace an image on an existing page (`block_insert` / `block_replace`)
- [+add-slide](lark-slides-add-slide.md) — Append/insert a single page (also supports automatic upload via the `@` placeholder)
