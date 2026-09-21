# Lark Sheet Write Cells

<a id="写入边界--回读诊断编辑类任务建议"></a>
## Write Boundaries + Read-Back Diagnostics (Recommended for Editing Tasks)

1. **Clarify write boundaries**: Before writing, you should be able to answer "What are the start and end row/column numbers of the target range? Does it fall within the user-authorized scope?" Except for areas the user explicitly wants modified, avoid expanding beyond the original data columns or creating new Sheets.
2. **Completeness assertion**: Before batch writing, hardcode the "expected number of rows to write" into the code (e.g., to fill 106 translations → `expected = 106`), and after writing, read back and compare `actual == expected`. If fewer than expected, prioritize filling the gap; if it cannot be filled, list the shortfall in the delivery notes.
3. **Read-back sampling verification**: After writing key values / regular formulas, use `+csv-get` or `+cells-get` to re-read the written area, sampling at least 3-5 representative cells (first / middle / last), and verify the values match expectations (compare against expected values calculated by the local script). For AI formula calculation status, do not first poll with `+cells-get`; instead directly follow the `references/lark-sheets-formula-verify.md` rule of performing a single asynchronous status check across the entire `+formula-verify --ai-only --range` range. For formula-specific details on "verify the template first, then --copy-to-range / read back after fixing," see the relevant sections below.
4. **Protect the original table · Placement of derived outputs (easy to lose data when writing ranking / markers / summaries / rewritten columns)**: Derived results should preferably be written to a **brand-new empty column at the real last column + 1** or a new sub-sheet, avoiding reuse of any existing original data column—even if that column appears "empty," first use `+csv-get` to read back and confirm the entire column has no original data before writing. Three guidelines: ① Try not to write new formulas / new values into original data columns (typical counterexample: writing a newly calculated ranking formula into a column that originally stored another set of raw data, overwriting and losing the entire column of original data); ② Try not to rewrite or merge original header field names (typical counterexample: merging several independent header fields into one column, losing the original field names); ③ Use `--allow-overwrite` with caution: once it causes the write area to cover adjacent original columns / rows, it is irreversible data loss. Before adding it, use `+sheet-info` / `+csv-get` to verify that the target range contains no original data.

<a id="新增列--新增行的样式继承防止视觉风格不一致"></a>
## Style Inheritance for New Columns / New Rows (Preventing Visual Style Inconsistency)

When adding new columns / new rows, apply styles first, then write values, in two steps—avoid passing only `value` and expecting the default style to match the original table (the default alignment for new Feishu cells is usually `H:right, V:bottom`, which is inconsistent with the `H:center, V:middle` of most original tables).

**Recommended approach (one step)**: Use `+range-copy --paste-type formats` to copy the style of an adjacent original column/row to the target area, then write values. `--paste-type formats` only copies styles without touching values. The target area size is inferred from the **source area**; `--target-range` only provides the target's top-left anchor cell; to fill an entire column, the source area must cover the entire column (e.g., `C1:C100`). The command must include complete positioning (one each of `--url`/`--spreadsheet-token` and `--sheet-id`/`--sheet-name`):

```bash
# New column D — copy column C's style to column D (source 100 rows → target starting from D1 for 100 rows)
lark-cli sheets +range-copy --url "<表格URL>" --sheet-name "<真实表名>" \
  --source-range "C1:C100" --target-range "D1" --paste-type formats

# New row 20 — copy row 19's style to row 20
lark-cli sheets +range-copy --url "<表格URL>" --sheet-name "<真实表名>" \
  --source-range "A19:Z19" --target-range "A20" --paste-type formats
```

The target anchor + source size determine the landing area; there is no need to write out the full range in `--target-range`. For parameter details, see `references/lark-sheets-range-operations.md`.

**Manual approach (when precise control is needed)**: First use `+cells-get --include style` to read the complete style of an adjacent cell as a template, then carry `cell_styles` cell by cell in `+cells-set`'s `--cells`. Fields that need to be inherited:

1. `cell_styles.font_family` / `cell_styles.font_size` / `cell_styles.font_weight` / `cell_styles.font_color` / `cell_styles.font_style`
2. `cell_styles.horizontal_alignment` / `cell_styles.vertical_alignment` — failing to inherit these causes new column alignment to be inconsistent with the original column (common)
3. `cell_styles.number_format` — failing to inherit this causes number formats within the same column to become inconsistent
4. `cell_styles.background_color`
5. `border_styles`
6. **`merged_cells` (merge ranges)**—must check in continuation scenarios: use `+sheet-info --include merges` to read the merge information of the original data area. When original rows have cross-column merges, new rows should use `+cells-{merge|unmerge}` to copy the same merge pattern. Passing only the cells array styles is not enough—merge ranges must be applied separately via `+cells-{merge|unmerge}`.

**Anti-patterns** (risks):
- Passing only `{"value": "四级菜单"}` to D1 without `cell_styles` → D1 defaults to non-bold, non-centered, breaking style continuity with A1/B1/C1
- When writing `=SUM(F5:L5)` to new column M5, passing only `formula` without styles → column M alignment becomes `H:right`, number format becomes default

<a id="长数字防科学计数法数值列写入必查"></a>
## Preventing Scientific Notation for Long Numbers (Must-Check for Numeric Column Writes)

For columns where writing or calculation results may produce long numbers (≥ 12-digit integers / high-precision decimals), it is recommended to explicitly set a non-general format in `cell_styles.number_format`, otherwise Feishu will automatically display them in scientific notation, and what the user sees is "content truncated / original value unreadable."

| Scenario | Required `number_format` |
|---|---|
| Long integers (order numbers / ID numbers / document numbers) | `"0"` or `"@"` (force text to avoid precision loss) |
| Amounts / thousands separator | `"#,##0.00"` |
| Percentages | `"0.00%"` |
| Quantities / counts | `"0"` (integer) |
| Dates | `"yyyy-mm-dd"` or `"yyyy/m/d"` |

**Typical counterexample**: A long-number column (such as approval numbers, serial numbers) without `number_format` set, Feishu displays it as `1.23E+15`, and the user has already lost precision when copying it out.

> **Number or text: choose based on "is the data essentially a quantity or an identifier" — not based on whether calculation is needed right now**: Data that is **essentially a quantity**, such as amounts / percentages / ratios / counts / measurements, should preferably be written as **numeric types** (percentages stored as decimals `0.54` with `number_format:"0%"`), avoiding `@` text format. **This is unrelated to "whether the user currently wants to sort / sum"**—data type is determined by the nature of the data, not by its current use: spreadsheet data will almost always be reused for subsequent sorting / charts / secondary calculations, `"54%"` text mixed with numeric columns inherently breaks consistency, and numbers + `number_format` display **identically** to text, so there is no reason to choose text. **The most common misjudgment is "this is just a leaderboard / report / dashboard display, no calculation needed, so writing it as a `54%` string is fine"—this is wrong; display purposes do not change the fact that "a percentage is a numeric value."** (`+table-put` uses `dtypes` to declare `int64` / `float64`; when the layout `+table-put` cannot fit, use `+cells-set` to pass numbers + `number_format`; in all cases, do not locally concatenate into strings with `$` / `%` and pass them through `+csv-put`.) Conversely, content that is **essentially an identifier / label** and must be preserved as-is without Feishu automatically interpreting it—such as numbers `001`, specifications `3-1`, ID numbers / phone numbers / document numbers (otherwise `001`→`1`, `3-1`→date, dotted dates `12.10`→`12.1` (trailing zeros lost), long numbers→scientific notation)—should only be written as **string types** (`dtypes` set `object`) with `number_format` set to `"@"` (text format), preserving literal fidelity.

**Typed columns must explicitly declare types**: Amounts, percentages, dates, booleans, counts, and quantity columns that will later participate in sorting / aggregation / charts must have their types declared column by column in `+table-put`'s `dtypes`, with `formats` controlling display; do not rely on string appearance or automatic type guessing. Pure text/identifier tables can declare all as `object`. For mixed columns, first preserve original values and add cleaning results/failure markers, and count totals, successes, failures, and nulls; means/ratios must specify the denominator, and it is forbidden to silently drop failed values and change the calculation basis.

**Appending data**: For ordinary end-of-table appending, directly use `+table-put`'s `mode:"append"`, which automatically locates the last row; only when the user explicitly requests physically inserting rows in the middle, inheriting template blocks, or extending merge structures, first use `+dim-insert`.

<a id="使用场景"></a>
## Use Cases

Writing. Write values, formulas, styles, comments, images, or dropdowns to a cell range in a Feishu sheet; also supports batch writing of CSV / DataFrame. This reference covers 6 shortcuts; choose based on data source + content form:

