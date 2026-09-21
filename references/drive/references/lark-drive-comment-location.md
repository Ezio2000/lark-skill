<a id="文档评论定位字段"></a>
# Document Comment Location Fields

When a user needs to locate a document body position based on a comment, review a document, distinguish multiple identical quoted texts, or map a comment anchor to the content of `docs +fetch --detail with-ids`, prefer using `drive +list-comments --need-relation` to query docx comment locations; when the comment ID is known, use `drive +batch-query-comments --need-relation`.

<a id="适用范围"></a>
## Scope of Application

- Currently only `file_type=docx` supports querying comment locations via `need_relation=true`, and returns fields such as `relation`, `parent_type`, `parent_token` that can be used to locate body blocks.
- Both `drive +list-comments` and `drive +batch-query-comments` will silently ignore `--need-relation` when the target is not a docx, to avoid passing invalid parameters to the OpenAPI. When encountering comments on sheets, bitables, slides, regular files, etc., do not promise that `need_relation` can be used to precisely locate the body position; instead fall back to regular comment fields, drilling down via the corresponding resource capabilities, or manual confirmation.
- Note the parameter position difference: the `need_relation` for list is in query params, while for batch_query it is in the request body (only relevant when calling the raw OpenAPI directly; the two shortcuts already handle this themselves).

<a id="调用方式"></a>
## Invocation Methods

When listing comments with pagination, prefer passing the URL; Wiki URLs / Wiki tokens are automatically resolved to the underlying real token/type:

```bash
lark-cli drive +list-comments --url '<docx_or_wiki_url>' --need-relation
```

If you only have a Wiki token, explicitly pass `--type wiki`:

```bash
lark-cli drive +list-comments --token '<wiki_token>' --type wiki --need-relation
```

When the comment ID is known, use `drive +batch-query-comments --need-relation` to fetch directly by ID:

```bash
lark-cli drive +batch-query-comments --url '<docx_or_wiki_url>' --comment-ids '<comment_id>' --need-relation
```

Only when you need underlying parameters not exposed by the shortcuts should you call the raw OpenAPI directly (the two shortcuts already handle the position difference of `need_relation` themselves: list in query params, batch_query in the request body).

Also fetch the document content and require block ids to be returned:

```bash
lark-cli docs +fetch --doc '<doc_token_or_url>' --detail with-ids
```

<a id="字段含义"></a>
## Field Meanings

- `relation`: The structured position of the comment within the document content. `relation.relation` is a JSON string that needs to be parsed again; within it, `positionInfo.blockID` is the most critical field, used to match the document block returned by `docs +fetch --detail with-ids`.
- `relation.content_deleted`: Whether the content referenced by the comment has been deleted. When it is `true`, do not assume the original position can still be found in the current body.
- `parent_type`: The type of the parent embedded resource where the comment is located. Common values include `SHEET_BLOCK`, `BITABLE_BLOCK`, `WHITEBOARD_BLOCK`, indicating the comment falls inside an embedded spreadsheet, bitable, or whiteboard within the document.
- `parent_token`: The parent embedded resource token. For comments inside a sheet / bitable / whiteboard, the server may not be able to provide a document block-level `relation` for the internal cell, record, or whiteboard node, but the parent embedded block in the document can be located via `parent_type` + `parent_token`.

<a id="准确度分级"></a>
## Accuracy Levels

When outputting location conclusions, you must distinguish the following three categories, and must not present weak inferences as precise locations:

| Level | Determination Condition | Output Wording |
|---|---|---|
| `relation 精确` | `relation.relation` contains `positionInfo.blockID`, and the same block can be matched in `docs +fetch --detail with-ids` | Can say "precisely located to the block" |
| `父级资源精确，内部需下钻` | Only the parent embedded resource's `blockID` / `parent_type` / `parent_token`, or the internal resource's `positionInfo` is empty | Can say "precisely located to the embedded resource; internal cells/records/nodes need to be confirmed by drilling down with the corresponding skill" |
| `弱匹配/推断` | Can only rely on `quote`, sequence number, current display order, or text search | Must mark as "inference", explain the source of ambiguity and the supplementary information needed |

