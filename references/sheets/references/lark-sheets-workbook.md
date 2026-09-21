# Lark Sheet Workbook

<a id="sheet-结构变更保守化编辑类任务必做"></a>
## Conservative Sheet Structure Changes (Mandatory for Editing Tasks)

`+sheet-{create|delete|rename|move|copy|hide|unhide|set-tab-color}` changes the physical structure of the original sheet and is a high-side-effect action. Before executing, you must comply with the following:

1. **Deleting / renaming / hiding / moving original Sheets requires explicit user instruction**: Unless the user explicitly requests these operations, it is **forbidden** to perform delete / rename / hide / move on **already existing** Sheets without authorization. Creating new Sheets is allowed (to carry intermediate results or pivot table / chart objects), but you should prioritize adding columns to the right of the original sheet; only when the volume of intermediate results is large or would be confused with the original data should you create a new blank Sheet (same as R1).
2. **List the inventory before Sheet-level operations**: Before calling `+sheet-{create|delete|rename|move|copy|hide|unhide|set-tab-color}`, you must first call `+workbook-info` to list "all current Sheet names + visibility + row/column counts", then decide whether to operate. It is forbidden to skip listing the inventory and directly create / delete / rename.
3. **Confirm with the user before deleting / renaming**: Deletion is irreversible, and renaming will invalidate the data sources of other formulas / pivot tables / charts—before executing, you must confirm in your reply that "X will be deleted / renamed, affecting Y references".

<a id="使用场景"></a>
## Use Cases

Read and write. Manage workbook structure. This reference covers 14 shortcuts:

| Operation need | Tool to use | Description |
|---------|---------|------|
| View workbook structure | `+workbook-info` | Get metadata such as sub-sheet list, names, row/column counts, freeze positions |
| Get current revision | `+revision-get` | Get the current document revision (version number), usable as a version anchor for recover / undo / changeset review |
| Create new workbook (can prefill data) | `+workbook-create` | Create a new sheet from in-memory data (`--values` / `--sheets` typed) |
| Import local file as new sheet | `+workbook-import` | Import local `.xlsx` / `.xls` / `.csv` as a new Feishu spreadsheet |
| Export workbook to local | `+workbook-export` | Export as local `.xlsx` (whole workbook) or single sub-sheet `.csv` |
| Change workbook structure | `+sheet-{create|delete|rename|move|copy|hide|unhide|set-tab-color}` | Create/delete/move/rename/copy/hide sub-sheets, modify tab colors |
| Toggle sub-sheet gridline visibility | `+sheet-show-gridline` / `+sheet-hide-gridline` | Show / hide gridlines of a single sub-sheet |

Note:

- If the user request contains multiple actions, for example "first rename, then create a new worksheet", issue multiple calls in order to cover all actions
- When using `create`, if the user specifies a worksheet name, you should explicitly pass `sheet_name`; do not omit it and rely on default naming
- If `+workbook-info` returns `warning_message`, it means some `sheet_id` are no longer valid (deleted/renamed or input incorrectly); you should stop reusing these ids, and re-fetch the full structure without `sheet_ids` before continuing operations

