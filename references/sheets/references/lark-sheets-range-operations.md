# Lark Sheet Range Operations

<a id="结构性操作影响面预检清除--合并--排序--移动前必做"></a>
## Structural Operation Impact Pre-check (mandatory before clear / merge / sort / move)

`+cells-clear`, `+cells-{merge|unmerge}`, and `+range-{move|copy|fill|sort}` (move / copy / sort / auto-fill) all cause existing reference relationships to shift or become invalid. **Before the operation you must** first confirm the following two points; otherwise execution is prohibited:

1. **Print the current merged cells + formula references + data validation ranges**: use `+sheet-info --include merges` + `+cells-get` to sample the target area and the data sources of formulas / pivot tables / charts / conditional formatting / filters around it; assess whether these references still point to the correct data after the operation.
2. **`+cells-clear` must not intrude beyond the user's authorized scope**: the clear range can only be the area the user explicitly wants cleared; do not casually clear adjacent cells that "look useless".

For details on storage type identification and extracting numeric values into helper columns in sort scenarios, see the "Must-read before sort operations" section below.

<a id="使用场景"></a>
## Use Cases

Write. Perform structural operations on a specified range. This reference covers 9 shortcuts, organized into 4 categories of use:

| Operation need | Tool to use | Description |
|---------|---------|------|
| Clear content/format | `+cells-clear` | "clear", "delete content", "remove formatting" |
| Merge/unmerge cells | `+cells-{merge|unmerge}` | "merge cells", "unmerge" |
| Adjust row height/column width | `+rows-resize / +cols-resize` | "widen column", "adjust row height", "auto-fit column width" |
| Move/copy/fill/sort | `+range-{move|copy|fill|sort}` | "move data", "copy to", "auto-fill", "sort by a column" |

Notes:

- **Do not mix up the two syntaxes of `--range`**: `+cells-clear` / `+cells-{merge|unmerge}` / `+range-*` use a cell A1 rectangle (e.g. `A2:A10`); `+rows-resize` / `+cols-resize` use pure row / column intervals (rows `2:10`, columns `A:C`), do not pass `A2:A10` to resize
- When the user says "this row / the whole row / the first row", prefer using a whole-row range such as `1:1`; for "this column / the whole column" use `J:J`. Do not truncate to a partial rectangle
- After merging, only the content of the top-left cell is retained; the rest is cleared. To write into a merged area, use `+cells-set` on the top-left cell
- When adjusting row height or column width, first read the dimensions of adjacent rows/columns before deciding on pixel values; do not guess arbitrarily
- `--copy-to-range` (a parameter of `+cells-set`) copies values/formulas/styles, not row height or column width. When uniform dimensions are needed, call `+rows-resize / +cols-resize` separately

**Sorting must cover the full record width**: `+range-sort --range` is the boundary for atomic movement of an entire row record, and must cover from the first column of the record to the last column; "sort by column B" only means `--sort-keys` selects B, not that the range should be written as `B:B`. If the range includes a header, add `--has-header`. After sorting, read back the first few rows and the last row to confirm that the columns still maintain their same-row relationships.

<a id="写入后列宽自适应防内容遮挡"></a>
## Column Width Auto-fit After Writing (prevent content occlusion)

After writing text / numbers you **must** proactively check whether the column width fits; otherwise user-perceivable problems occur such as "content truncated / long numbers displayed in scientific notation / text overflow occluded by adjacent columns":

1. **Read back the character count of the longest content after writing**: use `+csv-get` to read the actual written content of the target column, and count the character count of the longest cell (`max(len(cell) for cell in col)`). Estimate Chinese characters as 2 characters wide, and half-width letters/digits as 1 character.
2. **Determine the threshold**: the current column width (obtained with `+sheet-info --include row_heights,col_widths`) ≥ longest character count × font width coefficient + buffer counts as fitting. The default column width of 11 is usually only enough for 11 half-width characters or 5-6 Chinese characters; before writing long text you must widen it.
3. **Fix with one of two options**:
   - **Widen the column**: use `+rows-resize / +cols-resize` to set the target column width to `max(表头字符数, 内容采样最长字符数) × 8 + 16` pixels (empirical value)
   - **Wrap text**: when using `+cells-set`, set `cell_styles.word_wrap="auto-wrap"` on the cell (possible values: `overflow` / `auto-wrap` / `word-clip`; for the `cell_styles` field see `references/lark-sheets-write-cells.md`), and use `+rows-resize / +cols-resize` to increase the row height of the corresponding row
