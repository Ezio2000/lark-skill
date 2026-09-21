# base +field-create


Create one or more fields; for multiple fields in the same table, prefer passing a single JSON array input.

`formula` / `lookup` Before creating, read the corresponding guide; when cross-table references are involved, also read the target table structure.

<a id="推荐命令"></a>
## Recommended commands

```bash
lark-cli base +field-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --json '{"name":"预算","type":"number","style":{"type":"plain","precision":2}}'

lark-cli base +field-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --json '{"name":"状态","type":"select","multiple":false,"default_value":["Todo"],"options":[{"name":"Todo","hue":"Blue","lightness":"Lighter"},{"name":"Done","hue":"Green","lightness":"Light"}]}'

# Multiple fields reuse the same field JSON shape; pass a non-empty array at once
lark-cli base +field-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --json '[{"name":"备注","type":"text"},{"name":"优先级","type":"select","multiple":false,"options":[{"name":"高"},{"name":"低"}]}]'
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--base-token <token>` | Yes | Base Token |
| `--table-id <id_or_name>` | Yes | Table ID or table name |
| `--json <body>` | Yes | A single field JSON object, or a non-empty array of multiple field objects |

<a id="api-入参详情"></a>
## API input details

**HTTP method and path:**

```
POST /open-apis/base/v3/bases/:base_token/tables/:table_id/fields
```

<a id="json-值规范"></a>
## JSON value specification

- `--json` accepts a single field **JSON object**, and also accepts a non-empty array of multiple field objects; do not wrap it in another outer object such as `fields`.
- The array creates fields in order; it stops at the first failure and does not automatically roll back; on partial failure, keep the `created` items in `items`, fix them according to `hint`, then submit only the `failed` and `not_attempted` items, preserving dependency order.
- Each field object contains at minimum: `name`, `type`.
- All field types support the optional `description`; plain text is supported, as are Markdown links, such as `协作约定可参考[团队字段约定](https://example.com/field-spec)`.
- To set a field default value, pass `default_value`, directly using the CellValue corresponding to the field; for dynamic population of `datetime` / `user`, use `$slot`. For complete rules, see [Field Schema](lark-base-field-schema.md).
- `type` differ, and the required subfields differ:
  - `select`: `multiple` controls whether multiple selection is allowed, `options` defines static options, and `dynamic_options_source` defines the dynamic option source. Static and dynamic option configurations are mutually exclusive and cannot be passed at the same time.
  - `link`: must have `link_table`, and may optionally have `bidirectional`, `bidirectional_link_field_name`.
  - `formula`: must have `expression`; read the formula guide first, then create.
  - `lookup`: must have `from`, `select`, `where`; read the lookup guide first, then create.

**Correct (base +field-create)**

```json
{
  "name": "状态",
  "type": "select",
  "multiple": false,
  "default_value": ["Todo"],
  "options": [
    { "name": "Todo", "hue": "Blue", "lightness": "Lighter" },
    { "name": "Done", "hue": "Green", "lightness": "Light" }
  ]
}
```

<a id="参考"></a>
## References

- [Field Schema](lark-base-field-schema.md) — field JSON specification (recommended)
- [Formula Field](lark-base-field-formula.md) — required reading before creating formulas
- [Lookup Field](lark-base-field-lookup.md) — required reading before creating lookup references
