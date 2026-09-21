# okr +progress-create


Create an OKR progress record for an Objective or Key Result.

<a id="推荐命令"></a>
## Recommended Commands

```bash
# Create a progress record for an objective (default simple style, semi-plain-text format)
lark-cli okr +progress-create \
  --content '{"text":"本周完成了核心模块开发","mention":["ou_123"]}' \
  --target-id 1234567890123456789 \
  --target-type objective

# Create a progress record for a key result (richtext style, full ContentBlock format)
lark-cli okr +progress-create \
  --content '{"blocks":[{"block_element_type":"paragraph","paragraph":{"elements":[{"paragraph_element_type":"textRun","text_run":{"text":"指标已达到 80%"}}]}}]}' \
  --style richtext \
  --target-id 2345678901234567891 \
  --target-type key_result \
  --progress-percent 80 \
  --progress-status done

# Read content from a file (suitable for longer progress content)
lark-cli okr +progress-create \
  --content @progress_content.json \
  --target-id 1234567890123456789 \
  --target-type objective
```

<a id="参数"></a>
## Parameters

| Parameter                   | Required | Default                   | Description                                                                                                                                   |
|----------------------|----|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `--content`          | Yes  | —                     | Progress content. Format specified by `--style`: `simple` style is SemiPlainContent JSON, `richtext` style is ContentBlock JSON. Supports `@文件路径` to read from a file. Please refer to [ContentBlock format](lark-okr-contentblock.md). |
| `--style`            | No  | `simple`              | Input style: `simple` (semi-plain-text JSON, recommended) \| `richtext` (full ContentBlock JSON). Please refer to [ContentBlock format](lark-okr-contentblock.md) to learn about the two formats.          |
| `--target-id`        | Yes  | —                     | Objective ID or Key Result ID (int64 type, positive integer)                                                                                                         |
| `--target-type`      | Yes  | —                     | Objective type: `objective` \| `key_result`                                                                                                     |
| `--progress-percent` | No  | —                     | Progress percentage (-99999999999 - 99999999999). The percentage value is usually in the range 0-100, but values outside this range are allowed to indicate overachievement or negative growth, etc. When the quantitative metric of the mounted objective or key result does not use percentage units, this field is used to update the current value. The system retains at most two decimal places            |
| `--progress-status`  | No  | —                     | Progress status: `normal` (normal) \| `overdue` (overdue) \| `done` (completed). Only takes effect when `--progress-percent` is specified.                                                     |
| `--source-title`     | No  | `created by lark-cli` | Source title, used to display the progress source in the OKR interface                                                                                                               |
| `--source-url`       | No  | Automatically generated based on brand              | Source URL, used to display the progress source link in the OKR interface. Typically you can fill in the document link of the OKR writing information source, etc. The Feishu brand defaults to `https://open.feishu.cn/app`, and the Lark brand defaults to `https://open.larksuite.com/app` |
| `--user-id-type`     | No  | `open_id`             | User ID type: `open_id` \| `union_id` \| `user_id`                                                                                        |
| `--dry-run`          | No  | —                     | Preview the API call without actually executing it.                                                                                                                     |
| `--format`           | No  | `json`                | Output format.                                                                                                                                |

<a id="工作流程"></a>
## Workflow

1. Use `+cycle-list` and `+cycle-detail` to obtain the ID of the objective or key result.
2. Construct the progress content:
   - **Recommended**: Use `simple` style (default), construct SemiPlainContent JSON: `{"text":"内容","mention":["ou_xxx"]}`. Users mentioned in mention will all be connected at the end of the text.
   - If complex formatting is needed: Use `richtext` style, construct ContentBlock JSON. Please refer to [ContentBlock format](lark-okr-contentblock.md). If you need to insert images/Feishu documents or complex text formatting, you must use the richtext style
3. Execute `lark-cli okr +progress-create --content "..." --target-id "..." --target-type objective`.
4. Report the result: the newly created progress record ID, modification time, etc.

<a id="输出"></a>
## Output

Returns JSON:

```json
{
  "progress": {
    "progress_id": "1234567890123456789",
    "modify_time": "2025-01-15 10:30:00",
    "content": "{...}",
    "progress_rate": {
      "percent": 80.0,
      "status": "done"
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
