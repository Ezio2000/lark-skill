# Lark Sheet Filter View

<a id="概念回顾"></a>
## Concept Review

A filter view is one of multiple independent filter configurations within a sheet. Each view holds its own `range` and `rules`, identified by an independent `view_id` (a 10-character random string). A sheet can have multiple views. A view's hidden rows take effect locally only when the user enters that view; they do not affect other collaborators, nor do they interact with any filter that may coexist on the same sheet.

`+filter-view-{create|update|delete}` handles CRUD (create / update / delete) of the view itself; a view's "enter / exit" (active state) is local state and is not part of the tool semantics.

<a id="使用场景"></a>
## Use Cases

Read and write filter view objects. This reference covers 4 shortcuts:

| Operation need | Tool to use | Description |
|---------|---------|------|
| View existing filter views | `+filter-view-list` | Get all views on a sheet (view name, range, rules) |
| Create / update / delete filter views | `+filter-view-{create|update|delete}` | Three independent shortcuts: create / update / delete |

Typical workflow: first read existing views to understand the configuration → perform create / update / delete → **you must read again to verify the result**.

**Common configuration mistakes (must pay attention)**:
- **The view range must cover the header row**: the view's range must start from the header row (e.g. `A1:F100`), and cannot include only data rows
- **Read before updating**: when the user says "adjust this view", first use `+filter-view-list` to fetch the target view's current rules, **change only the differing columns**, then write back
- **Multiple creates cannot reuse view_id**: to reuse, go through `update`; repeating `create` will produce a new view
- **Filtering does not support regular expressions**: Lark Sheets filters do not support regular expressions; passing in a regex will be treated as plain text

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+filter-view-list` | read | Object |
| `+filter-view-create` | write | Object |
| `+filter-view-update` | write | Object |
| `+filter-view-delete` | high-risk-write | Object |

## Flags

### `+filter-view-list`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--view-id` | string | optional | Filter by filter view reference_id (a match returns only a single view) |

### `+filter-view-create`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--properties` | string + File + Stdin (composite JSON) | required | Filter view rules JSON, containing `rules?` (array of column-level filter rules) and `filtered_columns?`. `range` and `view_name` are independent flags |
| `--range` | string | required | The cell range the filter view applies to (A1 notation, e.g. `A1:F1000`); takes precedence over the field of the same name in `--properties`; required for create, and must cover the header row |
| `--view-name` | string | optional | Filter view name; if not passed, the system assigns one automatically; takes precedence over the field of the same name in `--properties` |

### `+filter-view-update`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--view-id` | string | required | Target filter view reference_id |
| `--properties` | string + File + Stdin (composite JSON) | required | Filter view rules JSON, containing `rules?` and `filtered_columns?`; update is a full-group overwrite (first read back with `+filter-view-list`, then patch; passing an empty `rules: []` clears it). `range` and `view_name` are independent flags |
| `--range` | string | optional | The cell range the filter view applies to (A1 notation, e.g. `A1:F1000`); takes precedence over the field of the same name in `--properties`; omitting it on update means keeping the current range |
| `--view-name` | string | optional | Filter view name; if not passed on create, the system assigns one automatically; if not passed on update, the original name is kept; takes precedence over the field of the same name in `--properties` |

### `+filter-view-delete`

_Common four-piece set · System: `--yes`, `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--view-id` | string | required | Target filter view reference_id |

## Schemas

> Composite JSON flag field quick reference (only top level + one level of nesting is listed). For deeper structures, see `## Examples` below, or use `--print-schema` to read the full JSON Schema (for usage, see "Common flag quick reference" and "Agent usage tips" in index.md).

### `+filter-view-create` `--properties` / `+filter-view-update` `--properties`

_View properties for create / update_

**Top-level fields**:
- `view_name` (string?) — optional — ⚠️ already extracted as the independent flag `--view-name`; do not fill it in again inside this JSON (for the same name, the independent flag takes precedence)
- `range` (string?) — the cell range the view applies to (A1 notation) — ⚠️ already extracted as the independent flag `--range`; do not fill it in again inside this JSON (for the same name, the independent flag takes precedence)
- `rules` (array<object>?) — list of column-level filter rules, each item corresponds to the filter condition of one specific column each: { column_index: string, conditions: array<oneOf>, filtered_rows?: array<number> }
- `filtered_columns` (array<string>?) — optional

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` arranged at the top (XOR). `view_id` is a 10-character random string; each sheet can have multiple views.

### `+filter-view-list`

```bash
# List all filter views of a sheet
lark-cli sheets +filter-view-list --url "..." --sheet-id "$SID"

# Locate precisely by view_id
lark-cli sheets +filter-view-list --url "..." --sheet-id "$SID" --view-id vAbcde1234
```

### `+filter-view-create`

`--range` (required) / `--view-name` (optional) are independent flags; `rules` goes through `--properties`:

```bash
lark-cli sheets +filter-view-create --url "..." --sheet-id "$SID" \
  --view-name "活跃用户" --range "A1:F1000" \
  --properties '{"rules":[{"column_index":"C","conditions":[{"type":"number","compare_type":"greaterThan","values":[100]}]}]}'
```

**`conditions[].type` × `compare_type` values** (`type` determines the available `compare_type`; both are required):

| `type` | Available `compare_type` | `values` |
|---|---|---|
| `text` | `contains` / `doesNotContain` / `beginsWith` / `doesNotBeginWith` / `endsWith` / `doesNotEndWith` / `equals` / `notEquals` | String array |
| `number` | `equal` / `notEqual` / `greaterThan` / `greaterThanOrEqual` / `lessThan` / `lessThanOrEqual` / `between` / `notBetween` | Number (or numeric string) array; `between` / `notBetween` pass two boundaries |
| `multiValue` | `equal` / `notEqual` | String array (exact match of any one of the values) |
| `color` | `backgroundColor` / `foregroundColor` | Do not pass `values` (filter by cell color) |

> ⚠️ `text` uses `equals` / `notEquals` (**with s**), while `number` / `multiValue` use `equal` / `notEqual` (**without s**) — do not mix them up. For the full schema, run `+filter-view-create --print-schema --flag-name properties`.

> `--range` **must cover the header row** (e.g. `A1:F1000`), and cannot include only data rows; when `--view-name` has a duplicate name, the server automatically renames it.

### `+filter-view-update`

> ⚠️ update is a full-group overwrite (PUT semantics): `--properties` **must be passed**; any rules / filtered_columns not present in the request will be cleared. To keep existing rules, first read them back with `+filter-view-list`, then merge and write back. When `--range` changes, discarding existing filter rules is expected behavior (rules are bound to the current range). Repeating `+filter-view-create` will not reuse the view_id; it will produce a new view.

### `+filter-view-delete`

> ⚠️ Deleting an **existing** view is irreversible; when the target view_id **does not exist**, it returns success idempotently (without error). First use `--dry-run` to check the view_id and confirm.

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute Constraints

- `Validate`: XOR common four-piece set; `+filter-view-create` validates that the starting row of `--range` is the header (first row); `+filter-view-update` must first use `+filter-view-list` to confirm the view exists, and `--properties` must be passed (full-group overwrite); `+filter-view-delete` enforces `--yes` or `--dry-run`.
- `DryRun`: outputs the "view request template about to be POST/PATCH/DELETE", with zero network side effects; `--sheet-name` is generated as the `<resolve:Sheet1>` placeholder in the dry-run output.
- `Execute`: does not automatically read back after writing; after create/update you must call `+filter-view-list --view-id <id>` to compare range + rules; after delete, list to confirm the target view does not exist.
