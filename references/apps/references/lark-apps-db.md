<a id="apps-db-域命令"></a>
# apps db domain commands

Manage Miaoda application databases: view tables and schemas, initialize and publish multiple environments, move data, change governance, point-in-time recovery, usage. Running SQL statements one by one (SELECT/DML/DDL) goes through [`+db-execute`](lark-apps-db-execute.md) (a separate article). Runtime command facts are governed by `lark-cli apps +<cmd> --help`; for authentication, `--as user`, exit codes, `_notice`, and other general handling, see [`../../shared/index.md`](../../shared/index.md) and this domain's [`index.md`](../index.md).

<a id="何时用"></a>
## When to use

When the user wants to see which tables exist in an application / the schema of a table, split a single-database application into dev/online multiple environments, import data into or export data from tables, find out who changed table schemas or table data and when, turn row-level auditing on or off, publish the development environment's database schema to online, restore the database to a past point in time, or view database usage. To execute SQL statements one by one, go through [`+db-execute`](lark-apps-db-execute.md); for file storage (uploading/downloading files), go through [`lark-apps-file.md`](lark-apps-file.md). For **platform content specifications for creating tables / altering tables / writing SQL** (audit columns, RLS, `user_profile`, prohibited SQL, PG pitfalls), see the "Platform SQL Specifications" section of [`lark-apps-db-execute.md`](lark-apps-db-execute.md).

<a id="命令一览"></a>
## Command overview

| Command | What it does | Key parameters |
|---|---|---|
| `+db-table-list` | List the data tables in an environment | `--environment`, `--page-size`/`--page-token` |
| `+db-table-get` | View a single table's schema (fields/indexes/constraints/DDL) | `--table`, `--environment`, `--format` |
| `+db-env-create` | Initialize a single-database application into dev/online multiple environments (high-risk) | `--environment`, `--sync-data`, `--yes` |
| `+db-data-export` | Export a table's data to a local file | `--table`, `--output`, `--limit`, `--environment` |
| `+db-data-import` | Import a local csv/json file into a table (high-risk) | `--file`, `--table`, `--environment`, `--yes` |
| `+db-sync-create` | Preview or create a sync task from Base to the application database (high-risk) | `--config`, `--preview`, `--output`, `--environment`, `--yes` |
| `+db-sync-list` | List Base sync tasks | `--mode`, `--status`, `--table`, `--page-size`/`--page-token`, `--environment` |
| `+db-sync-get` | View a sync task's configuration, status, statistics, and warnings | `--task-id` |
| `+db-sync-enable` | Enable a streaming sync task | `--task-id` |
| `+db-sync-disable` | Disable a streaming sync task | `--task-id` |
| `+db-sync-update` | Modify a streaming sync task's mapping configuration (high-risk) | `--task-id`, `--config`, `--yes` |
| `+db-sync-delete` | Delete a streaming sync task, retaining the target data (high-risk) | `--task-id`, `--yes` |
| `+db-changelog-list` | View table schema change (DDL) history | `--table`, `--change-id`, `--since`/`--until`, `--environment` |
| `+db-audit-status` | See which tables have row-level auditing enabled and the retention period | `--table`, `--environment` |
| `+db-audit-enable` | Enable row-level change auditing for a table | `--table`, `--retention`, `--environment` |
| `+db-audit-disable` | Disable row-level auditing for a table | `--table`, `--environment` |
| `+db-audit-list` | List a table's row-level change events (insert/delete/update traceability) | `--table` (repeatable), `--since`/`--until`, `--environment` |
| `+db-env-diff` | Preview the schema changes in the development environment pending publication to online | `--app-id` |
| `+db-env-migrate` | Publish the development environment's schema changes to online (high-risk) | `--app-id`, `--yes` |
| `+db-recovery-diff` | Preview the changes that restoring the database to a point in time would bring | `--target` |
| `+db-recovery-apply` | Restore the database to a point in time, overwriting current data (high-risk) | `--target`, `--yes` |
| `+db-quota-get` | View database storage usage | `--environment` |

<a id="约定先读"></a>
## Conventions (read first)

