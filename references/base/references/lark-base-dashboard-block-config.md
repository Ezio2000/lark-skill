<a id="base-dashboard-block-配置"></a>
# Base Dashboard Block Configuration

The `data_config` field of a Block varies by `type`. This document is the single source of truth (SSOT) for the Dashboard block flat single-data-source `data_config`, covering component types, field structures, filter formats, constraints, and copyable templates. The outer structure of BaseApp charts differs, but each `data_sources[]` element reuses the field values, filters, grouping, sorting, and normalization rules in this document; when creating or updating App components, you must also read [BaseApp Block data_config](lark-base-app-block-data-config.md) to learn about the shared `base_token`, multi-data-source wrapping, and the App-specific list component protocol.

<a id="支持的组件类型type-枚举"></a>
## Supported Component Types (`type` Enum)

| type value | Description |
|---------|------|
| `column` | Column chart |
| `bar` | Bar chart |
| `line` | Line chart |
| `pie` | Pie chart |
| `ring` | Donut chart |
| `area` | Area chart |
| `combo` | Combo chart |
| `scatter` | Scatter chart |
| `funnel` | Funnel chart |
| `wordCloud` | Word cloud |
| `radar` | Radar chart |
| `ranking` | Ranking list |
| `statistics` | Metric card |
| `nps` | NPS chart |
| `text` | Text (supports Markdown) |

<a id="字段类型与操作符速查ai-决策用"></a>
## Field Types and Operators Quick Reference (for AI Decision-Making)

> First use `+field-list` / `+field-get` to confirm the field `type`; this section uses the canonical type names from the current field API: `number`, `text`, `select`, `datetime`, `checkbox`, `user`. The `Rating` used by NPS is the rating field semantics recognized by the Dashboard server, and is not a general filter type in the current field operator quick reference.

```
text: is, isNot, contains, doesNotContain, isEmpty, isNotEmpty
number: is, isNot, isGreater, isGreaterEqual, isLess, isLessEqual, isEmpty, isNotEmpty
select（multiple=false）: is, isNot, isEmpty, isNotEmpty
select（multiple=true）: is, isNot, contains, doesNotContain, isEmpty, isNotEmpty
datetime: is, isGreater, isLess, isEmpty, isNotEmpty
checkbox: is (value: true/false)
user / created_by / updated_by: is, isNot, isEmpty, isNotEmpty
```

`isGreaterEqual` / `isLessEqual` are not globally unsupported: they can be used for `number`, but cannot be used for `datetime` / `created_at` / `updated_at`. Date ranges must use `isGreater` / `isLess` together with `ExactDate`; do not apply the operator set for numeric fields to date fields.

<a id="data_config-通用结构"></a>
## data_config General Structure

| Field | Type | Description |
|------|------|------|
| `table_name` | string | Name of the associated data table |
| `series` | `[{ "field_name": "xxx", "rollup": "SUM" }]` | Metric/Y-axis (choose one of this and `count_all`). rollup supports `SUM` / `MAX` / `MIN` / `AVERAGE` |
| `count_all` | boolean | COUNTA aggregation, counts all records (choose one of this and `series`) |
| `group_by` | `[{ "field_name": "xxx", "mode": "integrated", "sort": {...} }]` | X-axis grouping dimension. The requirements for `mode` and `sort` vary by component type, see the description below |
| `filter` | object | Filter conditions |
| `filter.conjunction` | `"and"` / `"or"` | Filter logic |
| `filter.conditions` | `[{ "field_name", "operator", "value" }]` | Array of filter conditions, value type varies by field type (see the filter format rules below) |
| `category_range` | `[min, detractorMax, passiveMax, max]` | NPS three-segment boundaries, only supported by the `nps` type; the first and last must equal the Rating field range, and the first/last match is validated by the server based on field metadata |

<a id="text-类型特殊结构"></a>
### text Type Special Structure

The `text` type component is used to display rich text content and **does not require data source configuration** (no `table_name`, `series`, `group_by`, `filter`).

