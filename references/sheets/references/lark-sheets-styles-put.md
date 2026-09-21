# Lark Sheet Styles Put (+styles-put)

> **Purpose of this document**: The default entry point for the final beautification pass on an **existing** spreadsheet — styles / borders / merges / row heights and column widths / freeze are written as a single declarative spec and delivered in one call. Which **values** styles take (color schemes / font sizes / alignment / number format standards) is governed solely by `references/lark-sheets-visual-standards.md`; this document only covers **how to apply them**.
>
> **Boundaries (three-way routing, choose the entry point by operation combination)**: target is any combination of **styles / merges / row heights and column widths / freeze** → this command; **the same write operation** applied to multiple ranges (e.g. multi-range clear, batch dropdown) → use that command's own plural form (`--ranges` / map input); operation chain is **cross-type with sequential dependencies** (e.g. insert column → write header → backfill data) → `+batch-update`. The beautification pass does not need and should not assemble a `--operations` sub-operation array.

<a id="使用场景"></a>
## Use Cases

Write. Batch-apply visual specs to multiple sub-sheets of an existing spreadsheet: beautify a new sheet, unify formatting after adding summary rows, merge similar cells by group, adjust column widths and row heights, freeze headers. The entire spec is expanded into a single batch submission executed in order, and like `+batch-update` it is **fail-fast** — after a failure, no uniform assumption is made about which sub-operations have taken effect; read back to confirm first, then resend (semantics same as `references/lark-sheets-batch-update.md` "execution semantics").

⚠️ **After a failure, do not copy the `operations[N]` from the error message to continue sending**: that array is expanded by the CLI from `--styles` (adjacent `cell_styles` with the same style are further merged into a larger rectangle), its indices do not correspond to the spec items you wrote, and it is not something you can directly resend. The correct approach: read back the affected ranges (`+cells-get --include style` / `+sheet-info`) to confirm which have taken effect, then resend the parts that did not land. Styles / row heights and column widths / freeze are idempotent stamps (resending the whole spec has no side effects, and this is usually the simplest solution); only `cell_merges` requires picking out the parts that did not take effect and sending them separately.

**Vocabulary is isomorphic in three places**: the field vocabulary of `--styles` is completely identical to `+workbook-create --styles` (create new sheet with synchronized beautification) and `+table-put --styles` (write data with synchronized beautification) — learn `cell_styles` / `cell_merges` / `row_sizes` / `col_sizes` / `freeze` once and they apply in all three places. There are only two differences: this command acts on an **existing** spreadsheet (located by top-level `--url` / `--spreadsheet-token`), and the range of `cell_styles` is not limited to "the region written this time" and may point to any region in the sheet.

**Spec highlights**:

- Top-level `{styles:[...]}`, each item corresponds to one target sub-sheet; `name` must be a real sub-sheet name (if unsure, look it up first with `+workbook-info`; do not guess `Sheet1`).
- Each sub-sheet item is executed in a fixed order: `cell_merges` → `cell_styles` → `row_sizes` → `col_sizes` → `freeze`; style stamping is allowed to cover ranges that include merged regions (the merged-region restriction applies only to value writes; styles are unrestricted).
- `row_sizes` / `col_sizes` only need `{range, size}` (px, i.e. pixel dimensions; only `standard` / row `auto` require an explicit `type`). The size key is uniformly `size`.
- Add borders with the `border` shorthand: `{"style":"solid","color":"#DDDDDD"}` applies to all four sides; only when different sides need different styles do you use the full `border_styles` form.
- `freeze` uses `{rows:N, cols:N}` to freeze the first N rows / columns; 0 or omitted means that dimension is not frozen; freeze is a full-state override, all 0 (e.g. `{"rows":0}`) = unfreeze both axes, equivalent to `+dim-freeze --rows 0 --cols 0` (only in `+workbook-create` when creating a new sheet is all 0 meaningless and rejected by validation).

