<a id="okr-实体定义"></a>
# OKR Entity Definitions

This document describes the core entities and their field definitions involved in the Feishu OKR API (`/open-apis/okr/v2`).

<a id="实体关系概览"></a>
## Entity Relationship Overview

```
Cycle (User Cycle)
  └── Objective (Objective)
        ├── KeyResult (Key Result)
        │     └── Indicator (Indicator)
        │     └── list<Progress> (Progress Record List)
        │     └── list<Comment> (Comment List)
        └── Indicator (Indicator)
        └── list<Progress> (Progress Record List)
        └── list<Comment> (Comment List)

Cycle and Progress can also have Comment attached directly.
Alignment (Alignment Relationship): Objective ↔ Objective
Category (Category): Grouping label for Objective
```

---

<a id="owner-所有者"></a>
## Owner

The owner identifies the belonging of an OKR entity. Currently, only the user type is supported.

| Field           | Type       | Required | Description                                            |
|--------------|----------|----|-----------------------------------------------|
| `owner_type` | `string` | Yes  | Owner type, usually `"user"`.                           |
| `user_id`    | `string` | No  | Employee ID, the type is determined by the request parameter `user_id_type` (default `open_id`) |

---

<a id="cycle-用户周期"></a>
## Cycle (User Cycle)

The user cycle is the top-level container of OKRs, representing all objectives and key results within a time period.

| Field                | Type        | Required | Description                                         |
|-------------------|-----------|----|--------------------------------------------|
| `id`              | `string`  | Yes  | User cycle ID                                    |
| `create_time`     | `string`  | Yes  | Creation time                                       |
| `update_time`     | `string`  | Yes  | Update time                                       |
| `tenant_cycle_id` | `string`  | Yes  | Tenant cycle ID (the same cycle has different user cycle IDs under different users, but the tenant cycle ID is the same) |
| `owner`           | `Owner`   | Yes  | Owner                                        |
| `start_time`      | `string`  | Yes  | Cycle start time. Always starts on the 1st of a month                           |
| `end_time`        | `string`  | Yes  | Cycle end time. Ends on the last day of a month                           |
| `cycle_status`    | `integer` | No  | Cycle status, see the table below                                   |
| `score`           | `number`  | No  | Cycle score, range [0, 1], supports one decimal place                      |

<a id="常用术语"></a>
### Common Terms

- **Current cycle**: Refers to the start_time/end_time of the cycle
  Refers to the cycle whose time period of start_time / end_time overlaps with the current time (that is: start_time <= current time and end_time >= current time).
  Note: Time overlap is the primary and mandatory hard condition for determining the current cycle. It must never be determined solely based on cycle_status == 1.
  If there are multiple cycles that meet the time overlap criterion, then filter among these cycles that contain the current time, keeping cycles whose cycle status is default (0) or normal (1).
  If there are still multiple, choose the newer one among them. When the user mentions expressions such as "previous cycle" or "next cycle", they are usually calculated based on the current cycle.
    - If the user does not mention it, the current cycle generally does not consider annual cycles (cycles whose start and end times are from 01-01 to 12-31)
- **Owner**: The vast majority of owners are users. A small number of tenants have enabled the "Team OKR" feature, and the owner may be a department. Under a user identity, you can only edit OKRs whose owner is the current user.

<a id="周期状态-cycle_status"></a>
### Cycle Status (cycle_status)

| Value | Constant Name       | Description          |
|---|-----------|-------------|
| 0 | `default` | Default status        |
| 1 | `normal`  | In effect         |
| 2 | `invalid` | Expired (usually can still be filled in) |
| 3 | `hidden`  | Hidden (invisible)    |

> **SHORTCUT:** `okr +cycle-list` [lark-okr-cycle-list.md](lark-okr-cycle-list.md) Get the user's cycle list, which can be filtered by time
>
> **API:** `cycles.list`

---

<a id="objective-目标"></a>
## Objective

An objective is the "O" in OKR. It belongs to a user cycle and can contain multiple key results.