| Field | Type | Description |
|------|------|------|
| `text` | string | **Required**. Supports Markdown syntax, see the description below |

**Supported Markdown syntax:**

| Syntax | Example | Effect |
|------|------|------|
| Level 1 heading | `# 标题` | Large heading |
| Level 2 heading | `## 标题` | Medium heading |
| Level 3 heading | `### 标题` | Small heading |
| Bold | `**文字**` | **text** |
| Italic | `*文字*` | *text* |
| Strikethrough | `~~文字~~` | ~~text~~ |
| Ordered list | `1. 项目` | 1. item |
| Unordered list | `- 项目` | - item |

> **Note**: Markdown syntax not mentioned above (such as links, images, code blocks, tables, etc.) is not supported.

<a id="group_by-详细说明"></a>
## group_by Detailed Description

<a id="mode-枚举"></a>
### mode Enum

| mode | Meaning | Applicable Scenario |
|------|------|----------|
| `integrated` | Aggregate grouping (default) | Most scenarios, group and count by field value |
| `enumerated` | Multi-value split counting | Multi-value fields such as multi-select and person, splitting each option/person for independent counting |

> Multi-value fields such as multi-select and person use `enumerated` by default; other fields use `integrated` by default.

<a id="sort-排序"></a>
### sort Sorting

| sort.type | Meaning | Typical Scenario |
|-----------|------|----------|
| `group` | Sort by horizontal axis value | Ascending by month, alphabetical by category name |
| `value` | Sort by vertical axis value | Sales amount from largest to smallest |
| `view` | Sort by data source record order | Preserve the original table row order (not commonly used) |

`sort.order`: `asc` (ascending) / `desc` (descending)

Whenever you write a `sort` object, you need to specify the sort direction explicitly. The CLI normalizes cases where `sort.type` is `group` or `view` and `order` is missing to `order:"asc"`; `sort.type:"value"` must explicitly write `order:"asc"` or `order:"desc"`, because the metric value sort direction changes the business meaning.

If the table row order is the business order, set `sort:{"type":"view","order":"asc"}` once when first creating the block to preserve row order, avoiding a second update of the sort condition after creation.

<a id="ranking-排行榜专属契约"></a>
### ranking Ranking-Specific Contract

The ranking list supports only one grouping and one metric, and the public fields are fixed as `table_name`, `series`/`count_all`, `group_by`, `filter`, `limit_size`:

- `group_by` is required and its length must be strictly 1; `mode` supports only `integrated` / `enumerated`.
- `series` length must be strictly 1, and choose one of this and `count_all:true`; `rollup` supports only `SUM` / `MAX` / `MIN` / `AVERAGE`.
- Sorting is written only in `group_by[0].sort`, `type` can only be `value`, and `order` is `asc` / `desc`. When omitted at creation, sorting defaults to descending by metric value.
- `limit_size` is Top N, with a value of an integer from `1..500`; when omitted at creation, it defaults to `10`.
- Top-level `sort`, public `ranking` objects, or avatar toggles are not supported.

When updating `ranking`, `data_config` is a top-level patch: passing only `limit_size` changes only Top N; passing only `group_by` replaces only the single grouping and sorting; passing only `series` or `count_all:true` switches only the metric; passing only `filter` replaces only the filter. When switching `table_name`, you must provide the new `group_by` and `series` or `count_all:true` in the same patch; if `filter` is not passed, the original filter is retained, and if `limit_size` is not passed, the original Top N is retained.

Example — column chart sorted descending by sales amount:

```json
{
  "table_name": "订单表",
  "series": [{ "field_name": "金额", "rollup": "SUM" }],
  "group_by": [{ "field_name": "类别", "mode": "integrated", "sort": {"type": "value", "order": "desc"} }]
}
```

<a id="filter-格式规则"></a>
## filter Format Rules

**Basic structure:**

