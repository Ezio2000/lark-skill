# Workflow steps JSON SSOT

This document is the single source of truth (SSOT) for Workflow `steps` JSON, defining the complete data structure, applicable to:
- **Query scenarios**: understanding the `steps` structure returned by `+workflow-get`
- **Create/modify scenarios**: constructing the `--json` body for `+workflow-create` / `+workflow-update`
> 💡 **This document is a pure field reference**. For complete examples of **creating/modifying** workflows, please read [Workflow](lark-base-workflow.md).
---
<a id="-快速导航"></a>
## 📖 Quick Navigation

Jump to the corresponding section based on your needs:

| Need | Section |
|------|------|
| Understand the basic Step structure | [WorkflowStep basic structure](#workflowstep-基础结构) |
| Query Trigger types and data fields | [Trigger data](#trigger-data-详细结构) |
| Query Action types and data fields | [Action data](#action-data-详细结构) |
| Query Branch/Loop structures | [Branch data](#branch-data-详细结构) / [System data](#system-data-详细结构) |
| Query common types such as ValueInfo/Condition | [Common types](#公共类型) |

---

<a id="workflowstep-基础结构"></a>
## WorkflowStep basic structure

Every step (Trigger / Action / Branch / System) shares the following fields:

```json
{
  "id": "step_xxx",
  "type": "AddRecordTrigger",
  "title": "监控新订单",
  "next": "step_yyy",
  "data": {}
}
```

| Field | Type | Required | Description |
|------|------|------|------|
| `id` | string | Yes | Unique step ID (user-defined, referenced by `next` and `children.links[].to`) |
| `type` | string | Yes | Step type, see the enumeration below |
| `title` | string | No | Step title |
| `children` | StepChildren | No | Child relationship edges, carrying all branches/loops |
| `next` | string | null | No | Linear successor node ID; `null` indicates the process ends |
| `data` | object | Yes | Detailed step configuration, distinguished by `type`, see the following sections |

> **General principle**: connections are written in `children`, extension identifiers are written in `meta`, input parameters are written in `data`.

---

<a id="stepchildren-与-childlink"></a>
## StepChildren and ChildLink

### StepChildren

```json
{
  "links": [ /* ChildLink[] */ ]
}
```

| Field | Type | Description |
|------|------|------|
| `links` | ChildLink[] | List of child relationship edges; empty array `[]` when there are no child relationships |

### ChildLink

Each relationship edge describes a directed connection from the current node to the target node:

```json
{ "kind": "if_true", "to": "step_4", "label": "branch_1", "desc": "金额大于1000" }
```

| Field | Type | Required | Description |
|------|------|------|------|
| `kind` | string | Yes | Relationship type: `if_true` / `if_false` / `case` / `loop_start` / `slot` |
| `to` | string | Yes | Target node ID |
| `label` | string | No | Optional label (such as `branch_1`, `tool`, `llm`, `memory`) |
| `desc` | string | No | Optional semantic description (such as "sales department", "positive sentiment") |

`kind` usage scenarios:

| kind | Node used | Description |
|------|---------|------|
| `if_true` | IfElseBranch | Jump when the condition is true |
| `if_false` | IfElseBranch | Jump when the condition is false |
| `case` | SwitchBranch / AIClassificationBranch | Multi-way branch, `label` recommends using neutral labels such as `branch_1`, and `desc` writes the semantics |
| `loop_start` | Loop | Loop body entry |
| `slot` | AIAgentAction | Mounts LLM / tool / memory child nodes, `label` is `llm` / `tool` / `memory` |

---

<a id="steptype-枚举"></a>
## StepType enumeration

<a id="trigger-类型"></a>
### Trigger types

| type | Description |
|------|------|
| `AddRecordTrigger` | Triggered when a record is added |
| `SetRecordTrigger` | Triggered when a record is modified |
| `ChangeRecordTrigger` | Triggered when a record meets the condition |
| `TimerTrigger` | Scheduled trigger |
| `ReminderTrigger` | Date reminder trigger |
| `ButtonTrigger` | Button click trigger |
| `LarkMessageTrigger` | Triggered by receiving a Feishu message |

> All Trigger nodes **must not set** `children`; connect successors via `next`.

<a id="触发器选型指南"></a>
### Trigger selection guide

| Requirement description | Trigger |
|---------|--------|
| When a record is added | `AddRecordTrigger` |
| When a specified field is modified (modification only, can restrict the value after modification) | `SetRecordTrigger` |
| When a record is added or modified and meets the configured filter conditions | `ChangeRecordTrigger` |

> ⚠️ `SetRecordTrigger` only listens for modifications, while `ChangeRecordTrigger` listens for both additions + modifications.

<a id="action-类型"></a>
### Action types

| type | Description |
|------|------|
| `AddRecordAction` | Add record |
| `SetRecordAction` | Update record |
| `FindRecordAction` | Find record |
| `HTTPClientAction` | HTTP request |
| `Delay` | Delay |
| `LarkMessageAction` | Send Feishu message |
| `GenerateAiTextAction` | AI-generated text |
| `AIAnalysisAction` | AI analysis |

> All Action nodes **must not set** `children`; connect successors via `next`.

<a id="branch-类型"></a>
### Branch types

| type | Description |
|------|------|
| `IfElseBranch` | Conditional branch, `children.links` contains `if_true` and `if_false` |
| `SwitchBranch` | Multi-way branch, `children.links` contains multiple `case` |
| `AIClassificationBranch` | AI classification branch, `children.links` contains multiple `case` |

<a id="system-类型"></a>
### System types

| type | Description |
|------|------|
| `Loop` | Loop, `children.links` contains `loop_start` pointing to the loop body entry |

---

<a id="trigger-data-详细结构"></a>
## Trigger data detailed structure


### AddRecordTrigger

```json
{
  "table_name": "订单表",
  "watched_field_name": "状态",
  "trigger_control_list": ["pasteUpdate", "automationBatchUpdate"],
  "condition_list": [] /* AndCondition 数组 */
}
```

| Field | Required | Description |
|------|------|------|
| `table_name` | Yes | Name of the monitored data table |
| `watched_field_name` | Yes | Name of the monitored field |
| `trigger_control_list` | No | Trigger control, optional values: `pasteUpdate` / `automationBatchUpdate` / `syncUpdate` / `appendImport` / `openAPIBatchUpdate` |
| `condition_list` | No | Each element in the array represents a condition group; condition groups are ORed, and conditions within a group must be ANDed |

### ChangeRecordTrigger

```json
{
  "table_name": "任务表",
  "trigger_control_list": [],
  "condition_list": [
    {
      "conjunction": "and",
      "conditions": [
        {
          "field_name": "预计工时",
          "operator": "isGreater",
          "value": [{ "value_type": "number", "value": 0 }]
        }
      ]
    }
  ]
}
```

| Field | Required | Description                                                                              |
|------|------|---------------------------------------------------------------------------------|
| `table_name` | Yes | Name of the monitored data table                                                                         |
| `trigger_control_list` | No | Trigger control, optional values: `pasteUpdate` / `automationBatchUpdate` / `syncUpdate` / `appendImport` |
| `condition_list` | Yes | Cannot be empty; each element in the array represents a condition group; condition groups are ORed, and conditions within a group must be ANDed                          |

### SetRecordTrigger

```json
{
  "table_name": "订单表",
  "record_watch_conjunction": "and",
  "record_watch_info": [ /* FieldCondition[] */ ],
  "field_watch_info": [
    { "field_name": "状态", "operator": "is", "value": [{ "value_type": "text", "value": "已发货" }] }
  ],
  "trigger_control_list": [],
  "condition_list": null
}
```

| Field | Required | Description |
|------|----|------|
| `table_name` | Yes  | Name of the monitored data table |
| `record_watch_conjunction` | No  | Record filter combination method: `and` / `or`, default `and` |
| `record_watch_info` | No  | Record-level filter conditions (matching the value before modification); if empty, all records are monitored |
| `field_watch_info` | Yes  | List of field-level monitoring conditions, at least one |
| `trigger_control_list` | No  | Trigger control, optional values: `pasteUpdate` / `automationBatchUpdate` / `syncUpdate` / `appendImport` |
| `condition_list` | No  | Each element in the array represents a condition group; condition groups are ORed, and conditions within a group must be ANDed |

`FieldWatchItem`:

| Field | Type | Description |
|------|------|------|
| `field_name` | string | Name of the monitored field |
| `operator` | string | Operator (filled in only when it is explicitly required that the field meets the condition) |
| `value` | ValueInfo[] | Trigger value |

### TimerTrigger

```json
{
  "rule": "WEEKLY",
  "start_time": "2025-01-01 09:00",
  "sub_unit": [1, 3, 5],
  "is_never_end": true
}
```

| Field | Required | Description |
|------|------|------|
| `rule` | Yes | `NO_REPEAT` / `DAILY` / `WEEKLY` / `MONTHLY` / `YEARLY` / `WORKDAY` / `CUSTOM` |
| `start_time` | No | Start time, format `yyyy-MM-dd HH:mm` |
| `interval` | No | Custom interval [1,30] (CUSTOM only) |
| `unit` | No | Custom unit: `SECOND` / `MINUTE` / `HOUR` / `DAY` / `WEEK` / `MONTH` / `YEAR` |
| `sub_unit` | No | Sub-unit (when `WEEKLY`, an array of days of the week 0-6; when `MONTHLY`, an array of days of the month 1-31) |
| `end_time` | No | End time |
| `is_never_end` | No | Whether it never ends |

### ReminderTrigger

```json
{
  "table_name": "项目表",
  "field_name": "截止日期",
  "offset": -1,
  "unit": "DAY",
  "hour": 9,
  "minute": 0,
  "condition_list": null
}
```

| Field | Required | Description |
|------|------|------|
| `table_name` | Yes | Data table name |
| `field_name` | Yes | Date field name (must be of type `datetime` / `created_at` / `formula` / `lookup`) |
| `unit` | Yes | Offset unit: `MINUTE` / `HOUR` / `DAY` / `WEEK` / `MONTH` |
| `offset` | Yes | Offset amount for advancing/delaying (trigger time = date field time + `offset` × `unit`, so a negative number = advance, a positive number = delay; the range is determined by `unit`): `MINUTE` ∈ {0, 5, 15, 30, -5, -15, -30}; `HOUR` ∈ [-6, -1] ∪ [1, 6]; `DAY` ∈ [-7, 7]; `WEEK` ∈ [-7, -1] ∪ [1, 7]; `MONTH` ∈ [-7, -1] ∪ [1, 7] |
| `hour` | Yes | Trigger hour (0-23), default 9 |
| `minute` | Yes | Trigger minute (0-59), default 0 |
| `condition_list` | No | Each element in the array represents a condition group; condition groups are ORed, and conditions within a group must be ANDed  |


### ButtonTrigger

```json
{
  "button_type": "buttonField",
  "table_name": "审批表"
}
```

| Field | Required | Description |
|------|------|------|
| `button_type` | Yes | Button type: `buttonField` (a button in a table, can operate on the current record data) / `buttonElement` (a button on a dashboard or application page, can perform overall operations) |
| `table_name` | No | Name of the bound data table, filled in only for `button_type=buttonField` |

> `buttonField` and `buttonElement` have different output capabilities; see the "ButtonTrigger (button trigger)" output description below for details.


### LarkMessageTrigger

```json
{
  "receive_scene": "group",
  "receiver": [{ "value_type": "group", "value": {"id": "oc_xxxx", "name": "测试群"} }],
  "scope": "all",
  "filter": {
    "conjunction": "and",
    "content_contains": ["关键词"],
    "sender_contains": [{ "value_type": "user", "value": {"id": "ou_xxxx", "name": ""} }],
    "is_new_message": true,
    "is_message_contain_attachment": false
  }
}
```

| Field | Required | Description|
|------|------|---|
| `receive_scene` | Yes | Receiving scenario: `group` (group chat) / `chat` (direct chat)|
| `receiver` | Yes | Trigger source, supports `user` / `group` / `ref`. In the direct chat scenario, this field refers to "users who can chat directly with the bot"; in the group chat scenario, this field refers to "groups that receive messages"|
| `scope` | Yes | Trigger scope: `at` (@mention) / `all` (all messages). This parameter is valid only in the group chat scenario; do not specify this parameter in the direct chat scenario|
| `filter` | Yes | MessageFilter message filter conditions|

`MessageFilter`:

| Field | Type | Description |
|------|------|----|
| `conjunction` | string | `and` meets all conditions / `or` any condition|
| `content_contains` | string[] | Keyword list|
| `sender_contains` | ValueInfo[] | Filter the sender (effective only for group chat + group source; do not specify this parameter in the direct chat scenario) |
| `is_new_message` | boolean | Only new topic messages (effective only for group chat; do not specify this parameter in the direct chat scenario) |
| `is_message_contain_attachment` | boolean | Whether only attachment messages trigger |

<a id="action-data-详细结构"></a>
## Action data detailed structure

### AddRecordAction

```json
{
  "table_name": "订单表",
  "field_values": [
    { "field_name": "客户名称", "value": [{ "value_type": "text", "value": "张三" }] },
    { "field_name": "金额", "value": [{ "value_type": "number", "value": 100 }] },
    { "field_name": "创建人", "value": [{ "value_type": "ref", "value": "$.trigger_1.fieldIdxxx" }] }
  ]
}
```

| Field | Required | Description |
|------|------|------|
| `table_name` | Yes | Target data table name |
| `field_values` | Yes | RecordFieldValue[] |

### SetRecordAction

```json
{
  "table_name": "订单表",
  "max_set_record_num": 10,
  "field_values": [
    { "field_name": "状态", "value": [{ "value_type": "option", "value": { "id": "opt1", "name": "已完成" } }] }
  ],
  "filter_info": { /* RecordFilterInfo */ },
  "ref_info": { "step_id": "step_trigger" }
}
```

| Field | Required | Description |
|------|------|------|
| `table_name` | Yes | Target data table name |
| `max_set_record_num` | No | Maximum number of records to update, default 100, range 1-15000 |
| `field_values` | Yes | RecordFieldValue[] |
| `filter_info` | No* | RecordFilterInfo filter conditions (mutually exclusive with `ref_info`) |
| `ref_info` | No* | RefInfo references the records of a preceding step (mutually exclusive with `filter_info`) |

### FindRecordAction

```json
{
  "table_name": "客户表",
  "field_names": ["客户名称", "联系方式", "等级"],
  "should_proceed_when_no_results": true,
  "filter_info": { /* RecordFilterInfo */ }
}
```

| Field | Required | Description |
|------|------|------|
| `table_name` | Yes | Target data table name |
| `field_names` | Yes | List of field names to retrieve, at least one |
| `should_proceed_when_no_results` | No | Whether to continue subsequent steps when there are no results, default `true` |
| `filter_info` | No* | RecordFilterInfo (mutually exclusive with `ref_info`) |
| `ref_info` | No* | RefInfo (mutually exclusive with `filter_info`) |

### HTTPClientAction

```json
{
  "method": "POST",
  "url": [{ "value_type": "text", "value": "https://api.example.com/webhook" }],
  "queries": [
    { "key": "source", "value": [{ "value_type": "text", "value": "workflow" }] }
  ],
  "headers": [
    { "key": "Content-Type", "value": [{ "value_type": "text", "value": "application/json" }] }
  ],
  "body_type": "raw",
  "raw_body": [
    { "value_type": "text", "value": "{\"record_id\":\"" },
    { "value_type": "ref", "value": "$.step_1.recordId" },
    { "value_type": "text", "value": "\"}" }
  ],
  "response_type": "json",
  "response_value": "{\"success\":true,\"message\":\"data fetched successfully\"}"
}
```

| Field | Required | Description |
|------|-----|------|
| `method` | No | Request method: `GET` / `POST` / `PUT` / `PATCH` / `DELETE`, default `POST` |
| `url` | Yes | ValueInfo[], request URL, supports concatenation of `text` / `ref` |
| `queries` | No | KeyValue[], query parameters |
| `headers` | No | KeyValue[], request headers |
| `body_type` | No | Request body type: `none` / `raw` / `form-data` / `form-urlencoded`, default `raw` |
| `raw_body` | No | ValueInfo[], raw request body, used only for `body_type=raw` |
| `form_body` | No | KeyValue[], form data, used only for `body_type=form-data` or `body_type=form-urlencoded` |
| `response_type` | No | Response type: `none` / `text` / `json`, default `json` |
| `response_value` | No | string, an example of the response result in JSON string form; required only when `response_type=json` |

`KeyValue`:

| Field | Type | Description |
|------|------|------|
| `key` | string | Parameter name / request header name |
| `value` | ValueInfo[] | Parameter value / request header value, supports `text` / `ref` |

### Delay

```json
{ "duration": 30 }
```

| Field | Required | Description |
|------|------|------|
| `duration` | Yes | Delay duration (minutes), range [1, 120] |

### LarkMessageAction

```json
{
  "receiver": [{ "value_type": "user", "value": {"id": "ou_xxxx"} }],
  "send_to_everyone": false,
  "title": [{ "value_type": "text", "value": "新订单通知" }],
  "content": [
    { "value_type": "text", "value": "客户 " },
    { "value_type": "ref", "value": "$.trigger_1.fldCustomerName" },
    { "value_type": "text", "value": " 创建了新订单" }
  ],
  "btn_list": [
    { "text": "查看详情", "btn_action": "openLink", "link": [{ "value_type": "text", "value": "https://example.com" }] }
  ]
}
```

| Field | Required | Description |
|------|------|------|
| `receiver` | Yes | ValueInfo[] |
| `send_to_everyone` | Yes | Whether to send to everyone |
| `title` | No | TextRefItem[] message title |
| `content` | Yes | TextRefItem[] message content |
| `btn_list` | Yes | Button list; empty array when not needed |

`ButtonConfig`:

| Field | Type | Description |
|------|------|------|
| `text` | string | Button text |
| `btn_action` | string | `addRecord` / `setRecord` / `openLink` |
| `link` | ValueInfo[] | Jump link (used when `openLink`) |
| `table_name` | string | Operation table name (used when `addRecord`) |
| `record_values` | RecordFieldValue[] | Record assignment (used when `addRecord` / `setRecord`) |

### GenerateAiTextAction

```json
{
  "prompt": [
    { "value_type": "text", "value": "请总结以下内容：" },
    { "value_type": "ref", "value": "$.step_1.fieldxxx" }
  ]
}
```

| Field | Required | Description |
|------|------|------|
| `prompt` | Yes | TextRefItem[] prompt, supports `text` / `ref` |

### AIAnalysisAction

```json
{
  "analysis_task": [
    { "value_type": "text", "value": "分析昨日订单趋势、异常原因，并给出行动建议" }
  ],
  "analysis_table_names": ["订单表", "退款表"],
  "identity_type": "maker",
  "output_instruction": "先给结论，再列证据与行动建议"
}
```

| Field | Required | Description |
|------|------|------|
| `analysis_task` | Yes | TextRefItem[] analysis task, supports mixed `text` / `ref`; must contain at least one valid item |
| `analysis_table_names` | No | string[] analysis data scope; when it is an empty array `[]` or omitted, it means all data tables of the current Base |
| `identity_type` | Yes | Data access identity: `maker` (fixed workflow identity) / `triggerPersonal` (workflow trigger) |
| `output_instruction` | No | Only plain text is supported |


<a id="branch-data-详细结构"></a>
## Branch data detailed structure

### IfElseBranch

`children.links` contains two edges, `if_true` and `if_false`; `next` points to the successor node after the two branches merge.

**If a complex multi-branch scenario is involved (when the number of branches >= 3), you should use SwitchBranch instead of nested IfElseBranch**

```json
{
  "condition": {
    "conjunction": "or",
    "conditions": [
      {
        "conjunction": "and",
        "conditions": [
          {
            "left_value": { "value_type": "ref", "value": "$.step_1.fieldxxx" },
            "operator": "isGreater",
            "right_value": [{ "value_type": "number", "value": 1000 }]
          }
        ]
      }
    ]
  }
}
```

| Field | Required | Description |
|------|------|------|
| `condition` | Yes | OrGroup condition, with the structure `(A and B) or (C and D)` |

### SwitchBranch

`children.links` contains multiple `case` edges (for `label`, it is recommended to use `branch_1`, `branch_2`; write the semantics in `desc`).

```json
{
  "mode": "exclusive",
  "no_match_action": "classifyToOther",
  "child_branch_list": [
    {
      "name": "高优先级",
      "condition": {
        "conjunction": "or",
        "conditions": [
          {
            "conjunction": "and",
            "conditions": [
              {
                "left_value": { "value_type": "ref", "value": "$.step_1.fieldxxx" },
                "operator": "is",
                "right_value": [{ "value_type": "text", "value": "P0" }]
              }
            ]
          }
        ]
      }
    }
  ]
}
```

| Field | Required | Description |
|------|------|------|
| `mode` | No | Branch mode. `exclusive`: exclusive mode, executes only one sub-branch that meets the conditions; `parallel`: parallel mode, executes all sub-branches that meet the conditions. Default `exclusive` |
| `no_match_action` | No | Used when `mode=exclusive`, handling strategy when there is no match. `classifyToOther`: classify into another branch; `fail`: error and terminate. Default `classifyToOther` |
| `fail_mode` | No | Used when `mode=parallel`, strategy when some branches error. `partialSuccess`: continue on partial success; `fail`: terminate on any failure. Default `partialSuccess` |
| `match_mode` | No | Used when `mode=parallel`, strategy when no branch meets the conditions. `noneMatchSkip`: skip and continue; `noneMatchFail`: error and terminate. Default `noneMatchSkip` |
| `child_branch_list` | Yes | BranchItem[], 1-10 conditional branches |

`BranchItem`:

| Field | Type | Description |
|------|------|------|
| `name` | string | Branch name |
| `condition` | OrGroup | Branch condition |

### AIClassificationBranch

`AIClassificationBranch` uses AI to classify the content of `content`, then enters the matched subsequent step through the `case` edge in `children.links`. `steps[].data` uses the public Agent Data protocol.

```json
{
  "classes": [
    {
      "name": "Bug",
      "desc": "功能报错、异常、不可用或结果错误"
    },
    {
      "name": "功能建议",
      "desc": "希望新增能力或优化现有功能"
    }
  ],
  "content": [
    { "value_type": "text", "value": "请根据反馈内容判断类型：" },
    { "value_type": "ref", "value": "$.step_trigger.fldFeedback" }
  ],
  "classification_rule": "信息不足时判定为无法匹配。"
}
```

| Field | Required | Description                                                                   |
|------|------|----------------------------------------------------------------------|
| `classes` | Yes | Classification list, at least 2 items. Each item contains `name` and `desc`                                     |
| `classes[].name` | Yes | Classification name, must remain consistent with the corresponding regular `children.links[].desc`                             |
| `classes[].desc` | Yes | Classification description; may be an empty string, but the field must exist                                                  |
| `content` | Yes | TextRefItem[], the content used for classification, supports `text` / `ref`                              |
| `classification_rule` | No | Global classification rule plain text                                                            |
| `no_match_action` | No | No-match strategy. `classifyToOther`: enter the default branch; `fail`: the current node fails. When omitted, `classifyToOther` is used |

`children.links` rules:
- Which subsequent step to jump to after each classification is matched must be written in children.links.
- Regular classification edges use stable labels such as `kind: "case"` and `label: "branch_1"`, `branch_2`; `desc` must remain consistent with `classes[i].name`; `to` points to the entry step of that classification.
- When `no_match_action: "classifyToOther"`, an additional default branch edge must be provided: `{ "kind": "case", "label": "default", "desc": "默认分支", "to": "step_other_action" }`.
- When `no_match_action: "fail"`, do not provide a default branch edge.


<a id="system-data-详细结构"></a>
## System data detailed structure

### Loop

`children.links` contains the `loop_start` edge pointing to the loop body entry, and `next` points to the successor node after the loop ends.

```json
{
  "loop_mode": "continue",
  "max_loop_times": 100,
  "data": [{ "value_type": "ref", "value": "$.find_record_stepIdxxx.fieldRecords" }]
}
```

| Field | Required | Description |
|------|------|------|
| `data` | Yes | ValueInfo[] (only supports the `ref` type), loop data source, only one can be filled in |
| `loop_mode` | No | Whether to continue on a single error: `end` (terminate) / `continue` (continue) |
| `max_loop_times` | No | Maximum number of loop iterations |

---


<a id="公共类型"></a>
## Common types

### ValueInfo

The base type of all values, distinguished by `value_type`:

| value_type | value type | Description | Example |
|------------|-----------|------|------|
| `text` | string | Text | `"张三"` |
| `number` | number | Number | `100` |
| `boolean` | boolean | Boolean | `true` |
| `date` | string | Date, can be a specific time string or a relative time value | `"2025/01/01"`, `"2025/01/01 11:00"`, `"now"`, `"now 11:00"`, `"today"`, `"today 11:00"`, `"yesterday"`, `"yesterday 11:00"`, `"lastWeek"`, `"currentMonth"`, `"lastMonth"`, `"theLastWeek"`, `"theNextWeek"`, `"theLastMonth"`, `"theNextMonth"` |
| `option` | `{ id, name }` | Option | `{ "id": "opt1", "name": "已完成" }` |
| `link` | `{ text, link }` | Link (including text and URL); the format of the text and URL can be the text/ref type in ValueInfo | `{ "text": [{ "value_type": "text", "value": "查看详情" }], "link": [{ "value_type": "text", "value": "https://example.com" }] }`, `{ "text": [{ "value_type": "text", "value": "查看详情" }], "link": [{ "value_type": "ref", "value": "$.step_1.fldXXX" }] }` |
| `user` | `{ id, name }` | User OpenID, name | `{ "id": "ou_xxxx", "name": "张三" }` |
| `group` | `{ id, name }` | Group Chat ID, name | `{ "id": "oc_xxx", "name": "测试群" }` |
| `ref` | `string` | Path referencing the output of a preceding node | See the "ref reference variable details" section |

> ⚠️ **The id in all user-related values uniformly uses OpenID (`ou_xxxx` format)**, and the conversion is completed by the CLI layer
> ⚠️ **The id in all group-related values uniformly uses ChatID (`oc_xxxx` format)**, and the conversion is completed by the CLI layer

<a id="ref-引用变量详解"></a>
### ref reference variable details

The `ref` type is the core mechanism for data transfer between nodes in a workflow. When `value_type` is `ref`, `value` points to an output variable of a preceding node. This section describes in detail the output variable definitions available for reference from each node.

<a id="引用路径格式"></a>
#### Reference path format

```
$.{stepId}
$.{stepId}.{pathId}
$.{stepId}.{pathId}.{childPathId}
$.{stepId}.{pathId}.{childPathId}.{grandChildPathId}
```

- `{stepId}`: the `id` of the preceding node (that is, the `id` field in WorkflowStep)
- `{pathId}`: the path identifier of the node output
- Supports multi-level drill-down, such as referencing a field attribute: `$.step_1.fldXXX.name`

---

<a id="触发器节点输出"></a>
#### Trigger node output

<a id="记录触发器addrecordtrigger--changerecordtrigger--setrecordtrigger--remindertrigger"></a>
##### Record triggers (AddRecordTrigger / ChangeRecordTrigger / SetRecordTrigger / ReminderTrigger)

The output structures of these 4 triggers are completely identical:

| pathId | Description | Reference example |
|--------|------|----------|
| `{fieldId}` | Field id, generated from all fields of the configured table or the specified field id; field attributes can be drilled down | `$.{stepId}.{fieldId}` |
| `{fieldId}.fieldId` | Field id attribute | `$.{stepId}.{fieldId}.fieldId` |
| `{fieldId}.fieldName` | Field name attribute | `$.{stepId}.{fieldId}.fieldName` |
| `startTime` | Trigger timestamp | `$.{stepId}.startTime` |
| `recordId` | Record ID | `$.{stepId}.recordId` |
| `recordLink` | Record link | `$.{stepId}.recordLink` |
| `recordCreatedUser` | Record creator | `$.{stepId}.recordCreatedUser` |
| `recordCreatedTime` | Record creation time | `$.{stepId}.recordCreatedTime` |
| `recordModifiedUser` | Last modifier | `$.{stepId}.recordModifiedUser` |
| `recordModifiedTime` | Last modification time | `$.{stepId}.recordModifiedTime` |

**Dynamic field output rules**:

- Read all fields of the data table configured for the trigger
- Each field generates one output: `pathId` = fieldId
- If the field is a linked field, children are all fields of the linked table (single-level drill-down, no further recursion)
- Each field can drill down to specific field attributes (see "Field attribute drill-down")

**children of recordLink**: if a data table is configured, it is the list of all views of that table, with each view `{ pathId: viewId, pathName: viewName, pathType: 'string' }`. Reference example: `$.{stepId}.recordLink.{viewId}`.

<a id="buttontrigger按钮触发器"></a>
##### ButtonTrigger (button trigger)

The output of `ButtonTrigger` depends on `button_type`:

#### `button_type = buttonField`

| pathId | Description | Reference example |
|--------|------|----------|
| `{fieldId}` | Field id, generated from all fields of the configured table or the specified field id; field attributes can be drilled down | `$.{stepId}.{fieldId}` |
| `{fieldId}.fieldId` | Field id attribute | `$.{stepId}.{fieldId}.fieldId` |
| `{fieldId}.fieldName` | Field name attribute | `$.{stepId}.{fieldId}.fieldName` |
| `recordId` | Record ID | `$.{stepId}.recordId` |
| `recordLink` | Record link | `$.{stepId}.recordLink` |
| `recordCreatedUser` | Record creator | `$.{stepId}.recordCreatedUser` |
| `recordModifiedUser` | Last modifier | `$.{stepId}.recordModifiedUser` |
| `recordModifiedTime` | Last modification time | `$.{stepId}.recordModifiedTime` |
| `time` | Trigger time | `$.{stepId}.time` |
| `user` | Trigger user | `$.{stepId}.user` |
| `buttonName` | Name of the triggered button | `$.{stepId}.buttonName` |

#### `button_type = buttonElement`

| pathId | Description | Reference example |
|--------|------|----------|
| `time` | Trigger time | `$.{stepId}.time` |
| `user` | Trigger user | `$.{stepId}.user` |
| `buttonName` | Name of the triggered button | `$.{stepId}.buttonName` |

<a id="timertrigger定时触发器"></a>
##### TimerTrigger (timer trigger)

| pathId | Description | Reference example |
|--------|------|----------|
| `scheduleTime` | Scheduled trigger time | `$.{stepId}.scheduleTime` |

<a id="larkmessagetrigger飞书消息触发器"></a>
##### LarkMessageTrigger (Feishu message trigger)

| pathId | Description | Reference example |
|--------|------|----------|
| `Sender` | Message sender | `$.{stepId}.Sender` |
| `AtUser` | User mentioned with @ in the message | `$.{stepId}.AtUser` |
| `SenderGroup` | Group where the message is located (group chat scenario only) | `$.{stepId}.SenderGroup` |
| `MessageSendTime` | Message sending time | `$.{stepId}.MessageSendTime` |
| `MessageContent` | Message body | `$.{stepId}.MessageContent` |
| `MessageType` | Message type identifier | `$.{stepId}.MessageType` |
| `MessageID` | Message unique identifier | `$.{stepId}.MessageID` |
| `MessageLink` | Message link (group chat scenario only) | `$.{stepId}.MessageLink` |
| `ParentID` | ID of the replied-to message | `$.{stepId}.ParentID` |
| `ThreadID` | ID of the topic message it belongs to | `$.{stepId}.ThreadID` |
| `Attachments` | Attachments in the message | `$.{stepId}.Attachments` |

Condition restrictions:

- If the scenario is a direct chat (`receive_scene = "Chat"`), then `SenderGroup` and `MessageLink` are unavailable

---

<a id="操作节点输出"></a>
#### Action node output

<a id="findrecordaction查找记录"></a>
##### FindRecordAction (find records)

| pathId | Description | Reference example|
|--------|------|-------|
| `fieldRecords` | References to all found records (can be used for Loop iteration) | `$.{stepId}.fieldRecords`|
| `firstfieldsRecord` | First matching record | `$.{stepId}.firstfieldsRecord`|
| `firstfieldsRecord.{fieldId}` | Field value of the first record; field attributes can be drilled down | `$.{stepId}.firstfieldsRecord.{fieldId}`|
| `firstfieldsRecord.recordId` | Record ID array | `$.{stepId}.firstfieldsRecord.recordId`|
| `fields` | Value of a certain column for all found records | Reference not supported|
| `fields.{fieldId}` | Fields selected by the user | `$.{stepId}.fields.{fieldId}`|
| `fields.{fieldId}.fieldId` | Array of field ids selected by the user | `$.{stepId}.fields.{fieldId}.fieldId`|
| `fields.{fieldId}.fieldName` | Array of field names selected by the user | `$.{stepId}.fields.{fieldId}.fieldName`|
| `fields.recordId` | Record ID array | `$.{stepId}.fields.recordId`|
| `recordNum` | Total number of found records | `$.{stepId}.recordNum`|

<a id="addrecordaction新增记录"></a>
##### AddRecordAction (Add Record)

| pathId | Description | Reference Example |
|--------|------|----------|
| `{fieldId}` | User-configured field values; field properties can be drilled down | `$.{stepId}.{fieldId}` |
| `{fieldId}.fieldId` | User-configured field ID | `$.{stepId}.{fieldId}.fieldId` |
| `{fieldId}.fieldName` | User-configured field name | `$.{stepId}.{fieldId}.fieldName` |
| `recordId` | ID of the newly added record | `$.{stepId}.recordId` |
| `recordLink` | URL of the newly added record | `$.{stepId}.recordLink` |

<a id="setrecordaction更新记录"></a>
##### SetRecordAction (Update Record)

| pathId | Description | Reference Example |
|--------|------|----------|
| `{fieldId}` | User-configured field values; field properties can be drilled down | `$.{stepId}.{fieldId}` |
| `{fieldId}.fieldId` | User-configured field ID | `$.{stepId}.{fieldId}.fieldId` |
| `{fieldId}.fieldName` | User-configured field name | `$.{stepId}.{fieldId}.fieldName` |
| `recordId` | Array of record IDs (since multiple records may be updated) | `$.{stepId}.recordId` |

<a id="httpclientactionhttp-请求"></a>
##### HTTPClientAction (HTTP Request)

The output of HTTPClientAction depends on `response_type`:

| response_type | Referenceable | Output Description | Reference Example |
|--------------|-----------|----------|----------|
| `none` | No | No referenceable output | Reference not supported |
| `text` | Yes | The entire response text is output as a whole node | `$.{stepId}` |
| `json` | Yes | The response body is attached as a whole under `body`, and `status_code` is also returned; only fields declared in `response_value` can be referenced | `$.{stepId}.body`, `$.{stepId}.body.success`, `$.{stepId}.body.message`, `$.{stepId}.status_code` |

**Additional Notes**:

- When `response_type = none`, subsequent nodes cannot reference any output of HTTPClientAction
- When `response_type = text`, `$.{stepId}` represents the entire response text
- When `response_type = json`, `$.{stepId}.body` represents the entire JSON body, and `$.{stepId}.body.字段名` represents a field within the body
- Only when `response_type = json`, `$.{stepId}.status_code` represents the HTTP status code returned after requesting that HTTP URL
- Only when `response_type = json`, `response_value` is required
- When `response_type = json`, subsequent nodes can only reference fields declared in `response_value`

**Example**:

Assume the configuration of a certain `HTTPClientAction` is as follows:

```json
{
  "id": "step_http_1",
  "type": "HTTPClientAction",
  "data": {
    "response_type": "json",
    "response_value": "{\"success\":true,\"message\":\"ok\"}"
  }
}
```

Then subsequent nodes can only reference:

- `$.step_http_1.body`
- `$.step_http_1.body.success`
- `$.step_http_1.body.message`
- `$.step_http_1.status_code`

But **cannot** reference fields not declared in `response_value`, for example:

- `$.step_http_1.body.data`
- `$.step_http_1.body.request_id`

<a id="generateaitextactionai-生成文本"></a>
##### GenerateAiTextAction (AI Generate Text)

| pathId | Description | Reference Example |
|--------|------|----------|
| (whole output) | AI-generated text content (drill-down not supported; only `$.{stepId}` can be referenced) | `$.{stepId}` |

<a id="aianalysisactionai-分析"></a>
##### AIAnalysisAction (AI Analysis)

| pathId | Description | Reference Example |
|--------|------|----------|
| `analysisResult` | AI analysis result string | `$.{stepId}.analysisResult` |

<a id="无输出的操作节点"></a>
##### Action Nodes with No Output

The following nodes do not produce any referenceable output data:

- **Delay** (delay wait)
- **LarkMessageAction** (send Lark message)

---

<a id="分支节点输出"></a>
#### Branch Node Output

The following branch nodes do not produce any referenceable output data:

- **IfElseBranch** (conditional branch)
- **SwitchBranch** (multi-condition branch)

---

<a id="系统节点输出"></a>
#### System Node Output

<a id="loop循环"></a>
##### Loop

| pathId | Description | Reference Example |
|--------|------|----------|
| `item` | Current loop element | `$.{stepId}.item` |
| `index` | Loop index starting from 0 | `$.{stepId}.index` |

**Type inference rules for `item`** (determined by the loop data source):

**Scenario 1: Iterating over combined records** — When the data source is of type `record` (such as `fieldRecords` of FindRecordAction), the type of `item` is `record`, and specific fields can be selected by drilling down:

| Description | Reference Example |
|------|----------|
| The record currently being iterated (record) | `$.{loopStepId}.item` |
| A specific field of the record | `$.{loopStepId}.item.{fieldId}` |
| Index starting from 0 (number) | `$.{loopStepId}.index` |

**Scenario 2: Iterating over fields** — When the data source is a multi-value type field, such as an attachment field or a person field, `item` inherits the type of that field and can continue to drill down into field properties:

| Description | Reference Example |
|------|----------|
| The element currently being iterated (type inherits from the data source field type, e.g., person field) | `$.{loopStepId}.item` |
| User name | `$.{loopStepId}.item.name` |
| Index starting from 0 (number) | `$.{loopStepId}.index` |

---

<a id="字段属性下钻"></a>
#### Field Property Drill-Down

Each field variable can be further drilled down to select field properties. All fields support at least the two basic properties `fieldId` and `fieldName`, and some fields also support additional properties:

| Field Type | Property Name | Property pathId | Property pathType | Description |
|----------|---------|-------------|--------------|------|
| **All fields (basic)** | Field ID | `fieldId` | `string` | Unique identifier of the field |
| | Field name | `fieldName` | `string` | Display name of the field |
| **Person field** (`user` / `created_by` / `updated_by`) | Name | `name` | `string` | User name |
| **Date field** (`datetime` / `created_at` / `updated_at`) | Timestamp | `timestamp` | `number` | Timestamp value |
| **Attachment field** (`attachment`) | File name | `fileName` | `string` | Attachment file name |
| | File type | `fileType` | `string` | MIME type |
| | File size | `size` | `number` | File size in bytes |
| | File Token | `fileToken` | `string` | Attachment token |
| **Hyperlink text field** (`text` and `style.type=url`) | Text | `text` | `string` | Link text portion |
| | Link | `link` | `string` | Link URL portion |
| **Auto-number field** (`auto_number`) | Sequence number | `sequence` | `number` | Pure numeric sequence of the number |
| **Link field** (`link`) | Field drill-down | `{fieldId}` | - | Can drill down to fields of the linked table |

> Other field types (such as `text`, `number`, `checkbox`, `select`, `location`, `formula`, `lookup`, etc.) only support the two basic properties `fieldId` and `fieldName`.

Drill-down reference example:

```
$.{stepId}.{fieldId} → field value itself
$.{stepId}.{fieldId}.fieldId → field ID (string)
$.{stepId}.{fieldId}.fieldName    → field name (string)
$.{stepId}.{fieldId}.name → list of person names (array<string>, person fields only)
$.{stepId}.{fieldId}.unionId → list of person unionIds (array<string>, person fields only)
$.{stepId}.{fieldId}.timestamp    → timestamps (array<number>, date fields only)
$.{stepId}.{fieldId}.fileName     → list of file names (array<string>, attachment fields only)
$.{stepId}.{fieldId}.fileToken    → list of file tokens (array<string>, attachment fields only)
```

---

<a id="节点输出能力总览"></a>
#### Node Output Capability Overview

| Node | Type | Has Output | Output Characteristics |
|------|------|--------|---------|
| AddRecordTrigger | Trigger | ✅ | Dynamic (table fields + record properties) |
| ChangeRecordTrigger | Trigger | ✅ | Dynamic (table fields + record properties) |
| SetRecordTrigger | Trigger | ✅ | Dynamic (table fields + record properties) |
| ReminderTrigger | Trigger | ✅ | Dynamic (table fields + record properties) |
| ButtonTrigger | Trigger | ✅ | Dynamic (table fields + record properties; buttonElement only has basic trigger properties) |
| TimerTrigger | Trigger | ✅ | Static (only scheduleTime) |
| LarkMessageTrigger | Trigger | ✅ | Static (message property list) |
| FindRecordAction | Action | ✅ | Dynamic (user-selected fields) |
| AddRecordAction | Action | ✅ | Dynamic (user-configured fields) |
| SetRecordAction | Action | ✅ | Dynamic (user-configured fields) |
| HTTPClientAction | Action | ✅ | Dynamic (depends on user-configured HTTP response output) |
| GenerateAiTextAction | Action | ✅ | Static (single string) |
| AIAnalysisAction | Action | ✅ | Static (`analysisResult`) |
| Delay | Action | ❌ | No output |
| LarkMessageAction | Action | ❌ | No output |
| IfElseBranch | Branch | ❌ | No output |
| SwitchBranch | Branch | ❌ | No output |
| Loop | System | ✅ | Dynamic (depends on data source) |

---

### TextRefItem

Mixed text and references, used for dynamic concatenation scenarios such as message content:

```json
[
  { "value_type": "text", "value": "客户 " },
  { "value_type": "ref", "value": "$.step_1.fieldxxx" },
  { "value_type": "text", "value": " 创建了新订单" }
]
```

### RecordFieldValue

```json
{ "field_name": "客户名称", "value": [{ "value_type": "text", "value": "张三" }] }
```

<a id="andconditiontrigger-过滤条件"></a>
### AndCondition (Trigger Filter Condition)

```json
{
  "conjunction": "and",
  "conditions": [
    { "field_name": "状态", "operator": "is", "value": [{ "value_type": "text", "value": "进行中" }] }
  ]
}
```

<a id="orgroupbranch-分支条件"></a>
### OrGroup (Branch Condition)

```json
{
  "conjunction": "or",
  "conditions": [
    {
      "conjunction": "and",
      "conditions": [
        {
          "left_value": { "value_type": "ref", "value": "$.step_1.fieldxxx" },
          "operator": "isGreater",
          "right_value": [{ "value_type": "number", "value": 1000 }]
        }
      ]
    }
  ]
}
```

**Available operator values:** `is` / `isNot` / `containsAny` / `doesNotContainAny` / /`containsAll`/ `isEmpty` / `isNotEmpty` / `isGreater` / `isGreaterEqual` / `isLess` / `isLessEqual`

### RecordFilterInfo
** Since conjunction only supports and, if you need to implement field X equals A or B, you can use containsAny
```json
{
  "conjunction": "and",
  "conditions": [
    { "field_name": "状态", "operator": "is", "value": [{ "value_type": "text", "value": "进行中" }] }
  ]
}
```

<a id="select-字段多值匹配"></a>
### `select` Field Multi-Value Matching

| Operation | operator | Correct Syntax |
|------|---------|---------|
| Equals a single value | `is` | `[{"value_type": "option", "value": {"name": "L2"}}]` |
| Matches multiple values (L2 or L3) | `containsAny` | `[{"value_type": "option", "value": {"name": "L2"}}, {"value_type": "option", "value": {"name": "L3"}}]` |

> ⚠️ Do not use multiple `is` conditions (they will be treated as OR, and AND cannot be achieved). It is recommended to use the `containsAny` operator to match multiple values.

> ⚠️ **Select field condition**: `value_type` must be `option`, and the `value` object can pass only `name` (such as `{"name": "L2"}`), without providing the option ID.

### RefInfo

```json
{ "step_id": "step_trigger" }
```

---

<a id="完整示例条件分支--发送消息"></a>
## Complete Example: Conditional Branch + Send Message

```json
{
  "title": "新订单自动通知",
  "steps": [
    {
      "id": "step_1",
      "type": "AddRecordTrigger",
      "title": "当「订单表」新增记录时触发",
      "next": "step_2",
      "data": {
        "table_name": "订单表",
        "watched_field_name": "订单编号"
      }
    },
    {
      "id": "step_2",
      "type": "IfElseBranch",
      "title": "判断订单金额是否大于 1000",
      "children": {
        "links": [
          { "kind": "if_true", "to": "step_3" },
          { "kind": "if_false", "to": "step_4" }
        ]
      },
      "next": "step_5",
      "data": {
        "condition": {
          "conjunction": "or",
          "conditions": [{
            "conjunction": "and",
            "conditions": [{
              "left_value": { "value_type": "ref", "value": "$.step_1.fieldxxx" },
              "operator": "isGreater",
              "right_value": [{ "value_type": "number", "value": 1000 }]
            }]
          }]
        }
      }
    },
    {
      "id": "step_3",
      "type": "LarkMessageAction",
      "title": "通知主管审批大额订单",
      "next": null,
      "data": {
        "receiver": [{ "value_type": "ref", "value": "$.step_1.fieldxxx" }],
        "send_to_everyone": false,
        "title": [{ "value_type": "text", "value": "大额订单提醒" }],
        "content": [
          { "value_type": "text", "value": "新订单金额为：" },
          { "value_type": "ref", "value": "$.step_1.fieldxxx" },
          { "value_type": "text", "value": "元，请及时审批。" }
        ],
        "btn_list": []
      }
    },
    {
      "id": "step_4",
      "type": "SetRecordAction",
      "title": "自动标记小额订单为已通过",
      "next": null,
      "data": {
        "table_name": "订单表",
        "ref_info": { "step_id": "step_1" },
        "field_values": [
          { "field_name": "审批状态", "value": [{ "value_type": "text", "value": "已通过" }] }
        ]
      }
    },
    {
      "id": "step_5",
      "type": "GenerateAiTextAction",
      "title": "AI 生成订单处理日报",
      "next": null,
      "data": {
        "prompt": [
          { "value_type": "text", "value": "请根据以下订单信息生成一份简要的处理日报：" },
          { "value_type": "ref", "value": "$.step_1.fieldxxx" }
        ]
      }
    }
  ]
}
```

---

<a id="参考"></a>
## Reference

- [Workflow](lark-base-workflow.md) — Complete examples and construction techniques
- During creation/update, the outer layer only carries workflow meta-information; the core validation object is `steps`; the list is only used to obtain the workflow ID and start/stop status
