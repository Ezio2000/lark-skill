<a id="docs-fetch读取飞书云文档"></a>
# docs +fetch (Read Feishu cloud documents)

Read an entire document, or fetch partial content by table of contents, section, range, and keyword.

<a id="常用示例"></a>
## Common examples

```bash
# Read the entire document, along with unresolved comments visible to the current user;
lark-cli docs +fetch --doc "文档URL或token"

# Fetch a portion by the #share anchor in the URL
lark-cli docs +fetch --doc '文档URL#share-anchor'

# Locate by keyword
lark-cli docs +fetch --doc Z1Fj...tnAc --scope keyword --keyword "部署|发布|上线"

# First view the table of contents, then read the specified section
lark-cli docs +fetch --doc Z1Fj...tnAc --scope outline --max-depth 3
lark-cli docs +fetch --doc Z1Fj...tnAc --scope section --start-block-id blkTitle
```

<a id="参数"></a>
## Parameters

|Parameter|Required|Description|
|-|-|-|
|`--doc`|Yes|Document URL or token, supports `/docx/`, `/wiki/`, and selection links with `#share-...`|
|`--doc-format`|No|`xml` (default) \| `markdown` \| `im-markdown` (for subsequent `lark-im` scenarios)|
|`--detail`|No|`simple` (default) \| `with-ids` \| `full`|
|`--revision-id`|No|Document version number; `-1` means the latest version (default)|
|`--scope`|No|`outline` \| `range` \| `keyword` \| `section`; if omitted, reads the entire document|
|`--start-block-id`|No|The start point of `range`, or the anchor of `section` (`section` required)|
|`--end-block-id`|No|The end point of `range`; `-1` means read to the end|
|`--keyword`|No|Keyword for `keyword` mode; supports multi-level automatic matching and multi-branch OR|
|`--context-before`|No|Number of top-level sibling blocks to return before the matched item (default `0`)|
|`--context-after`|No|Number of top-level sibling blocks to return after the matched item (default `0`)|
|`--max-depth`|No|`outline` means the heading level upper limit; other modes mean subtree depth (default `-1`, unlimited)|

<a id="选择详细度--detail"></a>
## Choosing detail level: `--detail`

|Purpose|Value|Returned content|
|-|-|-|
|Browsing, summarizing|`simple` (default)|Concise XML/Markdown, without block IDs, styles, or reference metadata|
|Locating, jumping|`with-ids`|Includes block IDs, usable for `+update --block-id`, and can be assembled into `文档URL#block_id` direct links|
|Editing documents|`full`|Includes block IDs, styles, and reference metadata, preserving complete structural information|

Use `full` when you need to modify a document; read-only scenarios usually do not need to fetch extra metadata.

<a id="选择读取范围--scope"></a>
## Choosing read range: `--scope`

`--scope` and `--detail` can be combined. Prefer reading the smallest range that satisfies the task; omit `--scope` only when the full text is truly needed.

|Mode|Applicable scenario|Key parameters|Return behavior|
|-|-|-|-|
|`outline`|Structure unknown, view the table of contents first|`--max-depth`|Lists headings flatly; the returned heading IDs can serve as endpoints for `section` or `range`|
|`section`|Read the entire section corresponding to a heading|`--start-block-id` (required)|A top-level heading expands up to the next heading of the same or higher level; nodes inside a container (including embedded headings) are returned as the container or table slice by the smallest containing unit|
|`range`|Exact start and end positions known|At least one of `--start-block-id`, `--end-block-id`|The same top-level sequence is sliced by range; the same container returns the entire container; the same table returns a slimmed slice; when spanning top-level blocks, the top-level blocks containing the endpoints are returned in full|
|`keyword`|Only keywords or fuzzy clues available|`--keyword` (required)|Returns matches by the smallest containing unit; multiple matches in the same container are automatically deduplicated, and multiple row matches in the same table are merged into a slice|

`keyword` tries substring, normalization, tokenization variants, and RE2 regex matching in sequence. For multiple keywords, use `|` to mean OR, for example `部署|发布|上线`; a match on any branch returns a result.

Common rules for range parameters:

- `--max-depth`: In `outline`, `3` means list h1–h3; in other modes, `0` means return only the block itself, and `-1` means unlimited depth.
- `--context-before` / `--context-after`: Only takes effect for complete top-level blocks. Matches located inside a container or table are ignored; if a larger range is needed, use `section` or `range` instead.

Recommended selection order:

