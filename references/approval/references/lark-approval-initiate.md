<a id="审批提单工作流"></a>
# Approval Instance Submission Workflow

<a id="执行摘要"></a>
## Executive Summary

- **For native approval instance submission, if the user does not explicitly provide `approval_code`, you must follow the fixed path `approvals search` -> `approvals get` -> `instances create`** Do not skip `get` and directly construct the request.
- **For native approval instance submission, if the user explicitly provides `approval_code`, follow the fixed path `approvals get` -> `instances create`** Do not skip `get` and directly construct the request.
- **The definition of `is_external=true` is a third-party definition.** Do not call `instances create` for such definitions; prefer using `create_link`.
- **All personnel-type parameters use `open_id` by default.** If the user provides a name, email, or other identity, first resolve it using [`../../contact/index.md`](../../contact/index.md).
- **First read the control parameter reference and the value source reference, then read the creation parameter rules in this document.** Before submitting, you must first read [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md) and [`lark-approval-instance-value-sourcing.md`](./lark-approval-instance-value-sourcing.md).
- **`approvals.get.form` is not a verbatim template for the creation payload.** It is mainly used to identify control `id`, `type`, option value ranges, and detail sub-control structures; in the actual `instances create --data.form`, the control `value` structure is governed by [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md).
- **Node parameters are only taken from `node_list` and the node parameter rules in this document.** Node keys must come from the node identifiers returned by the definition detail; when passing user IDs in the approver/cc list, do not mix in names or other identity identifiers.
- **Seeing `need_approver=true` indicates that the node requires the initiator to supplement approvers.** If `approver_chosen_multi=false`, the node allows only one `open_id`.
- **Confirm before creating the instance.** `approval instances create` is a write operation; before executing, have the user confirm the final definition, form values, and node parameters; when actually executing, explicitly pass `--yes`.

<a id="适用场景"></a>
## Applicable Scenarios

- "Help me submit a leave approval"
- "Help me initiate a reimbursement approval"
- "I want to submit a business trip approval"
- "First search for submittable approvals, then help me submit the instance"

<a id="严禁行为"></a>
## Strictly Prohibited Actions

- **Strictly prohibited to directly submit an instance without first reading the creation parameter rules in this document, [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md), and [`lark-approval-instance-value-sourcing.md`](./lark-approval-instance-value-sourcing.md).**
- **Strictly prohibited to skip `approvals.get`.** Before obtaining `form` and `node_list`, do not call `instances create`.
- **Strictly prohibited to write names directly into `node_approver_list`, `node_cc_list`, or form personnel controls.** They must first be converted to `open_id`.
- **Strictly prohibited to call `instances create` for third-party definitions.**
- **Strictly prohibited to force-submit instances for controls not supported by the API.** If the target definition contains controls not supported by the create instance API, you should clearly tell the user that the definition cannot be fully initiated through the API alone.
- **Strictly prohibited to treat `approvals.get.form` as a verbatim template that can be submitted directly.**
- **Strictly prohibited to directly execute a real instance submission without user confirmation.**

<a id="工作流"></a>
## Workflow

<a id="1-搜索可发起审批定义"></a>
### 1. Search for Submittable Approval Definitions

First search for definitions:

```bash
lark-cli approval approvals search --data '{"keyword":"请假"}'
```

Handling rules:

- If the result is empty, tell the user that there are no submittable definitions under the current keyword.
- If multiple definitions are matched, you must list the candidates for the user to choose; do not guess on your own.
- If the target definition `is_external=true`, preferentially return `create_link`, explaining that this is a third-party definition and cannot go through native `instances create`.
- Only native definitions with `is_external=false` proceed to the next step.

<a id="2-获取审批定义详情"></a>
### 2. Get Approval Definition Details

After obtaining `approval_code`, read the definition details:

```bash
lark-cli approval approvals get \
  --params '{"approval_code":"7C468A54-8745-2245-9675-08B7C63E7A85"}'
```

Focus on the returned:

- `approval_name`: which approval definition is currently being initiated.
- `form`: form definition snapshot, used to identify control `id`, `type`, option value ranges, and detail sub-control structures; it is not a payload template that can be submitted verbatim when creating an instance.
- `node_list`: process node information, which is the only reliable source for subsequent `node_approver_list` / `node_cc_list`.

