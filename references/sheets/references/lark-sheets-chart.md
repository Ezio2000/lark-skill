# Lark Sheet Chart

<a id="真对象硬约束"></a>
## Real Object Hard Constraints

When the user asks to "draw a chart / visualize data / trend chart / comparison chart / proportion chart", you **must** create a real chart object via the chart creation command. **Do not** use a local script calling matplotlib / seaborn to generate an image and then insert it into the sheet as a substitute — static images cannot update with the source data and lose interactivity. The criterion: the final object must be returnable by `+chart-list`; for a basic single chart, you may first verify using the complete `snapshot` returned by the creation call, and for batch creation you must read back the list per affected sheet.

<a id="使用场景"></a>
## Usage Scenarios

Read and write chart objects. For basic creation and common updates, prefer the semantic shortcuts, and only use the raw snapshot for advanced configuration:

| Operation need | Tool to use | Description |
|---------|---------|------|
| View existing charts | `+chart-list` | Get the chart's type, data source, and style configuration |
| Create a basic chart by type and range | `+chart-create-basic` | Supports column/bar/line/area/pie/scatter/combo/radar/bubble/waterfall/pareto, row/column direction, and whole-chart color scheme; no need to construct a snapshot |
| Update title, axes, legend, labels, stacking, smoothing, or whole-chart color scheme | `+chart-config-update` | The CLI reads the current snapshot and writes back only the configuration patch |
| Correct the data range or direction of an existing chart | `+chart-data-update` | The CLI reads the current snapshot and writes back only the data patch, preserving other configuration |
| Batch create multiple independent charts | `+batch-chart-create` | Preserves successful charts and returns the failure reason item by item; retry only the failed items |
| Batch update multiple independent charts | `+batch-chart-update` | Reads the current snapshot per chart and generates partial properties |
| Advanced create/update, delete charts | `+chart-{create\|update\|delete}` | Use raw properties only for advanced needs such as fine-grained per-series/per-data-point settings; for updates, submit only the necessary partial properties |

<a id="统一决策顺序"></a>
## Unified Decision Order

Once the goal is clear, always choose the entry point in the following order, and do not start from the raw snapshot:

1. Ordinary single chart creation → `+chart-create-basic`;
2. Multiple independent chart creation → `+batch-chart-create`;
3. Data source / direction / series changes to an existing chart → `+chart-data-update`;
4. Title / axes / legend / labels / stacking / smoothing / whole-chart color scheme changes to an existing chart → `+chart-config-update`;
5. Only for single-series, single-data-point, or advanced fields that the above semantic shortcuts cannot express, use the raw `properties` of `+chart-create` / `+chart-update`.

Before entering the advanced entry point, first write down "which user requirement cannot be expressed by which semantic parameter". If you cannot answer, fall back to the semantic shortcut. Do not switch to the raw snapshot just because a semantic call failed once; first correct the parameters based on the explicit error.

For ordinary creation, data source correction, and common configuration updates, do not construct a raw snapshot.

Typical workflow: first confirm the headers, the exact data range, and the chart configuration, run `uv run python scripts/lark_chart_size_advisor.py` to get the suggested size, then pass the returned `data.create_flags.width` / `height` as-is to `+chart-create-basic`; when creating, include known title/axis/label content requirements in the same call whenever possible, and pass label position only when the user explicitly specifies it. After creation, use the returned complete `snapshot` to check the range, direction, and series, then verify with `+chart-list` as needed. When the data range or direction of an existing chart is wrong, use `+chart-data-update`; for common configuration corrections, use `+chart-config-update`. Only when the user requests a single series, data point, or advanced engine field should you read the existing snapshot and call `+chart-update --properties`. Do not output the entire schema first for common configuration, and do not delete and recreate a chart that was already created successfully.

**Multi-chart workflow**: First complete all auxiliary data and headers, and list each target chart's type, exact data range, title, and placement; after confirming the list, use one `+batch-chart-create` to batch create. Each of its operations directly fills in the `+chart-create-basic` flags; the CLI internally always executes by `+chart-create-basic`, so do not wrap it again with `shortcut` / `input`. When charts are independent of each other, partial success is allowed: locate the failed charts based on the returned per-item results, and retry only the failed items. The per-item results of a batch create do not return the complete snapshot; after the batch, call `+chart-list` once for each affected sheet. When already successfully created charts have data source or configuration differences, use `+batch-chart-update` to batch execute the corresponding semantic updates; do not delete and recreate.

**Chart error handling workflow (must be followed in order)**:
1. **Basic single charts take the fast path**: when the sheet, range, type, and placement are all clear, directly call `+chart-create-basic` and check the returned complete `snapshot`; do not add an extra `--dry-run` just for preview.
2. **In the following cases you must `--dry-run` before creating**: batch creation, multiple ranges or cross-subsheet data sources, containing quantifiers such as "each / respectively / one by one", uncertain placement, or a genuine need for raw advanced configuration. Check the count, sheet, range, type, and placement; the `tool_name` / `operation` / `basic_chart` / `properties` in the output are the CLI-translated internal MCP body, and **can only be read, not copied back into operations**.
3. After batch execution, check `succeeded`, `failed`, and the per-item `results[index]` at the same time; a successful command exit or a top-level `ok=true` does not mean every chart succeeded. For a single chart, check the returned `snapshot`.
4. When there are failures, preserve the successful charts and regenerate new operations containing only the failed items based on the original `index`. Do not reuse the original full batch payload, otherwise charts that already succeeded will be created again.
5. After a successful batch, call `+chart-list` only once per affected sheet, and verify the total count, titles, ranges, directions, and series; when the returned `snapshot` of a basic single chart is complete and as expected, do not list again, and only list again when the response is incomplete, there are subsequent updates, or the result is in doubt.
6. When the snapshot does not match expectations, fix it in place: for data source, direction, dimensions/series, and separated headers use `+chart-data-update`; for title, axes, legend, labels, stacking, smoothing, and color scheme use `+chart-config-update`; only for advanced fields use the minimal partial patch of `+chart-update --properties`. Do not delete and recreate.

**Failure attribution and recovery**:
- Parameter validation failure: correct only once based on the unknown flag, missing field, or operations structure indicated by stderr; do not copy the internal body displayed by `--dry-run` back into the command.
- Batch partial failure: preserve the successful items and retry only the original index corresponding to `failed`; before retrying, assert that the number of new operations equals the number of failures.
- Execution succeeded but the result does not match: take the returned snapshot / `+chart-list` as authoritative and perform semantic updates on the original chart; do not delete and recreate just because the title, range, or color scheme is wrong.
- Empty output returned or cannot be confirmed: check the exit code and stderr, and do one object read-back; if still unconfirmable, report truthfully and do not claim completion.
- The same correction fails again: stop guessing at the schema, MCP body, or complete snapshot. If a semantic shortcut can express it, return to the semantic entry point; otherwise preserve the original object and report the explicit error.

