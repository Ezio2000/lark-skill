
# approval instances get

Get details of a single approval instance (user-level read-only operation). Useful for viewing the approval form, current nodes, task list, approval activity, and overall status before performing approve / reject / transfer / rollback / cancel / cc / remind.

Required scopes: ["approval:instance:read"]

<a id="命令"></a>
## Command

```bash
# Query details by instance Code
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user

# Table format output, for quickly browsing top-level fields
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --format table --as user

# Preview the API call without executing
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--params '{...}'` | Yes | Query parameters, passed as JSON |
| `instance_code` | Yes | Approval instance Code |
| `locale` | No | Return language, e.g. `zh-CN`, `en-US`, `ja-JP` |
| `user_id_type` | No | User ID type: `user_id`, `union_id`, `open_id` |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval instance detail queries should usually use the user identity |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call without executing |

<a id="常见输入来源"></a>
## Common input sources

If you already have the instance Code, you can query directly:

```bash
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user
```

If you do not yet have the instance Code, you can first obtain it from the following commands:

```bash
# Query approval instances I initiated
lark-cli approval instances initiated --params '{"page_size":20}' --as user

# Or get the associated instance Code from the task list
lark-cli approval tasks query --params '{"topic":"1"}' --as user
```

<a id="输出重点字段"></a>
## Key output fields

Common fields in the returned result:

| Field | Description |
|------|------|
| `instance_code` | Approval instance Code |
| `serial_number` | Approval form number |
| `definition_code` | Approval definition Code |
| `definition_name` | Approval name |
| `user_id` | User ID of the person who initiated the approval |
| `department_id` | Department ID of the initiator |
| `status` | Approval instance status, see "status enum" below |
| `reverted` | Whether the form has been revoked |
| `start_time` | Approval creation time |
| `end_time` | Approval completion time, usually `0` when not completed |
| `form` | Form data, JSON string |
| `current_nodes` | List of current approval nodes |
| `tasks` | List of approval tasks |
| `operation_records` | Approval activity, e.g. approved, rejected, transferred, added approver, rolled back, withdrawn, cc |
| `comments` | List of comments |

<a id="status-枚举"></a>
## status enum

| Value | Meaning |
|----|------|
| `PENDING` | In approval |
| `APPROVED` | Approved |
| `REJECTED` | Rejected |
| `CANCELED` | Withdrawn |
| `DELETED` | Deleted |

<a id="current_nodes-重点字段"></a>
## current_nodes key fields

`current_nodes` is often used to determine which level the approval flow is currently stuck at:

| Field | Description                                       |
|------|------------------------------------------|
| `current_nodes[].node_id` | Current approval node ID                                |
| `current_nodes[].node_name` | Current approval node name                                 |
| `current_nodes[].type` | Approval method: `AND` all-approve, `OR` any-approve, `SEQUENTIAL` sequential approval, etc. |
| `current_nodes[].approvers[].task_id` | Task ID associated with the current approver                             |
| `current_nodes[].approvers[].user_id` | User ID of the current approver                               |

<a id="tasks-重点字段"></a>
## tasks key fields

`tasks` is often used to associate an instance with specific approval tasks:

| Field | Description |
|------|------|
| `tasks[].id` | Approval task ID |
| `tasks[].node_id` | ID of the node the task belongs to |
| `tasks[].node_name` | Name of the node the task belongs to |
| `tasks[].user_id` | Approver user ID |
| `tasks[].status` | Task status: `PENDING`, `APPROVED`, `REJECTED`, `TRANSFERRED`, `DONE` |
| `tasks[].start_time` | Task start time |
| `tasks[].end_time` | Task completion time |

<a id="operation_records-重点字段"></a>
## operation_records key fields

`operation_records` is often used to audit the approval process:

| Field | Description |
|------|------|
| `operation_records[].type` | Event type, e.g. `PASS`, `REJECT`, `TRANSFER`, `ROLLBACK`, `CANCEL`, `CC` |
| `operation_records[].create_time` | Time the event occurred |
| `operation_records[].user_id` | User ID that triggered the event |
| `operation_records[].task_id` | Associated task ID |
| `operation_records[].node_id` | Associated node ID |
| `operation_records[].comment` | Reason / remark |
| `operation_records[].cc_user_ids` | List of cc recipients (for cc events) |

<a id="使用建议"></a>
## Usage recommendations

- **This is the most suitable read-only command for "detail confirmation"**: when you already have `instance_code` and need to confirm the form, current nodes, task status, and approval activity, use it first.
- **View details before performing write operations**: for example, confirm the rollback-able nodes before doing `tasks rollback`, confirm the instance status before doing `instances cancel`, and confirm whether the current task is still pending before doing `tasks remind`.
- **`form` is a JSON string**: the caller usually needs to parse it one more level to get the form field values.
- **`current_nodes` and `tasks` can be viewed together**: the former shows "which node it is currently stuck at", while the latter shows "who is currently handling each task and what the status is".
- **`operation_records` is suitable for timeline backtracking**: for example, investigating who transferred, who added an approver, and when it was withdrawn or cc'd.
- **Prefer explicitly passing `locale` and `user_id_type`**: this makes it easier for the agent to understand the returned text and ID semantics, reducing ambiguity.

<a id="输出与后续操作"></a>
## Output and follow-up operations

After reading the details, common next steps:

```bash
# Approve approval task
lark-cli approval tasks approve --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>"}' --as user --yes

# Withdraw approval instance
lark-cli approval instances cancel --data '{"instance_code":"<INSTANCE_CODE>"}' --as user --yes

# Remind approval task
lark-cli approval tasks remind --data '{"instance_code":"<INSTANCE_CODE>","task_ids":["<TASK_ID>"]}' --as user --yes
```