4. **Default column width rule for new columns**: the width of a new column ≥ `max(表头字符数, 内容采样最长字符数) × 8 + 16` pixels; it is **prohibited** to deliver directly with the default 11.

**Typical counterexample**: default column width 11 but the content contains 12+ characters of Chinese / numeric values with units (e.g. `109.10μmol/L`) / long numbers without `number_format` displayed in scientific notation — the user cannot see the complete original value in the result sheet.

**Control total width for print scenarios (mandatory when the user says "fit for printing / A4 / print range")**: while widening individual columns to prevent truncation, **the sum of all column widths must fall within the printable width of the paper** — A4 landscape is about ≤ 102 half-width characters (about 1000px), portrait about ≤ 70 characters. When too wide, do not widen indefinitely; instead use `cell_styles.word_wrap="auto-wrap"` + increase row height, or narrow non-critical columns, so the whole table fits on one page (counterexample: total column width far exceeds the A4 printable width, and long-text rows are truncated because the row height is insufficient).

**Only widen the columns carrying new content; do not change the column widths of existing columns**: column width auto-fit **only targets newly added columns / columns that genuinely cannot fit the new content**; the column widths of columns already present in the original table **must not be recalculated and must not be narrowed** — even if your estimated "ideal width" differs from the original value, as long as the original content is not truncated, do not touch it. Resetting the width of every column indiscriminately (even by only ±1) counts as destroying the original file's visual formatting (counterexample: after filling in data, casually changing an existing column's width from 16 to 17, inconsistent with the original attachment, destroying the original visual formatting).

**⚠️ Safe operation rules for merged cells** (`+cells-{merge|unmerge}` must-read):

1. **Read before write**: before operating you must use `+sheet-info --include merges` or `+cells-get` to identify existing merged areas (characteristic: among multiple consecutive cells only the top-left one has a value, the rest are empty).
2. **Do not merge again on an already merged area**: calling merge again on an already merged area will error or produce unpredictable results.
3. **Correct order for modifying a merged area**: first `unmerge` → modify content/style → then `merge`.
4. **Setting styles on a merged area**: set `cell_styles` only once for the complete range (written on the top-left cell), and use `{}` as a placeholder for the remaining positions.
5. **Data protection when adding a merge**: before merging, confirm that only the top-left cell of the target area has data and the rest are empty; otherwise merging will cause data in non-top-left cells to be lost.
6. **Batch unmerge needs only one call**: when multiple merged areas exist within one range (whole column `A:A`, whole row `3:3`, rectangle `A1:D100`), directly call `+cells-unmerge` once passing this large range, and all merged areas within that range will be unmerged in one go; **do not** call unmerge separately for each merged area, and do not use `+batch-update` to split it into multiple unmerge calls.
7. **Must verify after merge / unmerge**: `+sheet-info --include merges` to check the target range, then `+cells-get` to read back the top-left value and the cleared state of non-top-left cells.

**⚠️ Do not call multi-area merges one by one**: when performing `+cells-merge` on **multiple** different areas, write it as a single `+styles-put --styles` `cell_merges` delivered in one go (merge and style / row height and column width / freeze all belong to the same declarative specification, see `references/lark-sheets-styles-put.md`); only when the merge is embedded in a **cross-type, order-dependent** operation chain (e.g. insert column → merge → write header) use `+batch-update` (fail-fast; for failure handling and input format see `references/lark-sheets-batch-update.md`). The same applies to row height and column width — `+batch-update` is **not needed**: for different sizes across multiple rows / columns, directly use the map form of `+rows-resize --heights` / `+cols-resize --widths`, completing it in one call.

**The only exception**: `+cells-unmerge` natively supports passing one large range to unmerge all merged areas within it in one go; you should call it directly once, and **do not** split it into `+batch-update`.

**⚠️ Must-read before sort operations: confirm the data type of the target column**

Sorting compares by the cell's **storage type**: pure numbers sort numerically; text strings sort by **lexicographic order** (`"1000"` comes before `"999"`, the opposite of numeric order); dates sort by timestamp.

The following forms **look like numbers but are actually strings**; sorting them directly will produce wrong results:

| Example | Description |
|------|------|
| `843688.69+20042.35=863731.04` | Expression text (without a leading `=` it is not a formula; the whole string is compared lexicographically) |
| `¥1,234.56` / `$1,234` | With currency symbol |
| `1.2万` / `3.5亿` / `100kg` | With Chinese / English units |
| Numeric strings with leading/trailing spaces or invisible characters | Treated as text |
| A column mixing text and numbers | Sorted in blocks |

**Hard process**:

