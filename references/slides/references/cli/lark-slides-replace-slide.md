<a id="slides-replace-slide块级替换--插入"></a>
# slides +replace-slide (block-level replace / insert)

Perform block-level replacement or insertion on a specified slide. The main path for editing an existing PPT—`slide_id` stays unchanged, page order stays unchanged, only the specified block is affected.

> **When writing `--parts`, use only standard actions and fields**: `block_replace` uses `block_id` + `replacement`, `block_insert` uses `insertion` (optional `insert_before_block_id`). Do not guess actions or field names based on other APIs or natural language; the specific structures are defined by the tables in this document.

The four key capabilities of this shortcut:

1. `--presentation` accepts `xml_presentation_id` / `/slides/` URL / `/wiki/` URL (wiki is automatically resolved);
2. The `replacement` root element `id` of `block_replace` is automatically injected by the CLI as `block_id`; on 3350001, first confirm that `block_id` comes from the latest `+xml-get --slide-id` and exists on the current page;
3. When a `<shape>` element lacks a `<content/>` child element, the CLI automatically injects it—the SML 2.0 schema requires every `<shape>` to have a `<content/>` child element, and a missing one likewise triggers 3350001; a self-closing `<shape .../>` is also automatically expanded to `<shape ...><content/></shape>`;
4. On a 3350001 error, a context-aware hint is provided to help the AI agent and user quickly locate the cause.

<a id="命令"></a>
## Command

```bash
# block_insert: append a new element at the end of the page
lark-cli slides +replace-slide --as user \
  --presentation slidesXXXXXXXXXXXXXXXXXXXXXX \
  --slide-id pfG \
  --parts '[{"action":"block_insert","insertion":"<shape type=\"rect\" topLeftX=\"500\" topLeftY=\"100\" width=\"200\" height=\"100\"/>"}]'

# block_replace: given a block id, replace the entire block (the replacement root id is automatically injected as bUn)
lark-cli slides +replace-slide --as user \
  --presentation slidesXXXXXXXXXXXXXXXXXXXXXX \
  --slide-id pfG \
  --parts '[{"action":"block_replace","block_id":"bUn","replacement":"<shape type=\"text\" topLeftX=\"80\" topLeftY=\"80\" width=\"800\" height=\"120\"><content textType=\"title\"><p>新标题</p></content></shape>"}]'

# For large --parts, use a file or stdin (auto-gen commands do not support @file, but the shortcut does)
lark-cli slides +replace-slide --as user \
  --presentation $PRES_ID --slide-id $SID --parts @parts.json
cat parts.json | lark-cli slides +replace-slide --as user \
  --presentation $PRES_ID --slide-id $SID --parts -

# Pass the wiki URL directly (the CLI automatically obtains the real xml_presentation_id via node_by_token)
lark-cli slides +replace-slide --as user \
  --presentation "https://xxx.feishu.cn/wiki/wikcnXXXXXX" --slide-id pfG \
  --parts '[{"action":"block_insert","insertion":"<shape type=\"rect\" width=\"100\" height=\"100\"/>"}]'

# Preview (does not actually call)
lark-cli slides +replace-slide --as user \
  --presentation $PRES_ID --slide-id $SID --parts "$PARTS" --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--presentation` | Yes | `xml_presentation_id`, `/slides/<token>` URL, or `/wiki/<token>` URL |
| `--slide-id` | Yes | Page ID (obtained via `slides +xml-get`) |
| `--parts` | Yes | JSON array (`[{...}, ...]`), at most 200 entries per call. Supports `@<file>` and `-` (stdin) reading |
| `--revision-id` | No | Base version number; the default `-1` means execute based on the latest version; when a specific version number is passed, the server executes with that version as the base; **passing a nonexistent version number (exceeding the current revision) returns 3350002** |
| `--tid` | No | Concurrent transaction ID; only used for long transactions with multi-person collaboration, leave empty for a single-person single call |

<a id="parts-元素结构"></a>
## parts element structure

