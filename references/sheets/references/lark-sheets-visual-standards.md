<a id="飞书表格样式与配色规范"></a>
# Lark Sheets Style and Color Standards

> **Purpose of this document**: The value standards and beautification decision flow for "correct visual output" in Lark Sheets — color schemes, headers, alignment, number formats, zebra stripes, column widths and row heights, chart presentation, and the approaches for three scenarios: adding new areas, inheriting existing areas, and beautifying existing areas.
> **Boundaries**: This document only covers "what styles look like and how to decide on them"; **how to call tools to write styles** (`cell_styles` / `border_styles` fields, merging, resize, and other parameters) is covered in `references/lark-sheets-write-cells.md` / `references/lark-sheets-range-operations.md` / `references/lark-sheets-batch-update.md`. **Conditional formatting** (highlighting / red-flagging / data bars / color scales) is covered in `references/lark-sheets-conditional-format.md`. This document does not include shortcuts; for general editing guidelines, see "Lark Sheets Editing Guidelines" in the main index.md.

<a id="最高优先级原则"></a>
## Highest-Priority Principles

- **User instructions take priority**: Format requirements explicitly stated by the user (such as "use a red background") carry the highest weight, even if they conflict with general aesthetics.
- **Inherit the original sheet's style**: Before editing, first sample the original file's visual characteristics (color scheme, borders, alignment, number formats); new content must align with them. It is strictly forbidden to forcibly apply generic standardized formatting to a file that already has its own style.
- **Extend rather than overwrite**: When adding rows/columns or appending data, the goal is to "extend the original template" — inherit the header style, stripe rhythm, border hierarchy, alignment, number formats, and column width/row height strategy of the adjacent area.
- **Beautification only touches style attributes, not data**: When beautifying an **existing area**, you may **only** modify the 5 categories of style attributes: `font` / `fill` / `border` / `alignment` / `number_format`. It is **forbidden** to change the original cells' `value` / `formula`, merged areas, row/column structure, or Sheet names. If a beautification requirement necessitates changing the data layout (for example, "add a summary row into the table"), you must split "adding the summary row" and "beautification" into two separate steps; the former is an editing action and requires separate user authorization.
- **Invisible visual attributes are also protected**: The original sheet's **merge ranges, alignment (H-Align/V-Align), row heights and column widths, and number formats** are visual attributes that users can perceive but may not explicitly mention. Even if the user did not say "preserve these," it is **forbidden** to modify them as a side effect of writing new content; when writing formulas / values / new columns, only pass `value` / `formula`, and do not reset fields such as `alignment` / `number_format` to default values (resetting is equivalent to modification). **Exception**: These attributes may only be modified when the user explicitly asks to change them (such as "adjust alignment / merge / column width"); when the user **explicitly requests beautification** ("beautify / make the table clear / suitable for printing"), this is treated as authorization for all 5 dimensions of the checklist in the next section (including column width and row height).
- **Red-flagging / highlighting defaults to background color**: When the user says "mark in red / mark it / highlight," the default is to change the **background color** (font color may be layered on top) — background color is more conspicuous both during manual review and after export; only when the user explicitly says "mark the font in red" should you change only the font color.
- **The completion standard for print / download tasks is that there is no occlusion after export**: When "suitable for printing / download / export" is involved, after adjusting row heights and column widths in Lark Sheets, export to xlsx and check once more for no truncation, no `####`, and no overflow; give long-text columns sufficient column width and set an explicit row height fallback value — do not rely solely on auto.
- **The beautification range must cover all user semantic targets**: When the user says "add borders to the table / beautify the entire table," the range = the actual data area **including all data rows** (including summary rows, total rows, and footer note rows), and must not stop at the place where "the main content appears to end." Before finalizing, first use `current_region` + the last 5–10 rows to verify the true last row (same as the "Correct process for determining the data range" in `references/lark-sheets-read-data.md`), then set the beautification range. If the range misses any target row/column mentioned by the user, it is considered incomplete and must be supplemented before delivery.

<a id="美化任务-5-维度-checklist用户点名美化美化--让表更清晰--适合打印时必做整理默认指数据整理不触发本节"></a>
## Beautification Task 5-Dimension Checklist (required when the user **explicitly requests beautification** — "beautify / make the table clearer / suitable for printing"; "organize" by default refers to data organization and does not trigger this section)