1. Before sorting, first use `+csv-get` to sample the first 3–5 rows of the target column to confirm the original value form; do not sort directly based only on the column name and the user's question.
2. If it is pure numbers or dates → sort directly.
3. If it is text with symbols / expressions / units → **do not sort directly, and do not read the values and then use `+csv-put` to overwrite the original table to simulate sorting**:
   - Simple scenarios (currency, thousands separators, unit prefixes): add a helper column, use a formula to extract the numeric value (e.g. `=VALUE(SUBSTITUTE(SUBSTITUTE(A2,"¥",""),",",""))`), then use `+range-sort` to sort atomically by the helper column; after sorting you may delete the helper column as needed.
   - Complex scenarios (multi-segment expressions, Chinese units, mixed formats): first write a helper numeric column, then use `+range-sort`; when reliable extraction is impossible, keep the original order and explain, and it is prohibited to overwrite and write back the whole block.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+cells-clear` | high-risk-write | Cell |
| `+cells-merge` | write | Cell |
| `+cells-unmerge` | write | Cell |
| `+rows-resize` | write | Worksheet |
| `+cols-resize` | write | Worksheet |
| `+range-move` | write | Range |
| `+range-copy` | write | Range |
| `+range-fill` | write | Range |
| `+range-sort` | write | Range |

## Flags

### `+cells-clear`

_Common four-piece set · System: `--yes`, `--dry-run`

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | Clear range (A1 format) |
| `--scope` | string | optional | Clear range enum: `content` (default, clear content only) / `formats` (clear format only) / `all` (clear content + format) (possible values: `content` / `formats` / `all`) |

### `+cells-merge`

_Common four-piece set · System: `--dry-run`

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | Range to merge / unmerge (A1 format) |
| `--merge-type` | string | optional | Merge direction (only for `+cells-merge`) (possible values: `all` / `rows` / `columns`) (default `all`) |

### `+cells-unmerge`

_Common four-piece set · System: `--dry-run`

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | Range to merge / unmerge (A1 format) |

### `+rows-resize`

_Common four-piece set · System: `--dry-run`

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--height` | int | xor | Uniform row height (pixels, e.g. 30 / 40 / 60; not points), used with `--range`. Passing `--height` means pixel mode, and `--type` may be omitted; explicitly passing `--type pixel` also works (equivalent). For multiple rows with different heights use `--heights` |
| `--heights` | string + File + Stdin (composite JSON) | xor | Differentiated row height map, setting different heights for multiple rows in one call: keys are a single row (`"1"`) or a closed row interval (`"2:20"`), values are pixel heights (e.g. 30 / 50), `"auto"` (fit to content), or `"standard"` (reset to default). ⚠️ The unit is pixels, not points. Mutually exclusive with `--range` / `--height` / `--type` |
| `--type` | string | xor | Sizing method enum: `pixel` (requires `--height`) / `standard` (reset to default row height) / `auto` (auto-fit to content). In the conventional form, just giving `--height` allows omitting this flag; `--type standard` / `--type auto` cannot be given together with `--height` (possible values: `pixel` / `standard` / `auto`) |
| `--range` | string | xor | Closed interval of rows whose row height is to be adjusted; 1-based row numbers such as `2:10` or a single row `5`. Required in the uniform-size form (with `--height` or `--type`); not passed in the map form (`--heights`) |

### `+cols-resize`

_Common four-piece set · System: `--dry-run`

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--width` | int | xor | Uniform column width (pixels, e.g. 80 / 120 / 200; not Excel character units), used with `--range`. Passing `--width` means pixel mode, and `--type` may be omitted; explicitly passing `--type pixel` also works (equivalent). For multiple columns with different widths use `--widths` |
| `--widths` | string + File + Stdin (composite JSON) | xor | Differentiated column width map, setting different widths for multiple columns in one call: keys are a single column (`"A"`) or a closed column interval (`"C:E"`), values are pixel widths (e.g. 80 / 120 / 200) or `"standard"` (reset to default). ⚠️ The unit is pixels, not Excel character units (pixels ≈ character count × 8 + 16). Mutually exclusive with `--range` / `--width` / `--type` |
| `--type` | string | xor | Sizing method enum: `pixel` (requires `--width`) / `standard` (reset to default column width). In the conventional form, just giving `--width` allows omitting this flag; `--type standard` cannot be given together with `--width` (possible values: `pixel` / `standard`) |
| `--range` | string | xor | Closed interval of columns whose column width is to be adjusted; column letters such as `A:E` or a single column `C`. Required in the uniform-size form (with `--width` or `--type`); not passed in the map form (`--widths`) |

### `+range-move`

_Common four-piece set · System: `--dry-run`

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--source-range` | string | required | Source A1 range |
| `--target-sheet-id` | string | optional | Target sub-sheet id; when omitted, the same source sheet |
| `--target-range` | string | required | Target A1 range (passing the starting cell is enough; automatically inferred from the source dimensions) |

