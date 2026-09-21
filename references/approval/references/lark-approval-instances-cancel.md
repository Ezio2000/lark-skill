
# approval instances cancel

Withdraw an approval instance that has already been initiated (user-level write operation). Typically, first confirm the target approval instance via `instances initiated`, `tasks query`, or `instances get`, obtain `instance_code`, and then perform the withdrawal.

> [!CAUTION]
> This is a **high-risk-write** write operation. It is recommended to preview first with `--dry-run`; when actually executing, if the user has explicitly requested to withdraw the approval instance and the target instance is correct, then run with `--yes`. Do not silently append `--yes` without the user's explicit consent.

Required scopes: ["approval:instance:write"]

<a id="命令"></a>
## Command

```bash
# Preview the request first without actually executing
lark-cli approval instances cancel \
  --data '{"instance_code":"<INSTANCE_CODE>"}' \
  --as user \
  --dry-run

# Withdraw an approval instance
lark-cli approval instances cancel \
  --data '{"instance_code":"<INSTANCE_CODE>"}' \
  --as user \
  --yes

# Pass the request body via a file
lark-cli approval instances cancel \
  --data @./cancel-body.json \
  --as user \
  --yes
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--data '{...}'` | Yes | Request body JSON, passed using JSON |
| `instance_code` | Yes | Approval instance Code; typically obtained first via `instances initiated`, `tasks query`, or `instances get` |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval instance withdrawal usually must be executed as a user |
| `--yes` | No | Confirm execution of a high-risk write operation; if omitted, may return `confirmation_required` / exit 10 |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call without executing |

<a id="典型前置步骤"></a>
## Typical Prerequisite Steps

If you are looking for "approval instances I initiated", you can first query the initiated list:

```bash
lark-cli approval instances initiated --params '{"page_size":20}' --as user
```

If you have already located an approval in the task list, you can also get the instance Code from the task:

```bash
lark-cli approval tasks query --params '{"topic":"1"}' --as user
```

Commonly used fields:

| Field | Description |
|------|------|
| `instances[].instance_code` | Approval instance Code; must be provided when withdrawing |
| `tasks[].instance_code` | The approval instance Code associated with the approval task; can also be used as withdrawal input |
| `tasks[].instance_status` | Approval instance status; can be used to determine whether it is still in a withdrawable stage |

If you need to first confirm the approval form, current node, or flow status, you can continue to view the instance details:

```bash
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user
```

<a id="使用建议"></a>
## Usage Recommendations

- **What is withdrawn is the approval instance, not a single task**: `instances cancel` only requires `instance_code`, not `task_id`.
- **First confirm whether the instance can still be withdrawn**: Instances that have already been approved, rejected, revoked, or terminated are usually not suitable for further withdrawal.
- **Prefer obtaining the target instance from `instances initiated`**: Because withdrawal usually targets "approvals I initiated", this entry point is the most direct.
- **You can also look up `instance_code` from `tasks query`**: This is more convenient when you enter from the context of a pending/completed task.
- **`--dry-run` first, then execute**: Especially when the instance source is unclear, the user only provided a title keyword, or multiple instances need to be verified at once, previewing first is safer.
