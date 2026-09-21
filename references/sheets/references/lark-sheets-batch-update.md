# Lark Sheet Batch Update

<a id="写入边界--回读校验"></a>
## Write boundaries + read-back verification

`+batch-update` packs multiple writes into a single request, but each sub-operation should still be handled according to the scope and read-back recommendations for edit-type tasks:

1. **The target range should fall within the user-authorized scope**: apart from the areas the user explicitly wants to modify, sub-operations should avoid expanding into unrelated cells / columns / Sheets. When planning ranges, first confirm the boundaries of each sub-operation.
2. **Verify per sub-operation after the batch completes**: cell writes/clears → `+cells-get`/`+csv-get`; object CRUD → the corresponding `+*-list`; sheet CRUD → `+workbook-info`; size/hide/freeze/group/merge → `+sheet-info`; for states with no read-back interface, such as gridline visibility, confirmation from the sub-operation's return is sufficient. At minimum cover the first, middle, last, and user-named items; do not just do a uniform cells sampling.
3. **Assert expected counts up front**: when "batch-fill N rows" or "write to M ranges separately" is involved, it is recommended to hard-code N and M into the code first, then compare actual vs. expected after read-back; if they do not match, prioritize sending another round of `+batch-update` to fill the gaps, and if the gaps cannot be filled, list them in the delivery notes.
4. **Three hard tool constraints**: `--yes` is mandatory (high-risk-write; without it, exit code 10); a single call ≤100 operations, split into batches if exceeded; batch-type shortcuts such as `+cells-batch-set-style` / `+cells-batch-clear` cannot be embedded in operations (they are themselves batch atomic operations, so call them directly at the top level).

If any sub-operation of this `+batch-update` wrote a formula, copied a formula template, or imported a data block containing formulas, then in addition to read-back you must run `+formula-verify --exit-on-error` segment by segment over this formula range; `partial` splits and continues scanning, and it is complete only after all segments are `status='success'`. `+batch-update` only guarantees that write actions execute in order; it does not guarantee zero-error formula results. For AI formulas, switch to `+formula-verify --ai-only` and deliver according to the rule in `references/lark-sheets-formula-verify.md` of one asynchronous status check over the entire range (fix `failed` / `unsupported` first; only pending may be delivered, with a note that background computation is still in progress).

<a id="使用场景"></a>
## Use cases

Writes. Merge multiple write operations that are **cross-type and order-dependent** into a single request executed in order (e.g., insert column → write header → backfill data). Note: nested `+batch-update` is not supported.

**Route first, then act (choose the entry point by operation combination)**: beautification finishing touches (any combination of styles / merges / row height and column width / freeze) → a single `+styles-put` (declarative spec, see `references/lark-sheets-styles-put.md`); do not assemble a `--operations` sub-operation array; **the same write operation** targeting multiple ranges → use that command's own plural form (`+cells-set --writes` / `+cells-batch-clear` / `+dim-delete --ranges` / the map form of resize, etc.); only use this command for operation chains that are cross-type and order-dependent.

**⚠️ Scenarios where `+batch-update` should be preferred**:
- When you need to insert rows/columns before writing data (`+dim-{insert|delete|hide|unhide|freeze|group|ungroup}` + `+cells-set`)
- When you need to perform **different types** of write operations on multiple ranges (e.g., the combination of `+cells-set` + `+cells-clear`). For the same write operation targeting multiple ranges, use that command's own plural form; for multi-range merge, use `+styles-put`'s `cell_merges`; for large-scale unmerge, call it directly in a single call—all of these are covered by the routing above and do not go through this command

**For multiple mutually independent chart tasks, prefer `+batch-chart-create` / `+batch-chart-update`**; only when charts and other writes have order dependencies within the same batch should chart shortcuts be placed into `+batch-update`.

**Write shortcuts that cannot be placed into `--operations`** (the `shortcut` enum does not include them; forcing them in will be rejected by validation): `+cells-set-image` (requires local image upload), `+styles-put` / `+dropdown-update` / `+dropdown-delete` / `+cells-batch-clear` (they are already batch entry points and cannot be nested again), `+dim-move`. These operations must be called separately outside `+batch-update`.