**Image chart → real chart migration (tasks like "replace screenshots / pasted images with real charts")**:
1. First use `+float-image-list` to read the ID, position, size, and count of the floating images to be replaced, and confirm the correspondence between each image and the target real chart; do not treat logos, explanatory images, or images whose correspondence cannot be confirmed as charts to be replaced.
2. When the user requests "color scheme / style consistent with the original image", you must first use the available image understanding capability to visually inspect the original image and confirm the chart type, title, series color scheme, legend, labels, stacking method, position, and size; `+float-image-list` is only used to obtain object information and cannot replace visual inspection. Do not guess at styles that cannot be confirmed.
3. Prefer using the semantic parameters of `+chart-create-basic` / `+batch-chart-create` to replicate the confirmed type, title, color scheme, legend, labels, and stacking method, and place the chart according to the original image's position and size as much as possible. For ordinary whole-chart color schemes use `--colors` / `--color-palette`; only when the original image clearly contains single-series or single-data-point styles that the semantic shortcuts cannot express should you use the raw `properties`.
4. After building the real chart, you must first use the complete `snapshot` or `+chart-list` returned by creation to confirm that the chart count, titles, data sources, series, and positions are correct, then follow the high-risk deletion process of [Lark Sheet Float Image](./lark-sheets-float-image.md) to use `+float-image-delete` to delete the original floating images that correspond one-to-one with them.
5. After deletion, call `+float-image-list` once more to confirm that the replaced images have disappeared and that other images are unaffected.

**Quantifiers must be expanded**: When the user says "each / every day / respectively / one by one / one chart each", first count the number of entities `N` from the data, write these `N` charts into the list item by item, then add other summary charts to get the target total `M`; a single multi-series chart containing all entities cannot replace these `N` independent charts. Before the batch, assert that there are exactly `M` chart creations in operations; after the batch, `+chart-list` assert that the total chart count, per-chart titles, and entity set are consistent. **Chart types and dimensions must also be asserted per chart**: the chart type the user names (line / column / stacked / pie), which column the horizontal axis takes, and which column to group by — write these into the list before starting, and verify them item by item after drawing — multiple single-dimension charts cannot replace one chart grouped by dimension, and vice versa.

**Range and series pre-validation (must be done before creation)**: In the list, simultaneously record each chart's header range, included dimensions, explicitly excluded dimensions, data direction, and expected series count. Each chart supports only one category / X-axis dimension (`dim1`), and does not support using multiple fields as a multi-level horizontal axis; currently each chart supports **at most 50 numeric series**; when organized by column it is usually "the number of selected numeric columns", and when organized by row it is usually "the number of selected numeric rows". At creation time, use `+chart-create-basic --dim1-index ... --dim2-indexes ...` to explicitly select the category and no more than 50 numeric series; if the business requires displaying more than 50 series, you should first build a compact summary table or Top-N, rather than repeatedly deleting and recreating. Before creation, confirm the indices and boundaries based on the actual headers, and do not guess the range by letters; after creation, if the range, direction, or series count does not match, use `+chart-data-update` to correct it — the CLI will read the current snapshot, rebuild `refs` / `dim1` / `dim2.series`, and submit only the data patch; do not delete and recreate.

**Size suggestion (must be done before creation)**: After confirming `--chart-type`, `--data-range`, data direction, dim1/dim2, title, legend, and label strategy, first run the size suggester. When there are separated headers, also pass `--header-range`.

The hard lower bounds are as follows; even when the suggester is unavailable, you must not go below these values:

| Chart type | Minimum width × height (px) |
|---|---:|
| Column chart, line chart, area chart, and other default types | `640 × 400` |
| Bar chart, combo chart | `720 × 420` |
| Pie chart | `720 × 440` |

```bash
uv run python scripts/lark_chart_size_advisor.py "<表格 URL 或 spreadsheet token>" \
  --worksheet-id "<reference_id>" \
  --chart-type column --data-range "'Sheet1'!A1:C10" \
  --dim1-index 1 --dim2-indexes 2,3 \
  --data-labels value --legend-position bottom --title "销售额对比"
```

When running the suggester, the parameters must be consistent with the subsequent creation: when the creation command explicitly sets `--aggregate-categories`, pass the same value; for combo charts, also pass `--series-types`; when the creation command does not pass `--data-labels`, the suggester also estimates by `none`, and when labels are needed, both sides explicitly pass the same value. Use the returned `data.create_flags.width` / `height` as-is in the creation command (including `--dry-run`), and do not reduce them based on experience; `data.minimum_size` only represents the fallback lower bound. If `data.size_alone_is_insufficient=true`, first adjust the chart structure or label strategy according to `data.layout_advice`, then recalculate the size with the new configuration. The suggester is only responsible for pre-creation estimation; after the chart is created, the quality checker must still be run.

**Axis semantics and range**: For all charts with axes, record in the list the field semantics corresponding to each axis, the category-axis / continuous-axis type, the unit, and the primary/secondary axis assignment; do not check only the axis titles. The Y-axis display range is by default left to the chart engine; when the user does not explicitly require a fixed range, do not pass `--y-axis-min` / `--y-axis-max`, and when a fixed range is needed you must pass both upper and lower bounds, focusing only on continuous numeric X axes that genuinely need tightening. The peak of a stacked chart comes from the accumulation of series within the same category, and a combo chart must also be calculated separately by left and right axes; do not directly treat the minimum / maximum of a single column in the data source as the Y-axis boundary. The display range of a waterfall chart depends on all intermediate values, subtotals, and totals after item-by-item accumulation, and you must not proactively pass `--y-axis-min` / `--y-axis-max`; the only exception is when the user explicitly specifies a fixed range, and it must cover all accumulation nodes. For other charts, only when the user explicitly requires it or visual acceptance proves the automatic range is unreadable should you calculate and set the Y-axis range based on the chart type's actual plotted values. When comparing multiple charts, first determine whether "consistent range / scale" means identical absolute boundaries or comparable span and ticks; when comparing the same metric, keep the value axis consistent, and do not force metrics with different units or magnitudes to share boundaries.

**Horizontal category row recipe**: When categories such as dates/months are arranged horizontally in one row and the target values are in another row, put the "category row + value row" together into `--data-range` and pass `--data-direction row`, for example `--data-range "'Sheet1'!A1:M1,'Sheet1'!A3:M3" --data-direction row`. In this case the category row belongs to the data mapping, and **do not** pass it to `--header-range`. `--header-range` only represents "dimension/series names" separated from pure data: the column direction must be one row, and the row direction must be one column. Passing a multi-column header in the row direction usually indicates that the category row was mistaken for a separated header.

