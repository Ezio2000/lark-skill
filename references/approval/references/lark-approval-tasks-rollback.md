
# approval tasks rollback

Roll back an approval task to a specified node (user-level write operation). Typically, first obtain `tasks query` to get `task_id` and `instance_code`, then confirm the target node `node_ids` that can be rolled back to by combining with the instance details, and finally execute the rollback.

> [!CAUTION]
> This is a **high-risk-write** write operation. It is recommended to preview first with `--dry-run`; when actually executing, if the user has explicitly requested to roll back this approval and the target task and rollback node are both correct, then run with `--yes`. Do not silently append `--yes` without the user's explicit consent.

Required scopes: ["approval:task:write"]

<a id="命令"></a>
## Command

```bash
# Preview the request first, without actually executing
lark-cli approval tasks rollback \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","node_ids":["<NODE_ID>"],"comment":"退回补充材料"}' \
  --as user \
  --dry-run

# Roll back to a single node
lark-cli approval tasks rollback \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","node_ids":["<NODE_ID>"],"comment":"请补充附件后重新提交"}' \
  --as user \
  --yes

# Roll back to the initiator node (the initiator node ID is START)
lark-cli approval tasks rollback \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","node_ids":["START"],"comment":"退回发起人补充材料"}' \
  --as user \
  --yes

# Pass multiple candidate node IDs (subject to what the actual approval definition supports)
lark-cli approval tasks rollback \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","node_ids":["<NODE_ID_1>","<NODE_ID_2>"],"comment":"退回上一处理节点"}' \
  --as user \
  --yes

# Pass the request body via a file, suitable for longer comments or more node_ids
lark-cli approval tasks rollback \
  --data @./rollback-body.json \
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
| `node_ids` | Yes | Array of target node IDs to roll back to; the initiator node ID is `START`; before executing, first confirm that these nodes can indeed serve as rollback targets |
| `comment` | No | Approval comment or rollback explanation, e.g. `请补充附件后重新提交`, `预算说明不完整，请补充` |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval rollback usually must be executed as a user |
| `--yes` | No | Confirm execution of a high-risk write operation; if not provided, may return `confirmation_required` / exit 10 |
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
| `tasks[].instance_code` | Approval instance Code; usually required when executing operations such as approve / reject / transfer / rollback |
| `tasks[].task_id` | Approval task ID; used in pair with `instance_code` |
| `tasks[].support_api_operate` | Whether the task supports processing via API; it is recommended to check before rolling back |

To confirm the process nodes, current progress, and rollback positions, you can first view the instance details:

```bash
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user
```

<a id="使用建议"></a>
## Usage Recommendations

- **`instance_code` and `task_id` must be used in pair**: having only the instance ID or only the task ID is not enough to accurately execute the rollback operation.
- **`node_ids` is required**: rollback is not "automatically roll back to the previous step"; you must explicitly provide the target node ID array; when rolling back to the initiator node, pass `START`.
- **First confirm whether the node can be rolled back to**: different approval definitions may support different rollback targets; when uncertain, first verify via `instances get` or the business-side process information.
- **Prefer obtaining task parameters from the `tasks query` pending list**: especially pending approvals from `topic=1`, which are most suitable as the input source for rollback.
- **First check whether API operations are supported**: if `tasks[].support_api_operate` is `false`, it means the task may not support executing processing actions via API, and rollback should be carefully verified beforehand.
- **`comment` should clearly state the rollback reason**: e.g. `附件缺失，请补齐后重新提交`, `费用说明不完整，请补充明细`, so that the initiator or the previous processor can understand the reason.
- **`--dry-run` first, then execute**: especially when the node source is unclear, the approval chain is complex, or processing in batches, previewing first is safer.