- **Environment `--environment dev|online` (optional)**: viewing tables, viewing schemas, data import/export, change traceability, auditing, and quotas are all distinguished by environment. When `--environment` is omitted, the CLI does not include that parameter and the server automatically selects the branch based on the application's form—multi-environment applications go to `dev`, and those without multiple environments enabled go to `online`; to pin the environment, pass it explicitly. The only combination that errors: explicitly passing `--environment dev` for an application that does not have multiple environments enabled (there is no `dev` branch). For write operations, it is recommended to verify in `dev` first (only multi-environment applications have `dev`). The old name `--env` has been **removed**: passing it reports a validation error (prompting you to use `--environment` instead); always use `--environment`. `+db-env-diff`/`+db-env-migrate` have the semantics of "dev→online publication"; there is **no** `--environment`.
- **Local files / `--output` use relative paths within the working directory**: import `--file ./orders.csv`, export `--output ./out.csv`; absolute paths, or `--output` that escape the working directory via `..`/symbolic links, are rejected (validation / exit 2). If the path is elsewhere, first `cd` over to it or change it to a relative path.
- **High-risk operations must include `--yes`**: `+db-env-create`, `+db-data-import`, `+db-env-migrate`, `+db-recovery-apply`, `+db-sync-create`, `+db-sync-update`, `+db-sync-delete` are blocked by the confirmation gate by default; before acting, use the corresponding preview command or `--dry-run` to see the impact clearly. `+db-sync-create --preview` only parses/validates the configuration and does not write to the database, so it requires no confirmation and no `--yes`; actually creating a task (without `--preview`) requires `--yes`.
- **Base sync is not a whole-database task**: `+db-sync-create` processes only one Base table to one target table at a time. When the user says "the whole database" or "sync all three tables: customers, orders, and payments," first clearly tell the user that it will be split into three independent configurations, three previews, and, after user confirmation, three creates; do not imply that one sync task can cover the entire Base.
- **batch tasks cannot be re-enabled**: When the user says "re-enable the batch task" or "operation-not-allowed," give the conclusion first: batch/import are one-time tasks and cannot be enabled. Do not first get bogged down in authorization troubleshooting and miss this conclusion; when authorization is missing, also explain that after authorization is completed you should use `+db-sync-get` to check status/results, and that continuous syncing requires creating a new streaming task.
- **Time parameters are passed naturally in colloquial form** (`--since`/`--until`/`--target`); for formats, see the end.

<a id="各命令"></a>
## Commands

<a id="表与结构"></a>
### Tables and schemas

**`+db-table-list`**: List the data tables in an environment. Pagination `--page-size` (default 20) / `--page-token` (previous page cursor). Each item gives the table name, description, estimated row count, size, and column count; for complete column definitions / indexes / constraints, use `+db-table-get`. When you only know the business object name, use this first to locate possible table names.

```bash
lark-cli apps +db-table-list --app-id app_xxx
lark-cli apps +db-table-list --app-id app_xxx --environment dev --page-size 50
```

**`+db-table-get`**: View a single table's schema. By default, JSON gives structured fields / indexes / constraints / estimated row count / size; `--format pretty` directly outputs the table creation DDL text (use this when showing the user the table creation statement or using it as a migration reference).

```bash
lark-cli apps +db-table-get --app-id app_xxx --table orders
lark-cli apps +db-table-get --app-id app_xxx --table orders --environment dev --format pretty
```

<a id="多环境数据库初始化--发布"></a>
### Multi-environment database (initialization + publication)

**`+db-env-create` (high-risk)**: Initialize an existing single-database application into two databases, dev/online. This is irreversible and must include `--yes`. `--environment` currently only supports `dev` (default `dev`); `--sync-data` copies the existing online data to the new environment (if not passed, no copy is made). Note: applications newly created by `+create --app-type full_stack` usually already come with multiple environments, and repeated initialization returns a conflict error (the application is already multi-environment)—just relay the status according to `error.hint`; do not initialize again.

```bash
lark-cli apps +db-env-create --app-id app_xxx --environment dev --dry-run
lark-cli apps +db-env-create --app-id app_xxx --environment dev --sync-data --yes
```

**`+db-env-diff`**: Preview the table schema changes in the development environment pending publication to online, without applying them. Look at this before publishing. When there are no pending changes, it explicitly returns "no changes."

**`+db-env-migrate` (high-risk)**: Formally publish the development environment's schema changes to online. This is irreversible and must include `--yes`, and it returns the number of changes actually published. Publication is asynchronous, and the command waits until completion before returning the result.

> Preview and publication use the same endpoint, so `+db-env-diff` also requires the `spark:app:write` scope (it is not a purely read-only permission).

