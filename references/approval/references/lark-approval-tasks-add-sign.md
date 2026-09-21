
# approval tasks add_sign

Add a signer to an approval task (user-level write operation). Typically, first obtain `tasks query` and `task_id` via `instance_code`, confirm the target task, then provide the user ID of the added signer, the add-sign method, and other parameters to perform the add-sign.

> [!CAUTION]
> This is a **high-risk-write** write operation. It is recommended to preview first with `--dry-run`; when actually executing, if the user has clearly requested to add a signer to this approval task and the target task, add-sign target, and add-sign method are all correct, then run with `--yes`. When the user has clearly requested immediate execution and has listed the add-sign and transfer targets for this round, that confirmation covers these two already-specified actions; do not repeatedly ask about each one; do not silently add `--yes` without the user's explicit consent.

Required scopes: ["approval:task:write"]

<a id="先选择加签类型"></a>
## First choose the add-sign type

`add_sign_type` affects whether the current user's approval task remains actionable, so you cannot simply follow the example order or choose arbitrarily:

| User intent | `add_sign_type` | Handling |
|----------|-----------------|----------|
| Explicitly says pre-add-sign / "let someone review first, then I review" | `1` | Pre-add-sign, and choose `approval_method` as requested by the user |
| Explicitly says post-add-sign / "after I handle it, let someone review" | `2` | Post-add-sign, and choose `approval_method` as requested by the user |
| "Pull them in to review together" / "joint review" / "confirm together" | `3` | Parallel add-sign; do not pass `approval_method` |
| The same request requires adding a signer first, then transferring the current user's step | `3` | **Must use parallel add-sign**; after the add-sign succeeds, then transfer the current task |

Pre-add-sign or post-add-sign may advance the current user's task, making the original `task_id` no longer support subsequent transfer. Therefore, "add a signer first, then transfer my step to someone else" cannot use pre-add-sign or post-add-sign; first use `add_sign_type: 3` for parallel add-sign, and after confirming `tasks add_sign` succeeds, use the same set of `instance_code` + `task_id` to execute `tasks transfer`.

Only ask the user a second time when the context makes it completely impossible to determine which add-sign method is intended and different choices would change the approval flow. When the user has already said "review together" or has already requested "add a signer then transfer the current step," the information is sufficient; do not ask again about the add-sign type.

<a id="再选择-approval_method"></a>
## Then choose approval_method

Only pre-add-sign and post-add-sign require `approval_method`; parallel add-sign does not pass it. First follow the approval method explicitly specified by the user; when the user has not specified one, choose based on the number of people and the semantics:

| Number of added signers and semantics | `approval_method` | Handling |
|----------------|-------------------|----------|
| Only 1 added signer | `1` | Use or-sign; with a single person, or-sign and all-sign have the same practical effect, so do not ask again |
| Multiple people, explicitly "any one approval is enough" / "one approval suffices" | `1` | Or-sign; any one added signer completing the approval is enough |
| Multiple people, explicitly "everyone must approve" / "all confirm" | `2` | All-sign; all added signers must complete the approval |
| Multiple people, explicitly "sequential approval" / "A first, then B" | `3` | Sequential approval; each person approves one by one in the array order of `add_sign_user_ids` |
| Multiple people, cannot be inferred from context | Do not preset | Ask the user to choose or-sign, all-sign, or sequential approval, and explain the effects of the three |

Sequential approval must preserve the personnel order given by the user. If sequential approval has been determined, but the context cannot determine the order, first ask for the personnel order, then construct `add_sign_user_ids`; do not sort on your own.

<a id="命令"></a>
## Command

