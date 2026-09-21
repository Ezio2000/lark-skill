# Base Field Schema

> Applicable commands: `lark-cli base +field-create`, `lark-cli base +field-update`

This document defines the recommended format of `--json` when writing fields with `+field-create` / `+field-update`, and is the source of truth for field types and field JSON structure. The goal is not to replicate the complete schema, but to enable the agent to reliably produce correct payloads.

<a id="1-顶层规则必须遵守"></a>
## 1. Top-level rules (must be followed)

- A single field definition is always a JSON object, and every field object uniformly uses: `type` + `name` + type-specific fields.
- `+field-create --json` accepts a single field object or a non-empty array of field objects.
- `+field-update --json` accepts only a single field object.
- All field types support the optional `description`; plain text is supported, as are Markdown links.
- Field default values use `default_value`, passing the corresponding CellValue directly; the supported scope is only `text`, `number`, static `select`, `datetime`, `user`. To clear the default value, pass `null`; omitting it at creation time means it is not set.
- Do not use the old structures: `field_name`, `property`, `ui_type`, numeric enum `type`.
- `+field-update` is an override-style full replacement of `PUT`, not a partial update; first use `+field-get` to read the current definition, modify the target properties based on it, and write back the entire field's writable configuration that needs to be preserved in full, while including `--yes`.
- Before creating/updating with `type=formula` or `type=lookup`, you must first read the corresponding guide.

Recommended example:

```json
{
  "type": "text",
  "name": "需求背景",
  "description": "记录需求背景与已知约束"
}
```

<a id="2-字段速查"></a>
## 2. Field quick reference

| Type | Minimum required fields | Common supplementary fields |
|------|--------------|-------------|
| `text` | `type` `name` | `style.type` `default_value` |
| `number` | `type` `name` | `style` `default_value` |
| `select` | `type` `name` | `multiple` + `options` + static `default_value`, or `multiple` + `dynamic_options_source` |
| `datetime` | `type` `name` | `style.format` `default_value` |
| `created_at` / `updated_at` | `type` `name` | `style.format` |
| `user` / `group_chat` | `type` `name` | `multiple`; only `user` supports `default_value` |
| `created_by` / `updated_by` | `type` `name` | None |
| `link` | `type` `name` `link_table` | `bidirectional` `bidirectional_link_field_name` |
| `formula` | `type` `name` `expression` | None |
| `lookup` | `type` `name` `from` `select` `where` | `aggregate` |
| `auto_number` | `type` `name` | `style.rules` |
| `attachment` / `location` / `checkbox` | `type` `name` | None |
| `button` | `type` `name` `button_config.title` | None |

All types can additionally pass `description`; the "common supplementary fields" in the table above list only type-specific configuration.

<a id="3-各类型写法"></a>
## 3. How to write each type

### 3.1 text

Text field; phone, hyperlink, email, and barcode also belong to `text`, distinguished via `style.type`.
Supports `default_value`: static Markdown text string; `phone` style must be a valid phone number; `url` style passes a Markdown link or bare URL; `email` style must be a valid email string, do not pass a Markdown link or `mailto:`.

Minimal form (default `style.type` is `plain`):

```json
{
  "type": "text",
  "name": "标题",
  "default_value": "默认标题"
}
```

Common form:

The default value can be Markdown text
```json
{
  "type": "text",
  "name": "标题",
  "description": "主标题字段",
  "default_value": "未命名"
}
```

When `style.type=phone`, the default value is a valid phone number string.
```json
{
  "type": "text",
  "name": "联系电话",
  "style": { "type": "phone" },
  "default_value": "+8613800000000"
}
```

```json
{
  "type": "text",
  "name": "官网",
  "style": { "type": "url" },
  "default_value": "[官网](https://example.com)"
}
```

```json
{
  "type": "text",
  "name": "邮箱",
  "style": { "type": "email" },
  "default_value": "owner@example.com"
}
```

Common `style.type`: `plain` (default), `phone`, `url`, `email`, `barcode`.

### 3.2 number