```bash
lark-cli apps +db-env-diff --app-id app_xxx
lark-cli apps +db-env-migrate --app-id app_xxx --yes
```

<a id="数据导入导出"></a>
### Data import and export

**`+db-data-export`**: Export a table to a local file. The export format is **determined solely by the extension of `--output`**—`.csv` / `.json` / `.sql`; by default it is placed in the current directory according to `<表名>.csv`. Note: the global `--format json|pretty` only controls the rendering of **the command's own output** (success summary / error envelope) and **does not affect the format of the exported file**; the `--output` suffix must be one of `.csv/.json/.sql`, otherwise a validation error is reported (exit 2), and exporting to stdout is not supported. There are two size constraints:

- `--limit` (1..5000, default 5000) is a **row count upper-bound guard**: if the table's row count exceeds it, the whole export is rejected (it is not "export only the first N rows");
- If the exported artifact is >1 MB, it is also rejected.

Do not force-export very large tables: first use `+db-execute` with `WHERE` / `LIMIT` to narrow the scope and export in batches.

```bash
lark-cli apps +db-data-export --app-id app_xxx --table orders --output ./orders.csv
lark-cli apps +db-data-export --app-id app_xxx --table orders --output ./orders.json --environment dev
```

**`+db-data-import` (high-risk)**: Import the data from a local csv/json file into a table. The file must be `.csv`/`.json` and ≤1 MB, and `--yes` must be included. The target table by default takes the file name with the **last** extension removed (e.g., `orders.csv`→`orders`, `orders.2026.csv`→`orders.2026`); when the file name contains dots, it is recommended to explicitly pass `--table` to avoid landing on an unexpected table name.

```bash
lark-cli apps +db-data-import --app-id app_xxx --table orders --file ./orders.csv --environment dev --yes
```

**Import/export limits**: size ≤ **1 MB**, row count ≤ **5000**; import and export are the same, and exceeding the limit is rejected. If over the limit, batch it—split imports into multiple files of ≤1 MB / ≤5000 rows, and for exports use `WHERE` / `LIMIT` to narrow the scope.

<a id="base-数据同步"></a>
### Base data sync

Base data sync goes through `+db-sync-*`, which differs from local file import: `+db-data-import` only handles local `.csv/.json` files; Base links, Base tables, field mappings, and continuous sync tasks all go through `+db-sync-create` / `+db-sync-update`.

**Task types**:
- `mode=batch`: one-time task. `schema_only=true` only creates the target table; `schema_only=false` creates the table or writes to an existing table and imports the current Base data. After completion, it cannot be enabled/disabled/updated/deleted.
- `mode=streaming`: continuous sync task. After the initial sync, it continuously handles Base changes and can be enabled/disabled/updated/deleted.

**Environment (important)**: When `+db-sync-*` commands omit `--environment`, they default to **online** (unlike the rule for `+db-table-*`/`+db-audit-*` and others, which "automatically select dev for multi-environment and online for single-environment"—the db-sync family does not use the automatic branch selection). **Creating tables in a multi-environment application** (`target.table.action=create`) **must explicitly pass `--environment dev`**: leaving it blank or passing `online` is rejected by the online branch's DDL prohibition (`k_dl_4000001：forbid ddl/dcl operation in online env`), because the online branch does not allow direct table creation as a product rule, and table creation must land on the dev branch. Shared databases / single-environment applications only have online, and creating tables on online succeeds normally (it does not report `k_dl_4000001`); omitting `--environment` or passing `online` both work.

**Configuration format**: Pass the complete JSON only through `--config`, supporting inline JSON, `@file`, and `-` stdin. Configuration keys use the plural form: `field_maps`, `option_mappings`, `syncable_source_fields`. Do not write the singular `field_map` / `option_mapping`; the CLI will directly report a validation error. For a formal create, `field_maps` **may be omitted or passed as an empty array**: the server will use the same logic as preview to automatically match fields and directly create the task; if a mapping is explicitly passed, at least one item must not be written as `"enabled": false`; if written but all disabled, the CLI rejects it. `+db-sync-update` still requires at least one enabled `field_maps`, because the semantics of update is to modify existing mappings. `target.table.action` can only be `create` or `use_existing`: when creating a table, `pg_field` requires complete field definitions; when writing to an existing table, usually only the target column names are needed. `source.base_url` (the full URL of the source Base table) is required in `+db-sync-create` and enforced by the server; `+db-sync-update` is optional—when omitted, the server reuses the original task's source URL, and a new `base_url` is needed only when changing the source / replacing it with another Base table. `source.table.name` is the name of the Base table to sync. `base_url` has the form `https://.../base/<token>?table=<tableId>`: `token` locates the Base, and the `table=` parameter (tableId) locates the table. If `source.table.name` is provided, name takes precedence—the server uses `token + name` to look up the tableId in reverse (overriding the `table=` parameter in the url); only when it is not provided does it use the url's `table=` parameter to locate the table. Therefore, when the user says in natural language "sync the xxx table" or "sync the xxx table over," be sure to put "xxx" into `source.table.name`, and do not provide only `base_url`—especially when `base_url` does not carry the `table=` parameter (pointing to a Base without a specific table), if name is omitted the server has no way to locate the table.