### `+range-copy`

_Common four-piece set · System: `--dry-run`

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--source-range` | string | required | Source A1 range |
| `--target-sheet-id` | string | optional | Target sub-sheet id; when omitted, the same source sheet |
| `--target-range` | string | required | Target A1 range (passing the starting cell is enough; automatically inferred from the source dimensions) |
| `--paste-type` | string | optional | Paste content (only for `+range-copy`) (possible values: `values` / `formulas` / `formats` / `all`) (default `all`) |

### `+range-fill`

_Common four-piece set · System: `--dry-run`

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--source-range` | string | required | Fill template range (series starting cells) |
| `--target-range` | string | required | Target fill range (A1 format) |
| `--series-type` | string | optional | Fill series type (possible values: `auto` / `linear` / `growth` / `date` / `copy`) (default `auto`) |

### `+range-sort`

_Common four-piece set · System: `--dry-run`

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | Sort range (A1 format; whether it includes a header is determined by `--has-header`) |
| `--sort-keys` | string + File + Stdin (composite JSON) | required | JSON array: `[{"column":"<列字母>","ascending":<bool>}, ...]` |
| `--has-header` | bool | optional | The first row is a header and does not participate in sorting; default false |

## Schemas

> Composite JSON flag field quick reference (only top level + one level of nesting). For deeper structures see `## Examples` below, or use `--print-schema` to read the complete JSON Schema (usage see index.md "Common flag quick reference" and "Agent usage tips").

### `+rows-resize` `--heights`

_Row → height map_
- type: object

### `+cols-resize` `--widths`

_Column → width map_
- type: object

### `+range-sort` `--sort-keys`

_Sort condition list (only for sort operations)_

**Array items** (type object):
- `column` (string) — the column letter to sort by (e.g. "C", "D"), must be within the range
- `ascending` (boolean) — whether to sort in ascending order

## Examples

> ⚠️ The shortcuts derived from this reference span 3 groups: `+rows-resize` / `+cols-resize` → Worksheet, `+cells-*` → Cell, `+range-*` → Range. Here they are explained uniformly from the perspective of range operations.

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` (XOR) arranged at the top.

### `+cells-clear`

> ⚠️ **`--scope all` clearing the entire sheet is irreversible large-scale destruction**: it will also wipe out the merged cells in that area, the original formulas, and the data source columns referenced by charts / pivot tables (such columns are often to the right of the main data area, visually "looking useless" but referenced by legends / series). **"Beautifying / normalizing an existing sheet" never requires clearing the original sheet and rewriting it**—if you intend to "clear the original sheet → write the rearranged version", that means you have taken the wrong path; instead, only refresh the styles in place (see `references/lark-sheets-visual-standards.md` scenario three).

> **Cannot delete embedded objects**: `+cells-clear` (any `--scope`, including `all`) only clears the values / formats of cells, and **cannot delete** embedded objects such as pivot tables / charts overlaid within the range—the backend will report `can not find embedded block`. To delete a pivot table use `+pivot-delete`, to delete a chart use `+chart-delete` (first use `+pivot-list` / `+chart-list` to get the object id).

> When you need to clear **multiple non-contiguous ranges** at once (such as batch-removing borders/background colors scattered in various places after moving content away), use `references/lark-sheets-batch-update.md`'s `+cells-batch-clear` instead, to avoid calling `+cells-clear` range by range.

```bash
# dry-run first look
lark-cli sheets +cells-clear --url "..." --sheet-id "$SID" --range "A2:Z1000" --scope all --dry-run
# execute
lark-cli sheets +cells-clear --url "..." --sheet-id "$SID" --range "A2:Z1000" --scope all --yes
```

### `+cells-merge` / `+cells-unmerge`

```bash
# merge A1:C1 (optional --merge-type all/rows/columns)
lark-cli sheets +cells-merge   --url "..." --sheet-id "$SID" --range "A1:C1"
# unmerge: pass a large range to unmerge all merged areas within it at once
lark-cli sheets +cells-unmerge --url "..." --sheet-id "$SID" --range "A1:C100"
```

### `+rows-resize` / `+cols-resize`

Row height and column width are split into two shortcuts, to avoid mixing the differences between rows / columns in the underlying schema (rows support `auto`, columns do not). Two forms:

- **Uniform size**: `--range` + `--height`/`--width <px>` (omitting `--type` is equivalent to `--type pixel`). Non-pixel mode uses `--type standard` / `--type auto`, and in this case pixel values cannot be given.
- **Differentiated sizes**: `--heights`/`--widths` a single JSON map, with keys being a single row/column or a closed interval, and values being pixels or mode strings, **completing multiple rows / columns with different sizes in one call**—do not split into multiple calls, and do not use `+batch-update`.

```bash
# Uniform size: set rows 2-10 to a fixed 30 px
lark-cli sheets +rows-resize --url "..." --sheet-id "$SID" --range "2:10" --height 30

