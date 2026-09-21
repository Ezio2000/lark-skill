# Lark Sheet Pivot Table

<a id="真对象硬约束"></a>
## Hard Constraints on Real Objects

When the user requests "pivot table / grouped summary / cross-tabulation / count Y by X", you **must** create a real pivot table object via `+pivot-{create|update|delete}`. It is **forbidden** to use ordinary formulas such as `SUMIFS` / `COUNTIFS` plus `+cells-set` to assemble a "summary table that looks like a pivot table" in the original sheet as a substitute. The criterion: after delivery, `+pivot-list` must be able to return that object.

<a id="使用场景"></a>
## Use Cases

Read and write pivot table objects. This reference covers 4 shortcuts:

| Operation need | Tool to use | Description |
|---------|---------|------|
| View an existing pivot table | `+pivot-list` | Get the pivot table's structure, data source, and configuration |
| Create/update/delete a pivot table | `+pivot-{create|update|delete}` | Perform write operations on the pivot table |

Typical workflow: first read the existing pivot table to understand its configuration → perform create/update/delete → **must read again to verify the result**.

<a id="行值字段映射创建前必做"></a>
## Row/Value Field Mapping (Must Do Before Creating)

Before creating a pivot table, first identify the grouping dimensions and aggregation metrics in the user's request. **Do not get them reversed**:

- **rows (row fields)** = grouping dimensions, i.e. "group by what". Example: department, region, doctor, product category
- **values (value fields)** = aggregation metrics, i.e. "which numeric value to aggregate". Example: sales amount (aggregation `sum`), order count (aggregation `count`)
- **columns (column fields)** = cross-tabulation dimensions (optional), i.e. "what to expand horizontally by". Example: month, gender

| User says | rows | values | columns |
|--------|------|--------|---------|
| "Count people by department" | Department | Name (`summarize_by: "count"`) | — |
| "Count cost and balance by doctor" | Attending doctor | Cost (`"sum"`), balance (`"sum"`) | — |
| "Number of males and females per department" | Department | Name (`"count"`) | Gender |

**Common configuration errors (must pay attention)**:
- **Value field type must match the aggregator**: `sum/average/median/product/stdDev/stdDevp/var/varp` is only for numeric columns; use `countNums` for count of numbers, and `count` for count of non-empty records. For mixed columns, first keep the original values and add cleaning result/failure markers, record the total count, successes, failures, empty values, and the statistical denominator, then aggregate the cleaned numeric column.
- **Data source range must be precise**: the pivot table's data source range must include the header row and precisely cover all data rows and columns. A range that is too large (including empty rows/columns) or too small (missing data columns) will cause incorrect pivot table results
- **Row/column field selection must match user intent**: when the user says "count amount by product" → row field = product, value field = amount (`summarize_by: "sum"`). Do not reverse the row and column fields
- **Aggregation type must match**: when the user says "count quantity" → `summarize_by: "count"`; "count total" → `"sum"`; "count average" → `"average"`. Complete valid values: `sum` / `count` / `average` / `max` / `min` / `product` / `countNums` / `stdDev` / `stdDevp` / `var` / `varp` / `distinct` / `median`. Choose the aggregation method according to user intent; do not substitute `count` for `sum`
- **`--properties` also natively supports**: calculated fields `calculated_fields[].summarize_by ∈ {sum, custom}`, repeated row labels `repeat_row_labels: true` — do not judge it as "unsupported" and take a detour just because the quick reference table does not list them
- **Parameter length limit**: if the pivot table configuration JSON is too long (the data source range spans a large number of rows and columns), the tool call may fail. In this case, first confirm the precise boundaries of the data range to avoid passing an overly large range
- **The placement point must not overwrite any existing data (not just the `--source` range)**: after creation, the pivot table **expands** to the right and down. Even if the expanded area covers only one existing cell (even if the source data has been avoided), it will report "target position cannot overlap with data source" and produce `#REF!`. The expansion size cannot be precisely predicted before creation, so **strongly prefer the default strategy** (do not pass `--target-sheet-id/-name` and `--target-position`/`--range`; the backend automatically creates a new blank sub-sheet), with zero overwrite risk; if you must place it in an existing sub-sheet, you must choose a sufficiently large pure blank area
- **Poll and verify after creation**: call `+pivot-list --sheet-id/--sheet-name <落点表> --pivot-table-id <id>`. `Loading` / `ServiceCalcLoading` are transient; continue polling until `info.loaded=true` and `error_state=None`; for terminal errors such as `Cover` / `Shrink`, delete and recreate. Then use `info.content_range/page_range` to read back the expanded area and confirm it is non-empty, its size, the grand total position, and the metrics the user named.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+pivot-list` | read | Object |
| `+pivot-create` | write | Object |
| `+pivot-update` | write | Object |
| `+pivot-delete` | high-risk-write | Object |

## Flags

### `+pivot-list`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--pivot-table-id` | string | optional | Filter by id |