Number field; currency, progress, and rating also belong to `number`, distinguished via `style.type`.
Supports `default_value`: static JSON number; all number styles are written according to this rule.

Minimal form (default `style.type` is `plain`):

```json
{
  "type": "number",
  "name": "工时",
  "default_value": 8
}
```

`style` is an object distinguished by `type`; different `style.type` have different internal fields, do not mix them up.

#### `plain`

Supported fields: `precision`, `percentage`, `thousands_separator`

Default values / constraints:
- `precision` takes values `0..4`, default `2`
- `percentage` default `false`
- `thousands_separator` default `false`

```json
{
  "type": "number",
  "name": "工时",
  "style": {
    "type": "plain",
    "precision": 2,
    "percentage": false,
    "thousands_separator": true
  },
  "default_value": 8
}
```

#### `currency`

Supported fields: `precision`, `currency_code`

Default values / constraints:
- `precision` takes values `0..4`, default `2`
- `currency_code` required, such as `CNY`, `USD`, `EUR`

```json
{
  "type": "number",
  "name": "预算",
  "style": { "type": "currency", "precision": 2, "currency_code": "CNY" }
}
```

#### `progress`

Supported fields: `percentage`, `color`

Default values / constraints:
- `percentage` default `true`
- `color` required
- `color` available: `Blue`, `Purple`, `DarkGreen`, `Green`, `Cyan`, `Orange`, `Red`, `Gray`, `WhiteToBlueGradient`, `WhiteToPurpleGradient`, `WhiteToOrangeGradient`, `GreenToRedGradient`, `RedToGreenGradient`, `BlueToPinkGradient`, `PinkToBlueGradient`, `SpectralGradient`

```json
{
  "type": "number",
  "name": "完成度",
  "style": { "type": "progress", "percentage": true, "color": "Blue" },
  "default_value": 0.65
}
```

#### `rating`

Supported fields: `icon`, `min`, `max`

Default values / known platform scope:
- `icon` default `star`
- `icon` available: `star`, `heart`, `thumbsup`, `fire`, `smile`, `lightning`, `flower`, `number`
- `min` takes values `0..1`, default `1`
- `max` takes values `1..10`, default `5`

```json
{
  "type": "number",
  "name": "评分",
  "style": { "type": "rating", "icon": "star", "min": 1, "max": 5 }
}
```

### 3.3 select

Both single-select and multi-select use `select`; distinguished via `multiple`. `multiple` defaults to `false`. Static options use `options`, dynamic options use `dynamic_options_source`; do not pass both at the same time.

<a id="静态选项"></a>
#### Static options

Supported fields: `multiple`, `options`
Supports `default_value`: array of static option names; even for `multiple=false`, write an array, such as `["Todo"]`.

Default values / constraints:
- `multiple` default `false`
- `options` at most `10000` items
- `options[]` structure is `{name, hue?, lightness?}`
- `options[].name` required
- `options[].hue` available: `Red`, `Orange`, `Yellow`, `Lime`, `Green`, `Turquoise`, `Wathet`, `Blue`, `Carmine`, `Purple`, `Gray` default value is `Blue`
- `options[].lightness` available: `Lighter`, `Light`, `Standard`, `Dark`, `Darker` default value is `Lighter`
- Options do not have `id`, only `name`.
- Supports `default_value` configuration: fill in an array of option names.

```json
{
  "type": "select",
  "name": "状态",
  "multiple": false,
  "default_value": ["Todo"],
  "options": [
    { "name": "Todo", "hue": "Blue", "lightness": "Lighter" },
    { "name": "Done", "hue": "Green", "lightness": "Light" }
  ]
}
```

<a id="动态选项"></a>
#### Dynamic options

When a new field needs to reference or reuse the option list of another option field, prefer using `dynamic_options_source` to avoid repeatedly defining and maintaining `options`.

Supported fields: `multiple`, `dynamic_options_source`
Dynamic options do not support `default_value`.