**Common configuration errors (must pay attention)**:
- **Getting the structure is the first step**: Before any spreadsheet operation, you must first call `+workbook-info`; do not skip it and operate directly. The returned row/column counts and sub-sheet list are the basis for all subsequent operations
- **Do not write sheet_id incorrectly**: Obtain `sheet_id` precisely from the return value of `+workbook-info`; do not manually spell it or guess it from the URL
- **Unnamed grid target**: The default candidates are only the visible normal grids of `resource_type=sheet && is_hidden=false`; only a unique candidate is auto-selected, multiple candidates are matched by the table name/header/content given by the user, and if still not unique, ask. It is forbidden to use `index` or guess `Sheet1`; if the user explicitly names a hidden sheet, it can be operated, and bitable / `#UNSUPPORTED_TYPE` should switch to the corresponding product API.
- **xlsx acceptance trigger boundary**: Normal online delivery does not export. Only when the user explicitly requests local xlsx / download / print should you perform acceptance after exporting via `--output-path`; for local Excel input, directly verify the existing local file before import, and after importing online do not export back for verification. When triggering is allowed, confirm the file exists, can be reopened, and check formula error values, styles, and objects.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+workbook-info` | read | Workbook |
| `+sheet-list` | read | Workbook |
| `+revision-get` | read | Workbook |
| `+sheet-create` | write | Workbook |
| `+sheet-delete` | high-risk-write | Workbook |
| `+sheet-rename` | write | Workbook |
| `+sheet-move` | write | Workbook |
| `+sheet-copy` | write | Workbook |
| `+sheet-hide` | write | Workbook |
| `+sheet-unhide` | write | Workbook |
| `+sheet-set-tab-color` | write | Workbook |
| `+sheet-hide-gridline` | write | Workbook |
| `+sheet-show-gridline` | write | Workbook |
| `+workbook-create` | write | Workbook |
| `+workbook-export` | read | Workbook |
| `+workbook-import` | write | Workbook |

## Flags

### `+workbook-info`

_Common: URL/token (no sheet targeting) · System: `--dry-run`_

_Contains only common / system flags._

### `+sheet-list`

_Common: URL/token (no sheet targeting) · System: `--dry-run`_

_Contains only common / system flags._

### `+revision-get`

_Common: URL/token (no sheet targeting) · System: `--dry-run`_

_Contains only common / system flags._

### `+sheet-create`

_Common: URL/token (no sheet targeting) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--title` | string | required | New worksheet name |
| `--index` | int | optional | Insert position (0-based); when omitted, appended to the end |
| `--row-count` | int | optional | Initial row count (default 200, upper limit 50000) |
| `--col-count` | int | optional | Initial column count (default 20, upper limit 200) |
| `--type` | string | optional | New sub-sheet type: sheet (spreadsheet); default sheet (possible values: `sheet`) |

### `+sheet-delete`

_Common four-piece set · System: `--yes`, `--dry-run`_

_Contains only common / system flags._

### `+sheet-rename`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--title` | string | required | New name |

### `+sheet-move`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--index` | int | required | Target position (0-based) |
| `--source-index` | int | optional | Source position (0-based); optional for standalone calls, when not passed the CLI runtime automatically derives it from the current index of `--sheet-id` / `--sheet-name` in the workbook. However, it cannot be omitted within `+batch-update` (must be passed explicitly)—mid-batch, a structure query cannot be initiated to auto-derive it |

### `+sheet-copy`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--title` | string | optional | Copy name; when omitted, generated by the server |
| `--index` | int | optional | Copy insert position (0-based); when omitted, appended to the end |

### `+sheet-hide`

_Common four-piece set · System: `--dry-run`_

_Contains only common / system flags._

### `+sheet-unhide`

_Common four-piece set · System: `--dry-run`_

_Contains only common / system flags._

### `+sheet-set-tab-color`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--color` | string | required | Hex color value such as `#FF0000`; pass empty `""` to clear |

### `+sheet-hide-gridline`

_Common four-piece set · System: `--dry-run`_

_Contains only common / system flags._

### `+sheet-show-gridline`

_Common four-piece set · System: `--dry-run`_

_Contains only common / system flags._

### `+workbook-create`