### `+pivot-create`

_Common: URL/token (no sheet positioning) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--properties` | string + File + Stdin (composite JSON) | required | JSON: {"rows":[...],"columns":[...],"values":[...],"filters":[...],"show_row_grand_total":true,"show_col_grand_total":true} (the data source goes through --source; do not put it into properties.source again) |
| `--target-position` | string | optional | The starting cell within the pivot table's placement sub-sheet (A1 format, e.g. `A1`), default `A1` (not sent when the value is A1). It and `--range` land on the same wire field `properties.range`; when a non-default value is given, it takes precedence over `--range`; if both are given non-default values, it will be rejected; pass only one of them |
| `--target-sheet-id` | string | xor | The reference_id of the target sub-sheet where the pivot table is placed (mutually exclusive with `--target-sheet-name`, takes precedence over --target-sheet-name; when neither is passed, a new sub-sheet is automatically created to hold the pivot table — recommended). Distinguish from the data source sheet: the data source sheet is written in the A1 reference of --source (with a sheet prefix, in the form `'Sheet1'!A1:D100`). |
| `--target-sheet-name` | string | xor | The name of the target sub-sheet where the pivot table is placed (mutually exclusive with `--target-sheet-id`; when neither is passed, a new sub-sheet is automatically created to hold the pivot table — recommended). Distinguish from the data source sheet: the data source sheet is written in the A1 reference of --source (with a sheet prefix, in the form `'Sheet1'!A1:D100`). |
| `--source` | string | required | The pivot table source data range (A1 notation, format `'SheetName'!StartCell:EndCell`, e.g. `'Sheet1'!A1:D100`) |
| `--range` | string | optional | The top-left placement position of the pivot table (A1 single value, e.g. `F1`, only effective for create), mapped to `properties.range`; when omitted, it is placed at the top-left corner of the placement sub-sheet (a new sub-sheet by default). It and `--target-position` land on the same wire field; if both are given non-default values, it will be rejected; pass only one of them |

### `+pivot-update`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--pivot-table-id` | string | required | Target pivot table id |
| `--properties` | string + File + Stdin (composite JSON) | required | Complete or sufficiently complete configuration (first read back with `+pivot-list --pivot-table-id <id>`, then patch) |

### `+pivot-delete`

_Common four-piece set · System: `--yes`, `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--pivot-table-id` | string | required | Target pivot table id |

## Schemas

> Composite JSON flag field quick reference (only top level + one level of nesting). For deeper structures, see `## Examples` below, or use `--print-schema` to read the complete JSON Schema (usage see index.md "Common flag quick reference" and "Agent usage tips").

### `+pivot-create` `--properties` / `+pivot-update` `--properties`

_Pivot table properties for create/update_