**Not knowing which table to sync**: If `base_url` has only the domain plus token and does not carry the `?table=` parameter, and the table name is uncertain, do not guess. First use `lark-cli base +table-list --base-token <token>` to list all tables in that Base (`<token>` is the segment after `/base/` in `base_url`), have the user select the table name, then fill it into `source.table.name` (or switch to the full URL with `?table=<table_id>`). `+db-sync-create` will block locally the configuration where "`base_url` has no `?table=` and `source.table.name` is empty" (reporting a validation error before submission, without sending it to the server).

**Singular key recovery**: If the user says that in the configuration `field_map` is singular, `option_mapping` is singular, or the field mapping may not take effect, do not submit the original configuration directly. First find the user's sync configuration and do these three steps:

1. Change only the known keys to plural: `field_map` -> `field_maps`, `option_mapping` -> `option_mappings`; do not invent field names such as `fieldMappings` / `mapping`.
2. Check that `field_maps` is an array and that at least one item has `enabled` omitted or set to `true`. If all are `"enabled": false`, first have the user confirm which items to enable, then continue.
3. After fixing it, preview again first, or reuse the `data.config` produced by the most recent preview `--output`, then continue with create / update.

```bash
lark-cli apps +db-sync-create --app-id app_xxx --environment dev --config @sync.json --preview --output ./resolved-sync.json
lark-cli apps +db-sync-create --app-id app_xxx --environment dev --config @resolved-sync.json --yes
```

If the configuration file cannot be found locally, do not stop at "please provide the file." First explain the recovery sources: have the user paste the JSON that was passed when it failed, or look for the `--output` file from the most recent preview; if it is a modification of an existing task, first use `+db-sync-get` to retrieve the current task configuration, then correct it based on that and update:

```bash
lark-cli apps +db-sync-get --app-id app_xxx --task-id streaming_123 -q '.data | {mode, source, target, field_maps}' > sync.json
lark-cli apps +db-sync-update --app-id app_xxx --task-id streaming_123 --environment dev --config @sync.json --yes
```

**Recommended flow (best practice, not mandatory)**: Prefer previewing first, then having the user confirm the mapping, and finally using the complete config output by preview to formally create; this is the most reliable and also avoids hand-writing complex `field_maps`. If the user explicitly requests direct execution without preview, you may also omit `field_maps` in the create config (or pass an empty array), and the server will automatically match and directly create the task; the CLI should not force the user to preview first just to obtain the mapping.

```bash
lark-cli apps +db-sync-create \
  --app-id app_xxx \
  --environment dev \
  --config - \
  --preview \
  --output ./resolved-sync.json <<'JSON'
{
  "mode": "streaming",
  "source": {
    "type": "base",
    "base_url": "https://example.feishu.cn/base/xxx",
    "table": {"name": "客户"}
  },
  "target": {
    "type": "postgresql",
    "table": {"name": "customers", "action": "use_existing"}
  }
}
JSON
```

preview returns `data.config`, `syncable_source_fields`, and `summary`. `--output` writes only `data.config` to the file, and the file can be used directly as formal input:

```bash
lark-cli apps +db-sync-create --app-id app_xxx --environment dev --config @resolved-sync.json --yes
lark-cli apps +db-sync-get --app-id app_xxx --task-id streaming_123
```

**Multi-table Base**: This command processes only one table at a time. When the user wants to sync the entire Base, first explain the plan clearly: it is not one "whole-database sync task," but N single-table tasks split by table. Each table has its own configuration file, one `+db-sync-create --preview`, one `+db-sync-create --yes` after user confirmation, and records its own `task_id`.

