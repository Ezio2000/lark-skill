# Lark Sheet Read Data

<a id="列格式多样性预探写公式--排序--筛选前必做"></a>
## Column Format Diversity Pre-Probe (mandatory before writing formulas / sorting / filtering)

> This section gives the correct process for "probing column format diversity before writing formulas / sorting / filtering"; it is the implementation at the read_data tool layer of criterion 3 (read fully before writing) in the main index.md "Lark Sheet Editing Guidelines".

For columns involved in subsequent **calculation / sorting / filtering / formula extraction**, you **must** first sample **at least 50 rows** (or the full table if small), identify all value type variants in that column, and only then design formulas / conditions. Looking at only the first 10 rows is not enough, because the following differences usually lurk at the end or middle of the table:

- **A date column containing multiple formats at once**: `YYYYMM`, `YYYY-MM-DD`, `YYYY/M/D`, with timestamps, text "unknown"
- **A numeric column mixed with formula text / units / comments**: `1000+200=1200`, `100元`, `/（合同未明确）`, `#N/A`
- **Empty values mixed with 0 / "0"**
- **Case / full-width vs half-width differences** ("Office Expense" vs "Office Expense ", "Sales" vs "sales")

After pre-probing, you must handle all variants in formulas / filter conditions using `IFERROR` / `IFS` / a helper column that extracts numeric values; you cannot ship directly just because the head(10) sample passes. Logic designed to cover only the formats appearing in the sample will inevitably fail on rows outside the sample.

⚠️ **When deduplicating / comparing large numbers (ID numbers / reference numbers / serial numbers of 15+ digits), using the displayed value from `+csv-get` is forbidden**: `+csv-get` returns the **formatted display value**, and numbers of 15+ digits are displayed as scientific notation such as `1.04E+14` — multiple numbers that are actually different all become the same `1.04E+14` at the display layer, and using them for duplicate detection will **misjudge the entire column as duplicates**. When comparing / deduplicating / matching large numbers, you must instead use `+cells-get` (to get the original exact value) or read that column as text; using the scientific-notation display value from csv-get is forbidden (counterexample: after a large batch of long reference numbers was displayed in scientific notation, mutually different numbers all became the same value, were treated as an entire column of duplicates, and were incorrectly highlighted).

<a id="使用场景"></a>
## Use Cases

Read. Read cell data from a Lark Sheet. This reference covers 4 shortcuts; choose by reading purpose:

| Reading purpose | Use this shortcut | Data destination | Notes |
|---------|----------------|---------|------|
| Quickly view pure value data, batch processing | `+csv-get` | Conversation context | Returns CSV text (each line prefixed with `[row=N]`); for large tables, read in batches by `--range` row window (when truncated, check `has_more`) |
| Structured read by column type (feed a DataFrame / round-trip back to `+table-put`) | `+table-get` | Conversation context | Returns the typed protocol (`columns:[列名]` + `data` + `dtypes`/`formats` + `range`), with output shape aligned to pandas split; you can restore a DataFrame with one line of `pd.DataFrame(sheet["data"], columns=sheet["columns"]).astype(sheet["dtypes"])`, or round-trip directly back to `+table-put`. Without `--range`, it reads the **full used range** (crossing empty rows / empty columns in the middle of the table), and each subtable returns its read range `range`; when trimmed by `max_chars`, **that subtable** carries `truncated: true` and `truncation_warning`, and when the budget is exhausted so that subsequent whole tables are unread, the **top level** also carries the same set of fields; for `--output-path` file-output mode, also check `complete` / `truncated` in the stdout receipt — **check the truncation fields before using the data; the absence of a report at all three layers does not mean the logical read was complete**, and you must still cross-check against the actual number of rows in the returned data, the key last row, and the source data (see below). Note this is not contradictory to the `current_region` "truncates on empty rows in the middle of the table" below: `+table-get` reads the subtable's physical used range (the used rectangle recorded by Lark, including empty rows in between), while `current_region` expands contiguously from the anchor and stops at a fully empty row |
| View formulas, styles, comments, data validation | `+cells-get` | Conversation context | Returns complete cell information; token cost is relatively high |
| View the dropdown (data validation) configuration of a region | `+dropdown-get` | Conversation context | Returns the dropdown options, multi-select switch, and chip colors for that A1 range |

**Selection principles**:
- Only viewing values or doing data processing → `+csv-get`; for large tables, read in batches to avoid pulling the whole table at once and blowing up the context
- Structured read by column type (feed a DataFrame / round-trip back to `+table-put`) → `+table-get`
- Need formulas/styles/comments → `+cells-get`
- View the options, multi-select switch, or chip colors of a region's dropdown → `+dropdown-get`

<a id="读表理解脚本agent-优先入口"></a>
## Sheet Reading Comprehension Scripts (Agent preferred entry point)

When the goal is to "first understand the sheet content / structure / subtable boundaries" and `scripts/lark_*.py` exists locally (distributed only with the repository version of the skill; the binary-embedded version does not include `scripts/`), you may prefer this set of read-only scripts, then decide whether to call the above shortcuts directly. The scripts are an optional shortcut, not a mandatory entry point — when the scripts are unavailable, execute directly via the CLI equivalent path in the right column of the table below: if the task is very small, or requires information the scripts do not cover such as formulas / styles / comments / exact original values, you can use the CLI directly for an equivalent or more fine-grained read.

