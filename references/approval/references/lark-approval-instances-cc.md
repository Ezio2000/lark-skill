
# approval instances cc

Add cc recipients to an approval instance (user-level write operation). Typically, first confirm the target approval instance via `instances initiated`, `tasks query`, or `instances get`, obtain the `instance_code`, then provide the cc recipient's user ID to perform the cc.

> [!CAUTION]
> This is a **high-risk-write** operation. It is recommended to preview first with `--dry-run`; when actually executing, if the user has explicitly requested to cc this approval instance and both the target instance and cc recipients are correct, then run with `--yes`. Do not silently append `--yes` without the user's explicit consent.

Required scopes: ["approval:instance:write"]

<a id="命令"></a>
## Command

```bash
# Preview the request first, without actually executing
lark-cli approval instances cc \
  --data '{"instance_code":"<INSTANCE_CODE>","cc_user_ids":["ou_xxx"],"comment":"抄送给项目 owner 了解进展"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --dry-run

# CC one person by open_id
lark-cli approval instances cc \
  --data '{"instance_code":"<INSTANCE_CODE>","cc_user_ids":["ou_xxx"],"comment":"抄送给你知悉"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --yes

# CC multiple people at once
lark-cli approval instances cc \
  --data '{"instance_code":"<INSTANCE_CODE>","cc_user_ids":["ou_xxx","ou_yyy"],"comment":"请相关同学同步关注"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --yes

# CC by user_id
lark-cli approval instances cc \
  --data '{"instance_code":"<INSTANCE_CODE>","cc_user_ids":["123456789"],"comment":"抄送给财务负责人"}' \
  --params '{"user_id_type":"user_id"}' \
  --as user \
  --yes

# Pass the request body via a file
lark-cli approval instances cc \
  --data @./cc-body.json \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --yes
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--data '{...}'` | Yes | Request body JSON, passed as JSON |
| `instance_code` | Yes | Approval instance Code; typically obtained first via `instances initiated`, `tasks query`, or `instances get` |
| `cc_user_ids` | Yes | Array of cc recipients' user IDs; must be consistent with `user_id_type` |
| `comment` | No | CC message, e.g. `抄送给你知悉`, `请同步关注该审批进展` |
| `--params '{"user_id_type":"..."}'` | No | Query parameter JSON; used to declare the type of user IDs in `cc_user_ids` |
| `user_id_type` | No | User ID type: `user_id`, `union_id`, `open_id`; when not explicitly specified, be especially sure to confirm the cc recipient's ID type |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval instance cc must usually be performed as a user |
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
| `instances[].instance_code` | Approval instance Code; must be provided when cc'ing |
| `tasks[].instance_code` | The approval instance Code associated with the approval task; can also be used as cc input |
| `tasks[].title` | Task title, can be used to confirm whether it is the approval you want to operate on |
| `tasks[].instance_status` | Approval instance status; can be used to determine whether the current approval is still in progress |

If you only have a name or email, it is recommended to first resolve the correct user ID via the contacts capability, then perform the cc.

If you need to first confirm the approval form, current node, or flow status, you can continue to view the instance details:

```bash
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user
```

<a id="使用建议"></a>
## Usage Recommendations

- **What is cc'd is the approval instance, not a single task**: `instances cc` only needs `instance_code`, not `task_id`.
- **`cc_user_ids` and `user_id_type` must match**: for example, if passing open_id, set `user_id_type` to `open_id`; do not mix them.
- **`cc_user_ids` is an array**: even if cc'ing only one person, it must be passed as an array.
- **Prefer explicitly passing `user_id_type`**: this makes it easier for the agent to determine the meaning of the parameters and also reduces failures caused by ID type mismatches.
- **Prefer obtaining the target instance from `instances initiated`**: because cc'ing is common in the "approvals I initiated" scenario, and this entry point is the most direct.
- **You can also look up `instance_code` from `tasks query`**: when you enter from a certain approval context, this is more convenient.
- **`comment` should be concise and clear**: for example, `抄送给你知悉`, `请同步关注审批进展`. Avoid overly long or vague descriptions.
- **`--dry-run` first, then execute**: especially when there are many cc recipients, the source of cc recipients is unclear, or the user needs to first verify the instance title, previewing first is safer.
