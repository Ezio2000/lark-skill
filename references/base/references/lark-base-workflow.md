# Base Workflow

This document is the entry guide for Workflow, helping you choose step combinations, understand the create/update boundaries, and navigate to the steps JSON SSOT.

> **Companion documents**:
> - Workflow data structure reference: [lark-base-workflow-schema.md](lark-base-workflow-schema.md)
> - When creating/updating, focus on constructing `title`, `status`, and `steps`; the complexity is concentrated in `steps[].type/data/next`

---

<a id="快速开始"></a>
## Quick Start

<a id="最简单的-workflow"></a>
### The Simplest Workflow

Send a message notification when a record is added:

```json
{
  "client_token": "1704067200",
  "title": "新订单自动通知",
  "steps": [
    {
      "id": "trigger_1",
      "type": "AddRecordTrigger",
      "title": "监控新订单",
      "next": "action_1",
      "data": {
        "table_name": "订单表",
        "watched_field_name": "订单号"
      }
    },
    {
      "id": "action_1",
      "type": "LarkMessageAction",
      "title": "发送通知",
      "next": null,
      "data": {
        "receiver": [{ "value_type": "user", "value": {"id": "ou_xxxx", "name": "张三"} }],
        "send_to_everyone": false,
        "title": [{ "value_type": "text", "value": "新订单提醒" }],
        "content": [
          { "value_type": "text", "value": "收到新订单" }
        ],
        "btn_list": []
      }
    }
  ]
}
```

---

<a id="场景速查表"></a>
## Scenario Quick Reference