```bash
lark-cli apps +db-sync-create --app-id app_xxx --environment dev --config @customers-sync.json --preview --output ./customers-resolved.json
lark-cli apps +db-sync-create --app-id app_xxx --environment dev --config @orders-sync.json --preview --output ./orders-resolved.json
lark-cli apps +db-sync-create --app-id app_xxx --environment dev --config @payments-sync.json --preview --output ./payments-resolved.json
```

The configuration must also be at single-table granularity: each JSON has only one `source.table` and one `target.table`, and field names keep the plural keys `field_maps`, `option_mappings`, `syncable_source_fields`.

**Modifying streaming mappings**: First use get to export the current configuration, edit `field_maps`, then update. update is a high-risk operation and must be confirmed by the user before adding `--yes`.

The `source` returned by `+db-sync-get` **does not include `base_url`** (only token / tableId; the server has no domain and cannot assemble a full URL). This is normal. For updating the original table, simply omit `base_url`; only when switching to another Base table do you need to explicitly add a new `base_url` in the config. Do not fabricate a domain or concatenate a URL just to "complete" `base_url`—if you cannot obtain it, omit it and let the server reuse the original task's source URL.

`+db-sync-update` also follows the db-sync family rule of "omitting `--environment` lands on online," so modifying a task on dev must explicitly include the `--environment` of the environment where that task resides (streaming tasks for multi-environment applications are usually in `dev`); otherwise it will incorrectly land on online, fail to find the task, or modify the wrong branch.

```bash
lark-cli apps +db-sync-get --app-id app_xxx --task-id streaming_123 -q '.data | {mode, source, target, field_maps}' > sync.json
lark-cli apps +db-sync-update --app-id app_xxx --task-id streaming_123 --environment dev --config @sync.json --yes
```

**Listing and lifecycle**:

```bash
lark-cli apps +db-sync-list --app-id app_xxx --mode streaming --table customers
lark-cli apps +db-sync-disable --app-id app_xxx --task-id streaming_123
lark-cli apps +db-sync-enable --app-id app_xxx --task-id streaming_123
lark-cli apps +db-sync-delete --app-id app_xxx --task-id streaming_123 --yes
```

`+db-sync-enable`, `+db-sync-disable`, `+db-sync-update`, and `+db-sync-delete` apply only to `streaming_...` tasks. Performing these operations on `batch_...` returns failed-precondition.

**batch task operation-not-allowed recovery**: When the user says "re-enable the batch task", "re-enable the task that imported the historical orders table", or "the system says the operation is not allowed", first give the lifecycle conclusion: batch / import tasks are one-off tasks and cannot be re-enabled after they complete or fail, and do not repeatedly call `+db-sync-enable`. Instead, move on to checking status and results:

```bash
lark-cli apps +db-sync-get --app-id app_xxx --task-id batch_123
```

Tell the user about `status`, `result`, `warnings`, and the target table write status. If what the user wants is ongoing subsequent sync rather than "restarting this batch", a new `mode=streaming` task should be created: first `+db-sync-create --preview` for the user to confirm the mapping and impact, then create it with `--yes`; do not force-enable a completed batch task. If the CLI is still missing authorization at this point, still explain this lifecycle boundary first, then prompt that after authorization completes, use `+db-sync-get` to check the results.

**Failure recovery**: When you see `warnings`, do not directly say the sync succeeded. Continue troubleshooting according to the warning or error's `hint`, and branch the recovery path by task mode:

- **streaming task**: The common path is `+log-list --keyword <target_table>` / `+log-get` to check logs, then use `+db-execute` to fix the target table structure, or use `+db-sync-update` (with the `--environment` of the environment where the task resides) to fix the field mapping, and finally `+db-sync-get` the same `task_id` again to recheck.
- **batch task**: batch is a one-off task and **cannot be updated** (see the lifecycle above). After fixing the target table structure (`+db-execute`), do not update the original batch; instead `+db-sync-create --preview` again to create a new task; if you only want to see this batch's results, just `+db-sync-get`.

If the CLI is still missing authorization at this point and the warning details cannot be retrieved, do not just give generic field-checking suggestions either: first explain that you are blocked by authorization, then clearly lay out the fixed command chain for the corresponding mode as the next step after authorization completes.