**Batch row height and column width do not go here**: for different sizes across multiple rows / columns, use `+styles-put`'s `row_sizes` / `col_sizes` (can be in the same batch as styles), or the map form of `+rows-resize --heights` / `+cols-resize --widths` (see `references/lark-sheets-range-operations.md`); the map form cannot be embedded as a `--operations` sub-operation (within sub-operations you can still use the single-range form `range` + `height`/`width`).

**Execution semantics (fail-fast; which operations have already taken effect after a failure depends on the batch composition)**: by default, the first failed sub-operation interrupts the remaining operations. Whether prior sub-operations **have been persisted is not uniform**: pure cell / row-column structure writes only accumulate in memory before commit, and on failure nothing is persisted as a whole (equivalent to rollback); whereas object-type sub-operations such as charts / pivot tables **first commit the previously accumulated writes to disk and then create the object** during execution—when a batch contains such sub-operations, the parts completed before the failure (including the ordinary writes before them) have actually taken effect and cannot be rolled back. Therefore, after a failure, **do not assume "everything rolled back" or "everything retained"**: first look at the status of each sub-operation in the returned `results`, then read back the current state (row/column counts / target cells / object lists such as `+chart-list`) to confirm the set that has taken effect, and only resend the parts that have not taken effect—blindly resending the entire batch will re-apply operations that already took effect (such as inserting rows / creating charts), and blindly sending only the failed tail may write onto an old structure that has not taken effect. If `--continue-on-error` is passed, execution continues with the remaining operations even on failure, and the already-successful parts are retained (returning "N succeeded, M failed").

**Completion flow for formula-related batch processing**:
- Before writing: first read `references/lark-sheets-formula-translation.md` and rewrite the formula into Feishu-executable semantics.
- While writing: use `+batch-update` to complete the full set of actions such as inserting rows / writing formulas / copying templates in one go.
- After writing: read back the key formulas, and run `+formula-verify --exit-on-error` segment by segment over this formula range; complete only after all are success; for AI formulas, switch to `+formula-verify --ai-only` and deliver according to the rule in `references/lark-sheets-formula-verify.md` of one asynchronous status check over the entire range.

**`+dropdown-update` option modes (choose one of `--options` / `--source-range`) + color rules** (updating rewrites the complete validation rule; if existing colors need to be preserved, first read back and pass through `--colors`) see the "Dropdown options + colors" section of [`references/lark-sheets-write-cells.md`](lark-sheets-write-cells.md); this document does not repeat it. `+dropdown-delete` does not involve these flags.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+batch-update` | high-risk-write | Batch |
| `+batch-chart-create` | write | Batch |
| `+batch-chart-update` | write | Batch |
| `+dropdown-update` | write | Object |
| `+dropdown-delete` | high-risk-write | Object |
| `+cells-batch-clear` | high-risk-write | Batch |

## Flags

### `+batch-update`

_Common: URL/token (no sheet targeting) · System: `--yes`, `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--operations` | string + File + Stdin (composite JSON) | required | JSON array: [{"shortcut":"+xxx-yyy","input":{...}}, ...]. shortcut uses the CLI name; input is that shortcut's input set—it includes the sub-sheet targeting sheet_id (or sheet_name), but does not include the spreadsheet token/url (the latter is given only once at the top level via --url/--spreadsheet-token; +batch-update has no top-level --sheet-id); the keys of input are that shortcut's flags flattened into JSON (e.g., "range":"A11:B12"), not nested another layer. For basic flags check --help; for composite JSON flags check --print-schema --flag-name <flag>; do not manually fill in the operation field (it is automatically injected by the CLI according to the shortcut). Default fail-fast: the first failure interrupts the remaining operations; whether prior sub-operations have been persisted is **not uniform** (pure cell/structure writes are not persisted as a whole on failure, while object sub-operations such as charts/pivot tables commit accumulated writes to disk in advance and cannot themselves be rolled back), so after a failure do not assume full rollback or full retention—first look at results, then read back the current state to confirm the set that has taken effect, and only resend the parts that have not taken effect; passing --continue-on-error continues on failure and retains the already-successful parts; nesting is not supported; executed serially in array order |
| `--continue-on-error` | bool | optional | Whether to continue executing the remaining operations when a sub-operation fails; default false (the first failure interrupts the entire batch) |

### `+batch-chart-create`

_Common: URL/token (no sheet targeting) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--operations` | string + File + Stdin (composite JSON) | required | JSON array of chart creation operations; each item directly fills in `+chart-create-basic`'s flags and the target sheet targeting, without nesting `shortcut` / `input` again. The CLI internally always uses `+chart-create-basic`. Partial failure is allowed by default; successful charts are retained and only failed items are retried |
| `--continue-on-error` | bool | optional | Whether to continue after a single chart fails; default true |

