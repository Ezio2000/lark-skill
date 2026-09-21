# Sheets

Read the operation reference before issuing its write commands. Load formula/style guidance only when that task needs formulas/styles, not for every read.

## Routing

| Intent | Commands | Reference |
|---|---|---|
| Values/CSV or full cell data | `+csv-get`, `+cells-get` | [Read](references/lark-sheets-read-data.md) |
| Typed values, formulas, styles, cell images | `+table-put`, `+cells-set`, `+cells-set-style`, `+cells-set-image` | [Write](references/lark-sheets-write-cells.md) |
| Workbook creation/import/export and tabs | `+workbook-*`, `+sheet-*` | [Workbook](references/lark-sheets-workbook.md) |
| Physical rows/columns, freeze, dimensions | `+dim-*`, sheet metadata | [Structure](references/lark-sheets-sheet-structure.md) |
| Sort/copy/clear/merge/resize | Range/cell shortcuts | [Ranges](references/lark-sheets-range-operations.md) |
| Charts | `+chart-create-basic`, `+batch-chart-create`, data/config updates | [Charts](references/lark-sheets-chart.md) |
| Grouped aggregation | `+pivot-create` | [Pivot](references/lark-sheets-pivot-table.md) |
| Data-driven highlighting | `+cond-format-create` | [Conditional format](references/lark-sheets-conditional-format.md) |
| Existing-table visual formatting | `+styles-put` | [Styles](references/lark-sheets-styles-put.md) |
| Search/replace | `+cells-search`, `+cells-replace` | [Search](references/lark-sheets-search-replace.md) |

## Preserve semantics and structure

- Modify only requested cells/structure. Resolve unknown tabs via `+workbook-info`, not guessed `Sheet1`. When unspecified, choose a unique visible grid sheet; multiple candidates need resolution. "Every sheet" requires enumerating the complete workbook.
- Numeric quantities/percentages/counts and computational dates need typed values; percent 40% is `0.4` plus number format. IDs, leading zeros, date labels, and numeric-looking text need text/object dtype, not untyped CSV.
- Prefer formulas for values expected to recalculate; preserve an explicit user request for static results. Read [formula generation](references/lark-sheets-formula-translation.md) and [verification](references/lark-sheets-formula-verify.md). Check units, threshold inclusivity, source range, blanks, and boundary cases.
- Formula validation must inspect the written ranges. Split partial checks; ordinary formulas need successful compilation/runtime results and representative expected values. If formulas cannot be made to work, report the limitation before changing the deliverable to static values unless that fallback was authorized.
- Native `=AI(prompt, range)` suits independent row-wise NLP when acceptable for the task. Write formulas in batches, inspect a seed formula, then use `+formula-verify --ai-only` for asynchronous status, not repeated cell polling. Report pending work; zero failed results is not proof every row has finished. Returned counts may cover more than the requested range.
- Physical insertion uses `+dim-insert --inherit-style before|after`; extending into blank cells uses `+range-copy --paste-type formats` before values. Also inspect row heights, column widths, and merges as relevant.
- Sort with `+range-sort` over the whole record width; do not simulate it by overwriting CSV. Delete rows/columns with `+dim-delete`; clear only contents/formats with clear commands.
- Dynamic highlighting uses conditional formatting; static annotations use styles. Preserve user-specified font versus fill intent. Check created rules and representative result styles.
- Verify the requested values/formulas/styles/objects at representative first/middle/last locations and named targets. Strip annotated CSV `[row=N]` prefixes before writing. Report missing sourced data at actual cell addresses; do not invent external facts.

## Locator and payload contract

Most sheet-specific shortcuts require both XOR pairs:

1. `--url` or `--spreadsheet-token`.
2. `--sheet-id` or `--sheet-name`.

Use plain A1 ranges such as `A1:B2`; a sheet prefix inside the range does not replace a locator. Quote literal `!` safely in POSIX shells.

Read each shortcut's flag declaration for exceptions: workbook-level/batch commands and `+table-put` may not accept sheet locators; new workbook creation/import accepts no existing locator; export supports only `--sheet-id`; pivot creation has optional target-sheet locators.

- Boolean values use `--flag=true|false`, not a space-separated value.
- Composite JSON shape: `--print-schema --flag-name <name-or.dotted.path>` prints locally, without other required flags. The schema may omit an outer envelope required by the flag description.
- Charts offer `--print-example <type>`. Prefer semantic chart shortcuts; use advanced properties only when necessary and submit minimal patches.
- File-capable flags accept cwd-relative `@./payload.json` or `-` for stdin. Only one flag can consume stdin. Use UTF-8 files for large/complex payloads and non-POSIX shells; do not transplant bash heredocs into PowerShell/cmd.
- `--dry-run` prints without calls. High-risk writes/deletions/rollback require `--yes`, implementing existing exact authorization rather than another confirmation ritual.
- Responses use `{ok, identity, data, ...}`; writes do not automatically read back.

Filters and named filter views are separate objects. Sparklines are objects, not the unsupported `SPARKLINE()` formula. Cell images differ from floating images. History rollback is asynchronous; changesets cover at most 20 revisions. Load their references only when applicable.

## Operation references

- [sheets visual standards](references/lark-sheets-visual-standards.md)
- [sheets batch update](references/lark-sheets-batch-update.md)
- [sheets filter](references/lark-sheets-filter.md)
- [sheets filter view](references/lark-sheets-filter-view.md)
- [sheets sparkline](references/lark-sheets-sparkline.md)
- [sheets float image](references/lark-sheets-float-image.md)
- [sheets history](references/lark-sheets-history.md)
- [sheets changeset](references/lark-sheets-changeset.md)
- [index](../shared/index.md)
- [shared high risk approval](../shared/references/lark-shared-high-risk-approval.md)