**online DDL prohibition (`k_dl_4000001`) recovery**: When `+db-sync-create` table creation reports `k_dl_4000001：forbid ddl/dcl operation in online env`, this is necessarily a multi-environment app (a shared database creating a table in online would not report this code). The online branch **is inherently not allowed** to create tables directly; this is the product design for multi-environment apps, not a bypassable restriction. Instead use `--environment dev` to rerun `+db-sync-create` and create the table in the dev branch; do not try to "find a way to retry table creation in online"—there is no such option.

**Missing Base table record ID mapping column (`400002477`) recovery**: streaming auto-sync requires the target table to have a **text + single value + unique** column mapped to "Base table record ID". When using `action=use_existing` to write to an existing table, if the table has no such column, it reports `400002477` (Field mapping must include 'Base table record ID'). First use `+db-execute` to add one to the table, such as `ALTER TABLE <表> ADD COLUMN base_record_id varchar UNIQUE`, then map it to "Base table record ID" and rerun `+db-sync-create --preview`. Note that this is **adding a column**, not creating a table, so the audit column / RLS set of table-creation conventions is not needed.

<a id="变更追溯与审计"></a>
### Change tracing and auditing

**`+db-changelog-list`**: Check table structure change (DDL) history—who, when, which table was changed, and what was done. You can filter by `--table`, pinpoint a specific entry by `--change-id`, bound the time range with `--since`/`--until`, and paginate with `--page-size`/`--page-token`.

```bash
lark-cli apps +db-changelog-list --app-id app_xxx --table orders --since 7d
```

**`+db-audit-status`**: View audit switch status. Provide `--table` to see a single table; if not provided, list all configured tables (whether enabled, retention period).

**`+db-audit-enable` / `+db-audit-disable`**: Enable / disable row-level change auditing for a table. `--retention` sets the retention period, with values `7d`/`30d`/`180d`/`360d`/`forever` (default `7d`). Do not repeatedly enable a table that already has auditing enabled—if unsure, first check with `+db-audit-status`.

```bash
lark-cli apps +db-audit-enable --app-id app_xxx --table orders --retention 30d
lark-cli apps +db-audit-disable --app-id app_xxx --table orders
```

**`+db-audit-list`**: List a table's row-level change events (before/after values and operator for INSERT/UPDATE/DELETE). `--table` is required and can be passed repeatedly for multiple tables; `--since`/`--until` bound the time.
- **Multi-table query**: Tables that do not exist or do not have auditing enabled are first filtered out for the user before querying; the filtered tables and reasons are listed in the result's `skipped`—use this to tell the user which tables were not included and why.
- **Single-table query**: No pre-filtering; if the table does not exist / does not have auditing enabled, it errors directly (relay this to the user per `error.hint`, guiding them to first `+db-audit-enable`).

```bash
lark-cli apps +db-audit-list --app-id app_xxx --table orders --since 24h
lark-cli apps +db-audit-list --app-id app_xxx --table orders --table users
```

<a id="时间点恢复pitr"></a>
### Point-in-time recovery (PITR)

**`+db-recovery-diff`**: Preview what changes restoring the database to the `--target` point in time would bring (affected tables, row counts, estimated duration), without applying them. Also requires the `spark:app:write` scope.

**`+db-recovery-apply` (high risk)**: Restore the database to a point in time; **this overwrites current data**, is irreversible, and must include `--yes`.

- The recoverable window is at most **7 days**, and no earlier than the **most recent `+db-env-migrate`**; targets outside the window are rejected.
- When the target point in time matches the current database, it returns `no_changes` (no-op), which does not count as a failure.
- Before acting, be sure to first `+db-recovery-diff` for user confirmation.

```bash
lark-cli apps +db-recovery-diff --app-id app_xxx --target 2h
lark-cli apps +db-recovery-apply --app-id app_xxx --target 2026-04-15T10:00:00Z --yes
```

<a id="配额"></a>
### Quota

**`+db-quota-get`**: Check database storage usage (used amount, table count, view count; once quota integration is in place, it will also give total quota and usage rate).

```bash
lark-cli apps +db-quota-get --app-id app_xxx --environment dev
```

<a id="时间格式--since----until----target"></a>
## Time format (`--since` / `--until` / `--target`)

Just pass it in naturally as the user speaks; supported:
- Relative time `7d` / `2h` / `30s` (counting back from now)
- Date `2026-04-15`
- Date-time `2026-04-15T10:00:00`
- ISO 8601 with time zone `2026-04-15T10:00:00Z` / `2026-04-15T10:00:00+08:00`