| Scenario | Step Combination | Example |
|------|---------|------|
| Add trigger + notification | AddRecordTrigger → LarkMessageAction | [Below](#示例-1-新增记录触发--发送消息) |
| Button click + call external API + write log | ButtonTrigger → HTTPClientAction → AddRecordAction | [Below](#示例-6-按钮触发--调用外部接口--写入同步日志) |
| Scheduled + loop | TimerTrigger → FindRecordAction → Loop → LarkMessageAction | [Below](#示例-2-定时触发--查找记录--循环遍历--发送消息) |
| Conditional judgment | ... → IfElseBranch → branch handling | [Below](#示例-3-条件分支ifelsebranch) |
| Multi-way classification | ... → SwitchBranch → multi-branch handling | [Below](#示例-4-多路分支switchbranch) |
| Complex combination | Scheduled + find + loop + branch + message | [Below](#示例-5-组合场景定时查找循环分支消息) |
| AI classification | ... → AIClassificationBranch → post-classification handling | [Below](#示例-7-ai-分类用户反馈自动分流) |

---

<a id="完整示例"></a>
## Complete Examples

<a id="示例-1-新增记录触发--发送消息"></a>
### Example 1: Add Record Trigger + Send Message

**Scenario**: When a record is added to the order table, send a Feishu message to notify the person in charge.

```json
{
  "client_token": "1704067201",
  "title": "新订单自动通知",
  "steps": [
    {
      "id": "step_trigger",
      "type": "AddRecordTrigger",
      "title": "新增订单时触发",
      "next": "step_notify",
      "data": {
        "table_name": "订单表",
        "watched_field_name": "订单号",
        "condition_list": null
      }
    },
    {
      "id": "step_notify",
      "type": "LarkMessageAction",
      "title": "发送订单通知",
      "next": null,
      "data": {
        "receiver": [{ "value_type": "ref", "value": "$.step_trigger.fldManager" }],
        "send_to_everyone": false,
        "title": [{ "value_type": "text", "value": "新订单提醒" }],
        "content": [
          { "value_type": "text", "value": "客户 " },
          { "value_type": "ref", "value": "$.step_trigger.fldCustomer" },
          { "value_type": "text", "value": " 创建了新订单，金额：¥" },
          { "value_type": "ref", "value": "$.step_trigger.fldAmount" }
        ],
        "btn_list": [
          {
            "text": "查看订单",
            "btn_action": "openLink",
            "link": [{ "value_type": "ref", "value": "$.step_trigger.recordLink" }]
          }
        ]
      }
    }
  ]
}
```

**Key points**:
- `AddRecordTrigger` monitors the `watched_field_name` field of the `table_name` table
- Use `ref` to reference the field value output by the trigger (note it is the fieldId, not the field name)
- `recordLink` is a built-in trigger output, representing the record link

---

<a id="示例-2-定时触发--查找记录--循环遍历--发送消息"></a>
### Example 2: Scheduled Trigger + Find Records + Loop Iteration + Send Message

**Scenario**: Every day at 9 AM, find all pending orders and send a reminder to each customer.

```json
{
  "client_token": "1704067202",
  "title": "每日待处理订单提醒",
  "steps": [
    {
      "id": "step_timer",
      "type": "TimerTrigger",
      "title": "每天早上9点触发",
      "next": "step_find_orders",
      "data": {
        "rule": "DAILY",
        "start_time": "2025-01-01 09:00",
        "is_never_end": true
      }
    },
    {
      "id": "step_find_orders",
      "type": "FindRecordAction",
      "title": "查找所有待处理订单",
      "next": "step_loop_customers",
      "data": {
        "table_name": "订单表",
        "field_names": ["客户名称", "订单金额", "客户联系方式"],
        "should_proceed_when_no_results": false,
        "filter_info": {
          "conjunction": "and",
          "conditions": [
            {
              "field_name": "状态",
              "operator": "is",
              "value": [{ "value_type": "option", "value": { "name": "待处理" } }]
            }
          ]
        }
      }
    },
    {
      "id": "step_loop_customers",
      "type": "Loop",
      "title": "遍历每个订单",
      "children": {
        "links": [
          { "kind": "loop_start", "to": "step_send_reminder" }
        ]
      },
      "next": null,
      "data": {
        "loop_mode": "continue",
        "max_loop_times": 100,
        "data": [{
          "value_type": "ref",
          "value": "$.step_find_orders.fieldRecords"
        }]
      }
    },
    {
      "id": "step_send_reminder",
      "type": "LarkMessageAction",
      "title": "发送催办消息",
      "next": null,
      "data": {
        "receiver": [{
          "value_type": "ref",
          "value": "$.step_loop_customers.item.fldContact"
        }],
        "send_to_everyone": false,
        "title": [{ "value_type": "text", "value": "订单处理提醒" }],
        "content": [
          { "value_type": "text", "value": "您好，您的订单 " },
          { "value_type": "ref", "value": "$.step_loop_customers.item.fldName" },
          { "value_type": "text", "value": " 金额 ¥" },
          { "value_type": "ref", "value": "$.step_loop_customers.item.fldAmount" },
          { "value_type": "text", "value": " 正在处理中。" }
        ],
        "btn_list": []
      }
    }
  ]
}
```

**Key points**:
- `Loop.data` must be passed a data source of type `ref` (usually the `fieldRecords` of FindRecordAction)
- `Loop.children.links` must contain a link to the loop body via `kind: "loop_start"`
- Inside the loop body, use `$.{loopStepId}.item.{fieldId}` to reference the fields of the current iterated record
- `$.{loopStepId}.index` gets the current index (starting from 0)

---

<a id="示例-3-条件分支ifelsebranch"></a>
### Example 3: Conditional Branch (IfElseBranch)

**Scenario**: Based on the order amount, notify the supervisor for approval for large orders, and automatically approve small orders.

```json
{
  "client_token": "1704067203",
  "title": "订单金额自动判断",
  "steps": [
    {
      "id": "step_trigger",
      "type": "AddRecordTrigger",
      "title": "新增订单时触发",
      "next": "step_check_amount",
      "data": {
        "table_name": "订单表",
        "watched_field_name": "订单金额"
      }
    },
    {
      "id": "step_check_amount",
      "type": "IfElseBranch",
      "title": "判断是否为大额订单",
      "children": {
        "links": [
          { "kind": "if_true", "to": "step_notify_manager", "label": "high", "desc": "金额>=10000" },
          { "kind": "if_false", "to": "step_auto_approve", "label": "normal", "desc": "金额<10000" }
        ]
      },
      "next": "step_log",
      "data": {
        "condition": {
          "conjunction": "or",
          "conditions": [
            {
              "conjunction": "and",
              "conditions": [
                {
                  "left_value": { "value_type": "ref", "value": "$.step_trigger.fldAmount" },
                  "operator": "isGreaterEqual",
                  "right_value": [{ "value_type": "number", "value": 10000 }]
                }
              ]
            }
          ]
        }
      }
    },
    {
      "id": "step_notify_manager",
      "type": "LarkMessageAction",
      "title": "通知主管审批大额订单",
      "next": "step_log",
      "data": {
        "receiver": [{ "value_type": "user", "value": {"id": "ou_manager", "name": "主管"} }],
        "send_to_everyone": false,
        "title": [{ "value_type": "text", "value": "大额订单待审批" }],
        "content": [
          { "value_type": "text", "value": "有大额订单 ¥" },
          { "value_type": "ref", "value": "$.step_trigger.fldAmount" },
          { "value_type": "text", "value": " 需要您审批" }
        ],
        "btn_list": []
      }
    },
    {
      "id": "step_auto_approve",
      "type": "SetRecordAction",
      "title": "自动标记小额订单为已审核",
      "next": "step_log",
      "data": {
        "table_name": "订单表",
        "ref_info": { "step_id": "step_trigger" },
        "field_values": [
          {
            "field_name": "审批状态",
            "value": [{ "value_type": "option", "value": { "name": "已自动审核" } }]
          }
        ]
      }
    },
    {
      "id": "step_log",
      "type": "GenerateAiTextAction",
      "title": "生成订单处理日志",
      "next": null,
      "data": {
        "prompt": [
          { "value_type": "text", "value": "请生成订单处理日志，金额：" },
          { "value_type": "ref", "value": "$.step_trigger.fldAmount" }
        ]
      }
    }
  ]
}
```

**Key points**:
- `IfElseBranch.children.links` must contain the two branches `if_true` and `if_false`
- `next` points to the step after the two branches merge (optional; if null, the branch ends)
- `condition` uses the OrGroup structure, supporting complex conditions with `(A and B) or (C and D)`
- Inside the branch, you can use `ref_info` to reference the trigger record, and `filter_info` to batch-filter records

---

<a id="示例-4-多路分支switchbranch"></a>
### Example 4: Multi-way Branch (SwitchBranch)

**Scenario**: Execute different processing flows based on order priority (P0/P1/P2).

```json
{
  "client_token": "1704067204",
  "title": "按优先级分类处理订单",
  "steps": [
    {
      "id": "step_trigger",
      "type": "AddRecordTrigger",
      "title": "新增订单时触发",
      "next": "step_classify",
      "data": {
        "table_name": "订单表",
        "watched_field_name": "优先级"
      }
    },
    {
      "id": "step_classify",
      "type": "SwitchBranch",
      "title": "按优先级分类",
      "children": {
        "links": [
          { "kind": "case", "to": "step_p0_handler", "label": "p0", "desc": "P0-紧急" },
          { "kind": "case", "to": "step_p1_handler", "label": "p1", "desc": "P1-高优先级" },
          { "kind": "case", "to": "step_p2_handler", "label": "p2", "desc": "P2-普通" },
          { "kind": "case", "to": "step_other_handler", "label": "other", "desc": "其他" }
        ]
      },
      "next": null,
      "data": {
        "mode": "exclusive",
        "no_match_action": "classifyToOther",
        "child_branch_list": [
          {
            "name": "P0-紧急",
            "condition": {
              "conjunction": "or",
              "conditions": [
                {
                  "conjunction": "and",
                  "conditions": [
                    {
                      "left_value": { "value_type": "ref", "value": "$.step_trigger.fldPriority" },
                      "operator": "is",
                      "right_value": [{ "value_type": "option", "value": { "name": "P0" } }]
                    }
                  ]
                }
              ]
            }
          },
          {
            "name": "P1-高优先级",
            "condition": {
              "conjunction": "or",
              "conditions": [
                {
                  "conjunction": "and",
                  "conditions": [
                    {
                      "left_value": { "value_type": "ref", "value": "$.step_trigger.fldPriority" },
                      "operator": "is",
                      "right_value": [{ "value_type": "option", "value": { "name": "P1" } }]
                    }
                  ]
                }
              ]
            }
          },
          {
            "name": "P2-普通",
            "condition": {
              "conjunction": "or",
              "conditions": [
                {
                  "conjunction": "and",
                  "conditions": [
                    {
                      "left_value": { "value_type": "ref", "value": "$.step_trigger.fldPriority" },
                      "operator": "is",
                      "right_value": [{ "value_type": "option", "value": { "name": "P2" } }]
                    }
                  ]
                }
              ]
            }
          }
        ]
      }
    },
    {
      "id": "step_p0_handler",
      "type": "LarkMessageAction",
      "title": "P0紧急处理",
      "next": null,
      "data": {
        "receiver": [{ "value_type": "user", "value": {"id": "ou_director", "name": "总监"} }],
        "send_to_everyone": false,
        "title": [{ "value_type": "text", "value": "🚨 P0 紧急订单" }],
        "content": [{ "value_type": "text", "value": "有新的 P0 紧急订单需要立即处理" }],
        "btn_list": []
      }
    },
    {
      "id": "step_p1_handler",
      "type": "SetRecordAction",
      "title": "标记高优先级",
      "next": null,
      "data": {
        "table_name": "订单表",
        "ref_info": { "step_id": "step_trigger" },
        "field_values": [
          { "field_name": "处理状态", "value": [{ "value_type": "text", "value": "高优先级待处理" }] }
        ]
      }
    },
    {
      "id": "step_p2_handler",
      "type": "Delay",
      "title": "普通订单延迟处理",
      "next": null,
      "data": { "duration": 60 }
    },
    {
      "id": "step_other_handler",
      "type": "SetRecordAction",
      "title": "标记其他订单",
      "next": null,
      "data": {
        "table_name": "订单表",
        "ref_info": { "step_id": "step_trigger" },
        "field_values": [
          { "field_name": "处理状态", "value": [{ "value_type": "text", "value": "待分类" }] }
        ]
      }
    }
  ]
}
```

**Key points**:
- `SwitchBranch` is suitable for scenarios with 3 or more branches (for fewer than 3 branches, `IfElseBranch` is more concise)
- In `children.links`, the `label` of `kind: "case"` corresponds to the conditions in `child_branch_list`
- `mode: "exclusive"` indicates exclusive execution (stops after the first matching branch executes)
- `no_match_action: "classifyToOther"` indicates that when there is no match, the last `case` is used (fallback branch)

---

<a id="示例-5-组合场景定时查找循环分支消息"></a>
### Example 5: Combined Scenario (Scheduled + Find + Loop + Branch + Message)

**Scenario**: Every day at 9 AM, find yesterday's orders, classify them by amount, and send different notifications to salespeople of different levels.

```json
{
  "client_token": "1704067205",
  "title": "每日订单分级通知",
  "steps": [
    {
      "id": "step_timer",
      "type": "TimerTrigger",
      "title": "每天早上9点触发",
      "next": "step_find_orders",
      "data": {
        "rule": "DAILY",
        "start_time": "2025-01-01 09:00",
        "is_never_end": true
      }
    },
    {
      "id": "step_find_orders",
      "type": "FindRecordAction",
      "title": "查找昨天所有订单",
      "next": "step_loop",
      "data": {
        "table_name": "订单表",
        "field_names": ["订单号", "客户名称", "金额", "销售负责人"],
        "should_proceed_when_no_results": false,
        "filter_info": {
          "conjunction": "and",
          "conditions": [
            { "field_name": "创建时间", "operator": "isGreaterEqual", "value": [{ "value_type": "date", "value": "yesterday" }] }
          ]
        }
      }
    },
    {
      "id": "step_loop",
      "type": "Loop",
      "title": "遍历每个订单",
      "children": {
        "links": [
          { "kind": "loop_start", "to": "step_classify" }
        ]
      },
      "next": "step_summary",
      "data": {
        "loop_mode": "continue",
        "max_loop_times": 500,
        "data": [{ "value_type": "ref", "value": "$.step_find_orders.fieldRecords" }]
      }
    },
    {
      "id": "step_classify",
      "type": "SwitchBranch",
      "title": "按金额分类",
      "children": {
        "links": [
          { "kind": "case", "to": "step_vip_notify", "label": "vip", "desc": "VIP >= 10万" },
          { "kind": "case", "to": "step_normal_notify", "label": "normal", "desc": "普通 < 10万" }
        ]
      },
      "next": null,
      "data": {
        "mode": "exclusive",
        "no_match_action": "fail",
        "child_branch_list": [
          {
            "name": "VIP订单",
            "condition": {
              "conjunction": "or",
              "conditions": [
                {
                  "conjunction": "and",
                  "conditions": [
                    {
                      "left_value": { "value_type": "ref", "value": "$.step_loop.item.fldAmount" },
                      "operator": "isGreaterEqual",
                      "right_value": [{ "value_type": "number", "value": 100000 }]
                    }
                  ]
                }
              ]
            }
          },
          {
            "name": "普通订单",
            "condition": {
              "conjunction": "or",
              "conditions": [
                {
                  "conjunction": "and",
                  "conditions": [
                    {
                      "left_value": { "value_type": "ref", "value": "$.step_loop.item.fldAmount" },
                      "operator": "isLess",
                      "right_value": [{ "value_type": "number", "value": 100000 }]
                    }
                  ]
                }
              ]
            }
          }
        ]
      }
    },
    {
      "id": "step_vip_notify",
      "type": "LarkMessageAction",
      "title": "VIP订单通知",
      "next": null,
      "data": {
        "receiver": [{ "value_type": "ref", "value": "$.step_loop.item.fldSales" }],
        "send_to_everyone": false,
        "title": [{ "value_type": "text", "value": "🌟 VIP大额订单" }],
        "content": [
          { "value_type": "text", "value": "恭喜！您有一笔 VIP 订单 ¥" },
          { "value_type": "ref", "value": "$.step_loop.item.fldAmount" },
          { "value_type": "text", "value": "，客户：" },
          { "value_type": "ref", "value": "$.step_loop.item.fldCustomer" }
        ],
        "btn_list": []
      }
    },
    {
      "id": "step_normal_notify",
      "type": "LarkMessageAction",
      "title": "普通订单通知",
      "next": null,
      "data": {
        "receiver": [{ "value_type": "ref", "value": "$.step_loop.item.fldSales" }],
        "send_to_everyone": false,
        "title": [{ "value_type": "text", "value": "新订单通知" }],
        "content": [
          { "value_type": "text", "value": "您有一笔新订单 ¥" },
          { "value_type": "ref", "value": "$.step_loop.item.fldAmount" }
        ],
        "btn_list": []
      }
    },
    {
      "id": "step_summary",
      "type": "GenerateAiTextAction",
      "title": "生成日报",
      "next": null,
      "data": {
        "prompt": [
          { "value_type": "text", "value": "请生成昨日订单处理日报" }
        ]
      }
    }
  ]
}
```

---

<a id="示例-6-按钮触发--调用外部接口--写入同步日志"></a>
### Example 6: Button Trigger + Call External API + Write Sync Log

**Scenario**: In the "Customer Lead Table", configure a "Sync to CRM" button for each record. After the salesperson clicks the button, the Workflow calls the external CRM API to sync the current lead, then adds a record to the "Sync Log Table" for subsequent auditing and troubleshooting.

```json
{
  "client_token": "1704067206",
  "title": "线索一键同步到 CRM",
  "steps": [
    {
      "id": "step_button_trigger",
      "type": "ButtonTrigger",
      "title": "点击同步到 CRM 按钮时触发",
      "next": "step_call_crm_api",
      "data": {
        "button_type": "buttonField",
        "table_name": "客户线索表"
      }
    },
    {
      "id": "step_call_crm_api",
      "type": "HTTPClientAction",
      "title": "调用 CRM 同步接口",
      "next": "step_add_sync_log",
      "data": {
        "method": "POST",
        "url": [
          { "value_type": "text", "value": "https://api.example-crm.com/v1/leads/sync" }
        ],
        "headers": [
          { "key": "Content-Type", "value": [{ "value_type": "text", "value": "application/json" }] },
          { "key": "X-System", "value": [{ "value_type": "text", "value": "lark_base_workflow" }] }
        ],
        "body_type": "raw",
        "raw_body": [
          { "value_type": "text", "value": "{\"lead_name\":\"" },
          { "value_type": "ref", "value": "$.step_button_trigger.fldLeadName" },
          { "value_type": "text", "value": "\",\"mobile\":\"" },
          { "value_type": "ref", "value": "$.step_button_trigger.fldMobile" },
          { "value_type": "text", "value": "\",\"company\":\"" },
          { "value_type": "ref", "value": "$.step_button_trigger.fldCompany" },
          { "value_type": "text", "value": "\",\"owner\":\"" },
          { "value_type": "ref", "value": "$.step_button_trigger.fldOwner" },
          { "value_type": "text", "value": "\",\"source_record_id\":\"" },
          { "value_type": "ref", "value": "$.step_button_trigger.recordId" },
          { "value_type": "text", "value": "\"}" }
        ],
        "response_type": "json",
        "response_value": "{\"success\":true,\"message\":\"lead synced successfully\"}"
      }
    },
    {
      "id": "step_add_sync_log",
      "type": "AddRecordAction",
      "title": "写入同步日志",
      "next": null,
      "data": {
        "table_name": "同步日志表",
        "field_values": [
          {
            "field_name": "线索名称",
            "value": [{ "value_type": "ref", "value": "$.step_button_trigger.fldLeadName" }]
          },
          {
            "field_name": "手机号",
            "value": [{ "value_type": "ref", "value": "$.step_button_trigger.fldMobile" }]
          },
          {
            "field_name": "公司名称",
            "value": [{ "value_type": "ref", "value": "$.step_button_trigger.fldCompany" }]
          },
          {
            "field_name": "负责人",
            "value": [{ "value_type": "ref", "value": "$.step_button_trigger.fldOwner" }]
          },
          {
            "field_name": "来源记录ID",
            "value": [{ "value_type": "ref", "value": "$.step_button_trigger.recordId" }]
          },
          {
            "field_name": "同步状态",
            "value": [{ "value_type": "text", "value": "已提交 CRM 同步" }]
          },
          {
            "field_name": "同步是否成功",
            "value": [{ "value_type": "ref", "value": "$.step_call_crm_api.body.success" }]
          },
          {
            "field_name": "同步结果说明",
            "value": [{ "value_type": "ref", "value": "$.step_call_crm_api.body.message" }]
          },
          {
            "field_name": "备注",
            "value": [{ "value_type": "text", "value": "由按钮触发自动发起同步请求" }]
          }
        ]
      }
    }
  ]
}
```

**Key points**:
- `ButtonTrigger` is suitable for scenarios of "execute after manual confirmation", such as syncing to CRM, pushing to ERP, initiating approvals, etc.
- `button_type: "buttonField"` indicates that the button is attached to the record, so it can directly reference the fields and values of the current record
- `HTTPClientAction.raw_body` can dynamically concatenate the JSON request body via `text + ref + text`
- The output reference rules for `HTTPClientAction` are: when `response_type=none`, it cannot be referenced; when `response_type=text`, only `$.stepId` can be used to reference the entire text; when `response_type=json`, use `$.stepId.body` to reference the entire body, use `$.stepId.body.字段名` to reference fields in the body, and `$.stepId.status_code` represents the HTTP response status code
- Only the fields declared in `HTTPClientAction.response_value` can be referenced by subsequent nodes; for example, `$.step_call_crm_api.body.success`, `$.step_call_crm_api.body.message`
- `AddRecordAction` is commonly used to write to log tables, operation audit tables, and sync result tables, making it easy to track who triggered the external call and when
- The `fldLeadName` / `fldMobile` / `fldCompany` / `fldOwner` in the example are just placeholder fieldIds; please refer to the actual table field IDs

---

<a id="示例-7-ai-分类用户反馈自动分流"></a>
### Example 7: AI Classification (Automatic Routing of User Feedback)

**Scenario**: When a record is added to the user feedback table, AI classifies the feedback content as a Bug or a feature suggestion; if it cannot be determined, it is marked as pending manual review.

```json
{
  "client_token": "1704067206",
  "title": "用户反馈自动分流",
  "steps": [
    {
      "id": "step_trigger",
      "type": "AddRecordTrigger",
      "title": "新增反馈时触发",
      "next": "step_ai_classify",
      "data": {
        "table_name": "用户反馈表",
        "watched_field_name": "反馈详情"
      }
    },
    {
      "id": "step_ai_classify",
      "type": "AIClassificationBranch",
      "title": "AI 判断反馈类型",
      "children": {
        "links": [
          { "kind": "case", "to": "step_bug_action", "label": "branch_1", "desc": "Bug" },
          { "kind": "case", "to": "step_feature_action", "label": "branch_2", "desc": "功能建议" },
          { "kind": "case", "to": "step_other_action", "label": "default", "desc": "默认分支" }
        ]
      },
      "next": null,
      "data": {
        "classes": [
          {
            "name": "Bug",
            "desc": "功能报错、异常、崩溃、无法使用或结果错误"
          },
          {
            "name": "功能建议",
            "desc": "希望新增能力或改变产品行为"
          }
        ],
        "content": [
          { "value_type": "ref", "value": "$.step_trigger.fldFeedbackDetail" }
        ],
        "classification_rule": "有明确故障现象时优先归入 Bug；同时包含多个诉求时，以最影响用户完成任务的问题为准；信息不足时进入默认分支。"
      }
    },
    {
      "id": "step_bug_action",
      "type": "SetRecordAction",
      "title": "标记为 Bug",
      "next": null,
      "data": {
        "table_name": "用户反馈表",
        "ref_info": { "step_id": "step_trigger" },
        "field_values": [
          { "field_name": "分类", "value": [{ "value_type": "text", "value": "Bug" }] }
        ]
      }
    },
    {
      "id": "step_feature_action",
      "type": "SetRecordAction",
      "title": "标记为功能建议",
      "next": null,
      "data": {
        "table_name": "用户反馈表",
        "ref_info": { "step_id": "step_trigger" },
        "field_values": [
          { "field_name": "分类", "value": [{ "value_type": "text", "value": "功能建议" }] }
        ]
      }
    },
    {
      "id": "step_other_action",
      "type": "SetRecordAction",
      "title": "标记为待人工复核",
      "next": null,
      "data": {
        "table_name": "用户反馈表",
        "ref_info": { "step_id": "step_trigger" },
        "field_values": [
          { "field_name": "分类", "value": [{ "value_type": "text", "value": "待人工复核" }] }
        ]
      }
    }
  ]
}
```
**Key points**:
- `classes` corresponds in order to `branch_1`, `branch_2`; `desc` matches the classification name, and `to` points to an already-defined downstream step;

---

<a id="构造技巧"></a>
## Construction Techniques

<a id="loop-构造要点"></a>
### Loop Construction Key Points

1. **Data source**: `Loop.data` must be passed a type of `ref`, usually the `fieldRecords` of `FindRecordAction`
2. **Loop body**: `children.links` must contain `kind: "loop_start"` pointing to the loop body entry
3. **Reference**: Inside the loop body, use `$.{loopStepId}.item.{fieldId}` to reference the current element
4. **Index**: Use `$.{loopStepId}.index` to get the current index (starting from 0)

<a id="分支构造要点"></a>
### Branch Construction Key Points

1. **IfElseBranch**:
   - Suitable for binary judgments (yes/no, greater than/less than)
   - `children.links` must contain `if_true` and `if_false`
   - You can use `next` to point to the merge point

2. **SwitchBranch**:
   - Suitable for multi-way classification (3 or more branches)
   - `label` corresponds to the condition order in `child_branch_list`
   - It is recommended to add a fallback branch (other)

<a id="字段值构造"></a>
### Field Value Construction

| Field Type | value_type | Example |
|---------|------------|------|
| Text | `text` | `{"value_type": "text", "value": "张三"}` |
| Number | `number` | `{"value_type": "number", "value": 100}` |
| Single select | `option` | `{"value_type": "option", "value": {"name": "已完成"}}` |
| Person | `user` | `{"value_type": "user", "value": {"id": "ou_xxxx"}}` |
| Reference | `ref` | `{"value_type": "ref", "value": "$.step_1.fldxxx"}` |

---

<a id="常见错误避免"></a>
## Avoiding Common Errors

<a id="top-10-高频错误"></a>
### Top 10 High-Frequency Errors

| # | Error Message | Cause | Solution |
|---|---------|------|---------|
| 1 | `path "xxx" does not exist in the output path tree` | Incorrect ref reference path or stepId does not exist | Check whether the stepId is in the steps array; use fieldId instead of field name; ensure the path starts with `$.` |
| 2 | `recordInfo.conditions must be non-empty` | `condition_list` is an empty array `[]` | Switch to `null` or omit this field |
| 3 | `At least one of filter info and ref info is required` | SetRecordAction/FindRecordAction is missing a locating condition | You must provide one of `filter_info` or `ref_info` |
| 4 | `client token is empty` | Missing `client_token` | Pass a unique value with each request (timestamp or random string) |
| 5 | `valueType 'text' not allowed for fieldType '3'` | Incorrect value format for a select-type field | Switch to the `option` type |
| 6 | `Undefined Step Type` | An unsupported StepType was used | Use `AddRecordTrigger` instead of `CreateRecordTrigger` |
| 7 | `prompt references an unknown reference from step` | The referenced stepId does not exist | Ensure the referenced step is in the steps array of the same workflow |
| 8 | `[2200] Internal Error` | 1. Duplicate steps[].id 2. next/children.links references a nonexistent step | Ensure all step ids are unique; check the reference relationships |
| 9 | Incomplete workflow structure | Branch/Loop nodes are missing `children` | Only Branch (IfElseBranch/SwitchBranch) and Loop nodes need `children`; Trigger/Action nodes do not need to set it |
| 10 | Nested branches are too complex | Multiple levels of IfElseBranch nesting | For 3+ branches, use SwitchBranch instead of nested IfElseBranch |

<a id="其他常见错误"></a>
### Other Common Errors

**1. condition_list is an empty array**
```json
// ❌ Incorrect
{ "condition_list": [] }

// ✅ Correct
{ "condition_list": null }
// or omit this field
```

**2. filter_info and ref_info are provided at the same time**
```json
// ❌ Incorrect
{ "filter_info": {...}, "ref_info": {...} }

// ✅ Correct (choose one)
{ "filter_info": {...}, "ref_info": null }
{ "filter_info": null, "ref_info": {...} }
```

**3. Using the field name instead of fieldId**
```json
// ❌ Incorrect
{ "value": "$.step_1.客户名称" }

// ✅ Correct
{ "value": "$.step_1.fldXXXXXXXX" }
```

---

<a id="参考"></a>
## Reference

- [lark-base-workflow-schema.md](lark-base-workflow-schema.md) — Field definition reference
- Before creating/updating, first confirm the real table name, field name, and target workflow ID; construct the `steps` structure according to the schema, and do not guess `type` from natural language