_System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--title` | string | required | New spreadsheet title |
| `--folder-token` | string | optional | Target folder token; when omitted, placed in the cloud space root directory |
| `--values` | string + File + Stdin (simple JSON) | optional | untyped initial data, a JSON two-dimensional array (header merged into the first row): `[["列A","列B"],["alice",95]]`; values are written as-is, types are automatically recognized by Feishu (dates / numbers will land as text; to preserve types, switch to --sheets), using the same batched `+cells-set` as --sheets; pair with --styles to control formatting/color/merges/row-column sizes |
| `--sheets` | string + File + Stdin (composite JSON) | optional | typed table protocol JSON written after creating the sheet (same as +table-put): top-level `{"sheets":[...]}`, each array item is a sub-sheet `{name, start_cell?, mode?, header?, allow_overwrite?, columns:["colA","colB",...], data:[[...]], dtypes?:{colA:pandasDtype, ...}, formats?:{colA:numberFormat, ...}}` — `name` and the outer `sheets` array are both mandatory. Agents use `df_to_sheet(df, name)` of `scripts/lark_sheets_df.py` to convert a DataFrame into one item and then wrap it in `{"sheets":[...]}`. Mutually exclusive with --values; the new sheet's default sub-sheet is reused as the first sub-sheet, preserving date/number types. |
| `--styles` | string + File + Stdin (composite JSON) | optional | Visual processing operation JSON written at the same time as creating the sheet: top-level `{styles:[...]}`, each item corresponds to a target sub-sheet, contains `name`, and provides at least one of `cell_styles` / `row_sizes` / `col_sizes` / `cell_merges`. `cell_styles` uses A1 cell range + flat style fields (fields same as +cells-set-style, including number_format / color / alignment / border_styles); row/col sizes use row/column ranges + type/size; merges use cell range + optional merge_type. When paired with --sheets, the styles array length/order/name must correspond to --sheets.sheets; when paired with --values, provide only one styles item (its name is ignored). For the complete cell_styles field structure, run `+workbook-create --print-schema --flag-name styles`. |

### `+workbook-export`

_Common: URL/token (no sheet targeting) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--file-extension` | string | optional | Export file format; `csv` mode must be paired with `--sheet-id` (possible values: `xlsx` / `csv`) (default `xlsx`) |
| `--sheet-id` | string | optional | Required only in csv mode: specifies which sheet to export as CSV. This is a flag specific to `+workbook-export` and is unrelated to the sheet targeting of the common four-piece set (this shortcut does not accept common sheet targeting) |
| `--output-path` | string | optional | Local save path; when omitted, **only triggers and polls the export task, does not download the file** (returns file_token / status, convenient for later resumption). To write to disk, pass a specific path (such as `./out.xlsx`) or directory (such as `.`; the filename given by the server lands under that directory). Note: the corresponding `lark-cli drive +export --doc-type sheet` uses the three flags `--output-dir` / `--file-name` / `--overwrite` and downloads to the current directory by default—this wrapper combines them into a single `--output-path` to simplify common use cases, but does not download by default; if needed, you can also switch to `drive +export`. |

### `+workbook-import`

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--file` | string | required | Local file path (.xlsx / .xls / .csv) |
| `--folder-token` | string | optional | Target folder token; when omitted, imports to the cloud space root directory |
| `--name` | string | optional | Table name after import; when omitted, uses the local filename (without extension) |

## Schemas

> Composite JSON flag field quick reference (only lists top level + one level of nesting). For deeper structures, see `## Examples` below, or use `--print-schema` to read the complete JSON Schema (usage see index.md "Common flag quick reference" and "Agent usage tips").

### `+workbook-create` `--sheets`

_typed data for one or more sub-sheets, each array element is written to one sub-sheet; supports multiple DataFrames → multiple sub-sheets written at once_

**Array items** (type object):
- `name` (string) — Target sub-sheet name
- `start_cell` (string?) — Write start cell (A1 notation, such as "B2"), default "A1"
- `mode` (enum?) — overwrite (default): write the "header + data" block starting from start_cell; append: append data below the existing data of the sub-sheet (by default does not repeat the header) [overwrite / append]
- `header` (boolean?) — Whether to write a row of column name headers
- `allow_overwrite` (boolean?) — When false, if the write would land on non-empty cells, refuse to write to protect the original data (returns partial_success)
- `columns` (array<string>) — Array of column name strings, order corresponds one-to-one with the value of each row in `data`
- `data` (array<array<string|number|boolean|null>>) — Data rows; each row is an array, length must equal the number of `columns`
- `dtypes` (object?) — optional
- `formats` (object?) — optional

