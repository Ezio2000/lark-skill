# okr +indicator-update


Directly update the current value of an Objective or Key Result indicator, without needing to manually query the indicator ID.

> **Querying indicators:** To view indicator details, use the native API:
> - Objective indicator: `lark-cli okr objective.indicators list --objective-id <id>`
> - KR indicator: `lark-cli okr key_result.indicators list --key-result-id <id>`

<a id="推荐命令"></a>
## Recommended commands

```bash
# Update the Objective's indicator value
lark-cli okr +indicator-update \
  --level objective \
  --id 7000000000000000001 \
  --value 75.5 \
  --as user

# Update the Key Result's indicator value
lark-cli okr +indicator-update \
  --level key-result \
  --id 7000000000000000002 \
  --value 100 \
  --as user
```

<a id="参数"></a>
## Parameters

| Parameter         | Required | Default    | Description                                                                 |
|------------|----|--------|--------------------------------------------------------------------|
| `--level`  | Yes  | —      | Operation level: `objective` (update Objective indicator) \| `key-result` (update KR indicator) |
| `--id`     | Yes  | —      | Objective ID or KR ID (int64 type)                                       |
| `--value`  | Yes  | —      | New current value of the indicator (number, range: -99999999999 to 99999999999)              |
| `--dry-run`| No  | —      | Preview the API call without actually executing it                                            |
| `--format` | No  | `json` | Output format                                                             |

<a id="工作流程"></a>
## Workflow

1. Use `+cycle-list` and `+cycle-detail` to obtain the Objective ID or KR ID.
2. To view the current indicator value, query using `objective.indicators list` or `key_result.indicators list`.
  If the current quantitative indicator does not have the start_value/current_value/target_value/unit fields, it means the current quantitative indicator is an unset default initial progress.
3. Execute `+indicator-update` specifying the level, ID, and new value.
  Using +indicator-update to set a current value for the default initial progress will configure that quantitative indicator as the default percentage mode. If the user does not want the indicator to be set to a percentage, use the native API for detailed settings; refer to [lark-okr-indicators.md](lark-okr-indicators.md)
4. The command automatically queries the indicator ID and updates the current value.

<a id="输出"></a>
## Output

<a id="json-格式"></a>
### JSON format

```json
{
  "ok": true,
  "data": {
    "indicator_id": "7000000000000000003",
    "current_value": 75.5,
    "level": "objective",
    "target_id": "7000000000000000001"
  }
}
```

<a id="字段说明"></a>
### Field descriptions

| Field             | Type     | Description                     |
|----------------|--------|------------------------|
| `indicator_id` | string | The updated indicator ID            |
| `current_value`| number | The updated current value of the indicator           |
| `level`        | string | Operation level: `objective` / `key-result` |
| `target_id`    | string | The ID of the Objective or KR            |

<a id="注意事项"></a>
## Notes
- Only the `current_value` field is updated; other fields such as `unit`, `start_value`, `target_value` remain unchanged
  - If these fields need to be modified, use the native API indicators.patch
- The indicator's `current_value_calculate_type` must be "manual update" in order to be modified through this command.

<a id="参考"></a>
## References

- [OKR indicator update API](https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=patch&project=okr&resource=okr.indicator&version=v2)
- [`lark-okr-progress-create.md`](./lark-okr-progress-create.md) — Create a progress record
- [`lark-okr-cycle-detail.md`](./lark-okr-cycle-detail.md) — Query cycle details to obtain the ID
