# okr +progress-get


Get a single OKR progress record by progress record ID.

<a id="推荐命令"></a>
## Recommended Commands

```bash
# Get the progress record with the specified ID (default simple style, semi-plain text format)
lark-cli okr +progress-get --progress-id 1234567890123456789

# Get the progress record with the specified ID (richtext style, raw ContentBlock JSON)
lark-cli okr +progress-get --progress-id 1234567890123456789 --style richtext

# Use a specific user ID type
lark-cli okr +progress-get --progress-id 1234567890123456789 --user-id-type open_id

# Preview the API call without actually executing it
lark-cli okr +progress-get --progress-id 1234567890123456789 --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter               | Required | Default         | Description                                                                 |
|------------------|----|-------------|--------------------------------------------------------------------|
| `--progress-id`  | Yes  | —           | Progress record ID (int64 type, positive integer)                                               |
| `--style`        | No  | `simple`    | Output style: `simple` (semi-plain text SemiPlainContent, recommended) \| `richtext` (raw ContentBlock JSON). Please refer to [ContentBlock format](lark-okr-contentblock.md). |
| `--user-id-type` | No  | `open_id`   | User ID type: `open_id` \| `union_id` \| `user_id`                           |
| `--dry-run`      | No  | —           | Preview the API call without actually executing it.                                                        |
| `--format`       | No  | `json`      | Output format.                                                                     |

<a id="工作流程"></a>
## Workflow

1. Get the ID of the target progress record. You can get the objective and key results via `+cycle-detail`, then obtain the progress record ID from them.
2. Execute `lark-cli okr +progress-get --progress-id "1234567890123456789"`.
3. Report the result: the progress record's ID, modification time, progress percentage, and content.

<a id="输出"></a>
## Output

Returns JSON, the format of the `content` field is controlled by `--style`:

<a id="--style-simple默认输出示例"></a>
### `--style simple` (default) output example:

```json
{
  "progress": {
    "progress_id": "1234567890123456789",
    "modify_time": "2025-01-15 10:30:00",
    "content": {
      "text": "已完成 80% 的开发工作 @{ou_zhangsan} ",
      "mention": ["ou_zhangsan"],
      "docs": [],
      "images": []
    },
    "progress_rate": {
      "percent": 75.0,
      "status": "normal"
    }
  },
  "style": "simple"
}
```

<a id="--style-richtext-输出示例"></a>
### `--style richtext` output example:

```json
{
  "progress": {
    "progress_id": "1234567890123456789",
    "modify_time": "2025-01-15 10:30:00",
    "content": "{\"blocks\":[{\"block_element_type\":\"paragraph\",\"paragraph\":{\"elements\":[{\"paragraph_element_type\":\"textRun\",\"text_run\":{\"text\":\"已完成 80% 的开发工作 \"}},{\"paragraph_element_type\":\"mention\",\"mention\":{\"user_id\":\"ou_zhangsan\"}}]}}]}",
    "progress_rate": {
      "percent": 75.0,
      "status": "normal"
    }
  },
  "style": "richtext"
}
```

Where:

- The format of the `content` field is controlled by `--style`:
  - `--style simple` (default): `SemiPlainContent` object, containing the `text`, `mention`, `docs`, `images` fields. `text` contains a `@{userID}` placeholder used to identify the mention position.
  - `--style richtext`: JSON string, in OKR ContentBlock rich text format
- Please refer to [lark-okr-contentblock.md](lark-okr-contentblock.md) for detailed information on the two formats.
- `progress_rate.status` returns a readable string: `normal` (normal), `overdue` (overdue), `done` (completed).

<a id="参考"></a>
## References

- [lark-okr](../index.md) -- all OKR commands (shortcut and API interfaces)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