### `+workbook-create` `--styles`


**Array items** (type object):
- `cell_merges` (array<object>?) — Array of cell merge operations; range uses A1 cell range, merge_type defaults to all each: { merge_type?: enum, range: string }
- `cell_styles` (array<object>?) — Array of cell style operations; each item uses A1 cell range to specify the range, field names align with +cells-set-style each: { background_color?: string, border?: object, border_styles?: object, font_color?: string, font_family?: string, …14 items in total }
- `col_sizes` (array<object>?) — Array of column width operations; range uses column ranges such as A:C, giving size (px) means pixel column width (type can be omitted); when type is standard, no size is included each: { range: string, size?: number, type?: enum }
- `freeze` (object?) — Freeze rows and columns: rows = freeze the first N rows, cols = freeze the first N columns (0 or omitted = that dimension is not frozen) { cols?: integer, rows?: integer }
- `name` (string) — Sub-sheet name
- `row_sizes` (array<object>?) — Array of row height operations; range uses row ranges such as 1:3, giving size (px) means pixel row height (type can be omitted); when type is standard/auto, no size is included each: { range: string, size?: number, type?: enum }

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` (XOR) arranged at the top. `+workbook-info` uses only the first two; the `+sheet-*` series operates on a single worksheet and requires `--sheet-id` or `--sheet-name`.

### `+workbook-info`

Output contract: returns `sheets[]`, each containing `sheet_id` / `title` (worksheet display name; old payloads use `sheet_name`, when reading prefer `title`, and fall back to `sheet_name` if missing) / `index` / `resource_type` / `row_count` / `column_count` / `is_hidden`, as well as count fields `merged_cells_count` / `chart_count` / `pivot_table_count` / `float_image_count` (there is no `frozen_*` field; for freeze information, use `+sheet-info` to read). This is the first step in operating a Feishu spreadsheet—any subsequent sheet-level action requires first obtaining the sheet_id from here.

> **Sub-sheet type `resource_type`**: `sheet` (normal grid sub-sheet) / `bitable` (embedded Base sub-sheet) / `#UNSUPPORTED_TYPE` (other embedded sub-sheets not yet supported).
> - Grid-type operations (reading/writing cells / ranges / styles / CSV / filters / pivot / charts, etc.) **apply only to `sheet`**. Performing grid operations on `bitable` / `#UNSUPPORTED_TYPE` sub-sheets will be directly rejected with a clear error, no longer failing silently.
> - To operate on data in a `bitable` sub-sheet: that sub-sheet entry will carry two fields, `bitable_app_token` + `bitable_table_id`; directly use Base commands to operate, for example `lark-cli base +record-list --base-token <bitable_app_token> --table-id <bitable_table_id>` (the entire set of `lark-cli base` commands for record CRUD, fields, views, etc. are all available). Do not use sheets grid commands.
> - `bitable` / `#UNSUPPORTED_TYPE` sub-sheet entries **only contain** `sheet_id` / `sheet_name` / `index` / `resource_type` (bitable additionally adds the above two tokens) as well as `is_hidden` / `tab_color`; they **do not output** grid metrics such as `row_count` / `column_count` / `merged_cells_count` / `chart_count` / `pivot_table_count` / `float_image_count` / `frozen_*` (meaningless for non-grid sub-sheets).
> - tab management operations (`+sheet-rename` / `+sheet-move` / `+sheet-delete` / `+sheet-hide`, etc.) are legal for sub-sheets of any `resource_type` and are not subject to this restriction.

### `+revision-get`