<a id="3-创建请求参数速查"></a>
### 3. Create Request Parameters Quick Reference

Input parameters are as follows:

| Parameter | Required | Description |
|---|---|---|
| `--data '{...}'` | Yes | Request body, passed in as JSON |
| `approval_code` | Yes | Approval definition Code; must first be confirmed via `approvals search` / `approvals get` |
| `form` | No | Form values, **JSON array string**, not a plain object; not required at the API layer, but must be passed when the approval definition has required controls or the user needs to submit form values |
| `node_approver_list` | No | Node approver list; only pass when the definition requires supplementing approvers |
| `node_cc_list` | No | Node cc list; only pass when the user explicitly needs to supplement node cc recipients |
| `uuid` | No | Idempotency identifier; recommended to explicitly pass when retrying the same request |
| `--as user` | No | Recommended to explicitly specify user identity; approval initiation should typically use user identity |
| `--yes` | Yes | Write operation confirmation; must be explicitly passed when actually executing |
| `--dry-run` | No | Preview API call, does not execute |

<a id="4-组装-form"></a>
### 4. Assemble `form`

`instances create --data.form` is an optional field; when passed, it must be a JSON array string. Approvals with no form or no need to fill in form values may omit `form`, but as long as the approval definition contains controls that need to be submitted, they must be assembled according to the control structure and passed. Assembly principles:

- First use `approvals.get.form` to identify which controls exist, each control's `id` / `type` / optional value ranges, then reassemble the creation payload according to the creation parameter rules in this document and [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md).
- When submitting, you must at least ensure that each control's `id`, `type`, and `value` conform to the current interface requirements; do not assume that other fields appearing in the definition snapshot can all be copied directly.
- If the user provides personnel information, preferentially convert it to `open_id` before writing it into the corresponding control.
- Single-select/multi-select controls submit the option `value`, which can be obtained from the option definitions in `approvals.get.form`.
- The `value` structures of controls such as `contact`, `department`, `fieldList`, `dateInterval`, `amount`, `telephone`, `document` are all different and must be assembled separately according to [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md); do not apply the text control pattern.
- For where the value itself comes from, preferentially handle according to [`lark-approval-instance-value-sourcing.md`](./lark-approval-instance-value-sourcing.md); do not mistake "knowing the structure" for "already having a submittable value".
- If [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md) indicates that a control does not support submission through the create instance API, do not force-guess a workaround; you should clearly tell the user that the definition currently cannot be submitted through the API alone.
- If you encounter a complex control not explicitly covered by the current skill, do not force-guess; first determine supportability and value-passing structure based on [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md), then confirm with the user.

<a id="api-不支持的控件"></a>
## Controls Not Supported by the API

According to [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md), controls not supported by the create approval instance API include at least:

- `text`
- `mutableGroup`
- `account`
- `serialNumber`
- `tripGroup`
- `apaascorehrOnboardingGroup`
- `apaascorehrRegularateGroup`
- `remedyGroupV2`
- `apaascorehrJobAdjustGroup`
- `apaascorehrOffboardingGroup`

If the target approval definition contains the above controls, do not continue to force-assemble `form`; you should directly tell the user that the definition cannot be fully submitted through the current API alone.

<a id="高频控件速查"></a>
## High-Frequency Controls Quick Reference

Preferentially assemble according to [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md); below only the most commonly used and most error-prone formats are retained:

- `input` / `textarea`: `value` is a string
- `date`: `value` is an RFC3339 time string
- `dateInterval`: `value` is an object, containing `start` / `end` / `interval`
- `radio` / `radioV2`: `value` is a single option value, taken from `option.value` in the definition details; when associating external options, pass `options.id`
- `checkbox` / `checkboxV2`: `value` is an array of option values
- `number`: `value` is a number
- `amount`: `value` is a number, and must also carry `currency`
- `formula`: `value` must match the formula result in the definition, otherwise an error will be reported
- `contact`: only writing `open_ids` is recommended, with personnel information first converted to `open_id`
- `connect`: `value` is an array of associated approval instance `instance_code`, and currently by default requires the user to directly provide `instance_code`
- `document`: `value` is an object, containing at least `token` and `type=docx`
- `attachmentV2` / `image` / `imageV2`: `value` is an array of file codes, and currently by default requires the user to directly provide them
- `fieldList`: `value` is a two-dimensional array, and sub-items continue to be assembled according to their respective control types
- `department`: `value` is an array of objects, with the element field name being `open_id`, whose value is filled with the department's `open_department_id`
- `telephone`: `value` is an object, containing `countryCode` and `nationalNumber`
- `address`: `value` is an array of objects, containing at least the geographic library `id`, and optionally `detailAddress`; currently by default requires the user to directly provide the `id`

