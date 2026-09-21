<a id="编辑已有-ppt读-改-写闭环"></a>
# Editing an existing PPT: read-modify-write loop

For local edits, use the **shortcut [`+replace-slide`](../cli/lark-slides-replace-slide.md)** (block-level replace / insert), together with `+xml-get --slide-id` to read the original page and get the `block_id`. For full-page rebuilds, use **[`+update-slide`](../cli/lark-slides-update-slide.md)**, running it once per page for multiple pages — it overwrites in place and preserves the `slide_id` and page order; only elements written into `--content` with their original id will keep their element id, and omitted elements will be deleted.

> Before generating XML, you **must read** [xml-schema-quick-ref.md](../xml/xml-schema-quick-ref.md).

<a id="决策树block_replace-vs-block_insert"></a>
## Decision tree: block_replace vs block_insert

| Requirement | Recommended action | Reason |
|------|------------|------|
| You know a block's `block_id` and want to replace that block's content (change title, swap image, move coordinates) | `block_replace` | Precise replacement, good atomicity; the `replacement` root `id` is automatically injected by the CLI as `block_id` |
| Only add 1~N elements without touching the existing layout | `block_insert` | Adds without overwriting, optionally use `insert_before_block_id` to specify the position |
| Modify multiple elements at once (e.g., change title + add image) | Combine multiple entries in a single `--parts` | The whole batch acts as an atomic transaction; if any one fails, the whole batch does not take effect; `block_replace` and `block_insert` can be mixed |
| Full-page layout rebuild, full-page coordinate rearrangement, change page background, delete several elements | `+update-slide` (once per page) | In-place full-page overwrite, `slide_id` and page order unchanged; elements with the original `id` keep their id, those without `id` are inserted as new elements, and omitted ones are deleted |

> **There is no field-level patch**: even if you only want to change one `shape`'s `topLeftX`, you still have to write out the entire block's new XML and use `block_replace`. This is not a "fine-tuning", it is a block-level rewrite.

<a id="最小读-改-写闭环"></a>
## Minimal read-modify-write loop

```bash
PRES_ID="xml_presentation_id_here"
SID="slide_id_here"

# 1. Read the original page, and pick out the 3-digit short id (e.g. bUn / bab) of the block you want to change from the XML
lark-cli slides +xml-get --as user \
  --presentation "$PRES_ID" --slide-id "$SID" --raw

# 2. Use +replace-slide to directly modify that block (no need to move the original XML)
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --parts '[{"action":"block_replace","block_id":"bUn","replacement":"<shape type=\"text\" topLeftX=\"80\" topLeftY=\"80\" width=\"800\" height=\"120\"><content textType=\"title\"><p>新标题</p></content></shape>"}]'
```

`slide_id` / page order will not change. The `replacement` root element `id` of `block_replace` is automatically injected as `block_id`, so users do not need to add it themselves when writing XML by hand.

> **When writing `--parts`, use only standard fields**: `block_replace` uses `action` + `block_id` + `replacement` (XML string), and `block_insert` uses `action` + `insertion` (optional `insert_before_block_id`). When you receive an unknown field error, you should modify the field name according to the structure above, not the field value.

<a id="revision_id-参数"></a>
## `revision_id` parameter

`--revision-id` defaults to `-1`, meaning it executes based on the current latest version. When a specific version number is passed, the server applies the change with that version as the base:

```bash
# Get the current revision_id when reading
REV=$(lark-cli slides +xml-get --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --jq '.data.revision_id')

# Pass that version number when writing, and the server uses it as the base
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" --revision-id "$REV" \
  --parts '[{"action":"block_replace","block_id":"bUn","replacement":"<shape type=\"rect\" topLeftX=\"100\" topLeftY=\"100\" width=\"200\" height=\"100\"/>"}]'
```

Note: passing a nonexistent version number (beyond the current revision) returns 3350002 not found; when unsure, just use `-1`.

<a id="--tid-事务锁"></a>
## `--tid` transaction lock

A cross-request concurrent transaction ID, only useful for long transactions in multi-person collaboration. **Leave it empty for a single-person single call.**

<a id="两种-action-详解"></a>
## Detailed explanation of the two actions

<a id="block_replace--整块替换"></a>
### block_replace — whole-block replacement

Suitable for the scenario "you know the block ID and want to replace the entire content of this block". The `id="<block_id>"` of the `replacement` root element is automatically injected by the CLI (if the XML you write by hand does not include `id`, you can simply omit it; if it includes a wrong one, it will be overwritten with the correct value).