### `+batch-chart-update`

_Common: URL/token (no sheet targeting) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--operations` | string + File + Stdin (composite JSON) | required | JSON array of chart update operations; each item uses `+chart-config-update` or `+chart-data-update`, and input passes the corresponding command's flag set and the target sheet targeting. The CLI first reads each chart's current snapshot, then generates partial properties; partial failure is allowed by default |
| `--continue-on-error` | bool | optional | Whether to continue after a single chart fails; default true |

### `+dropdown-update`

_Common: URL/token (no sheet targeting) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--ranges` | string + File + Stdin (simple JSON) | required | JSON array of target ranges (at most 100, e.g., `["Sheet1!A2:A100","Sheet1!C2:C100"]`, with the prefix written bare without quotes); each item must carry a sheet prefix; the prefix must exactly match the sheet's real display name (including case), and sheet reference_id is not accepted |
| `--options` | string + File + Stdin (composite JSON) | xor | JSON array of dropdown options, for example `["opt1","opt2"]`. The server does not limit the number of options, nor the length of a single option; options containing commas are acceptable (they are automatically escaped when written). For a large number of options, it is recommended to use `--source-range` instead. |
| `--colors` | string + File + Stdin (simple JSON) | optional | Dropdown pill background colors, an RGB hex array. Updating rewrites the entire validation rule: if the user did not ask to reset the colors, first use `+dropdown-get` to read back and pass the existing `highlight_colors` back as this flag; omitting it rebuilds from the built-in 10-color palette. When the user explicitly requests new colors or the options have clear semantic coloring, choose light, low-saturation backgrounds to suit black text. The length may be shorter but not longer—over-length is intercepted by Validate (`--colors length (N) must not exceed dropdown source size (M)`), and unspecified items are filled by cycling through the built-in palette. Passing it alone takes effect; it is ignored when `--highlight=false`. |
| `--multiple` | bool | optional | Enable multiple selection. This flag only updates the validation rule and does not write selected values; when subsequently writing values with `+cells-set`, you must pass a `multiple_values` array, not a comma-joined `value` |
| `--highlight` | bool | optional | Dropdown pill background color highlight toggle. **Not passing = on** (colors cycle through the built-in 10-color palette); `--highlight=false` turns it off to get a pure white dropdown. Colors are overridden with `--colors`. |
| `--source-range` | string | xor | The dropdown source range for listFromRange mode, A1 notation + sheet prefix (e.g., `'Sheet1'!T1:T3`). Maps to server `data_validation.range`, and takes effect automatically together with server `data_validation.type='listFromRange'`. Choose one of this and `--options`: passing `--options` uses an inline list (type=list), passing this flag uses a range reference (type=listFromRange). The `--colors` length rule is unchanged (≤ the number of cells in the source range), and `--highlight` / `--multiple` behave the same. When `--highlight` is enabled and the number of cells covered by source exceeds 2000, the server will judge the dropdown as option-error (this is an unsupported combination); the CLI will give a warning in the returned result's `data.warnings`. To cancel, pass `--highlight=false`. |

### `+dropdown-delete`

_Common: URL/token (no sheet targeting) · System: `--yes`, `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--ranges` | string + File + Stdin (simple JSON) | required | JSON array of target ranges (at most 100, e.g., `["Sheet1!E2:E6"]`, with the prefix written bare without quotes); each item must carry a sheet prefix; the prefix must exactly match the sheet's real display name (including case), and sheet reference_id is not accepted |

### `+cells-batch-clear`