**Top-level fields**:
- `range` (string?) — The A1 address of the top-left cell where the pivot table is placed (e.g. 'F1') (only effective for create) — ⚠️ Already extracted as an independent flag `--range`; do not fill it in again in this JSON (for the same name, the independent flag takes precedence)
- `source` (string?) — Source data range address, in the format 'SheetName!StartCell:EndCell' (e.g. 'Sheet1!A1:D100') — ⚠️ Already extracted as an independent flag `--source`; do not fill it in again in this JSON (for the same name, the independent flag takes precedence)
- `rows` (array<object>?) — Vertical grouping fields (row fields) each: { field: string, display_name?: string, sort?: object, filter?: object, condition_filter?: object, …6 items total }
- `columns` (array<object>?) — Horizontal grouping fields (column fields) each: { field: string, display_name?: string, sort?: object, filter?: object, condition_filter?: object, …6 items total }
- `filters` (array<object>?) — Filter area fields (page fields) each: { field: string, display_name?: string, filter?: object, condition_filter?: object, group?: object }
- `values` (array<object>?) — Fields to summarize (at least 1 required) each: { field: string, display_name?: string, summarize_by?: enum, show_data_as?: enum, base_field?: string }
- `auto_fit_col` (boolean?) — Whether to automatically adjust column width to fit content
- `show_row_grand_total` (boolean?) — Whether to show row grand totals (default true)
- `show_col_grand_total` (boolean?) — Whether to show column grand totals (default true)
- `show_subtotals` (boolean?) — Whether to show category subtotals (default true, applied to all fields)
- `repeat_row_labels` (boolean?) — Whether to show repeated item labels
- `calculated_fields` (array<object>?) — List of calculated fields each: { name: string, formula: string, summarize_by?: enum }
- `collapse` (object?) — Row field expand/collapse state: field name -> list of items to collapse

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` arranged at the top, where `--sheet-id` / `--sheet-name` have the common four-piece set semantics on `+pivot-update` / `+pivot-delete` / `+pivot-list` (locating the sheet where the pivot table resides; XOR, exactly one must be passed).

**`+pivot-create` exception**: the placement selector uses `--target-sheet-id` / `--target-sheet-name` (at most one, both may be omitted; when omitted, the backend automatically creates a new sub-sheet, recommended). The data source sheet is written in the `'SheetName'!Range` of `--source`.

### `+pivot-list`

```bash
lark-cli sheets +pivot-list --url "..." --sheet-id "$SID"
```

> **The return value includes `info` (the occupied area and status after expansion)**: in addition to `position` / `snapshot`, each pivot table object also returns `info`, indicating its tiled area and status on the sheet — `info.page_range` (filter/pagination area A1), `info.content_range` (main data area A1), `info.span_range` (empty table merge area A1), `info.error_state` (error status, such as `None`/`Cover`/`Shrink`/`Loading`), `info.is_empty` / `info.is_hidden`, `info.row`/`info.col` (anchors), etc.
> **Use 1 (decide whether to change a value or change the configuration)**: when the user describes that a certain cell needs to be changed, first use `+pivot-list` to get `info`, and determine whether that cell falls within `page_range` / `content_range` — **falling within the area = it belongs to the pivot table, and you should use `+pivot-update` to change the configuration** (pivot table cells cannot be directly changed via `+cells-set`); **falling outside the area = an ordinary cell, change the value normally via `+cells-set`**.
> **Use 2 (verify overwrite after creation)**: after creation, poll `info.loaded/error_state`; for `Loading` / `ServiceCalcLoading`, continue waiting; only terminal errors such as `Cover` / `Shrink` indicate a conflict. After success, use `content_range/page_range` to check the actual occupied area against the original data boundaries.

### `+pivot-create`

> The data source `--source` must start from the header row; empty rows / summary rows will be treated as data and participate in aggregation, so you need to confirm the start and end boundaries in advance with `+csv-get`. `--source` and `--range` are independent flags (do not put them into `--properties` again); array fields such as `rows` / `columns` / `values` go through `--properties`.
>
> **First clarify the 4 position-type input parameters on `+pivot-create` (different semantics, do not mix them up)**:
> - `--source` (**required**): the **source data** range, which must carry a `Sheet!` prefix (e.g. `'Sheet1'!A1:D100`; the sheet name is wrapped in single quotes per the A1 standard). The name of the source sheet is in the `--source` string, and is **not** passed via a separate flag.
> - `--target-sheet-id` / `--target-sheet-name`: the **placement sheet of the pivot table** (i.e. which sub-sheet the output goes into). The two are mutually exclusive (pass at most one); when neither is passed, the backend automatically creates a new sub-sheet to hold the output (strongly recommended).
> - `--target-position` (optional, default `A1`) and `--range` (optional) both map to `properties.range`, expressing the same placement point; do not give both non-default values at the same time.
>
> **3 placement strategies (mutually exclusive, choose one)**:
> 1. **Default (strongly recommended)**: `--target-sheet-id` / `--target-sheet-name` / `--target-position` / `--range` **all not passed** → the server **automatically creates a new sub-sheet** to hold the output, never touching any existing data.
> 2. **Place into a specified existing sub-sheet**: pass `--target-sheet-id <落点子表 id>` (or `--target-sheet-name`), optionally `--target-position <子表内起点 cell>`. ⚠️ **If the placement sub-sheet is the sheet where the source data resides**, you must configure `--target-position` or `--range` to point to a position **outside** the source data range; otherwise the output, starting from A1 by default, will overwrite the source data.
> 3. **`--range`**: equivalent to strategy 2 (likewise requires `--target-sheet-id` / `--target-sheet-name` to specify the placement sub-sheet, otherwise it falls into an automatically created sub-sheet), except that `--range` is used to express the same placement point (the same wire field as `--target-position`). The same overwrite risk, and likewise you need to avoid the source data range.
>
> Generally strategy 1 (default new sub-sheet) is sufficient, with zero overwrite risk and no need for any `--target-*` / `--range` flag.

```bash
# Strategy 1 (strongly recommended): do not pass any placement flag → the backend automatically creates a new sub-sheet, zero overwrite risk
lark-cli sheets +pivot-create --url "..." \
  --source "'Sheet1'!A1:D100" --properties @pivot.json