When the user **explicitly requests beautification** ("beautify / make the table clear / suitable for printing / adjust styles" — "organize" does not count; that is data organization), you **must** go through the following 5 dimensions and implement each one; delivering with only one item done (such as only adding borders) is incomplete. **When beautification is explicitly requested for an existing table, the values for the 5 dimensions should first follow the original table's color scheme / alignment (the inheritance principle takes priority); the checklist only fills in the dimensions missing from the original table**:

1. **Header format differentiation**: Header row bold + background color fill (with color contrast against data rows) + center alignment; for multi-row headers, all rows must be handled consistently
2. **Alignment**: Text columns left-aligned, numeric / currency / percentage columns right-aligned, date / category columns centered; vertical alignment uniformly centered
3. **Number format**: Each column must have consistent decimal places + thousands separator (use `number_format`); amount columns must have a consistent currency symbol; within the same column, it is **forbidden** to mix 0-decimal / 1-decimal / 2-decimal values
4. **Borders**: Coverage range follows the rule above, "The beautification range must cover all user semantic targets" (including summary / total / footer note rows), with clear inner and outer border lines
5. **Column width + row height + auto-wrap**: For detailed rules, see the "Column width auto-fit after writing" section in `references/lark-sheets-range-operations.md` (expand column width based on the longest character count / set `cell_styles.word_wrap="auto-wrap"` for long text + increase row height / set `number_format` for long numbers to prevent scientific notation)

**Differentiated annotation scenarios**: When the user requests "visual distinction for duplicate rows / outliers / important items," the annotation column / row must be set with a `cell_styles` that is **significantly different** from normal data (at least one of background color + bold + font color must be changed), and must not be completely identical to the normal data format.