**Prefer semantic parameters for whole-chart color schemes**: For unified theme or series color schemes use `--color-palette` / `--colors`, and for existing charts use `+chart-config-update`; prefer inheriting the original sheet theme, keep the same metric the same color across charts, and for combo charts use same-color-family columns, high-contrast lines, and neutral auxiliary lines. `--colors` will cycle and reuse, and when explicitly coloring per series, the number of colors must match the number of series. When there are too many colors to distinguish, prefer Top-N or splitting charts; only for single-series/single-data-point coloring should you use the raw snapshot.

<a id="需求图表类型映射创建前必查"></a>
## Requirement → Chart Type Mapping (must check before creation)

| User says | Chart type | Notes |
|--------|---------|------|
| "proportion", "ratio", "how much each XX accounts for" | Pie chart (pie) | First choice for single-dimension proportion |
| "comparison", "YY of each XX" | Column chart (column, vertical) | Multi-category numeric comparison; for horizontal bars use `bar` |
| "trend", "change", "movement" | Line chart (line) | First choice for time series |
| "trend and magnitude", "cumulative change", "interval scale" | Area chart (area) | Use area to emphasize trend and numeric magnitude |
| "stacked", "composition" | Stacked column chart (column + stack) | Multi-series accumulation |
| "clustered stacked column chart" | Stacked column chart (column + stack) | Native clustered stacking is currently not supported; split the cluster dimension into horizontal axis categories and use a stacked column chart to achieve a similar effect |
| "distribution", "correlation" | Scatter chart (scatter) | Relationship between two variables |
| "bubble size", "three-variable relationship", "grouped scatter" | Bubble chart (bubble) | x/y determine position, size determines bubble size, group determines grouping |
| "item-by-item increase/decrease", "change contribution", "from beginning to end of period" | Waterfall chart (waterfall) | Shows positive and negative changes and totals/subtotals; usually select one category column and one increase/decrease value column |
| "main causes", "cumulative proportion", "80/20" | Pareto chart (pareto) | Descending columns + cumulative percentage curve; only one numeric series is allowed |

**Multi-chart requirements**: When the user mentions multiple analyses at the same time (such as "count proportions + compare quantities"), you must create multiple charts, each corresponding to one type; do not make only one.

**Common configuration errors (must pay attention)**:
- **Wrong chart type selection**: When the user says "stacked column chart / percentage stacked", use `+chart-create-basic --stack normal|percent` or `+chart-config-update --stack normal|percent`; when the user says "proportion / ratio", prefer a pie chart or percentage stacked chart. Note that `column` is a vertical column chart and `bar` is a horizontal bar chart; for "comparison / each XX" type vertical columns, use `column` by default; area charts natively support `snapshot.plotArea.plot.type="area"`, so do not judge it as "unsupported" just because the quick reference table does not list it.
- **Data label toggle**: For ordinary basic charts, first run the size suggester with `--data-labels value` intended to be enabled, then create with the suggested width and height; do not preemptively pass `none` based only on the number of data points or series. If it is still too dense after using the suggested size, switch in order to sparse labels for key points / last values / outliers, Top-N, or split charts; only pass `none` when the user explicitly requires hiding all labels. For existing charts use `+chart-config-update --data-labels`, and do not construct a raw `labels` object for common label configuration. In advanced configuration, the existence of the `plotArea.plot.labels` object is itself the toggle: when creating with labels off, omit the field; when updating, delete the existing global labels by passing `labels: null`, and do not substitute by setting all fields to `false`. When multiple series have different data label display requirements, do not pass the global `--data-labels`; instead, after creation read the complete `plotArea.plot.series`, set `labels` only for the series that need labels, then write back the entire array with `+chart-update --properties`.
- **Auxiliary lines and single-point labels**: When the user requests a baseline, target line, threshold line, average line, or upper/lower limits, first add a column next to the source data repeating the target value as the auxiliary line; if a label only needs to be shown at the end of the line or at a key position, then add a column of sparse marker data, writing the same value only in the target row and keeping the remaining cells truly blank. After data preparation is complete, create a combo chart: use `line` for the auxiliary value column and `scatter` for the sparse marker column, omit the global `--data-labels`, and pass `--aggregate-categories=false` to turn off "aggregate same categories"; for existing charts use `+chart-config-update --aggregate-categories=false`. Then read the complete series array and set numeric labels only for the sparse marker series; the auxiliary line series must omit `labels`; whether to set labels for the original data series is decided according to the user's request. Do not simulate single-point labels with full-series labels on a repeated-value auxiliary line, and do not use 0 in place of blank markers, otherwise aggregation will materialize the blank markers as data points for each category, causing labels to appear repeatedly.
- **Constant series labels**: Repeated constant series such as target lines, threshold lines, and upper/lower limits do not display per-point labels by default; put the name and value in the series name, legend, title, or a single sparse marker. After creation, if the quality checker reports "constant series repeated labels", remove that series' labels or change it to a sparse marker with only one non-empty point.
- **Data label position**: Pass `--data-label-position` only when the user explicitly requires it and labels already exist; it only adjusts the position of existing labels and does not enable labels on its own. When labels need to be displayed at the same time, pass `--data-labels` as well; when the position is not specified, omit it and let the chart choose automatically by type. Label position only controls the placement method and cannot achieve showing only the last point or key points. For ordinary non-stacked column charts, generally pass `outside` for the data label position.
- **Data source range and series name source must align**:
  - By default, let `--data-range` include the real header row / column; a merged large title above the header must be skipped.
  - When data and semantic headers are separated, pass only pure data to `--data-range`, and pass the corresponding one row (column) or one column (row) header to `--header-range`. The range can be non-contiguous multiple ranges and also supports coming from multiple subsheets; do not fall back to the raw snapshot just because it crosses subsheets.
  - A horizontal category row belongs to `--data-range`, not `--header-range`; when organized by row, pass `--data-direction row`.
- **Data source must be numeric / date type**: Charts only render numeric cells. When using `+cells-set` to construct a data source, set `cell_styles.number_format` for numeric / date cells, and do not leave them as plain text, otherwise that series will render as empty.
- **Numeric / date display anomalies**: Axes inherit the source cell format. When dates display as serial numbers or large numbers display in scientific notation, fix the source data's `cell_styles.number_format`, and do not construct an undefined format field for the chart axis.
- **Wrong axis semantics**: When the user wants "proportion / ratio", use a pie chart or `--stack percent`, and verify that the data source and labels genuinely express percentages; do not deliver a chart that still uses raw counts as the vertical axis.
- **Combo chart series flattened**: Before creation, compare the units and typical values / peak magnitudes of each series; when the units differ, differ by about one order of magnitude or more, or a line is close to the X axis, do not put all series on the left axis. Use `--series-y-axes` to put the series that would be flattened (commonly percentages, ratios, or small-magnitude lines) on the right axis, and clarify their respective units with left and right axis titles; `--series-types` / `--series-y-axes` must align item by item with `--dim2-indexes`.
- **Pie chart label truncation**: For pie charts, pass `--legend-position bottom` by default, and use a wider canvas than ordinary single charts; at creation time also pass `--width` / `--height`. The width mainly leaves whitespace for the longest labels on the left and right sides, and does not increase linearly with the number of categories; when there are too many categories, switch to Top-N or a bar chart, and do not deliver by infinitely widening or truncating labels.
- **Object semantic verification**: For basic single charts, first verify the returned complete `snapshot`; for batch creation, incomplete responses, subsequent updates, or doubtful results, then call `+chart-list` once per affected sheet. This only verifies the count, data source, direction, series, and configuration, and cannot replace the layout check before delivery.

