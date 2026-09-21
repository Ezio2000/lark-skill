# Base Role Permission Schema

> **Module entry**: [Advanced Permission and Role](lark-base-advanced-permission-and-role.md) | **Related commands**: `+role-create` · `+role-update` · `+role-get`

This document is the single source of truth (SSOT) for the role permission JSON (AdvPermBaseRoleConfig), for reference by `+role-create` and `+role-update` when constructing the `--json` parameter.

<a id="-目录"></a>
## 📋 Table of Contents

- [Top-level structure (AdvPermBaseRoleConfig)](#顶层结构-advpermbaseroleconfig)
- [Role type (RoleType)](#角色类型-roletype)
- [Reading and updating roles](#读取与更新角色)
- [Base-level permissions (BaseRuleMap)](#base-级权限-baserulemap)
- [Dashboard permissions (DashboardRule)](#仪表盘权限-dashboardrule)
- [Document permissions (DocxRule)](#文档权限-docxrule)
- [Table permissions (TableRule)](#数据表权限-tablerule)
    - [Table-level permissions (TablePerm)](#表级权限-tableperm)
    - [View permissions (ViewRule)](#视图权限-viewrule)
    - [Field permissions (FieldRule)](#字段权限-fieldrule)
    - [Record permissions (RecordRule)](#记录权限-recordrule)
    - [Filter conditions (FilterRuleGroup)](#筛选条件-filterrulegroup)
- [Default permission policies and risk control rules](#默认权限策略与风控规则)
    - [Items disabled by default](#默认关闭项)
    - [Permission object selection](#权限对象选择)
    - [Default record operation policies](#记录操作默认策略)
    - [field_perms construction SOP](#field_perms-构造-sop)
    - [Default view permission policies](#视图权限默认策略)

---

<a id="顶层结构-advpermbaseroleconfig"></a>
## Top-level structure (AdvPermBaseRoleConfig)

```json
{
  "role_name": "财务审核员",
  "role_type": "custom_role",
  "base_rule_map": { "copy": false, "download": false },
  "table_rule_map": { "订单表": { "perm": "edit", "...": "..." } },
  "dashboard_rule_map": { "销售看板": { "perm": "read_only" } },
  "docx_rule_map": { "文档A": { "perm": "edit", "allow_download": true } }
}
```

| Field | Type | Required | Description |
|------|------|----|------|
| `role_name` | string | Yes  | Role name, cannot be empty |
| `role_type` | string | Yes  | Role type, see [RoleType](#角色类型-roletype) |
| `base_rule_map` | map\<string, bool\> | Yes  | Base-level permissions, see [BaseRuleMap](#base-级权限-baserulemap) |
| `table_rule_map` | map\<string, TableRule\> | No  | Table permissions, key is the table name |
| `dashboard_rule_map` | map\<string, DashboardRule\> | No  | Dashboard permissions, key is the dashboard name |
| `docx_rule_map` | map\<string, DocxRule\> | No  | Document permissions (single-item mode only), key is the document name |

---

<a id="角色类型-roletype"></a>
## Role type (RoleType)

| Value | Description |
|------|------|
| `editor` | System role: Editor |
| `reader` | System role: Reader |
| `custom_role` | Custom role |

**Note**:
- The create API (`+role-create`) only supports `custom_role`
- The update API (`+role-update`) supports `editor` / `reader` / `custom_role`

---

<a id="读取与更新角色"></a>
## Reading and updating roles

- `+role-list` is used to locate a role and returns a role summary; both system roles and custom roles may appear in the list.
- `+role-get` returns the complete permission configuration. Before updating, use it to confirm the current `role_name`, `role_type`, and existing permission structure.
- `+role-update` is a delta merge; submit only the fields that need to change; however, `role_name` and `role_type` must still carry their current values to avoid accidentally changing role identity information.
- `+role-delete` applies only to custom roles; system roles can have their configuration adjusted within the permission ceiling, but cannot be deleted.

---

<a id="base-级权限-baserulemap"></a>
## Base-level permissions (BaseRuleMap)

1. The default value is `false`; set it to `true` when it needs to be enabled.
2. This field must be included by default when creating and modifying roles; it is **strictly prohibited** to set it to `true` when the user has not explicitly requested it.

```json
{
  "base_rule_map": {
    "copy": true,
    "download": false
  }
}
```

| Key | Description |
|-----|------|
| `copy` | Allow copying Base content |
| `download` | Allow creating copies, downloading, and printing the Base |

---

<a id="仪表盘权限-dashboardrule"></a>
## Dashboard permissions (DashboardRule)

```json
{
  "dashboard_rule_map": {
    "销售看板": { "perm": "read_only" },
    "内部数据": { "perm": "no_perm" }
  }
}
```

| Field | Type | Description |
|------|------|------|
| `perm` | string | Dashboard permission |

**perm possible values**:

| Value | Description |
|----|------|
| `read_only` | Read only |
| `no_perm` | No permission |

---

<a id="文档权限-docxrule"></a>
## Document permissions (DocxRule)

> ⚠️ Available only in single-item mode (`is_base_solo = true`).

```json
{
  "docx_rule_map": {
    "文档A": { "perm": "edit", "allow_download": true },
    "文档B": { "perm": "read_only" }
  }
}
```

| Field | Type | Required | Description |
|------|------|------|------|
| `perm` | string | Yes | Document permission |
| `allow_download` | bool | No | Whether downloading/exporting is allowed |

**perm possible values**:

| Value | Description |
|----|------|
| `edit` | Editable |
| `read_only` | Read only |
| `no_perm` | No permission |

---

<a id="数据表权限-tablerule"></a>
## Table permissions (TableRule)

```json
{
  "table_rule_map": {
    "订单表": {
      "perm": "edit",
      "view_rule": {
        "allow_edit": true,
        "visibility": { "all_visible": true }
      },
      "record_rule": {
        "record_operations": ["add", "delete"],
        "other_record_all_read": true
      },
      "field_rule": {
        "field_perm_mode": "all_edit"
      }
    },
    "用户表": {
      "perm": "read_only",
      "view_rule": {
        "allow_edit": false,
        "visibility": { "all_visible": true }
      },
      "record_rule": {
        "record_operations": [],
        "other_record_all_read": true
      },
      "field_rule": {
        "field_perm_mode": "all_read"
      }
    },
    "内部表": {
      "perm": "no_perm"
    }
  }
}
```

| Field | Type | Description |
|------|------|------|
| `perm` | string | Table-level permission, see [TablePerm](#表级权限-tableperm) |
| `view_rule` | ViewRule | View permission configuration |
| `record_rule` | RecordRule | Record permission configuration |
| `field_rule` | FieldRule | Field permission configuration |

**`+role-create` hard constraints**:

- When `perm` is `no_perm`, do not set `view_rule`, `record_rule`, or `field_rule`.
- When `perm` is any other value, complete `view_rule`, `record_rule`, and `field_rule` must all be provided; missing any one of them will cause creation to fail.
- `+role-update` is a delta merge; submit only the fields to be modified; do not fabricate unchanged configuration for a partial update.

---

<a id="表级权限-tableperm"></a>
### Table-level permissions (TablePerm)

| Value | Description |
|----|------|
| `manage` | Can manage |
| `edit` | Can edit |
| `read_only` | Read only |
| `no_perm` | No permission (in this case, view, record, and field permissions cannot be set) |

---

<a id="视图权限-viewrule"></a>
### View permissions (ViewRule)

```json
{
  "view_rule": {
    "allow_edit": true,
    "visibility": {
      "all_visible": false,
      "visible_views": ["表格视图", "看板视图"]
    }
  }
}
```

| Field | Type | Description                         |
|------|------|----------------------------|
| `allow_edit` | bool | Can add, delete, and modify views; defaults to `true` when the table permission is `edit`, and to `false` when the table permission is `read_only` or the user explicitly restricts it |
| `visibility` | object | Visible view configuration                    |
| `visibility.all_visible` | bool | Whether all are visible                     |
| `visibility.visible_views` | []string | List of visible view names                  |

**⚠️ Core rule: `view_rule` must contain both the `allow_edit` and `visibility` fields; neither can be omitted.**

When outputting `view_rule`, you **must** use the following complete structure, choosing the corresponding template based on the scenario:

```json
// Case A: Table permission is edit and the user has not explicitly restricted it → allow_edit defaults to true, all visible
{
  "view_rule": {
    "allow_edit": true,
    "visibility": {
      "all_visible": true
    }
  }
}

// Case B: Table permission is read_only, or the user explicitly says views cannot be edited → all visible, not editable
{
  "view_rule": {
    "allow_edit": false,
    "visibility": {
      "all_visible": true
    }
  }
}

// Case C: The user mentioned specific views → only the specified views are visible (allow_edit is still determined by the A/B rules)
{
  "view_rule": {
    "allow_edit": true,
    "visibility": {
      "all_visible": false,
      "visible_views": ["表格视图", "看板视图"]
    }
  }
}
```

**Note**:
- When `all_visible` is `false`, `visible_views` cannot be empty; at least one visible view must be specified
- Views whose `biz_type` is `query_form_view` cannot be placed in `visible_views` (visibility cannot be configured)

---

<a id="字段权限-fieldrule"></a>
### Field permissions (FieldRule)

```json
{
  "field_rule": {
    "field_perm_mode": "specify",
    "field_perms": {
      "金额": "edit",
      "备注": "read",
      "密码": "no_perm"
    },
    "allow_edit_and_modify_option_fields": [],
    "allow_edit_and_download_file_fields": []
  }
}
```

| Field | Type | Description |
|------|------|------|
| `field_perm_mode` | string | Field permission mode |
| `field_perms` | map\<string, string\> | Field name → permission, valid only when `field_perm_mode` is `specify` |
| `allow_edit_and_modify_option_fields` | []string | List of field names that allow adding, deleting, and modifying options |
| `allow_edit_and_download_file_fields` | []string | List of field names that allow downloading attachments |

**field_perm_mode possible values**:

| Value | Description |
|----|------|
| `all_edit` | All fields editable, but options cannot be added, deleted, or modified |
| `all_read` | All fields readable |
| `specify` | Specify field permissions (can further set `field_perms` and option add/delete/modify permissions) |
| `no_perm` | No permission |

**Permission value for a single field in field_perms**:

| Value | Description |
|----|------|
| `edit` | Editable (includes add and read permissions) |
| `create` | Can add (includes read permission) |
| `read` | Readable |
| `no_perm` | No permission |

**⚠️ Important field_perms rules**:
1. Before writing, you must first check the field's `type`
2. Fields of type `formula` / `lookup` / `auto_number` **must be forcibly** downgraded to `read` or `no_perm`; setting them to `edit` is **strictly prohibited**
3. All fields except the 4 system fields must be output
4. `allow_edit_and_modify_option_fields`: configure only when the user explicitly requests "allow adding, deleting, and modifying options"; otherwise it must be an empty array `[]`. Only fields of type `select` are supported
5. `allow_edit_and_download_file_fields`: do not set it when the user has not requested it, and it can be set only when `field_perm_mode` is `specify`

---

<a id="记录权限-recordrule"></a>
### Record permissions (RecordRule)

```json
{
  "record_rule": {
    "record_operations": ["add"],
    "edit_filter_rule_group": {
      "conjunction": "and",
      "filter_rules": [
        {
          "conjunction": "and",
          "filters": [
            {
              "field_name": "部门",
              "operator": "is",
              "filter_values": ["财务部"]
            }
          ]
        }
      ]
    },
    "other_record_all_read": true
  }
}
```

| Field | Type | Description |
|------|------|------|
| `record_operations` | []string | Record operation permissions, valid only when `TablePerm = edit` |
| `edit_filter_rule_group` | FilterRuleGroup | Filter conditions for editable records; this field is empty when the scope is all records |
| `other_record_all_read` | bool | Whether all records are readable. It is `true` when all are readable, and `false` otherwise |
| `read_filter_rule_group` | FilterRuleGroup | Additional filter rules for readable records. Set only when the readable scope differs from the editable scope (depends on `other_record_all_read = false`) |

**record_operations possible values**:

| Value | Description |
|----|------|
| `add` | Can add records |
| `delete` | Can delete records |

---

<a id="筛选条件-filterrulegroup"></a>
### Filter conditions (FilterRuleGroup)

```json
{
  "conjunction": "and",
  "filter_rules": [
    {
      "conjunction": "and",
      "filters": [
        {
          "field_name": "部门",
          "operator": "is",
          "filter_values": ["财务部"]
        }
      ]
    }
  ]
}
```

**FilterRuleGroup structure**:

| Field | Type | Description |
|------|------|------|
| `conjunction` | string | Logical connective: `and` / `or` |
| `filter_rules` | []FilterRule | Array of filter rules |

**FilterRule structure**:

| Field | Type | Description |
|------|------|------|
| `conjunction` | string | Logical connective, defaults to `and` |
| `filters` | []Filter | Array of filter conditions |

**Filter structure**:

| Field | Type | Required | Description |
|------|------|------|------|
| `field_name` | string | Yes | Field name. Limited to fields whose `can_filter` is `true`. If the server requires current-user-type conditions, handle it according to the API response structure |
| `operator` | string | Yes | Operator, see the table below |
| `field_type` | string | No | Usually filled in by the server-side filterFiller; when the Agent determines the field type, use `+field-list` / the `type` of the field operation API as the basis; common filterable types include `select`, `user`, `created_by`, `number`, and some `formula` / `lookup` |
| `reference_type` | string | Conditional | Reference type. Must be assigned when `field_type` is a formula or reference field; it cannot be assigned in other cases |
| `filter_values` | []string | Conditional | Filter value. Not set when `operator` is `isEmpty` / `isNotEmpty`; also not required when the field type is `user`; must be set in other cases. The value is the option's `name` |
| `field_ui_type` | string | Conditional | Must be filled in when this field has a value |
| `is_invalid` | bool | No | Determines whether the filter condition is valid |

**operator possible values**:

| Value | Description |
|----|------|
| `is` | Equals |
| `isNot` | Does not equal |
| `contains` | Contains |
| `doesNotContain` | Does not contain |
| `isEmpty` | Is empty |
| `isNotEmpty` | Is not empty |
| `isGreater` | Greater than |
| `isGreaterEqual` | Greater than or equal to |
| `isLess` | Less than |
| `isLessEqual` | Less than or equal to |

**Note**:
- `field_type`, `field_ui_type`, and `reference_type` are automatically filled in by the server-side filterFiller when creating/updating a role; the client usually only needs to pass `field_name`, `operator`, and `filter_values`

---

<a id="默认权限策略与风控规则"></a>
## Default permission policies and risk control rules

When constructing the role configuration JSON, adopt a **default-deny and least-privilege** policy. Any permission the user has not explicitly mentioned is not granted; do not proactively expand the permission scope based on "reasonable guesses" or "common practice".

<a id="默认关闭项"></a>
### Items disabled by default

The following capabilities are **disabled by default** when the user has not explicitly stated otherwise:

| Capability | Default value | Enabling condition |
|------|--------|----------|
| Any access to tables not mentioned | `no_perm` | The user explicitly mentions the table |
| Dashboard access | Not configured | The user explicitly mentions the dashboard |
| `base_rule_map.copy` | `false` | The user explicitly requests "allow copying" |
| `base_rule_map.download` | `false` | The user explicitly requests "allow downloading/printing/copies" |

<a id="默认开启项条件性"></a>
### Items enabled by default (conditional)

The following capabilities are **enabled by default** under specific conditions, and are excluded only when the user explicitly restricts them:

| Capability | Default value | Exclusion condition |
|------|--------|----------|
| `record_operations` in `delete` | **Included** (when `perm = edit`) | Excluded only when the user explicitly restricts it |
| `view_rule.allow_edit` | **`true`** (when `perm = edit`) | Set to `false` when the user explicitly restricts "views cannot be edited" or when `perm = read_only` |

---

<a id="editor--reader-的权限上限规则"></a>
### Permission ceiling rules for Editor / Reader
1. For Editor and Reader, the system allows modifying their permission configuration, but simultaneously imposes the following ceiling constraints:
2. No permission item of a Reader may exceed "read only"
3. A Reader is not allowed to have any edit-, add-, or delete-related permissions; an Editor's permissions can be modified, but its capability scope is capped by the advanced permission capabilities.

<a id="权限对象选择"></a>
### Permission object selection

**Note**:
- Generate configuration only for permission objects the user explicitly points to (explicitly mentioned table names, dashboard names, or references that can be resolved to a unique object such as "the current table" or "this table")
- It is **strictly prohibited** to infer or expand permission objects based on business common sense, job responsibilities, name similarity, or other roles' historical configurations
- Objects the user has not explicitly mentioned generate no permission configuration and are treated as `no_perm`

---

<a id="记录操作默认策略"></a>
### Default Record Operation Policy

**Note**:
- When the user does not mention it, when the table permission is `edit`, it includes both `add` and `delete` by default; the default exclusion of `delete` applies only to scenarios where the user explicitly restricts operations
- The read scope defaults to aligning with the edit scope: when the user only describes the editable scope and does not specify the read scope, the readable scope stays consistent with the editable scope and is not proactively expanded
- When the readable scope and the editable scope are consistent, `read_filter_rule_group` **must not** be generated; instead, set `other_record_all_read = false` and `read_filter_rule_group = null`

**⚠️ Record Operation Restrictions**:
1. When `perm` is `read_only`, `record_rule.record_operations` **can only be empty**
2. For sync tables (`is_sync = true`), adding and deleting records is **strictly prohibited**

---

<a id="field_perms-构造-sop"></a>
### field_perms Construction SOP

When generating `field_perms`, **strictly do not** rely on the vague concept of "inheritance"; the following steps must be executed:

| Step | Operation | Description |
|------|------|------|
| 1. Baseline setting | `perm = edit` → all fields preset to `"edit"`; `perm = read_only` → all preset to `"read"` | Based on all fields in `base_table_info` |
| 2. Physical downgrade | `formula` / `lookup` / `auto_number` and system fields → forcibly downgraded to `"read"` | Immutable fields must never be set to `edit` |
| 3. User override | Apply `no_perm` / `read` / `create` only to fields for which the user has **explicitly specified** particular permissions | Fields not explicitly specified retain the baseline value |
| 4. Anti-filtering misjudgment | For fields used in `filter_rules`, if the baseline is `"edit"` and the user has not requested a downgrade → **keep `"edit"`** | Filter conditions do not affect field editability |
| 5. Filter dependency fallback | Fields appearing in `filter_rules` **must not** be omitted; permission is at least `"read"` | Final validation step |

**⚠️ field_perm_mode Selection Rules**:
1. When the user describes it with holistic expressions such as "all fields" or "the entire field set" and does not require adding, deleting, or modifying options, `all_edit` / `all_read` **must** be used, and it is **strictly prohibited** to switch to per-field `specify`
2. Use `specify` only in the following cases: the user explicitly raises a field-level differentiation requirement, there are significant differences between permission targets for different fields, or the user explicitly requires configuring add/delete/modify option permissions
3. Automatic downgrades caused by hard constraints on system fields are **not considered** differences and do not trigger `specify`
4. For restrictive modifiers such as "only", "can only", or "partial", fields outside the scope are set in the opposite direction of the modifier

**⚠️ Sync Table Restriction**: For tables in `is_sync = true`, setting fields to `edit` or `create` is **strictly prohibited**

---

<a id="视图权限默认策略"></a>
### Default View Permission Policy

**Decision flow (must be executed in order; stop once a match is hit)**:

1. **First determine whether the user mentioned a specific view name** (such as "kanban view visible", "Gantt chart not editable", etc.)
  - **Yes** → `all_visible = false`, and `visible_views` includes only the view names the user explicitly mentioned as "visible" (not viewID); views not mentioned are considered invisible
  - **No** (the user did not mention any view at all) → `all_visible = true`
2. When the table permission is `edit`, `allow_edit` **defaults to `true`**; set it to `false` only when the user explicitly restricts "views cannot be edited". When set to `true`, it **must** still include the `visibility` field (refer to View Permission Case A)
3. When `all_visible` is `false`, `visible_views` **must not be empty** and must include at least one view

**❌ Common Error — Missing `visibility` field:**
```json
// Error! Missing visibility
{ "view_rule": { "allow_edit": false } }
```
**✅ Correct form:**
```json
// Even if all are visible, visibility must still be written explicitly
{ "view_rule": { "allow_edit": false, "visibility": { "all_visible": true } } }
```

---

<a id="字段类型与筛选算子的强约束关系"></a>
### Strong Constraint Relationship Between Field Types and Filter Operators

When a field is used in record filter conditions, the `type` returned by the field operation interface has a fixed binding relationship with the available operators:

**`user` / `created_by` type fields:**
- Only the `contains` operator is allowed
- Exact-match operators such as `is` and `isNot` are not allowed
- This is the current member matching mode; there is no need to fill in a specific member value in the filter condition; do not write a name or user ID into `filter_values`

**`select` (`multiple=false`) type fields:**
- The `is` and `isNot` operators are only allowed for matching a **single option** and must not be used for multiple values
- When the user expresses "the field value equals/does not equal one specific option" (such as "attendance status does not equal present"), the Agent must use `is` / `isNot`, and filter_values contains only a single value.
- When the user expresses "the field value equals/does not equal a set of multiple options" (such as "education is not associate degree and others"), the Agent must use `contains` / `doesNotContain`, and put multiple options into filter_values.
- filter_values in `contains` / `doesNotContain` may contain multiple values, representing an OR relationship

**`select` (`multiple=true`) type fields:**
- `is` / `isNot`: filter_values allows multiple options to be filled in
  - When operator = is and A and B are checked, the semantics are that the field **contains both** A and B (A&B), not "equals A or equals B"
  - When the user expresses "contains any option", in addition to using contains, it can also be implemented using is together with filter_rules.conjunction = or
- `contains` / `doesNotContain`: used to express "contains any option / does not contain any option"; filter_values may contain multiple options (the system handles it as "any match"); to express "equals A or equals B", it should be split into multiple filter conditions and combined with "or".

**Percentage fields**
- For "number" filter conditions in query, if percentages are involved, restore the value the user gave you exactly as is (percentages all become decimals). For example, "greater than 20%" becomes "greater than 0.2", and "xx rate less than 60" becomes "less than 0.6".

<a id="被用于筛选的字段的-field_perms-权限强制要求"></a>
### Mandatory field_perms Permission Requirements for Fields Used in Filtering

When a field (system fields do not have this requirement) is used in a filter condition in "records that meet specific conditions", the system will automatically impose the following **immutable constraints** based on the current data table permissions and record permissions:

**Read-write consistency of filter fields:**
- If the table permission is edit and the field type belongs to [editable fields], the filter field must retain edit permission unless the user explicitly requests a downgrade.
- It is strictly prohibited to downgrade a field to read merely because it is used as a filter condition. Filter conditions only require the field to be visible, not read-only.

**Minimum field permission when adding records:**
- If and only if the record permission includes "can add records", the field must be at least creatable (create), to ensure that filter condition fields can be written correctly when adding records.
- If the current record permission is "read only", this constraint is not triggered.

**Whether a field is editable (edit) is not a mandatory requirement**; it is determined by the specific permission scheme and is not within the scope of infra mandatory constraints.

The field permissions automatically imposed by the system above cannot be manually removed or downgraded.
