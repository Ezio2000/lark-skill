# Lark Sheet Sparkline

<a id="真对象硬约束"></a>
## Real Object Hard Constraints

When the user requests "sparkline / trend line / in-cell chart", you **must** create a real sparkline object via `+sparkline-{create|update|delete}`. **Do not** substitute by concatenating text characters (such as `▁▂▃▅▇`) in a cell, or by using the `SPARKLINE()` formula function (which is disabled). The criterion: after delivery, `+sparkline-list` must be able to return that object.

<a id="使用场景"></a>
## Use Cases

Read and write sparkline objects. This reference covers 4 shortcuts:

| Operation need | Tool to use | Description |
|---------|---------|------|
| View existing sparklines | `+sparkline-list` | Get the sparkline's type, data source, and style configuration |
| Create/update/delete sparklines | `+sparkline-{create|update|delete}` | Perform write operations on sparklines |

Typical workflow: first read existing sparklines to understand the configuration → perform create/update/delete → **must read again to verify the result**.

**Common configuration mistakes (must pay attention)**:
- **Data source range must be precise**: The sparkline's data source range must correspond exactly to the actual data rows and columns; a range offset will cause incorrect chart display
- **Do not confuse with the SPARKLINE() formula**: Lark Sheets' `SPARKLINE()` formula function has been disabled; sparklines can only be created via the `+sparkline-{create|update|delete}` object approach
- **Win/loss / count sparklines are natively supported**: `config.type="win_loss"`—do not judge them as "unsupported" and take a detour just because the quick reference table does not list them
- **Must verify after creation**: Call `+sparkline-list` to confirm the sparkline configuration is correct

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+sparkline-list` | read | Object |
| `+sparkline-create` | write | Object |
| `+sparkline-update` | write | Object |
| `+sparkline-delete` | high-risk-write | Object |

## Flags

### `+sparkline-list`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--group-id` | string | optional | Filter by group_id |

### `+sparkline-create`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--properties` | string + File + Stdin (composite JSON) | required | JSON: `{config（共享样式配置）, sparklines（迷你图数组）}`; run `--print-schema` for the complete field structure |

### `+sparkline-update`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--group-id` | string | required | Target group id |
| `--properties` | string + File + Stdin (composite JSON) | required | JSON: `{config, sparklines}`; first read back with `+sparkline-list --group-id <id>` then patch; run `--print-schema` for the complete field structure |

### `+sparkline-delete`

_Common four-piece set · System: `--yes`, `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--group-id` | string | required | Target group id |

## Schemas

> Composite JSON flag field quick reference (only top level + one level of nesting listed). For deeper structures, see `## Examples` below, or use `--print-schema` to read the complete JSON Schema (usage see index.md "Common flag quick reference" and "Agent usage tips").

### `+sparkline-create` `--properties` / `+sparkline-update` `--properties`

_Sparkline properties for create/update/partial delete_

**Top-level fields**:
- `config` (object?) — Sparkline style configuration; sparklines with the same groupId share the same style { theme_type?: enum, non_num_show_as?: enum, empty_show_as?: enum, contain_hidden_cells?: boolean, series_color?: string, …13 items in total }
- `sparklines` (array<object>?) — Sparkline item list each: { sparkline_id?: string, position?: object, source?: string, source_range?: object }

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` (XOR) arranged at the top. Sparklines are managed with **two levels of id**—`group_id` selects the group (a group of sparklines of the same form shares type / style / data source mapping), and `sparkline_id` selects a specific item within the group. Note: this is not the same as the disabled `SPARKLINE()` formula function.

> **When you need to `+sparkline-list` first:**
> - `+sparkline-update`: **always** needed—get the `sparkline_id` of each item in the group, and fill it back into `properties.sparklines[i]`; the server uses it for mapping.
> - `+sparkline-delete`: `sparkline_id` **not** needed—the CLI only supports deleting the entire group by `--group-id` (this shortcut has no `--properties`).

### `+sparkline-list`

```bash
# List all sparkline groups in the entire sub-sheet
lark-cli sheets +sparkline-list --url "..." --sheet-id "$SID"