Default values / constraints:
- `multiple` default `false`
- `dynamic_options_source` structure is `{table_id, field_id}`
- `dynamic_options_source.table_id` fill in the source table id or table name
- `dynamic_options_source.field_id` fill in the source field id or field name
- `dynamic_options_source` is supported only at creation; do not pass it when updating an existing field
- Referenced option conditions / cascading filter conditions: this feature is supported in the Base frontend and is a UI-only property; it is not supported in OpenAPI, and the CLI cannot read, create, or update it; do not judge that it is unconfigured based on its absence from the API response
- Dynamic options do not support configuring `default_value`.

```json
{
  "type": "select",
  "name": "动态状态",
  "multiple": false,
  "dynamic_options_source": {
    "table_id": "选项表",
    "field_id": "候选状态"
  }
}
```

### 3.4 datetime

A manually filled date/time field. For system time use `created_at` / `updated_at`.
Supports `default_value`: a static time string, or `{ "$slot": "record_created_time" }`. `datetime + record_created_time` is an auto-filled editable cell; `created_at` is read-only creation-time metadata.

Minimal form:

```json
{
  "type": "datetime",
  "name": "截止时间",
  "default_value": "2026-03-24 10:00"
}
```

Supported fields: `style.format`

Default values / constraints:
- `style.format` default `yyyy/MM/dd` available formats: `yyyy/MM/dd`, `yyyy/MM/dd HH:mm`, `yyyy/MM/dd HH:mm Z`, `yyyy-MM-dd`, `yyyy-MM-dd HH:mm`, `yyyy-MM-dd HH:mm Z`, `MM-dd`, `MM/dd/yyyy`, `dd/MM/yyyy`
- `style.format` only controls Base frontend display and does not affect the CellValue read by the CLI; the frontend currently supports configuring display down to the minute level at most, and the underlying time value is stored with millisecond precision.

Common form:

```json
{
  "type": "datetime",
  "name": "截止时间",
  "style": { "format": "yyyy-MM-dd HH:mm" },
  "default_value": { "$slot": "record_created_time" }
}
```

### 3.5 created_at / updated_at

System creation time / system update time fields; the display format can be configured, but they should be treated as read-only when records are written.

Supported fields: `style.format`

Default values / constraints:
- `style.format` default `yyyy/MM/dd`
- Available formats: `yyyy/MM/dd`, `yyyy/MM/dd HH:mm`, `yyyy/MM/dd HH:mm Z`, `yyyy-MM-dd`, `yyyy-MM-dd HH:mm`, `yyyy-MM-dd HH:mm Z`, `MM-dd`, `MM/dd/yyyy`, `dd/MM/yyyy`

```json
{ "type": "created_at", "name": "创建时间" }
```

```json
{ "type": "updated_at", "name": "更新时间", "style": { "format": "yyyy/MM/dd HH:mm" } }
```

### 3.6 user / group_chat

Both support `multiple` (default `true`); only `user` supports the personnel array `default_value`, whose elements use `{ "id": "ou_xxx" }` or `{ "$slot": "current_user" }`, and user IDs must come from real queries.

```json
{
  "type": "user",
  "name": "负责人",
  "multiple": true,
  "default_value": [{ "$slot": "current_user" }, { "id": "ou_xxx" }]
}
```

```json
{ "type": "group_chat", "name": "负责群", "multiple": true }
```

### 3.7 created_by / updated_by

System creator and modifier fields, read-only when records are written: `{ "type": "created_by", "name": "创建人" }`, `{ "type": "updated_by", "name": "更新人" }`.

### 3.8 link

Link field; `link_table` is required.

Supported fields: `link_table`, `bidirectional`, `bidirectional_link_field_name`

Default values / constraints:
- `link_table` required
- The cell of the `link` field represents "the set of records in the opposite table that the current record is linked to"
- `bidirectional` default `false`
- When `bidirectional=true`, a reverse link field is automatically created in the linked table. When the link relationship of a record on either side changes, the corresponding record on the other side is automatically updated
- `bidirectional_link_field_name` is used only when `bidirectional=true`
- Link field filtering: this feature is supported in the Base frontend and is a UI-only property; it is not supported in OpenAPI, and the CLI cannot read, create, or update it; do not judge that it is unconfigured based on its absence from the API response