| Field            | Type             | Required | Description                                                      |
|---------------|----------------|----|---------------------------------------------------------|
| `id`          | `string`       | Yes  | Objective ID                                                   |
| `create_time` | `string`       | Yes  | Creation time, millisecond timestamp, the shortcut will parse it into a date-time                          |
| `update_time` | `string`       | Yes  | Update time, millisecond timestamp, the shortcut will parse it into a date-time                          |
| `owner`       | `Owner`        | Yes  | Owner                                                     |
| `cycle_id`    | `string`       | Yes  | Belonging user cycle ID                                               |
| `position`    | `integer`      | Yes  | Sort order, starting from 1, range [1, 100]                                 |
| `content`     | `ContentBlock` | No  | Objective content (rich text), see [ContentBlock Definition](lark-okr-contentblock.md) |
| `score`       | `number`       | No  | Objective score, range [0, 1], supports one decimal place                                   |
| `notes`       | `ContentBlock` | No  | Objective notes (rich text), see [ContentBlock Definition](lark-okr-contentblock.md) |
| `weight`      | `number`       | No  | Objective weight, range [0, 1], supports three decimal places                                   |
| `deadline`    | `string`       | No  | Deadline, millisecond timestamp, the shortcut will parse it into a date-time                          |
| `category_id` | `string`       | No  | Belonging category ID                                                 |

> **SHORTCUT:**
> - `okr +cycle-detail` [lark-okr-cycle-detail.md](lark-okr-cycle-detail.md) Get all objectives and key results under a user cycle. Time-related fields will be parsed in date-time format
>
> **API:**
> - `cycle.objectives.list` — Get the objective list under a cycle
> - `objectives.get` — Get a single objective
> - `cycle.objectives.create` — Create an objective
> - `objectives.delete` — Delete an objective
> - `cycles.objectives_position` — Update the objective sort order under a cycle
> - `cycles.objectives_weight` — Update the objective weight under a cycle

---

<a id="keyresult-关键结果"></a>
## KeyResult

A key result is the "KR" in OKR. It belongs to an objective and describes the measurable outcome of the objective.

| Field             | Type             | Required | Description                                                        |
|----------------|----------------|----|-----------------------------------------------------------|
| `id`           | `string`       | Yes  | Key result ID                                                   |
| `create_time`  | `string`       | Yes  | Creation time, millisecond timestamp                                                |
| `update_time`  | `string`       | Yes  | Modification time, millisecond timestamp                                                |
| `owner`        | `Owner`        | Yes  | Owner                                                       |
| `objective_id` | `string`       | Yes  | Belonging objective ID                                                   |
| `position`     | `integer`      | Yes  | Sort order, starting from 1, range [1, 100]                                   |
| `content`      | `ContentBlock` | No  | Key result content (rich text), see [ContentBlock Definition](lark-okr-contentblock.md) |
| `score`        | `number`       | No  | Key result score, range [0, 1], supports one decimal place                                   |
| `weight`       | `number`       | No  | Weight, range [0, 1], supports three decimal places                                       |
| `deadline`     | `string`       | No  | Deadline, millisecond timestamp                                                |

> **API:**
> - `objective.key_results.list` — Get the key result list under an objective
> - `key_results.get` — Get a single key result
> - `key_results.patch` — Update a key result
> - `key_results.delete` — Delete a key result
> - `objectives.key_results_position` — Update the key result sort order under an objective
> - `objectives.key_results_weight` — Update the key result weight under an objective

---

<a id="progress-进展记录"></a>
## Progress

Progress records are attached to an Objective or Key Result and are used to record phased progress content and progress percentage. Each progress record contains rich text content and an optional progress rate.

| Field              | Type             | Required | Description                                                      |
|-----------------|----------------|----|---------------------------------------------------------|
| `progress_id`   | `string`       | Yes  | Progress record ID (int64, positive integer)                                      |
| `modify_time`   | `string`       | Yes  | Last modification time, millisecond timestamp, the shortcut will parse it into a date-time                        |
| `content`       | `ContentBlock` | No  | Progress content (rich text), see [ContentBlock Definition](lark-okr-contentblock.md) |
| `progress_rate` | `ProgressRate` | No  | Progress rate, including percentage and status                                            |

