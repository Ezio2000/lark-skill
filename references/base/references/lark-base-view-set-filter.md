# base +view-set-filter


Update the view filter configuration.

<a id="1-filter-结构"></a>
## 1. filter structure

`--json` is a filter condition object; for its structure, see the shared protocol SSOT [lark-base-filter-condition.md](lark-base-filter-condition.md), i.e. `{logic?, conditions?}`. Here, `field` in `conditions` references a **table field name or field id**.

- Supported view types for `filter`: `grid`, `kanban`, `gallery`, `calendar`, `gantt`.

<a id="2-推荐命令"></a>
## 2. Recommended command

```bash
lark-cli base +view-set-filter \
  --base-token <base_token> \
  --table-id <table_id> \
  --view-id <view_id> \
  --json '{"logic":"and","conditions":[["状态","intersects",["Doing"]],["负责人","intersects",[{"id":"ou_xxx"}]],["截止时间","empty"]]}'
```

<a id="3-json-写法"></a>
## 3. JSON syntax

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

For the complete operator list and the value syntax for each field type (`text` / `number` / `select` / `user` / `datetime` / `formula` / `lookup`, etc.), see [lark-base-filter-condition.md](lark-base-filter-condition.md).

<a id="4-使用建议"></a>
## 4. Usage recommendations

- First read the current filter configuration to understand how the existing `logic` and `conditions` are combined; replace only the conditions the user asked to change, and keep unmentioned conditions by default.
- Prefer passing field ids; do not rely on field names.
- When unsure about a field's type or actual values, first confirm with `+field-list` / `+record-list`, then construct conditions according to the value syntax for the corresponding field type; do not guess the type from the field name or guess enum values from impression.
- To clear all filters, pass `{"conditions":[]}` directly.

<a id="5-易错点"></a>
## 5. Common pitfalls

- This tuple DSL is shared by `+view-set-filter` and `--filter-json` of `+record-list` / `+record-search`; do not write it in the object style `{"field_name":...,"operator":...}` of `+data-query` (this will cause a validation failure).
- For scalar-type fields (`text` / `number` / `datetime`, etc.), use a scalar for value; do not wrap it in an array (see the value syntax section for details on each type).
- Do not write `user` / `group_chat` / `link` as a single scalar.
- Do not force meaningless values into `empty` / `non_empty`.
- For stable date conditions, use `ExactDate(...)` or `Today` / `Yesterday` / `Tomorrow`.
- The value shape of `formula` / `lookup` is not fixed; when unsure, first read the current filter or field definition, or correct the type based on the error message.

<a id="6-参考"></a>
## 6. References

- [lark-base-filter-condition.md](lark-base-filter-condition.md): shared protocol SSOT for filter/visible_rule condition structures
- [Lookup Field](lark-base-field-lookup.md)
