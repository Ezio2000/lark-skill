# okr +cycle-detail


List all objectives and their key results under the specified OKR cycle.

<a id="推荐命令"></a>
## Recommended Commands

```bash
# List the objectives and key results of the specified cycle (default simple style, semi-plain-text format, recommended, more concise)
lark-cli okr +cycle-detail --cycle-id 1234567890123456789

# List the objectives and key results of the specified cycle (richtext style, raw ContentBlock JSON)
lark-cli okr +cycle-detail --cycle-id 1234567890123456789 --style richtext

# Preview the API call without actually executing it
lark-cli okr +cycle-detail --cycle-id 1234567890123456789 --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter           | Required | Default      | Description                                                                                                                          |
|--------------|----|----------|-----------------------------------------------------------------------------------------------------------------------------|
| `--cycle-id` | Yes  | —        | OKR cycle ID (int64 type). Obtained from `+cycle-list`.                                                                                     |
| `--style`    | No  | `simple` | Output style: `simple` (semi-plain-text format, recommended when font/color information is not involved) \| `richtext` (raw ContentBlock JSON). Please refer to [ContentBlock format](lark-okr-contentblock.md). |
| `--dry-run`  | No  | —        | Preview the API call without actually executing it.                                                                                                            |
| `--format`   | No  | `json`   | Output format.                                                                                                                       |

<a id="工作流程"></a>
## Workflow

1. Use `lark-cli okr +cycle-list` to obtain the OKR cycle ID.
2. Execute `lark-cli okr +cycle-detail --cycle-id "123456"`.
3. Report the results: the number of objectives found, each objective's ID, score, weight, and its key results.

<a id="输出"></a>
## Output

Returns JSON:

```json
{
  "cycle_id": "1234567890123456789",
  "objectives": [
    {
      "id": "2345678901234567890",
      "create_time": "2025-01-01 00:00:00",
      "update_time": "2025-01-15 12:00:00",
      "owner": {
        "owner_type": "user",
        "user_id": "ou_xxx"
      },
      "cycle_id": "1234567890123456789",
      "position": 0,
      "score": 0.75,
      "weight": 1.0,
      "deadline": "2025-06-30 23:59:59",
      "category_id": "cat_456",
      "content": "{...}",
      "notes": "{...}",
      "key_results": [
        {
          "id": "3456789012345678901",
          "create_time": "2025-01-01 00:00:00",
          "update_time": "2025-01-15 12:00:00",
          "owner": {
            "owner_type": "user",
            "user_id": "ou_xxx"
          },
          "objective_id": "2345678901234567890",
          "position": 0,
          "score": 0.8,
          "weight": 0.5,
          "deadline": "2025-06-30 23:59:59",
          "content": "{...}"
        }
      ]
    }
  ],
  "total": 1
}
```

Among them, the format of the content and notes fields is controlled by `--style`:
- `--style simple` (default): `SemiPlainContent` object, containing the `text`, `mention`, `docs` fields
- `--style richtext`: JSON string, in OKR ContentBlock rich-text format

Please refer to [lark-okr-contentblock.md](lark-okr-contentblock.md) for detailed information on the two formats.

<a id="参考"></a>
## References

- [lark-okr](../index.md) -- all OKR commands (shortcut and API interfaces)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
