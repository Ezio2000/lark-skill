# okr +weight


Adjust the weight of an Objective under an OKR cycle or a Key Result under an Objective. Supports specifying weights partially; unspecified ones are automatically allocated in proportion to their original weights.

<a id="推荐命令"></a>
## Recommended Commands

```bash
# Adjust Objective weights (partially specified, the remainder automatically allocated)
lark-cli okr +weight \
  --cycle-id 7000000000000000001 \
  --level objective \
  --weights '[
    {"id": "7000000000000000002", "weight": 0.6},
    {"id": "7000000000000000003", "weight": 0.3}
  ]' \
  --as user

# Adjust KR weights (all specified, sum equals 1)
lark-cli okr +weight \
  --cycle-id 7000000000000000001 \
  --level key-result \
  --objective-id 7000000000000000002 \
  --weights '[
    {"id": "7000000000000000004", "weight": 0.6},
    {"id": "7000000000000000005", "weight": 0.4}
  ]' \
  --as user

# Read weights from a file
lark-cli okr +weight \
  --cycle-id 7000000000000000001 \
  --level objective \
  --weights @weights.json \
  --as user
```

Parameter limits: Weights in the request retain three decimal places, and the sum of all allocated weights cannot exceed 1 (less than or equal to 1 is allowed).

<a id="权重归一化"></a>
### Weight Normalization

- In OKR, the sum of the weights of all Objectives under a cycle and all Key Results under an Objective is fixed at 1.
- When using the +weight shortcut to allocate OKR weights, the total allocated weight must not exceed 1.
- If the allocated weight < 1, the remaining weight is distributed evenly to the unspecified Objectives/Key Results in proportion to their original weights.
  - If all Objectives/Key Results have been assigned weights but the sum < 1, the remaining weight is calculated under the last Objective/Key Result.



<a id="参数"></a>
## Parameters

| Parameter               | Required | Default    | Description                                                                  |
|------------------|----|--------|---------------------------------------------------------------------|
| `--level`        | Yes  | —      | Adjustment level: `objective` (adjust Objective weights under a cycle) \| `key-result` (adjust KR weights under an Objective)             |
| `--cycle-id`     | Yes  | —      | OKR cycle ID (int64 type)                                                 |
| `--objective-id` | Conditional | —      | Objective ID. When `--level=key-result`, this is **required**, used to locate the parent Objective.                       |
| `--weights`      | Yes  | —      | Weight allocation in JSON array format. Supports `@文件路径` or `@-` to read from stdin. Weights retain three decimal places, and the sum of all allocated weights cannot exceed 1 |
| `--dry-run`      | No  | —      | Preview the API call without actually executing it                                                     |
| `--format`       | No  | `json` | Output format                                                                |

<a id="工作流程"></a>
## Workflow

1. Use `+cycle-list` and `+cycle-detail` to obtain the cycle ID, Objective ID, KR ID, and current weights.
2. Construct the `--weights` JSON array, specifying the IDs and weights to adjust, and execute the command.
3. Return the complete list of weights after adjustment.

<a id="输出"></a>
## Output

On success, returns JSON:

```json
{
  "ok": true,
  "data": {
    "level": "objective",
    "cycle_id": "7000000000000000001",
    "total": 3,
    "weights": [
      {"id": "7000000000000000002", "weight": 0.6},
      {"id": "7000000000000000003", "weight": 0.3},
      {"id": "7000000000000000004", "weight": 0.1}
    ]
  }
}
```

<a id="关于-1001001-错误"></a>
## About the 1001001 Error

Sometimes, even if the input parameters are completely correct, +weight returns a 1001001 error. This is because the weight-setting feature for Objectives or Key Results may not be enabled in your tenant settings.
If you confirm that the input parameters are correct (cycle-id/objective-id are correct, the ids in weights are all Objectives under the same cycle or Key Results under the same Objective, and the sum of weights in weights < 1),
do not make further attempts; you need to confirm with the user whether the OKR app currently has the weight-setting feature for Objectives or Key Results enabled.

<a id="参考"></a>
## References

- [OKR business entities](lark-okr-entities.md) -- OKR entity structure definition
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
