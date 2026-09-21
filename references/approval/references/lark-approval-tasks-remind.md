
# approval tasks remind

Send a reminder for a specified task in an approval instance (user-level write operation). Typically, first use `tasks query` to find the pending task, obtain the `instance_code` and the `task_ids` to remind, and if necessary use `instances get` to view details, then execute the reminder.

> [!CAUTION]
> This is a **high-risk-write** write operation. It is recommended to first preview with `--dry-run`; when actually executing, if the user has explicitly requested to remind for this approval and the target instance and target task are both correct, then run with `--yes`. Do not silently append `--yes` without the user's explicit consent.

Required scopes: ["approval:instance:write"]

<a id="命令"></a>
## Command

```bash
# Preview the request first, without actually executing
lark-cli approval tasks remind \
  --data '{"instance_code":"<INSTANCE_CODE>","task_ids":["<TASK_ID>"],"comment":"请尽快处理"}' \
  --as user \
  --dry-run

# Remind a single approval task
lark-cli approval tasks remind \
  --data '{"instance_code":"<INSTANCE_CODE>","task_ids":["<TASK_ID>"],"comment":"请尽快审批该单据"}' \
  --as user \
  --yes

# Remind multiple tasks under the same instance
lark-cli approval tasks remind \
  --data '{"instance_code":"<INSTANCE_CODE>","task_ids":["<TASK_ID_1>","<TASK_ID_2>"],"comment":"请相关审批人尽快处理"}' \
  --as user \
  --yes

# Pass the request body via a file, suitable for longer comment or multiple task_ids
lark-cli approval tasks remind \
  --data @./remind-body.json \
  --as user \
  --yes
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--data '{...}'` | Yes | Request body JSON, passed using JSON |
| `instance_code` | Yes | Approval instance Code; typically obtained first via `tasks query` or `instances get` |
| `task_ids` | Yes | Array of task IDs to be reminded; should belong to the same approval instance as `instance_code` |
| `comment` | No | Reminder description, e.g. `请尽快处理`, `该单据较急，请优先审批` |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval reminders usually must be executed as a user |
| `--yes` | No | Confirm execution of a high-risk write operation; if not provided, may return `confirmation_required` / exit 10 |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call without executing |

<a id="典型前置步骤"></a>
## Typical Prerequisite Steps

First find the pending task:

```bash
lark-cli approval tasks query --params '{"topic":"1"}' --as user
```

Commonly used fields:

| Field | Description |
|------|------|
| `tasks[].instance_code` | Approval instance Code; must be provided when sending a reminder |
| `tasks[].task_id` | Approval task ID; put into the `task_ids` array |
| `tasks[].title` | Task title, can be used to confirm whether the reminder target is correct |
| `tasks[].status` | Task status; generally prioritize reminding tasks that are still in pending status |

If you need to further confirm the current approval flow, nodes, and personnel information, you can continue to view the instance details:

```bash
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user
```

<a id="使用建议"></a>
## Usage Recommendations

- **`instance_code` and `task_ids` must correspond to the same approval instance**: Do not mix task IDs from different instances in the same reminder request.
- **`task_ids` is an array**: Even if only reminding one task, it must be passed in array form.
- **Prefer to get parameters from the pending list of `tasks query`**: Especially pending approvals from `topic=1`, which are most suitable as the input source for remind.
- **Confirm before reminding that the task still needs to be handled**: Tasks that have already been approved, withdrawn, or terminated are generally not suitable for further reminders.
- **`comment` should be concise and clear**: For example, `该单据较急，请优先审批`, `请今天内处理`. Avoid overly long or vague descriptions.
- **`--dry-run` first, then execute**: Especially when reminding multiple tasks at once, when the task source is unclear, or when the user needs to review the reminder targets, previewing first is safer.
