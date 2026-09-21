
# approval tasks reject

Reject an approval task (user-level write operation). Typically, first obtain `tasks query` and `task_id` via `instance_code`, then use `instances get` to view details if necessary, and then perform the rejection.

> [!CAUTION]
> This is a **high-risk-write** write operation. It is recommended to preview first with `--dry-run`; when actually executing, if the user has explicitly requested to reject this approval and the target task is correct, then run with `--yes`. Do not silently append `--yes` without the user's explicit consent.

Required scopes: ["approval:task:write"]

<a id="命令"></a>
## Command

```bash
# Preview the request first, without actually executing
lark-cli approval tasks reject \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","comment":"拒绝"}' \
  --as user \
  --dry-run

# Reject the approval task, with an approval comment attached
lark-cli approval tasks reject \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","comment":"拒绝，信息不完整"}' \
  --as user \
  --yes

# Pass the request body via a file, suitable for longer comments
lark-cli approval tasks reject \
  --data @./reject-body.json \
  --as user \
  --yes
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--data '{...}'` | Yes | Request body JSON, passed in as JSON |
| `instance_code` | Yes | Approval instance Code; typically obtained first via `tasks query` or `instances initiated` / `instances get` |
| `task_id` | Yes | Approval task ID; typically obtained first via `tasks query` |
| `comment` | No | Approval comment, e.g. `拒绝`, `拒绝，信息不完整` |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval rejection usually must be executed as a user |
| `--yes` | No | Confirm execution of a high-risk write operation; if not provided, may return `confirmation_required` / exit 10 |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call, without executing |

<a id="典型前置步骤"></a>
## Typical Prerequisite Steps

First look up the pending task:

```bash
lark-cli approval tasks query --params '{"topic":"1"}' --as user
```

Two commonly used fields:

| Field | Description |
|------|------|
| `tasks[].instance_code` | Approval instance Code; typically required when performing operations such as approve / reject / rollback |
| `tasks[].task_id` | Approval task ID; used in pair with `instance_code` |

If you need to first confirm the form, nodes, or approval flow progress, you can continue to view the instance details:

```bash
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user
```

<a id="使用建议"></a>
## Usage Recommendations

- **`instance_code` and `task_id` must be used in pair**: having only the instance ID or only the task ID is not sufficient to accurately perform the rejection operation.
- **Prefer to get parameters from the pending list of `tasks query`**: especially pending approvals of `topic=1`, which are most suitable as the input source for reject.
- **First check whether API operations are supported**: if the `tasks[].support_api_operate` returned by `tasks query` in the previous step is `false`, it means the task may not support approve/reject via API.
- **For `comment`, it is recommended to clearly state the rejection reason**: e.g. `拒绝，缺少合同附件`, `拒绝，预算字段填写不完整`. This helps the initiator understand the reason and supplement materials.
- **`--dry-run` first, then execute**: especially when processing in batches or when the task source is unclear, previewing first is safer.