| Script | Underlying shortcut | Applicable scenario |
| --- | --- | --- |
| `scripts/lark_inspect_workbook.py` | `+workbook-info` / `+sheet-info` / `+csv-get` | First-step pre-check for a Lark Sheet: outputs all sheet summaries, layouts, previews, and `data.selection`; when no sheet is named, select only from the visible_grid candidates of `resource_type=sheet && is_hidden=false`, and auto-use only when there is a unique one; with multiple candidates, do not guess by index. |
| `scripts/lark_detect_subtables.py` | `+workbook-info` / `+sheet-info --include merges,hidden_rows,hidden_cols` / small-window `+csv-get` | When the same sheet may have multiple table regions, summary blocks, or note blocks, identify candidate subtable ranges within a **known and untruncated window** |
| `scripts/lark_profile_table.py` | `+csv-get` / `+sheet-info --include hidden_rows,hidden_cols` (by default includes hidden rows and columns; manually add `+cells-get` / `+table-get` if necessary) | Profile headers, data ranges, column types, and special rows for a **confirmed and untruncated candidate range**, and output `summary` / `field_map` / `risk_warnings` / `write_hints` |

`lark_profile_table.py` is a **heuristic profile**, not a final judge: it can reduce the risk of manually counting rows and columns and missing special rows, but headers, multi-row titles, the last data row, column types, special rows, and appended columns may all need secondary confirmation. Before operations such as batch writes, formulas, sorting, filtering, deduplication, pivot/charts, you cannot write directly based only on profile results; you must verify the profile output together with the task semantics, sample values, and necessary supplementary CLI reads.

Usage criteria for `lark_profile_table.py`:

| Task type | Recommendation |
| --- | --- |
| Only reading or modifying a single cell / very small range explicitly specified by the user, and no need to understand the whole table | Use the CLI directly |
| Batch writes, formulas / calculations, sorting, filtering, deletion, keep-only, deduplication, lookup / matching, conditional highlighting, pivot tables, charts, summaries | Prefer running `lark_profile_table.py` on the target region; if the header, data range, field columns, column types, and special rows have already been explicitly confirmed with the equivalent CLI, you may skip the script. For deduplication / lookup, if the target column contains `long_numeric_like_id`, leading zeros, or formatted numbers, the profile can only locate the column; comparison values must instead use `+cells-get` or `+table-get` |
| Multiple table blocks, uncertain headers, presence of merges / summaries / empty rows / note blocks, selection is a single cell but the task semantics concern the whole table | First use `lark_detect_subtables.py` or supplementary CLI to confirm the candidate range, then run `lark_profile_table.py` on the target range |
| Need formulas, styles, comments, data validation, exact original values, precise comparison of long numeric IDs | First use the scripts to form a structured understanding, then supplement as needed with `+cells-get` / `+table-get` / batched `+csv-get` |

Recommended chain (for large tables, define the window first; the scripts do not accept truncated results):

```bash
uv run python scripts/lark_inspect_workbook.py --url "<表格URL>"
# First use +workbook-info and a small-window +csv-get to confirm the real sheet, column boundaries, and starting region; for large tables, advance by row window.
uv run python scripts/lark_detect_subtables.py --url "<表格URL>" --sheet-name "<子表名>" --range "A1:H200"
uv run python scripts/lark_profile_table.py --url "<表格URL>" --sheet-name "<子表名>" --range "A1:H200"
```

When the `+csv-get` of `lark_detect_subtables.py` / `lark_profile_table.py` hits `has_more`, it exits with an error and reports the `actual_range` already read, and never gives a candidate range or profile based on half-truncated data. When encountering this error, take `actual_range` as the completed window, reduce the number of columns, or continue reading after its last row; candidate ranges, summary rows, and write landing points that span windows must be re-verified with the CLI, and a single window's result must not be treated as a conclusion about the whole table.

The scripts are read-only and do not perform any writes. Their output is used to reduce tokens and locate errors; when formulas, styles, comments, or exact original values are subsequently needed, still call `+cells-get` / `+table-get` / `+csv-get` directly according to the rules in this file. If `lark_profile_table.py` was used before writing, read and use at least these fields: `summary.header_row`, `summary.data_range`, `summary.data_row_segments`, `field_map`, `risk_warnings`, `visibility`, `write_hints.safe_append_col`, and `special_rows`. Only when `risk_warnings` does not contain `data_range_has_gaps` may you treat `data_range` as a contiguous write range; when there are gaps, read and write in segments according to `data_row_segments`.

Key script flags:

