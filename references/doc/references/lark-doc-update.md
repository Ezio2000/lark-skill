<a id="docs-update更新飞书云文档"></a>
# docs +update (Update Feishu Cloud Docs)

Use text or block commands to precisely update Feishu Cloud Docs. Use XML by default; use Markdown only when the user explicitly requests it or when Markdown fidelity is required.

Before writing, you must read the corresponding format reference according to `--doc-format`: for `xml`, read [`lark-doc-xml.md`](lark-doc-xml.md); for `markdown`, read [`lark-doc-md.md`](lark-doc-md.md);

<a id="常用示例"></a>
## Common Examples

```bash
# First locate the content and get the latest block ID
lark-cli docs +fetch --doc "文档URL或token" --scope keyword --keyword "key1|key2" --detail with-ids

# Replace text; --content "" can delete text
lark-cli docs +update --doc "xx" --command str_replace --pattern "旧内容" --content "新内容"

# Replace a single block, or blocks within a contiguous range under the same parent
lark-cli docs +update --doc "xx" --command block_replace --block-id blkTarget --content '<p>新段落</p>'
lark-cli docs +update --doc "xx" --command block_replace --start-block-id blkFirst --end-block-id blkLast --content '<p></p>'

lark-cli docs +update --doc "xx" --command block_insert_after --block-id blkAnchor --content '<h2>新章节</h2><p>章节内容</p>'

# Delete a single block or blocks within a range
lark-cli docs +update --doc "xx" --command block_delete --block-id blkA
lark-cli docs +update --doc "xx" --command block_delete --start-block-id blkFirst --end-block-id blkLast
```

<a id="推荐流程"></a>
## Recommended Workflow

1. **Observe (read the current state)**: First use `docs +fetch` to read the current document state, and select the minimal scope according to your intent.
   - To modify a section or a large document: first use `--scope outline --max-depth 2` to find the section, then `--scope section --start-block-id <标题id> --detail with-ids`
   - For a precise cross-section range: use `--scope range --start-block-id xxx --end-block-id yyy`
   - If you only have vague keywords: use `--scope keyword --keyword "key1|key2" --context-before 1 --context-after 1 --detail with-ids`
   - Only read the full text with `--detail with-ids` when a complete rewrite is clearly intended; use a lighter fetch when only reading a summary or confirming facts
2. **Diagnose (diagnose the problem)**: Determine the user's goal, current structure, tone, duplication, broken flow, factual alignment, and resources that need to be preserved; identify which blocks must be kept as-is.
3. **Patch Plan (create a localized plan)**: Break the modifications into minimal safe operations: use `str_replace` for simple inline text replacement, but it does not support resource replacement; use one `--block-id` for a single block, and `--start-block-id`/`--end-block-id` for contiguous blocks under the same direct parent node. Contiguous ranges apply to `block_replace` and `block_delete`. Use `block_replace` for rewriting an entire paragraph/block; use `block_insert_after` to add sections; use `block_delete` to remove redundancy; use `block_move_after` to adjust order.
4. **Patch (precise modification)**: Execute localized commands by block / section. The replacement content must conform to the structure of the target parent container; for example, use `<li>...</li>` when replacing a range of list items. Protect tokenized content such as `<cite>`, `<img>`, `<source>`, `<whiteboard>`, `<sheet>`, `<bitable>`, `<synced_reference>`; do not convert them to plain text or placeholders. Merge multiple modifications to the same block into a single `block_replace`.
5. **Verify (fetch verification)**: After each round of write operations, re-fetch according to the affected scope, and check whether the user's requirements, structure, tone, facts, resource blocks, and block IDs meet expectations; if not, continue Diagnose / Patch based on the latest fetch results, and do not reuse block IDs from the previous round.

Unless the user explicitly requests a complete rebuild, or the original text no longer has value to preserve, do not use `overwrite`; it may lose comments and resources that are not yet supported.

<a id="生成-block-直达链接"></a>
## Generate Block Direct Links

When the user needs a direct link to a block, only locate the block and do not perform any document write operations:

1. Use a localized `docs +fetch --detail with-ids` to obtain the target `block_id`.
2. Return `文档基础 URL#block_id`; if there is no `block_id`, do not guess.

<a id="参数"></a>
## Parameters