# Uniform size: set columns A-C to a fixed 120 px
lark-cli sheets +cols-resize --url "..." --sheet-id "$SID" --range "A:C" --width 120

# Differentiated sizes: multiple columns with different widths, in one call (values can mix in "standard" to reset a column)
lark-cli sheets +cols-resize --url "..." --sheet-id "$SID" \
  --widths '{"A": 100, "B": 358, "C:E": 120, "G": "standard"}'

# Differentiated sizes: multiple rows with different heights, values can mix "auto" / "standard"
lark-cli sheets +rows-resize --url "..." --sheet-id "$SID" \
  --heights '{"1": 50, "2:20": 30, "21": "auto"}'

# Row 1 row height automatically adapts to content (column width does not support auto)
lark-cli sheets +rows-resize --url "..." --sheet-id "$SID" --range "1" --type auto

# Reset columns A-E to the default column width
lark-cli sheets +cols-resize --url "..." --sheet-id "$SID" --range "A:E" --type standard
```

**⚠️ The unit is pixels, not Excel character units / points**: column widths are commonly 60~400px; if you calculate in your head using Excel character units (openpyxl / xlsxwriter's `width`), first convert `px ≈ 字符数 × 8 + 16`—writing `{"A": 10}` gives you an unusable narrow column of 10px (the CLI will reject column widths < 20px and prompt for conversion). Row height is pixels, not points; the default row height is about 24px.

**Column width has no auto-fit**: when you need "column width auto-adapting to content", estimate the pixel value using the formula in the "column width auto-adapts after writing" section (`max(表头字符数, 内容最长字符数) × 8 + 16`), then explicitly set it with `--widths`.

> Also appears in `references/lark-sheets-sheet-structure.md` — row height / column width adjustment also counts as a row-column structure layer action.

### `+range-move` / `+range-copy`

> `+range-move` will **clear the source range** (move = copy + clear_source); `+range-copy` does not touch the source.

### `+range-fill`

```bash
# Use the sequence pattern of A1:A2 to fill down to A3:A100 (the target range cannot overlap with source, otherwise the backend reports source overlaps destination)
lark-cli sheets +range-fill --url "..." --sheet-id "$SID" --source-range "A1:A2" --target-range "A3:A100" --series-type auto
```

### `+range-sort`

```bash
# Sort A1:E100 by column C descending (the first row is a header and does not participate)
lark-cli sheets +range-sort --url "..." --sheet-id "$SID" --range "A1:E100" --has-header --sort-keys '[{"column":"C","ascending":false}]'
```

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute constraints

- `Validate`: XOR common four-piece set; `+cells-clear` forces `--yes` or `--dry-run`; `+range-*` validates that the source / target ranges are in the same spreadsheet; `+range-sort`'s `--sort-keys` must be a valid JSON array and all cols must be within `--range`; `+rows-resize` / `+cols-resize` choose one of the two forms—the uniform form must give `--range` and at least one of `--height`/`--width` or `--type` (`--type standard`/`auto` cannot be given together with pixel flags, `--type pixel` coexisting is OK), the map form (`--heights`/`--widths`) cannot be mixed with `--range`/`--height`/`--width`/`--type`, map keys must match the command dimension (row numbers / column letters), must not be duplicated, and values must be positive integer pixels or mode strings; column width < 20px is rejected (suspected Excel character units); `+cols-resize` does not accept `auto` (column width does not support auto-fit). The map form is unavailable in the `+batch-update` sub-operation (it is itself a batch submission).
- `DryRun`: all write operations output "the range to be PATCHed + an estimate of the number of affected cells".
- `Execute`: after sort/move/copy/fill, read back the first, middle, and last records; after merge/unmerge, verify the range, top-left value, and boundaries with `+sheet-info --include merges` + `+cells-get`; after clear, confirm the target scope is empty; for resize results, verify the size with `+sheet-info`, and do not only read cell values.