> **⚠️ Hard rule: when the user specifies the horizontal-axis/vertical-axis series by column header name (rather than column index), you must first read the first row of the sheet (the header) to determine the mapping between column names and column indexes, then set the `--dim1-index` / `--dim2-indexes` of a regular chart or the role indexes of a bubble chart.**
> For example, if the user says "the horizontal axis is the vehicle model series, and the vertical axis is the Q1-Q4 sales", you must not guess the column indexes; first use `+cells-get` to read the header of the data source range, then pass the confirmed 1-based indexes to `+chart-create-basic`.

<a id="️-chart-数据源引用-pivot-时必须排除总计行"></a>
## ⚠️ When a chart data source references a pivot, the total row must be excluded

When a chart is to be drawn based on a just-created pivot output, **it is forbidden to write `refs` based on guesswork**. A pivot enables `show_row_grand_total` / `show_col_grand_total` by default, and the last row/column of the output is usually "Total". If `refs` includes the total row as well:
- **Column chart**: an extra astronomically large bar appears at the end (= the sum of all data), flattening the other bars until they are invisible
- **Pie chart**: an extra "Total" sector takes up 33%+, and the proportions of the real categories are completely distorted

**Correct process**:
1. `+pivot-create create` returns `sheet_id` + `pivot_table_id`
2. Call `+csv-get(sheet_id, 'A1:E30')` or `+pivot-list` to read the **actual data range** of the pivot output
3. Identify and exclude the "Total"/"Subtotal" row (usually the last row; for a nested pivot, also exclude intermediate-level subtotals)
4. Use `+chart-create-basic` to create the chart, with `--data-range` precise down to the data rows (e.g., if the pivot occupies A1:D9 and the total is in row9 → the chart uses `A1:D8`)

<a id="图表位置选择创建前必做"></a>
## Chart position selection (mandatory before creation)

Picking column numbers/row numbers by feel will be rejected by the API (`position is out of sheet range`). Follow these four steps:

1. **Check dimensions**: `+workbook-info` to get the sheet's `row_count` / `column_count` (referred to below as rowCount / columnCount; `+sheet-info` returns only the layout, not the total row/column counts).
2. **Estimate the span**: by default a cell is **105 px wide × 27 px high**, `needCols = ceil(width/105)`, `needRows = ceil(height/27)`.
3. **Validate**: `position.row + needRows ≤ rowCount` and `col_idx + needCols ≤ columnCount` (`position.row` is **0-based**: the first row = `row:0`, which differs from the 1-based row numbers of A1 ranges / `+dim-insert --position`; col is converted as A=0, B=1, …, Z=25, AA=26…).
4. **If there is not enough room, expand the sheet first**; choose one of the two options, and do not force an out-of-bounds position:
   - **Preferred**: place it in the empty area below the data: `position = {row: data_end_row + 2, col: "A"}`;
   - Otherwise, first call `+dim-insert` (`references/lark-sheets-sheet-structure.md`) to expand rows/columns, then create.

⚠️ **The chart placement must not overlap an existing data rectangle** — it must fall in the blank area to the **right of or below** the data area; otherwise the chart overlay will obscure the original data and be judged a failure (counterexample: a line chart placed in the middle of the data area, obscuring the original data below).

**Example**: a 21-column sheet with a 600×400 chart → `needCols=6, needRows=15`
- ❌ `{row: 0, col: "W"}` — col=22 is out of bounds
- ✅ `{row: 42, col: "A"}` — place it below the data
- ✅ First `+dim-insert --position V --count 6` (insert 6 columns before column V, i.e., after column U), then place the chart at `{row: 0, col: "V"}`

**Title and axis text**: prefer the text explicitly specified by the user; when unspecified, generate concise natural language based only on the headers that have been read. The chart title summarizes the object, the metric, and the necessary trend/comparison relationship; the subtitle supplements only the confirmed time range or statistical scope, and is omitted when unnecessary; the X axis states the category or time dimension, and the Y axis states the metric name, with the unit appended when it is clear. It is forbidden to write cell references, formulas, internal IDs, placeholders, unresolved text, garbled characters, or empty parentheses into the title, and it is also forbidden to fabricate time, units, or business scope.

<a id="交付前验收任何图表改动后必做"></a>
## Pre-delivery acceptance (mandatory after any chart change)

After completing all chart creations or updates in this task, check the following items chart by chart; only when all pass is the task complete:

1. **Count**: the number of charts = the number explicitly requested by the user (quantity words such as "each / respectively / one by one" have been expanded item by item into independent charts, not replaced by a single multi-series chart).
2. **Text and display items**: read back the chart title, subtitle, and axis titles to confirm the semantics are accurate and there are no garbled characters, placeholders, or empty parentheses; the legend is shown or hidden as requested by the user, and data labels are shown by default for regular basic charts; when dense, handle it as "suggested size → sparse labels → Top-N / split charts". Auxiliary series must not use all-point repeated labels to simulate a single point or the last point. For charts with axes, also read back each axis's field semantics, type, unit, minimum / maximum, scale, and primary/secondary axis assignment; when comparing multiple charts, further check whether the boundaries, spans, and scope meet the user's comparability requirements.
3. **Chart quality**: after chart creation, configuration update, data update, or position adjustment, run `uv run python scripts/lark_chart_quality_check.py "<表格 URL 或 spreadsheet token>" --worksheet-id "<reference_id>"` once for each affected sub-sheet, without first using `ls` to probe the script. The checker covers geometric overlap, obscured content, out-of-bounds, minimum size, numeric source format, all-zero/empty series, and repeated labels on constant series. For dynamic numeric sources, only the first 50 points of each series are sampled, and at most 2000 source cells are read cumulatively per chart (including headers and gaps between series); `numeric_source_samples` gives the actual range and the number of sampled points, and does not continue reading the remaining data. If only the sample is all-zero/constant but does not cover the complete series, it is listed as unverifiable, and the entire series must not be modified based on that. `data.passed=true` with exit code `0` means no problems were found within the checked range, and it must not be taken to mean that unsampled data is also fine. Exit code `2` means the check succeeded in finding problems; adjust according to the returned fix suggestions and rerun; for exit code `1`, a network timeout, or no valid JSON, retry only once, and if it still fails, clearly report that the quality check was not completed; it is forbidden to substitute manual estimation.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+chart-list` | read | Object |
| `+chart-create-basic` | write | Object |
| `+chart-config-update` | write | Object |
| `+chart-data-update` | write | Object |
| `+chart-create` | write | Object |
| `+chart-update` | write | Object |
| `+chart-delete` | high-risk-write | Object |

## Flags

### `+chart-list`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--chart-id` | string | optional | Filter by a single chart reference_id |