|Parameter|Required|Description|
|-|-|-|
|`--doc`|Yes|Document URL or token|
|`--command`|Yes|Update command, see the table below|
|`--doc-format`|No|`xml` (default) or `markdown`|
|`--content`|Depends on command|Content to write; for `str_replace`, passing an empty string deletes text|
|`--pattern`|Depends on command|Simple inline match text for `str_replace`; do not use for multiple lines, entire paragraphs, or multiple blocks|
|`--block-id`|Depends on command|Target block ID; `-1` means the end of the document, `0` means the beginning of the document (only applies to commands that support these anchors)|
|`--start-block-id` / `--end-block-id`|Depends on command|Contiguous closed interval under the same parent for `block_replace` / `block_delete`, must be used in pairs, and cannot be mixed with `--block-id`; for `--start-block-id`, use `0` to indicate starting from the beginning of the document; for `--end-block-id`, use `-1` to indicate ending at the end of the document|
|`--src-block-ids`|Depends on command|Source block ID(s) to copy or move; separate multiple IDs with commas|
|`--reference-map`|No|Preserve or replay existing `reference_map`, must be used together with `--content`; supports JSON, a relative `@file` within the task directory, or stdin `-`|
|`--revision-id`|No|Base version number, defaults to `-1` (latest version)|

<a id="指令速查"></a>
## Command Quick Reference

|Command|Purpose and Limitations|Required Parameters|
|-|-|-|
|`str_replace`|Full-document find and replace; supports text replacement within rich text, but does not support resource replacement; when multiple blocks are involved, `block_replace` is recommended; an empty `--content` means delete|`--pattern`, `--content`|
|`block_insert_after`|Insert content after the specified block; when filling in chapter by chapter, specify the block ID of the corresponding heading|`--block-id`, `--content`|
|`block_copy_insert_after`|Copy source blocks in ID order; the source blocks remain unchanged; all basic tags are supported, and for resource blocks only `img`, `source`, `whiteboard`, `sheet`, `chat_card`, `sub-page-list` are supported; `task`, `bitable`, `base_ref`, `synced_reference`, `synced_source`, `okr` are not supported|`--block-id`, `--src-block-ids`|
|`block_replace`|Replace a single block (`--block-id`) or a contiguous closed interval under the same parent (`--start-block-id`/`--end-block-id`); cross-container or reversed intervals are not supported|`--content`, and `--block-id` or `--start-block-id`+`--end-block-id`|
|`block_delete`|Delete a single block (`--block-id`) or a contiguous closed interval under the same parent (`--start-block-id`/`--end-block-id`); cross-container or reversed intervals are not supported|`--block-id` or `--start-block-id`+`--end-block-id`|
|`block_move_after`|Move existing blocks; supports all block types;|`--block-id`, `--src-block-ids`|
|`append`|Append only at the end of the document, equivalent to `block_insert_after --block-id -1`|`--content`|
|`overwrite`|Clear and rewrite the entire document; loses images, comments, and other content; do not use unless necessary|`--content`|

<a id="通用安全规则"></a>
## General Safety Rules

- After every write operation, treat block IDs as having changed. Newly inserted or copied content must use new IDs; replacement, deletion, and overwriting invalidate old IDs; moving changes section and range semantics.
- When there are multiple modifications to the same block, merge them into a single `block_replace` to avoid consecutively using old IDs.

<a id="返回值"></a>
## Return Values

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "revision_id": 2,
      "new_blocks": [
        { "block_id": "blkcnXXXX", "block_type": "whiteboard", "block_token": "boardXXXX" }
      ]
    },
    "result": "success",
    "updated_blocks_count": 1,
    "warnings": [],
    "tips": ""
  }
}
```

|Field|Description|
|-|-|
|`result`|`success` \| `partial_success` \| `failed`|
|`updated_blocks_count`|Actual number of blocks updated|
|`warnings`|List of warnings returned by the server; even if `result=success`, check whether there is degraded or incompletely processed content|
|`tips`|Follow-up processing suggestions returned by the server; empty means there are no additional suggestions, and non-empty does not by itself indicate that the update failed|
|`document.new_blocks`|Newly added blocks; `block_id` is used for subsequent editing, and the `block_token` of resource blocks can be handed off to the corresponding skill for further processing|

<a id="需要查文档"></a>
## Need to Check the Documentation

You can view [`+fetch`](lark-doc-fetch.md).
