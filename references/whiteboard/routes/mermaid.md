<a id="mermaid-路径"></a>
# Mermaid Path

Applies to: mind maps, sequence diagrams, class diagrams, pie charts, Gantt charts.

## Workflow

```
Step 1: Read knowledge
  - Read scenes/mermaid.md — Mermaid syntax and usage

Step 2: Generate Mermaid
  - Write the .mmd file according to the syntax in mermaid.md
  - Output only plain Mermaid syntax text

Step 3: Render validation & write to board & deliver
  1. Create the artifact directory ./diagrams/YYYY-MM-DDTHHMMSS/
  2. Save as diagram.mmd
  3. Render (for preview validation only; the PNG is not the final artifact):
       npx -y @larksuite/whiteboard-cli@^0.2.13 -i diagram.mmd -o diagram.png
  4. Review the PNG; if there are issues, fix them and re-render (at most 2 rounds)
  5. Write to board: use whiteboard-cli to convert diagram.mmd to OpenAPI format and pipe it to +update:
       npx -y @larksuite/whiteboard-cli@^0.2.13 -i diagram.mmd --to openapi --format json \
         | lark-cli whiteboard +update --whiteboard-token <board_token> \
             --source - --input_format raw --idempotent-token <时间戳+标识> --as user
       → For the full dry-run / confirmation flow, see [§ Write to Board](../references/lark-whiteboard-workflow.md#写入画板)
  6. Deliver: report to the user that board_token was written successfully
```
