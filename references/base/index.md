# Base

A Base is a data container with a resource-block tree: tables, dashboards, workflows, docx documents, and folders. Fields/records/views/forms are internal table objects, not Base blocks. Advanced permissions/roles are Base-level settings. Workspace contains Base and BaseApp; BaseApp organizes pages/components and is not a Base alias.

Use user identity by default; bot only when selected. Repair access under the same identity rather than silently switching.

## Resolve the entity

Use supplied structured resource IDs directly. Otherwise:

- URL/share link: `lark-cli base +url-resolve --url <url> --as user`; route by returned `resource_type`/`block_type` and actual coordinates.
- Existing Base title: `base +title-resolve --title <keyword>`; resolve multiple candidates using owner/time/context, asking if still ambiguous.
- Browse recent/owned/created Bases: [Drive](../drive/index.md) `+search --doc-types bitable`. Owner (`--mine`) and original creator (`--created-by-me`) differ.
- BaseApp: resolve its `/app/` URL or list `+workspace-entity-list --type baseapp` in a known Workspace. A Base token alone cannot substitute for an app token.
- [Template center](references/lark-base-template-center.md) is a public template catalog, not the user's existing Bases.

Create a new Base/first table/fields together with `+base-create --name <name> --table-name <name> --fields <array>`. Native whole-Base copying uses `+base-copy`. Local Excel/CSV/`.base` import/export belongs to Drive.

## Blocks and tables

`+base-block-list` discovers blocks. Create/rename/move/delete operate on that tree; moves use `--parent-id` and `--before-id`/`--after-id`. Table/dashboard/workflow block IDs are their respective resource IDs. Docx blocks carry a separate `docx_token`, used through [Documents](../doc/index.md).

Use `+table-list`/`+table-get` to find tables. Fields are stable by `field_id`, mutable by display name. Only fetch schema when needed for typed writes, filters, or relationships, not before every simple read.

- [Field create](references/lark-base-field-create.md) accepts multiple field objects; [field update](references/lark-base-field-update.md) routes formulas/lookups.
- [Field extensions](references/lark-base-field-extension.md) generate values into supported existing text/select/number fields.
- Table updates can become visible asynchronously. Use successful write output; if final verification is required, consolidate checks after related writes.

## Record values and queries

`record_id` is the stable unique key; the primary display field is not a database key.

| Intent | Command |
|---|---|
| Known record IDs | `+record-get --record-id <id>` (repeatable) |
| Keyword in specified fields | `+record-search --keyword <text> --search-field <field>` |
| Other reads | `+record-list`, optional `--filter-json` / `--sort-json` |
| Create | `+record-batch-create --json '{"create_records":[{"Name":"Task A"}]}'` |
| Update selected fields | `+record-batch-update --json '{"update_records":{"<record_id>":{"Name":"Task B"}}}'` |
| Delete | `+record-delete --record-id <id>` |
| Attachments | `+record-upload-attachment`, `+record-download-attachment`, `+record-remove-attachment` |

Supply base/table coordinates and explicit identity to these commands. Project needed fields with repeatable `--field-id`. For larger reads use NDJSON files (`--format ndjson --output ./records.ndjson`); check `records_count`, `has_more`, and offset. The default/maximum limit is 2,000; a limited preview is not a complete dataset.

Read [filters](references/lark-base-filter-condition.md) for tuple conditions. Text/select/link containment uses `intersects`; empty/nonempty conditions have no value. Dates use `ExactDate(...)` and Base timezone; do not assume numeric comparison operators all apply to dates. Read [query and analysis](references/lark-base-record-query-and-analysis-sop.md) for complete large-table/view reads, joins, multivalues, time series, and advanced analysis.

Cell values: text is string; number is numeric; checkbox is boolean; select is an array of existing option strings (single-select at most one); users/groups/links are arrays of `{"id":"..."}`; location is `{"lng":...,"lat":...}`; clear uses `null` (arrays may also use `[]`). Dates accept supported ISO/timezone forms or Unix milliseconds; unzoned text uses Base timezone. Use attachment shortcuts, not guessed attachment cell objects.

Created/updated timestamps/users, auto-number, formula, and lookup fields are read-only. Inspect `ignored_fields` rather than assuming every submitted field was written. Batch at most 200 records; serialize writes to one table to avoid `1254291`. Large JSON can use `@file.json`.

## Views and forms

Read [view lifecycle](references/lark-base-view.md) before modifying views. Views share table records; grid is a sensible default unless another presentation is requested.

Forms use table fields as questions and submissions create records:
- List/get forms and questions by base/table coordinates. Reuse a same-title question unless a separate duplicate is intended.
- [Create questions](references/lark-base-form-questions-create.md): new field needs title/type; reuse needs `use_existing_field:true` and `field_id`, without new-field definition properties.
- [Update questions](references/lark-base-form-questions-update.md) preserves existing data. Question deletion normally deletes the underlying field and its records' values; use `--keep-field` when only removing it from the form.
- Visible-question ordering uses view visible fields with `form_id` as `--view-id`. Submit the complete ordered list of existing form members; omissions hide questions, an empty list hides all, and visibility rules can reference only earlier visible questions.
- Read sharing state before updates; change one sharing field at a time with explicit booleans.
- To fill a shared form, resolve `share_token`, read [detail](references/lark-base-form-detail.md) for actual questions/requirements, then [submit](references/lark-base-form-submit.md).

## Dashboards, BaseApp, workflows, and roles

- [Dashboard](references/lark-base-dashboard.md): container theme/layout differs from internal component configuration. `+dashboard-block-get-data` reads calculated results; get/list reads configuration. Dashboard internal blocks are not Base-tree blocks.
- [BaseApp and Workspace](references/lark-base-app.md): creation needs a real Workspace; pages use `app_token/page_id`, components use `block_id`, and referenced records still use the source Base token. Read [component config](references/lark-base-app-block-data-config.md) before writes. Copying BaseApp/full pages, page icons, and moving resources out of Workspace are unsupported; do not fake them with empty objects.
- Reused component configuration is only a structural template. Match explicit grouping/sort requirements, including `group_by[].sort.order` or top-level `sort.order`; existing result order is not a sort contract. Dashboard/App component IDs are not interchangeable.
- [Workflow](references/lark-base-workflow.md): get/list reads a steps graph linked by `next`/`children`; create/update writes the definition; enable/disable changes running state without rewriting steps.
- [Advanced permissions/roles](references/lark-base-advanced-permission-and-role.md): inspect `is_advanced` and real role configuration; only change these when requested.

For every update distinguish full replacement from delta. Full replacements require current configuration plus the requested change; deltas carry only changed fields. Confirmation flags implement the existing precise authorization.

## Operation references

- [base record history list](references/lark-base-record-history-list.md)