| Flag | Script / default | When to adjust |
| --- | --- | --- |
| `--skip-hidden` | profile / detect, off (by default includes hidden rows and columns) | Turn on when analyzing only visible data; in that case you must use the profile's `data_row_segments`, and do not use the contiguous `data_range` directly for writing. |
| `--max-chars` | inspect `8000`; profile / detect `25000` | When the output is too large, narrow the range or lower the value; if profile / detect is truncated it errors out and gives `actual_range`, so continue by window. |
| `--header-scan-rows` | profile `20` | Increase when there are multiple title rows, notes, or empty rows before the header; when too large, supplement with `possible_multi_row_header` to confirm, and do not write based only on the scoring result. |
| `--max-sheets` | inspect `3` | When no sheet is specified, only the first N sheets carry layout / preview; the rest still return summaries and are explained in warnings. |
| `--max-merge-components` | detect `2000` | Exceeding the limit skips gap merging and warns; you need to narrow the window or manually re-verify subtable boundaries. |
| `--gap-rows` / `--gap-cols` | detect `1` / `0` | Adjust when subtables are fragmented or stuck together; re-verify candidate ranges after each adjustment. |

detect confirms at most 10 cross-window merge anchors; exceeding the limit explains the number skipped in `warnings`. When encountering this warning, narrow the scan window and then re-verify the affected subtable boundaries.

Rules for `lark_profile_table.py` output triggering supplementary reads:

- When `risk_warnings` is non-empty, do not treat the profile as final fact; supplement or adjust according to the table below, and conservatively re-verify warnings not in the table as well.

| Warning | Required action |
| --- | --- |
| `mixed_value_types` / `long_numeric_like_id` / `formula_or_value_errors` | Supplement with `+cells-get` or `+table-get` to confirm original values, types, and formulas. |
| `duplicate_headers` / `unnamed_columns` / `header_not_detected` / `header_row_not_first` / `many_empty_cells` | Supplement with `+csv-get` to read near the header and empty-value samples, and confirm the true header and field columns. |
| `data_range_not_detected` / `special_rows_present` / `empty_rows_present` | Supplement with `+csv-get` to read the tail and special-row samples, and confirm the last valid data row. |
| `possible_multi_row_header` | Supplement by reading 1-2 rows above and below the header; if necessary use `+sheet-info --include merges` to verify cross-column merges. |
| `hidden_rows_in_range` / `hidden_columns_in_range` | Before writing, use `+sheet-info --include hidden_rows,hidden_cols` to confirm whether it is overwrite or skip hidden content. |
| `data_range_has_gaps` | Do not write according to contiguous `data_range`; use `summary.data_row_segments` to read and write each actual read row segment separately. |
| `data_range_has_col_gaps` | The returned columns are not contiguous (`--skip-hidden` skipped hidden columns); do not write `data_range` back as a contiguous column region, handle it by column segments according to `summary.data_col_segments`, otherwise values to the right of the gap will be shifted as a whole. |

- `write_hints.safe_append_col` is only a candidate appended column and does not mean it is absolutely safe. Before adding a column or overwriting a region, you must use `+csv-get` / `+cells-get` / `+sheet-info` to verify that the column is empty, has no hidden columns/formulas/styles/object dependencies, and matches the landing point required by the user. This field has already automatically skipped hidden columns (the skipped column names are listed in `write_hints.skipped_hidden_cols`) — note that under `--skip-hidden` hidden columns do not appear in the returned grid at all, and if they happen to all be attached to the right edge of the data, `data_range_has_col_gaps` will not warn either, so this layer of skipping is the only protection; do not bypass it and derive the landing point yourself as "last column + 1".

⚠️ **When parsing CLI output, read only stdout**: data goes to stdout, diagnostics and warnings go to stderr; when parsing JSON, do not merge with `2>&1` (warnings mixed in will cause parsing to fail); use a pipe or redirect stdout separately. If a command fails, read stderr first before adjusting, and do not resend it as-is.

⚠️ **For large data, prefer writing to disk; do not pour it into the context**: both `+csv-get` / `+cells-get` are constrained by the caller's Bash / terminal single-command stdout output limit (common default is about 30000 characters; exceeding it will be truncated or spilled to a file). For pure value analysis, prefer using `+csv-get` in `--range` row windows (`A1:Z500` / `A501:Z1000` …) to redirect to a file in batches + process with local scripts + write back in batches with `+csv-put`; if you really want the results to go directly into the context without triggering spill, for any command lower `--max-chars` (default 500000) to slightly below that limit (e.g. `25000`), and the CLI switches to graceful truncation + `has_more` pagination.

> **Writing to disk does not equal reading completely**: `--output-path` merely relaxes the limit from the stdout criterion to a bounded 20 million characters (the read path is not streaming; this limit is memory protection), not unlimited. The stdout receipt carries the `complete` field — when `complete:false`, there is additionally `truncated` and a hint, and the file contains only half the data; multi-subtable reads also provide `unread_sheets` listing the subtables not read before the budget was exhausted. **When you get the receipt, check `complete` first; do not assume the whole table has been fully written to disk.**