> **Limit**: at most 200 entries; `block_replace` and `block_insert` can be mixed in the same batch. **Other actions (including `str_replace`) are directly rejected with an error by the CLI**.

Each part takes different fields according to `action`:

### action = `block_replace`

| Field | Required | Description |
|------|------|------|
| `action` | Yes | `"block_replace"` |
| `block_id` | Yes | The 3-digit short element ID of the target block (read from the XML returned by `+xml-get --slide-id`) |
| `replacement` | Yes | New XML fragment; **the root element `id` is automatically injected by the CLI as `block_id`**, the user does not need to add it themselves (if it has already been added and is inconsistent, it will be overwritten with the correct value) |

### action = `block_insert`

| Field | Required | Description |
|------|------|------|
| `action` | Yes | `"block_insert"` |
| `insertion` | Yes | The XML fragment to insert |
| `insert_before_block_id` | No | Insert before this block; if omitted (this field not provided), append to the end of the page |

<a id="错误字段名cli-直接拒绝"></a>
### Invalid field names (directly rejected by the CLI)

When writing a part, use only the standard fields in the table above. When the CLI returns an unknown field, it names the incorrectly written field and gives the next step as appropriate: when it can be matched to the correct field, it directly suggests it (`did you mean \"replacement\"?`); when the field belongs to another action, it explains the ownership (`it belongs to block_insert`); when neither matches, it lists the legal field set for that action. In any case, **what needs to be changed is the field name, not the field value**.

```jsonc
// ❌ All rejected
[{"action":"block_replace","block_id":"bUn","xml":"<shape.../>"}]           // unknown field "xml"; did you mean "replacement"?
[{"action":"block_replace","block_id":"bUn","data":"<shape.../>"}]          // data is not a standard field
[{"action":"block_replace","block_id":"bUn","insertion":"<shape/>"}]        // insertion belongs to block_insert
[{"action":"block_replace","block_id":"bUn","replacement":{"type":"..."}}]  // replacement must be a string, reports .replacement must be a string

// ✅ Correct
[{"action":"block_replace","block_id":"bUn","replacement":"<shape type=\"text\"><content><p>新内容</p></content></shape>"}]
[{"action":"block_insert","insertion":"<shape type=\"rect\" width=\"100\" height=\"100\"/>"}]
```

<a id="合法根元素速查"></a>
## Legal root elements quick reference

`block_replace.replacement` and `block_insert.insertion` must have a legal element defined by SML 2.0 as the root. For the complete authoritative definition, see [`slides_xml_schema_definition.xml`](../xml/slides_xml_schema_definition.xml); here only the types that can serve as a **root** are listed + the minimal working fragment for each type.

| Element | Purpose | Key point |
|---|---|---|
| `<shape>` | All shapes such as rectangles/ellipses/triangles/text boxes | `type` is required; when `<content/>` is missing, the CLI automatically injects it |
| `<line>` | Straight line | Requires `startX/startY/endX/endY` |
| `<polyline>` | Polyline | `points` is normalized and discarded by the server when read back (the geometry is already stored) |
| `<img>` | Image | `src` must be the `file_token` returned by [`+media-upload`](lark-slides-media-upload.md), not a URL |
| `<icon>` | Icon | `iconType` is taken from iconpark resources; for semantic icons, first search using `scripts/iconpark_tool.py search` |
| `<table>` | Table | Replacing the entire table **rebuilds the internal td ids**, and old td block_ids immediately become invalid |
| `<td>` | Cell partial replacement | Can only `block_replace`, cannot `block_insert`; `block_id` must be the td id obtained from the latest `+xml-get --slide-id` |
| `<chart>` | Chart (line/bar/column/pie/area/radar/combo) | Must embed `<chartPlotArea>` + `<chartData>` + `<dim1>/<dim2>/<chartField>` |

**Cannot be used as a root element**:

