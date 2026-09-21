
# drive +add-comment


Add a comment to a document, a supported Drive regular file, a spreadsheet, Feishu Slides, or Base. When no location is specified, a full-text comment is created, but this only applies to doc/docx, whitelisted Drive files, and wikis that resolve to these types; sheet, slides, and Base (bitable) must specify `--block-id`. The `--block-id` formats for different types are described below. Supports passing a docx URL/token, legacy doc URL (full-text comments only), Drive file URL/token (**only whitelisted extensions are supported, and only full-text comments are supported**), sheet URL, slides URL, base/bitable URL, and also supports passing a wiki URL that ultimately resolves to doc/docx/file/sheet/slides/base(bitable).

<a id="命令"></a>
## Command

```bash
# Default: add a full-text comment when no location is specified
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/docx/<DOC_ID>" \
  --content '[{"type":"text","text":"请补充发布说明"}]'

# It can also be explicitly specified as a full-text comment; legacy doc URLs only support full-text comments
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/doc/<DOC_ID>" \
  --full-comment \
  --content '[{"type":"text","text":"请补充旧版文档的背景信息"}]'

# Wiki links also work; the shortcut first resolves to the real doc/docx token
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/wiki/<WIKI_TOKEN>" \
  --content '[{"type":"text","text":"这里需要一段全文评论"}]'

# Add a full-text comment to a supported Drive regular file
# Note: the CLI first queries drive metas; only whitelisted extensions are allowed to be commented on
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/file/<FILE_TOKEN>" \
  --content '[{"type":"text","text":"请补充文件说明"}]'

# Bare tokens are also supported, but --type file must be explicitly declared
lark-cli drive +add-comment \
  --doc "<FILE_TOKEN>" --type file \
  --content '[{"type":"text","text":"请补充目录说明"}]'

# Add a local comment to a specified block of a docx document (block_id can be obtained via docs +fetch --detail with-ids)
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/docx/<DOC_ID>" \
  --block-id "<BLOCK_ID>" \
  --content '[{"type":"text","text":"请补充流程说明"}]'

# Wiki links also support local comments; the resolution result can be docx/sheet/slides, and the block-id format is passed according to the target type
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/wiki/<WIKI_TOKEN>" \
  --block-id "<BLOCK_ID>" \
  --content '[{"type":"text","text":"请补充更细的开发步骤"}]'

# Combine text, @user, and link elements
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/docx/<DOC_ID>" \
  --block-id "<BLOCK_ID>" \
  --content '[{"type":"text","text":"请 "},{"type":"mention_user","text":"ou_xxx"},{"type":"text","text":" 处理，参考 "},{"type":"link","text":"https://example.com"}]'

# Add a comment to a spreadsheet cell (--block-id format is <sheetId>!<cell>)
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/sheets/<SHEET_TOKEN>" \
  --block-id "<SHEET_ID>!D6" \
  --content '[{"type":"text","text":"请检查此单元格数据"}]'

# Sheets pointed to by wiki links are also supported
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/wiki/<WIKI_TOKEN>" \
  --block-id "<SHEET_ID>!A1" \
  --content '[{"type":"text","text":"请 "},{"type":"mention_user","text":"ou_xxx"},{"type":"text","text":" 确认"}]'

# Add a comment to a slide element (--block-id format is <slide-block-type>!<xml-id>)
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/slides/<PRESENTATION_ID>" \
  --block-id "<SLIDE_BLOCK_TYPE>!<XML_ELEMENT_ID>" \
  --content '[{"type":"text","text":"请调整这个元素的位置"}]'

# For example: add a comment to an entire slide page
# <slide id="pkk"> ... </slide>  =>  --block-id slide!pkk
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/slides/<PRESENTATION_ID>" \
  --block-id "slide!pkk" \
  --content '[{"type":"text","text":"这一页需要补充过渡说明"}]'

# For example: add a comment to an image element
# <img id="bPk" ... />  =>  --block-id img!bPk
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/slides/<PRESENTATION_ID>" \
  --block-id "img!bPk" \
  --content '[{"type":"text","text":"这张图片建议换成更清晰的版本"}]'

# For example: add a comment to a text shape
# <shape type="text" id="bPq"> ... </shape>  =>  --block-id shape!bPq
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/slides/<PRESENTATION_ID>" \
  --block-id "shape!bPq" \
  --content '[{"type":"text","text":"这段文案可以再精简"}]'

# Slides pointed to by wiki links are also supported
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/wiki/<WIKI_TOKEN>" \
  --block-id "<SLIDE_BLOCK_TYPE>!<XML_ELEMENT_ID>" \
  --content '[{"type":"text","text":"这里需要补充说明"}]'

# When passing a bare token, --type is required to specify the document type
lark-cli drive +add-comment \
  --doc "<SHEET_TOKEN>" --type sheet \
  --block-id "<SHEET_ID>!D6" \
  --content '[{"type":"text","text":"请检查"}]'

lark-cli drive +add-comment \
  --doc "<DOCX_TOKEN>" --type docx \
  --content '[{"type":"text","text":"全文评论"}]'

# Bare token + local comment with a known block_id
lark-cli drive +add-comment \
  --doc "<PRESENTATION_ID>" --type slides \
  --block-id "<SLIDE_BLOCK_TYPE>!<XML_ELEMENT_ID>" \
  --content '[{"type":"text","text":"slide block comment"}]'

# Bare token + local comment with a known block_id
lark-cli drive +add-comment \
  --doc "<DOCX_TOKEN>" --type docx \
  --block-id "<BLOCK_ID>" \
  --content '[{"type":"text","text":"请 "},{"type":"mention_user","text":"ou_xxx"},{"type":"text","text":" 处理，参考 "},{"type":"link","text":"https://example.com"}]'

# If you need the lower-level native API, you can also call the V2 protocol directly
lark-cli schema drive.file.comments.create_v2

lark-cli drive file.comments create_v2 \
  --params '{"file_token":"<DOC_TOKEN>"}' \
  --data '{"file_type":"docx","reply_elements":[{"type":"text","text":"全文评论内容"}]}'

# Local comment on a Base record; pass bitable for the native file_type.
lark-cli drive +add-comment \
  --doc "<BASE_TOKEN>" --type bitable \
  --block-id "<TABLE_ID>!<RECORD_ID>!<VIEW_ID>" \
  --content '[{"type":"text","text":"Base record-local comment"}]'

# `base` can also be used as a bare token type alias; both /base/ and /bitable/ URLs are automatically recognized as Base.
lark-cli drive +add-comment \
  --doc "<BASE_TOKEN>" --type base \
  --block-id "<TABLE_ID>!<RECORD_ID>!<VIEW_ID>" \
  --content '[{"type":"text","text":"Base alias comment"}]'

# Preview the underlying call chain
lark-cli drive +add-comment \
  --doc "https://example.larksuite.com/docx/<DOC_ID>" \
  --block-id "<BLOCK_ID>" \
  --content '[{"type":"text","text":"请补充流程说明"}]' \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--doc` | Yes | Document URL / token, file / sheet / slides / base / bitable URL, or a wiki URL that can resolve to `doc`/`docx`/`file`/`sheet`/`slides`/`base(bitable)` |