# Pin to a single group: return the sparkline_id of each item in that group (required for update)
lark-cli sheets +sparkline-list --url "..." --sheet-id "$SID" --group-id "grpA"
```

### `+sparkline-create`

> `--properties` has only two top-level fields: `config` (style shared within the group, such as `line_width` / `points` / `extremum_max` / `extremum_min`) and `sparklines` (sparkline item array). Each `sparklines[i]` item must contain `position` (target cell, `row` + `col`) + `source` (data A1 range, choose one of the two with `source_range`); at create time `sparkline_id` may be omitted and is generated by the system.

```bash
lark-cli sheets +sparkline-create --url "..." --sheet-id "$SID" --properties @sparkline.json
```

`sparkline.json` example (embed two rows of line sparklines in column F, with data from A2:E2 and A3:E3 respectively):

```jsonc
{
  "config": { "line_width": 2 },
  "sparklines": [
    {"position": {"row": 1, "col": "F"}, "source": "'Sheet1'!A2:E2"},
    {"position": {"row": 2, "col": "F"}, "source": "'Sheet1'!A3:E3"}
  ]
}
```

### `+sparkline-update`

> Two-step approach: first `+sparkline-list --group-id <id>` to get the current group's `sparkline_id` list, then construct `properties.sparklines[]`—**each item must carry `sparkline_id`**. To change only the style, you may pass only `properties.config` (without `sparklines`; the entire group's style is updated in overwrite mode).

```bash
# Assume +sparkline-list has returned group_id=grpA, with sparkline_id=sl_1 / sl_2 in the group
lark-cli sheets +sparkline-update --url "..." --sheet-id "$SID" --group-id "grpA" --properties '{
  "sparklines": [
    {"sparkline_id":"sl_1","source":"'Sheet1'!A2:A20"},
    {"sparkline_id":"sl_2","source":"'Sheet1'!B2:B20"}
  ]
}'
```

### `+sparkline-delete`

> The CLI only supports **deleting the entire group**: pass `--group-id` to delete all sparklines in that group. This shortcut has **no** `--properties`, so it cannot delete only a single item within a group (when the requirement is to "keep part of them", instead use `+sparkline-update` to rewrite that group's `sparklines` list, rather than delete). `--yes` or `--dry-run` is mandatory; first `--dry-run` to confirm the target group to delete.

```bash
# Delete the entire group
lark-cli sheets +sparkline-delete --url "..." --sheet-id "$SID" --group-id "grpA" --yes
```

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute Constraints

- `Validate`:
  - XOR common four-piece set; `+sparkline-{update,delete}` must `--group-id`.
  - **`+sparkline-update`**: When `properties.sparklines` is non-empty, each item must contain `sparkline_id` (CLI pre-check; the error message will point back to `+sparkline-list`, avoiding an unreadable rejection from the server); passing only `properties.config` (config-only update) is valid and does not trigger the sparkline_id check.
  - **`+sparkline-delete`**: Only accepts `--group-id` (delete the entire group); there is **no** `--properties`, so a single item within a group cannot be deleted.
  - `--properties` (only `+sparkline-create` / `+sparkline-update`) top level only accepts `config` (style shared within the group) and `sparklines` (sparkline item array); `+sparkline-create` requires each `sparklines[i]` to contain `position` and `source` (or `source_range`, choose one of the two).
  - `+sparkline-delete` mandates `--yes` or `--dry-run`.
- `DryRun`: Write operations output the "sparkline group request template about to be POST/PATCH/DELETE".
- `Execute`: After create/update, you must call `+sparkline-list --group-id <id>` to verify the config, item count, source, and position; after delete, list to confirm the target group no longer exists.