- `<video>` / `<audio>` — SML 2.0 does not have these two native elements; `<undefined type="video|audio">` is a placeholder **at export time** (the server uses it to substitute when encountering an unsupported type), and **cannot be written**. Attempting insert/replace both return 3350001.

<a id="最小-xml-片段json-嵌入时记得把--转义成-"></a>
### Minimal XML fragment (remember to escape `"` as `\"` when embedding in JSON)

`<shape>` (text box; `type` can also optionally have `rect`/`ellipse`/`triangle`/`custom`, etc.):
```xml
<shape type="text" topLeftX="80" topLeftY="80" width="800" height="120">
  <content textType="title"><p>标题</p></content>
</shape>
```

`<img>`：
```xml
<img src="{file_token}" topLeftX="600" topLeftY="20" width="80" height="80"/>
```

`<polyline>`：
```xml
<polyline topLeftX="10" topLeftY="10" width="100" height="50" points="0,0 50,50 100,0"/>
```

`<table>`（2×2）：
```xml
<table topLeftX="30" topLeftY="80">
  <colgroup><col span="2" width="110"/></colgroup>
  <tr><td><content><p>A</p></content></td><td><content><p>B</p></content></td></tr>
  <tr><td><content><p>C</p></content></td><td><content><p>D</p></content></td></tr>
</table>
```

`<td>` (`block_replace` cell; `block_id` must be the td id obtained from the latest `+xml-get --slide-id`):
```xml
<td><content><p>新内容</p></content></td>
```

`<chart>` (change `type` to `bar`/`column`/`pie`/`area`/`radar`/`combo` to switch the chart type):
```xml
<chart topLeftX="30" topLeftY="300" width="300" height="200">
  <chartPlotArea><chartPlot type="line"/></chartPlotArea>
  <chartData>
    <dim1><chartField name="x" valueType="string">Q1,Q2,Q3,Q4</chartField></dim1>
    <dim2><chartField name="Sales" valueType="number">10,20,15,30</chartField></dim2>
  </chartData>
</chart>
```

<a id="返回值"></a>
## Return value

```json
{
  "xml_presentation_id": "slidesXXXXXXXXXXXXXXXXXXXXXX",
  "slide_id": "pfG",
  "parts_count": 1,
  "revision_id": 102
}
```

| Field | Description |
|------|------|
| `xml_presentation_id` | The resolved real token (it changes after a wiki URL is resolved) |
| `slide_id` | Consistent with the input parameter |
| `parts_count` | The number of parts submitted this time |
| `revision_id` | The new version number after success, used for the next optimistic lock |
| `failed_part_index` | Present when there is a partial failure, points to which part failed |
| `failed_reason` | Text description of the failure reason |

The entire batch is an atomic transaction: if any part fails, the entire batch does not take effect, and the server tells you which one it is via `failed_part_index` / `failed_reason`; locate and fix accordingly, then resend.

<a id="使用流程"></a>
## Usage flow

<a id="给已有页加图典型场景"></a>
### Add an image to an existing page (typical scenario)

```bash
PRES_ID=xxx
SID=yyy

# 1) Upload the image
TOKEN=$(lark-cli slides +media-upload --as user \
  --file ./pic.png --presentation "$PRES_ID" --jq '.data.file_token')

# 2) block_insert to the end of the page
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --parts "$(jq -n --arg token "$TOKEN" \
    '[{action:"block_insert",insertion:("<img src=\""+$token+"\" topLeftX=\"500\" topLeftY=\"100\" width=\"200\" height=\"150\"/>")}]')"
```

<a id="改标题block_replace"></a>
### Change the title (block_replace)

```bash
# First get the original page XML, and find the 3-digit short id of the title block from it (e.g. bUn)
lark-cli slides +xml-get --as user \
  --presentation "$PRES_ID" --slide-id "$SID" --raw

# block_replace replaces the entire title block (id automatically injected)
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --parts '[{"action":"block_replace","block_id":"bUn","replacement":"<shape type=\"text\" topLeftX=\"80\" topLeftY=\"80\" width=\"800\" height=\"120\"><content textType=\"title\"><p>新标题</p></content></shape>"}]'
```