_Common: URL/token (no sheet targeting) · System: `--yes`, `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--ranges` | string + File + Stdin (simple JSON) | required | JSON array of target ranges (at most 100); each item must carry a sheet prefix (e.g., `["Sheet1!A2:Z1000","Sheet2!A2:Z1000"]`, with the prefix written bare without quotes); the prefix must exactly match the sheet's real display name (including case), and sheet reference_id is not accepted; cross-sheet is supported; performs the same scope of clearing on all ranges |
| `--scope` | string | optional | Clear scope enum: `content` (default, clears content only) / `formats` (clears format only) / `all` (clears content + format) (possible values: `content` / `formats` / `all`) |

## Schemas

> Composite JSON flag field quick reference (only top level + one level of nesting is listed). For deeper structures see `## Examples` below, or use `--print-schema` to read the complete JSON Schema (usage see "Common flag quick reference" and "Agent usage tips" in index.md).

### `+batch-update` `--operations`

_List of CLI shortcut operations to execute in batch, executed serially in declaration order; any failure interrupts immediately_

**Array items** (type object):
- `shortcut` (enum) — CLI shortcut name (not the underlying MCP tool name) [+cells-set / +cells-set-style / +cells-clear / +cells-merge / +cells-unmerge / +cells-replace / +csv-put / +dropdown-set / +dim-insert / +dim-delete / +dim-hide / +dim-unhide / +dim-freeze / +dim-group / +dim-ungroup / +rows-resize / +cols-resize / +range-move / +range-copy / +range-fill / +range-sort / +sheet-create / +sheet-delete / +sheet-rename / +sheet-move / +sheet-copy / +sheet-hide / +sheet-unhide / +sheet-set-tab-color / +sheet-show-gridline / +sheet-hide-gridline / +chart-create / +chart-update / +chart-delete / +chart-create-basic / +chart-config-update / +chart-data-update / +pivot-create / +pivot-update / +pivot-delete / +cond-format-create / +cond-format-update / +cond-format-delete / +filter-create / +filter-update / +filter-delete / +filter-view-create / +filter-view-update / +filter-view-delete / +sparkline-create / +sparkline-update / +sparkline-delete / +float-image-create / +float-image-update / +float-image-delete]
- `input` (object) — that shortcut's input set—includes the sub-sheet targeting sheet_id (or sheet_name)

### `+batch-chart-create` `--operations`


**Array items** (type object):
- `sheet_id` (string?) — target sub-sheet ID; choose one of this and sheet_name
- `sheet_name` (string?) — target sub-sheet name; choose one of this and sheet_id
- `chart_type` (enum) [column / bar / line / area / pie / scatter / combo / radar / bubble / waterfall / pareto]
- `data_range` (string)
- `header_range` (string?)
- `data_direction` (enum?) [row / column]
- `dim1_index` (integer?)
- `dim2_indexes` (oneOf?)
- `series_types` (oneOf?)
- `series_y_axes` (oneOf?)
- `key_index` (integer?) — 1-based index of the bubble chart's identifier/name dimension; default 1
- `x_index` (integer?) — 1-based index of the bubble chart's X value dimension; provided together with y_index
- `y_index` (integer?) — 1-based index of the bubble chart's Y value dimension; provided together with x_index
- `group_index` (integer?) — 1-based index of the bubble chart's optional grouping dimension
- `size_index` (integer?) — 1-based index of the bubble chart's optional bubble size dimension
- `title` (string?)
- `anchor_cell` (string?)

### `+batch-chart-update` `--operations`


**Array items** (type object):
- `shortcut` (enum) [+chart-config-update / +chart-data-update]
- `input` (object) — the flag set of the corresponding chart update shortcut; includes sheet_id or sheet_name, does not include spreadsheet token/url

### `+dropdown-update` `--options`

_List options_

**Array items** (type string):
- Scalar: string

## Examples

Common four-piece set: `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` (the first two are XOR; `+batch-update` itself does not enforce sheet-id, and sub-operations each carry their own).

### `+batch-update`

Example:

```bash
lark-cli sheets +batch-update --url "https://example.feishu.cn/sheets/shtXXX" --yes \
  --operations @ops.json

# ops.json (array<{shortcut, input}>, shortcut uses the CLI name):
# [
#   {"shortcut": "+dim-insert", "input": {"sheet_id":"...","position":10,"count":3}},
#   {"shortcut": "+cells-set",  "input": {"sheet_id":"...","range":"A11:B12","cells":[[{"value":"a"},{"value":"b"}],[{"value":"c"},{"value":"d"}]]}}
# ]
```

> ⚠️ **Sub-operation targeting rules**:
> - spreadsheet targeting (`--url` / `--spreadsheet-token`) is **given only once at the top level**; the `+batch-update` top level **has no** `--sheet-id` / `--sheet-name`, and passing them at the top level has no effect.
> - **Each sub-operation's sheet targeting `sheet_id` (or `sheet_name`) goes into its own `input`** (see each item in ops.json above).
> - The keys of `input` are that shortcut's flags **flattened** into JSON (`"range":"A11:B12"`, `"position":11`); do not wrap the whole set of `--operations` in another layer of nested JSON.

> **Common combination: insert column + write header + backfill entire column**—submit in one batch, do not split into N separate calls. Batch backfilling the same column **requires only one** `+cells-set` (range writes the entire column range, cells writes an N×1 matrix); no need to loop row by row.
>
> ```jsonc
> // Insert a new column before column C → write header C1 → backfill C2:C100, 99 rows total
> [
>   {"shortcut": "+dim-insert",
>    "input": {"sheet_name": "Sheet1", "position": "C", "count": 1}},
>   {"shortcut": "+cells-set",
>    "input": {"sheet_name": "Sheet1", "range": "C1:C100",
>              "cells": [[{"value":"score"}], [{"value":95}], [{"value":87}], /* ... 97 more rows ... */ ]}}
> ]
> ```

> **Multi-chart combination**: first complete all auxiliary data, then put each chart's input into `+batch-chart-create`; for each item, also record the exact header range, data direction, and expected series count. After the batch completes, call `+chart-list` once for each affected sheet. For batch corrections to existing charts, use `+batch-chart-update` instead.
>
> ```json
> [
>   {"sheet_name":"Sheet1","chart_type":"column","data_range":"'Sheet1'!A1:C10","title":"分类对比","anchor_cell":"F2"},
>   {"sheet_name":"Sheet1","chart_type":"line","data_range":"'Sheet1'!E1:G10","title":"趋势变化","anchor_cell":"F18"}
> ]
> ```
>
> ```bash
> lark-cli sheets +batch-chart-create --url "..." --operations @ops.json
> ```

### `+cells-batch-clear`

Clear multiple ranges at once (the server uses `+batch-update` batch submission, fail-fast; for failure handling see "Execution semantics" below); `--scope` is the same as `+cells-clear` (`content` / `formats` / `all`, default `content`), `high-risk-write` forces `--yes`:

```bash
# dry-run to see the clear range first
lark-cli sheets +cells-batch-clear --url "..." \
  --ranges '["sheet1!A2:Z1000","sheet2!A2:Z1000"]' --scope all --dry-run
# execute
lark-cli sheets +cells-batch-clear --url "..." \
  --ranges '["sheet1!A2:Z1000","sheet2!A2:Z1000"]' --scope all --yes
```

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute constraints

- `Validate`: `+batch-update`'s `--operations` must be valid JSON and a non-empty array; validate each sub-operation's required `shortcut` / `input` fields, and input keys must be within that shortcut's flag vocabulary (unknown keys raise an error and suggest the closest key plus the full key contract); **validation errors are aggregated and reported**—the first error of all sub-operations is returned at once, so fix them all and resend once; **nested `+batch-update` is forbidden**. `+cells-batch-clear`'s `--ranges` must be a JSON array, each item prefixed with sheet, and `high-risk-write` forces `--yes` or `--dry-run` (`--scope` defaults to `content`).
- `DryRun`: output each sub-operation's target API + request body template in order, without making any calls.
- `Execute`: execute serially in declaration order; fail-fast by default. On failure, already-succeeded sub-operations are not rolled back; first read back the current state by sub-operation type, and resend only the remaining subset starting from the failure; on success, also complete the above branching validation.
