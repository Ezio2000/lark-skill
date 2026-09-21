
# approval tasks transfer

Transfer an approval task to another user for handling (user-level write operation). Typically, first obtain `tasks query` to get `task_id` and `instance_code`, confirm the target task, then provide the transferee's user ID to execute the transfer.

> [!CAUTION]
> This is a **high-risk-write** write operation. It is recommended to first preview with `--dry-run`; when actually executing, if the user has explicitly requested to transfer this approval and both the target task and transferee are correct, then run with `--yes`. Do not silently append `--yes` without the user's explicit consent.

Required scopes: ["approval:task:write"]

<a id="命令"></a>
## Command

```bash
# Preview the request first, without actually executing
lark-cli approval tasks transfer \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","transfer_user_id":"ou_xxx","comment":"请你继续处理"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --dry-run

# Transfer the approval task by open_id
lark-cli approval tasks transfer \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","transfer_user_id":"ou_xxx","comment":"转交给你处理"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --yes

# Transfer the approval task by user_id
lark-cli approval tasks transfer \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","transfer_user_id":"123456789","comment":"请补充审核"}' \
  --params '{"user_id_type":"user_id"}' \
  --as user \
  --yes

# Pass the request body via a file, suitable for longer comments
lark-cli approval tasks transfer \
  --data @./transfer-body.json \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --yes
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--data '{...}'` | Yes | Request body JSON, passed as JSON |
| `instance_code` | Yes | Approval instance Code; typically obtained first via `tasks query` or `instances initiated` / `instances get` |
| `task_id` | Yes | Approval task ID; typically obtained first via `tasks query` |
| `transfer_user_id` | Yes | The transferee's user ID; must be consistent with `user_id_type` |
| `comment` | No | Approval comment or transfer note, e.g. `转交给你处理`, `请继续审核该单据` |
| `--params '{"user_id_type":"..."}'` | No | Query parameter JSON; used to declare the ID type of `transfer_user_id` |
| `user_id_type` | No | User ID type: `user_id`, `union_id`, `open_id`; when not explicitly specified, be especially sure to confirm the actual type of `transfer_user_id` |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval transfer typically must be executed as a user |
| `--yes` | No | Confirm execution of a high-risk write operation; if omitted, may return `confirmation_required` / exit 10 |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call without executing |

<a id="典型前置步骤"></a>
## Typical Prerequisite Steps

First look up the pending task:

```bash
lark-cli approval tasks query --params '{"topic":"1"}' --as user
```

Commonly used fields:

| Field | Description |
|------|------|
| `tasks[].instance_code` | Approval instance Code; typically required when performing operations such as approve / reject / transfer / rollback |
| `tasks[].task_id` | Approval task ID; used in pair with `instance_code` |
| `tasks[].support_api_operate` | Whether the task supports handling via API; it is recommended to check before transferring |

If you only have a name or email, it is recommended to first resolve the correct user ID via the contacts capability, then execute the transfer.

If you need to first confirm the form, nodes, or approval flow progress, you can continue to view the instance details:

```bash
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user
```

<a id="使用建议"></a>
## Usage Recommendations

- **`instance_code` and `task_id` must be used in pair**: having only the instance ID or only the task ID is not sufficient to accurately execute the transfer operation.
- **`transfer_user_id` and `user_id_type` must match**: for example, if passing open_id, set `user_id_type` to `open_id`; do not mix them.
- **Prefer explicitly passing `user_id_type`**: this makes it easier for the agent to determine the meaning of the parameters and also reduces failures caused by ID type mismatches.
- **Prefer obtaining task parameters from the pending list of `tasks query`**: especially pending approvals of `topic=1`, which are most suitable as the input source for transfer.
- **First check whether API operations are supported**: if `tasks[].support_api_operate` is `false`, it means the task may not support handling actions such as approve/reject via API, and caution should also be exercised before transferring.
- **For `comment`, it is recommended to state the reason for transfer**: for example, `你更熟悉该项目，请继续处理`, `转交给预算 owner 审核`, to help the recipient understand the context.
- **`--dry-run` first, then execute**: especially for cross-department transfers, batch processing, or when the source of the transferee is unclear, previewing first is safer.