```json
{
  "filter": {
    "conjunction": "and",
    "conditions": [
      { "field_name": "字段名", "operator": "操作符", "value": "值" }
    ]
  }
}
```

**Multi-condition example (and/or):**

```json
{
  "filter": {
    "conjunction": "and",
    "conditions": [
      { "field_name": "状态", "operator": "is", "value": "已完成" },
      { "field_name": "金额", "operator": "isGreater", "value": 1000 }
    ]
  }
}
```

**Operators:**

| Operator | Meaning | Requires value |
|--------|------|---------------|
| `is` | Equals | Yes |
| `isNot` | Not equals | Yes |
| `contains` | Contains | Yes |
| `doesNotContain` | Does not contain | Yes |
| `isEmpty` | Is empty | No |
| `isNotEmpty` | Is not empty | No |
| `isGreater` | Greater than | Yes |
| `isGreaterEqual` | Greater than or equal to | Yes |
| `isLess` | Less than | Yes |
| `isLessEqual` | Less than or equal to | Yes |

**value format for each field type:**

| Field Type | value Type | Applicable Operators | Example |
|----------|-----------|-----------|------|
| `text` | string | is, isNot, contains, doesNotContain, isEmpty, isNotEmpty | `{"field_name":"姓名","operator":"contains","value":"张"}` |
| `number` | number | is, isNot, isGreater, isGreaterEqual, isLess, isLessEqual, isEmpty, isNotEmpty | `{"field_name":"金额","operator":"isGreater","value":0}` |
| `select` (`multiple=false`) | string (option name) | is, isNot, isEmpty, isNotEmpty | `{"field_name":"状态","operator":"is","value":"已完成"}` |
| `select` (`multiple=true`) | string[] (multiple selected) / string (single selected) | is, isNot, contains, doesNotContain, isEmpty, isNotEmpty | For multi-select pass an array such as `["标签1","标签2"]`; for single-select pass a single string |
| `datetime` / `created_at` / `updated_at` | `["ExactDate", Unix 毫秒时间戳]` | is, isGreater, isLess, isEmpty, isNotEmpty | `{"field_name":"创建日期","operator":"isGreater","value":["ExactDate",1704038400000]}` |
| `checkbox` | boolean | is | `{"field_name":"已审核","operator":"is","value":true}` |
| `user` / `created_by` / `updated_by` | string or string[] (user ID, format `ou_xxx`). If you do not know the `open_id`, first use `lark-cli contact +search-user --query "<姓名/邮箱/手机号>" --as user` to look up the id. | is, isNot, isEmpty, isNotEmpty | `{"field_name":"负责人","operator":"is","value":"ou_xxxxxxxxxxxxxxxx"}` |
| All types (empty/not empty) | value not required | isEmpty, isNotEmpty | `{"field_name":"备注","operator":"isEmpty"}` |

> The `value` type varies by field and can be `string | number | boolean | string[] | ["ExactDate", number]`, and must be constructed according to the table above.

<a id="日期筛选"></a>
### Date Filtering

When a chart `data_config.filter` filters `datetime` / `created_at` / `updated_at` fields:

- Value conditions can only use `is`, `isGreater`, or `isLess`, and must not use `isGreaterEqual` or `isLessEqual`.
- `value` must be written as `["ExactDate", <Unix 毫秒时间戳>]`, and a bare timestamp must not be passed directly.
- `isEmpty` / `isNotEmpty` do not pass `value`.

Date range example:

```json
{
  "filter": {
    "conjunction": "and",
    "conditions": [
      {
        "field_name": "派单日期",
        "operator": "isGreater",
        "value": ["ExactDate", 1785686400000]
      },
      {
        "field_name": "派单日期",
        "operator": "isLess",
        "value": ["ExactDate", 1786032000000]
      }
    ]
  }
}
```

<a id="约束与本地校验"></a>
## Constraints and Local Validation