Output contract: returns a single `revision` field, i.e. the current document version number. It is the version anchor for recover / undo / `+changeset-get`: if a read/write operation was just performed, you can also directly reuse the `revision` from that response; when you only want to fetch the current version number on its own and don't need other structural information, `+revision-get` is the most direct.

### `+workbook-create`

Create a new spreadsheet, optionally pre-filling data. Two data entry points (untyped `--values` / typed `--sheets` JSON) are **mutually exclusive**; choose one as needed—both go through the same batched write:

> ⚠️ **`--title` is required and will not be inferred from the data**: it is the name of this sheet in the cloud space; if omitted, it will fail before the sheet is created (`required flag(s) "title" not set`), and not a single row of data will be written. The sub-sheet name is written in the `name` field of `--sheets`; the two are entirely different things—`--title "2026年Q3销售分析"` pairs with `"name": "明细"` in `--sheets`.

```bash
# 1) untyped: --values (a two-dimensional array, with the header merged into the first row; values are written as-is and types are automatically recognized by Feishu,
#    dates will land as text; pair with --styles to control formatting)
lark-cli sheets +workbook-create --title "销售" \
  --values '[["门店","销售额"],["北京",259874]]'

# 2) typed JSON: --sheets (create the sheet + preserve types in one step). date columns land as real dates (sortable/pivotable),
#    number does not lose precision, string columns preserve leading zeros (e.g. order number 00123); multiple sub-sheets are created in one go.
lark-cli sheets +workbook-create --title "交易" --sheets '{
  "sheets":[
    {"name":"明细",
     "columns":["日期","金额","单号"],
     "dtypes":{"日期":"datetime64[ns]","金额":"float64","单号":"object"},
     "formats":{"金额":"#,##0.00"},
     "data":[["2024-01-15",1234.5,"00123"]]}
  ]}'
```

The `--sheets` protocol is completely isomorphic to `+table-put` (for field meanings see `+table-put` in lark-sheets-write-cells; large payloads go through stdin / `@file`). Key difference: **the default sub-sheet of a newly created workbook will be reused as the first sub-sheet** (renamed and then carrying the data), with no leftover empty `Sheet1`; the remaining sub-sheets are created as needed. It combines "create sheet + typed write", which `+table-put` cannot do on its own, into a single command, making it the first choice for "land a new sheet with real dates directly after pandas finishes computing". Use `+table-get` for read-back verification (isomorphic to `--sheets`, round-trippable).

> 💡 When a pandas DataFrame goes through `--sheets`, directly `from lark_sheets_df import df_to_sheet` ([`scripts/lark_sheets_df.py`](../scripts/lark_sheets_df.py), sharing the same helper as `+table-put`); the helper's advantage is even more obvious in multi-sub-sheet scenarios:
> ```python
> import sys; sys.path.insert(0, "scripts")  # when cwd is not at the skill root, change to the actual path of scripts/
> from lark_sheets_df import df_to_sheet
>
> payload = {"sheets": [df_to_sheet(income, "Income Statement"),
>                       df_to_sheet(balance, "Balance Sheet"),
>                       df_to_sheet(cashflow, "Cash Flow")]}
> ```

`--styles` can write visual treatments at the same time as creating the sheet and writing data. Like `--sheets`, it has only one outer form: a `styles` array in the top-level object; each item in the array corresponds to a sub-sheet, contains `name`, and is split by capability into four optional arrays:

- `cell_styles`: like `+cells-set-style`, using an A1 cell `range` plus flat style fields (`font_weight` / `background_color` / `horizontal_alignment` / `vertical_alignment` / `number_format`, etc.) and an optional `border_styles`; these styles are applied together with the content in the same write. Run `+workbook-create --print-schema --flag-name styles` for the complete fields.
- `cell_merges`: use an A1 cell `range` to set merging; `merge_type` defaults to `all`, with optional `rows` / `columns`.
- `row_sizes`: use a row range (e.g. `1:3`) to set row height; `type` is `pixel` / `standard` / `auto`; `pixel` requires `size`.
- `col_sizes`: use a column range (e.g. `A:C`) to set column width; `type` is `pixel` / `standard`; `pixel` requires `size`.