<a id="返回示例"></a>
## Return Examples

A comment on a regular docx block will return `relation`. Note that `relation.relation` itself is a string and needs to be JSON parsed once more:

```json
{
  "comment_id": "7646774324967295982",
  "quote": "code2",
  "relation": {
    "content_deleted": false,
    "relation": "{\"22-doc_token_xxx\":{\"objType\":22,\"index\":2,\"objVersion\":10,\"positionInfo\":{\"blockID\":\"block_id_xxx\"}}}"
  },
  "parent_type": null,
  "parent_token": null
}
```

After parsing `relation.relation` again, take `positionInfo.blockID`:

```json
{
  "22-doc_token_xxx": {
    "objType": 22,
    "index": 2,
    "objVersion": 10,
    "positionInfo": {
      "blockID": "block_id_xxx"
    }
  }
}
```

Then look up the same block id in the result of `docs +fetch --detail with-ids`, for example:

```json
{
  "block_id": "block_id_xxx",
  "block_type": "code",
  "text": "code1\ncode2"
}
```

Comments inside an embedded sheet / bitable / whiteboard may not have a usable `relation`, but will return a parent marker:

```json
{
  "comment_id": "7646775036988148672",
  "quote": "记录 2",
  "relation": null,
  "parent_type": "BITABLE_BLOCK",
  "parent_token": "bitable_app_token_xxx_table_id_xxx"
}
```

In this case, use `parent_type` to determine that the target is an embedded resource, then use `parent_token` to match the bitable / sheet block in `docs +fetch --detail with-ids`. The location granularity is the parent embedded block in the document, not the internal record, field, or cell.

The return form for comments inside a whiteboard is similar:

```json
{
  "comment_id": "7646775036988148673",
  "quote": "画板节点文本",
  "relation": null,
  "parent_type": "WHITEBOARD_BLOCK",
  "parent_token": "whiteboard_token_xxx"
}
```

At this point `parent_token` corresponds to the `token` property of `<whiteboard>` in the `docs +fetch --detail with-ids` result, for example:

```xml
<whiteboard id="whiteboard_block_id_xxx" token="whiteboard_token_xxx"></whiteboard>
```

After matching this `<whiteboard>`, `id` is the parent whiteboard block id in the document body. The location granularity is the whiteboard block in the document; if you need to further locate a specific node inside the whiteboard, you need to use the whiteboard capability to read the whiteboard's internal structure.

<a id="定位流程"></a>
## Location Workflow

1. Confirm the target is `file_type=docx`; only docx documents support querying comment locations via `need_relation`.
2. Use `drive +list-comments --need-relation` to fetch comments; when the comment ID is known and batch querying is needed, use `drive +batch-query-comments --need-relation`. The native `drive file.comments list/batch_query` is only a fallback when underlying parameters not exposed by the shortcuts are needed.
3. Use `docs +fetch --detail with-ids` to fetch the document content.
4. For each comment, first check `relation`:
   - If `relation.relation` exists, parse this JSON string.
   - Take `positionInfo.blockID` from the parsed result.
   - Look up the same block id in the `docs +fetch` result; this is the document block corresponding to the comment.
5. If there is no usable `relation`, but there is `parent_type` and `parent_token`:
   - `SHEET_BLOCK`: Locate the sheet embedded block in the document; `parent_token` usually contains the sheet token and sheet id; if necessary, take the token before `_` and compare it with the embedded resource token of the document block.
   - `BITABLE_BLOCK`: Locate the bitable embedded block in the document; `parent_token` usually contains the bitable app token and table id; if necessary, take the token before `_` and compare it with the embedded resource token of the document block.
   - `WHITEBOARD_BLOCK`: Locate the whiteboard embedded block in the document; `parent_token` corresponds to the `token` property of `<whiteboard>` in `docs +fetch --detail with-ids`.
   - In this scenario, the parent embedded block can be located, but usually the specific cell, field, record, or whiteboard node inside the embedded resource cannot be located from the comment API alone.
