# okr +reorder


Adjust the order of Objectives under an OKR cycle or Key Results under an Objective.

<a id="推荐命令"></a>
## Recommended Commands

```bash
# Adjust Objective order
lark-cli okr +reorder \
  --cycle-id 7000000000000000001 \
  --level objective \
  --ops '[
    {"id": "7000000000000000002", "position": 2},
    {"id": "7000000000000000003", "position": 1}
  ]' \
  --as user

# Adjust KR order (requires --objective-id)
lark-cli okr +reorder \
  --cycle-id 7000000000000000001 \
  --level key-result \
  --objective-id 7000000000000000002 \
  --ops '[
    {"id": "7000000000000000004", "position": 1},
    {"id": "7000000000000000005", "position": 2}
  ]' \
  --as user

# Read ops from a file
lark-cli okr +reorder \
  --cycle-id 7000000000000000001 \
  --level objective \
  --ops @reorder_ops.json \
  --as user
```

- Multiple objective/key-result items are not allowed to be placed at the same position

<a id="参数"></a>
## Parameters

| Parameter               | Required | Default    | Description                                                      |
|------------------|----|--------|---------------------------------------------------------|
| `--level`        | Yes  | —      | Adjustment level: `objective` (adjust the order of Objectives under a cycle) \| `key-result` (adjust the order of KRs under an Objective) |
| `--cycle-id`     | Yes  | —      | OKR cycle ID (int64 type).                                    |
| `--objective-id` | Conditional | —      | Objective ID. When `--level=key-result`, this is **required**, used to locate the parent Objective.           |
| `--ops`          | Yes  | —      | Order adjustment operations in JSON array format. Supports reading from stdin via `@文件路径` or `@-`.          |
| `--dry-run`      | No  | —      | Preview the API call without actually executing it                                         |
| `--format`       | No  | `json` | Output format                                                    |

<a id="工作流程"></a>
## Workflow

1. Use `+cycle-list` and `+cycle-detail` to obtain the cycle ID, Objective ID, and KR ID.
2. Construct the `--ops` JSON array, specifying the IDs to adjust and the new position, then execute the command.
3. Return the complete order after adjustment.

<a id="输出"></a>
## Output

On success, returns JSON (taking adjusting an Objective's position as an example):

```json
{
  "ok": true,
  "data": {
    "level": "objective",
    "cycle_id": "7000000000000000001",
    "total": 3,
    "ordered": [
      "7000000000000000003",
      "7000000000000000002",
      "7000000000000000004"
    ]
  }
}
```

<a id="参考"></a>
## References

- [OKR business entities](lark-okr-entities.md) -- OKR entity structure definition
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
