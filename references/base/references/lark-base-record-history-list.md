# base +record-history-list

Query the change history of a single record. It returns historical events, not the record's current values, and does not support full-table audit scans.

<a id="使用前置"></a>
## Prerequisites

`+record-history-list` queries only a single record. Before calling, you must obtain a `record_id` that uniquely corresponds to the user-specified target and belongs to the same table as `table_id`.

If the current information cannot uniquely determine the target record, first confirm with the user, and if necessary use `+record-list` to help locate it; do not select a record on your own, and do not expand to batch or full-table scans. When multiple records need to be queried, first confirm the scope, then call one by one.

When using `+record-list` to display candidates, you may pass `--field-id` repeatedly for a minimal projection. When a field name contains spaces, you need to quote the complete value, for example `--field-id "Project Owner"`.

When the user explicitly specifies the Nth row of a view, first call `+record-list` with the same `view_id`, and set `--offset` to N-1 and `--limit` to 1, then obtain `record_id` from the unique result. If the view or sort context is unclear, you still need to confirm first.

<a id="推荐命令"></a>
## Recommended commands

```bash
lark-cli base +record-history-list \
  --base-token <base_token> \
  --table-id <table_id> \
  --record-id <record_id>

lark-cli base +record-history-list \
  --base-token <base_token> \
  --table-id <table_id> \
  --record-id <record_id> \
  --page-size 30 \
  --max-version <next_max_version>

lark-cli base +record-history-list \
  --base-token <base_token> \
  --table-id <table_id> \
  --record-id <record_id> \
  --format pretty
```

<a id="返回解释"></a>
## Return interpretation

- History entries are usually returned in descending version order, with the latest first.
- Each history entry includes the version number, operator, operation time, operation type, and field changes.
- In the default JSON, `create_time` is a second-level Unix timestamp; `--format pretty` converts it to local time with a UTC offset, and places it on the same line as the operator and field changes.
- `field_changes` describes field changes; focus on the field name/field type, `before`, and `after`.
- In `--format pretty`, an empty `before` or `after` is displayed as `-`; the default JSON preserves the original value.
- Common values of `activity_type`: `create` (create record), `update` (edit record), `delete` (delete record).

Changes to the following field types may not appear in `field_changes`:

- Calculated fields: `formula`, `lookup`
- System fields: auto number, creation time, creator, modification time, modifier

<a id="翻页"></a>
## Pagination

- Do not pass `--max-version` on the first request.
- If `has_more=true` is returned, take the returned `next_max_version` as the `--max-version` for the next request.
- `--page-size` defaults to 30, maximum 50.

<a id="注意"></a>
## Notes

- `table-id` and `record-id` must come from the same table.
- This is single-record history, not table-level auditing; when the user explicitly requests querying multiple records, first confirm the target scope, then call serially by record.
