<a id="审批提单值来源"></a>
# Approval Instance Value Sources

<a id="目的"></a>
## Purpose

This document answers one fixed question: when calling `approval instances create` to create a native approval instance, **where does each value to be filled in come from**.

The reading order is fixed as follows:

1. The create request parameters, node parameters, and return result descriptions in [`lark-approval-initiate.md`](./lark-approval-initiate.md)
2. The `form` / `node_list` returned by `approval approvals get`
3. [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md)
4. This document

<a id="总原则"></a>
## General Principles

- `lark-approval-initiate.md` determines the create request field names, field hierarchy, and node parameter structure.
- `approvals.get.form` determines the widget `id`, `type`, option value range, and sub-widget structure.
- `approvals.get.node_list` determines the node key, whether an approver must be added, and whether multiple people are allowed.
- [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md) determines the final structure of each widget's `value`.
- Unless this document explicitly permits otherwise, do not guess the value source, and do not treat display text directly as a submittable value.

<a id="默认来源"></a>
## Default Sources

- Basic information such as the approval definition, `approval_code`, `is_external`, and `create_link` is obtained from `approval approvals search` by default.
- Widget `id`, `type`, option values, and sub-widget structure are obtained from `approval approvals get.form` by default.
- Node information such as the node key, `need_approver`, and `approver_chosen_multi` is obtained from `approval approvals get.node_list` by default.
- This document only supplements the value sourcing rules **beyond these default sources**, as well as the values that currently must be provided directly by the user.

<a id="控件值来源规则"></a>
## Widget Value Source Rules

<a id="联系人-contact"></a>
### Contact `contact`

- Only writing `open_ids` is recommended.
- Writing both `value(user_id)` + `open_ids` is no longer recommended, to avoid further increasing complexity.
- If the user provides a name, email, or account, first use `lark-contact` to resolve it into `open_id`.

<a id="部门-department"></a>
### Department `department`

- Highest priority: the user directly provides `open_department_id`.
- If the user says "my department" or "Zhang San's department", first use `lark-contact` to query the corresponding person's information, then take the `open_department_id` from the department they belong to.
- If the query finds that the person has only one department, it can be used directly.
- If the query finds multiple departments, do not guess automatically; the user must explicitly choose one, or directly enter the `open_department_id`.
- If it still cannot be determined, clearly inform the user that automatically determining the department value is currently not supported.

<a id="附件-attachmentv2"></a>
### Attachment `attachmentV2`

- Currently `lark-approval` is not responsible for uploading files.
- The user must directly provide the file code.
- If the user cannot provide the file code, clearly inform them that submitting this widget cannot currently be completed through `lark-approval` alone.

<a id="图片-image--imagev2"></a>
### Image `image` / `imageV2`

- Currently `lark-approval` is not responsible for uploading images.
- The user must directly provide the file code.
- If the user cannot provide the file code, clearly inform them that submitting this widget cannot currently be completed through `lark-approval` alone.

<a id="文档-document"></a>
### Document `document`

- The user can directly provide `token` / `document_id`.
- If the user provides a Feishu document link, first try to extract the token from the link.
- If link extraction fails, then ask the user to manually enter the token.

<a id="关联审批-connect"></a>
### Related Approval `connect`

- The user directly provides the `instance_code` of the target approval instance.
- Currently, the automatic process of "searching for the related instance and then looking up the code" is not performed by default.

<a id="地址-address"></a>
### Address `address`

- The user directly provides the geographic database `id`.
- If the user cannot provide this `id`, automatic value sourcing is currently not supported.

<a id="特殊控件组"></a>
## Special Widget Groups

The structure of the following widget groups is still assembled according to [`lark-approval-instance-form-control-parameters.md`](./lark-approval-instance-form-control-parameters.md):

- `leaveGroupV2`
- `workGroup`
- `outGroup`
- `shiftGroup`

Supplementary rules:

- The `id` / `type` of the widget group itself and its sub-widgets are identified from `approval approvals get.form`.
- For single-select/multi-select or business enumeration values within the group, preferentially take them from the option structure returned by `approval approvals get.form`.
- Do not submit the widget group as a whole as an ordinary string or flat object.

<a id="不支持自动准备的值"></a>
## Values Not Supported for Automatic Preparation

The following values are currently not recommended to be automatically prepared by `lark-approval`:

- The file code after file upload
- The file code after image upload
- The geographic database `id` of the address widget
- A department `open_department_id` that cannot be uniquely determined

When encountering such values, clearly tell the user what needs to be provided, rather than continuing to guess.

<a id="最小决策表"></a>
## Minimal Decision Table

| Scenario | Handling |
|---|---|
| The user says "find Zhang San as the approver" | Use `lark-contact` to resolve Zhang San, and take `open_id` |
| The user says "my department" | First query the current user's department; if there are multiple departments, let the user choose |
| The user provides a document link | First try to extract the token |
| The user wants to fill in an image/attachment | Require them to directly provide the file code |
| The user wants to fill in a related approval | Require them to directly provide `instance_code` |
| The user wants to fill in an address | Require them to directly provide the geographic database `id` |