> **Time zone**: `日期` / `日期时间` without a time zone are parsed according to the **local time zone of the machine running it** (then normalized to UTC). Running the same command in CI (UTC) and locally (e.g. UTC+8) will differ by a few hours at the time boundary; to lock the time zone precisely, explicitly write ISO 8601 with an offset (e.g. `...+08:00` / `...Z`). `--target` (PITR restore) especially should include a time zone, to avoid restoring to an unintended point in time.

<a id="agent-规则"></a>
## Agent rules

- When the user says "local / dev database / debug database", prefer `--environment dev`; for online troubleshooting use `--environment online`; for data-plane write operations (import / audit switches), it is recommended to first verify in `dev` before touching `online`. **Note that when `--environment` is omitted, write operations land on the branch selected by the server—for a single-environment app that is `online` (production)**: when unsure whether the app is multi-environment, explicitly pass `--environment` for write operations; explicitly passing `dev` on a single-environment app safely errors (no dev branch), which is exactly usable as a probe for "is it multi-environment".
- To view tables use `+db-table-list`; to view structure use `+db-table-get` (add `--format pretty` for the create-table statement); `+db-env-create` is only for splitting an existing single database into multiple environments, and newly created full_stack apps generally do not need it.
- For high-risk commands (`+db-env-create`, `+db-data-import`, `+db-env-migrate`, `+db-recovery-apply`, `+db-sync-create`, `+db-sync-update`, `+db-sync-delete`), understand the impact before acting, then include `--yes`: for publish / restore, first run the corresponding preview `+db-env-diff` / `+db-recovery-diff`; for Base sync, first run `+db-sync-create --preview`; import has no preview command, so you can first `--dry-run` to see the request or first verify in `--environment dev`; do not silently append `--yes`; when encountering confirmation_required (exit 10), confirm the irreversible risk with the user per the lark-shared protocol, then add `--yes` and retry.
- Use relative paths within the working directory for import / export local paths; exporting an oversized table will be rejected by the row count / size limit, so switch to `+db-execute` for batching.
- For Base sync, prefer preview → user confirmation → create; this is the most reliable best practice, not mandatory. When the user explicitly requests direct create, you may omit `field_maps` (or pass an empty array) to let the server auto-match and create; do not force the user to preview first just to get the mapping. When explicitly writing mappings, use the plural keys `field_maps` / `option_mappings`.
- When fixing Base sync configuration, only change `field_map` / `option_mapping` to `field_maps` / `option_mappings`. If `field_maps` is explicitly given, check that at least one mapping is enabled; when all are `"enabled": false`, first have the user confirm which one to enable. For create you may also delete/empty `field_maps` and let the server auto-match, but update must still provide enabled mappings.
- It is legal for `+db-sync-update` to omit `source.base_url` (the server reuses the original task's source URL); it is normal for `+db-sync-get` not to return `base_url`, so do not fabricate a domain / concatenate a URL to "complete" it on that basis; only pass a new `base_url` when changing the source / replacing the table. `+db-sync-create`'s `base_url` is required, and if missing the server reports an error. When the user says "sync the xxx table", put "xxx" into `source.table.name`—if name is provided, name takes precedence (the server uses `base_url`'s token + name to look up the tableId, overriding the url's `table=` parameter); only if not provided does it use the url's `table=` parameter for location; do not provide only `base_url`.
- batch sync tasks cannot be re-enabled. When encountering operation-not-allowed, first `+db-sync-get` to check status and results; if ongoing sync is needed, create a new streaming task, going through preview -> user confirmation -> create.
- When `+db-sync-*` omits `--environment`, it defaults to online. Creating tables for a multi-environment app (`action=create`) must explicitly include `--environment dev`; omitting it or passing `online` will hit `k_dl_4000001` (online prohibits DDL)—that is the product design for multi-environment apps, so just create the table in the dev branch and do not retry table creation in online. Shared-database apps creating tables in online is normal and not subject to this restriction.
- For `+db-audit-list` multi-table queries, explain to the user the tables in the result's `skipped` (nonexistent / auditing not enabled) along with the reasons, so the user does not think these tables "have no changes".
- Restore is overwrite-based and irreversible: before `+db-recovery-apply` you must first `+db-recovery-diff`, and clearly tell the user that current data will be overwritten.