```bash
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --parts '[{"action":"block_replace","block_id":"bab","replacement":"<shape type=\"text\" topLeftX=\"80\" topLeftY=\"80\" width=\"800\" height=\"120\"><content textType=\"title\"><p>新标题</p></content></shape>"}]'
```

Field description:

| Field | Required | Description |
|------|------|------|
| `action` | Yes | Fixed to `block_replace` |
| `block_id` | Yes | The 3-digit short element ID of the target block (read from the XML returned by `+xml-get --slide-id`)|
| `replacement` | Yes | The new XML fragment; the root element `id` will be automatically injected by the CLI as `block_id` |

<a id="block_insert--整块插入"></a>
### block_insert — whole-block insertion

Suitable for the scenario "you only want to add one element without touching existing elements" (typical: add an image to an existing page).

```bash
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --parts "$(jq -n --arg token "$FILE_TOKEN" \
    '[{action:"block_insert",insertion:("<img src=\""+$token+"\" topLeftX=\"500\" topLeftY=\"100\" width=\"200\" height=\"150\"/>"),insert_before_block_id:"baa"}]')"
```

Field description:

| Field | Required | Description |
|------|------|------|
| `action` | Yes | Fixed to `block_insert` |
| `insertion` | Yes | The complete XML fragment to insert |
| `insert_before_block_id` | No | Insert before this block; if omitted (this field is not provided), append to the end of the page |

> **`<img>` must use `file_token`**, external link URLs cannot be used — first use `slides +media-upload --file ./pic.png --presentation $PRES_ID` to get the token.

<a id="批量-parts"></a>
### Batch parts

A single `--parts` supports at most 200 entries, executed serially in array order. `block_replace` and `block_insert` can be mixed in the same batch. For example: replace the title block and then append a decorative image at the end in one go.

```bash
lark-cli slides +replace-slide --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --parts '[{"action":"block_replace","block_id":"bab","replacement":"<shape type=\"text\" topLeftX=\"80\" topLeftY=\"80\" width=\"800\" height=\"120\"><content textType=\"title\"><p>新标题</p></content></shape>"},{"action":"block_insert","insertion":"<img src=\"<file_token>\" topLeftX=\"700\" topLeftY=\"400\" width=\"180\" height=\"100\"/>"}]'
```

The whole batch acts as an atomic transaction: if any one entry fails, the whole batch does not take effect. On failure, the backend usually returns 3350001; if the response includes `failed_part_index` / `failed_reason` fields, the shortcut passes them through as-is.

<a id="大---parts-用-jq-或-stdin-组装"></a>
## Assembling large --parts with jq or stdin

`--parts` supports `@file` (read file) and `-` (stdin) as value sources, suitable for batch XML scenarios:

```bash
# Read from file
lark-cli slides +replace-slide --as user --presentation "$PRES_ID" --slide-id "$SID" \
  --parts @parts.json

# Read from stdin
cat parts.json | lark-cli slides +replace-slide --as user --presentation "$PRES_ID" --slide-id "$SID" \
  --parts -
```

<a id="错误排查"></a>
## Troubleshooting

| Symptom | Cause | Countermeasure |
|------|------|------|
| 3350001, hint contains "block_id not found" | `parts[i].block_id` does not exist on the current page | Use `+xml-get --slide-id` again to get the latest XML, and fill it in again according to the short ID in it |
| 3350002 not found | `--revision-id` passed a nonexistent version number | Use `-1` or the `revision_id` returned by `+xml-get --slide-id` |
| `<img>` does not display / shows a broken image | `src` wrote an external link URL | Replace it with the `file_token` obtained through `+media-upload` |
| 3350001 (returned by block_replace) | Normally the CLI has already automatically injected `id` and `<content/>`; if it still reports an error, confirm that `block_id` exists on the current page (run `+xml-get --slide-id` again), check whether the XML structure is valid; whether the coordinates exceed the 960×540 range | — |

<a id="相关文档"></a>
## Related documents

- [lark-slides-replace-slide.md](../cli/lark-slides-replace-slide.md) — +replace-slide shortcut parameter details
- [lark-slides-update-slide.md](../cli/lark-slides-update-slide.md) — +update-slide shortcut parameter details (full-page overwrite)
- [lark-slides-xml-presentations-get.md](../cli/lark-slides-xml-presentations-get.md) — `+xml-get` parameters and single-page reading method
- [lark-slides-media-upload.md](../cli/lark-slides-media-upload.md) — upload an image to get file_token
- [xml-schema-quick-ref.md](../xml/xml-schema-quick-ref.md) — XML element and attribute quick reference