<a id="progressrate-进度率"></a>
### ProgressRate

| Field        | Type       | Required | Description                                                                                                                           |
|-----------|----------|----|------------------------------------------------------------------------------------------------------------------------------|
| `percent` | `number` | No  | Progress percentage, range [-99999999999, 99999999999]. The percentage value is usually in 0-100, but values outside this range are allowed to represent situations such as overachievement or negative growth. When the quantitative metric of the attached objective or key result does not use percentage units, use this field to update the current value. The system retains at most two decimal places |
| `status`  | `string` | No  | Progress status, the shortcut returns a readable string, see the table below                                                                                                    |

<a id="进度状态-progress_ratestatus"></a>
### Progress Status (progress_rate.status)

| Value         | Constant Name | Description    |
|-----------|-----|-------|
| `normal`  | Normal  | Progress is normal  |
| `overdue` | Overdue  | Progress is overdue  |
| `done`    | Completed | Progress is completed |

<a id="创建进展记录时的参数"></a>
### Parameters When Creating a Progress Record

When creating a progress record, in addition to `content`, you also need to specify the corresponding objective or key result to which this progress record is attached:

| Field              | Type             | Required | Description                                                      |
|-----------------|----------------|----|---------------------------------------------------------|
| `content`       | `ContentBlock` | Yes  | Progress content (rich text), see [ContentBlock Definition](lark-okr-contentblock.md) |
| `target_id`     | `string`       | Yes  | Objective ID or key result ID                                          |
| `target_type`   | `integer`      | Yes  | Target type: `2`=Objective, `3`=KeyResult              |
| `progress_rate` | `ProgressRate` | No  | Progress rate, can set `percent` and `status`                            |
| `source_title`  | `string`       | No  | Source title, used to display the progress source in the OKR interface                                  |
| `source_url`    | `string`       | No  | Source URL, used to display the progress source link in the OKR interface                              |

> **SHORTCUT:**
> - `okr +progress-get` [lark-okr-progress-get.md](lark-okr-progress-get.md) Get a single progress record
> - `okr +progress-create` [lark-okr-progress-create.md](lark-okr-progress-create.md) Create a progress record for an objective or key result
> - `okr +progress-update` [lark-okr-progress-update.md](lark-okr-progress-update.md) Update progress record content
> - `okr +progress-delete` [lark-okr-progress-delete.md](lark-okr-progress-delete.md) Delete a progress record
> - `okr +progress-list` [lark-okr-progress-list.md](lark-okr-progress-list.md) Get the progress records under an objective/key result

---

<a id="comment-评论"></a>
## Comment

Comments can be attached to a Cycle, Objective, KeyResult, or Progress, and are used to discuss an OKR entity or a passage of text in the body. Comments fall into two types: entity-level comments and selection comments:

- **Entity-level comments**: Attached directly to a Cycle or Progress. One comment is one comment item, and solve/reopen only affects that comment.
- **Selection comments**: Attached to a text selection in the body of an Objective or KeyResult, and carry a `selection`. Comments under the same `selection.id`
  belong to the same comment thread; solve/reopen are handled by comment thread, but delete still deletes only the specified single comment.

<a id="comment-字段"></a>
### Comment Fields

