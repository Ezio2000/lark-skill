
# approval tasks approve

Approve an approval task (user-level write operation). Typically, first obtain `tasks query` and `task_id` via `instance_code`, then if necessary use `instances get` to view details, and then perform the approval.

> [!CAUTION]
> This is a **high-risk-write** write operation. It is recommended to preview first with `--dry-run`; when actually executing, if the user has explicitly agreed to the approval and the target task is correct, then run with `--yes`. Do not silently append `--yes` without the user's explicit consent.

Required scopes: ["approval:task:write"]

<a id="命令"></a>
## Command

```bash
# Preview the request first without actually executing
lark-cli approval tasks approve \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","comment":"同意"}' \
  --as user \
  --dry-run

# Approve the approval task and attach an approval comment
lark-cli approval tasks approve \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","comment":"同意"}' \
  --as user \
  --yes

# When form backfilling is needed, pass form (per the current command definition, form is a stringified JSON)
lark-cli approval tasks approve \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","comment":"同意并补充信息","form":"[{\"id\":\"user_name\",\"type\":\"input\",\"value\":\"Alice\"}]"}' \
  --as user \
  --yes

# Pass the request body via a file, suitable for longer comment / form
lark-cli approval tasks approve \
  --data @./approve-body.json \
  --as user \
  --yes
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--data '{...}'` | Yes | Request body JSON, passed using JSON |
| `instance_code` | Yes | Approval instance Code; typically obtained first via `tasks query` or `instances initiated` / `instances get` |
| `task_id` | Yes | Approval task ID; typically obtained first via `tasks query` |
| `comment` | No | Approval comment, e.g. `同意`, `已确认` |
| `form` | No | Form data; per the current command definition, the field type is `string`, typically passed as stringified JSON; only used when the approval action needs to backfill the form at the same time |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval approval usually must be executed as a user |
| `--yes` | No | Confirm execution of a high-risk write operation; if not provided, may return `confirmation_required` / exit 10 |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call without executing |

<a id="典型前置步骤"></a>
## Typical Prerequisite Steps

First find the pending task:

```bash
lark-cli approval tasks query --params '{"topic":"1"}' --as user
```

Two commonly used fields:

| Field | Description |
|------|------|
| `tasks[].instance_code` | Approval instance Code; usually required when performing operations such as approve / reject / rollback |
| `tasks[].task_id` | Approval task ID; used in pair with `instance_code` |

If you need to first confirm the form, nodes, or approval flow progress, you can continue to view the instance details:

```bash
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user
```

<a id="使用建议"></a>
## Usage Recommendations

- **`instance_code` and `task_id` must be used in pair**: having only the instance ID or only the task ID is not enough to accurately perform the approval operation.
- **Prefer to get parameters from the pending list of `tasks query`**: especially pending approvals of `topic=1`, which are most suitable as the input source for approve.
- **First check whether API operations are supported**: if the `tasks[].support_api_operate` returned by `tasks query` in the previous step is `false`, it means the task may not support approval/rejection via API.
- **`comment` should be concise and clear**: for example `同意`, `同意，信息已核对`. It can be omitted when there is no approval comment requirement.
- **Only pass `form` when truly needed**: in most simple approval scenarios, passing only `instance_code`, `task_id`, and optionally `comment` is sufficient.
- **`--dry-run` first, then execute**: especially when batch processing, form backfilling, or the task source is unclear, previewing first is safer.