**Core design of the `+csv-get` return value**:
- `annotated_csv` — **the sole entry point for CSV data**. Each logical row is prefixed with `[row=N] ` (N = the real sheet row number). For any downstream operation that needs row numbers (merging, writing, clearing, formatting, inserting/deleting, conditional formatting, filtering, chart/pivot table ranges, search and replace, etc.), **always read row numbers directly from `[row=N]`**. If you need pure CSV (e.g. to feed a local script for parsing), just remove the prefix: `line.replace(/^\[row=\d+\] /, '')`.
- `col_indices` — **the sole entry point for locating column letters**. Find the target field in the header as the j-th (0-based), and use `col_indices[j]` to get the column letter. **Do not count commas by hand** — when there are more than 10 columns, off-by-one is very easy (for example, misjudging W as X).
- `row_indices` — a backup array for programmatic reference. For LLM reasoning, use the prefix of `annotated_csv`; do not look up the index in this array (using row numbers as numeric values makes mental calculation error-prone).
- `current_region` — expands from the requested range to the contiguous data region surrounded by empty rows and empty columns (equivalent to Excel Ctrl+Shift+*), suitable for first reading a few rows to probe the header. ⚠️ It **truncates on a fully empty row / fully empty column in the middle of the table**, and may be smaller than the real data range (missing rows after the empty row); it **cannot** be used directly as the last row of the whole table. To judge whether the whole table has been read completely, cross-check using the physical `row_count` / `column_count` of `+workbook-info` as the upper bound (see "Blind-reading empty rows by row_count" and "Correct process for determining the data range" below).

Note:

- `+csv-get` and `+cells-get` support pagination/truncation; be sure to check the `has_more` / `truncated` flags; both must first read `warning_message` before processing the returned data (the upstream schema requires reading it before using other fields; it contains positioning and truncation-continuation hints), and `+cells-get` must also use each range's `actual_range` / `row_indices` / `col_indices` to determine the true position
- Hidden rows and columns are included in the returned result by default (`--skip-hidden=false`); if you only want to see visible data, set `true`. The read primitives themselves do not mark which rows/columns are hidden: to identify hidden intervals (to decide whether to filter, or how to interpret mixed-in hidden data), use `+sheet-info --include hidden_rows,hidden_cols` to get the set of hidden rows and columns, then combine with the `row_indices` / `col_indices` returned by `+csv-get` / `+cells-get` to determine whether each row / column is hidden
- To determine whether cell content is cut off from full display by row height or column width (layout checks, before adjusting row height or column width), add `--include truncation` to `+cells-get`: it estimates based on font size / automatic wrapping / row height and column width and returns the `isRowTruncated` / `isColTruncated` of truncated cells (not returned means not truncated). It has extra computation overhead, so only enable it when needed

**Common configuration errors (must pay attention)**:
- **Full read causing context overflow**: Do not directly use `+csv-get` or `+cells-get` to read all data into context for large tables (hundreds of rows or more). For large tables, you must read in batches: use `--range` to slice row windows and read block by block (the single-return amount of `+csv-get` / `+cells-get` is automatically capped by `--max-chars`, and `has_more` is returned on truncation); if too large, consider exporting to a local file, processing with a script, then writing back in batches
- **Understanding the structure ≠ reading all data**: Probing a table does not require reading the whole table, but you must probe headers in both directions at the same time:
  - **Horizontal (column headers)**: First read the first few rows, and **the column range must cover all columns** — use `+workbook-info` to get the total column count, and fill the last column of `range` through to the final column (for example, if the total column count is N, then `range: "A1:[列N]10"`). Shortening the column range will miss fields on the right and cause incorrect column positioning in subsequent writes.
  - **Vertical (row labels)**: If the left 1-2 columns are row labels (dates/categories/numbers enumerating the meaning of each row, typical cross-tab/pivot layout), **you must also read `A:A` or `A:B` all the way to the bottom of the row-label columns** to get all row labels. Reading only the first few rows will fail to see the rows at the end of the table, causing batch writes to miss changes — this is the main cause of "only the first N rows were changed, the rest were not updated." For flat lists (each row is an independent record, columns are fields), you can skip this step, but you still need to cross-check the last row using the physical `row_count` of `+workbook-info` according to the "Correct process for determining the data range" below (`current_region` truncates when it encounters empty rows and cannot serve as a sole fallback).
  - When the data volume is large or will hit the context limit, read in batches + process locally + write back in batches; do not pull the whole table into context in one go.