| Field               | Type                 | Required | Description                                                                                            |
|------------------|--------------------|----|-----------------------------------------------------------------------------------------------|
| `id`             | `string`           | Yes  | Comment ID, a positive int64 integer.                                                                              |
| `target`         | `CommentTarget`    | Yes  | The object the comment is attached to, containing `target_type` and `target_id`. The type is `cycle`, `progress`, `objective`, or `key_result`.      |
| `commentator_id` | `string`           | Yes  | Commenter ID; the returned ID type is determined by the request parameter `user_id_type`.                                                       |
| `status`         | `string`           | Yes  | Comment status: `open` (open) or `solved` (resolved).                                                               |
| `create_time`    | `string`           | Yes  | Creation time;                                                                                         |
| `update_time`    | `string`           | Yes  | Last update time;                                                                                       |
| `content`        | `ContentBlock`     | No  | Comment body, see [ContentBlock definition](lark-okr-contentblock.md).                                           |
| `solver_id`      | `string`           | No  | ID of the user who resolved the comment.                                                                                   |
| `solved_time`    | `string`           | No  | Comment resolution time, a millisecond timestamp.                                                                                 |
| `ref_comment_id` | `string`           | No  | Referenced comment ID. Entity-level comments such as Progress/Cycle can use it to express a reply relationship; when creating a selection comment on an Objective/KeyResult, it can be used to locate an existing selection thread, but the new comment itself does not establish a reference relationship. |
| `selection`      | `CommentSelection` | No  | Selection information. Empty for entity-level comments; selection comments contain a selection ID and optional selected text.                                                    |

<a id="commenttarget-评论目标"></a>
### CommentTarget

| Field            | Type       | Required | Description                                             |
|---------------|----------|----|------------------------------------------------|
| `target_type` | `string` | Yes  | `cycle`, `progress`, `objective`, or `key_result`. |
| `target_id`   | `string` | Yes  | The ID of the corresponding Cycle, Progress, Objective, or KeyResult.  |

<a id="commentselection-划词信息"></a>
### CommentSelection

| Field              | Type       | Required | Description                          |
|-----------------|----------|----|-----------------------------|
| `id`            | `string` | Yes  | Selection ID. Comments under the same `id` belong to the same comment thread. |
| `selected_text` | `string` | No  | The body text anchored by the selection.                  |

<a id="评论创建与状态规则"></a>
### Comment Creation and Status Rules

- When creating an entity-level comment on a Cycle/Progress, do not pass `selected_text`; you can reply to an existing comment via `ref_comment_id`.
- When creating a selection comment on an Objective/KeyResult, choose one of `selected_text` or `ref_comment_id`: the former creates a new selection, and the latter attaches the comment to the existing selection thread that the referenced comment belongs to. shortcut
  additionally provides `--select-all` in place of `selected_text` to select all content within the O/KR.
- The request parameter of `solve` / `reopen` is a single comment ID. For entity-level comments it affects only that comment; for selection comments it affects the entire comment thread.
- `delete` permanently deletes the specified comment, does not delete other comments in the same comment thread, and cannot be recovered after deletion.

> **SHORTCUT:**
> - `okr +comment-detail` [lark-okr-comment-detail.md](lark-okr-comment-detail.md) Get all comments of all objects under a cycle and organize them by comment thread
> - `okr +comment-list` [lark-okr-comment-list.md](lark-okr-comment-list.md) Get comments under a single comment target with pagination
> - `okr +comment-get` [lark-okr-comment-get.md](lark-okr-comment-get.md) Get a single comment
> - `okr +comment-create` [lark-okr-comment-create.md](lark-okr-comment-create.md) Create a comment, reply, or attach to an existing selection thread
> - `okr +comment-patch` [lark-okr-comment-patch.md](lark-okr-comment-patch.md) Modify the comment body
> - `okr +comment-delete` [lark-okr-comment-delete.md](lark-okr-comment-delete.md) Permanently delete a single comment
> - `okr +comment-solve` [lark-okr-comment-solve-reopen.md](lark-okr-comment-solve-reopen.md) Resolve a comment/comment thread
> - `okr +comment-reopen` [lark-okr-comment-solve-reopen.md](lark-okr-comment-solve-reopen.md) Reopen a comment/comment thread
---

<a id="indicator-指标"></a>
## Indicator

An indicator is a quantitative measure of an objective or key result, and can be attached independently to an Objective or KeyResult.

