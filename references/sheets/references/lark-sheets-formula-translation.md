<a id="飞书表格公式生成规则"></a>
# Lark Sheets Formula Generation Rules

> **Purpose of this document**: The **sole authority** on Lark formula correctness — read this before writing any Lark formula or migrating an Excel formula to Lark. It covers formula writing conventions (absolute references, range syntax), projection vs. spill, `ARRAYFORMULA` / array semantics and row-by-row filling, high-risk reference functions, date differences, and the list of unsupported functions.
> **Boundary**: This document only covers "how to write a formula correctly"; how a formula is **written into a sheet** (`+cells-set` / template cells + `--copy-to-range` / fault-tolerant read-back) is covered in `references/lark-sheets-write-cells.md`. After a formula is written, you must use `references/lark-sheets-formula-verify.md` to diagnose the formula range segment by segment and read back the key formulas; do not mistake "translated correctly" for "the result is definitely correct". This document contains no shortcuts; for general editing guidelines see "Lark Sheets Editing Guidelines" in the main index.md.

**Core principle one: Lark does not spill (overflow-expand) by default the way Excel 365 does.** When a parameter requires a single value but a range is actually passed in, Lark by default takes the "projection" (the one value corresponding to the formula's row/column); only when evaluation is **inside an array formula context** — the outermost layer is wrapped in `ARRAYFORMULA`, or the formula already contains a native array function (`FILTER` / `XLOOKUP` / `SORT`, etc., see the list below) — does it expand item by item. Both `ARRAYFORMULA` and "row-by-row scalar formula + `--copy-to-range` fill" are faithful after export; choose as needed: the former covers the whole block with one formula and is shorter to write; the latter has an independent formula in each cell, so after export each cell can be edited individually in Excel.

**Core principle two: `LAMBDA`-family higher-order functions (`MAP` / `REDUCE` / `SCAN` / `BYROW` / `BYCOL` / `MAKEARRAY`) compute correctly inside Lark, but silently compute incorrectly when exported to `.xlsx`.** On export, Lark only inlines the LAMBDA body into an ordinary array expression and **does not preserve higher-order semantics**, with no error at any point:

- `REDUCE(0,A2:A6,LAMBDA(acc,x,acc+x))` (reduction sum) → `=0+A2:A6`, the entire reduction is lost
- `BYROW(A2:B6,LAMBDA(r,SUM(r)))` (row-by-row sum) → `=SUM(A2:B6)`, 5 results collapse into 1
- `MAP(A2:A6,LAMBDA(x,IF(x>0,x,0)))` → `=A2:A6>0`, `IF` disappears entirely

The only exception is `MAP` when the LAMBDA body is a **pure operator or single-parameter function**, where the expansion happens to be equivalent (`LAMBDA(a,b,a*b)` → `=A2:A6*B2:B6` ✓). **In all other cases, switch to `ARRAYFORMULA` / row-by-row filling / helper columns** — the same item-by-item logic written as `=ARRAYFORMULA(IF(A2:A6>0,A2:A6,0))` is fully preserved after export, while written as `MAP(...LAMBDA(...IF...))` it is lost. Such incorrect formulas raise no error, and read-back inside Lark is also correct; they are exposed only after export, and cannot be found by after-the-fact inspection.

<a id="公式书写约定写任何公式都先满足"></a>
## Formula Writing Conventions (satisfy these before writing any formula)

- **Absolute references `$`**: before filling down / to the right, determine which references must be locked — user-specified fixed cells (`$C$3`), data ranges to fix (`$A$2:$B$5`), lock column but not row (`$A2`), lock row but not column (`B$1`). Before filling, check whether exchange rates / tax rates / lookup tables / weight tables need to be fixed, and whether the formula structure is consistent within the same column / row.
- **Formula strings use Lark range syntax**: write `H:H`, `A2:B5`; `H2:H` / `2:2` are **forbidden**. To reference an entire row in a formula, use an explicit range (e.g. `$A2:$Z2`) instead of the forbidden `2:2`. This differs from the A1 notation used for CLI tool parameters (e.g. `--range` / `--copy-to-range`): `D3:D`, `1:1`, `3:6`, which are legal on the parameter side, are instead illegal in a formula string. **Formula strings ≠ CLI parameters**; do not copy the two sets of rules onto each other, as mixing them causes call failures or formula errors.
- **When the deliverable is an exported xlsx, prefer Excel-compatible functions**: if the same computation can be expressed with Excel-compatible functions (SUMIFS / TEXT / MID / FIND, etc.), do not use Lark-specific functions (MAP / REGEXEXTRACT / ARRAYFORMULA, etc.) — Lark-specific functions may fail to recalculate in the exported xlsx; if they must be used, verify recalculation works after export before delivering.

<a id="业务语义契约复杂统计公式写前必做"></a>
## Business Semantics Contract (mandatory before writing complex statistical formulas)

A formula having no error code does not mean the business logic is correct. Before writing, organize the user's requirements into a short contract and check it item by item:

1. **Fields**: use the header plus 3–5 rows of real values to confirm the semantics of columns such as "name/employee ID, start/end, seconds/minutes"; never guess from column letters or column names alone.
2. **Thresholds**: for Chinese "Above / At least / No less than" use `>=`; for "Exceed / Greater than" use `>`; for "Below / At most / No higher than" use `<=`. Records whose value exactly equals the threshold must serve as sentinels.
3. **Units and time zones**: explicitly record seconds↔minutes, percentage↔decimal, Unix seconds/milliseconds, and UTC→local time zone conversions; when a date is computed from a timestamp, first hand-calculate it with one known record.
4. **Complete range**: the formula range must cover the true first and last rows of the source data; do not treat the first N rows sampled to probe the structure as the computation range; when `truncated` / `complete:false` appears in read-back/persisted results, continue reading first.
5. **Business sentinels**: before writing, obtain at least one verifiable expectation using a local script or hand calculation; after writing, verify the first, middle, last, empty values, threshold boundaries, and that expectation at the same time. `formula-verify success` only proves there is no formula error code; it cannot replace these result assertions.

<a id="翻译后建议代码复现校验"></a>
## Post-translation recommendation: code reproduction verification

After the formula syntax translation is complete, it is recommended to independently reproduce an "equivalent computation result" on the source data with a local script before writing. Process:

1. **Pick 3-5 representative input rows** (one each for first row / middle section / last row / containing empty values / containing abnormal formatting)
2. **Use Python to reproduce the semantics of the original Excel formula** (not the semantics of the Lark translation, but the result the user originally wanted)
3. **After writing the translated Lark formula, read back the actual values of these rows**
4. **Three-way comparison**: `Excel 原公式语义 == Python 复现 == 飞书译文回读值`; when inconsistent, investigate first (array semantics? date difference? range reference?), and if it cannot be fully fixed, state the risk in the delivery notes.

**Rationale**: Excel→Lark syntax translation easily produces equivalence deviations in spill / arrays / date differences / range references; passing syntax conversion alone is not enough to guarantee correct business results.

<a id="落表后的默认交接"></a>
## Default handoff after writing to the sheet

This document addresses "how to write a formula correctly", not "it will definitely run with zero errors once written into the sheet". Therefore:

1. After completing the formula rewrite per this document, use `references/lark-sheets-write-cells.md` / `references/lark-sheets-batch-update.md` to actually write the formula into the sheet.
2. Once a formula is written to the sheet, you must run `+formula-verify --exit-on-error` segment by segment over the formula ranges added / modified this time; for key formula areas, also read back the `formula` of the first, middle, last, and summary rows.
3. Only end the formula task after each segment's `status='success'`; for `errors_found` continue fixing, for `partial` narrow the `--range` or split by sheet and continue scanning; do not replace complete verification with an explanation; AI formulas do not follow this success convergence — deliver them per the "AI formulas" rule below of one asynchronous status check over the entire range.

**Extra step for changing static values into formulas (tasks like "make the statistics table follow changes in the source data")**: before rewriting, snapshot the original static values, and after the formulas are written, diff each cell against the snapshot. When inconsistent, first try caliber variants (`>` / `>=`, rounding method, matching column) to approach the original values; still inconsistent does not count as failure — the original static values may correspond to old data or contain an undeclared caliber — but you must provide the diff table and an explanation of the caliber used in the delivery notes; never deliver without declaring the differences.

**When writing computation results for the first time, write formulas by default**: when doing statistics, summaries, rankings, classification calculations, etc. on an existing sheet — regardless of whether the source data is existing cells or newly read data — by default write the computation results as formulas referencing the source data; do not compute the values locally in Python and then hard-code them in. Exceptions to the formula-first principle: externally scraped data, constants that never change, circular references.

<a id="ai-公式ai-函数"></a>
## AI formulas (`AI` function)

Lark Sheets provides a unified **`AI` formula**: describe the requirement in natural language, and the AI returns a text result. An AI formula is **written in exactly the same way as an ordinary formula** (reusing `references/lark-sheets-write-cells.md`'s `+cells-set` / `set_cell_range`, no special interface needed); the only difference is that the computation is **asynchronous** — after writing, you must wait for the AI to finish computing before there is a result.

**AI formulas almost inevitably contain commas + double quotes (e.g. `=AI("翻译成中文", E2)`), so by default use `+cells-set`'s JSON `formula` field, not `+csv-put`**: `+csv-put` splits the formula into columns by comma and corrupts it (see `references/lark-sheets-write-cells.md` for details). In `+cells-set`, write the double quotes inside the formula as `\"`. To fill an entire column, use a template + `--copy-to-range`:

```bash
# Write one AI formula in the seed cell (escape internal quotes as \"), then fill down the entire column
lark-cli sheets +cells-set --url <表URL> --sheet-name <子表名> \
  --range D2 --cells '[[{"formula":"=AI(\"翻译成中文\", E2)"}]]' \
  --copy-to-range "D2:D107"
# After writing, first do one +cells-get --include formula check of the seed cell D2 to verify the text, then use --ai-only to validate the entire written range; do not use +cells-get to poll for computation results
lark-cli sheets +formula-verify --url <表URL> --sheet-name <子表名> --range D2:D107 --ai-only
```

**Verification discipline**: AI formula computation is asynchronous. After writing, first do a **one-time formula text check** (do **one** `+cells-get --include formula` on the seed cell / first cell to confirm that what was written in is indeed `=AI(...)` rather than `#ERROR` or a truncated literal) — this step is **mandatory**; what is forbidden is only repeatedly **polling for computation results** with `+cells-get` / `+csv-get`. The **first verification entry point for computation status must be `+formula-verify --ai-only`**; `--range` gives the **entire written range** (read-only, low cost, do not sample); note that `--range` is only passed through to the backend, and the AI-only summary is not guaranteed to narrow by it, so **trust the cell locations in the response, not the total count**. Delivery criterion (machine-readable): `ai_formula_failed_count == 0`; for `failed` / `unsupported` fix first; once satisfied, it can be delivered even if `ai_formula_pending_count > 0` remains, and inform the user that the backend is still computing. If the text check reveals `#ERROR` / a truncated literal (half bracket / full-width bracket), then the formula string was corrupted by escaping at the writing layer, not an AI failure; go back to `+cells-set` and rewrite with `\"` (see `references/lark-sheets-formula-verify.md` for details).

<a id="语法"></a>
### Syntax

```
=AI(prompt)
=AI(prompt, range)
=AI(part1, part2, ...)
```

- `prompt`: the prompt, describing what you want the AI to do (it can be a string constant or a cell reference).
- `range`: optional, the input data handed to the AI for processing. It can be a single cell (e.g. `A2`) or a range of cells (e.g. an entire row `A2:G2` or several columns `A2:C2`) — this range of cells is fed to the AI together as the **input context for this one computation**, and the formula returns **one** result. For the specific syntax see "Common uses" below.
- **Multi-parameter concatenation**: `AI` accepts multiple parameters and concatenates string constants and cell / range references in order into one complete prompt. This can be used to assemble values scattered in different locations into one sentence, e.g. `=AI("结合", A2, "和", A4, "的描述，总结3个关键词")`.

<a id="常见用途同一个函数靠提示词区分"></a>
### Common uses (same function, distinguished by the prompt)

`range` can be a single cell, or reference an entire row / multiple columns as the input context for one computation; multiple parameters can also be used to concatenate values from different locations into the same prompt:

| Scenario | Example |
|---|---|
| Translation | `=AI("翻译成日语", A2)` |
| Sentiment analysis | `=AI("判断客户情绪，只返回 Positive、Neutral、Negative", A2)` |
| Classification / tagging | `=AI("判断这封邮件是不是垃圾邮件", D2)`; combined with multiple columns of auxiliary information for judgment: `=AI("把餐厅归类到它所属的纽约市行政区，可参考街区信息", A2:C2)` |
| Information extraction | `=AI("提取邮箱", A2)` / `=AI("提取手机号", A2)` |
| Summarization | `=AI("为这位客户的反馈写一句话总结", A2:D2)`; `=AI("用要点列出这段书籍摘要的主要主题", D2)` |
| Multi-value concatenation | `=AI("结合", A2, "和", A4, "的描述，总结3个关键词")` |
| Polishing / rewriting | `=AI("改写得更正式", A2)` |
| Copy generation | `=AI("用 10 个字以内为活动生成一句宣传语", A2)`; reference an entire row to respond to specific content: `=AI("给评审写一封邮件，针对评审意见中的具体条目逐条回应", A2:G2)`; `=AI("根据这段岗位职责摘要，为该职位生成一组关键词", A2:C2)` |
| Data cleaning / standardization | `=AI("统一公司名称写法", A2)` |
| Keyword extraction | `=AI("提取 5 个关键词，用逗号分隔", A2)` |

<a id="提示词最佳实践写对提示词是结果稳定的关键"></a>
### Prompt best practices (writing the prompt correctly is the key to stable results)

The quality of an AI formula depends heavily on the prompt. Recommended:

1. **Specify the output format**: rather than writing "analyze this", write "judge the sentiment, return only Positive / Neutral / Negative". Limiting the possible values makes the result machine-readable and recomputable.
2. **Specify the language**: writing "translate into Chinese" is more stable than just "translate".
3. **Specify the length**: e.g. "summarize in one sentence", "within 30 characters".
4. **When structure is needed, explicitly ask for JSON**: e.g. prompt "return JSON: {category:'', score:0-100}", and the AI can output a structured result fairly reliably.

<a id="与普通公式组合"></a>
### Combining with ordinary formulas

`AI` can be nested into a formula chain like an ordinary function, referencing cells or ranges:

```
=IF(B2>90, AI("夸奖一下这位员工"), "")
=IF(A2="", "", AI("翻译成英文", A2))
```

`AI(...)` returns a single result (a scalar); when nesting it into a formula chain, just treat it as a scalar, and do not wrap it in `TEXTJOIN` / `ARRAYFORMULA` or other constructs designed for array semantics — AI formulas do not spill arrays.

<a id="用-cli-对一列逐行处理"></a>
### Processing a column row by row with the CLI

To run AI row by row over an entire column, the recommended approach is **template cell + `--copy-to-range` extension downward**: write `=AI("<提示词>", A2)` in the seed cell, then use `--copy-to-range` to extend it to the entire column; relative references increment with the row (`A2` → `A3` → …). This way each row is computed independently and behavior is predictable, which is more stable than relying on a single formula to spread across the entire column at once.

**When there are many rows, batch serially**: AI formula computation is asynchronous, and the more rows extended at once, the more likely a timeout is triggered. Ordinary formulas can be spread across the entire column / to the end of the column (`H:H`, `D3:D`) in one go per `references/lark-sheets-write-cells.md`; for **AI formulas** with many rows, it is recommended to extend **serially** in batches (order-of-magnitude reference: about a few hundred to a thousand rows per batch) — after writing one batch, use `+formula-verify --ai-only` to confirm this batch has entered computation before spreading the next batch; do not spread an extremely long column at once, and do not run multiple batches concurrently.

**Verification and delivery after writing AI formulas**: first do **one** `+cells-get --include formula` on the seed cell / first cell to check the formula text (**mandatory step**, confirming that what was written in is `=AI(...)` rather than `#ERROR` / a truncated literal), then the first verification entry point for computation status must be `references/lark-sheets-formula-verify.md`'s `+formula-verify --ai-only --range <整个写入区间>` (read-only, low cost, `--range` covers the entire range, do not sample), and **polling for computation results with `+cells-get` / `+csv-get` is forbidden**. Delivery criterion (machine-readable): `ai_formula_failed_count == 0` (`--range` does not guarantee narrowing the summary scope; verify this range by the cell locations in the response, not by comparing totals); once satisfied, it can be delivered even if `ai_formula_pending_count > 0` remains; Lark will continue computing in the background, and at delivery inform the user that "the AI formula is still running in the background and results will complete progressively". For details see `references/lark-sheets-formula-verify.md`.

<a id="决策流程"></a>
## Decision flow

1. The final result is a **scalar** (single value) → write an ordinary formula directly
2. The final result is a **one-dimensional or two-dimensional array**:
   - The formula **contains** a Lark native array function (such as FILTER, XLOOKUP, MAP, etc.) → write it directly; array semantics automatically propagate through the entire formula, including scalar operations applied outside a native array function (e.g. `+1`, `*100`)
   - The formula **contains no** native array function and is merely doing scalar computation on a range → wrap the entire expression in `ARRAYFORMULA`, or write a **single-row scalar formula and fill down / to the right** (`--copy-to-range`)
3. Excel relies on `ROW(range)` to drive `SUBTOTAL/INDIRECT/OFFSET` item by item → split into helper columns: write a single-row scalar formula in each row of the helper column (`=SUBTOTAL(103,INDIRECT("E"&ROW(E16)))`) and fill down, then aggregate over the helper column; but when the result must stay linked to filtering, keep a single `MAP(...LAMBDA(...))`, see "Excel implicit item-by-item evaluation" below
4. The inner `INDEX/INDIRECT/OFFSET` returns a range, and the outer `SUMIF/COUNTIF/SUMIFS` still needs to consume these ranges → likewise split into helper columns computed row by row, then aggregate
5. The formula's intent is "compute over multiple ranges separately and then summarize" (for example, using INDIRECT/OFFSET to generate one range per row, then aggregate over all ranges) → Lark cannot directly return "a list of ranges"; you must explicitly reduce the dimensionality: use `VSTACK` to merge vertically, `HSTACK` to merge horizontally, `TOCOL/TOROW` to flatten, or first write the results of each segment into a helper area and then summarize with ordinary aggregate functions
6. Computing a date difference → do not write `DAY(end-start)`; use `DAYS`, `DATEDIF`, or directly `end-start`

<a id="飞书的投影行为不是默认-spill"></a>
## Lark's projection behavior (not spill by default)

The trigger condition is **a parameter requires a single value but a range is actually passed in**; in this case Lark takes a "projection" rather than a "spill":

- Single-column range → take the value by the row where the current formula is located
- Single-row range → take the value by the column where the current formula is located
- Two-dimensional range → take a value only when the current formula position can be mapped into that range; otherwise error
- Array constant `{...}` or a function returning a matrix, in an ordinary scalar context, usually takes only the top-left corner

**The exception is inside an array formula context**: when the outermost layer is wrapped in `ARRAYFORMULA`, or the formula already contains a native array function, the same range is expanded item by item instead of projected.

Therefore (the following all refer to ordinary formulas, i.e. not in an array formula context):
- `=A1:A2` does not spill in an ordinary Lark formula; it only projects to the current row
- `=ABS(A2:B2)` does not yield an entire row; write `=ARRAYFORMULA(ABS(A2:B2))`, or write `=ABS(A2)` / `=ABS(B2)` in cells A and B respectively
- `=TRUNC({1.1111,2.222},{1,2})` to get an entire row, write `=ARRAYFORMULA(TRUNC({1.1111,2.222},{1,2}))`

<a id="没有原生数组函数时arrayformula-或逐行填充"></a>
## When there is no native array function: ARRAYFORMULA or row-by-row filling

**Prerequisite: this section applies when the formula contains no native array function.** If the formula already contains a native array function (such as FILTER, XLOOKUP, MAP, etc.), array semantics automatically propagate through the entire formula's evaluation process (see the next section).

The following operations and functions **evaluate only as scalars**; feeding them an entire range directly does not expand item by item:

- Arithmetic operations: `+ - * / ^ %`
- Comparison operations: `= <> > >= < <=`
- Scalar math functions: `ABS ROUND INT TRUNC MOD LOG LN SQRT SIN COS TAN ...`
- Text functions: `LEN LEFT RIGHT MID UPPER LOWER TRIM TEXT VALUE ...`
- Date functions: `YEAR MONTH DAY DATE TIME EDATE EOMONTH ...`
- Conditional functions: `IF IFS IFERROR IFNA NOT ISNUMBER ISTEXT ISBLANK ...`
- Reference functions (high risk): `INDEX OFFSET COLUMN ROW MATCH`

**Two equivalent approaches, both faithful after exporting `.xlsx`; choose one as needed:**

- **`ARRAYFORMULA(<整个表达式>)`**: one formula covers the whole block, shorter to write. `=ARRAYFORMULA(A2:A100*B2:B100)` ✓, `=ARRAYFORMULA(IF(A2:A100>0,B2:B100,""))` ✓
- **Row-by-row scalar formula + fill**: write `=A2*B2` / `=IF(A2>0,B2,"")` in the first row, then use `--copy-to-range` to spread it across the entire column, with references incrementing by row. Each cell is an independent formula, so after export each cell can be edited individually in Excel

`MAP` is only usable when the LAMBDA body is a **pure operator or single-parameter function** (such as `=MAP(A2:A100,B2:B100,LAMBDA(a,b,a*b))`); if the body contains `IF`, a multi-parameter function, or string concatenation, switch to the two approaches above; for the reason, see core principle two at the beginning.

<a id="公式中有原生数组函数时整个公式已进入数组模式"></a>
### When a formula contains a native array function, the entire formula has already entered array mode

Lark's array semantics accumulate and propagate throughout the entire formula evaluation process: once a native array function runs, all subsequent operators and functions are also automatically processed element by element, no matter which layer they appear in.

Therefore the following forms work directly, with no need to wrap them in `ARRAYFORMULA` or split them into row-by-row fills:

- `=FILTER(A2:A10,B2:B10="x")+1` ✓
- `=XLOOKUP(E2:E10,A2:A10,B2:B10)*100` ✓
- `=ABS(FILTER(A2:A10,B2:B10>0))` ✓
- `=MAP(A2:A10,LAMBDA(x,x*2))-1` ✓

<a id="原生数组函数清单"></a>
## List of native array functions

The following functions work with array semantics and can directly return an entire block of results without being split into row-by-row fills; they also exist on the Excel side, so they can be used safely:

`CELL` `CHOOSECOLS` `CHOOSEROWS` `DROP` `EXPAND` `FILTER` `FREQUENCY` `GROWTH` `HSTACK` `LINEST` `LOGEST` `LOOKUP` `MINVERSE` `MMULT` `MUNIT` `RANDARRAY` `SEQUENCE` `SORT` `SORTBY` `SUMPRODUCT` `SWITCH` `TAKE` `TEXTSPLIT` `TOCOL` `TOROW` `TRANSPOSE` `TREND` `UNIQUE` `VSTACK` `WRAPCOLS` `WRAPROWS` `XLOOKUP`

`BYCOL` `BYROW` `MAKEARRAY` `MAP` `REDUCE` `SCAN` are also native array functions, but they are subject to core principle two — exporting `.xlsx` loses higher-order semantics, so by default switch to `ARRAYFORMULA` / row-by-row fill / helper columns.

`ARRAYFORMULA` is not in the list above — its role is to apply array semantics to expressions that **would otherwise be evaluated only as scalars**, rather than returning an array itself. When exporting `.xlsx`, it is translated into an Excel native array formula (`=ARRAYFORMULA(IF(A2:A6>2,B2:B6,""))` → `=IF(A2:A6>2,B2:B6,"")`, with the scope covering the entire block), fully preserving the semantics, so it can be used safely.

> **Note: `SWITCH` is treated as a native array function in Lark, which differs from Excel behavior — feeding a range to it expands it item by item.**

<a id="跨电子表格取数不要用公式"></a>
## Do not use formulas to fetch data across spreadsheets

Lark formulas have no general way to reference across workbooks (Excel external links do not carry over either). When you need data from another spreadsheet, first read that data out (`+csv-get`, etc.) into a sub-sheet of the current sheet, then compute within the current sheet using ordinary references — this both avoids the cross-sheet reference limitation and ensures the formulas remain usable after export.

<a id="index--offset--column--row--match-是高风险函数"></a>
## INDEX / OFFSET / COLUMN / ROW / MATCH are high-risk functions

This group of functions easily leads people to assume they will automatically spread multiple values out, but in Lark you cannot assume this.

**High-risk signals:**

- The row number / column number / offset is itself an array
- The result should originally be a row or a two-dimensional block
- There is an outer layer of arithmetic, comparison, `IF`, etc. that continues to process it

More reliable approaches: wrap the whole thing in `=ARRAYFORMULA(INDEX(...))` / `=ARRAYFORMULA(ROW(...))`; or fall back to a **scalar formula for the current row and fill downward** — write `=INDEX($A$2:$A$100,ROW(A1))` in the first row, and when filling downward `ROW(A1)` automatically increments to 1, 2, 3…

**Exception:** If the return value is immediately consumed by an aggregate function, write it directly:

- `=SUM(INDEX(A1:B2,0,1))` ✓

<a id="excel-隐式逐项求值飞书里要拆辅助列"></a>
## Excel evaluates implicitly item by item; in Lark you need to split out helper columns

**Typical characteristics:**

- The outer layer is an aggregate such as `SUMPRODUCT`, `SUM`
- The inner layer uses functions such as `SUBTOTAL`, `INDIRECT`, `OFFSET` that are more oriented toward "single value / single reference"
- Excel carries the intermediate results into the calculation item by item
- Copying this directly into Lark often does not produce the same item-by-item semantics

The same category in essence also includes: `INDEX/INDIRECT/OFFSET` first returns ranges, and the outer layer then passes these ranges to range-aware functions such as `SUMIF`, `COUNTIF`, `AVERAGEIF`, `SUMIFS` — in Lark these outer functions do not automatically expand the inner ranges a second time.

In this case, move the "iteration" onto **helper columns**, in two steps:

```excel
辅助列首行（如 Z16）：=单行计算逻辑          # 例：=SUBTOTAL(103,INDIRECT("E"&ROW(E16)))
                        用 --copy-to-range 铺满 Z16:Z387（引用随行递增）
汇总格：              =SUM(Z16:Z387)         # 需要时可隐藏辅助列
```

The helper columns are all ordinary scalar formulas, and after exporting `.xlsx` they are preserved cell by cell exactly as they are, also avoiding the export pitfalls of `LAMBDA`-family higher-order functions.

**Exception: when the result needs to update with filtering, keep a single formula.** The point of `SUBTOTAL` is to recalculate after the filter changes; for this kind of requirement, write

```excel
=SUMPRODUCT(MAP(ARRAYFORMULA(ROW($E$16:$E$387)),LAMBDA(row,SUBTOTAL(103,INDIRECT("E"&row)))))
```

The filter state itself is not preserved when exporting `.xlsx`, so this scenario is Lark-only and is not subject to the export constraint of core principle two.

Other scenarios of the same kind use helper columns:

- `INDIRECT("A"&ROW(...))`
- `OFFSET(...,ROW(...)-ROW(...),...)`
- `SUBTOTAL(...)`
- `SUMIF(内层返回范围, ...)`
- `COUNTIF(内层返回范围, ...)`
- `SUMIFS(内层返回范围, ...)`
- Any pattern that "wants to compute once for each row / each column"

<a id="多层范围结果与三维以上结果"></a>
## Multi-layer range results and results of three or more dimensions

Lark formula results can only be two-dimensional ranges, not "arrays of arrays".

<a id="多层范围不能自动二次展开"></a>
### Multi-layer ranges cannot be automatically expanded a second time

When the inner `INDEX/INDIRECT/OFFSET` returns a two-dimensional range and the outer layer still wants to perform range calculations on these ranges, do not assume Lark will "expand one more layer". Instead, use helper columns to compute row by row and then aggregate (see the previous section); do not compress the second expansion into a single array formula.

<a id="真正的三维或更高维结果不能直接返回"></a>
### Truly three-dimensional or higher-dimensional results cannot be returned directly

Typical triggering scenarios: wanting to merge and display results from multiple different ranges or different conditions, for example:
- Applying FILTER separately to column A, column B, and column C, and wanting to display the three columns of results side by side
- Generating data rows separately for multiple months, and wanting to stack all months vertically

Lark cannot directly return "a collection of multiple ranges"; you must first decide how to reduce the dimensions:

- Stack vertically: `=VSTACK(slice1, slice2, slice3)`
- Concatenate horizontally: `=HSTACK(slice1, slice2, slice3)`
- Flatten into a single column: `=TOCOL(...)`
- Flatten into a single row: `=TOROW(...)`
- Keep only aggregate values: place each slice into a helper area separately, then summarize with ordinary aggregate functions such as `SUM` / `SUMPRODUCT` (`REDUCE` is subject to core principle two; do not use it)

Do not "secretly decide" the display method for the third dimension on the user's behalf; if the user has not clearly stated how to display it, at least first rewrite the result into a visible two-dimensional shape.

<a id="不能机械照抄的-excel-语法"></a>
## Excel syntax that cannot be copied mechanically

<a id="-隐式交叉"></a>
### `@` implicit intersection

Excel: `=@A1:A10` (forces a single value, taking the value corresponding to the current row)

Lark does not have the `@` operator. Lark ordinary formulas already have projection semantics by default for referenced ranges, so just remove `@`:

- Excel: `=@A1:A10`
- Lark: `=A1:A10`

### `#` spill range

Excel: `=A1#` (references the entire range spilled by the formula in A1)

Lark does not have this syntax; migration approaches:

- Spill range known → change it to an explicit range
- Spill range unknown → go back to the source formula and rewrite it, or use `TAKE` / `DROP` to extract

<a id="结构化引用"></a>
### Structured references

Excel: `=SUM(Table1[Amount])`

Lark does not support structured references; change them to explicit A1 ranges: `=SUM(A2:A100)`

<a id="老式-cse-花括号"></a>
### Old-style CSE curly braces

Excel: `{=A1:A10*B1:B10}` (entered with Ctrl+Shift+Enter)

In Lark, change it to: `=ARRAYFORMULA(A1:A10*B1:B10)` — after exporting `.xlsx` it is restored exactly to Excel's CSE array formula; or write `=A1*B1` in the first row and fill downward

<a id="日期序列与日期差"></a>
## Date serials and date differences

Lark date serials: `0 = 1899-12-30`, `1 = 1899-12-31`, with no Excel 1900 leap year compatibility issue.

**Incorrect forms (do not use):**

- `=DAY(B2-A2)` ✗ — the difference is treated as a date serial number and then split into fields
- `=MONTH(B2-A2)` ✗
- `=YEAR(B2-A2)` ✗

**Correct forms:**

- Day difference: `=DAYS(B2,A2)` or `=DATEDIF(A2,B2,"D")` or `=B2-A2`
- Month difference: `=DATEDIF(A2,B2,"M")`
- Year difference: `=DATEDIF(A2,B2,"Y")`
- Workday difference: `=NETWORKDAYS(A2,B2)`

<a id="飞书不支持的函数"></a>
## Functions not supported by Lark

> This section is the **sole authoritative list** of "functions not supported by Lark". The following functions do not exist in Lark or are disabled; do not use them proactively; if the user explicitly requests them, refuse and provide alternatives:

- `STOCKHISTORY` — real-time stock data; Lark has no equivalent function, so data must be imported manually
- `WEBSERVICE` — external HTTP requests; Lark has no equivalent function
- CUBE family (`CUBEVALUE`, `CUBEMEMBER`, `CUBESET`, `CUBERANK`, etc.) — OLAP cube functions, not supported by Lark
- Google-specific functions such as `GOOGLEFINANCE`, `GOOGLETRANSLATE` — no equivalent functions
- `FORECAST.ETS` family (`FORECAST.ETS`, `FORECAST.ETS.STAT`, etc.) — not supported by Lark
- `INFO`, `RTD` — system information / real-time data functions, not supported by Lark
- `PIVOT` — replace with the `+pivot-{create|update|delete}` pivot table object
- `AMORDEGRC`, `PHONETIC`, `DETECTLANGUAGE` — not supported by Lark
- `LET`, named custom functions (LAMBDA defined in Name Manager), standalone calls to `LAMBDA` (such as `=LAMBDA(x,x+1)(5)`) — will report `#NAME?`; switch to nested IF / helper columns. **Exception**: `LAMBDA` is **supported** by Lark when used as an inline parameter of `MAP` / `REDUCE` / `BYROW` / `BYCOL` / `SCAN` / `MAKEARRAY`, but it is subject to core principle two (exporting `.xlsx` loses higher-order semantics), so by default still use row-by-row fill / helper columns

<a id="代表性改写示例"></a>
## Representative rewrite examples

- Basic item-by-item calculation
  - Excel: `=A2:A100*B2:B100`
  - Lark: `=ARRAYFORMULA(A2:A100*B2:B100)`; or first row `=A2*B2` + `--copy-to-range` filled downward
- Conditional judgment
  - Excel: `=IF(A2:A100>0,B2:B100,"")`
  - Lark: `=ARRAYFORMULA(IF(A2:A100>0,B2:B100,""))`; or first row `=IF(A2>0,B2,"")` + fill downward (the LAMBDA body contains `IF`, so `MAP` cannot be used)
- Native array function (no change needed)
  - Excel: `=FILTER(A2:C100,B2:B100="East")`
  - Lark: `=FILTER(A2:C100,B2:B100="East")`
- Native array function + scalar operation (no change needed; array semantics propagate automatically)
  - Excel: `=XLOOKUP(E2:E10,A2:A10,B2:B10)*100`
  - Lark: `=XLOOKUP(E2:E10,A2:A10,B2:B10)*100`
- High-risk reference functions
  - Excel: `=INDEX(A1:D2,{2,1},0)`
  - Lark: `=ARRAYFORMULA(INDEX(A1:D2,{2,1},0))` (`col_num=0` taking an entire row must be wrapped in `ARRAYFORMULA` to work; writing it bare reports `#VALUE!`)
- Date difference
  - Incorrect: `=DAY(B2-A2)`
  - Recommended: `=DAYS(B2,A2)` or `=DATEDIF(A2,B2,"D")` or `=B2-A2`
- Excel implicit item-by-item evaluation
  - Excel: `=SUMPRODUCT(SUBTOTAL(103,INDIRECT("E"&ROW($E$16:$E$387))))`
  - Lark: `=SUMPRODUCT(MAP(ARRAYFORMULA(ROW($E$16:$E$387)),LAMBDA(row,SUBTOTAL(103,INDIRECT("E"&row)))))` (`SUBTOTAL` needs to update with filtering, so keep a single formula)
- Multi-layer ranges / second expansion
  - Incorrect approach: `=SUMIF(INDIRECT("E"&ROW($E$16:$E$387)),">0")`
  - Lark: helper column `Z16` writes `=SUMIF(INDIRECT("E"&ROW(E16)),">0")` and fills downward to `Z387`
- Three dimensions reduced to two (keeping all layers)
  - Lark: `=VSTACK(slice1,slice2,slice3)` or `=HSTACK(slice1,slice2,slice3)`
- Three dimensions reduced to two (keeping only aggregate values)
  - Lark: after each slice is placed into a helper area, `=SUM(辅助区域)` (do not use `REDUCE`)