### `+chart-create-basic`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--chart-type` | string | required | Chart type (possible values: `column` / `bar` / `line` / `area` / `pie` / `scatter` / `combo` / `radar` / `bubble` / `waterfall` / `pareto`) |
| `--data-range` | string | required | Data range; when --header-range is not passed, it must include the header; when it is passed, pass only pure data; supports comma separation and multiple ranges across sub-sheets |
| `--header-range` | string | optional | Optional separate header range; in the column direction it must be one row, and in the row direction it must be one column; the number of headers must equal the number of data dimensions |
| `--data-direction` | string | optional | Data series direction; column means the first column is the category, row means the first row is the category (possible values: `column` / `row`) (default `column`) |
| `--aggregate-categories` | bool | optional | Whether to aggregate identical categories; use --aggregate-categories=false for sparse punctuation or when row-by-row data points need to be preserved; when omitted, the chart's default behavior is used |
| `--x-axis-numbers-as` | string | optional | How to interpret numbers on the horizontal axis; text treats numbers as equally spaced text categories, values plots them as continuous numeric values with their real spacing (possible values: `text` / `values`) (default `text`) |
| `--x-axis-min` | float64 | optional | Lower bound of the display range of a continuous numeric X axis; must be used together with --x-axis-numbers-as values |
| `--x-axis-max` | float64 | optional | Upper bound of the display range of a continuous numeric X axis; must be used together with --x-axis-numbers-as values |
| `--y-axis-min` | float64 | optional | Lower bound of the display range of the left Y axis; omitted by default, and passed together with --y-axis-max only when the user explicitly requests a fixed range; must not directly use the minimum value of a single data source column, and must be less than the upper bound |
| `--y-axis-max` | float64 | optional | Upper bound of the display range of the left Y axis; omitted by default, and passed together with --y-axis-min only when the user explicitly requests a fixed range; must be calculated based on the values actually plotted by the chart, and must be greater than the lower bound |
| `--dim1-index` | int | optional | 1-based index of the unique category/X-axis dimension within the data range; default 1; multiple fields forming a multi-level horizontal axis are not supported |
| `--dim2-indexes` | string | optional | Comma-separated list of 1-based indexes of the value/Y-axis series; must not include dim1, at most 50. For legacy bubble chart calls, pass 2–4 in the order of `x,y[,group][,size]`; for new calls, prefer role indexes; for pie charts and permutation charts, pass only 1 |
| `--series-types` | string | optional | Combination charts only; specify the series types in the order of --dim2-indexes, comma-separated, with possible values column, line, area, scatter; the count must match the numeric series |
| `--series-y-axes` | string | optional | Combination charts only; first compare the units and magnitudes of the series, and put the series that would be flattened on the right axis; pass left or right in the order of --dim2-indexes; the count must match the numeric series |
| `--key-index` | int | optional | Bubble charts only: 1-based index of the identifier/name dimension; mutually exclusive with the dim1/dim2 indexes; default 1 |
| `--x-index` | int | optional | Bubble charts only: 1-based index of the X value dimension; must be provided together with --y-index |
| `--y-index` | int | optional | Bubble charts only: 1-based index of the Y value dimension; must be provided together with --x-index |
| `--group-index` | int | optional | Bubble charts only: 1-based index of the optional grouping dimension |
| `--size-index` | int | optional | Bubble charts only: 1-based index of the optional bubble size dimension |
| `--title` | string | optional | Chart title |
| `--subtitle` | string | optional | Chart subtitle |
| `--legend-position` | string | optional | Legend position; pie charts default to bottom, hidden hides the legend (possible values: `top` / `bottom` / `left` / `right` / `hidden`) |
| `--x-axis-title` | string | optional | X-axis title |
| `--y-axis-title` | string | optional | Left Y-axis title |
| `--secondary-y-axis-title` | string | optional | Right Y-axis title |
| `--x-axis-label-angle` | int | optional | X-axis label rotation angle (possible values: `-90` / `-45` / `0` / `45` / `90`) |
| `--y-axis-label-angle` | int | optional | Left Y-axis label rotation angle (possible values: `-90` / `-45` / `0` / `45` / `90`) |
| `--data-labels` | string | optional | Data label content; for regular basic charts, pass value by default, and do not omit it merely because there are many data points or series; pass none only when the user explicitly requests hiding all labels; value, category, and percentage can form any non-empty combination in the order value_category_percentage; series displays the series name (possible values: `none` / `value` / `category` / `percentage` / `value_category` / `value_percentage` / `category_percentage` / `value_category_percentage` / `series`) |
| `--data-label-position` | string | optional | For regular non-stacked column charts, generally pass outside when labels are shown; in other scenarios, pass it only when the user explicitly specifies it; it only adjusts the position of existing data labels and does not enable labels on its own (possible values: `auto` / `top` / `bottom` / `left` / `right` / `center` / `inside` / `outside`) |
| `--stack` | string | optional | Stacking mode (possible values: `none` / `normal` / `percent`) |
| `--stacked` | bool | optional | Compatibility alias; equivalent to --stack normal (hidden flag: not listed in `--help`, but can be passed normally) |
| `--smooth` | bool | optional | Whether to use a smooth curve; explicitly disable with --smooth=false |
| `--color-palette` | string | optional | Preset color theme for the whole chart; mutually exclusive with --colors (possible values: `brandColorSeries@v2` / `rainbowColorSeries@v2` / `complementaryColorSeries@v2` / `converseColorSeries@v2` / `primaryColorSeries@v2` / `singleColorSeries-B-@v2` / `singleColorSeries-W-@v2` / `singleColorSeries-G-@v2` / `singleColorSeries-Y-@v2` / `singleColorSeries-O-@v2` / `singleColorSeries-R-@v2` / `singleColorSeries-D-@v2`) |
| `--colors` | string_slice | optional | Custom colors for the whole chart series, comma-separated and at least 2 hexadecimal color values; mutually exclusive with --color-palette |
| `--anchor-cell` | string | optional | Optional chart anchor cell, such as F2; when omitted, it is placed to the right of the data range |
| `--width` | int | optional | Optional chart width; must be passed together with --height; for pie charts and scenarios with long category labels, widen appropriately to avoid truncation |
| `--height` | int | optional | Optional chart height; must be passed together with --width |