| `--type` | Required for bare tokens | Document type: `doc`, `docx`, `file`, `sheet`, `slides`, `bitable`, `base`; for commenting on Base documents, passing `bitable` is recommended, and `base` is only used as a compatibility alias fallback. Automatically recognized for URL input, no need to pass |
| `--content` | Yes | `reply_elements` JSON array string. Example: `'[{"type":"text","text":"文本"},{"type":"mention_user","text":"ou_xxx"},{"type":"link","text":"https://example.com"}]'` |
| `--full-comment` | No | Explicitly specify creating a full-text comment; when `--block-id` is not passed, it also defaults to a full-text comment (only applies to doc/docx, whitelisted Drive files, and wikis that resolve to these types; does not apply to sheet, slides, Base / bitable) |
| `--block-id` | Required for local comments | Target block ID, obtainable via `docs +fetch --detail with-ids`; for sheet use `<sheetId>!<cell>`, for slides use `<slide-block-type>!<xml-id>`, for Base use `<table-id>!<record-id>!<view-id>` |

<a id="行为说明"></a>
## Behavior Notes

- **Miaoda apps are not supported**: Miaoda does not support adding comments; passing a `/page/<token>` URL or `--type apps` to `--doc` will not work. The other comment management commands (list, batch query, reply, resolve/restore, reaction) all support apps.
- **Local comments require obtaining the block ID first**: first call `docs +fetch --doc <TOKEN> --detail with-ids` to get the document content with block IDs, then use `--block-id` to specify the target block.
- **For review scenarios, prefer local comments**: when reviewing, proofreading, or pointing out issues one by one, you must first try to locate the specific block / cell / slide element and create a local comment for each issue; do not merge all issues into a single full-text comment.
- When `--block-id` is not passed, the shortcut creates a **full-text comment** by default; `--full-comment` can also be passed explicitly. Full-text comments support `docx`, legacy `doc` URLs, Drive files with whitelisted extensions, and wiki URLs that ultimately resolve to `doc`/`docx`/`file`.
- **Drive file comments**: only regular files with whitelisted extensions are supported. Currently supported: `.md`, `.txt`, `.json`, `.csv`, `.go`, `.js`, `.py`, `.pptx`, `.png`, `.jpg`, `.jpeg`, `.zip`, `.mp3`, `.mp4`.
- **Drive files not yet supported**: regular files not in the whitelist, such as `.pdf`, `.docx`, `.xlsx`, will be rejected by the CLI, with the message "this type of comment is not currently supported". Although these types may accept OpenAPI requests, there are issues with displaying comments on the page.
- **Drive files only support full-text comments**: file targets do not support local comments, and passing `--block-id` is not allowed.
- When `--block-id` is passed, the shortcut creates a **local comment (selection comment)**; this mode supports `docx`, `sheet`, `slides`, Base / bitable, and wiki URLs that ultimately resolve to these types.
- **Sheet comments**: when `--doc` is a sheet URL or a wiki resolves to a sheet, use `--block-id "<sheetId>!<cell>"` to specify the cell (e.g. `a281f9!D6`); sheets have no full-text comments, and `--full-comment` is unavailable.
- **Slide comments**: when `--doc` is a slides URL, `--type slides`, or a wiki resolves to slides, `--block-id "<SLIDE_BLOCK_TYPE>!<XML_ELEMENT_ID>"` must be passed. In this case `--full-comment` is unavailable.
- **Base record local comments**: Base does not support global comments; all comments are attached to records; bare tokens can pass `--type bitable` or `--type base`, with `bitable` recommended. The location information must be the file token (base token) + `--block-id "<table-id>!<record-id>!<view-id>"`, where table/record/view IDs usually start with `tbl`/`rec`/`vew` respectively; view_id only determines which view is opened when clicking the notification upon being mentioned, and does not affect the comment attachment point, but it must be passed. For obtaining IDs, refer to [`lark-base`](../../base/index.md).
- **Slide parameter mapping example**: `--block-id` consists of the PPT XML element type and the element `id`. For example:
    - `<slide id="pkk">` corresponds to `--block-id slide!pkk`, indicating a comment on the entire page.
    - `<img id="bPk" ... />` corresponds to `--block-id img!bPk`, indicating a comment on an image element.
    - `<shape type="text" id="bPq">...</shape>` corresponds to `--block-id shape!bPq`, indicating a comment on a text shape.

- `--content` is a structured array of comment elements (`text` / `mention_user` / `link`); for the complete format see [`lark-drive-comment-content.md`](lark-drive-comment-content.md); the examples above already cover common usages.
- Before writing a comment, a request body conforming to the OpenAPI definition is automatically generated; shortcut users only need to pass `--doc` and `--content`, and for local comments also pass `--block-id` in the corresponding format.
- `--dry-run` only previews the call chain and request body, and does not actually write.
- If you need lower-level control, you can still switch to `lark-cli schema drive.file.comments.create_v2` + `lark-cli drive file.comments create_v2`.
- When calling the native `drive.file.comments.create_v2` directly, omit `anchor` for full-text comments; for docx/sheet/slides local comments pass `anchor.block_id`, and for Base record local comments pass `anchor.block_id` (table_id), `anchor.base_record_id`, `anchor.base_view_id`.
- When calling the native `drive.file.comments.*` / `drive.file.comment.replys.*` directly to comment on Base documents, fill `file_type` with `bitable`, not `base`.

> [!CAUTION]
> This is a **write operation** -- you must confirm the user's intent before executing.

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for Drive (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