- Required and mutually exclusive
  - Required for chart types: `table_name`
  - Required for text type: `text`
  - Mutually exclusive: choose one of `series` and `count_all`, and provide at least one of them (chart types only)
  - Required for nps type: `table_name`, `group_by` of length 1; `group_by[0].mode` can be omitted, and when omitted it is treated as `integrated`; when explicitly passed it can only be `integrated`; `group_by[0].sort` and `series` are not supported; `count_all` can be omitted, and when present it can only be `true`
  - text type **does not support**: `series`, `count_all`, `group_by`, `filter`
- Length/structure
  - `group_by` at most 2; each `field_name` is required
  - `group_by[].sort.type` takes the value `group|value|view`; `order` takes the value `asc|desc`
- Normalization (handled automatically by the CLI; does not take effect when `--no-validate`, and `data_config` is passed through to the backend as-is)
  - `series[].rollup` is automatically converted to uppercase (e.g., `sum` → `SUM`)
  - `group_by[].sort.type/order` is automatically converted to lowercase
  - When `group_by[].sort.type` is `group` or `view` and `order` is missing, `order:"asc"` is automatically added; `value` sorting does not automatically add a direction
- Local validation (can be skipped via `--no-validate`)
  - `+dashboard-block-create` performs lightweight validation on `data_config` by default; on failure it aggregates errors and provides fix suggestions
  - `+dashboard-block-update` does not carry `--type`, so it does not perform strict validation by component type; but it does perform lightweight validation on parseable `filter` conditions, including `conjunction`, field references, `operator`, and the required `value`, and blocks illegal `number_format` subfields just like create (see the number_format section below)
  - Only valid JSON needs to be passed in; the CLI will not arbitrarily rewrite your business meaning

<a id="可复制模板"></a>
## Copyable Templates

**Choose a template by intent:**
- Compare values across different categories → Column chart / Bar chart
- See trend changes → Line chart / Area chart
- See proportion distribution → Pie chart / Donut chart / Word cloud
- Multi-metric comparison → Combo chart
- See the relationship between two variables → Scatter chart
- See process conversion → Funnel chart
- See multi-dimensional ratings → Radar chart
- Display a single metric → Metric card (statistic or record count)
- Count satisfaction rating distribution → NPS chart (one Rating field + optional segments)
- View Top N for a single dimension → Ranking list

Minimal column chart:

```json
{
  "table_name": "表名",
  "series": [{ "field_name": "数值字段", "rollup": "SUM" }],
  "group_by": [{ "field_name": "分组字段", "mode": "integrated" }]
}
```

Minimal pie chart/donut chart (count row proportion by category field):

```json
{
  "table_name": "表名",
  "count_all": true,
  "group_by": [{ "field_name": "分类字段", "mode": "integrated" }]
}
```

Line chart (monthly trend):

```json
{
  "table_name": "表名",
  "series": [{ "field_name": "金额", "rollup": "SUM" }],
  "group_by": [{ "field_name": "月份", "mode": "integrated", "sort": {"type":"group","order":"asc"} }]
}
```

Bar chart (horizontal column chart):

```json
{
  "table_name": "表名",
  "series": [{ "field_name": "数值字段", "rollup": "SUM" }],
  "group_by": [{ "field_name": "分组字段", "mode": "integrated" }]
}
```

Area chart (trend fill):

```json
{
  "table_name": "表名",
  "series": [{ "field_name": "数值字段", "rollup": "SUM" }],
  "group_by": [{ "field_name": "时间字段", "mode": "integrated", "sort": {"type":"group","order":"asc"} }]
}
```

Combo chart (multi-metric comparison such as columns + lines):

```json
{
  "table_name": "表名",
  "series": [
    { "field_name": "指标1", "rollup": "SUM" },
    { "field_name": "指标2", "rollup": "SUM" }
  ],
  "group_by": [{ "field_name": "分类字段", "mode": "integrated" }]
}
```

Scatter chart (correlation between two variables):

```json
{
  "table_name": "表名",
  "series": [{ "field_name": "Y轴字段（数值/指标）", "rollup": "SUM" }],
  "group_by": [{ "field_name": "X轴字段（分类/维度）", "mode": "integrated" }]
}
```