### `+chart-config-update`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--chart-id` | string | required | Target chart reference_id |
| `--title` | string | optional | Chart title |
| `--subtitle` | string | optional | Chart subtitle |
| `--legend-position` | string | optional | Legend position; hidden hides the legend (possible values: `top` / `bottom` / `left` / `right` / `hidden`) |
| `--x-axis-title` | string | optional | X-axis title |
| `--y-axis-title` | string | optional | Left Y-axis title |
| `--secondary-y-axis-title` | string | optional | Right Y-axis title |
| `--x-axis-label-angle` | int | optional | X-axis label rotation angle (possible values: `-90` / `-45` / `0` / `45` / `90`) |
| `--y-axis-label-angle` | int | optional | Left Y-axis label rotation angle (possible values: `-90` / `-45` / `0` / `45` / `90`) |
| `--x-axis-min` | float64 | optional | Lower bound of the display range of a continuous numeric X axis; must be less than --x-axis-max |
| `--x-axis-max` | float64 | optional | Upper bound of the display range of a continuous numeric X axis; must be greater than --x-axis-min |
| `--y-axis-min` | float64 | optional | Lower bound of the display range of the left Y axis; omitted by default, and passed together with --y-axis-max only when the user explicitly requests a fixed range; must not directly use the minimum value of a single data source column, and must be less than the upper bound |
| `--y-axis-max` | float64 | optional | Upper bound of the display range of the left Y axis; omitted by default, and passed together with --y-axis-min only when the user explicitly requests a fixed range; must be calculated based on the values actually plotted by the chart, and must be greater than the lower bound |
| `--data-labels` | string | optional | Data label content; value, category, and percentage can form any non-empty combination in the order value_category_percentage; series displays the series name, none hides labels (possible values: `none` / `value` / `category` / `percentage` / `value_category` / `value_percentage` / `category_percentage` / `value_category_percentage` / `series`) |
| `--data-label-position` | string | optional | Pass only when the user explicitly specifies it; it only adjusts the position of existing data labels and does not enable labels on its own; when omitted, the data label position is automatically optimized by chart type (possible values: `auto` / `top` / `bottom` / `left` / `right` / `center` / `inside` / `outside`) |
| `--aggregate-categories` | bool | optional | Whether to aggregate identical categories; use --aggregate-categories=false for sparse punctuation or when row-by-row data points need to be preserved; when omitted, the current setting is retained |
| `--stack` | string | optional | Stacking mode (possible values: `none` / `normal` / `percent`) |
| `--stacked` | bool | optional | Compatibility alias; equivalent to --stack normal (hidden flag: not listed in `--help`, but can be passed normally) |
| `--smooth` | bool | optional | Whether to use a smooth curve; explicitly disable with --smooth=false |
| `--color-palette` | string | optional | Preset color theme for the whole chart; mutually exclusive with --colors (possible values: `brandColorSeries@v2` / `rainbowColorSeries@v2` / `complementaryColorSeries@v2` / `converseColorSeries@v2` / `primaryColorSeries@v2` / `singleColorSeries-B-@v2` / `singleColorSeries-W-@v2` / `singleColorSeries-G-@v2` / `singleColorSeries-Y-@v2` / `singleColorSeries-O-@v2` / `singleColorSeries-R-@v2` / `singleColorSeries-D-@v2`) |
| `--colors` | string_slice | optional | Custom colors for the whole chart series, comma-separated and at least 2 hexadecimal color values; mutually exclusive with --color-palette |

### `+chart-data-update`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--chart-id` | string | required | Target chart reference_id |
| `--data-range` | string | required | New data range; when --header-range is not passed, it must include the header; when passed or when the original chart already uses a detached header, pass only pure data; supports comma-separated and multi-range across sub-sheets |
| `--header-range` | string | optional | Optional detached header range; when provided, the detached header mapping is used automatically; when omitted, the original chart's existing detached mapping is preserved |
| `--data-direction` | string | optional | Data series direction; when omitted, the existing chart direction is used (optional values: `column` / `row`) |
| `--dim1-index` | int | optional | 1-based index of the unique category/X-axis dimension in the data range; when omitted, the 1st dimension is used; multiple fields forming a multi-level horizontal axis are not supported |
| `--dim2-indexes` | string | optional | 1-based index of the value/Y-axis series in the data range, comma-separated; when omitted, all dimensions except dim1 are used |
| `--key-index` | int | optional | Bubble chart only: 1-based index of the identifier/name dimension; mutually exclusive with dim1/dim2 indices, defaults to 1 |
| `--x-index` | int | optional | Bubble chart only: 1-based index of the X value dimension; must be provided together with --y-index |
| `--y-index` | int | optional | Bubble chart only: 1-based index of the Y value dimension; must be provided together with --x-index |
| `--group-index` | int | optional | Bubble chart only: 1-based index of the optional group dimension |
| `--size-index` | int | optional | Bubble chart only: 1-based index of the optional bubble size dimension |

### `+chart-create`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--properties` | string + File + Stdin (composite JSON) | required | Complete chart configuration JSON. Top-level fields are `position` / `offset` / `size` / `snapshot` (no top-level `data`, and no further nested `properties`); chart data configuration is under `snapshot.data` (including `refs` / `headerMode` / `dim1` / `dim2`); it must contain at least one of `snapshot.data.dim1.serie.index` or `dim2.series[].index`, otherwise the server rejects it. The structure is deeply nested; for the complete structure run `--print-schema --flag-name properties` |
| `--print-example` | string | optional | Print the minimal usable `--properties` template for the specified chart type and then exit directly (`area` / `bar` / `bubble` / `column` / `combo` / `line` / `pareto` / `pie` / `radar` / `scatter` / `waterfall`). Purely local execution, no locator flag needed, no network request sent; when an unknown type is passed, all available types are listed |

### `+chart-update`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--chart-id` | string | required | Target chart reference_id |
| `--properties` | string + File + Stdin (composite JSON) | required | Chart configuration patch JSON; by default only changed fields are passed, and fields not passed remain unchanged; ordinary objects are merged recursively, arrays are replaced as a whole |

### `+chart-delete`

_Common four-piece set · System: `--yes`, `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--chart-id` | string | required | Target chart reference_id |

## Schemas

> Composite JSON flag field quick reference (only top level + one level of nesting is listed). For deeper structures see `## Examples` below, or use `--print-schema` to read the complete JSON Schema (usage see index.md "Common flag quick reference" and "Agent usage tips").

### `+chart-create` `--properties` / `+chart-update` `--properties`

_Chart properties for create/update_