- **`+cells-get` abuse**: When you only need data values, use `+csv-get` (token cost is about 1/5 of `+cells-get`). Only use `+cells-get` when you actually need formulas, styles, or comments
- **Ignoring pagination flags**: When the read returns `has_more=true`, it means there is more data. If the task requires complete data, you must continue paginated reads; you cannot process only the first page and start writing
- **Directly deriving the true position from the 2D array indices returned by `+cells-get`**: The `i/j` in `ranges[n].cells[i][j]` is only the returned array index, not equal to the real table row/column. To locate the real row number you must use `ranges[n].row_indices[i]`, and to locate the real column letter you must use `ranges[n].col_indices[j]`; if `--skip-hidden=true`, the requested range is out of bounds and clipped, or the last row is partially returned, incorrectly counting indices yourself will immediately misalign
- **CSV row number counting errors**: The CSV returned by `+csv-get` follows the RFC 4180 standard; newline characters inside fields wrapped by double quotes `"..."` are **part of the field content** (i.e., line breaks within a cell) and do not represent a new row. When calculating row numbers, you must count by **logical record**, not by physical newline character `\n`
- **Manually counting columns to determine column numbers**: It is forbidden to determine the column letter of a target column by manually counting commas/fields in the CSV header. When the number of columns exceeds 10, manual counting is highly prone to off-by-one errors (for example, mistaking column W for column X). **You must use `col_indices`**: first find the target field name in the CSV header as the j-th field (0-based), then use `col_indices[j]` to get the actual column letter of that column
- **Deriving row numbers from values in data columns (often masked by coincidence)**: Columns in CSV that look like row numbers, such as "sequence / ID / number / No.", have **no binding relationship whatsoever** between their values and the actual table row numbers — sequence numbers may skip (1,2,3,5,6...), may start from something other than 1, may repeat, or may be reset midway. This rule applies to **all downstream operations that need row numbers**: merged cells, range writes/clears/formatting, inserting/deleting rows, conditional formatting ranges, filter ranges, chart data sources, pivot table ranges, search-and-replace ranges, and so on — **in any scenario where a row number is to be filled into any tool parameter, the row number must be read directly from the `[row=N]` prefix at the start of the target row in `annotated_csv`**; it is forbidden to mentally calculate things like "sequence number = row number," "the header occupies 1 row so data starts at row 2," or "the Nth sequence number is on row N+1," and it is also forbidden to mentally calculate first and "verify afterward." **Dangerous characteristic**: In the first few dozen rows, the sequence number happens to equal the table row number (typical cause: a +1 offset from the header and a -1 offset from one skipped number cancel each other out to form a coincidence); once the model treats this coincidence as a rule, it will carry it through all subsequent rows; and when another skipped number appears later, the entire block from that row onward becomes misaligned, and such misalignment is hard to detect without self-checking. **Correct workflow**: ① Locate the target logical row in `annotated_csv` (match by field content); ② directly read the `[row=N]` prefix at the start of that row to get the real table row number; ③ fill this row number into the downstream tool parameters. For range operations, use the `[row=N]` of the start row as the start row and the `[row=N]` of the end row as the end row. **Self-check**: Before acting, sample another 1~2 rows near the end of `annotated_csv` and verify whether `[row=N]` matches the "sequence number" in the first column — if they do not match (typical: `[row=57] 58,...`), it means there are skipped/hidden rows, and you should be even stricter about taking values from `[row=N]`; do not be misled by the sequence number column
- **Neither `row_count` nor `current_region` can determine the last row on its own**: The `row_count` of `+workbook-info` is the sheet's **physical grid row count** (often a default value such as 200 / 1000), usually **greater than** the real last data row — directly using it to pull `--range` to `S200` will read back a large number of empty rows and waste context. Conversely, the `current_region` returned by `+csv-get` is a contiguous block expanded from an anchor and surrounded by empty rows and columns, and **it truncates when it encounters a fully empty row in the middle of the table**, so it may be **smaller than** the real data range (missing rows after the empty row; typical counterexample: rows 1–80 have data, row 81 is empty, and data continues from row 82 onward, but `current_region` only goes to 80, so the entire section from row 82 onward is missed). Correct approach: treat `row_count` as the **upper bound** and `current_region` as a **starting-point reference**, and between them confirm the real last row according to the "Correct process for determining the data range" below (including cross-checking across empty rows in the middle); do not trust only one of them.
- **Treating current_region as a pure data range**: What `current_region` returns is the **contiguous non-empty region** expanded from the requested range outward until surrounded by empty rows and columns, equivalent to Excel's Ctrl+Shift+\*. It includes **all non-empty rows** in that region — not only data rows, but possibly also title rows, summary rows (such as "Total"), signature rows (such as "Prepared by / Approved by"), footnotes, and other non-data content. **It is strictly forbidden to directly use the last row of `current_region` as the end row of the data range**. For the correct approach, see "Correct process for determining the data range" below

<a id="确定数据范围的正确流程排序筛选批量写入等操作前必做"></a>
### Correct process for determining the data range (required before operations such as sorting, filtering, and batch writing)

When subsequent operations require a precise data range (such as sorting, filtering, deleting, or batch writing), the range detected by `current_region` alone is not enough — it **may be inaccurate at both ends**: when there is a fully empty row in the middle of the table it will be truncated (the last row is too small, missing data), and when there are summary / signature rows at the end of the table it will be too large. You must confirm both the **start row** and the **end row** of the data. Specific steps:

1. **Confirm the start row**: Read the first 5~10 rows, identify the position of the header row; data start row = header row + 1
2. **Confirm the end row** (key step, cannot be skipped):
   - **First prevent truncation (missing data)**: Take the physical `row_count` of `+workbook-info` as the upper bound and compare it with the last row of `current_region`. If the last row of `current_region` is **far smaller than** `row_count` (a large gap remains), do not directly trust it — probe further after the last row of `current_region` (for example, read down to `row_count`, or scan in segments to the first contiguous blank area) to confirm that there really is no data after the empty row; typical counterexample: `row_count=327`, `current_region` only goes to row 80, row 81 is empty, and data continues from row 82 onward, so reading only to 80 misses a large section.
   - **Then exclude trailing non-data rows**: Read several rows near the confirmed last row (recommended: the last 5~10 rows) and exclude row by row:
     - **Summary rows**: content such as "Total," "Grand Total," "Subtotal," "Total:" etc.
     - **Signature/approval rows**: content such as "Prepared by," "Reviewed by," "Department Head," etc.
     - **Empty rows or separator rows**: the entire row is empty or has only borders
     - **Remark/footnote rows**: explanatory text, notes, etc.