<a id="特殊控件组"></a>
## Special Control Groups

[`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md) also explicitly provides the instance submission formats for several special control groups, including at least:

- `leaveGroupV2`
- `workGroup`
- `outGroup`
- `shiftGroup`

Such control groups are not simple text controls; they usually also nest sub-controls such as `radioV2`, `date`, `fieldList`, `image`, `contact`. When encountering these control groups:

- First find the control group and its sub-control IDs from `approvals.get.form`
- Then strictly assemble `value` according to the examples in [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md)
- Do not submit the control group as a whole as a plain string or flat object

<a id="5-组装节点参数"></a>
### 5. Assemble Node Parameters

Derive node parameters from `node_list`:

- If a node `need_approver=true`, then the approvers for that node must be supplemented in `node_approver_list`.
- `key` preferentially takes `custom_node_id`; if it does not exist, then use `node_id`.
- `value` is the approver `open_id` list.
- If `approver_chosen_multi=false`, the node allows only one approver `open_id`.
- `node_cc_list` is filled in only when the user explicitly needs to supplement node cc recipients; its `key/value` rules are the same as `node_approver_list`.

<a id="6-创建审批实例"></a>
### 6. Create Approval Instance

The creation command uses `approval instances create`, required scopes: ["approval:instance:write"]

Execute after confirming the final form values and node parameters:

```bash
lark-cli approval instances create \
  --data '{
    "approval_code":"7C468A54-8745-2245-9675-08B7C63E7A85",
    "form":"[{\"id\":\"widget1\",\"type\":\"input\",\"value\":\"请假半天\"}]",
    "node_approver_list":[
      {
        "key":"manager_node_id",
        "value":["ou_xxx"]
      }
    ]
  }' \
  --as user \
  --yes
```

Execution rules:

- Before executing, first confirm with the user: target approval definition, core form values, node approvers/cc recipients.
- If idempotency is needed, `uuid` may be supplemented.
- After success, report back `instance_code` and `instance_link`.

<a id="组装时优先依据的资料"></a>
## Materials to Prioritize When Assembling

The priority is fixed as follows:

1. The creation request parameters, node parameters, and return result descriptions in this document: determine which fields `instances create` should pass, how to execute, and what to return after success.
2. [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md): determines the `value` structure and support scope of each control type.
3. [`lark-approval-instance-value-sourcing.md`](./lark-approval-instance-value-sourcing.md): determines where each type of value should be obtained from, and which values currently must be directly provided by the user.
4. `approvals.get.form`: provides which controls actually exist in the current approval definition, control `id`, control `type`, option value ranges, and detail sub-control structures.
5. `approvals.get.node_list`: provides clues about node keys and whether approvers/cc recipients need to be supplemented.

Do not reverse the order and treat `approvals.get.form` as the first priority, and even less as a JSON template that can be submitted directly.

<a id="最小判断表"></a>
## Minimal Decision Table

| What you have | Next step |
|---|---|
| Only a colloquial request, such as "help me submit a leave approval" | First `approvals.search` |
| Already obtained `approval_code` | Directly `approvals.get` |
| Already obtained `form` / `node_list`, and the user has provided form values and approvers | Assemble `instances create` |
| `is_external=true` | Return `create_link`, do not call `instances create` |

<a id="返回结果"></a>
## Return Results

After completing creation, at least return to the user:

- `approval_name`
- `instance_code`
- `instance_link`

It is recommended to organize it into the following structure:

```text
Approval created successfully:

- approval_name: Leave Request
- instance_code: 19EAC829-F1CB-527F-BE2A-1330422E60C0
- instance_link: https://...
```
