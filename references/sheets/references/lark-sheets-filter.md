# Lark Sheet Filter

<a id="真对象硬约束--数量校验"></a>
## Hard Constraints on Real Objects + Count Verification

1. **First determine the artifact form, then choose the approach**: **Need to trim columns / need to save results to a separate sheet** ("only keep certain columns", "filter out and put into a new sheet", including row-level filtering where the user explicitly requests the filtered results be made into an independent new sheet) → create a separate result sheet to materialize the matching rows and columns, **keeping the original sheet unchanged**; **row-level only, no column trimming** ("filter / only view / only keep matching rows") → **must** create a real filter object via `+filter-{create|update|delete}`, **forbidden** to substitute with "delete non-matching rows" / "create a new sub-sheet containing only matching rows" / overwriting the original sheet with `+cells-set` — these approaches cause the original data to be lost or unrecoverable.
2. **Filter count must be verified**: After executing the filter, **must** read back and assert `len(visible_rows) == expected_count`. `expected_count` comes from first independently reproducing the filter condition on the source data using a local script to obtain the result count. If the two do not match, delivery is forbidden; investigate the filter condition / data column type issues.
3. **Mixed text columns forbid literal comparison**: When the filter key is formula text (e.g., `1000+200=1200`) or mixed text with units, first extract the pure numeric value in a helper column before filtering; do not directly use text comparison.

<a id="使用场景"></a>
## Use Cases

Read and write filter objects. This reference covers 4 shortcuts:

| Operation Need | Tool to Use | Description |
|---------|---------|------|
| View existing filters | `+filter-list` | Get the filter's range, rules, and condition configuration |
| Create/update/delete filters | `+filter-{create|update|delete}` | Perform write operations on filters |

Typical workflow: first read existing filters to understand the configuration → execute create/update/delete → **must read again to verify the result**.

**Read-only scenario exception**: When the user only wants to know which data meets the conditions and does not require modifying the sheet display, you can use `references/lark-sheets-read-data.md` to read and answer in text without creating a filter.

**Common configuration errors (must pay attention)**:
- **Filter range must cover the header row**: The filter's range must start from the header row (e.g., `A1:F100`), and cannot include only data rows. Missing the header will cause filter conditions to fail to correctly match columns
- **Read before updating an existing filter**: If a filter already exists on the sub-sheet, directly creating one will error or overwrite the original configuration. First use `+filter-list` to check whether a filter exists; if it does, use update instead of create
- **Filter condition column index must be precise**: The column identifier in filter conditions must precisely correspond to the actual data column; do not fill in based on guesswork
- **"Adjust filter logic" requires reading the old configuration first**: When the user says "adjust the filter", first read the complete configuration of the existing filter, understand the current rules before modifying, and do not create from scratch
- **Must verify after creation**: Call `+filter-list` to confirm the filter configuration is correct and effective
- **Filters do not support regular expressions**: Lark Sheets filters do not support regular expressions; passing a regex will be treated as plain text.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+filter-list` | read | Object |
| `+filter-create` | write | Object |
| `+filter-update` | write | Object |
| `+filter-delete` | high-risk-write | Object |

## Flags

### `+filter-list`

_Common four-piece set · System: `--dry-run`_

_Contains only common / system flags._

### `+filter-create`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | Filter range (A1 notation, including header row, e.g., `A1:F1000`); do not duplicate the range field in `--properties` |
| `--properties` | string + File + Stdin (composite JSON) | optional | Filter rules JSON: `rules` (array of column-level filter rules) + `filtered_columns?` (active column index hint). `--properties` is entirely optional — when passing it, `rules` cannot be empty; if not passed, only an empty filter is established on `--range` (no column conditions). `range` is an independent flag (do not put it in this JSON again) |

### `+filter-update`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--properties` | string + File + Stdin (composite JSON) | required | Filter rules JSON, containing `rules` and `filtered_columns?`; update is a full-group overwrite (passing empty `rules: []` clears). `range` has been extracted as an independent flag |
| `--range` | string | required | The cell range the filter applies to (A1 notation, e.g., `A1:F1000`); takes priority over the same-named field in `--properties` |

### `+filter-delete`

_Common four-piece set · System: `--yes`, `--dry-run`_

_Contains only common / system flags._

## Schemas

> Composite JSON flag field quick reference (only lists top level + one level of nesting). For deeper structures see `## Examples` below, or use `--print-schema` to read the complete JSON Schema (usage see index.md "Common Flag Quick Reference" and "Agent Usage Tips").

### `+filter-create` `--properties` / `+filter-update` `--properties`

_Filter properties for create/update_

**Top-level fields**:
- `range` (string) — The cell range the filter object applies to (A1 notation) — ⚠️ Already extracted as an independent flag `--range`, do not duplicate it in this JSON (same name defers to the independent flag)
- `rules` (array<object>) — List of column-level filter rules, each item corresponds to a specific column's filter condition each: { column_index: string, conditions: array<oneOf>, filtered_rows?: array<number> }
- `filtered_columns` (array<string>?) — optional

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` (XOR) at the top. `filter_id` is equivalent to `sheet_id` (at most one filter per worksheet).

### `+filter-list`

```bash
# View the current sheet's filter configuration (filter_id equals sheet_id)
lark-cli sheets +filter-list --url "..." --sheet-id "$SID"
```

### `+filter-create`

`--range` is an independent flag (including header row); `rules` goes through `--properties`:

```bash
lark-cli sheets +filter-create --url "..." --sheet-id "$SID" \
  --range "A1:F1000" \
  --properties '{"rules":[{"column_index":"B","conditions":[{"type":"multiValue","compare_type":"equal","values":["北京","上海"]}]}]}'
```

**`conditions[].type` × `compare_type` values** (`type` determines the available `compare_type`; both are required):

| `type` | Available `compare_type` | `values` |
|---|---|---|
| `text` | `contains` / `doesNotContain` / `beginsWith` / `doesNotBeginWith` / `endsWith` / `doesNotEndWith` / `equals` / `notEquals` | String array |
| `number` | `equal` / `notEqual` / `greaterThan` / `greaterThanOrEqual` / `lessThan` / `lessThanOrEqual` / `between` / `notBetween` | Numeric (or numeric string) array; `between` / `notBetween` pass two boundaries |
| `multiValue` | `equal` / `notEqual` | String array (exact match to any one of the values) |
| `color` | `backgroundColor` / `foregroundColor` | Do not pass `values` (filter by cell color) |

> ⚠️ `text` uses `equals` / `notEquals` (**with s**), `number` / `multiValue` uses `equal` / `notEqual` (**without s**) — do not mix them up. For the complete schema run `+filter-create --print-schema --flag-name properties`.

### `+filter-update`

> ⚠️ update is overwrite-style: passing a new `rules` in `--properties` will replace the old group. If you only want to add one, you must include all existing conditions and then append. Required `--range`.

### `+filter-delete`

```bash
lark-cli sheets +filter-delete --url "..." --sheet-id "$SID" --yes
```

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute Constraints

- `Validate`: XOR common four-piece set; `+filter-create` validates that `--range` has at least 2 rows (header + at least 1 data row); `+filter-update` must first `+filter-list` to confirm the target exists; `+filter-delete` enforces `--yes` or `--dry-run`.
- `DryRun`: Outputs the "filter request template to be POST/PATCH/DELETE'd".
- `Execute`: Does not automatically read back after writing; after create/update you must call `+filter-list` to verify range, rules, and filtered row count; after delete, list to confirm the filter no longer exists.