<a id="批量一次换标题--追加装饰图"></a>
### Batch: change the title + append a decorative image in one go

`block_replace` and `block_insert` can be mixed in the same `--parts`, and the entire batch executes atomically.

```bash
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --parts '[
    {"action":"block_replace","block_id":"bab","replacement":"<shape type=\"text\" topLeftX=\"80\" topLeftY=\"80\" width=\"800\" height=\"120\"><content textType=\"title\"><p>新标题</p></content></shape>"},
    {"action":"block_insert","insertion":"<img src=\"<file_token>\" topLeftX=\"700\" topLeftY=\"400\" width=\"180\" height=\"100\"/>"}
  ]'
```

<a id="乐观锁"></a>
### Optimistic lock

```bash
# Record revision_id when reading
REV=$(lark-cli slides +xml-get --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --jq '.data.revision_id')

# Pass --revision-id when writing; passing a nonexistent version number (exceeding the current revision) returns 3350002
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" --revision-id "$REV" \
  --parts "$PARTS"
```

<a id="常见错误"></a>
## Common errors

| Symptom | Cause | Countermeasure |
|------|------|------|
| 3350001 + hint "block_id not found" | `parts[i].block_id` does not exist on the current page | Use `+xml-get --slide-id` again to get the latest XML, and fill it in again according to the short ID in it |
| 3350002 not found | `--revision-id` passed a nonexistent version number (exceeding the current revision) | Use `-1` or use the valid `revision_id` obtained via `+xml-get --slide-id` |
| `--parts invalid JSON` | The JSON itself is incomplete, or was broken by shell quoting/escaping | Write the array to `parts.json` and then pass `--parts @parts.json`, or pass it to `--parts -` via stdin |
| `--parts[i] action "str_replace" is not supported` | The CLI does not expose `str_replace` | Rewrite the replacement requirement as `block_replace` / `block_insert` |
| `--parts[i] action "page_replace" / "slide_replace" means whole-page replacement` | A whole-page update intent was passed to the block-level shortcut | Use [`slides +update-slide`](lark-slides-update-slide.md) to write the entire page back in place |
| `--parts contains N items, exceeds maximum of 200` | Too many parts submitted at once | Split into multiple calls |
| `--parts[i] unknown field "xml"; did you mean "replacement"?` | XML was put into an unsupported field name (such as `xml` / `new_xml` / `data`) | Use standard fields: `block_replace` uses `replacement`, `block_insert` uses `insertion` |
| `--parts[i] unknown field "insertion"; it belongs to block_insert` | The field and `action` do not match | Take fields according to the action: `block_replace` = `block_id` + `replacement`; `block_insert` = `insertion` (+ `insert_before_block_id`) |
| `--parts[i] (block_replace) requires non-empty block_id` / `replacement` | The field name is correct, but the value is missing or an empty string | Fill in the value according to the parts element structure |
| `<img>` does not display / displays a broken image | `src` wrote an external URL | Replace it with the `file_token` obtained via [`+media-upload`](lark-slides-media-upload.md) |
| 3350001 | `replacement` is not a legal single-root XML fragment, or `block_id` does not exist | The CLI has automatically injected `id` and `<content/>`; if it still reports an error, use `+xml-get --slide-id` again to get the latest XML and confirm that `block_id` exists; check whether the XML structure is legal; whether the coordinates exceed 960×540 |
| 403 | Insufficient permissions | Requires `slides:presentation:update` or `slides:presentation:write_only`; a wiki URL also requires `wiki:node:read` |

<a id="相关命令"></a>
## Related commands

- [slides +xml-get](lark-slides-xml-presentations-get.md) — read the original page to get `block_id` / `revision_id`
- [+media-upload](lark-slides-media-upload.md) — upload an image to get `file_token`
- [slides-editing.md](../workflow/slides-editing.md) — read-modify-write loop + decision tree