```json
{
  "type": "link",
  "name": "关联任务",
  "link_table": "任务表"
}
```

Bidirectional link:

```json
{
  "type": "link",
  "name": "关联任务",
  "link_table": "任务表",
  "bidirectional": true,
  "bidirectional_link_field_name": "反向关联"
}
```

Notes when updating:
- `link` is not allowed to be converted to other types, and other types cannot be converted to `link`.
- The `bidirectional` of an existing `link` field cannot be changed.

### 3.9 formula

Formula field; `expression` is required. Before creating/updating, first read [Formula Field](lark-base-field-formula.md) to learn the formula syntax.

```json
{
  "type": "formula",
  "name": "合计",
  "expression": "1+1"
}
```

### 3.10 lookup

Lookup reference fields use `from`, `select`, `where`, and the optional `aggregate`; the structure, conditions, and aggregate values must be constructed according to [Lookup Field](lark-base-field-lookup.md).

### 3.11 auto_number

Auto-number field; if `style.rules` is not written at creation, the default rule is used: `NO.001`. When updating an existing auto-number field, the target `style.rules` should be submitted explicitly, because `+field-update` will reapply the new numbering rule to existing numbers.

Minimal form:

```json
{
  "type": "auto_number",
  "name": "编号"
}
```

`style.rules` contains 1–9 rules: use `{ "type":"text", "text":"TASK-" }` for fixed text; use `{ "type":"incremental_number", "length":4 }` for the incrementing sequence number (length 1–9); use `{ "type":"created_time", "date_format":"yyyyMMdd" }` for creation time, with supported formats `yyyyMMdd`, `yyyyMM`, `yyMM`, `MMdd`, `yyyy`, `MM`, `dd`.

Custom rules:

```json
{
  "type": "auto_number",
  "name": "编号",
  "style": {
    "rules": [
      { "type": "text", "text": "TASK-" },
      { "type": "created_time", "date_format": "yyyyMMdd" },
      { "type": "incremental_number", "length": 4 }
    ]
  }
}
```

### 3.12 attachment / location / checkbox

```json
{ "type": "attachment", "name": "附件" }
```

```json
{ "type": "location", "name": "位置" }
```

Location is read as `{lng,lat,full_address}`; for writing, use only the numeric `{lng,lat}`, and `full_address` is resolved by the platform based on the coordinates and cannot be specified manually; filtering behavior follows `full_address` for string filtering, treating Location as a text column and using text operators. When `location -> text`, only `full_address` is retained.

```json
{ "type": "checkbox", "name": "完成" }
```

### 3.13 button

```json
{ "type": "button", "name": "按钮", "button_config": { "title": "点击按钮" } }
```

When binding a Workflow, use `+button-rule-bind`; when reading the binding relationship, use `+button-rule-get`; to unbind, use `+button-rule-unbind`.

<a id="4-创建与更新"></a>
## 4. Creation and update

- `+field-create`: directly construct `--json` according to the target field configuration.
- `+field-update`: use the same JSON structure, but perform a full replacement update, not a partial patch. First use `+field-get` to read the current definition, and modify the target properties based on it; the name, type, style, options, default value, description, and type-specific configuration that need to be preserved should all be written back in full, with `--yes` included.

<a id="5-暂不支持字段"></a>
## 5. Fields not yet supported

Object (object field) and Stage (process field) are not yet supported by the CLI. These fields are displayed as `not_support` fields and are protected: modification is not allowed, and content reading is not allowed.

<a id="6-易错点"></a>
## 6. Common pitfalls

- `select` has only one type; do not write `single_select` / `multi_select`, use `multiple` to control whether it is multi-select.
- The precision, currency, progress, and rating configuration of `number` are all placed under `style`, do not write top-level `precision`.
- `datetime` is a manual date field; for system time use `created_at` / `updated_at` instead.
- Do not write `formula` / `lookup` directly before reading the guide.
- Only `text`, `number`, static `select`, `datetime`, `user` support `default_value`; to clear, uniformly pass `"default_value": null`. Do not configure default values for other field types.