|Known information|Preferred method|Follow-up action|
|-|-|-|
|Specific term, error code, or identifier|`keyword`|When context is insufficient, use the returned `top-block-id` to run `section` or `range` again|
|Section or heading|`outline --max-depth 3`|After obtaining the heading ID, run `section`|
|Exact start and end positions|`range`|Adjust endpoints or depth as needed|
|No keywords and structure unknown|`outline`|Based on the table of contents, switch to `section` or `range`|
|The entire document is truly needed|Omit `--scope`|—|

<a id="返回值"></a>
## Return values

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "document_id": "docToken",
      "revision_id": 12,
      "content": "<title>标题</title><p>文档内容...</p>",
      "reference_map": {
        "<block_type>": {
          "<ref>": {
            "<real-attr-key>": "<real-attr-value>"
          }
        },
        "comments": {
          "c1": {
            "data": "<comment comment-id=\"xx\" block-id=\"xx\"><quote>引用内容</quote><msg>评论内容</msg></comment>"
          }
        }
      },
      "tips": "<safe replay or degradation guidance>"
    }
  }
}
```
- The format of `content` is determined by `--doc-format`. `reference_map` is a structured sidecar; first-level keys represent reference groups: ordinary resource groups are usually named `block_type`, second-level keys `ref` correspond to temporary references in the body text, and their values consist of real attributes; the reserved group `comments` uses `<ref>.data` to store comments. XML, Markdown, and IM Markdown all return this group when visible comments exist; Markdown body text has no inline reference corresponding to the comment key, which is an intentional protocol design. When no data is extracted, `reference_map` may be empty. `comments.tips.data` indicates that comments were truncated due to the quantity limit, while the document top-level `tips` gives safe replay or dependency degradation hints. `content` and `reference_map` belong to the same response, and the complete JSON response should be preserved; `im-markdown` is only used after fetching content in `lark-im` scenarios. When `--scope` is set, it is wrapped by `<fragment>`; see “Output structure of partial reads” below for details.
- Comment content is not guaranteed to be returned in full; when detailed information is needed, use `drive +list-comments` to fetch complete comments.

<a id="理解局部读取结果"></a>
### Understanding partial read results

<a id="参数-1"></a>
## Parameters

After setting `--scope`, the outer layer of `content` is `<fragment>`, and it carries `mode`, `requested-start`, `requested-end`, or `keyword` attributes as needed. Its child nodes have two forms:

- **Top-level block**: Directly a child node of `<fragment>`, indicating that a complete block was returned.
- **`<excerpt top-block-id="..." parent-block-path="...">`**: Indicates that only an excerpt from a container or table was returned.
  - `top-block-id` is the top-level block ID where the excerpt is located. To view the complete block, you can use it as the anchor for `section` or `range` to read again.
  - `parent-block-path` is the ID path from the top-level block to the direct parent node of the excerpt content, separated by `/`; in a table slice, it is the table's own ID.

When you see `<excerpt>`, do not assume that the entire top-level block has been fetched.

Tables are slimmed by default: even if `<table>` itself is a top-level block, only the header and matched rows are returned. To read the entire table, use `range --start-block-id <table-id> --end-block-id <table-id>`. If the slice covers all data rows, the SDK automatically returns the complete table without wrapping `<excerpt>`.

<a id="处理文档内嵌资源"></a>
## Handling embedded resources in documents

|Returned content|Handling method|
|-|-|
|`<img>`, `<source>`|When `url` is present, download only trusted public HTTPS URLs: reject userinfo and hosts that resolve to private, loopback, link-local, multicast, or unspecified addresses, and validate redirects one by one; when these conditions are not met, requests are prohibited. When `url` is absent, extract `token`; use `docs +media-preview` for preview and `docs +media-download` for download|
|`<whiteboard>`|Extract `token`, use `docs +media-download`|
|`<sheet>`, `<cite file-type="sheets">`|Extract `token` and `sheet-id`, go to [`lark-sheets`](../../sheets/index.md)|
|`<bitable>`, `<cite file-type="bitable">`|Extract `token` and `table-id`, go to [`lark-base`](../../base/index.md)|
|`<vc-transcribe-tab>`|Extract `vc-node-id`, use `note +detail` of [`lark-meeting`](../../meeting/index.md)|
|`<synced_reference>`|Extract `src-token` and `src-block-id`, read the source document and locate the block|

<a id="参考"></a>
## References

- [lark-doc-media-preview](lark-doc-media-preview.md) — preview media
- [lark-doc-media-download](lark-doc-media-download.md) — download media or board thumbnails