```bash
# Preview the add-sign request first, without actually executing it
lark-cli approval tasks add_sign \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","add_sign_type":3,"add_sign_user_ids":["ou_xxx"],"comment":"请项目 owner 一起审核"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --dry-run

# Single-person pre-add-sign: use or-sign when no method is specified
lark-cli approval tasks add_sign \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","add_sign_type":1,"add_sign_user_ids":["ou_xxx"],"approval_method":1,"comment":"请先补充审核"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --yes

# Multi-person post-add-sign: everyone needs to approve, use all-sign
lark-cli approval tasks add_sign \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","add_sign_type":2,"add_sign_user_ids":["ou_xxx","ou_yyy"],"approval_method":2,"comment":"当前审批完成后请两位都完成审核"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --yes

# Multi-person pre-add-sign: approve sequentially in the order of the people in the array
lark-cli approval tasks add_sign \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","add_sign_type":1,"add_sign_user_ids":["ou_first","ou_second"],"approval_method":3,"comment":"请先由第一位审核，再由第二位审核"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --yes

# The same request requires adding a signer first, then transferring: must use parallel add-sign; execute the two commands in order
lark-cli approval tasks add_sign \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","add_sign_type":3,"add_sign_user_ids":["ou_reviewer"],"comment":"请一起审核"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --yes

# Only after the above add_sign succeeds, transfer the same current task
lark-cli approval tasks transfer \
  --data '{"instance_code":"<INSTANCE_CODE>","task_id":"<TASK_ID>","transfer_user_id":"ou_transferee","comment":"出差期间请代为处理"}' \
  --params '{"user_id_type":"open_id"}' \
  --as user \
  --yes

# Pass the request body via a file, suitable for longer comments or more added signers
lark-cli approval tasks add_sign \
  --data @./add-sign-body.json \
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
| `add_sign_type` | Yes | Add-sign type: `1` pre-add-sign, `2` post-add-sign, `3` parallel add-sign |
| `add_sign_user_ids` | Yes | Array of added signer IDs; must be consistent with `user_id_type` |
| `approval_method` | No | Approval method: `1` or-sign, `2` all-sign, `3` sequential approval; **only required for pre-add-sign and post-add-sign**. Use `1` for a single person when unspecified; ask the user first when multiple people cannot be inferred from semantics |
| `comment` | No | Approval comment or add-sign note, for example `前加签给财务复核`, `请项目 owner 一并确认` |
| `--params '{"user_id_type":"..."}'` | No | Query parameter JSON; used to declare the type of user IDs in `add_sign_user_ids` |
| `user_id_type` | No | User ID type: `user_id`, `union_id`, `open_id`; when not explicitly specified, pay special attention to confirming the ID type of the added signer |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval add-sign usually must be executed as a user |
| `--yes` | No | Confirm execution of a high-risk write operation; if not provided, may return `confirmation_required` / exit 10 |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call without executing |

<a id="枚举说明"></a>
## Enum descriptions

### add_sign_type

| Value | Meaning | Impact on the current task |
|----|------|------------------|
| `1` | Pre-add-sign | Insert an approver before the current approval, which may advance the current user's task |
| `2` | Post-add-sign | Append an approver after the current approval, which may advance the current user's task |
| `3` | Parallel add-sign | Add a parallel approver; use when the current step needs to be transferred afterward |

### approval_method

Only applies to pre-add-sign and post-add-sign; parallel add-sign does not pass it.

| Value | Meaning | Completion condition |
|----|------|----------|
| `1` | Or-sign | Any one added signer completing the approval is enough |
| `2` | All-sign | All added signers must complete the approval |
| `3` | Sequential approval | All added signers approve one by one in the array order of `add_sign_user_ids` |

<a id="典型前置步骤"></a>
## Typical prerequisite steps

First look up the pending task:

```bash
lark-cli approval tasks query --params '{"topic":"1"}' --as user
```

Commonly used fields:

| Field | Description |
|------|------|
| `tasks[].instance_code` | Approval instance Code; usually required when performing operations such as approve / reject / transfer / rollback / add_sign |
| `tasks[].task_id` | Approval task ID; used in pair with `instance_code` |
| `tasks[].support_api_operate` | Whether the task supports handling via API; it is recommended to check before add-sign |

If you only have a name or email, it is recommended to first resolve the correct user ID via contact capabilities, then perform the add-sign.

If you need to first confirm the form, nodes, or approval flow progress, you can continue to view the instance details:

```bash
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user
```

<a id="使用建议"></a>
## Usage recommendations

- **`instance_code` and `task_id` must be used in pair**: having only the instance ID or only the task ID is not enough to accurately perform the add-sign operation.
- **`add_sign_user_ids` and `user_id_type` must match**: for example, if passing open_id, set `user_id_type` to `open_id`; do not mix them.
- **Prefer to explicitly pass `user_id_type`**: this makes it easier for the agent to determine the meaning of the parameters and also reduces failures caused by ID type mismatches.
- **`add_sign_type` must be consistent with the business intent**: pre-add-sign inserts an approver before the current approval, post-add-sign appends an approver after the current approval, and parallel add-sign adds a parallel approver.
- **When the current step must be transferred after add-sign, parallel add-sign must be used**: use `add_sign_type: 3`, wait for the add-sign to succeed, then transfer using the same set of task parameters; do not use pre-add-sign or post-add-sign, which would cause the current task to advance prematurely.
- **Only ask when the type cannot be inferred**: if the user has not stated the sequential or parallel relationship, and subsequent actions cannot help determine it either, then ask the user to choose; do not repeatedly ask about "review together" or "add-sign then transfer."
- **Pre-add-sign / post-add-sign must include `approval_method`**: use or-sign for a single person when unspecified; for multiple people, prefer choosing based on semantics, and ask the user when it cannot be inferred; do not silently default.
- **Sequential approval preserves the personnel order**: construct `add_sign_user_ids` in the order specified by the user; if the order is unclear, ask first and do not sort on your own.
- **Prefer to get task parameters from the pending list of `tasks query`**: especially pending approvals of `topic=1`, which are most suitable as the input source for add_sign.
- **First check whether API operations are supported**: if `tasks[].support_api_operate` is `false`, it means the task may not support handling actions via API, and you should verify carefully before add-sign.
- **For `comment`, it is recommended to state the reason for add-sign**: for example `增加财务复核`, `增加项目 owner 并行确认`, to help relevant personnel understand the context.
- **`--dry-run` first, then execute**: especially for multi-person add-sign, cross-department add-sign, or when the source of the add-sign target is unclear, previewing first is safer.