> ⚠️ **Calculation results default to writing formulas, not static values**: Numbers / statistics / rankings / proportions that need to be calculated should by default be written as formulas to cells, not computed in Python and then hardcoded. Exceptions to the formula-first principle: externally fetched data, constants that never change, circular references.

| Scenario | Use this shortcut | Reason |
|------|----------------|------|
| The model already has CSV text in hand (small-scale manual construction, simple processing after retrieving from `+csv-get`) | `+csv-put` | Directly pass CSV text + `--start-cell`, no need to build a 2D cells array yourself; automatically expands rows/columns when necessary |
| Columns with numeric-semantic data (numbers / amounts / percentages / dates / counts) → Feishu, requiring type fidelity (source unrestricted: DataFrame, Counter, dict, list all count) | `+table-put` | Each typed protocol item must contain `name/columns/data`, can include `start_cell/mode/header/allow_overwrite/dtypes/formats`; numeric-semantic columns explicitly declare `dtypes`, `formats` controls thousands separator / percentage / date. Dates land as real dates, numeric columns can be sorted / summed / charted, string preserves leading zeros, multiple sheets written in one pass |
| Writing any rich content including styles, comments, images, data validation, etc. | `+cells-set` | The only shortcut supporting complete rich fields (formulas `+csv-put` can also be written) |
| Only modifying existing cell styles, without touching value/formula | `+cells-set-style` | Flattens 10 style fields into independent flags; does not trigger unnecessary value writes |
| Single cell embedded image | `+cells-set-image` | Shorter parameters than `+cells-set` |
| Locally supplementing header styles/borders in an **existing area** | First use `+csv-put` to write values, then use `+cells-set-style` to supplement styles | Division of labor, shortest input parameters |
| **Creating a new sub-sheet / full-sheet beautification** (even if all plain text) | `+table-put --sheets … --styles …` one step with values + full styles (area background / borders / column width / row height / merges; sheet names not present in the payload automatically create sub-sheets) | `--styles` is unrelated to whether columns are typed; plain text applies equally; saves several calls compared to "write values + multiple style refreshes" |

**Choose commands by content form (no "default first choice")**: ① Columns with numeric semantics (amounts / percentages / dates / counts) → `+table-put` (`dtypes` declares types + `formats` sets display format); when the layout cannot fit → `+cells-set` pass numbers + `number_format`; ② Need styles / comments / images / rich text → `+cells-set`; ③ **Only** all-text content with no numeric semantics, flat → `+csv-put` (shortest input parameters). For criteria, see "Number or Text" above.

⚠️ `+csv-put` can write values or formulas: cells starting with `=` are treated as formulas and calculated (when read back, the `formula` field is preserved and `value` is the calculated result). **When formulas contain commas / quotes / newlines, it is recommended to escape according to RFC 4180**—fields containing commas should be wrapped in double quotes, and quotes inside fields should be doubled: e.g., `=COUNTIF(D5:D22,"及格")` should be written as `"=COUNTIF(D5:D22,""及格"")"`. Missing escapes will cause the CSV parser to split columns by commas, misaligning the entire write area. **Therefore, formulas containing commas / quotes / newlines should preferably use `+cells-set`**; `+table-put` does not support formula fields.

⚠️ **`+csv-put` will land numbers as text**: If you locally concatenate amounts / percentages / counts into strings with `$` / `%` / thousands separators (e.g., `"$1,234.50"` / `"+30.5%"`) and then pour them in via `+csv-put`, the cells will be **text**—losing sorting / summing / charting capabilities, and unable to participate in calculations when mixed with numeric columns. For how numbers should be written, when to use `+table-put`, and when to fall back to `+cells-set` passing numbers + `number_format` when the layout cannot fit, see "Number or Text" above for criteria and routing; the core point: **when you are about to format a number into a string before writing, you have taken the wrong path; numbers should always be written as numbers + `number_format` controls display.**

⚠️ **`+csv-put` will also silently numericize fields that "look like numbers"** (the other half of the pitfall, opposite to the previous point): Columns in CSV whose semantics are **date labels / numbers / identifiers** but whose content is entirely numeric characters will be parsed as numbers—`12.10`→`12.1` (dotted date trailing zeros lost), `3.0`→`3`, `001`→`1`, long numbers→scientific notation. **For such columns, even if CSV text is already prepared, it is not recommended to go through `+csv-put` bare**: prefer `+table-put` to declare that column's `dtypes` as `object` (dotted labels without years such as `12.10` / `3-1` preserve literal fidelity) or `datetime64[ns]` (complete real dates); if the layout cannot fit, fall back to `+cells-set` + `number_format:"@"`. Such distortions are easily masked during "sample first / middle / last" read-backs (rows with trailing zeros like `12.10` / `12.20` often do not fall within the sampling window); for date / number column read-backs, specifically pick representative values with trailing zeros / leading zeros to verify.

⚠️ Large data write-backs should follow "`+csv-get` read to local in batches by `--range` row windows + local script processing + `+csv-put` batch write-back."

<a id="cells-set-写入要点常用模式--公式--样式"></a>
## `+cells-set` Writing Key Points (Common Patterns / Formulas / Styles)

> The following are common patterns and guidelines for rich writing with `+cells-set` (and `+cells-set-style`); for which shortcut to choose, see "Use Cases" above.

`+cells-set` sets values / formulas / comments / styles for a range, and also supports `rich_text`'s `type: "embed-image"` for embedding cell images. **Key: `--cells` is always a 2D array (rows × cells); a single cell is also `[[{"value":…}]]`; a bare `--range A1` (or `--start-cell`) is the top-left **anchor**, and the landing area is determined by `--cells`'s own row and column counts; writing it as a rectangle (`A1:B2`) makes it a **boundary**—if the array is smaller it narrows, if larger it is rejected, rather than writing outside the range**.

> **Cell images vs floating images**: If an image **belongs to a record and should sort / filter / add / delete along with that row** (vouchers / ID photos / per-row images, with binding words like "corresponding / per row / this column" in the request) → **cell image** (this tool): use `+cells-set-image` (shortest) or `+cells-set`'s `rich_text` + `type: "embed-image"`. If it is just freely placed decoration (logo / watermark / cover) → floating image, see lark-sheets-float-image. Do not default to floating images because "floating images are easier to control / more familiar"—images that carry "corresponding to a record" will misalign when rows are added/deleted / sorted.

Common patterns (recommended, avoiding row-by-row writing alternatives):

- Whole-column formulas: First write one formula in `H2`, then use `--copy-to-range "H2:H100"` or `--copy-to-range "H:H"` to fill down. Avoid calling `+cells-set` separately for each row to write formulas with the same structure
- Whole-column styles: Use `+cells-set-style` or `+styles-put` to specify the target range; do not use `--copy-to-range` purely for style refreshing
- First-row styles: Same as above, directly set styles on `1:1` or the actual header range
- When the user says "this column / whole column / this row / first row / copy formula down," use template cell + `--copy-to-range` for value/formula filling; use `+cells-set-style` / `+styles-put` for style-only changes
- When writing the same value/formula structure to multiple areas, preferably write one template, then copy with `--copy-to-range`; if only styles are the same, still use style commands

⚠️ **`--copy-to-range` copies the template cell's entire content (values + formulas + styles), not just styles**: Do not use it to "refresh styles" when the target area **already has values**—it will overwrite the entire area's values with the template cell's values (this is how the accident of 65 cells all becoming the same number happens). To change only styles without touching values / formulas, use `+cells-set-style` / `+cells-batch-set-style`; `--copy-to-range` is only for scenarios where the target area is empty or you intend to write isomorphic formulas / values.

⚠️ **Template `--range` starts from the data row, do not include the header**: `--copy-to-range` will periodically tile the `--range` template according to the target area size; if the template includes a header row, the header will be repeatedly tiled into the data area every few rows. When filling an entire column, the template should take only one data cell's style (e.g., `H2`), not `H1:H2`.

⚠️ **Writing formulas row by row is a common inefficient approach**: Calling `+cells-set` separately for each row to write formulas (e.g., 26 times) is both slow and error-prone, and does not automatically shift formula references. The correct approach is 1 template write + 1 `--copy-to-range` (formula references automatically shift).

💡 **Writing to multiple non-contiguous areas (the correct way to batch-fix formulas)**: For values / formulas scattered across multiple locations (can span sheets), use `--writes` to deliver in one batch (fail-fast; after failure, read back first then resend)—each item `{sheet_name, range, cells}` (for cross-sheet items, write the sheet positioning within the item; if not written in the item, use the top-level `--sheet-name` / `--sheet-id`); do not concatenate `+batch-update`'s `--operations` for this, and do not call multiple times per area (multiple round trips, difficult to recover from mid-way failures):

