<a id="okr-量化指标管理"></a>
# OKR Quantitative Indicator Management


Manage the quantitative indicators of OKR objectives (Objective) and key results (Key Result), including querying and updating indicators.

> **Quickly update the current value:** If you only need to update the current value of an indicator, it is recommended to use the shortcut [`okr +indicator-update`](lark-okr-indicator-update.md), without needing to manually query the indicator ID.
>
> The native API in this guide is suitable for scenarios that require modifying other fields of the indicator (such as `unit`, `target_value`, `status_calculate_type`, etc.).

---

<a id="指标字段说明"></a>
## Indicator Field Descriptions

| Field                          | Type   | Description                                                                 |
|-----------------------------|------|--------------------------------------------------------------------|
| `id`                        | string | Indicator ID (required when updating)                                                     |
| `entity_id` / `entity_type` | string/int | Owning entity ID and type (2=objective, 3=key result)                                   |
| `current_value`             | number | Current value                                                                 |
| `target_value`              | number | Target value                                                                 |
| `start_value`               | number | Start value                                                                 |
| `indicator_status`          | int    | Status: -1=undefined, 0=normal, 1=at risk, 2=delayed                                   |
| `status_calculate_type`     | int    | Status calculation method: 0=manual update, 1=automatically updated based on progress and current time, 2=updated based on the status of the highest-risk KR       |
| `current_value_calculate_type` | int | Current value calculation method: 0=manual update, 1=automatically updated based on KR progress (objective), 2=updated based on the progress of decomposed KRs (KR) |
| `unit`                      | object | Unit, including `unit_type` (0=public, 1=custom) and `unit_value` (such as PERCENT, YUAN, etc.)       |
| `owner`                     | object | Owner                                                                 |

---

<a id="一查询目标的量化指标"></a>
## I. Query the Quantitative Indicators of an Objective

<a id="命令"></a>
### Command

```bash
lark-cli okr objective.indicators list --objective-id "<目标ID>" [flags]
```

<a id="常用示例"></a>
### Common Examples

```bash
# Get the quantitative indicators of an objective
lark-cli okr objective.indicators list \
  --objective-id 7000000000000000001

# Specify the user ID type
lark-cli okr objective.indicators list \
  --objective-id 7000000000000000001 \
  --user-id-type "user_id"
```

<a id="参数"></a>
### Parameters

| Parameter                   | Required | Default value            | Description                                                  |
|----------------------|----|----------------|-----------------------------------------------------|
| `--objective-id`     | Yes  | —              | Objective ID                                               |
| `--user-id-type`     | No  | `open_id`      | User ID type: `open_id` \| `union_id` \| `user_id`     |
| `--department-id-type` | No | `open_department_id` | Department ID type: `open_department_id` \| `department_id` |

<a id="返回"></a>
### Return

Returns the `indicator` field, containing the quantitative indicator details of the objective.

Example return value:
When there is progress:
```json 
{
   "ok": true,
   "identity": "user",
   "data": {
      "indicator": {
         "create_time": "1782835200000",    // Creation time
         "current_value": 60,               // Current value
         "current_value_calculate_type": 0, // Current value calculation method: 0 (manual update) | 2 (calculated by KR) | 3 (calculated by decomposition). Only when this is 0 is it allowed to use the patch API to update the current value
         "entity_id": "7000000000000000001",// ID of the Objective/KR to which the indicator is attached
         "entity_type": 2,                  // Whether the indicator is attached to an Objective or a KR: 2 (Objective) | 3 (KR)
         "id": "7000000000000000002",       // ID of the indicator itself
         "indicator_status": 0,             // Indicator status: -1 (undefined) | 0 (normal) | 1 (at risk) | 2 (delayed)
         "owner": {                         // User to whom the indicator belongs
            "owner_type": "user",
            "user_id": "ou_xxx"
         },
         "start_value": 0,                  // Starting value, default 0
         "status_calculate_type": 0,        // Status calculation method
         "target_value": 100,               // Target value, default 100
         "unit": {                          // Indicator unit, defaults to the common percentage
            "unit_type": 0,                 // Unit type: 0 (common) | 1 (custom)
            "unit_value": "PERCENT"         // Unit name
         },
         "update_time": "1782835200000"     // Update time
      }
   }
}
```
Default initial progress:
```json 
{
   "ok": true,
   "identity": "user",
   "data": {
      "indicator": {
         "create_time": "1782835200000",
         "entity_id": "7000000000000000001",
         "entity_type": 2,
         "id": "7000000000000000002",
         "indicator_status": -1,
         "owner": {
            "owner_type": "user",
            "user_id": "ou_xxx"
         },
         "status_calculate_type": 0,
         "update_time": "1782835200000"
      }
   }
}
```

The default initial progress does not carry information such as start_value/current_value/target_value/unit. If the current value is set directly, the percentage is used as the default unit.
Since the default unit is percentage, when a numerical value must be calculated, it can be regarded as 0%, but when reporting the default initial progress to the user, it should be made clear that the corresponding O/KR has not set progress, so as to distinguish it from a true 0%.

---

<a id="二查询关键结果的量化指标"></a>
## II. Query the Quantitative Indicators of a Key Result

<a id="命令-1"></a>
### Command

```bash
lark-cli okr key_result.indicators list --key-result-id "<关键结果ID>" [flags]
```

<a id="常用示例-1"></a>
### Common Examples

```bash
# Get the quantitative indicators of a key result
lark-cli okr key_result.indicators list \
  --key-result-id "7652569715131075780"
```

<a id="参数-1"></a>
### Parameters