3. **Final data range** = start row ~ last valid data row (crossing over empty rows in the middle, excluding trailing non-data rows)

**Example**: `current_region` returns `A1:N51`; reading Row 48~51 reveals:

- Row 49: sequence number=47, name=xxx, has normal data → ✅ data row
- Row 50: "Grand Total," has merged cells → ❌ summary row
- Row 51: "General Manager: ...", "Prepared by: ..." → ❌ signature row
- **Correct data range = A3:N49** (not A3:N51)

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+cells-get` | read | Cell |
| `+dropdown-get` | read | Object |
| `+csv-get` | read | Cell |
| `+table-get` | read | Cell |

## Flags

### `+cells-get`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | A1 range, such as `A1:F10` (without sheet prefix; use `--sheet-id` / `--sheet-name` to specify the sheet) |
| `--include` | string_slice | optional | Categories of information to return, multiple separated by commas. `truncation` additionally estimates whether each cell is truncated in display based on row height/column width / font size / automatic wrapping, returning `isRowTruncated` / `isColTruncated` (extra computation overhead; only enable before layout checks / adjusting row height or column width) (possible values: `value` / `formula` / `style` / `comment` / `data_validation` / `conditional_format` / `truncation`) |
| `--max-chars` | int | optional | Single-return character limit, default 500000 (fallback protection against blowups). For a full table without truncation, directly use --output-path to write to disk (the limit is automatically relaxed to 20 million characters — the read pipeline is non-streaming, and this limit is memory protection; for anything larger, explicitly pass --max-chars); only lower it (such as 25000) when you want the result to go directly into context and not to disk, and paginate by has_more. Passing 0 means "do not set a limit yourself," equivalent to not passing it (still 500000 / 20 million when writing to disk), and will not fall back to the smaller default truncation of the underlying tool. |
| `--output-path` | string | optional | Write the complete read result to a local path (such as `./out.json`); the file content is the JSON of the data payload; stdout only returns a confirmation message containing output_path/byte count. **Once set, the character limit is automatically relaxed to a bounded 20 million characters** (overriding the --max-chars default), not unlimited — the read pipeline is non-streaming, and this limit is memory protection; an explicit --max-chars takes precedence. The stdout receipt includes the `complete` field (when the limit is hit, there is also `truncated` and a hint); use it to determine whether the file is complete, and do not assume by default that the whole table has been written. When omitted, the result is printed to stdout as usual. |
| `--skip-hidden` | bool | optional | Skip hidden rows and columns, default `false` |

### `+dropdown-get`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | A1 range, such as `A2:A100` (without sheet prefix; use `--sheet-id` / `--sheet-name` to specify the sheet) |

### `+csv-get`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | optional | A1 range, such as `A1:F30` (without sheet prefix; use `--sheet-id` / `--sheet-name` to specify the sheet). **Can be omitted: by default reads the entire sub-sheet** (clipped to the actual table boundaries; the returned actual_range marks the actual read range); for large tables, use --max-chars / --output-path to control the volume |
| `--max-chars` | int | optional | Single-return character limit, default 500000 (fallback protection against blowups). For a full table without truncation, directly use --output-path to write to disk (the limit is automatically relaxed to 20 million characters — the read pipeline is non-streaming, and this limit is memory protection; for anything larger, explicitly pass --max-chars); only lower it (such as 25000) when you want the result to go directly into context and not to disk, and paginate by has_more. Passing 0 means "do not set a limit yourself," equivalent to not passing it (still 500000 / 20 million when writing to disk), and will not fall back to the smaller default truncation of the underlying tool. |
| `--output-path` | string | optional | Write the complete read result to a local path (such as `./out.json`); the file content is the JSON of the data payload; stdout only returns a confirmation message containing output_path/byte count. **Once set, the character limit is automatically relaxed to a bounded 20 million characters** (overriding the --max-chars default), not unlimited — the read pipeline is non-streaming, and this limit is memory protection; an explicit --max-chars takes precedence. The stdout receipt includes the `complete` field (when the limit is hit, there is also `truncated` and a hint); use it to determine whether the file is complete, and do not assume by default that the whole table has been written. ⚠️ What is written to disk is the **JSON** of the data payload (`+csv-get` is the same; the CSV text is one field inside the JSON), not a directly usable .csv file; for a pure CSV file, redirect stdout to a file. When omitted, the result is printed to stdout as usual. |
| `--include-row-prefix` | bool | optional | Whether to add a `[row=N]` prefix before each row, default `true` |
| `--skip-hidden` | bool | optional | Skip hidden rows and columns, default `false` |

### `+table-get`

_Common: URL/token (no sheet positioning) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--sheet-id` | string | optional | Read only this sub-sheet (by id); if omitted, read all sub-sheets |
| `--sheet-name` | string | optional | Read only this sub-sheet (by name); if omitted, read all sub-sheets |
| `--range` | string | optional | A1 range to read; if omitted, read each sub-sheet's complete used range (it will cross fully empty rows / fully empty columns in the middle of the table and will not be truncated) |
| `--max-chars` | int | optional | Single-return character limit, default 500000 (fallback protection against blowups). Even if not passed, the underlying tool has a default truncation of about 50000, so it is explicitly sent here to relax it; to read the entire table, use --output-path to write to disk (the limit is automatically relaxed to a bounded 20 million characters, not unlimited; the receipt's complete field indicates whether it is complete). Passing 0 means "do not set a limit yourself," equivalent to not passing it (still 500000 / 20 million when writing to disk), and will not fall back to the smaller default truncation of the underlying tool. |
| `--output-path` | string | optional | Write the complete read result to a local path (such as `./out.json`); the file content is the JSON of the data payload; stdout only returns a confirmation message containing output_path/byte count. **Once set, the character limit is automatically relaxed to a bounded 20 million characters** (overriding the --max-chars default), not unlimited — the read pipeline is non-streaming, and this limit is memory protection; an explicit --max-chars takes precedence. The stdout receipt includes the `complete` field (when the limit is hit, there is also `truncated` and a hint); use it to determine whether the file is complete, and do not assume by default that the whole table has been written. When omitted, the result is printed to stdout as usual. |
| `--no-header` | bool | optional | Treat the first row as data rather than a header (column names become col1/col2 ...) |

## Examples

### `+csv-get`

Common four-piece set: `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` (the first two are XOR, the last two are XOR).

Example:

```bash
# Simple read (sheet positioning is required: one of --sheet-name or --sheet-id must be given; the Sheet1! prefix in range cannot replace it)
lark-cli sheets +csv-get --url "https://example.feishu.cn/sheets/shtXXX" --sheet-name "Sheet1" --range "A1:F30"

# Use sheet-name for fuzzy positioning (the runtime framework resolves it to sheet-id first)
lark-cli sheets +csv-get --spreadsheet-token shtXXX --sheet-name "销售明细" --range "A1:F30"

# Full read: omitting --range reads the entire sub-sheet (clipped to actual boundaries; the returned actual_range marks the actual read range),
# no need to first use +workbook-info to probe rows and columns and then assemble a range; for large tables, use --max-chars / --output-path
lark-cli sheets +csv-get --spreadsheet-token shtXXX --sheet-name "销售明细"
```

Output contract (envelope.data):

- `annotated_csv` — the main CSV entry point containing the `[row=N]` prefix
- `col_indices` / `row_indices` — column letter / row number mapping arrays
- `current_region` — the A1 range of the contiguous region expanded from the anchor until surrounded by empty rows and columns. ⚠️ **It is not the true boundary of the whole table**: it truncates when it encounters a fully empty row / fully empty column in the middle of the table and may be smaller than the real data range; summary / signature / footnote rows at the end of the table may also make it larger than the pure data range. To determine whether the whole table has been fully read, you must cross-check using the physical `row_count` of `+workbook-info` as the upper bound (see "Neither `row_count` nor `current_region` can determine the last row on its own" above)
- `actual_range` — **the A1 range actually read this time**. For continuation reads / verifying coverage, always use it as the standard: when `actual_range` is smaller than the requested range, even if `has_more=false` also indicates that only a partial window was obtained, you cannot treat `row_count` as "fully read"
- `row_count` / `col_count` — **the number of rows / columns returned this time** (= the size of `actual_range`, which changes with `--range`), **not the total physical row/column count of the whole table**; for the whole table's physical size, use `+workbook-info`
- `has_more` — whether the current `--range` is truncated due to `--max-chars` (for continuation reads after truncation, keep using `--range`); it **only reflects whether there are further pages within this range**, and `has_more=false` **does not mean the whole table or that window has been fully read** — you still need to combine it with `actual_range` to see how far the actual coverage goes

> To read out structured by column type (feed a DataFrame, or round-trip back to `+table-put`), use `+table-get` (see below); what `+csv-get` gives is a pure-value snapshot with the `[row=N]` prefix; when downstream needs row numbers/column coordinates, take them directly from the prefix and `col_indices`.

### `+cells-get`

Example:

```bash
# Read formulas + styles for A1:F10 (sheet positioning is required)
lark-cli sheets +cells-get --url "https://example.feishu.cn/sheets/shtXXX" --sheet-name "Sheet1" \
  --range "A1:F10" --include formula,style
```

> ⚠️ The caller **cannot** use indices in `cells[i][j]` to infer the real rows and columns: you must read `ranges[n].row_indices[i]` / `ranges[n].col_indices[j]`.

<a id="table-get飞书--dataframe类型保真读出"></a>
### `+table-get` (Feishu → DataFrame, type-faithful read)

`+table-put` (the write side, see the write-cells reference) is the mirror image: it reads the sheet back into a typed protocol fully isomorphic to `--sheets` (`sheets[]` + `columns:[列名]` + `data:[[行]]` + `dtypes:{列名:pandas_dtype}` + `formats?:{列名:number_format}` + `range`), which can be fed directly back into `+table-put` or used to restore a DataFrame in one line.

**By default (without `--range`), the used range is first detected based on the physical grid of the entire sub-sheet**: it can locate the real data boundaries across blank rows / blank columns in the middle of the sheet, and then read that region. It is still subject to the `--max-chars` upper limit; when `truncated=true` or `complete=false` is returned, the file/response contains only partial data, so switch to `--output-path`, raise the limit, or continue reading by sheet/range. The `range` of each sub-sheet only represents the target region for this call and cannot by itself prove that the content has been returned in full.

Column types are inferred from each column's `number_format` (date format → `date`/`datetime64[ns]`, numeric → `number`/`float64`, bool → `bool`), and serial numbers in `date` columns are converted back to ISO `yyyy-mm-dd` — dates and numbers round-trip without losing their types. **A column type is only determined when all non-empty values in that column are consistent (`number` / `date` / `bool`); if a column mixes types (e.g. a numeric column mixed with "None yet", or a date column mixed with bare numbers), it degrades to `string` (dtypes output `object`), so that every value in `dtypes` and `data` is self-consistent — it can round-trip back to `+table-put` and won't crash pandas `astype`. The degradation is lossless (dirty values are preserved as-is as text); if you want to convert scattered dirty values into a numeric column, leave that to the caller to do on the pandas side (`to_numeric(errors='coerce')`), where the original values are still present and traceable.** By default, all sub-sheets are read and the first row is used as the header (`--no-header` treats the first row as data and takes column names as `col1` / `col2` …).

```bash
# By default, read all sub-sheets → sheets[] (isomorphic to +table-put's --sheets, can be fed back or converted to a DataFrame)
lark-cli sheets +table-get --url "<表URL>"
# Optional: --sheet-name / --sheet-id restricts reading to a single sub-sheet (if not given, read all)
lark-cli sheets +table-get --url "<表URL>" --sheet-name "销售"
```

<a id="输出--dataframe用-sheet_to_df-helper"></a>
#### Output → DataFrame (using the `sheet_to_df` helper)

The output shape aligns with pandas split: `columns` is the array of column names, `data` is the two-dimensional data, `dtypes` is the `{列名: pandas_dtype_str}` mapping; `truncated/complete/truncation_warning` describes the coverage. When not truncated, it can be fed directly to `pd.DataFrame(...).astype(...)`. This module provides [`scripts/lark_sheets_df.py`](../scripts/lark_sheets_df.py):

```python
import sys; sys.path.insert(0, "scripts")  # if cwd is not at the skill root, change to the actual path of scripts/
from lark_sheets_df import sheet_to_df

# single sheet
df = sheet_to_df(out["data"]["sheets"][0])

# multiple sheets — retrieve by name
sheets = {s["name"]: sheet_to_df(s) for s in out["data"]["sheets"]}
df_sales = sheets["销售"]
```

> Display formats (thousands separators, percentages, custom dates) are in `sheet["formats"]`, which pandas does not consume; when round-tripping the modified data back, just pass them through to `+table-put`, and the display on the Feishu side stays unchanged.

<a id="round-trip读--改--写回写读对偶"></a>
#### round-trip: read → modify → write back (write-read duality)

`sheet_to_df` and `df_to_sheet` are a pair of mirror helpers ([`scripts/lark_sheets_df.py`](../scripts/lark_sheets_df.py)) that make the three round-trip stages — read / modify / write — one line each:

```python
import json, subprocess
import sys; sys.path.insert(0, "scripts")  # if cwd is not at the skill root, change to the actual path of scripts/
from lark_sheets_df import df_to_sheet, sheet_to_df

# 1. Read
out = json.loads(subprocess.check_output(
    ["lark-cli","sheets","+table-get","--url",URL,"--sheet-name","销售"]))
sheet = out["data"]["sheets"][0]
df = sheet_to_df(sheet)

# 2. Modify (pandas operations)
df["营收"] = df["营收"] * 1.1

# 3. Write back (formats are Feishu-side display formats, which pandas does not consume; pass them through to preserve the display)
payload = {"sheets": [df_to_sheet(df, sheet["name"], formats=sheet.get("formats"))]}
subprocess.run(["lark-cli","sheets","+table-put","--url",URL,"--sheets","-"],
               input=json.dumps(payload).encode(), check=True)
```

`sheet_to_df(sheet)` consumes `(columns, data, dtypes)`, and `df_to_sheet(df, name, formats=...)` regenerates the same three fields — read / write are fully dual, and only `formats` needs to be passed through manually once.

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute constraints

- The `Validate` stage only performs XOR checks, Enum validity checks, and anti-explosion parameter upper-limit validation; **network access is forbidden** (e.g. you cannot use `--sheet-name` to look up `sheet-id` in advance).
- `DryRun` outputs the request template: `--sheet-name` is generated as the `<resolve:销售明细>` placeholder in the dry-run output and is not actually resolved.
- Only the `Execute` stage performs sheet-name → sheet-id resolution and API calls.