**When borders / headers / alignment are explicitly requested, also implement according to the standards above** (no need to wait for the user to say "beautify"): ① When the user says "add borders to a certain rectangular area," you must **add inner and outer borders to the entire rectangle including the header row, data rows, and summary rows**, and after implementation verify the three boundaries: start / end row and last column (counter-example: the area requested to have borders actually has no borders at all); ② **Before creating a new header, first confirm which row is actually the header** — do not mistake an existing first data row for a header and paint it blue with white text, and also create the header columns that should actually be added (counter-example: the first data row was mistakenly styled as a header); ③ The font size of newly added / edited areas must match the original table; it is forbidden to mix size 13 with 14, or size 10 with 11 (counter-example: the new column's font size is inconsistent with the original table).

<a id="通用样式规范"></a>
## General Style Standards

> The following value standards all take effect under the premise of "inherit the original sheet's style / extend rather than overwrite" from the "Highest-Priority Principles": for any item involving "follow the original table," simply follow that principle; this section will not repeat it item by item.

<a id="1-表头样式"></a>
### 1. Header Style

- Headers/summary rows must have clear visual distinction from the data area.
- Use low-saturation background colors paired with font colors (such as dark blue + white text, light blue + black text), with bold text and horizontal centering.
- Use merged cells when a header spans multiple columns.

<a id="2-数据区域样式"></a>
### 2. Data Area Style

- Reduce vertical lines; prefer horizontal light gray thin lines.
- **Alignment**: Text left-aligned, numeric/currency/percentage right-aligned, dates or categories centered, all content vertically centered.
- Secondary information (notes, secondary dates, etc.) should use a smaller font size or light gray color.
- **Zebra Stripes**: When data rows > 10, alternating background colors may be used to guide the eye.
  - Before setting, first clear the original area's background color to white (#FFFFFF), then set the zebra stripe colors, to avoid mixing old and new.
  - Prefer setting cell background colors directly rather than conditional formatting (unless the user requests it).
  - Recommended colors: odd rows #FFFFFF, even rows #F3F4F6 or #EBF1F8.

<a id="3-数值格式"></a>
### 3. Number Format

- Use the `%` symbol for percentages, and appropriately note units and currency symbols (¥, $).
- Numbers greater than 1000 should use thousands separators, with consistent decimal places (1–2 digits).
- When data retrieval is involved, the data source must be noted.
- Data bars/color scales/conditional formatting may be used to enhance visualization.

<a id="4-整体结构"></a>
### 4. Overall Structure

- For long tables / wide tables whose data rows exceed one screen, freeze the header at the end (if there are title / description rows above the header, freeze those together): provide all rows and columns at once via `+dim-freeze` or `+styles-put`'s `freeze` (full state coverage; splitting into two calls keeps only the last axis), then read back with `+sheet-info` to confirm. Do not touch tables that already have freeze settings.
- **Long text handling**: Enable auto-wrap, adjust row height reasonably to ensure comfortable reading, add appropriate vertical whitespace; the goal is a clear, professional, uncrowded layout.
- Keep the table concise, group reasonably (merged cells may be used to show groupings), and add total or summary rows where appropriate.
- **Area separation**: For multiple stages or categories, use soft background color blocks for logical partitioning rather than simple borders.
- **Style rules for adding/removing rows and columns**:
  - A newly added whole column inherits the header style, column width, alignment, and number format of the same column group; a newly added whole row inherits the style of data rows or summary rows at the same level, and must not be written in header style. When appending columns, determine whether they should be added to existing merged cells (commonly seen in top title rows).
  - If the append position is adjacent to a summary row, description area, or blank separator area, first determine the true data area boundary before operating, to avoid breaking the original structure.
  - **Zebra Stripes maintenance**: After inserting or deleting rows, if the parity of subsequent rows is affected, rebuild the stripes from the affected row onward (clear first, then reset). For small additions/deletions, use local rebuilding; for large changes, use global clearing + unified rebuilding.
  - For the specific sampling and copying process, see "Scenario 2: Inheriting beautification from an existing area" below.
- **Column width / row height adjustment** (Lark `+cols-resize` / `+rows-resize` directly take pixel values: for uniform sizes use `--range` + `--width`/`--height <px>`; for multiple columns / rows with different sizes use `--widths`/`--heights` map to complete in one call, such as `--widths '{"A":100,"C:E":120}'`):
  - Hardcoding fixed column widths is forbidden; estimate pixels based on the column's actual content length.
  - Empirical estimation: approximately 15-18px per Chinese character, approximately 7-9px per English character/digit, plus 10-16px padding.
  - Recommended upper and lower limits: 80~400px; when exceeding the upper limit, enable auto-wrap (`word_wrap: auto-wrap`) + adjust row height, rather than widening indefinitely.
  - Merged cells do not participate in column width calculation, to avoid stretching a single column wide.
  - Columns copied from the original file should preferentially retain the original column width, not be recalculated and overwritten.

<a id="5-配色"></a>
### 5. Color Scheme

- Prefer following the original table's palette and light/dark hierarchy (see "Inherit the original sheet's style"); new areas should not change colors out of nowhere, ensuring visual continuity.
- Choose soft colors for background fills (such as light blue `#DDEBF7`); when distinguishing colors, prefer different shades of the same theme color, and avoid more than 3 theme colors.

<a id="6-图表展示"></a>
### 6. Chart Presentation

- Follow user instructions to choose the chart type, or match user intent (pie chart → proportions, line chart → trends).
- Include necessary elements: title, axis titles, legend for multiple series; for ordinary basic charts, first run the size advisor with value labels enabled and display them by default; when dense, successively adopt the suggested size, sparse labels, Top-N, or split charts; constant series such as target lines should not display repeated per-point labels.
- The Y-axis display range is by default left to the chart engine; do not proactively set limits based on the minimum / maximum of a single data source column; for combo charts, first compare series units and magnitudes, and put series that would be squashed onto the right axis.
- For pie charts, place the legend at the bottom by default; the size advisor keeps the pie area relatively fixed and mainly adds side whitespace based on the longest label. When there are too many categories or values are highly skewed, prefer Top-N or bar charts, and avoid solving it by widening indefinitely.
- Before creating, run `scripts/lark_chart_size_advisor.py` and use its `create_flags`; if it indicates that enlarging alone cannot solve the problem, switch to a bar chart, Top-N, or split charts. After creating, run `scripts/lark_chart_quality_check.py`.
- Prefer inheriting the original table's color scheme; keep the same color for the same metric across charts; for combo charts, use same-color-family bars and high-contrast lines, and use neutral colors for auxiliary series. When there are too many categorical colors, prefer simplifying the data rather than relying on more similar colors to distinguish them.
- **Chart placement anti-overlap**: Before adding a new chart, calculate the placement area to avoid overlapping with existing charts. Specific steps:
  1. Call `+chart-list` to get the `position` of all existing charts in the current worksheet (anchor cell: `col` is the column letter such as "A"/"B", `row` is the 1-based row number; refer to the actual fields returned by `+chart-list`), `offset` (offset within the anchor: `row_offset`, `col_offset`, in pixels), and `size` (`width`, `height`, in pixels).
  2. Get the worksheet's row height and column width information (in pixels).
  3. Based on each chart's anchor `position.row`/`position.col` + offset `offset.row_offset`/`offset.col_offset` + size `size.width`/`size.height`, combined with row heights and column widths, calculate the pixel rectangular area `(x_min, y_min, x_max, y_max)` covered by each existing chart.
  4. After selecting a size for the new chart, candidate placement positions should avoid all existing rectangular areas; if overlap exists, offset downward or rightward until a conflict-free position is found.
  5. If the worksheet no longer has enough space, preferentially place it in the blank area below, maintaining at least 1 row or 1 column of spacing between charts.

> In Lark Sheets, colors need the `#` prefix (such as `#0070C0`), which differs from openpyxl's unprefixed notation.
> For the specific tool call parameter formats, please read the corresponding tool skill (`references/lark-sheets-write-cells.md`, `references/lark-sheets-conditional-format.md`, `references/lark-sheets-range-operations.md`, etc.).

---

<a id="场景化操作指南"></a>
## Scenario-Based Operation Guide

<a id="场景一新增独立样式"></a>
### Scenario 1: Adding Independent Styles

> Applicable situation: Creating entirely new areas in a sheet with independent visual characteristics, such as summary rows, new headers, independent data tables, etc.

<a id="1a-添加汇总行--表头行"></a>
#### 1A. Adding a Summary Row / Header Row

**Decision flow:**
1. First use `+cells-get` to read the data area above the target position, confirming the data boundary and existing styles (background color, font size, etc.)
2. If a new blank row needs to be added, first use `+dim-{insert|delete|hide|unhide|freeze|group|ungroup}` to insert the row
3. Use `+cells-set` to write the summary formula + special styles (background color differentiation + bold + borders)
4. If the summary row title needs to span columns, append `+cells-{merge|unmerge}` to merge the title area

**Style points:**
- The summary row uses a darker shade of the same color family than the data area (such as data area #EBF1F8 → summary row #D6E4F0 or #4472C4 + white text)
- Must be bold, with horizontal alignment consistent with the data columns (numeric columns right-aligned, text columns left-aligned)
- Add a thicker border line above to create visual separation from the data area

<a id="1b-添加独立数据表独立区域"></a>
#### 1B. Adding an Independent Data Table / Independent Area

**Decision flow:**

1. Create a new sheet, or use `+cells-get` or `+workbook-info` to confirm the occupied range of existing tables and find a free area
2. Use `+cells-get` to sample the existing table's header style (background color, font size, font weight, alignment) and data area style
3. The new header reuses the existing header's color scheme and font parameters (maintaining style consistency), but content and column width may be independent
4. The new data area reuses the existing data area's alignment rules, border style, and number format
5. Use `+cells-set` to write the new header + data in one call

**Style points:**
- Must reuse: background color family, font size, font weight, border style
- May be independent: column width, row height, specific number format (adjusted based on the new data type)
- Leave at least 1~2 blank rows between the new and old tables as visual separation

<a id="场景二从已有区域继承美化"></a>
### Scenario 2: Inheriting Beautification from an Existing Area

> Applicable situation: Newly added rows/columns/areas have the same nature as existing content (consistent data type and hierarchy) and need to seamlessly connect with existing formatting.

<a id="2a-继续补充行列数据性质与已有内容一致"></a>
#### 2A. Continuing to Add Rows/Columns (data nature consistent with existing content)

**Core rule**: Sample the 2 adjacent rows → determine and continue the Zebra Stripes parity → write with the full style set according to the write-cells inheritance checklist.

**Zebra stripe continuation points** (this section only covers the "parity determination" standard; for the mechanism of "which style fields to write," see the pointer below):

- Read at least 2 rows (last row + second-to-last row) to determine whether there is zebra stripe alternating color
- If the last two rows have different background colors (such as #FFFFFF and #F3F4F6), new rows should continue by parity; do not fix on a single color

> For which fields to inherit specifically and how to sample and write them (`+cells-get` reads source row `cell_styles` + `border_styles`, `+sheet-info --include row_heights,merges` reads row height and merges, write with the full 6 categories of styles), see the "Style inheritance for new columns / new rows" section in `references/lark-sheets-write-cells.md` — the four sides of `border_styles` are easily missed; refer to that section as authoritative.

<a id="2b-基于模板区域的修改copy-保留所有格式"></a>
#### 2B. Modification Based on a Template Area (copy preserves all formatting)

**Core approach: Three-step layered method**

```
Step 1 — Format spreading: `+range-copy --paste-type formats`
  └── Copy the template row/area's **entire formatting** (styles, borders, number formats, data validation, etc.) to the target area
  └── This is the "format painter" — only formatting is copied; target values/formulas are preserved
  └── If formula translation and fill are also needed (such as when the formula column structure is consistent), use `+range-fill --series-type copy` instead

Step 2 — Content overwrite: `+cells-set` (only pass value/formula, no styles)
  └── Write the actual data for each row, omitting all cell_styles, because the formatting is already in place from Step 1

Step 3 — Fine-tuning and finishing: `+rows-resize --heights` / `+cols-resize --widths` (row height and column width map completed in one call), `+cells-{merge|unmerge}`, etc.
  └── Adjust row heights and column widths, handle merged cells, extend conditional formatting ranges, and other edge cases
```

**Key notes:**
- When using `+range-copy --paste-type formats` in Step 1, only spread formatting without touching values/formulas; then in Step 2 use `+cells-set` to write values (`+cells-set` overwrites by default, no extra flag needed); if Step 1 used `--paste-type all` and copied values/formulas along with it, Step 2's write will also overwrite them (default behavior)
- `+range-fill --series-type auto` (or `linear`/`date`) automatically increments numeric sequences (1→2→3) and date sequences, while `+range-fill --series-type copy` copies values as-is but formula references are automatically translated
- If the template area has merged cells, copy/fill will not copy the merge state; it must be completed in Step 3 using `+cells-{merge|unmerge}`
- If the template area has conditional formatting, the ranges need to be extended in Step 3 via `+cond-format-update`

**Scenario: Pure "format painter" (user says "apply column A's style to column B," "copy the formatting over," "only paint the format without changing data")**

A single step suffices; no three-step layering needed: call `+range-copy --paste-type formats`, with `--source-range` as the style source and `--target-range` as the target starting point. For parameter details, see `references/lark-sheets-range-operations.md`.

<a id="场景三已有区域格式美化"></a>
### Scenario 3: Format Beautification of an Existing Area

> Applicable situation: Format beautification of an area that already contains data (without changing data content), focusing on the identification and format setting of special rows such as headers and summary rows, with particular attention to safe operations on merged cells.

<a id="整体操作流程"></a>
#### Overall Operation Flow

```
1. Exploration phase
   ├── `+workbook-info` → Get the sheet list, row/column counts, freeze positions
   ├── `+sheet-info --include merges` → Get merged areas
   ├── `+cells-get` (first few rows + last few rows, `--include style`) → Sample header/data area/summary row styles
   └── Analyze results → Build an area map (header row number, data start/end row numbers, summary row number, merged area list)

2. Planning phase
   ├── Determine the header row: usually row 1 or the first 2 rows, characterized by bold/background color/merge/centering
   ├── Determine the summary row: usually the last 1~2 rows, characterized by bold/SUM/AVERAGE formulas/darker background color
   ├── Determine merged areas: identify from the `+cells-get` return (multiple cells with the same value and same style usually suggest a merge)
   └── Formulate the beautification plan: set styles separately by area

3. Execution phase (in order)
   ├── Handle merged cells first (if unmerging and re-merging is needed, you must unmerge first, then merge)
   ├── Set header styles
   ├── Set data area styles
   ├── Set summary row styles
   └── Adjust column widths and row heights
```

<a id="美化中的合并单元格要点"></a>
#### Key Points for Merged Cells During Beautification

- Before editing, first identify existing merged areas (see the exploration phase) to avoid breaking the original semantic partitions.
- When beautifying headers/group titles, if the range or style of a merged area needs to be modified, follow the order "first `unmerge` → modify → then `merge`."
- Only write styles to the top-left cell of a merged area; do not repeatedly write styles to other cells within the merge.

> For the complete safe operation rules for merged cells (including data protection, style placeholders, and 5 other rules), see the `+cells-{merge|unmerge}` section in `references/lark-sheets-range-operations.md`.
