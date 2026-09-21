# base +field-update


Update an existing field.

<a id="推荐命令"></a>
## Recommended command

```bash
lark-cli base +field-update \
  --base-token <base_token> \
  --table-id <table_id> \
  --field-id <field_id> \
  --json '{"name":"状态","type":"select","multiple":false,"default_value":["Doing"],"options":[{"name":"Todo","hue":"Blue","lightness":"Lighter"},{"name":"Doing","hue":"Orange","lightness":"Light"},{"name":"Done","hue":"Green","lightness":"Light"}]}' \
  --yes

```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--base-token <token>` | Yes | Base Token |
| `--table-id <id_or_name>` | Yes | Table ID or table name |
| `--field-id <id_or_name>` | Yes | Field ID or field name |
| `--json <body>` | Yes | Field property JSON object |
| `--yes` | Yes | Confirm execution of a high-risk field update |

> This is a **high-risk write operation**. `+field-update` uses `PUT` full field definition semantics; changing the field type or key configuration may affect the interpretation, display, or availability of existing data in the entire column. The CLI layer requires explicitly passing `--yes`; if the user has already clearly specified the target and expected update, you can execute directly and include `--yes`.

<a id="api-入参详情"></a>
## API input details

**HTTP method and path:**

```
PUT /open-apis/base/v3/bases/:base_token/tables/:table_id/fields/:field_id
```

<a id="json-值规范"></a>
## JSON value specification

- `--json` must be a **JSON object**, with the field definition passed directly at the top level.
- The update semantics are an override-style full replacement of `PUT`, not a partial update; first read the current definition, then submit the entire writable configuration that the field needs to retain. Do not pass only scattered fragments.
- All field types support the optional `description`; plain text is supported, as are Markdown links.
- When a field default value is needed, pass `default_value`, using the CellValue corresponding to the field directly; pass `null` to clear it. For complete rules, see [Field Schema](lark-base-field-schema.md).
- When updating `select`: `options` is still passed as an array of objects, to avoid mixing in invalid fields.
- `link` update restrictions:
  - You cannot change a non-`link` field into `link`, nor can you change `link` into non-`link`.
  - The `bidirectional` of an existing `link` field cannot be changed.
- Updating `auto_number.style.rules` updates the numbering of existing records according to the new rule; for the rule structure, see [Field Schema](lark-base-field-schema.md).

**Recommended update example**

```json
{
  "name": "状态",
  "type": "select",
  "multiple": false,
  "default_value": ["Doing"],
  "options": [
    { "name": "Todo", "hue": "Blue", "lightness": "Lighter" },
    { "name": "Doing", "hue": "Orange", "lightness": "Light" },
    { "name": "Done", "hue": "Green", "lightness": "Light" }
  ]
}
```

<a id="返回重点"></a>
## Return highlights

- Returns `field` and `updated: true`.
- Continue based on the returned `next_step` and `verification_hint`; when type conversion involves existing values, sample-read records.

<a id="工作流"></a>
## Workflow


1. First use `+field-get` to read the current definition, change only the target property, and write back completely all other writable configuration that needs to be retained.
2. Before updating the `formula/lookup` type, read the corresponding guide first.
3. If this update will change the field `type`, first determine whether it can be executed according to the "Field type change rules" below. If `type` is not modified, most scenarios are relatively safe.

<a id="字段类型变更规则"></a>
## Field type change rules

Field type changes use a whitelist mechanism: **only whitelist conversions are allowed**; when the whitelist is not matched, **it is not recommended to use the CLI to convert the field type** unless the user clearly knows the risk and agrees.

<a id="允许直接转换-type"></a>
### Allowed direct type conversion

First use `+field-get` / `+field-list` to inspect the structure, then sample-read values; only when the following rules are matched is the conversion relatively safe.

<a id="相对安全"></a>
#### Relatively safe

| Target type | Allowed source types | Description |
|------|------|------|
| `text` | `number`, `select`, `datetime`, `created_at`, `updated_at`, `location` (only `full_address` is retained), `auto_number`, `checkbox` | Retains the string representation; loses the original type semantics and structured capabilities |
| `number` | `text`, `number`, `datetime`, `created_at`, `updated_at`, `checkbox` | Retains parseable numeric values; values that cannot be parsed become empty, and the original text format is lost |
| `datetime` | `text`, `number`, `datetime`, `created_at`, `updated_at` | Retains parseable time strings and timestamps; values that cannot be parsed become empty, and the original text format is lost |
| `select` | `text -> select`, `number -> select`, `single select -> multi select` | Only values that exactly match the target option name are converted to the corresponding option; values that do not match are discarded |

<a id="可执行但会截断--重算"></a>
#### Executable but will truncate / recalculate

- `select(multi) -> select(single)`: only the first value is retained; the remaining values are discarded.
- `user(multi) -> user(single)`: only the first person is retained; the remaining values are discarded.
- `group_chat(multi) -> group_chat(single)`: only the first group is retained; the remaining values are discarded.

<a id="无状态字段可直接转换"></a>
#### Stateless fields can be converted directly

- `created_at`, `created_by`, `updated_at`, `updated_by`, `formula`, `lookup`: values of these fields are generated by the system or calculation logic and do not carry independently stored data; type conversion can be performed without worrying about destroying the original record values, but downstream read-back verification is still required.

<a id="一律不要用-cli-转换"></a>
### Never use the CLI to convert

The following scenarios are all treated as blacklisted; by default, require the user to change them manually on the Web page, or switch to "create a new field + data migration".

- `any -> checkbox`
- `any -> user`
- `any -> group_chat`
- `any -> attachment`
- `any -> location`
- `link` type changes
- Any `select` type change involving switching between dynamic / static option sources

<a id="可例外继续执行的场景"></a>
### Scenarios where execution may continue as an exception

Only when **loss of the entire column's data is acceptable** is it allowed to execute blacklisted scenarios as an exception.

1. The column is empty.
2. A newly created empty table is being initialized.
3. The primary field cannot be deleted and needs to be initialized through an update.
4. The user explicitly accepts the loss of the entire column's data.

If the above conditions are not met, do not convert.

<a id="非白名单场景如何处理"></a>
### How to handle non-whitelist scenarios

- When the whitelist is matched: it is recommended to convert in place directly, then perform read-back verification.
- When the whitelist is not matched: first ask the user whether they still want to perform the conversion, and clearly explain the risks:
  - Except for stateless fields; such fields can be converted directly
  - The entire column may become empty
  - Only the first value may be retained
  - Only the string representation may be retained, losing the original type semantics and structured capabilities
  - Views / filters / sorting / formulas / lookup / write references may be affected
- If the user does not accept the risk: do not perform the conversion.

<a id="坑点"></a>
## Pitfalls

- ⚠️ This is full field property update semantics, not a patch.
- ⚠️ This is a high-risk write operation, and `--yes` must be included when executing.
- ⚠️ When `type` is `formula` or `lookup`, read the corresponding guide before executing.

<a id="参考"></a>
## References

- Before updating, read the current field to confirm the existing `type` and specific configuration details, then decide whether to update in place or create a new field and migrate.
- [Field Schema](lark-base-field-schema.md) — field JSON specification (recommended)
- [Formula Field](lark-base-field-formula.md) — required reading before updating a formula
- [Lookup Field](lark-base-field-lookup.md) — required reading before updating a lookup reference