```bash
lark-cli sheets +cells-set --url "..." --writes - <<'JSON'
[
  {"sheet_name":"明细","range":"D5","cells":[[{"formula":"=IFERROR(C5/B5,0)"}]]},
  {"sheet_name":"汇总","range":"B3","cells":[[{"formula":"=SUM(明细!C:C)"}]]}
]
JSON
```

Range-level uniform styles are not done in `--writes` (cells' per-cell `cell_styles` is only for per-cell differentiation); after writing, follow up with `+styles-put`.

💡 **Before writing formulas, first rewrite according to migration rules**: If the formula comes from Excel or involves array scenarios, first read and follow the rules in `references/lark-sheets-formula-translation.md` to complete the rewrite, then write the final formula into the `formula` field.

💡 **Separate content and style writing**: When styles are highly repetitive within the same area, first write content with the correct types, then use `+cells-set-style` or `+styles-put` to supplement styles for the target range; do not use `--copy-to-range` purely for style refreshing, as it will copy template values / formulas along with it. Only when the target area is empty or you intend to copy isomorphic formulas / values should you use template cells + `--copy-to-range`.

💡 **Style updates are "partial merges," not full overwrites**: `+cells-set-style` / `+styles-put` (and `+cells-set`'s `cell_styles` / `border_styles`) only modify the style properties you **explicitly pass in**; properties not passed retain their original values. Two practical corollaries:
- **Can be layered**: Apply font color to the same area first, then background color separately, then borders separately; each subsequent step will not clear the previous one—when beautifying an existing area, there is no need to include all fields at once; it can be split into multiple narrow calls.
- **`border_styles` merges per edge**: Passing only `{"top":{...}}` updates only the top border; `bottom` / `left` / `right` retain their original state; there is no need to re-pass all four edges just to "change only one edge." (For exceptions, see "Avoid using `{}` to skip borders/styles for new rows" above: **brand-new rows** have no borders underneath, so all edges to be displayed still need to be explicitly passed.)

💡 **Batch writing for large data volumes (recommended)**: When needing to write a large number of rows (e.g., dozens or more), do not attempt to generate all `cells` data in a single call—an overly large `cells` array makes the content generated in a single pass too long, prone to errors or truncation. Data should be split into multiple batches of 20-50 rows each, calling `+cells-set` multiple times to generate and write batch by batch (e.g., write `A2:D21` first, then `A22:D41`, and so on). Only generate the current batch's data each time, controlling the single-pass generation volume.

Notes:

- Do not write `cells` as stringified JSON
- `+cells-set` by default overwrites non-empty cells (`--allow-overwrite` defaults to true); to **protect** non-empty cells from being overwritten, explicitly pass `--allow-overwrite=false` (errors on non-empty cells)
- If the target area involves merged cells, do not write data to non-top-left cells within the merged area; if writing is needed, rewrite the top-left cell of the merged area, or first adjust/cancel the merged area
- **When constructing `range`, row numbers should be based on logical row numbers**: If data was previously read via `+csv-get`, multi-line fields wrapped in double quotes in the CSV (e.g., `"2026年3月2日\n星期一"`) are **one cell**, not two rows. Row numbers when writing should be calculated by logical records, not by physical newline characters, otherwise `range` will be offset entirely, causing writes to incorrect positions

> The same applies when the user says "styles consistent with the original table / keep the original table format / border inheritance": `cell_styles` only covers fonts and alignment, and **does not include borders**. For borders, it is recommended to pass them via the separate `border_styles` field — see "Style inheritance for new columns / new rows" above for the complete inheritance list.

⚠️ **After writing formulas, verification must be completed (the backend will not report all syntax / runtime errors)**: When `+cells-set` writes formulas, even if a formula has mismatched parentheses (e.g., `=IFERROR(VALUE(MID(D5,3,4))), 0)` has one more `)` than IFERROR) or uses a function not supported by Feishu (e.g., `GOOGLETRANSLATE` / `CUBEVALUE`), **the backend tool may still return `updated_cells_count=N, rc=0` "success"** — the error will be silently written into the cell and displayed as `#VALUE!` / `#NAME?` / `#REF!`. Therefore:
1. **Read back immediately after writing**: After `+cells-set`, immediately follow with `+csv-get` (or `+cells-get`) to read the first, middle, last, and summary rows of the target range, check for error values, and verify `formula`; for AI formulas, at this step only do **one** formula text check (`+cells-get --include formula` to look at the seed cell / first cell, confirming that quotes / parentheses were not broken at the shell / CSV / JSON layer and that what landed is indeed `=AI(...)`). Do not use it to poll calculation results — for calculation status, use `+formula-verify --ai-only`
2. **Run diagnostics segment by segment**: Call `+formula-verify --exit-on-error` on the formula ranges added / modified this time; `partial` split into smaller chunks and continue scanning, and only complete after all segments are `status='success'`. AI formulas do not follow this rule: instead use `+formula-verify --ai-only` to deliver according to the full-range one-time asynchronous status check rule (fix `failed` / `unsupported` first; if only pending remains, it can be delivered with an explanation that background calculation is still in progress; see `references/lark-sheets-formula-verify.md` for details)
3. **When you see an error value starting with `#`**, fix the formula immediately: `#NAME?` is most likely a misspelled function name or use of a function not supported by Feishu (e.g., `GOOGLETRANSLATE` / the CUBE series; note that `UNIQUE` / `FILTER` are supported by Feishu); `#VALUE!` is most likely a type mismatch or misplaced parentheses; `#REF!` is a reference error; `~CIRCULAR~REF~` is a circular reference (the formula references itself or forms a closed loop)
4. **Verify the template before extending with `--copy-to-range`**: If the template cell formula itself calculates incorrectly, copying it with `--copy-to-range` to 100 rows means 100 errors
5. **Deduplication / filtering functions**: Feishu **supports** `UNIQUE` / `FILTER` (native array functions; see `references/lark-sheets-formula-translation.md` for details), and they can be used directly; `DISTINCT` is not a Feishu function — for deduplication use `UNIQUE`. For large-data deduplication / grouping, you can also use a pivot table (`+pivot-{create|update|delete}`, with the value field aggregation method set to count)
6. **Circular reference pre-check**: Before writing aggregate formulas (SUM / AVERAGE / COUNT, etc.), it is recommended to make clear that **the reference range does not include the target cell itself or its transitive dependencies**. Typical counterexample: writing `=SUMIF(B:B,LEFT(B3,9)&"*",C:C)` in C3, where column B matches the first 9 characters of B3 and C3 itself also matches, causing C3 to self-reference → `~CIRCULAR~REF~`. Fix: use a helper column / explicitly exclude itself (`SUMIFS(C:C, B:B, ..., A:A, "<>"&A3)`) / narrow the range to avoid itself
7. **Coverage verification for text extraction formulas**: Before extracting data from text with `LEFT` / `MID` / `FIND` / `SUBSTITUTE` / `TEXTSPLIT`, etc., it is recommended to use a local script to run a hit-rate statistic over the **entire column of source data** (`df[col].str.contains(pattern).mean()`); when the hit rate is < 100%, prioritize adding branches (IFS / multiple chained IFERRORs) as a fallback, or switch to using a local script to calculate and write static values. **Avoid** delivering after covering only the first N sample rows (typical counterexample: extracting values from dimension text with a prefix like "length 123", which directly misses matches for other formats such as "width×height", "×", "*", etc.)
8. **Formula ranges must align literally with user instructions**: When the user says "sum columns F through L", prioritize writing `SUM(F2:L2)` or `F2+G2+H2+I2+J2+K2+L2`, and **do not omit columns, add columns, or use the wrong columns**. After writing, use `+cells-get` to get back the `formula` string and compare it word by word with the user's original wording (the column names participating in the sum are consistent / the start and end column numbers are consistent / the operators are consistent); any inconsistency is a risk
9. **Pre-check dimensions / unit conversion / quantity multiplication terms (formulas do not error but results are off by a whole multiple)**: Before extracting numbers from text for calculation, first verify **whether units are unified, whether quantity multiplication was omitted, and whether the basis is consistent** — such errors let formulas run through with no `#` error, and readback cannot reveal them either (the values "look right"). It is recommended to use a local script to **manually calculate the expected values offline** for 3–5 representative rows, and compare the magnitude cell by cell against the formula results: ① If units are inconsistent, unify them before calculating (typical counterexample: dimensions `320CM*337CM` are taken directly, multiplied, and divided by 1e6 to get 0.11, but the correct result after CM→MM conversion is 10.78, **a 100-fold difference**); ② For quantities based on "single item × quantity", it is recommended to multiply by the quantity column (typical counterexample: side panel area omits multiplication by the quantity in column F, so rows with F=2 calculate only half); ③ Align the basis of standard values (typical counterexample: nutrient composition mg/kg and g/100g bases are mixed, magnifying the entire column by 100 times). **If any one of basis / unit / quantity is wrong, the entire column's calculation result is wrong; such errors do not make formulas error and are not easy to spot on readback, so it is recommended to rely on offline manual calculation for comparison.**

**The diagnostic entry point after formula writing is `+formula-verify`**: The sampled readback of `+csv-get` / `+cells-get` can only quickly discover obvious errors; it does not cover errors in the middle of a whole column, hidden rows, or errors obscured by conditional formatting, nor can it see `partial` truncation. As long as this operation actually wrote formulas via `+cells-set` / `--copy-to-range` / `+csv-put`, run `+formula-verify --exit-on-error` segment by segment over the target range according to the process above. AI formulas instead use the full-range one-time asynchronous status check of `--ai-only`, and do not converge according to `status='success'`.

⚠️ **After receiving `formula_errors` feedback, it is not recommended to only patch it**: If `formula_errors: [{cell, formula, error_type, detail}]` appears in the return value of `+cells-set`, it means some cell formulas failed to compile (`error_type=compile_failed` is usually a function syntax error, such as directly writing `[1]` index access on an array result — Feishu does not support this syntax; to get the Nth item, use `INDEX(<数组表达式>, N)`; `non_formula` starts with `=` but fails to parse). At this point, **avoid focusing only on fixing the local syntax at the reported error point** (e.g., only replacing `[1]` with `INDEX(..,1)`). It is recommended to:

1. **Re-examine the completeness of the entire formula**: For the row marked by formula_errors, besides the index syntax error, the formula may also have other inherent defects (incomplete character cleaning, missing conditions in the IFERROR fallback, wrong referenced column). After fixing the syntax error, immediately review the whole formula
2. **Symmetrically fix all similar columns at the same time**: If the same task involves similar processing for multiple columns (e.g., "calculate column H area" using column D dimensions, "calculate column I area" using column E dimensions), **after fixing one column, it is recommended to synchronize the same cleaning/fallback logic to all similar columns**, avoiding asymmetric handling such as column H using `SUBSTITUTE(长)+SUBSTITUTE(高)+SUBSTITUTE(×)` while column I only uses `SUBSTITUTE(×)` — this would cause one column to compile and have values, while the other compiles but all IFERRORs return empty, so what the user sees is "empty data" rather than "formula error"
3. **After fixing, read back to verify**: Do not only check that `formula_errors` is empty (this only proves compilation passed, not that there are runtime values). It is recommended to use `+csv-get` to read the first 3-5 rows of the target column and confirm that **target columns corresponding to non-empty source data have non-empty calculation results**
4. **Core mindset**: `formula_errors` is a tool that "helps expose compilation errors", not a pass that means "once you fix it, you're done". Compilation passed + runtime IFERROR fallback empty = from the user's perspective, "it didn't calculate"

⚠️ **Avoid using `{}` to skip borders/styles for newly added rows**: In the `cells` array, the semantics of `{}` is "**make no modification to this cell and preserve its original state**". This is safe when writing to **existing rows** (the original borders/styles remain unchanged), but it is disastrous when writing to **new rows** (such as appending a summary row at the end of the table or extending rows): the new row's underlying state originally has no borders, and `{}` not modifying it = preserving the no-border state, causing that cell to visually break.

⚠️ **Identifying a "summary row" → read `references/lark-sheets-visual-standards.md` to get the complete style specification**: Only when the following dual conditions are **both satisfied** is it a summary row; avoid judging solely because "there is an AVERAGE":
- **Semantic signal** (choose one of two): the user prompt contains intent words such as "total/summary/grand total/statistics/average score for each subject/add a row at the bottom to calculate.../bottom total"; or the context clearly indicates "append a row at the end of the table for aggregation"
- **Structural signal**: the entire new row is doing aggregation (including `=SUM/AVERAGE/COUNT/MAX/MIN/SUBTOTAL(...)`, supporting IFERROR wrapping), and is **not** a single cell calculating a reference value or a derived column calculated for every row

When the above is satisfied, **do not guess the style in this document**; go directly to read the "Scenario 1 → 1A. Add summary row / header row" section of `references/lark-sheets-visual-standards.md`, and configure `font.bold / horizontal_alignment / background_color / border_styles` completely according to the style points there.

Counterexamples (**not** summary rows; avoid automatically bolding):
- The user says "help me calculate an AVERAGE reference in H5" → single-cell calculation
- A derived column where every row has `=AVERAGE(本行区间)` → belongs to data columns
- The user explicitly says "do not bold / keep styles consistent with data rows" → follow the user's intent

**Correct approaches** (choose one of two):

- **Approach A (recommended)**: First write value / formula according to the correct type, then use `+cells-set-style` or `+styles-put` to fill in `cell_styles` + `border_styles` for the entire row; do not use `--copy-to-range` to purely brush styles. For the summary row's bold / background color / top border, see "Scenario 1 → 1A. Add summary row / header row" in `references/lark-sheets-visual-standards.md`.
- **Approach B**: Write in one pass, but every cell (including blank cells) explicitly carries `cell_styles` + `border_styles`, and **`{}` cannot be used**.

**Determining whether it is a "new row"**: If the write range exceeds the right / bottom boundary of `current_region` returned by `+csv-get` (e.g., `current_region=A1:H10`, writing `A11:H11`), it is a new row, and it is recommended to add borders according to the approaches above.

<a id="富文本单元格超链接--人--文档rich_text"></a>
## Rich text cells: hyperlinks / @mentions / @documents (`rich_text`)

Rich content such as hyperlinks with display text, @mentions, and @documents **is recommended** to go through the `rich_text` field of `+cells-set` (`cells[].rich_text` array, one object per segment, with `type`), and **cannot** be passed directly as an ordinary string — a plain string will only be stored in the cell as plain text. For the complete fields, run `lark-cli sheets +cells-set --print-schema --flag-name cells`. Common segment types:

- **Hyperlink (with display text)**: `{"type":"link","text":"飞书","link":"https://www.feishu.cn"}`. A plain URL does not need `rich_text`; just write an ordinary string directly.
- **@mention**: `{"type":"mention","mention_token":"<userId>","notify":false}`. **Only same-tenant users are supported, with a maximum of 50 people per write.** `notify` **defaults to `true`** (it will send a notification to the mentioned person); if you do not want to send one, be sure to explicitly pass `false`.
- **@document**: Also `"type":"mention"`; pass the document token in `mention_token` (e.g., `shtXXX`).

Optional fields such as `mention_type` (type number) are subject to the output of `--print-schema`.

> ⚠️ Once `rich_text` is set, it will **ignore** `value` in the same cell; it, `formula`, and `multiple_values` can only choose one as the content field (they can be combined with `cell_styles` / `note`, etc.).

<a id="dropdown-选项--配色dropdown-set--dropdown-update"></a>
## Dropdown options + colors (`+dropdown-set` / `+dropdown-update`)

<a id="选项怎么来--options-与---source-range-二选一"></a>
### Where options come from: choose one of `--options` and `--source-range`

| flag | Option source | Applicable scenario |
|---|---|---|
| `--options '["a","b","c"]'` | Fixed list written in the command | The option set is constant and does not need later maintenance |
| `--source-range ''\''Sheet1'\''!T1:T3'` | Values in existing cells | Options need to stay dynamically synchronized with data; you want to maintain an "enum values" column and reference it in multiple places |

The two flags **must pass one, and only one** — if both are passed or neither is passed, the CLI will immediately error. `--source-range` uses A1 with a sheet prefix (e.g., `'Sheet1'!T1:T3`; the sheet name is wrapped in single quotes according to the A1 standard). It can refer to the same sheet or another sheet (e.g., `'Refs'!A1:A10`).

<a id="多选下拉验证规则与选中值是两层数据"></a>
### Multi-select dropdown: validation rules and selected values are two layers of data

`+dropdown-set --multiple` only sets the target cell's validation rule to "allow multiple selections" and **does not write the currently selected values**. When later using `+cells-set` to fill in multi-select results, each option must be written as an item in the `multiple_values` array; do not join multiple options with commas into a single ordinary `value`, otherwise the whole string will be treated as a single value and trigger data validation failure.

```bash
# First create a dropdown rule that allows multiple selections
lark-cli sheets +dropdown-set \
  --spreadsheet-token shtXXX --sheet-id "$SID" \
  --range "E2:E15" \
  --options '["A","B","C","D"]' \
  --multiple

# Then write 3 selected values to E6
lark-cli sheets +cells-set \
  --spreadsheet-token shtXXX --sheet-id "$SID" \
  --range "E6" \
  --cells '[[{"multiple_values":[{"value":"A"},{"value":"B"},{"value":"C"}]}]]'
```

<a id="配色新建默认用内置色板更新保留已有配色"></a>
### Colors: new creation uses the built-in palette by default; updates preserve existing colors

Dropdowns **have capsule highlighting by default** — when creating, do not pass `--highlight` / `--colors`; all options are colored cyclically according to the built-in 10-color palette, aligning with the default behavior of manually configuring dropdowns in the UI. Pass `--colors` only when the user explicitly specifies custom colors, or when the options have clear semantic coloring (such as status, risk, priority, and the colors help understanding).

Dropdown capsule text is black by default. When customizing colors, use **light, low-saturation backgrounds** to avoid vivid or dark color values affecting readability.

`+dropdown-update` rewrites the entire validation rule. If the user has not asked to reset existing colors, first use `+dropdown-get` to read back, and pass the existing `highlight_colors` back as `--colors`; omitting it will rebuild according to the built-in palette.

| Desired effect | How to pass |
|---|---|
| Use the default palette when creating | Pass neither `--highlight` / `--colors` |
| Preserve existing colors when updating | First read back with `+dropdown-get`, then pass `highlight_colors` back as `--colors` |
| The user explicitly requests it, or the options have semantic coloring | Pass only light, low-saturation `--colors '["#hex",...]'` (no need to pass `--highlight`) |
| Pure white dropdown, no highlighting | Pass `--highlight=false` (note that `=false` cannot be omitted; writing only `--highlight` in cobra is equivalent to true) |

The length of `--colors` **can be shorter than** the number of options (in list mode, shorter than the length of `--options`; in listFromRange mode, shorter than the number of cells in `--source-range`); unspecified options are filled cyclically according to the built-in palette; but it **cannot be longer than** — the CLI will intercept it at the Validate stage, with an error like `--colors length (4) must not exceed dropdown source size (3)`.

When `--highlight=false` explicitly disables highlighting, `--colors` will be ignored even if passed (the semantics are self-contradictory, but no error is reported).

<a id="最小用例"></a>
### Minimal use cases

**`--options` mode — default palette (most common)**:

```bash
lark-cli sheets +dropdown-set \
  --url https://... --sheet-id <id> \
  --range A2:A100 \
  --options '["待开始","进行中","已完成","已取消"]'
```

**When the user explicitly requests semantic coloring**:

```bash
lark-cli sheets +dropdown-set \
  --url https://... --sheet-id <id> \
  --range A2:A100 \
  --options '["待开始","进行中","已完成"]' \
  --colors '["#E8F3FF","#FFF3D6","#E8F8E8"]'
```

**`--source-range` mode** (first maintain the three rows "Male/Female/Confidential" in `'Sheet1'!T1:T3`, then have `B2:B21` reference it):

```bash
lark-cli sheets +dropdown-set \
  --url https://... --sheet-id <id> \
  --range B2:B21 \
  --source-range ''\''Sheet1'\''!T1:T3'
```

**Pure white dropdown** (use only when explicitly telling the user "no colors"):

```bash
lark-cli sheets +dropdown-set \
  --url https://... --sheet-id <id> \
  --range A2:A100 \
  --options '["低","中","高"]' \
  --highlight=false
```

> ⚠️ **`--source-range` must include the sheet prefix** (even if it is the same sheet as `--range`). Note a pitfall: when reading back such a listFromRange dropdown cell, `data_validation.range` appears not to include the sheet prefix (in the form `$T$1:$T$3`). If you want to write the read-out range back to `--source-range`, **you must re-add the sheet prefix yourself**, otherwise it will be rejected.
>
> ⚠️ **The sheet prefix for batch flags like `--ranges` must be written "bare"** — the `--ranges` parser for `+cells-batch-clear` / `+dropdown-update` / `+dropdown-delete` does not accept quotes: even if the sheet name contains dots or spaces (e.g., `2025.9`, `一月份`), write `2025.9!A1` directly; writing `'2025.9'!A1` will be treated as part of the sheet name and report `sheet not found`. **But `--source-range`, pivot table `--source`, and `--range` follow the A1 standard**: a sheet name with single quotes (e.g., `'Sheet1'!A1:B2`) is the standard form, and bare writing is also accepted; readback uniformly returns the quoted form — do not apply the bare-writing requirement of `--ranges` to these flags.

`+dropdown-update` (multi-range batch update) targets `--ranges` as a JSON array (each item with a sheet prefix), applying the same options + colors to all ranges. It replaces the complete validation rule; when existing colors need to be preserved, first read back and pass through `--colors` as described above.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+cells-set` | write | Cell |
| `+cells-set-style` | write | Cell |
| `+cells-set-image` | write | Cell |
| `+dropdown-set` | write | Object |
| `+csv-put` | write | Cell |
| `+table-put` | write | Cell |

## Flags

### `+cells-set`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | xor | Write range (A1 format). Choose one of this and `--writes` (for a single range use --range+--cells; for multiple ranges use --writes) |
| `--start-cell` | string | optional | Alias of `--range` (consistent with `+csv-put`; use --start-cell to set the top-left anchor); when a range is passed, writing starts from the top-left corner of the range (hidden flag: not listed in `--help`, but can be passed normally) |
| `--cells` | string + File + Stdin (composite JSON) | xor | JSON: 2D array `[[{cell},...],...]`; a bare `--range A1` (or `--start-cell`) is the top-left anchor, and the write range is inferred from the number of rows and columns in this array; if `--range` is written as a rectangle (`A1:B2`), that is the boundary — if this array is smaller than it, it narrows; if larger, it is rejected. Each cell may contain `value` / `formula` / `multiple_values` / `cell_styles` / `note` / `rich_text` (including `type="embed-image"` embedded cell images), etc. When writing selected values to a multi-select-enabled dropdown cell, you must use `multiple_values:[{"value":...}]`; do not join multiple options with commas into a single `value`; for the complete fields, run `--print-schema` |
| `--writes` | string + File + Stdin (composite JSON) | xor | Multi-range write JSON array (up to 100 items), each item `{sheet_name\|sheet_id, range, cells}` — **for cross-sheet items, put the sheet location inside the item** (same convention as +batch-update sub-operations and +styles-put items); if not written inside the item, take the top-level `--sheet-name` / `--sheet-id`; the cells structure is the same as `--cells` (2D array, can carry cell_styles/border_styles per cell). The whole batch expands into a **single batch submission** (fail-fast; after failure, read back first and then resend), and supports cross-sheet; typical scenarios: batch-fixing formulas scattered in multiple places, cross-table isomorphic writes — do not assemble +batch-update --operations for this. Choose one of this and `--range`+`--cells`; range-level uniform styles are not done here — after writing, follow with +styles-put |
| `--allow-overwrite` | bool | optional | Allow overwriting non-empty cells (default true); when set to false, error on encountering a non-empty cell |
| `--max-cells` | int | optional | Explosion protection, default 50000 (hidden flag: not listed in `--help`, but can be passed normally) |
| `--copy-to-range` | string | optional | Copy range (A1 notation): copy the content written by --cells in --range (values/formulas/styles, depending on the fields actually passed) to this area, with formula references automatically shifted (e.g., C2=B2 → C3=B3). Suitable for first writing one row/block as a template and then extending to fill the entire column/area (e.g., --range A1:G1 to write the template, --copy-to-range A1:G100 to fill 100 rows). Supports whole rows 3:6, whole columns C:E, to column end D3:D, to row end D3:3; supports multiple target ranges separated by English commas, such as C1:D2,E5:F6 |

### `+cells-set-style`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | Target range (A1 format, e.g. `A1:B2`) |
| `--background-color` | string | optional | Background color (hex, e.g. `#ffffff`) |
| `--font-color` | string | optional | Font color (hex, e.g. `#000000`) |
| `--font-family` | string | optional | Font name (e.g. `Arial`, `微软雅黑`) |
| `--font-size` | float64 | optional | Font size (px, e.g. 10, 12, 14) |
| `--font-style` | string | optional | Font style (allowed values: `normal` / `italic`) |
| `--font-weight` | string | optional | Font weight (allowed values: `normal` / `bold`) |
| `--font-line` | string | optional | Font line style (allowed values: `none` / `underline` / `line-through`) |
| `--horizontal-alignment` | string | optional | Horizontal alignment (allowed values: `left` / `center` / `right`) |
| `--vertical-alignment` | string | optional | Vertical alignment (allowed values: `top` / `middle` / `bottom`) |
| `--word-wrap` | string | optional | Wrap strategy (allowed values: `overflow` / `auto-wrap` / `word-clip`) |
| `--number-format` | string | optional | Number format (e.g. text `@`, number `0.00`, currency `$#,##0.00`, date `mm/dd/yyyy`) |
| `--border-styles` | string + File + Stdin (composite JSON) | optional | Border configuration JSON: `{ top: {style,weight,color}, bottom: ..., left: ..., right: ... }`; the 4 directions share the same structure. style = line type (solid\|dashed\|dotted\|double\|none); weight = thickness (thin\|medium\|thick —— a string, not a pixel number); color = hex such as #000000. `{ all: {...} }` sets all four sides at once. Borders have only this one flag: there is no --border-all / --border-top / --border-color |

### `+cells-set-image`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | Target cell (A1 format, must be a single cell, e.g. `A1`; start and end cell must be the same) |
| `--image` | string | required | Local image path (supports PNG / JPEG / JPG / GIF / BMP / JFIF / EXIF / TIFF / BPG / HEIC) |
| `--name` | string | optional | Image file name (including extension); when omitted, the basename of `--image` is used |

### `+dropdown-set`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | Target range (A1 format, e.g. `A2:A100`) |
| `--options` | string + File + Stdin (composite JSON) | xor | Dropdown option JSON array, e.g. `["opt1","opt2"]`. The server does not limit the number of options, nor the length of a single option; options containing commas are acceptable (they are automatically escaped on write). For a large number of options, it is recommended to use `--source-range` instead. |
| `--colors` | string + File + Stdin (simple JSON) | optional | Dropdown chip background color, an RGB hex array. When creating, do not pass this by default: omitting it uses the built-in 10-color palette; pass it only when the user explicitly requests it or the options have clear semantic coloring. Chip text is black by default, so choose light, low-saturation backgrounds. The length may be shorter but not longer —— overly long values are blocked by Validate (`--colors length (N) must not exceed dropdown source size (M)`); unspecified items are filled by cycling through the built-in palette. Passing it alone takes effect; it is ignored when `--highlight=false`. |
| `--multiple` | bool | optional | Enable multi-select; default `false`. This flag only sets the validation rule and does not write selected values; when subsequently writing values with `+cells-set`, you must pass a `multiple_values` array, not a comma-joined `value` |
| `--highlight` | bool | optional | Dropdown chip background color highlight switch. **Not passing = on** (colors cycle through the built-in 10-color palette); `--highlight=false` turns it off to get a pure white dropdown. Override the coloring with `--colors`. |
| `--source-range` | string | xor | The dropdown source range for listFromRange mode, A1 notation + sheet prefix (e.g. `'Sheet1'!T1:T3`). Maps to server `data_validation.range`, and takes effect automatically together with server `data_validation.type='listFromRange'`. Choose one of this and `--options`: passing `--options` uses an inline list (type=list), passing this flag uses a range reference (type=listFromRange). The `--colors` length rule is unchanged (≤ the number of cells in the source range), and `--highlight` / `--multiple` behave the same. When `--highlight` is enabled and the source covers more than 2000 cells, the server will judge that dropdown as option-error (this is an unsupported combination); the CLI will give a warning in the returned result's `data.warnings`. To cancel, pass `--highlight=false`. |

### `+csv-put`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--start-cell` | string | required | Target area start A1 (e.g. `A1`, `B5`, without a sheet prefix; use `--sheet-id` / `--sheet-name` to specify the sheet); must be a single cell, range notation is not accepted; the end point is automatically inferred from the actual number of rows and columns in the CSV |
| `--csv` | string + File + Stdin (non-JSON text) | required | RFC 4180 CSV text; can write values or formulas (cells starting with = are computed as formulas); no styles / comments / images, use +cells-set for those. |
| `--allow-overwrite` | bool | optional | Allow overwrite (default true); when set to false, an error is reported if the target is non-empty |
| `--range` | string | optional | Alias for --start-cell (consistent with +csv-get / +cells-set, locate with --range); when a range is passed (e.g. A1:H17), its top-left cell is automatically taken (hidden flag: not listed in `--help`, but can be passed normally) |

### `+table-put`

_Common: URL/token (no sheet positioning) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--sheets` | string + File + Stdin (composite JSON) | required | Typed table protocol (pandas-DataFrame-shaped) JSON: top-level `{"sheets":[...]}`, each array item is a subtable `{name, start_cell?, mode?, header?, allow_overwrite?, columns:["colA","colB",...], data:[[...]], dtypes?:{colA:pandasDtype, ...}, formats?:{colA:numberFormat, ...}}` —— neither `name` nor the outer `sheets` array may be omitted. Agents can use `scripts/lark_sheets_df.py`'s `df_to_sheet(df, name)` to convert a DataFrame into one item in a single line (for multiple subtables, concatenate them in a list and wrap with `{"sheets":[...]}`). The `dtypes` value is a pandas dtype string (`int64`, `float64`, `Int64`, `bool`, `boolean`, `datetime64[ns]`, `object`, ...), which the CLI maps to internal string/number/date/bool —— when `dtypes` is omitted, that column is written as text (suitable for raw CSV-shaped data). `formats[col]` is an Excel number_format string (e.g. `#,##0.00`, `0.0%`, `yyyy-mm`); when omitted, date columns use `yyyy-mm-dd` and string columns use the text format `@`. |
| `--styles` | string + File + Stdin (composite JSON) | optional | Visual processing operation JSON applied after type-faithful writing: top-level `{styles:[...]}`, each item corresponds to a written subtable, contains `name`, and provides at least one of `cell_styles` / `row_sizes` / `col_sizes` / `cell_merges`. `cell_styles` uses an A1 cell range + flat style fields (fields are the same as +cells-set-style, including number_format / colors / alignment / border_styles); row/col sizes use row/column ranges + type/size; merges use cell ranges + optional merge_type. The length/order/name of the styles array must correspond to the written subtables (one-to-one with --sheets.sheets). For the complete cell_styles field structure, run `+table-put --print-schema --flag-name styles`. |

## Schemas

> Composite JSON flag field quick reference (only top level + one level of nesting). For deeper structures, see `## Examples` below, or use `--print-schema` to read the complete JSON Schema (usage see index.md "Common flag quick reference" and "Agent usage tips").

### `+cells-set` `--cells`

_[Dimension] The number of rows and columns must exactly match the range: 'A1:C2'→[[_,_,_],[_,_,_]] (2 rows × 3 columns), 'B5:B7'→[[_],[_],[_]] (3 rows × 1 column), 'A1'→[[_]] (1×1)_

**2D array item** (type object):
- `value` (oneOf?) — static cell value (text, number, boolean)
- `formula` (string?) — cell formula starting with '=' (for example: '=SUM(A1:A10)')
- `note` (string?) — cell comment/note
- `cell_styles` (object?) — cell style properties, including font, color, alignment, and number format { font_color?: string, font_family?: string, font_size?: number, font_weight?: enum, font_style?: enum, … 11 items in total }
- `border_styles` (object?) — cell border configuration, containing the four directions top/bottom/left/right, each direction having the same structure (see top) { top?: object, bottom?: object, left?: object, right?: object }
- `rich_text` (array<object>?) — rich text content each: { type: enum, text: string, style?: object, link?: string, mention_token?: string, … 17 items in total }
- `multiple_values` (array<object>?) — multi-value content, used for list validation cells that support multi-select each: { value: oneOf, format?: string }
- `data_validation` (object?) — data validation configuration { type: enum, items?: array<string>, range?: string, operator?: enum, values?: array<oneOf>, … 9 items in total }

### `+cells-set` `--writes`

_Array of multi-region write items (up to 100 items), the whole batch is submitted in a single batch (fail-fast, after a failure read back first then resend); supports cross-sheet_

**Array item** (type object):
- `sheet_id` (string?) — target subtable reference_id; choose one of this and sheet_name, must be written in each item (top-level sheet positioning is not recognized)
- `sheet_name` (string?) — target subtable name; choose one of this and sheet_id, must be written in each item
- `range` (string) — A1 rectangular range, the row and column dimensions must strictly match cells (same as --range)
- `cells` (array) — 2D cell array, structure same as --cells (value / formula / cell_styles / border_styles etc., see set_cell_…

### `+cells-set-style` `--border-styles`

_Cell border configuration, containing the four directions top/bottom/left/right, each direction having the same structure (see top)_

**Top-level fields**:
- `top` (object?) { style?: enum, weight?: enum, color?: string }
- `bottom` (object?) { style?: enum, weight?: enum, color?: string }
- `left` (object?) { style?: enum, weight?: enum, color?: string }
- `right` (object?) { style?: enum, weight?: enum, color?: string }

### `+dropdown-set` `--options`

_List options_

**Array item** (type string):
- scalar: string

### `+table-put` `--sheets`

_Typed data for one or more subtables, each array element writes to one subtable; supports multiple DataFrames → multiple subtables written at once_

**Array item** (type object):
- `name` (string) — target subtable name
- `start_cell` (string?) — write start cell (A1 notation, e.g. "B2"), default "A1"
- `mode` (enum?) — overwrite (default): write the "header + data" block starting from start_cell; append: append the data below the existing data in the subtable (by default does not repeat the header) [overwrite / append]
- `header` (boolean?) — whether to write a row of column-name headers
- `allow_overwrite` (boolean?) — when false, if the write would land on non-empty cells, refuse to write to protect the original data (returns partial_success)
- `columns` (array<string>) — array of column-name strings, in an order that corresponds one-to-one with the values of each row in `data`
- `data` (array<array<string|number|boolean|null>>) — data rows; each row is an array whose length must equal the number of `columns`
- `dtypes` (object?) — optional
- `formats` (object?) — optional

### `+table-put` `--styles`


**Array item** (type object):
- `cell_merges` (array<object>?) — array of cell merge operations; range uses an A1 cell range, merge_type defaults to all each: { merge_type?: enum, range: string }
- `cell_styles` (array<object>?) — array of cell style operations; each item specifies a range with an A1 cell range, field names align with +cells-set-style each: { background_color?: string, border?: object, border_styles?: object, font_color?: string, font_family?: string, … 14 items in total }
- `col_sizes` (array<object>?) — array of column width operations; range uses a column range such as A:C, giving size (px) means pixel column width (type may be omitted); when type is standard, no size is given each: { range: string, size?: number, type?: enum }
- `freeze` (object?) — freeze rows and columns: rows = freeze the first N rows, cols = freeze the first N columns (0 or omitted = do not freeze that dimension) { cols?: integer, rows?: integer }
- `name` (string) — subtable name
- `row_sizes` (array<object>?) — array of row height operations; range uses a row range such as 1:3, giving size (px) means pixel row height (type may be omitted); when type is standard/auto, no size is given each: { range: string, size?: number, type?: enum }

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` arranged at the top (XOR).

<a id="cells-set-的拆分与转介绍"></a>
### Splitting and cross-referral of `+cells-set`

The "Tool selection" section already explained pure values (`+csv-put`) vs rich writes (`+cells-set`). The table below supplements the CLI-side `+cells-set` **sibling split**, as well as **cross-reference referrals** that do not belong to this reference —— to avoid agents using `+cells-set` to force through all write scenarios.

| Write scenario | Use this | Do not use |
|---------|--------|--------|
| Only change the **style of an existing cell**, without touching value/formula | `+cells-set-style` | `+cells-set` (triggers unnecessary value writes) |
| **Embed a single image** into a cell | `+cells-set-image` | `+cells-set` (more cumbersome parameters) |
| Multi-step combinations like **insert row/column + write**, delivered in one go | `+batch-update` (see lark-sheets-batch-update) | Multiple independent `+cells-set` (insertion disturbs the ranges of subsequent calls) |
| Apply the same set of styles to **multiple non-contiguous ranges** | `+styles-put` (multiple cell_styles items means multiple regions, see lark-sheets-styles-put) | Multiple `+cells-set-style` (multiple round trips) |

### `+cells-set`

Example:

```bash
# Pure values (array form); by default overwrites non-empty cells, no need to explicitly pass --allow-overwrite
lark-cli sheets +cells-set --url "https://example.feishu.cn/sheets/shtXXX" \
  --sheet-name "Sheet1" --range "A1:B2" \
  --cells '[[{"value":"name"},{"value":"score"}],[{"value":"alice"},{"value":95}]]'

# Rich cell (formula + styles, cells is a 2D matrix with one cell schema per element)
lark-cli sheets +cells-set --spreadsheet-token shtXXX --sheet-id "$SID" \
  --range "C2:C10" --cells @rich-cells.json
```

`--cells` For rich formatting, see the `## Schemas` section (the cells element contains value / formula / cell_styles / border_styles / data_validation / multiple_values / note / rich_text); values / formulas / styles / comments / embedded images can be submitted together in a single write.

> For cells you want to skip in the middle, use an empty object `{}` as a placeholder (the underlying semantics are "keep the original value unchanged"). Example: `--range A1:A5 --cells '[[{"value":1}],[{}],[{}],[{}],[{"value":5}]]'` writes only A1 and A5.
>
> Scattered writes across multiple non-contiguous regions (such as `D2` + `F7` + `J15`) exceed the scope of a single `--range` + `--cells`, but are **still within `+cells-set`**: use this command's plural form `--writes` to deliver them all in one batch (each item is `{sheet_name, range, cells}`, and can span sheets; see "Writing to multiple non-contiguous regions" above). **Do not piece together `+batch-update`'s `--operations` for this**—that is for cross-type operation chains with sequential dependencies.

### `+cells-set-style`

Only change styles, without touching value / formula. The 10 cell_styles fields are flattened into independent flags, and borders use `--border-styles` JSON.

```bash
# Bold + yellow background
lark-cli sheets +cells-set-style --url "..." --sheet-name "Sheet1" \
  --range "A1:B2" --font-weight bold --background-color "#FFFF00"

# Matching borders
lark-cli sheets +cells-set-style --url "..." --sheet-id "$SID" \
  --range "A1:D10" --font-size 12 --horizontal-alignment center \
  --border-styles '{"top":{"style":"solid","color":"#000","weight":"thin"},"bottom":{"style":"solid","color":"#000","weight":"thin"}}'
```

### `+cells-set-image`

Embed a single image into a cell (must be a single-cell range):

```bash
lark-cli sheets +cells-set-image --url "..." --sheet-name "Sheet1" \
  --range "A1" --image ./logo.png
```

### `+csv-put`

Example:

```bash
# Inline CSV
lark-cli sheets +csv-put --url "https://example.feishu.cn/sheets/shtXXX" \
  --sheet-name "Sheet1" --start-cell "A1" \
  --csv $'name,score\nalice,95\nbob,87'

# From a file
lark-cli sheets +csv-put --spreadsheet-token shtXXX --sheet-id "$SID" \
  --start-cell "A1" --csv @data.csv
```

> `+csv-put` is much shorter than `+cells-set`—prefer it when bulk-loading values or formulas. Switch to `+cells-set` only when you need styles/comments/images.
>
> ✅ Cells starting with `=` are treated as formulas for calculation (not literal text):
>
> ```bash
> lark-cli sheets +csv-put --url "..." --sheet-name "Sheet1" \
>   --start-cell "A1" \
>   --csv $'name,score\nalice,=SUM(B2:B10)'
> # ↑ B2 writes the formula =SUM(B2:B10); when read back, formula is preserved and value is the calculation result.
> # Conversely: you cannot use +csv-put to write "literal text starting with =", because it will be treated as a formula; for styles/comments/images, still use +cells-set.
> ```
>
> ⚠️ **For formulas containing commas / quotes, RFC 4180 escaping is recommended**: CSV uses commas to separate fields, and commas inside formulas (such as the argument-separating comma in `COUNTIF(D5:D22,"及格")`) will be treated by the parser as field separators, splitting one cell into multiple cells and flattening and misaligning the entire two-dimensional structure. Rule: **wrap the entire field containing commas in double quotes, and double any quotes inside the field**:
>
> ```bash
> # Write a 2-column, 3-row statistics block starting at G4; =COUNTIF contains a comma + internal quotes, so escaping is recommended
> lark-cli sheets +csv-put --url "..." --sheet-name "Sheet1" \
>   --start-cell "G4" \
>   --csv $'统计项,结果\n成绩总和,=SUM(C5:C22)\n及格人数,"=COUNTIF(D5:D22,""及格"")"'
> # ↑ "=COUNTIF(D5:D22,""Pass"")": the outer double quotes wrap the entire cell, and the quotes around the inner "Pass" are doubled to ""Pass"".
> # Writing =COUNTIF(D5:D22,"Pass") bare will be split by CSV at the comma into two cells, and the write region will shift from G4:H6 to G4:K4.
> ```
>
> 💡 **For formulas containing commas / quotes / line breaks, prefer writing with `+cells-set` (JSON two-dimensional array)**—`cells[r][c].formula` places the formula string directly, with no CSV escaping burden. `+table-put`'s typed payload can carry `name/start_cell/mode/header/allow_overwrite/columns/data/dtypes/formats`, but has no formula field; for formula writes, use `+cells-set` or escaped `+csv-put`:
>
> ```bash
> # The same statistics block, written structurally with no escaping needed
> lark-cli sheets +cells-set --url "..." --sheet-name "Sheet1" --range "G4:H6" \
>   --cells '[[{"value":"统计项"},{"value":"结果"}],[{"value":"成绩总和"},{"formula":"=SUM(C5:C22)"}],[{"value":"及格人数"},{"formula":"=COUNTIF(D5:D22,\"及格\")"}]]'
> ```

> **Positioning + write boundaries (critical, to avoid accidental overwrites)**:
> - Use `--start-cell` for positioning (the anchor = top-left cell); the `--range` alias is also accepted (consistent with `+csv-get` / `+cells-set`; passing a range automatically takes the top-left corner).
> - ⚠️ `--start-cell` / `--range` **only set the top-left corner and do not limit the write size**: CSV auto-expands from the anchor according to its own row and column count. Giving a "small range" will **not** truncate the data—the excess is still written, and overwrites by default. `+cells-set` only has this semantics for bare `--range A1`; once `--range` is written as a rectangle, it is a boundary, and `--cells` exceeding it will be rejected.
> - Both dry-run and successful responses echo `writes_range` (the actual landing region, such as `B2:D4`): **before writing, first `--dry-run` to check the landing region**, and confirm it will not overwrite adjacent data.
> - To protect non-empty cells: `--allow-overwrite=false` (an error is raised if a non-empty cell appears in the landing region).

<a id="table-putdataframe--飞书类型保真写入"></a>
### `+table-put` (DataFrame → Feishu, type-preserving write)

Write structured data (DataFrame, list of dict, Counter) with type preservation into an **existing** sheet (write semantics are the same as `+cells-set`). The protocol shape is **aligned with pandas `to_json(orient="split")`**: `columns:[列名]` + `data:[[行...]]`, with optional `dtypes:{列名:pandas_dtype}` to determine each column's type (number preserves precision, date lands as a real date), and optional `formats:{列名:number_format}` to override display formats (thousands separator / percentage / custom date). When dtypes are missing, the entire table is written as string (with `@` text format, preserving ids with leading zeros such as postal codes / order numbers).

Only writes to an **existing** sheet (`--url` / `--spreadsheet-token`, one of the two is required), and does not create a new workbook—**to create a new sheet, use `+workbook-create --sheets` directly** (same protocol, one-step sheet creation + type-preserving write; see the workbook reference for details). For read-back, use the mirror command `+table-get` (see the read-data reference); the output is isomorphic to `--sheets` and can round-trip.

```bash
# Sheets are matched by name, and created if missing; multiple DataFrames are written to multiple sheets at once via stdin
uv run python export.py | lark-cli sheets +table-put --url "<表URL>" --sheets -
# A sheet with "mode":"append" appends to the end of existing data, and by default does not repeat the header
lark-cli sheets +table-put --spreadsheet-token "<token>" --sheets @payload.json
# When both --sheets and --styles are large JSON: stdin can only provide one flag per invocation, so one goes through -, and the other goes through an @cwd relative path
lark-cli sheets +table-put --url "<表URL>" --sheets - --styles @styles.json < sheets.json
```

Each sheet can also carry `"allow_overwrite": false` (refuse to write when encountering non-empty cells, protecting the original data) and `"header": false` (write only data, not the header). For the complete fields, run `+table-put --print-schema --flag-name sheets`.

<a id="dataframe--协议用-df_to_sheet-helper"></a>
#### DataFrame → protocol (using the `df_to_sheet` helper)

pandas' `df.to_json(orient="split", date_format="iso")` completes all cleaning in one step (NaN→null, Timestamp→ISO string, numpy scalar→native number); just attach the dtypes. This module packages this 5-line helper into an importable [`scripts/lark_sheets_df.py`](../scripts/lark_sheets_df.py) (including `df_to_sheet` and `sheet_to_df`, paired for write / read-back):

```python
import sys; sys.path.insert(0, "scripts")  # When cwd is not at the skill root, change it to the actual path under scripts/
from lark_sheets_df import df_to_sheet

# Single sheet (explicit format overrides the default display)
payload = {"sheets": [df_to_sheet(df, "销售", {"营收": "#,##0.00", "毛利率": "0.0%"})]}

# Multiple sheets—the helper lets each sheet be one line, with no repeated boilerplate
payload = {"sheets": [df_to_sheet(df1, "销售"),
                      df_to_sheet(df2, "成本"),
                      df_to_sheet(df3, "利润")]}
```

> For **CSV-shaped all-text data** (no type preservation needed, and ids with leading zeros must also be preserved), just omit dtypes and write it inline in one line; there is no need to go through the helper (note that `date_format="iso"` must be preserved, otherwise datetime columns will be serialized into epoch millisecond numbers and rejected by the CLI):
> ```python
> payload = {"sheets": [{"name": "原始",
>                        **json.loads(df.to_json(orient="split", date_format="iso"))}]}
> ```
> **Do not replace `to_json + json.loads` with `df.to_dict(orient="split")`**: it will leave `numpy.int64` and cause `json.dumps` to later report "not serializable"—this step is the key to cleaning.
> **Column names must be strings**: integer column names (such as pandas' default 0/1/2 when no header is specified) will enter `columns` as JSON numbers and be rejected by the CLI; for inline writing, first `df.columns = df.columns.map(str)`. `df_to_sheet` already performs this step automatically.

You do not have to use pandas—the typed protocol is pure JSON. For handwritten scenarios:

```python
# Counter / dict / manually assembled data: write columns + data directly, and add dtypes/formats as needed
payload = {"sheets": [{
    "name": "渠道",
    "columns": ["channel", "count", "rate"],
    "data": [["app", 1240, 0.62], ["web", 760, 0.38]],
    "dtypes": {"count": "int64", "rate": "float64"},
    "formats": {"rate": "0.0%"},
}]}
```

> **dtype quick reference**: `int64`/`float64` (numeric), `Int64` (integer with null values, nullable), `bool`/`boolean`, `datetime64[ns]` (date, default `yyyy-mm-dd`), `object` (string). pandas dtype strings can be put directly into dtypes as-is; the CLI side matches by prefix (`int*`/`uint*`/`Int*`/`float*` → number, etc.). Unrecognized dtypes fall back to string.

<a id="--styles写入时同时套样式"></a>
#### `--styles` (apply styles at the same time as writing)

`--styles` applies visual treatment along with the typed write, saving one `+cells-set-style` round trip. The protocol is **fully isomorphic** to `+workbook-create --styles` (see the workbook reference for details): top-level `{styles:[...]}`, each item in the array corresponds to a written subtable and contains `name`, and is split by capability into four optional arrays—`cell_styles` (A1 cell range + flat style fields, including `number_format` / color / alignment / `border_styles`, applied together with the content in the same write), `cell_merges`, `row_sizes`, `col_sizes`. The styles array's length / order / name must correspond to the written subtables (one-to-one with `--sheets.sheets`).

```bash
lark-cli sheets +table-put --url "<表URL>" \
  --sheets '{"sheets":[{"name":"明细","columns":["日期","金额"],"dtypes":{"日期":"datetime64[ns]","金额":"float64"},"formats":{"金额":"#,##0.00"},"data":[["2024-01-15",1234.5]]}]}' \
  --styles '{"styles":[{"name":"明细",
    "cell_styles":[{"range":"A1:B1","font_weight":"bold","background_color":"#f5f5f5","horizontal_alignment":"center"}],
    "cell_merges":[{"range":"A1:B1"}],
    "col_sizes":[{"range":"A:B","type":"pixel","size":120}]}]}'
```

For the complete fields, run `+table-put --print-schema --flag-name styles`.

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute constraints

- `Validate`: XOR common four-piece set; `+cells-set`'s `--cells` must be parseable as a JSON two-dimensional matrix with equal width per row (the landing region is inferred from its row and column count); `+cells-set-style`'s style flags must have at least one non-empty (or carry `--border-styles`); `+cells-set-image`'s `--range` must be a single cell (start and end cells identical); `+csv-put`'s `--csv` must be parseable according to RFC 4180; if `+table-put` provides `--styles`, validate alignment with `--sheets.sheets` by subtable name / order / count; validate explosion-prevention parameter upper limits.
- `DryRun`: outputs the target range + inferred size + whether it will overwrite non-empty cells warning, with zero network side effects.
- `Execute`: after writing, must read back the first, middle, last, and user-named items according to the written range; for formulas, also read formula, and verify according to the formula completion flow.