**Top-level fields**:
- `position` (object?) — required { row: number, col: string }
- `offset` (object?) — optional { row_offset?: number, col_offset?: number }
- `size` (object?) — required { width: number, height: number }
- `snapshot` (oneOf?) — chart snapshot configuration

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` arranged at the top (XOR rules same as `+csv-get`).

### `+chart-list`

Output contract: returns a list of charts grouped by worksheet, each chart containing `chart_id` / `position` / `details.snapshot`, etc.

### `+chart-create-basic`

By default, the 1st dimension is used as the category/X-axis, and the remaining dimensions are used as value series; for ordinary charts, you can precisely select using the 1-based `--dim1-index` and the comma-separated `--dim2-indexes`. For combination charts, by default the first value series is a left-axis column and the rest are right-axis lines; before creating, still compare the units and magnitudes of each series to avoid lines or small-magnitude series being pressed close to the X-axis because they share the left axis. When other combinations are needed, use `--series-types` and `--series-y-axes` to specify the series type and left/right axis item by item in the order of `--dim2-indexes`; series types can be `column`, `line`, `area`, `scatter`, and the counts of both parameter groups must match the final number of value series. Horizontal-axis numbers are by default treated as equally spaced text categories; only when the true spacing between numbers needs to affect the graphical positions should you pass `--x-axis-numbers-as values` to use a continuous numeric axis. Bubble charts instead use `--key-index`, `--x-index`, `--y-index`, and the optional `--group-index` / `--size-index`, where x/y must be provided together, and key defaults to 1; role indices cannot be mixed with dim1/dim2 indices. The old bubble chart dim1/dim2 positional calls remain compatible. Pie charts and permutation charts allow only one value series; combination charts require at least two value series; all charts can select at most 50 value series. Pie charts place the legend at the bottom by default and appropriately increase `--width` according to the length of category labels (pass `--height` at the same time). By default, let `--data-range` include the real header; only when the "dimension/series names" are separated from the pure data should you let `--data-range` pass only pure data and use `--header-range` to pass the corresponding one-row (column) or one-column (row) header. When category dimensions and value dimensions are not contiguous, the range parameter can pass comma-separated multiple ranges, and ranges from multiple sub-sheets are also supported; cross-sub-sheet ranges aligned along the data point axis retain independent references, while misaligned rows, misaligned columns, or overlaps within the same sub-sheet are merged into the minimal bounding rectangle, and cross-sub-sheet ranges that cannot be aligned will report an error. A successful standalone call returns the complete `snapshot`, so you can directly inspect the creation result and continue modifying. Parameter names use `--anchor-cell` and `--data-labels`. In compatible calls, `--type` / `--range` are handled as `--chart-type` / `--data-range` respectively, and `--x-axis` / `--y-axis` are handled as axis titles; new calls should still prefer the canonical parameter names.

**Readability of a continuous numeric X-axis**: `--x-axis-numbers-as values` preserves the true spacing of numbers, but when no range is specified it may automatically include 0. If the data is concentrated in a narrow interval far from 0, the data points will be squeezed to one side of the chart; in this case you should keep `values`, tighten the range at creation time with `--x-axis-min` / `--x-axis-max`, and for existing charts correct it with `+chart-config-update`; do not change it to `text` to mask the problem. The two boundaries can be set separately; when set together, min must be less than max.

```bash
# Column chart: placed to the right of the data range by default
lark-cli sheets +chart-create-basic --url "..." --sheet-name "Sheet1" \
  --chart-type column --data-range "'Sheet1'!A1:C10" \
  --title "销售额对比" --x-axis-title "品类" --y-axis-title "销售额" \
  --legend-position bottom --data-labels value

# Dual-axis combination chart: monthly target and actual completion as left-axis columns, completion rate as a right-axis line
lark-cli sheets +chart-create-basic --url "..." --sheet-name "Sheet1" \
  --chart-type combo --data-range "'Sheet1'!A1:D13" \
  --dim1-index 1 --dim2-indexes 2,3,4 \
  --series-types column,column,line --series-y-axes left,left,right \
  --title "价格与效率" --y-axis-title "价格" --secondary-y-axis-title "效率" \
  --anchor-cell F2 --width 720 --height 420

# Reference line shows only one label: column C contains repeated target values, column D has values only at target positions and is empty in the remaining cells
lark-cli sheets +chart-create-basic --url "..." --sheet-name "Sheet1" \
  --chart-type combo --data-range "'Sheet1'!A1:D7" \
  --dim1-index 1 --dim2-indexes 2,3,4 \
  --series-types line,line,scatter --series-y-axes left,left,left \
  --aggregate-categories=false \
  --title "趋势与目标线" --anchor-cell F2 --width 720 --height 420

# First obtain the complete series array from the creation result or +chart-list, then write it back as a whole; the reference line series does not set labels
lark-cli sheets +chart-update --url "..." --sheet-id "$SID" --chart-id "chrXXX" \
  --properties '{"snapshot":{"plotArea":{"plot":{"series":[{"index":2,"comboType":"line","labels":{"value":true}},{"index":3,"comboType":"line"},{"index":4,"comboType":"scatter","labels":{"value":true}}]}}}}'

# Bubble chart: x and y are required, group and size are optional
lark-cli sheets +chart-create-basic --url "..." --sheet-name "Sheet1" \
  --chart-type bubble --data-range "'Sheet1'!A1:E20" \
  --key-index 1 --x-index 2 --y-index 3 --group-index 4 --size-index 5 \
  --title "客户分布"

# Numeric scatter chart: preserve the true X spacing while tightening the display range far from 0
lark-cli sheets +chart-create-basic --url "..." --sheet-name "Sheet1" \
  --chart-type scatter --data-range "'Sheet1'!A1:B20" \
  --x-axis-numbers-as values --x-axis-min 237 --x-axis-max 239

# Header separated from data: data-range passes only pure data, header-range passes the header in the same dimension order
lark-cli sheets +chart-create-basic --url "..." --sheet-name "Sheet1" \
  --chart-type line \
  --data-range "'Sheet1'!A2:A10,'Sheet1'!K2:L10" \
  --header-range "'Sheet1'!A1,'Sheet1'!K1:L1"

# Horizontal category row + one row of values: the category row also belongs to data-range, do not put it into header-range
lark-cli sheets +chart-create-basic --url "..." --sheet-name "Sheet1" \
  --chart-type line \
  --data-range "'Sheet1'!A1:M1,'Sheet1'!A3:M3" \
  --data-direction row --dim1-index 1 --dim2-indexes 2
