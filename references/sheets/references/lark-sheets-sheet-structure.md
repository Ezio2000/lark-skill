# Lark Sheet Sheet Structure

<a id="结构性操作影响面预检插入--删除行列前必做"></a>
## Structural Operation Impact Pre-check (mandatory before inserting / deleting rows or columns)

Inserting / deleting rows or columns, hiding / unhiding, freezing, and row/column grouping all shift the reference relationships of the original sheet. **Before the operation, you must** first print the following three types of information and assess whether the operation will invalidate them; otherwise execution is prohibited:

1. **Current merged cell ranges** (from `+sheet-info`'s `merged_cells`): when inserting rows / columns, merged regions that span the insertion position may expand or break; when deleting rows / columns, merged regions may disappear entirely.
2. **Reference ranges of existing formulas** (use `+cells-get` to sample nearby rows + cross-sheet references + data source ranges of pivot tables / charts / conditional formatting / filters): inserting / deleting will cause relative references like `=SUM(B4:B13)` to shift; if the operation occurs inside a reference range, it may produce `#REF!`.
3. **Application ranges of data validation (dropdown list) rules**: when the list source is a region, partially deleting the region will invalidate the rule.

Irreversible impacts must first be communicated to the user in the reply, and execution may proceed only after confirmation.

<a id="合并安全契约按模块--分组展示"></a>
## Merge Safety Contract (displayed by module / group)

Before merging, first read the complete contiguous region of the target column; merging is allowed only when values are identical and contiguous, and cells other than the top-left cell have no value / formula / comment / data validation or independent styles that need to be preserved. Empty values, value changes, changes in the parent module, or the above valid content immediately break the group. First read existing merges; overlapping with existing merged regions or expanding across groups is prohibited; before execution, record each group's `range + 左上角原文`, and submit either from bottom to top or as a single batch. After completion, use `+sheet-info --include merges` to verify the range, and use `+cells-get` to confirm that the top-left text is not lost and that boundaries outside the group are not merged.

<a id="使用场景"></a>
## Use Cases

Read and write. Manage sub-sheet structure and layout. This reference covers 9 shortcuts (divided into two categories by purpose):

| Operation need | Tool to use | Description |
|---------|---------|------|
| View sub-sheet layout | `+sheet-info` | Get information such as row heights, column widths, hidden rows/columns, row/column grouping, and merged cells |
| Change sub-sheet structure | `+dim-{insert|delete|hide|unhide|freeze|group|ungroup|move}` | Insert/delete/hide/unhide/freeze/group/move rows and columns |

Notes:

- When the sheet has merged cells, use the returned `merged_cells` to determine headers, group titles, and region semantics
- Do not interpret blank cells other than the top-left cell in a merged region as "no content"; the content of the top-left cell should generally be treated as the semantic content of the entire merged region
- For insertion use `+dim-insert`: `--position` (insertion position; for rows use a 1-based row number such as `3`, for columns use a letter such as `C`, and the new row/column is inserted **before** this position) + `--count` (insertion count, >0). For new row/column style inheritance use `--inherit-style` (`before` inherits from the previous row/column / `after` inherits from the next row/column); it only determines which side's style is inherited, and **the insertion position is always before `--position` and does not change the insertion direction**. ⚠️ When not passed, it defaults to inheriting from the **next row/column** (same as `after`); the underlying layer cannot insert "unformatted" rows/columns, so for truly blank rows/columns, after insertion use `+cells-clear --scope formats` to clear the formatting of the new rows/columns.
- For example, "add 116 rows after row 20": `--position 21 --count 116` ("after row 20" means 1-based row number 21)

**Range expressions are unified as A1 style**: all shortcuts involving "a contiguous span of rows/columns" use the same A1 closed-interval string syntax, and **there is no inclusive / exclusive / 0-based / 1-based difference across commands**:

| Command | Which flag expresses the range / position | Example |
| --- | --- | --- |
| `+dim-insert` | `--position` + `--count` | `--position 3 --count 5` (insert 5 rows before row 3) / `--position C --count 2` (insert 2 columns before column C) |
| `+dim-delete` / `+dim-hide` / `+dim-unhide` / `+dim-group` / `+dim-ungroup` / `+rows-resize` / `+cols-resize` | `--range` | `"3:7"` (rows 3-7, closed interval) / `"C:F"` (columns C-F, closed interval) / `"5"` or `"C"` (single row/column) |
| `+dim-move` | `--source-range` (source range) + `--target` (target position) | `--source-range "3:7" --target 12` (move rows 3-7 before row 12) / `--source-range "C:F" --target H` |

Rows use 1-based numbers, columns use letters—exactly matching the row numbers and column letters seen in Excel / Feishu UI.

**Common configuration errors (must pay attention)**:
- **Insert columns directly with letters**: `+dim-insert`'s `--position` passes letters directly in column scenarios (such as `C`); do not convert column letters to 0-based indexes
- **Reference shift after insertion**: after inserting rows/columns, the row numbers / column letters of existing data will shift. If write operations on the original region are still needed after insertion, the shifted positions must be recalculated
- **Confirm the range before deleting rows/columns**: deletion operations are irreversible, so before execution confirm that `--range` is exactly correct. You may first use `+csv-get` to read the target region and verify the content (`+csv-get` / `+cells-get` see `references/lark-sheets-read-data.md`)
- **Correct way to write "add one column to the left of column D"**: `--position D --count 1` (the new column is inserted before column D); to inherit the left column's style add `--inherit-style before`. Do not treat `--inherit-style after` as "insert to the right of column D"; it is not an insertion direction parameter.
- **`+dim-move` same-dimension constraint**: when `--source-range` is a row range, `--target` must be a row number (number); when it is a column range, `--target` must be a column letter—one row and one column cannot be mixed
- **After inserting columns, you must check multi-row header merged regions**: many sheets have 2-3 row merged headers. After inserting columns, the original merged regions will not automatically expand to the new columns. You must first use `+sheet-info --include merges` to read the merged regions, and after insertion re-set the merged regions that span the insertion position (using `+cells-{merge|unmerge}`); otherwise the new columns' headers will be empty and the formatting will be discontinuous
- **Formula write ranges skip header rows**: when writing formulas, start from the data row (not row 1). First confirm how many rows the header occupies (possibly 1-3 rows); the formula's starting row = number of header rows + 1

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+sheet-info` | read | Worksheet |
| `+dim-insert` | write | Worksheet |
| `+dim-delete` | high-risk-write | Worksheet |
| `+dim-hide` | write | Worksheet |
| `+dim-unhide` | write | Worksheet |
| `+dim-freeze` | write | Worksheet |
| `+dim-group` | write | Worksheet |
| `+dim-ungroup` | write | Worksheet |
| `+dim-move` | write | Worksheet |

## Flags

### `+sheet-info`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--include` | string_slice | optional | Categories of structure information to return, multiple separated by commas (possible values: `merges` / `row_heights` / `col_widths` / `hidden_rows` / `hidden_cols` / `groups` / `frozen`) |
| `--range` | string | optional | Restrict the returned structure information to this A1 range only; when omitted, returns the entire sheet |

### `+dim-insert`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--inherit-style` | string | optional | New row/column style inheritance enum: `before` (inherit from the previous row/column) / `after` (inherit from the next row/column); when not passed, defaults to inheriting from the next row/column (same as `after`), and the underlying layer cannot insert unformatted rows/columns. It only determines which side's style is inherited and does not change the insertion direction (always inserted before `--position`); for truly blank rows/columns, after insertion use `+cells-clear --scope formats` (possible values: `before` / `after`) |
| `--position` | string | required | Insertion position (insert **before** this row/column): for rows use a 1-based row number such as `3`; for columns use a letter such as `C` |
| `--count` | int | required | Insertion count (>0) |

### `+dim-delete`

_Common four-piece set · System: `--yes`, `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | xor | Closed interval of rows/columns to delete; for rows use 1-based numbers such as `3:7` or a single row `5`, for columns use letters such as `C:F` or a single column `C`. Choose one of this and `--ranges` |
| `--ranges` | string + File + Stdin (simple JSON) | xor | JSON array of multiple row/column intervals to delete (at most 100, such as `["5:5","8:8","11:13"]` or `["C:C","F:G"]`); all rows or all columns cannot be mixed, and intervals cannot overlap; choose one of this and `--range`. The CLI combines them into a single batch deletion **in reverse order from largest to smallest** by position (fail-fast; after a failure, read back first and then resend)—deleting in forward order would cause subsequent indexes to shift out of place because earlier rows/columns were deleted; the CLI handles the reverse order for you, so there is no need to sort yourself |

### `+dim-hide`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | Closed interval of rows/columns to hide; for rows such as `3:7`, for columns such as `C:F` |

### `+dim-unhide`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | Closed interval of rows/columns to unhide; for rows such as `3:7`, for columns such as `C:F` |

### `+dim-freeze`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--rows` | int | optional | Freeze the first N rows; together with --cols it describes the complete freeze state, and an omitted axis means not frozen (0 means do not freeze rows) |
| `--cols` | int | optional | Freeze the first N columns; together with --rows it describes the complete freeze state, and an omitted axis means not frozen (0 means do not freeze columns) |

### `+dim-group`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--depth` | int | optional | Level of nested grouping (how many levels to create), default 1 |
| `--group-state` | string | optional | Initial expansion state of the group (possible values: `expand` / `fold`) (default `expand`) |
| `--range` | string | required | Closed interval of rows/columns for which to create the group; for rows such as `3:7`, for columns such as `C:F` |

### `+dim-ungroup`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--depth` | int | optional | Group level to ungroup, default 1 (1=outermost, larger numbers are more inner) |
| `--range` | string | required | Closed interval of rows/columns to ungroup; for rows such as `3:7`, for columns such as `C:F` |

### `+dim-move`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--source-range` | string | required | Closed interval of source rows/columns to move; for rows such as `3:7`, for columns such as `C:F` |
| `--target` | string | required | Target position (move to **before** this row/column): for rows use a 1-based row number such as `12`, for columns use a letter such as `H`. Must be the same dimension (row/column) as `--source-range` |

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` (XOR) arranged at the top.

### `+sheet-info`

Output contract: returns layout metadata such as the sub-sheet's row heights / column widths / hidden / merged / grouped information.

### `+dim-insert`

```bash
# Insert 3 rows before row 10, inheriting the style from above
lark-cli sheets +dim-insert --url "https://example.feishu.cn/sheets/shtXXX" \
  --sheet-id "$SID" --position 10 --count 3 --inherit-style before

# Insert 2 columns before column C
lark-cli sheets +dim-insert --url "..." --sheet-id "$SID" --position C --count 2
```

### `+dim-delete`

```bash
# Delete rows 5-7
lark-cli sheets +dim-delete --url "..." --sheet-id "$SID" --range "5:7" --yes

# Delete columns D-F
lark-cli sheets +dim-delete --url "..." --sheet-id "$SID" --range "D:F" --yes

# Delete multiple scattered intervals (such as deleting rows based on deduplication results): --ranges delivers them all in one batch (fail-fast; after a failure, read back first and then resend; the CLI preserves indexes via reverse order).
# The CLI automatically executes in reverse order from largest to smallest by position—forward order would cause subsequent indexes to shift out of place because earlier rows were deleted;
# no need to sort yourself, and do not assemble a +batch-update sub-operation array for this
lark-cli sheets +dim-delete --url "..." --sheet-id "$SID" --ranges '["5:5","8:8","11:13"]' --yes
```

### `+dim-hide` / `+dim-unhide`

```bash
lark-cli sheets +dim-hide   --url "..." --sheet-id "$SID" --range "5:7"
lark-cli sheets +dim-unhide --url "..." --sheet-id "$SID" --range "5:7"
lark-cli sheets +dim-hide   --url "..." --sheet-id "$SID" --range "C:F"
```

### `+dim-move`

```bash
# Move rows 3-7 before row 12
lark-cli sheets +dim-move --url "..." --sheet-id "$SID" --source-range "3:7" --target 12

# Move columns C-F before column H
lark-cli sheets +dim-move --url "..." --sheet-id "$SID" --source-range "C:F" --target H
```

### `+rows-resize` / `+cols-resize`

> ⚠️ These two shortcuts come from `references/lark-sheets-range-operations.md`'s `+rows-resize / +cols-resize` tool (grouped under "Worksheet" for discoverability). Detailed parameters and examples are in `references/lark-sheets-range-operations.md`.
>
> Conventional usage: row heights use `--range` + `--height <px>`, column widths use `--range` + `--width <px>`, and there is no need to pass `--type` again (equivalent to `--type pixel`); for multiple rows / multiple columns with different sizes, use the map form `--heights` / `--widths` (such as `--widths '{"A":100,"C:E":120}'`) to complete it in one call, rather than splitting into multiple calls or using `+batch-update`. `--type standard` / `--type auto` are for non-pixel mode and cannot be given together with pixel flags. `+cols-resize.--type` does not accept `auto` (column width does not support auto-fit). ⚠️ The unit is pixels (not Excel character units / points).

### `+dim-freeze`

Freezing is a **full-state overwrite**, not accumulation by axis: `--rows` / `--cols` together describe the complete target state, and any axis not written means not frozen. Therefore, to freeze both rows and columns at the same time, you must provide them all at once; splitting into two calls will leave only the axis from the last call.

```bash
# Freeze the first 1 row + first 2 columns (provide all at once)
lark-cli sheets +dim-freeze --url "..." --sheet-id "$SID" --rows 1 --cols 2

# Unfreeze rows but keep columns: write out the axis to keep as well
lark-cli sheets +dim-freeze --url "..." --sheet-id "$SID" --rows 0 --cols 2
```

<a id="dim-group--dim-ungroup大纲"></a>
### `+dim-group` / `+dim-ungroup` (outline)

> Triggered only when the user explicitly says "row grouping / column grouping / outline / outline"; to group data by field use `+pivot-create`.

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute Constraints

- `Validate`: XOR common four-piece set; `--range` / `--source-range` must be valid A1 closed intervals (rows use numbers, columns use letters, and they cannot be mixed); `+dim-insert`'s `--count` > 0; `+dim-freeze` must provide at least one of `--rows` / `--cols`; `+dim-move`'s `--target` must be the same dimension as `--source-range` (row vs column); `+dim-delete` enforces `--yes` or `--dry-run`, choose one of `--range` and `--ranges`, and `--ranges` intervals must all be the same dimension and cannot overlap (≤100); `+rows-resize` / `+cols-resize`'s unified form (`--range` + `--height`/`--width` or `--type`) and map form (`--heights`/`--widths`) are choose-one and cannot be mixed; see `references/lark-sheets-range-operations.md` for details.
- `DryRun`: write operations output "the target range to be PATCHed + target parameters".
- `Execute`: after writing, you must call `+sheet-info --include row_heights,col_widths,hidden_rows,hidden_cols,groups,frozen,merges` to verify the affected range according to this structural action.