# Strategy 2: place into a specified existing target sub-sheet (note that the target sheet ≠ the source sheet, otherwise you must configure --target-position to avoid the source data)
lark-cli sheets +pivot-create --url "..." \
  --source "'Sheet1'!A1:D100" --target-sheet-id "$DEST_SID" --target-position "A1" --properties @pivot.json
```

### `+pivot-update`

> Changing the placement range is not allowed; before updating the configuration, first read back the complete snapshot with `+pivot-list --sheet-id/--sheet-name <落点表> --pivot-table-id <id>`, then patch rows / columns / values / filters. When you need to switch the data source, you can provide a new `source` in `--properties`.

### `+pivot-delete`

```bash
lark-cli sheets +pivot-delete --url "..." --sheet-id "$SHEET_ID" --pivot-table-id "$PIVOT_TABLE_ID" --yes
```

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute Constraints

- `Validate`: `--url` / `--spreadsheet-token` XOR required; for update/delete/list, `--sheet-id` / `--sheet-name` XOR required; for create, at most one target selector, and both may be omitted; `--source` and a valid `--properties` are required; delete enforces `--yes` or `--dry-run`. The schema validates types and enums, but allows creating an empty-shell configuration; business completeness must be verified via list/data after creation.
- `DryRun`: outputs the pivot request template to be sent and the local placement_warning; does not go online and does not estimate the actual expansion size.
- `Execute`: does not automatically read back after writing; after create/update, you must poll `+pivot-list` by placement sheet + pivot id until loaded, and check error_state/content_range and the data; after delete, use list to confirm the target no longer exists.

> ⚠️ pivot output includes grand total / subtotal rows; when a subsequent chart references the pivot, `snapshot.data.refs` must exclude these rows (see the "⚠️ chart data source must exclude grand total rows when referencing a pivot" section of `references/lark-sheets-chart.md`).