When the same cell matches multiple `cell_styles` items, later operations continue to merge and overwrite already-passed fields. `cell_merges` / `row_sizes` / `col_sizes` are executed in order after the content write.

```bash
# 3) untyped: still use {"styles":[...]}, with only one sub-sheet style item (name ignored); range covers the initial --values area
lark-cli sheets +workbook-create --title "销售" \
  --values '[["门店","销售额"],["北京",259874],["上海",198320]]' \
  --styles '{
    "styles":[
      {"name":"Sheet1","cell_styles":[
        {"range":"A1:B1","font_weight":"bold","background_color":"#f5f5f5","horizontal_alignment":"center","vertical_alignment":"middle"},
        {"range":"B2:B3","number_format":"#,##0"}
      ]}
    ]
  }'

# 4) typed single sub-sheet: --styles.styles[0].name must correspond to --sheets.sheets[0].name
lark-cli sheets +workbook-create --title "交易" --sheets '{
  "sheets":[
    {"name":"明细",
     "columns":["日期","金额"],
     "dtypes":{"日期":"datetime64[ns]","金额":"float64"},
     "formats":{"金额":"#,##0.00"},
     "data":[["2024-01-15",1234.5]]}
  ]}' --styles '{
    "styles":[
      {"name":"明细",
       "cell_styles":[
        {"range":"A1:B1","font_weight":"bold","background_color":"#f5f5f5",
          "border_styles":{"bottom":{"style":"solid","weight":"thin","color":"#000000"}}},
        {"range":"A2:A2","number_format":"yyyy-mm-dd"},
        {"range":"B2:B2","number_format":"#,##0.00","font_color":"#0f7b0f"}
       ],
       "cell_merges":[{"range":"A1:B1"}],
       "col_sizes":[{"range":"A:B","type":"pixel","size":120}],
       "row_sizes":[{"range":"1:1","type":"pixel","size":28}]}
    ]
  }'

# 5) typed multiple sub-sheets: the styles array and sheets array must match in length, order, and name
lark-cli sheets +workbook-create --title "经营看板" --sheets '{
  "sheets":[
    {"name":"收入","columns":["月份","收入"],"dtypes":{"收入":"int64"},"formats":{"收入":"#,##0"},"data":[["2026-05",1200000]]},
    {"name":"成本","columns":["月份","成本"],"dtypes":{"成本":"int64"},"formats":{"成本":"#,##0"},"data":[["2026-05",730000]]}
  ]}' --styles '{
    "styles":[
      {"name":"收入","cell_styles":[
        {"range":"A1:B1","font_weight":"bold","background_color":"#f0f7ff"},
        {"range":"B2:B2","font_color":"#0f7b0f"}
      ]},
      {"name":"成本","cell_styles":[
        {"range":"A1:B1","font_weight":"bold","background_color":"#fff7ed"},
        {"range":"B2:B2","font_color":"#b42318"}
      ]}
    ]
  }'
```

> ⚠️ **`+workbook-create` writes in-memory data as a new sheet; to import an existing local Excel/CSV file as-is into a new sheet, use `+workbook-import`** (see below), do not first read the file locally and then `+workbook-create` to reload it.

### `+workbook-import`

Import an existing local `.xlsx` / `.xls` / `.csv` file as a **new** Feishu spreadsheet (async task + built-in polling), symmetric with `+workbook-export` (export), always importing as the spreadsheet type.

```bash
# Import to the cloud space root directory; the sheet name defaults to the local file name (with the extension removed)
lark-cli sheets +workbook-import --file ./data.xlsx

# Specify the target folder and the sheet name after import
lark-cli sheets +workbook-import --file ./report.csv --folder-token <FOLDER_TOKEN> --name "月度报表"
```