Funnel chart (process conversion):

First determine the numeric semantics the user wants to see:

- **Current count**: count how many records are in each current status/stage, for example "current count at each step" or "current stage distribution". When the source table has a status/stage field, directly use `count_all:true` + `group_by`.
- **Cumulative count**: count the cumulative number that reached that stage and its subsequent stages (suffix sum), for example "process conversion" or "conversion at each step from A to B". This definition assumes the process is unidirectional, with no stage skipping/rollback, and that records are not deleted; if these do not hold, you must use status change history and cannot accumulate over the current snapshot. If the table already has a cumulative count field or a stage summary table, directly use that field to draw the funnel chart; otherwise first calculate the cumulative count, create and write to a helper summary table, and then draw the chart.

Current count:

```json
{
  "table_name": "表名",
  "count_all": true,
  "group_by": [{ "field_name": "状态字段", "mode": "integrated" }]
}
```

Cumulative count:

```json
{
  "table_name": "流程汇总表名",
  "series": [{ "field_name": "累计数量", "rollup": "SUM" }],
  "group_by": [{ "field_name": "阶段字段", "mode": "integrated", "sort": {"type":"view","order":"asc"} }]
}
```

If there is only current status data but the user wants to see process conversion, you need to first calculate the cumulative count for each stage in business stage order, then create a helper summary table (such as: stage, cumulative count), write it in one call with `+record-batch-create`, and then create the funnel chart according to the "cumulative count" template. If the helper table row order is the business order, set `group_by.sort` once when first creating the block.

> ⚠️ Note: the helper summary table is only used for scenarios where the source table cannot directly aggregate the target shape (such as the cumulative count funnel chart above). As long as it can be calculated directly on the source table using `group_by` + `rollup` (including `AVERAGE`), there is no need to create a new helper table.

Word cloud (text frequency):

```json
{
  "table_name": "表名",
  "count_all": true,
  "group_by": [{ "field_name": "文本字段", "mode": "integrated" }]
}
```

Radar chart (multi-dimensional ratings):

```json
{
  "table_name": "表名",
  "series": [
    { "field_name": "维度1", "rollup": "SUM" },
    { "field_name": "维度2", "rollup": "SUM" },
    { "field_name": "维度3", "rollup": "SUM" }
  ],
  "group_by": [{ "field_name": "分类字段", "mode": "integrated" }]
}
```

Ranking list (Top 10 by sales amount):

```json
{
  "table_name": "订单表",
  "series": [{ "field_name": "金额", "rollup": "SUM" }],
  "group_by": [{ "field_name": "负责人", "mode": "integrated", "sort": {"type":"value","order":"desc"} }],
  "limit_size": 10
}
```

Ranking list updating only Top N:

```json
{"limit_size": 20}
```

Metric card (statistic):

```json
{
  "table_name": "数据表",
  "series": [{ "field_name": "数字", "rollup": "SUM" }]
}
```

NPS chart (count records by Rating field):

```json
{
  "table_name": "问卷结果",
  "group_by": [{ "field_name": "满意度评分", "mode": "integrated" }],
  "category_range": [0, 6, 8, 10]
}
```

The NPS `group_by[0].field_name` must point to the Base rating field (recognized internally by Dashboard as `Rating` semantics). The caller can confirm the minimum and maximum values of the rating field through the Base field details or the UI field configuration; the CLI can only perform lightweight JSON validation, and the field type, field range, and whether the first and last values of `category_range` equal the minimum and maximum values of the rating field are validated by the server based on field metadata.

`category_range` can be omitted, and the server will generate default segments according to the Rating field's own range. When explicitly passed, the array length must be 4, and the first and last values must equal the minimum and maximum values of the Rating field.

Metric card (record count):

```json
{
  "table_name": "数据表",
  "count_all": true
}
```

