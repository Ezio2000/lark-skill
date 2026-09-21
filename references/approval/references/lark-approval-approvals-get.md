
# approval approvals get

Get details of a single approval definition (user-level read-only operation). Suitable for confirming the approval name, form control structure, option value ranges, and process node information before initiating an approval instance.

Required scopes: ["approval:approval:read"]

<a id="命令"></a>
## Command

```bash
# Query approval definition details by approval_code
lark-cli approval approvals get --params '{"approval_code":"<APPROVAL_CODE>"}' --as user

# Table format output for quick browsing of top-level fields
lark-cli approval approvals get --params '{"approval_code":"<APPROVAL_CODE>"}' --format table --as user

# Preview the API call without executing
lark-cli approval approvals get --params '{"approval_code":"<APPROVAL_CODE>"}' --as user --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--params '{...}'` | Yes | Query parameters, passed in as JSON |
| `approval_code` | Yes | Approval definition Code; usually comes from the result of `approval approvals search` |
| `locale` | No | Return language, e.g. `zh-CN`, `en-US`, `ja-JP` |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval definition details are usually read according to the current user's visibility scope |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call without executing |

<a id="常见输入来源"></a>
## Common Input Sources

If you already have `approval_code`, you can query directly:

```bash
lark-cli approval approvals get --params '{"approval_code":"<APPROVAL_CODE>"}' --as user
```

If you do not yet have `approval_code`, first search for initiable approval definitions:

```bash
lark-cli approval approvals search --data '{"keyword":"请假"}' --as user
```

<a id="输出重点字段"></a>
## Key Output Fields

In the returned result, prioritize the following fields:

| Field | Description |
|------|------|
| `approval_code` | Approval definition Code |
| `approval_name` | Approval definition name; confirm whether it is the form the user wants to initiate |
| `form` | Form definition snapshot; used to identify controls `id`, `type`, option value ranges, and detail sub-control structures |
| `node_list` | Process node list; used to identify node keys, whether approvers need to be supplemented, and whether multiple approvers are allowed |

<a id="form-的使用重点"></a>
## Key Points for Using form

The most important role of `form` is to help the agent **identify how to assemble `instances.create.data.form`**, rather than submitting it directly as-is.

Focus on:

| Field / Structure | Description |
|------|------|
| `form[].id` | Control ID; must be used when creating an instance later |
| `form[].type` | Control type, e.g. `input`, `date`, `radio`, `checkbox`, `fieldList` |
| `form[].value` / option definitions | Used to identify selectable value ranges, default values, or option values |
| Detail / sub-control structure | Used to identify the sub-field structure of complex controls such as `fieldList` and control groups |

**Note: `approvals.get.form` is not a payload template that `instances.create` can directly reuse.** It is a "definition snapshot", mainly used to identify field structures and option value ranges.

<a id="node_list-的使用重点"></a>
## Key Points for Using node_list

`node_list` is mainly used to subsequently decide whether to supplement `node_approver_list` / `node_cc_list`.

Focus on:

| Field | Description |
|------|------|
| `node_list[].custom_node_id` | Custom node identifier; prioritize as the key when supplementing node parameters later |
| `node_list[].node_id` | Node ID; if there is no `custom_node_id`, usually fall back to using it as the key |
| `node_list[].need_approver` | Whether the initiator is required to supplement approvers |
| `node_list[].approver_chosen_multi` | Whether multiple approvers can be selected for this node |

<a id="使用建议"></a>
## Usage Recommendations

- **This is a necessary read-only step before initiating a native approval instance.** It is recommended to always follow: `approvals search` -> `approvals get` -> `instances create`.
- **If the user has already explicitly provided `approval_code`, use this command directly.** No need to go through `approvals search` again.
- **First confirm `approval_name`.** Avoid confusing approval definitions with similar names.
- **First use `form` to identify the control structure, then assemble the creation payload.** Do not guess control `id`, `type`, or option values without looking at the details.
- **First use `node_list` to see whether approvers need to be supplemented.** If a node has `need_approver=true`, you usually need to supplement `node_approver_list` when creating an instance.
- **For the key of `node_list`, prioritize `custom_node_id`.** If it does not exist, then use `node_id`.
- **When `approver_chosen_multi=false`, a node usually can only have one approver supplemented.**

<a id="输出与后续操作"></a>
## Output and Follow-up Operations

After reading the definition details, common next steps:

```bash
# Initiate a native approval instance
lark-cli approval instances create --data '{"approval_code":"<APPROVAL_CODE>","form":"[...]"}' --as user --yes
```

If you need to further understand control values and node parameters, prioritize referring to:

- `lark-approval-instance-form-control-parameters.md`
- `lark-approval-instance-value-sourcing.md`
- `lark-approval-initiate.md`

<a id="结果整理方式"></a>
## How to Organize Results

**Organize the results into "approval definition overview + form structure summary + node requirements summary".**

It is recommended to output in the following structure:

```text
Approval definition: Leave Request
approval_code: 7C468A54-8745-2245-9675-08B7C63E7A85

Form control summary:
- leave_type: radio, selectable values [annual_leave, sick_leave]
- reason: textarea
- start_end: dateInterval

Node requirements summary:
- manager_node: need_approver=true, approver_chosen_multi=false
- hr_node: need_approver=false
```
