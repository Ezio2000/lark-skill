# okr +progress-update


Update the content of the OKR progress record with the specified ID.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Update the progress record content (default simple style, semi-plain-text format)
lark-cli okr +progress-update \
  --progress-id 1234567890123456789 \
  --content '{"text":"更新后的进展内容","mention":["ou_123"]}'

# Update the progress record content and update the progress at the same time (richtext style, full ContentBlock format)
lark-cli okr +progress-update \
  --progress-id 1234567890123456789 \
  --content '{"blocks":[{"block_element_type":"paragraph","paragraph":{"elements":[{"paragraph_element_type":"textRun","text_run":{"text":"进度已更新至 90%"}}]}}]}' \
  --style richtext \
  --progress-percent 90 \
  --progress-status normal

# Read content from a file (suitable for longer progress content)
lark-cli okr +progress-update \
  --progress-id 1234567890123456789 \
  --content @updated_progress.json

# Preview the API call without actually executing it
lark-cli okr +progress-update \
  --progress-id 1234567890123456789 \
  --content '{"text":"test"}' \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter                   | Required | Default value       | Description                                                                                                             |
|----------------------|----|-----------|----------------------------------------------------------------------------------------------------------------|
| `--progress-id`      | Yes  | —         | Progress record ID (int64 type, positive integer)                                                                                          |
| `--content`          | Yes  | —         | Progress content. Format specified by `--style`: `simple` style is SemiPlainContent JSON, `richtext` style is ContentBlock JSON. Supports `@文件路径` to read from a file. Please refer to [ContentBlock format](lark-okr-contentblock.md). |
| `--style`            | No  | `simple`  | Input style: `simple` (semi-plain-text JSON, recommended) \| `richtext` (full ContentBlock JSON). Please refer to [ContentBlock format](lark-okr-contentblock.md) to learn about the two formats.          |
| `--progress-percent` | No  | —         | Progress percentage (-99999999999 - 99999999999). The percentage value is usually in the range 0-100, but values outside this range are allowed to indicate situations such as overachievement or negative growth. When the quantitative metric of the mounted objective or key result does not use percentage units, use this field to update the current value. The system retains at most two decimal places |
| `--progress-status`  | No  | —         | Progress status: `normal` (normal) \| `overdue` (overdue) \| `done` (completed). Only takes effect when `--progress-percent` is specified.                               |
| `--user-id-type`     | No  | `open_id` | User ID type: `open_id` \| `union_id` \| `user_id`                                                                  |
| `--dry-run`          | No  | —         | Preview the API call without actually executing it.                                                                                               |
| `--format`           | No  | `json`    | Output format.                                                                                                          |

<a id="工作流程"></a>
## Workflow

1. Use `+progress-get` to get the ID and current content of the progress record to be updated.
2. Modify the progress content:
   - **Recommended**: Use `simple` style (default), construct SemiPlainContent JSON: `{"text":"内容","mention":["ou_xxx"]}`, and users mentioned in mention will all be concatenated at the end of the text.
   - If complex formatting is needed: Use `richtext` style, construct ContentBlock JSON. Please refer to [ContentBlock format](lark-okr-contentblock.md). If you need to insert images/Feishu documents or complex text formatting, you must use richtext style
3. Execute `lark-cli okr +progress-update --progress-id "..." --content "..."`.
4. Report the result: the updated progress record ID, modification time, progress percentage, etc.

<a id="输出"></a>
## Output

Returns JSON:

```json
{
  "progress": {
    "progress_id": "1234567890123456789",
    "modify_time": "2025-01-15 14:30:00",
    "content": "{...}",
    "progress_rate": {
      "percent": 90.0,
      "status": "normal"
    }
  }
}
```

Where:

- The `content` field is a JSON string, in OKR ContentBlock
  rich text format. Please refer to [lark-okr-contentblock.md](lark-okr-contentblock.md) for details.
- `progress_rate.status` returns a readable string: `normal` (normal), `overdue` (overdue), `done` (completed).

<a id="参考"></a>
## References

- [lark-okr](../index.md) -- all OKR commands (shortcut and API interfaces)
- [ContentBlock format](lark-okr-contentblock.md) -- the rich text format used by progress content
- [lark-shared](../../shared/index.md) -- authentication and global parameters
