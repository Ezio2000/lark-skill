<a id="docs-create创建飞书云文档"></a>
# docs +create (Create a Feishu cloud document)

Create a Feishu cloud document from XML (CLI default) or Markdown content. Simple paragraphs, lists, and tables can use Markdown directly; use XML for precise layout, complex blocks, or XML extension components. Explicitly specify `--doc-format`, and follow the user's format and fidelity requirements.

Before writing, you must read the corresponding format reference according to `--doc-format`: for `xml`, read [`lark-doc-xml.md`](lark-doc-xml.md); for `markdown`, read [`lark-doc-md.md`](lark-doc-md.md); when using XML extension tags in Markdown, you must also read `lark-doc-xml.md`.

<a id="命令"></a>
## Command

```bash
# For simple content, prefer `--content -`; file import is as follows:
lark-cli docs +create --doc-format xml --content "@<XML 文件相对路径>"
lark-cli docs +create --doc-format markdown --content "@./draft.md"
```

<a id="返回值"></a>
## Return Value

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "document_id": "docx_token",
      "revision_id": 1,
      "url": "https://xxx.feishu.cn/docx/docx_token",
      "new_blocks": [
        { "block_id": "blkcnXXXX", "block_type": "whiteboard", "block_token": "boardXXXX" }
      ]
    },
    "warnings": [],
    "tips": ""
  }
}
```

- **`document.new_blocks`**: The list of blocks newly added by this operation (such as a whiteboard). `block_id` can be used for precise editing of `docs +update`'s `--block-id`; `block_token` is the token of a resource block (such as a whiteboard), which can be handed to skills such as `lark-whiteboard` for further operations.
- **`warnings`**: The list of warnings returned by the server; also check when `ok=true`, and follow the prompts to confirm whether there is degraded or incompletely processed content.
- **`tips`**: Follow-up handling suggestions returned by the server; empty means there are no additional suggestions, and non-empty itself does not indicate that creation failed.
- **`permission_grant`**: Returned only when creating as a bot. The CLI will attempt to grant the current CLI user `full_access` on the new document; `status` being `granted` indicates successful authorization, `skipped` indicates there is no available current user `open_id`, and `failed` indicates the document was created but authorization failed. `perm` is fixed as `full_access`; on failure or skip, handle according to `message` / `hint`. **Automatic authorization does not equal owner transfer; it is only executed when the user authorizes an owner transfer; existing explicit authorization can be reused.**

<a id="参数"></a>
## Parameters

|Parameter|Required|Description|
|-|-|-|
|`--title`|No|Document title, used for Markdown import; for XML creation, it is recommended to write `<title>...</title>` at the beginning of `--content`; if there are multiple titles, only the first is kept|
|`--content`|Depends|Document content (XML or Markdown format); if `--content` is not passed, `--title` must be passed|
|`--reference-map`|No|Structured `reference_map` JSON object; must be used together with `--content`. For ordinary writing, prefer putting the structure in the body; this parameter is mainly used to preserve or replay an existing `document.reference_map`. Supports direct JSON, a relative `@file` within the task-exclusive directory, or `-` to read from stdin.|
|`--doc-format`|No|CLI default is `xml`, and it should be passed explicitly; for plain text structures or importing Markdown as-is, `markdown` can be used. Do not mix complete XML and Markdown document formats; XML extension tags already defined by the document are allowed in Markdown.|
|`--parent-token`|No|Parent folder or wiki node token (mutually exclusive with `--parent-position`)|
|`--parent-position`|No|Parent node position, such as `my_library` (mutually exclusive with `--parent-token`)|

<a id="需要回查文档"></a>
## Need to Look Up the Document

Use `lark-cli docs +fetch --doc "<document_id 或文档 URL>" --detail with-ids` to look it up; if more information is needed, see [`+fetch`](lark-doc-fetch.md).