**Read-back verification**: after the entire spec executes successfully, sample-read the affected ranges per the editing guidelines (`+cells-get --include style` or `+sheet-info` to check merges / row heights and column widths / freeze) to confirm the key styles actually took effect.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+styles-put` | write | Batch |

## Flags

### `+styles-put`

_Common: URL/token (no sheet location) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--styles` | string + File + Stdin (composite JSON) | required | Visual spec JSON applied to an **existing** spreadsheet: top-level `{styles:[...]}`, each item corresponds to one target sub-sheet (`name` uses a real sub-sheet name), and at least one of `cell_styles` / `cell_merges` / `row_sizes` / `col_sizes` / `freeze` must be given. Field vocabulary is completely isomorphic to `--styles` of `+workbook-create` / `+table-put` (cell_styles uses A1 range + flat style fields; borders use the `border` shorthand {style,weight,color} for all four sides alike, and border_styles only when sides differ; row/col sizes use row/column ranges + size (px means pixels; type is only needed for standard/auto); merges use cell ranges; freeze uses `{rows:N, cols:N}` to freeze the first N rows/columns). The entire spec is expanded into a single batch submission (fail-fast: after a failure, no uniform assumption is made about what has taken effect; read back to confirm first, then resend); range is not limited to "the region written this time" and may point to any region in the sheet |

## Schemas

> Quick reference for composite JSON flag fields (only top level + one level of nesting). For deeper structures, see `## Examples` below, or use `--print-schema` to read the full JSON Schema (usage see index.md "Common flag quick reference" and "Agent usage tips").

### `+styles-put` `--styles`


**Array items** (type object):
- `cell_merges` (array<object>?) — Array of cell merge operations; range uses A1 cell ranges, merge_type defaults to all each: { merge_type?: enum, range: string }
- `cell_styles` (array<object>?) — Array of cell style operations; each item specifies a range with an A1 cell range, field names align with +cells-set-style each: { background_color?: string, border?: object, border_styles?: object, font_color?: string, font_family?: string, …14 items in total }
- `col_sizes` (array<object>?) — Array of column width operations; range uses column ranges such as A:C, giving size (px) means pixel column width (type may be omitted); when type is standard, no size is given each: { range: string, size?: number, type?: enum }
- `freeze` (object?) — Frozen rows and columns: rows = freeze the first N rows, cols = freeze the first N columns (0 or omitted = that dimension is not frozen) { cols?: integer, rows?: integer }
- `name` (string) — Sub-sheet name
- `row_sizes` (array<object>?) — Array of row height operations; range uses row ranges such as 1:3, giving size (px) means pixel row height (type may be omitted); when type is standard/auto, no size is given each: { range: string, size?: number, type?: enum }

## Examples

### `+styles-put`

Header beautification + merge by group + column widths + freeze first row, delivered in one go:

```bash
lark-cli sheets +styles-put --url "https://example.feishu.cn/sheets/shtXXX" --styles - <<'JSON'
{"styles":[{
  "name": "Sheet1",
  "cell_merges": [{"range":"A5:A8"},{"range":"A9:A12"}],
  "cell_styles": [
    {"range":"A1:F1","font_weight":"bold","background_color":"#1E5BC6","font_color":"#FFFFFF","horizontal_alignment":"center"},
    {"range":"A2:F30","border":{"style":"solid","color":"#DDDDDD"}}
  ],
  "row_sizes":  [{"range":"1:1","size":36}],
  "col_sizes":  [{"range":"A:C","size":120}],
  "freeze":     {"rows":1}
}]}
JSON
```

Multiple sub-sheets delivered in the same batch (one styles item per sub-sheet):

```bash
lark-cli sheets +styles-put --url "..." --styles - <<'JSON'
{"styles":[
  {"name":"明细","cell_styles":[{"range":"A1:H1","font_weight":"bold","background_color":"#F0F0F0"}],"freeze":{"rows":1}},
  {"name":"汇总","cell_styles":[{"range":"A1:D1","font_weight":"bold"}],"col_sizes":[{"range":"A:D","type":"pixel","size":140}]}
]}
JSON
```

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute Constraints

- `Validate`: `--styles` must be valid JSON and `styles` a non-empty array; each item's `name` is required, and at least one of `cell_merges` / `cell_styles` / `row_sizes` / `col_sizes` / `freeze` must be given; each item of `cell_styles` must have at least one style field; after expansion it is subject to the sub-operation count (100) and total cell budget constraints; exceeding the limit reports an error with splitting suggestions.
- `DryRun`: outputs the request template for each expanded sub-operation without making any calls.
- `Execute`: the entire spec is combined into a single batch request executed in order; fail-fast. The error lists the failed sub-operations and reasons, but the `operations[N]` in it are internal indices after CLI expansion (including `cell_styles` merges), do not correspond to the items in `--styles`, and cannot be used to continue sending by index directly — the error states this explicitly and tells you to read back first, then resend.