- **Does not accept any spreadsheet / sheet locating flag** (it creates new, does not operate on an existing sheet): only `--file` (required) / `--folder-token` / `--name`.
- **`--file` only accepts relative paths within the current working directory**: first `cd` to the directory containing the file (or the workspace), then pass `./file.xlsx` / `data/file.xlsx`; passing absolute paths like `/home/.../file.xlsx`, `C:\...\file.xlsx` will be judged `unsafe file path` and rejected.
- After a successful import, hand off the new sheet link through the host's artifact delivery tool, and confirm that this call returned success; merely writing it into the reply body does not count as delivery.
- For local spreadsheet files → Feishu spreadsheets, always use this command; **do not** use `drive +import` to import spreadsheets—it is a general import outside of sheets and additionally requires specifying `--type`, which is a detour and more error-prone. Only when you want to import a local spreadsheet as a **bitable** should you switch to `lark-cli drive +import --type bitable`.
- Returns `token` / `url` / `ticket` / `ready` / `job_status`. Only `ready=true` and `job_status=0` count as import complete; then use the new URL to call `+workbook-info`, and if there is a named content contract, read back the key sheet/range. When `timed_out=true`, continue checking per `next_command`; it must not be delivered as success.
- **Values and formulas are preserved; layout is not**: after a round trip, values, formulas, number formats, merged areas, frozen panes, and dropdown validations are all preserved as-is; row heights and column widths, borders, theme-color fills (`fgColor theme=N`), and **cells that follow the workbook default font** (when the source sheet's default font is a Chinese font, such cells will fall back to the system default) will change, regardless of what was done this round. When the original layout must be preserved, after import write back the dimensions using `+rows-resize` / `+cols-resize` based on the source file's values (Feishu uses pixels, Excel row height uses points, conversion is about `px ≈ pt × 4/3`); other layout differences cannot be written back, so state them clearly in the delivery notes.
- Polling is done by the command itself: this command and other async shortcuts have built-in polling, and the status is already up to date when it returns; just rerun `next_command` directly, and there is no need and no reason to add `sleep` to wait.

### `+workbook-export`

Export a Feishu spreadsheet as a local `.xlsx` (entire workbook) or a single sub-sheet `.csv` (async task + built-in polling + optional download).

```bash
# 1) Only create and poll the export task, do not download (default): returns file_token / status for later resumption
lark-cli sheets +workbook-export --url "https://example.feishu.cn/sheets/shtXXX"

# 2) Download to a specific file name
lark-cli sheets +workbook-export --url "..." --output-path ./report.xlsx

# 3) Download to a directory (preserving the file name given by the server)
lark-cli sheets +workbook-export --url "..." --output-path ./downloads/

# 4) csv mode must pass --sheet-id (the API exports only one sub-sheet at a time)
lark-cli sheets +workbook-export --url "..." --file-extension csv --sheet-id "$SID" --output-path ./sheet.csv
```

> ⚠️ **Does not download by default**: when `--output-path` is omitted, only the export task is created and polled. Ordinary online delivery must not proactively export for internal verification; only when the user explicitly requests a local xlsx / download / print should you provide `--output-path` and accept it. During acceptance, confirm the file exists and can be reopened, and check formula error values, styles, and objects.
>
> **Relationship with `drive +export --doc-type sheet`**: this wrapper is a specialized encapsulation of it, fixing `--doc-type sheet`, and folding drive's three flags `--output-dir` / `--file-name` / `--overwrite` into a single `--output-path` to simplify common use cases. The cost is different defaults: `drive +export` downloads to the current directory by default, while this wrapper does not download by default. If you need fine control over directory/file name/whether to overwrite, fall back to `drive +export --doc-type sheet`.

### `+sheet-create`

Example:

```bash
lark-cli sheets +sheet-create --url "https://example.feishu.cn/sheets/shtXXX" \
  --title "汇总" --index 0
```

> 💡 `+sheet-create` only creates an **empty sub-sheet**. To create a sub-sheet in an existing workbook and write typed data and/or styles in one step, use `+table-put` (a sub-sheet named in the payload is automatically created if missing) together with its `--sheets` / `--styles`, saving the second round trip of first creating the sheet and then `+cells-set` / `+cells-set-style`.

### `+sheet-delete`

> ⚠️ Worksheet deletion is irreversible; first `--dry-run` to see the output sheet_id + title and confirm it is the one to delete.

### `+sheet-rename`

```bash
lark-cli sheets +sheet-rename --url "..." --sheet-id "$SID" --title "汇总"
```

### `+sheet-move`

The standalone path, when `--source-index` is missing / only `--sheet-name` is given, will automatically initiate a `+workbook-info` read to resolve them.

> ⚠️ **Calling `+sheet-move` within `+batch-update`**: you must explicitly pass `--sheet-id`, `--source-index`, and `--index` (the target position) at the same time. Structural queries cannot be initiated mid-batch, and `--index` will silently fall back to the default position 0 if not explicitly given, so the batch translator enforces that all three be explicit.

### `+sheet-copy`

```bash
# When --title is omitted, the server generates the copy name
lark-cli sheets +sheet-copy --url "..." --sheet-id "$SID" --title "副本"
```

> 💡 `+sheet-copy` copies the entire sheet including **formulas / merges / group background colors / column widths / conditional formatting**. When "batch-creating new sub-sheets with the same structure from an existing sub-sheet" (e.g. creating one isomorphic sub-sheet for each dataset based on a template), first `+sheet-copy` to copy the template and then use `+cells-*` to change only the data, which saves a great deal compared with `+sheet-create` from scratch + rebuilding formulas / styles, and naturally satisfies "formulas / groups / colors copied over". To merge local files / data into an **existing workbook** as a sub-sheet, go through it (or `+sheet-create`), and do not use `+workbook-import` / `+workbook-create`—those two only create independent sheets.

### `+sheet-hide` / `+sheet-unhide`

```bash
lark-cli sheets +sheet-hide   --url "..." --sheet-id "$SID"
lark-cli sheets +sheet-unhide --url "..." --sheet-id "$SID"
```

### `+sheet-set-tab-color`

```bash
# Hex color value; pass an empty string "" to clear the tab color
lark-cli sheets +sheet-set-tab-color --url "..." --sheet-id "$SID" --color "#FF0000"
```

### `+sheet-show-gridline` / `+sheet-hide-gridline`

```bash
# Toggle sub-sheet gridline visibility; the two-state semantics are in the command name, no extra parameter needed (same as +sheet-hide/+sheet-unhide)
lark-cli sheets +sheet-show-gridline --url "..." --sheet-id "$SID"
lark-cli sheets +sheet-hide-gridline --url "..." --sheet-id "$SID"
```

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute constraints

- `Validate`: XOR the common four-piece set; `+sheet-create` validates that `--title` is non-empty, `--row-count` ≤ 50000, `--col-count` ≤ 200; `+sheet-delete` must be `--yes` or `--dry-run`; `--sheets` and `--values` of `+workbook-create` are **mutually exclusive**; if `--sheets` is given, validate the payload per the typed protocol (other constraints same as `+table-put`).
- `DryRun`: `+sheet-*` write operations output "the sheet metadata about to be PATCHed"; `--sheet-name` is generated in the dry-run output as the `<resolve:Sheet1>` placeholder, and is not actually resolved to a sheet-id.
- `Execute`: after sheet create/rename/move/copy/hide/unhide/delete, you must call `+workbook-info` to verify the name, order, visibility, and count by the stable sheet_id; import closes the loop per the ready/job_status + workbook-info above; export that requires a local file closes the loop per output-path + file existence/reopenability.