6. Only when `relation`, `parent_type`, and `parent_token` are all missing should you fall back to using `quote` text for weak matching; `quote` is the quoted text field returned by the comment API. Weak matching cannot distinguish multiple occurrences of the same text.

<a id="嵌入资源内部定位"></a>
## Locating Inside Embedded Resources

<a id="sheet-内部评论"></a>
### Comments Inside a Sheet

- The common format of `parent_token` is `<spreadsheet_token>_<sheet_id>`; you may also see `subToken` as `3-<spreadsheet_token>` in `relation.relation`.
- The comment API usually only points `positionInfo.blockID` to the `<sheet>` block in the document; the internal sheet's `positionInfo` may be empty.
- If `quote` is a cell coordinate such as `C3`, `A1`, you can split out `spreadsheet_token` / `sheet_id` and then use `lark-sheets` to read that cell for confirmation:

```bash
lark-cli sheets +cells-get \
  --spreadsheet-token '<spreadsheet_token>' \
  --sheet-id '<sheet_id>' \
  --range '<cell>'
```

- Accuracy wording: The parent sheet block can be precisely located by relation/parent token; if the cell coordinate comes only from `quote`, you should state "the cell comes from quote, verified by reading via sheets", and not say it comes from `positionInfo`.

<a id="bitable--base-内部评论"></a>
### Comments Inside a Bitable / Base

- The common format of `parent_token` is `<base_token>_<table_id>`, where `table_id` usually starts with `tbl`. When parsing, prefer splitting at the last `_tbl` boundary, to avoid incorrect splitting when `_` appears inside the base token.
- The comment API may return only `parent_type=BITABLE_BLOCK` and `parent_token`, without `relation`; even if there is a relation, it is usually only enough to locate the `<bitable>` block in the document.
- When drilling down to read, switch to `lark-base`, and at minimum confirm the table, field, and record:

```bash
lark-cli base +table-list --base-token '<base_token>'
lark-cli base +field-list --base-token '<base_token>' --table-id '<table_id>'
lark-cli base +record-list --base-token '<base_token>' --table-id '<table_id>' --limit 200 --format json
```

- If `quote` is a stable business value, prefer using field/record data for precise matching; if `quote` is merely a UI sequence number such as "the Nth item" or "the Nth row", you can only infer the corresponding record based on the current record order, and must output it as an "inference", explaining that the comment API did not return `record_id` / `field_id`.
- If `record-list` returns `has_more=true`, do not draw global conclusions based on the first page; continue paginating or state that only the range already read can be covered.
- When writing is needed, if the comment has no field information, do not guess the field yourself; unless the user provides a default rule, ask the user to confirm the field, or clearly state which field will be used as the default.

<a id="whiteboard-内部评论"></a>
### Comments Inside a Whiteboard

- `parent_token` corresponds to `<whiteboard token="...">` in the document XML; first use it to match the whiteboard block in the document.
- To locate a node inside the whiteboard, switch to `lark-whiteboard` to read the raw node structure:

```bash
lark-cli whiteboard +export \
  --whiteboard-token '<whiteboard_token>' \
  --output-type raw
```

- If there is a text node in the raw nodes that uniquely matches `quote`, you can locate that node; if there are multiple identical text nodes, it is still a weak match and requires combining position, style, user description, or manual confirmation.
- Before modifying a whiteboard node, first state the matched node id and text; for complex whiteboards, do not batch-replace all nodes with the same name based only on `quote`.

<a id="使用原则"></a>
## Usage Principles

- When reviewing a document, do not rely only on `quote` text to locate comments; multiple occurrences of the same text will cause ambiguity.
- When `relation.positionInfo.blockID` is available, use the block id as the basis, then use the block content to understand the context.
- For comments inside an embedded sheet / bitable / whiteboard, use the parent embedded block as the document body location point; if you need to further locate a table cell, bitable record, or whiteboard internal node, you need to call the corresponding sheet / bitable / whiteboard capability to read the internal data.