| Parameter                   | Required | Default value            | Description                                                  |
|----------------------|----|----------------|-----------------------------------------------------|
| `--key-result-id`    | Yes  | —              | Key result ID                                            |
| `--user-id-type`     | No  | `open_id`      | User ID type: `open_id` \| `union_id` \| `user_id`     |
| `--department-id-type` | No | `open_department_id` | Department ID type: `open_department_id` \| `department_id` |

<a id="返回-1"></a>
### Return

Returns the `indicator` field, containing the quantitative indicator details of the key result.

---

<a id="三更新量化指标"></a>
## III. Update Quantitative Indicators

<a id="命令-2"></a>
### Command

```bash
lark-cli okr indicators patch --indicator-id "<指标ID>" --data '<JSON>'
```

<a id="常用示例-2"></a>
### Common Examples

```bash
# Update the current value of the indicator (manual update method)
lark-cli okr indicators patch \
  --indicator-id "ind-123" \
  --data '{"current_value": 75.5, "current_value_calculate_type": 0}'

# Update the indicator status to "at risk" (requires status_calculate_type=0)
lark-cli okr indicators patch \
  --indicator-id "ind-123" \
  --data '{"indicator_status": 1, "status_calculate_type": 0}'

# Update the target value and unit of the key result indicator
lark-cli okr indicators patch \
  --indicator-id "ind-456" \
  --data '{
    "target_value": 100,
    "unit": {"unit_type": 0, "unit_value": "PERCENT"}
  }'

# Read the request body from a file
lark-cli okr indicators patch \
  --indicator-id "ind-123" \
  --data @indicator_update.json
```

<a id="参数-2"></a>
### Parameters

| Parameter               | Required | Description                                                                 |
|------------------|----|--------------------------------------------------------------------|
| `--indicator-id` | Yes  | Indicator ID (obtained from the list interface)                                             |
| `--data`         | Yes  | JSON request body, containing the fields to update. Supports `@文件路径` to read from a file.                        |
| `--user-id-type` | No  | User ID type                                                           |

<a id="请求体字段"></a>
### Request Body Fields

Select and pass in the fields to update as needed; incremental updates are supported:

| Field                          | Type   | Applicable entity | Description                                                                 |
|-----------------------------|------|------|--------------------------------------------------------------------|
| `current_value`             | number | All   | Current value, range -99999999999 to 99999999999                                  |
| `current_value_calculate_type` | int  | All   | Current value calculation method: 0=manual, 1=based on KR progress (objective), 2=based on the progress of decomposed KRs (KR)              |
| `indicator_status`          | int    | All   | Status: -1=undefined, 0=normal, 1=at risk, 2=delayed. Can only be modified when `status_calculate_type=0`      |
| `status_calculate_type`     | int    | All   | Status calculation method: 0=manual, 1=automatic (progress+time), 2=automatic (highest-risk KR). Objectives support 0/1/2, KRs support 0/1 |
| `start_value`               | number | KR    | Start value. Objectives do not support modification                                                   |
| `target_value`              | number | KR    | Target value. Objectives do not support modification; KRs with inheritance records do not support modification                                  |
| `unit`                      | object | KR    | Unit. Objectives do not support modification; KRs with inheritance records do not support modification                                  |

<a id="单位-unit-格式"></a>
### Unit (`unit`) Format

```json
{
  "unit": {
    "unit_type": 0,              // 0 = common unit, 1 = custom unit
    "unit_value": "PERCENT"      // Common unit enums: PERCENT, NONE, YUAN, DOLLAR; custom unit: maximum 5 characters
  }
}
```

<a id="限制说明"></a>
### Restrictions

- **Objective indicators**: Do not support modifying `start_value`, `target_value`, `unit`
- **Key result indicators**: KRs with inheritance records do not support modifying `target_value`, `unit`
- **Automatically calculated indicators**: When `current_value_calculate_type != 0`, the `current_value` cannot be modified manually
- **Indicators with automatic status**: When `status_calculate_type != 0`, the `indicator_status` cannot be modified manually

---

<a id="完整工作流示例"></a>
## Complete Workflow Example

<a id="场景更新关键结果的指标当前值和状态"></a>
### Scenario: Update the current value and status of a key result's indicator

1. **Query the key result's indicator** (obtain `indicator_id` and the current configuration)
   ```bash
   lark-cli okr key_result.indicators list \
     --key-result-id 7652569715131075780
   ```

2. **Check the indicator configuration** and confirm:
   - `current_value_calculate_type` is 0 (manual update) to be able to modify `current_value`
   - `status_calculate_type` is 0 (manual update) to be able to modify `indicator_status`

3. **Update the indicator**
   ```bash
   lark-cli okr indicators patch \
     --indicator-id "ind-123" \
     --data '{"current_value":65.0,"current_value_calculate_type":0,"indicator_status":1,"status_calculate_type":0}'
   ```

4. **Verify the update result**
   ```bash
   lark-cli okr key_result.indicators list \
     --key-result-id 7652569715131075780
   ```

<a id="场景修改关键结果指标的目标值和单位"></a>
### Scenario: Modify the target value and unit of a key result's indicator

```bash
# 1. Query to obtain indicator_id
lark-cli okr key_result.indicators list --key-result-id 7652569715131075780

# 2. Update the target value and unit
lark-cli okr indicators patch \
  --indicator-id 7652569715131075781 \
  --data '{"target_value":500,"unit":{"unit_type":0,"unit_value":"YUAN"}}'
```

<a id="参考"></a>
## Reference

- [lark-okr](../index.md) -- all OKR commands
- [lark-shared](../../shared/index.md) -- authentication and global parameters
- [okr +indicator-update](lark-okr-indicator-update.md) -- quickly update the indicator's current value (recommended)