```

Create multiple basic charts at once. First prepare all the data, then generate `ops.json`:

```json
[
  {
    "sheet_name": "Sheet1",
    "chart_type": "column",
    "data_range": "'Sheet1'!A1:C10",
    "title": "分类对比",
    "anchor_cell": "F2"
  },
  {
    "sheet_name": "Sheet1",
    "chart_type": "line",
    "data_range": "'Sheet1'!E1:G10",
    "title": "趋势变化",
    "anchor_cell": "F18"
  }
]
```

```bash
lark-cli sheets +batch-chart-create --url "..." --operations @ops.json
lark-cli sheets +chart-list --url "..." --sheet-name "Sheet1"
```

For compatibility with old calls, the CLI can still read the historical `{shortcut:"+chart-create-basic",input:{...}}` structure, but new tasks should directly fill in the flat `+chart-create-basic` flags above.

When batch-correcting existing charts, operations should contain only configuration or data updates; the CLI first reads the current snapshot of each target chart, then merges the corresponding partial properties into a single `batch_update`:

```json
[
  {"shortcut":"+chart-config-update","input":{"sheet_name":"Sheet1","chart_id":"chrA","title":"新标题"}},
  {"shortcut":"+chart-data-update","input":{"sheet_name":"Sheet1","chart_id":"chrB","data_range":"'Sheet1'!A1:D10"}}
]
```

```bash
lark-cli sheets +batch-chart-update --url "..." --operations @updates.json
```

### `+chart-data-update`

When after creation you find a missing column, an overly wide range, a change in an auxiliary category column, an incorrect series selection, or an incorrect data direction, update only the data source and preserve the title, color scheme, legend, and placement. The update must specify `--chart-id`; the semantics of range, direction, ordinary dim1/dim2 indices, and bubble chart role indices are the same as `+chart-create-basic`. When `--data-direction` is omitted, the existing chart direction is used. By default, let the new range include the header; if the original chart already uses a detached header and the header is unchanged, `--header-range` can be omitted, and the tool will preserve the existing mapping. The tool returns the updated `data` and the actually adopted `normalized_data_ranges`.

```bash
# Include the omitted last column in the original line chart, preserving the title, color scheme, legend, and placement
lark-cli sheets +chart-data-update --url "..." --sheet-id "$SID" --chart-id "chrXXX" \
  --data-range "'Sheet1'!A1:M6"
```

### `+chart-config-update`

Pass only the fields that need to be changed; on success, return the updated `viewModel`. `--data-labels` supports any non-empty combination of `value`, `category`, `percentage`, and the combined values are concatenated in the order of `value_category_percentage`; additionally, `series` can be used to show series names, and `none` can be used to delete data labels. When multiple series need different label strategies, do not use this global parameter; handle it according to the auxiliary column and advanced series configuration process above. `--legend-position hidden` hides the legend; to explicitly turn off smooth curves, use `--smooth=false`. To reduce parameter retries, `--stacked` is automatically handled as `--stack normal`, `percentage,value` or `value,percentage` is automatically handled as `value_percentage`, and `--x-axis` / `--y-axis` is automatically handled as `--x-axis-title` / `--y-axis-title`; new calls should still prefer the canonical parameters.

```bash
lark-cli sheets +chart-config-update --url "..." --sheet-id "$SID" --chart-id "chrXXX" \
  --title "新标题" --x-axis-label-angle -45 --legend-position right

lark-cli sheets +chart-config-update --url "..." --sheet-id "$SID" --chart-id "chrXXX" \
  --data-labels value_percentage --stack percent --aggregate-categories=false

```

### `+chart-create`

For basic charts, prefer `+chart-create-basic`. Use `+chart-create` only when the semantic shortcut cannot express a single series, a single data point, or advanced engine fields. Advanced creation requires a structurally complete snapshot; first use `+chart-create --print-example <type>` to obtain the minimal structure for the corresponding chart type, then modify only the fields needed by the task. Do not print or read the entire large schema first.

### `+chart-update`

For titles, axes, legends, labels, stacking, smoothing, color schemes, and aggregation of identical categories, prefer `+chart-config-update`; for data range and direction, use `+chart-data-update`. Use `+chart-update` only for advanced fields; do not construct raw properties for common modifications.

`+chart-update` supports true partial updates: pass only the fields that actually change, and fields not passed remain unchanged; do not copy and write back the complete snapshot.

- Ordinary objects inside `snapshot` are merged recursively;
- Arrays such as `refs` / `axes` / `series` are replaced as a whole. When changing only one item in an array, first read the current complete array from `+chart-list`, then write back only that array after modification;
- `snapshot.data.isStaticData` cannot be changed through update; when you need to switch between static / non-static data, delete and recreate;
- When adjusting only the size, pass `size` directly; there is no need to pass `snapshot`;
- Before execution, use `--dry-run` to check the target sheet, chart_id, and minimal patch; after execution, use `+chart-list --chart-id <id>` to verify the actual snapshot.

```bash
# Adjust size only; no need to carry a snapshot
lark-cli sheets +chart-update --url "..." --sheet-id "$SID" --chart-id "chrXXX" \
  --properties '{"size":{"width":640,"height":400}}'
```

<a id="高级-properties-边界"></a>
#### Advanced `properties` boundaries

- Query only the subtree to be changed this time; do not print the complete large schema first:
  ```bash
  lark-cli sheets +chart-update --print-schema \
    --flag-name properties.snapshot.plotArea.axes
  ```
- `--dry-run` in the output, `tool_name` / `operation` / `basic_chart` / `properties` are internal requests after CLI translation, used only for inspection, and cannot be copied back into operations or submitted again as an MCP body.
- `--data-range` itself supports comma-separated multiple ranges and cross-sub-sheet ranges. Data being non-contiguous or spanning sub-sheets alone is not a reason to hand-write a raw data mapping.
- When raw data uses an inline header, `refs` includes the real header and does not write `nameRef`; only when `refs` covers only pure data and the real header is outside the range should you use detached: explicitly set `headerMode='detached'`, and make `dim1.serie.nameRef` and each `dim2.series[].nameRef` point to the corresponding header cell.
- The raw stacking field is located at `snapshot.plotArea.plot.extra.stack`; ordinary tasks still use `--stack normal|percent`. The existence of the `plotArea.plot.labels` object is itself the switch; when turning off labels, omit the entire object; ordinary tasks use `--data-labels none`.
- `axes[].label` does not accept `format` / `number_format`. For date, percentage, and numeric formats, modify the source cell's `cell_styles.number_format`.

### `+chart-delete`

Example:

```bash
# dry-run first see what will be deleted (sheet locator required)
lark-cli sheets +chart-delete --url "https://example.feishu.cn/sheets/shtXXX" --sheet-id "$SID" \
  --chart-id "chrXXX" --dry-run

# Actually execute
lark-cli sheets +chart-delete --url "https://example.feishu.cn/sheets/shtXXX" --sheet-id "$SID" \
  --chart-id "chrXXX" --yes
```

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute constraints

- `Validate`: XOR common four-piece set; `+chart-data-update` requires `--chart-id` and `--data-range`, and validates that `--dim1-index` / `--dim2-indexes` are positive integer indices; the `--properties` of `+chart-create` / `+chart-update` must be parseable as valid JSON; `+chart-delete` (high-risk-write) validates that at least one of `--yes` or `--dry-run` is present.
- `DryRun`: `+chart-data-update` / `+chart-create` / `+chart-update` output the "body template to be POSTed"; `+chart-delete` outputs the "chart_id to be deleted and the sheet it belongs to", with zero network side effects.
- `Execute`: after `+chart-create-basic` succeeds, it returns the complete `snapshot`, which can be verified directly; for batch creation, incomplete responses, subsequent updates, or questionable results, call `+chart-list` once per affected sheet to compare the results.

> `+chart-create` / `+chart-update` are write level; as needed, `--dry-run` can be used to preview, and `--yes` is not required. Only `+chart-delete` (high-risk-write) requires `--yes`.