| Field                             | Type              | Required | Description                                 |
|--------------------------------|-----------------|----|------------------------------------|
| `id`                           | `string`        | Yes  | Indicator ID                              |
| `create_time`                  | `string`        | Yes  | Creation time, a millisecond timestamp                         |
| `update_time`                  | `string`        | Yes  | Update time, a millisecond timestamp                         |
| `owner`                        | `Owner`         | Yes  | Owner                                |
| `entity_type`                  | `integer`       | Yes  | Owning entity type: `2`=objective, `3`=key result             |
| `entity_id`                    | `string`        | Yes  | Owning entity ID                            |
| `indicator_status`             | `integer`       | Yes  | Indicator status, see the table below                           |
| `status_calculate_type`        | `integer`       | Yes  | Status calculation method, see the table below                         |
| `start_value`                  | `number`        | No  | Start value, range [-99999999999, 99999999999] |
| `target_value`                 | `number`        | No  | Target value, range [-99999999999, 99999999999] |
| `current_value`                | `number`        | No  | Current value, range [-99999999999, 99999999999] |
| `current_value_calculate_type` | `integer`       | No  | Current value calculation method, see the table below                        |
| `unit`                         | `IndicatorUnit` | No  | Indicator unit                               |

<a id="修改指南"></a>
### Modification Guide

- **Progress value**: Generally refers to `current_value`; when no unit is mentioned, it is usually calculated on a percentage scale.
- When the user asks to update OKR progress quantitatively, it generally means modifying the Indicator of the corresponding OKR.
- When an OKR has no quantitative indicator set, the Indicator content is empty. If the user does not specify otherwise, when updating progress you can by default set the progress on a percentage scale (start value 0, target value 100, unit
  set to 0/PERCENT as described below)

<a id="指标状态-indicator_status"></a>
### Indicator Status (indicator_status)

| Value  | Description  |
|----|-----|
| -1 | Undefined |
| 0  | Normal  |
| 1  | At risk |
| 2  | Delayed |

<a id="状态计算方式-status_calculate_type"></a>
### Status Calculation Method (status_calculate_type)

| Value | Description              | Applicable scope    |
|---|-----------------|---------|
| 0 | Manual update            | Objective, key result |
| 1 | Automatically updated based on progress and current time   | Objective, key result |
| 2 | Updated based on the status of the highest-risk key result | Objective only     |

<a id="当前值计算方式-current_value_calculate_type"></a>
### Current Value Calculation Method (current_value_calculate_type)

| Value | Description            | Applicable scope    |
|---|---------------|---------|
| 0 | Manual update          | Objective, key result |
| 1 | Automatically updated based on key result progress  | Objective only     |
| 2 | Updated based on the progress of decomposed key results | Key result only   |

<a id="indicatorunit-指标单位"></a>
### IndicatorUnit

| Field           | Type        | Required | Description                                                                          |
|--------------|-----------|----|-----------------------------------------------------------------------------|
| `unit_type`  | `integer` | Yes  | Unit type: `0`=common, `1`=custom                                                         |
| `unit_value` | `string`  | Yes  | Unit value. Options for the common type: `PERCENT` (percentage), `NONE` (no unit), `YUAN` (yuan), `DOLLAR` (US dollar); custom type character length must not exceed 5 |

> **API:**
> - `key_result.indicators.list` — Get the indicators of a key result
> - `objective.indicators.list` — Get the indicators of an objective
> - `indicators.patch` — Update an indicator

---

<a id="alignment-对齐关系"></a>
## Alignment

An alignment relationship describes the vertical alignment between two objectives.

| Field                 | Type        | Required | Description                    |
|--------------------|-----------|----|-----------------------|
| `id`               | `string`  | Yes  | Alignment ID                 |
| `create_time`      | `string`  | Yes  | Creation time, a millisecond timestamp            |
| `update_time`      | `string`  | Yes  | Update time, a millisecond timestamp            |
| `from_owner`       | `Owner`   | Yes  | Owner who initiates the alignment              |
| `to_owner`         | `Owner`   | Yes  | Owner being aligned to               |
| `from_entity_type` | `integer` | Yes  | Entity type that initiates the alignment, fixed as `2` (objective) |
| `from_entity_id`   | `string`  | Yes  | Entity ID that initiates the alignment            |
| `to_entity_type`   | `integer` | Yes  | Entity type being aligned to, fixed as `2` (objective)  |
| `to_entity_id`     | `string`  | Yes  | Entity ID being aligned to             |

