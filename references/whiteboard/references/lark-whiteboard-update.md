<a id="whiteboard-update更新画板"></a>
# whiteboard +update (Update Whiteboard)


Update whiteboard content. Supports four input formats:

- `raw`: Feishu OpenAPI native whiteboard node format; direct editing is not recommended.
- `plantuml`: PlantUML code
- `mermaid`: Mermaid code
- `svg`: SVG text

Input content can be read from stdin via a pipe, or a file can be specified via `--source`.

<a id="参数"></a>
## Parameters

| Parameter                   | Required | Description                                         |
|----------------------|----|--------------------------------------------|
| `--whiteboard-token` | Yes  | Whiteboard token; you need edit permission on the whiteboard                       |
| `--idempotent-token` | No  | Idempotency token to ensure the update operation is idempotent; at least 10 characters; recommended to concatenate a timestamp + scenario identifier (e.g. `1744800000-board-1`). Generate this token only once per logical update, and reuse it as-is on retries; never regenerate the timestamp or idempotency key on each retry, otherwise duplicate writes will occur |
| `--overwrite`        | No  | Write mode: if provided, overwrite update (delete all existing whiteboard content before writing, then write); if omitted, incremental append (keep existing content and write new content on top). Default false (incremental append)|
| `--source`           | Yes  | Input whiteboard content; supports reading from a file using `@path`, or reading from stdin using `-` |
| `--input_format`     | No  | Input format: `raw`, `plantuml`, `mermaid`, `svg`; default is `raw`  |

<a id="以-raw-openapi-原生画板节点格式-创作"></a>
### Creating with raw (OpenAPI native whiteboard node format)

**Do not create raw-format Feishu OpenAPI native whiteboard node parameters by directly generating JSON syntax**

For diagrams such as mind maps, sequence diagrams, class diagrams, pie charts, and flowcharts, it is recommended to draw them using Mermaid/PlantUML syntax.

When you need to draw architecture diagrams, organization charts, swimlane diagrams, comparison charts, fishbone diagrams, bar charts, line charts, tree diagrams, funnel charts, pyramid charts, cycle/flywheel diagrams, milestones, or other relatively complex diagrams, it is recommended to refer to [§ Rendering & Writing to Whiteboard](lark-whiteboard-workflow.md#渲染--写入画板) and use the whiteboard-cli tool to create them.

<a id="示例"></a>
## Examples

<a id="示例-1使用-plantuml-代码更新画板从-stdin-读取"></a>
### Example 1: Update a whiteboard using PlantUML code (read from stdin)

```bash
# Write PlantUML code
cat > diagram.puml << 'EOF'
@startuml
Alice -> Bob: Hello
Bob -> Alice: Hi
@enduml
EOF

# Pass to the command via a pipe
cat diagram.puml | lark-cli whiteboard +update \
  --whiteboard-token <画板Token> \
  --input_format plantuml --source -\
  --overwrite --as user
```

<a id="示例-2使用-mermaid-代码更新画板从文件读取"></a>
### Example 2: Update a whiteboard using Mermaid code (read from a file)

```bash
# Write Mermaid code
cat > diagram.mmd << 'EOF'
graph TD
    A[开始] --> B{判断}
    B -->|是| C[处理]
    B -->|否| D[结束]
    C --> D
EOF

# Read from a file and update
lark-cli whiteboard +update \
  --whiteboard-token <画板Token> \
  --input_format mermaid \
  --source @./diagram.mmd \
  --overwrite --as user
```

<a id="示例-3使用-whiteboard-cli-生成-openapi-格式并写入画板"></a>
### Example 3: Use whiteboard-cli to generate OpenAPI format and write it to the whiteboard

For specific usage of the whiteboard-cli tool, refer to [§ Rendering & Writing to Whiteboard](lark-whiteboard-workflow.md#渲染--写入画板)

```bash
# Use whiteboard-cli to generate OpenAPI format and pass it via a pipe
npx -y @larksuite/whiteboard-cli@^0.2.13 -i <产物文件> --to openapi --format json \
  | lark-cli whiteboard +update \
    --whiteboard-token <画板Token> \
    --source - --input_format raw \
    --idempotent-token <10+字符唯一串> \
    --as user
```

<a id="示例-4先生成产物文件再从文件读取更新"></a>
### Example 4: First generate an artifact file, then read from the file and update

For specific usage of the whiteboard-cli tool, refer to [§ Rendering & Writing to Whiteboard](lark-whiteboard-workflow.md#渲染--写入画板)

```bash
# Generate OpenAPI format to a file
npx -y @larksuite/whiteboard-cli@^0.2.13 -i <DSL 文件> --to openapi --format json -o ./temp.json

# Read from a file and update
lark-cli whiteboard +update \
  --whiteboard-token <画板Token> \
  --idempotent-token <10+字符唯一串> \
  --input_format raw \
  --source @./temp.json \
  --overwrite --as user
```

<a id="示例-5使用-svg-写入画板从文件读取"></a>
### Example 5: Write to a whiteboard using SVG (read from a file)

Suitable for creating from scratch (writing SVG directly) and editing an existing whiteboard (for the editing workflow, see [`../routes/svg-edit.md`](../routes/svg-edit.md)).

```bash
# Write or export an SVG file
cat > diagram.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
  <rect x="10" y="10" width="80" height="40" fill="#4A90E2"/>
  <text x="50" y="35" text-anchor="middle" fill="#fff">Hello</text>
</svg>
EOF

# Read from a file and update
lark-cli whiteboard +update \
  --whiteboard-token <画板Token> \
  --input_format svg \
  --source @./diagram.svg \
  --overwrite --as user
```
