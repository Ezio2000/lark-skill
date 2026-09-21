# Approvals

Use explicit `--as user`. Approval todos are not ordinary [Tasks](../task/index.md). Route approval definitions, instances, forms, approval/rejection, transfer, rollback, cancellation, reminders, additional signers, and CC here.

## Operation routing

All commands below follow `lark-cli approval`. Read the selected reference for exact fields.

| Intent | Command | Reference |
|---|---|---|
| Find definitions | `approvals search` | [Search](references/lark-approval-approvals-search.md) |
| Inspect form and workflow before submission | `approvals get` | [Definition](references/lark-approval-approvals-get.md) |
| Submit a native approval | `instances create` | [Initiate](references/lark-approval-initiate.md) |
| Pending/completed/read/unread items | `tasks query` | [Query](references/lark-approval-tasks-query.md) |
| Form, progress, or current node | `instances get` | [Instance](references/lark-approval-instances-get.md) |
| Approve | `tasks approve` | [Approve](references/lark-approval-tasks-approve.md) |
| Reject | `tasks reject` | [Reject](references/lark-approval-tasks-reject.md) |
| Transfer | `tasks transfer` | [Transfer](references/lark-approval-tasks-transfer.md) |
| Add signers | `tasks add_sign` | [Signers](references/lark-approval-tasks-add-sign.md) |
| Roll back | `tasks rollback` | [Rollback](references/lark-approval-tasks-rollback.md) |
| Remind | `tasks remind` | [Remind](references/lark-approval-tasks-remind.md) |
| Cancel a submitted instance | `instances cancel` | [Cancel](references/lark-approval-instances-cancel.md) |
| Add CC | `instances cc` | [CC](references/lark-approval-instances-cc.md) |
| Find submitted instances | `instances initiated` | [Initiated](references/lark-approval-instances-initiated.md) |

## Execution

- Submission usually needs definition search → definition/form inspection → instance creation. Creating approval definitions belongs in the client/admin console. For third-party definitions, return the supplied `create_link`.
- Processing an existing task requires the paired `instance_code` and `task_id`. Reuse known IDs and fresh query results. Query `tasks` only when needed; fetch instance details when the user needs them or they are necessary to decide the requested action.
- `tasks query` topics: `1` pending, `2` completed, `17` unread, `18` read.
- Error `1395001` indicates changed task state, failed write preconditions, or lost eligibility. Do not repeatedly submit. At most one state query and one corrected retry are appropriate when the response indicates recovery is possible; otherwise report the restriction.
- Existing authorization for a specific task action remains valid. A query alone does not authorize approving or rejecting it.

```sh
lark-cli approval tasks query --params '{"topic":"1"}' --as user
lark-cli approval tasks approve --data '{"instance_code":"<instance_code>","task_id":"<task_id>","comment":"<comment>"}' --as user
```