> **API:**
> - `alignments.get` — Get an alignment relationship
> - `alignments.delete` — Delete an alignment relationship
> - `objective.alignments.list` — Batch get alignment relationships under an objective
> - `objective.alignments.create` — Create an alignment relationship

---

<a id="category-分类"></a>
## Category

Categories are used to group and label objectives (such as "personal OKR", "team OKR", "committed OKR"), etc. The specific categories depend on tenant settings.

| Field              | Type             | Required | Description                                                          |
|-----------------|----------------|----|-------------------------------------------------------------|
| `id`            | `string`       | Yes  | Category ID                                                       |
| `create_time`   | `string`       | Yes  | Creation time, a millisecond timestamp                                                  |
| `update_time`   | `string`       | Yes  | Update time, a millisecond timestamp                                                  |
| `category_type` | `string`       | Yes  | Category type: `"person"`=personal, `"team"`=team                              |
| `enabled`       | `boolean`      | Yes  | Whether enabled                                                        |
| `color`         | `string`       | Yes  | Color identifier: `blue`, `purple`, `wathet`, `turquoise`, `indigo`, `orange` |
| `name`          | `CategoryName` | Yes  | Multilingual name                                                       |

<a id="categoryname-分类名称"></a>
### CategoryName

| Field   | Type       | Required | Description  |
|------|----------|----|-----|
| `zh` | `string` | No  | Chinese name |
| `en` | `string` | No  | English name |
| `ja` | `string` | No  | Japanese name |

> **API:** `categories.list` — Batch get the list of categories configured for the tenant

---

<a id="通用请求参数"></a>
## Common Request Parameters

The following parameters are common to most OKR APIs:

| Parameter                   | Location      | Required | Default Value                    | Description                                               |
|----------------------|---------|----|------------------------|--------------------------------------------------|
| `user_id_type`       | `query` | No  | `"open_id"`            | User ID type: `open_id` \| `union_id` \| `user_id`    |
| `department_id_type` | `query` | No  | `"open_department_id"` | Department ID type: `open_department_id` \| `department_id` |
| `page_size`          | `query` | No  | `10`                   | Page size, maximum 100                                      |
| `page_token`         | `query` | No  | `""`                   | Page token, pass an empty string for the first page                                        |

---

<a id="权限-scope-说明"></a>
## Permission Scope Description

| Scope                          | Permission Type | Description           |
|--------------------------------|------|--------------|
| `okr:okr.content:readonly`     | Read    | Read OKR content    |
| `okr:okr.content:writeonly`    | Write    | Write/delete OKR content |
| `okr:okr.period:readonly`      | Read    | Read OKR cycles    |
| `okr:okr.progress:readonly`    | Read    | Read progress records       |
| `okr:okr.progress:writeonly`   | Write    | Create/update progress records    |
| `okr:okr.progress:delete`      | Write    | Delete progress records       |
| `okr:okr.progress.file:upload` | Write    | Upload progress record image attachments   |
| `okr:okr.setting:read`         | Read    | Read OKR settings    |

All OKR APIs support both `user` and `tenant` (app) access token types.

<a id="参考"></a>
## References

- [OKR ContentBlock rich text format](lark-okr-contentblock.md) — Rich text structure definition for the content/notes fields
- [okr +cycle-list](lark-okr-cycle-list.md) — List a user's OKR cycles
- [okr +cycle-detail](lark-okr-cycle-detail.md) — Get the objectives and key results under a cycle
- [okr +progress-get](lark-okr-progress-get.md) — Get a progress record
- [okr +progress-create](lark-okr-progress-create.md) — Create a progress record
- [okr +progress-update](lark-okr-progress-update.md) — Update a progress record
- [okr +progress-delete](lark-okr-progress-delete.md) — Delete a progress record
