<a id="base-filter-条件结构公共协议"></a>
# Base Filter Condition Structure (Common Protocol)

A Filter is a combination of "field/operator/value" conditions, using `logic` (`and` / `or`) to connect multiple `conditions` entries, used to describe "what conditions must be met". View filters `filter`, record read/search `--filter-json`, and form question show/hide conditions `visible_rule` all reuse the same tuple structure; this file is their common protocol (SSOT).

<a id="0-适用范围"></a>
## 0. Scope of Application

This protocol applies only to the following scenarios:

- View filter configuration for `+view-set-filter` / `+view-get-filter`.
- Structured record filtering for `+record-list --filter-json` / `+record-search --filter-json`.
- `visible_rule` show/hide conditions in `+form-questions-create` / `+form-questions-update`.

This protocol **does not apply to `+data-query`**. `+data-query` supports filtering, but uses the LiteQuery DSL `filters` object structure: `{"type":1,"conjunction":"and","conditions":[{"field_name":"状态","operator":"is","value":["有效"]}]}`, not the tuple condition `["状态","==","有效"]` here. When aggregate queries are needed, first return to [Record Query and Analysis SOP](lark-base-record-query-and-analysis-sop.md) for routing; after the SOP selects `+data-query`, then read the guide and the complete DSL reference.

<a id="1-顶层结构"></a>
## 1. Top-Level Structure

- Must be a JSON object.
- The top-level structure is `{logic?, conditions?}`.
- `logic` defaults to `and`; it is recommended to use only the canonical values `and` / `or`.
- `conditions` defaults to an empty array.
- Each condition is written as a tuple: `[field, operator, value?]`.
- `empty` / `non_empty` can be written as 2 items: `[field, "empty"]`, `[field, "non_empty"]`.

```json
{
  "logic": "and",
  "conditions": [
    ["状态", "intersects", ["Doing"]],
    ["负责人", "intersects", [{ "id": "ou_xxx" }]],
    ["截止时间", "empty"]
  ]
}
```

Clearing syntax:

```json
{
  "conditions": []
}
```

<a id="2-单表谓词下推常用-example"></a>
## 2. Common Examples of Single-Table Predicate Pushdown

The `--filter-json '<filter-json>'` of `+record-list` / `+record-search` also supports using the same tuple condition as views. The following examples use comments to explain the meaning of each condition; when actually passing parameters, delete the comments and use standard JSON:

```jsonc
{
  "logic": "and", // All conditions must hold simultaneously; use "or" when any one holding is sufficient
  "conditions": [
    ["标题", "==", "Launch plan"], // Exact text match
    ["标题", "!=", "Archived plan"], // Text not exactly equal
    ["标题", "intersects", "urgent"], // Text contains the target fragment
    ["标题", "disjoint", "internal"], // Text does not contain the target fragment
    ["金额", ">=", 100], // Numeric comparison; supports ==, !=, >, >=, <, <=
    ["状态", "intersects", ["进行中", "暂停"]], // Select set intersection: contains either "In Progress" or "Paused"
    ["状态", "disjoint", ["已终止"]], // Select sets have no intersection
    ["已完成", "==", true], // Checkbox
    ["负责人", "intersects", [{ "id": "ou_xxx" }]], // Assignee contains a certain person; intersects means contains any one person in the array
    ["负责人", "disjoint", [{ "id": "ou_yyy" }]], // Assignee does not contain any of the specified persons
    ["关联项目", "intersects", [{ "id": "recxxx" }]], // Linked project contains a certain record_id; intersects means contains any one link in the array
    ["备注", "non_empty"], // Cell is not empty; to check that a cell is empty, use ["Notes", "empty"] instead
    ["业务日期", "==", "ExactDate(2026-08-07)"], // A specific day: matches the day 2026-08-07 according to the Base timezone
    ["发生时间", ">", "ExactDate(2024-01-31 23:59:59.999)"], // Dates do not support >=; use > the last millisecond of the previous day to express an inclusive lower bound for the current day
    ["发生时间", "<", "ExactDate(2024-03-01 00:00:00)"] // Upper bound of the February 2024 range: less than midnight of March 1
  ]
}
```

## 3. operator

Available operators:
- `==`
- `!=`
- `>`
- `>=`
- `<`
- `<=`
- `intersects`
- `disjoint`
- `empty`
- `non_empty`

<a id="4-value-写法"></a>
## 4. value Syntax

The value type depends on the type of the referenced object (field / question).

### `text`

Use a string; for high-frequency fragment inclusion / exclusion use `intersects` / `disjoint`, and for full text comparison use `==` / `!=`:

```json
["标题", "intersects", "发布"]
```

```json
["标题", "disjoint", "内部"]
```

### `location`

location filtering only matches by `full_address` string, and cannot filter directly by latitude/longitude; prefer using `intersects` for inclusion matching, for example to search for Shenzhen:

```json
["位置", "intersects", "深圳"]
```

### `number` / `auto_number`

Use a number:

```json
["工时", ">=", 3.5]
```

### `select`

Use an array of option names; `intersects` means matching any option, `disjoint` means not containing any of the options:

```json
["状态", "intersects", ["Doing", "Blocked"]]
```

```json
["状态", "disjoint", ["Archived"]]
```

### `user` / `group_chat` / `created_by` / `updated_by`

Use an array of objects; for people use `ou_xxx`, for groups use `oc_xxx`. When the ID is unknown, query people with `lark-contact`, and search groups with `lark-im`.

```json
["负责人", "intersects", [{ "id": "ou_xxx" }]]
```

```json
["负责人", "disjoint", [{ "id": "ou_xxx" }]]
```

```json
["负责群", "intersects", [{ "id": "oc_xxx" }]]
```

### `link`

Use an array of record id objects:

```json
["关联任务", "intersects", [{ "id": "recxxx" }]]
```

### `checkbox`

Use a boolean value:

```json
["完成", "==", true]
```

### `datetime` / `created_at` / `updated_at`

Use a relative time keyword or `ExactDate(...)`:

```json
["截止时间", "==", "ExactDate(2026-01-01)"]
```

```json
["截止时间", "==", "ExactDate(2026-01-01 11:30)"]
```

```json
["截止时间", "==", "Today"]
```

Available keywords:
- `Today`
- `Yesterday`
- `Tomorrow`

### `formula` / `lookup`

The value schema varies with the result calculation type; when unsure, first read the field definition, or correct the value and operator based on the error message.

<a id="5-易错点"></a>
## 5. Common Pitfalls

- Do not write the old object style again: `{"field_name":...,"operator":...}`.
- `user` / `group_chat` / `link` must not be written as a single scalar.
- `empty` / `non_empty` uniformly indicate that a cell is empty / not empty; do not pass a value; a scalar empty cell and a multi-value field with no elements at all both count as empty.
- For stable date condition syntax, use `ExactDate(...)` or `Today` / `Yesterday` / `Tomorrow`.
- The value schema of `formula` / `lookup` is dynamic; when unsure about the value type, first read the field definition, or correct the type based on the error message.

<a id="6-参考"></a>
## 6. References
- [Lookup Field](lark-base-field-lookup.md)