<a id="statistics-指标卡数值格式-number_format可选"></a>
### statistics metric card number format number_format (optional)

Only `type: statistics` supports adding an optional `data_config` inside `number_format`, controlling the numeric display format and precision; when not provided, the server fills in `{"formatName":"digital"}`, and `precision` remains omitted. Other component types do not support this field: create will be directly rejected by the CLI (explicit `--no-validate` can skip this), avoiding deferring backend strict schema errors to the request stage; update does not carry `--type`, and the server decides based on the component's existing type.

- `formatName` (string, optional): must exactly match one of the 5 enums in the table below, **case-sensitive** (unlike `series[].rollup`, which is automatically converted to uppercase, no normalization is done here, and `DIGITAL` will be rejected).
- `precision` (integer, optional): number of decimal places, an integer from `0` to `9`; non-integers such as `2.5` will be rejected locally.

| formatName | Meaning | Example (precision=2) |
|------------|------|--------------------|
| `digital` | Thousands-separated number (server default when `number_format` is not provided) | `1,234.56` |
| `digital_without_separator` | Number without thousands separator | `1234.56` |
| `percentage_rounded` | Percentage | `1,234.56%` |
| `cyn_rounded` | CNY amount | `¥1,234.56` |
| `dollar_rounded` | USD amount | `$1,234.56` |

Metric card (amount, keep 2 decimal places):

```json
{
  "table_name": "订单表",
  "series": [{ "field_name": "金额", "rollup": "SUM" }],
  "number_format": { "formatName": "dollar_rounded", "precision": 2 }
}
```

> **On update, `number_format` is merged by subfield**: for example, when the existing `{"formatName":"digital","precision":2}` only passes `{"number_format":{"precision":0}}`, the server keeps `formatName:"digital"` and changes the precision to `0`. For the update strategy of other top-level keys, see [lark-base-dashboard.md](lark-base-dashboard.md).

Text component (Markdown rich text):

```json
{
  "text": "# 🚀 一级标题\n这是一个 **加粗** *斜体* ~~删除线~~ 的示例。\n\n## 📌 二级标题\n1. 有序列表项 1\n2. 有序列表项 2\n\n### 📌 三级标题\n- 无序列表项 1\n- 无序列表项 2"
}
```

> **Note**: text-type components do not need data source-related fields such as `table_name`, `series`, `group_by`, `filter`.

<a id="常见错误与修复"></a>
## Common Errors and Fixes

- Both `series` and `count_all` exist
  - Symptom: backend/local validation reports a mutual exclusion error
  - Fix: see the either/or rule in the "Key Constraints" section
- Missing `table_name`
  - Symptom: local validation reports a missing required field
  - Fix: specify the data source table name (use the table name, not the table ID)
- `series[].rollup` case/value is invalid
  - Symptom: local validation reports an unsupported enum
  - Fix: change to one of `SUM|MAX|MIN|AVERAGE` (case-insensitive, the CLI normalizes to uppercase; for counting, use `count_all:true`)
- `group_by` exceeds 2 or the field name is empty
  - Fix: keep the first 2, or fill in `field_name`
- Invalid sort enum
  - Fix: `group_by.sort.type` can only be `group|value|view`; `order` is `asc|desc`
- filter syntax is nonstandard
  - Fix: `conjunction` takes `and|or`; `conditions[].operator` must be within the range listed in the table on this page; except for `isEmpty/isNotEmpty`, `value` must be provided

<a id="坑点"></a>
## Pitfalls

- **Choose one of `count_all` and `series`** — the two cannot be used at the same time
- **filter `value` type varies by field** — text/single select is string, number is number, date is a millisecond timestamp, multi-select/person can be string[], checkbox is boolean; `isEmpty`/`isNotEmpty` do not need value
- **`data_config` structure varies with `type`** — different component types have different fields; before creating, be sure to confirm the fields corresponding to the type
- **Table name uses name, not ID** — `table_name` corresponds to the table name (such as "Orders table"), not `table_id`
