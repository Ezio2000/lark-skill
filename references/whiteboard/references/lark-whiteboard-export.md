<a id="whiteboard-export导出画板"></a>
# whiteboard +export (Export Whiteboard)


Export whiteboard content. Supports exporting as a preview image, SVG vector graphic, extracting PlantUML/Mermaid code, or retrieving the Feishu OpenAPI native whiteboard node format.

<a id="参数"></a>
## Parameters

| Parameter                   | Required | Description                                                                     |
|----------------------|----|------------------------------------------------------------------------|
| `--whiteboard-token` | Yes  | Whiteboard token. Requires read permission for the whiteboard                                                    |
| `--output-type`      | Yes  | Output format: `preview` (preview image), `svg` (SVG vector graphic), `source` (PlantUML/Mermaid code), `raw` (OpenAPI native whiteboard node format) |
| `--output`           | No  | Output path. Required when `--output-type preview`; optional when `--output-type svg/source/raw`, if not provided, output directly to the terminal |
| `--overwrite`        | No  | Overwrite existing files. Defaults to false                                                     |

<a id="输出格式"></a>
## Output Formats

- `preview`: Preview image. When saving, the extension is determined by the actual `Content-Type` returned by the API. For example, `image/jpeg` will be saved as `.jpg`.
- `svg`: Export the whiteboard as a standard SVG vector graphic. Can be used to write back to the whiteboard after SVG editing (see [`routes/svg-edit.md`](../routes/svg-edit.md)). Note: The export is a purely visual snapshot; semantic information such as mind map hierarchy, table structure, and connector bindings will be lost.
- `source`: PlantUML/Mermaid code. Code can only be exported when there is exactly one PlantUML/Mermaid diagram in the whiteboard; otherwise the return value will indicate that no node exists or there are multiple nodes.
- `raw`: Feishu OpenAPI native whiteboard node format. This JSON format is not suitable for directly editing complex layouts or content. It is recommended to use it only when you need to modify simple details such as text content or colors. For more complex design/modification needs, refer to [§ Editing Workflow](lark-whiteboard-workflow.md#编辑-workflow).
  - **When editing and writing back is needed, be sure to add `--output <file>` when exporting to write to a file**: The file content can be used directly as input for `+update`; results output directly to the terminal will have an extra layer of `{ ok, identity, data }` wrapping, which `+update` cannot parse.

<a id="示例"></a>
## Examples

<a id="示例-1导出画板为预览图片"></a>
### Example 1: Export whiteboard as a preview image

```bash
lark-cli whiteboard +export \
  --whiteboard-token "wbcnxxxxxxxx" \
  --output-type preview \
  --output ./preview
```

<a id="示例-2提取画板中的代码并直接输出"></a>
### Example 2: Extract code from the whiteboard and output directly

```bash
lark-cli whiteboard +export \
  --whiteboard-token "wbcnxxxxxxxx" \
  --output-type source
```

<a id="示例-3导出画板为-svg-矢量图"></a>
### Example 3: Export whiteboard as an SVG vector graphic

```bash
lark-cli whiteboard +export \
  --whiteboard-token "wbcnxxxxxxxx" \
  --output-type svg \
  --output ./whiteboard.svg \
  --as user
```

<a id="示例-4导出画板原始节点结构到文件"></a>
### Example 4: Export the whiteboard's raw node structure to a file

```bash
lark-cli whiteboard +export \
  --whiteboard-token "wbcnxxxxxxxx" \
  --output-type raw \
  --output ./nodes.json \
  --overwrite
```
