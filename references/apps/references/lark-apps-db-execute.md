# apps +db-execute

Executes SQL in the application database via the Miaoda server side. For runtime command facts, `lark-cli apps +db-execute --help` is authoritative.

> **Before writing SQL, read the "Platform SQL Specification" at the end of this document**: Miaoda's underlying layer is PostgreSQL plus a layer of platform constraints; SQL content that does not comply will be directly rejected by the server side or will create tables with incorrect behavior. The three most easily tripped items: ① Creating a business table must include 4 audit columns (`_created_at`/`_updated_at`/`_created_by`/`_updated_by`) + enable RLS + 4 policies, all written in a single call; ② Personnel fields use the built-in composite type `user_profile` (write with `ROW('<user_id>')::user_profile`, query by dereferencing `(field).user_id`); ③ `CREATE/DROP DATABASE·SCHEMA·USER·ROLE`, non-whitelisted `CREATE EXTENSION`, and platform-reserved tables `auth`/`users` will be hard-rejected, and the `online` environment prohibits DDL.

<a id="何时用"></a>
## When to use

Used to execute application database SQL via the Miaoda server side. Do not take the connection string from environment variables and connect to the database directly; local debugging also goes through this shortcut. For what kind of SQL to write (platform constraints, table creation templates, `user_profile`, audit columns, prohibited SQL, PG pitfalls), see the "Platform SQL Specification" at the end of this document.

<a id="命令骨架"></a>
## Command skeleton

- Required: `--app-id`, plus one of `--sql` / `--file` (mutually exclusive).
- `--sql`: inline SQL text; when `-` is passed, read from stdin. Absolute-path files are passed in via stdin: `--sql - < <absolute-path>` (the shell resolves the path; the CLI only receives the content).
- `--file`: `.sql` file path, which must be a relative path within the working directory (such as `--file ./migration.sql`); absolute paths, or paths that escape the working directory via `..`/symbolic links, will be rejected. When the file is not within the working directory, use `--sql - < <文件路径>` to pass it in via stdin instead.
- `--environment` enum: `dev` / `online`, **if not passed, the server side automatically selects based on whether the application has multi-environment enabled (multi-environment → `dev`, multi-environment not enabled → `online`)**; to fix the environment, explicitly pass `--environment dev|online`. **For applications without multi-environment enabled, explicitly passing `--environment dev` will error (no dev branch) — such applications should not pass `--environment` (go with `online`) or explicitly pass `--environment online`**. The old name `--env` has been **removed**: passing it will cause a validation error (prompting to use `--environment` instead); always use `--environment`.
- risk is `high-risk-write` (SQL may contain DML/DDL): any execution requires `--yes`, otherwise it returns `confirmation_required` / exit 10. `--dry-run` preview does not require `--yes`.
- **It will not automatically wrap a transaction for you; transaction boundaries must be controlled by yourself in the SQL**: multiple statements are by default committed independently one by one; if one in the middle fails, the preceding statements have already taken effect and will not be rolled back; if you need the atomicity of "either all succeed or all roll back", explicitly write `BEGIN … COMMIT` within the SQL (see "Agent rules" below for details).

<a id="示例"></a>
## Examples

```bash
lark-cli apps +db-execute --app-id app_xxx --environment dev --sql "select * from orders limit 5" --yes
lark-cli apps +db-execute --app-id app_xxx --environment dev --file ./migration.sql --dry-run
# Absolute-path file / cwd not fixed: pass in via stdin
lark-cli apps +db-execute --app-id app_xxx --environment dev --sql - --yes < /Users/.../migrations/0001_init.sql
```

<a id="输出契约"></a>
## Output contract

- On success, the default JSON's `data` adapts to the SQL type (does not pass through the backend's raw string):
  - Single SELECT → `data` is a row array `[{...}]` (empty → `[]`), directly `-q '.data[].col'` to get fields.
  - Single DML → `data = {command, rows_affected}` (such as `{"command":"INSERT","rows_affected":1}`).
  - Single DDL → `data = {command}` (such as `{"command":"CREATE_TABLE"}`).
  - Multiple statements → `data` is an array of elements: SELECT is `{command:"SELECT", rows:[...]}`, DML is `{command, rows_affected}`, DDL is `{command}`.
- pretty renders adaptively by SELECT/DML/DDL; multiple statements display a Statement summary one by one.
- On failure, returns a typed `error` (`type:"api"`, `subtype:"server_error"`, `code`, `message`, `hint`): the failure position is in `message`'s "(at statement N of M)"; whether the preceding statements landed / whether the whole batch rolled back is written in `hint` — failure within a transaction: "Transaction rolled back; no changes persisted."; non-transactional multiple statements with preceding statements already landed: "Earlier statements were committed and not rolled back; fix statement N and re-run the remaining statements."; failure on the first statement (no preceding statements landed): "No statements were applied; fix the SQL and re-run.". Based on this, decide whether to re-run the whole segment or only the remaining statements.

<a id="agent-规则"></a>
## Agent rules

- This command is high-risk-write; execution always requires `--yes`; without `--yes` it returns `confirmation_required` / exit 10.
  - **Read-only queries, and statements that do not delete/lose existing data and are retractable**: when already authorized, can be executed directly with `--yes`.
  - **Statements that delete or lose existing data, or are difficult to retract**: first `--dry-run` preview (no `--yes` needed), confirm with the user, then execute with `--yes`; do not automatically add `--yes` without the user's knowledge.
- When multiple statements fail, the statements before the failure may already have been committed and landed. Do not re-run the whole batch; fix the failed statement according to the error message/hint, and continue from the remaining statements.
- If atomicity is needed, have the user explicitly write `BEGIN` / `COMMIT` within the SQL; do not assume the CLI will wrap a transaction.
- Do not take the database connection string from env and connect to the database directly.

---

<a id="平台-sql-规范"></a>
# Platform SQL Specification

The above explains how to call the command; here we explain **what kind of SQL should be written**: Miaoda's underlying layer is PostgreSQL plus a layer of platform constraints (RLS, audit columns, `user_profile` composite type, prohibited SQL whitelist); non-compliant SQL will be directly rejected by the server side or will create tables with incorrect behavior. To view tables / view structure, use [`+db-table-list`/`+db-table-get`](lark-apps-db.md); do not hand-write system table queries to simulate it.

<a id="平台禁用-sql硬拒绝"></a>
## Platform-prohibited SQL (hard rejection)

The following hits will be rejected by the server side; `error` (`type:"api"`)'s message/hint will explain the reason — first fix according to the hint and then retry; do not repeatedly retry the same statement.

| Category | Prohibited |
|---|---|
| Database level | `CREATE / DROP / ALTER DATABASE` |
| Schema level | `CREATE / DROP SCHEMA` |
| User / role level | `CREATE / DROP USER`, `CREATE / DROP / ALTER ROLE` |
| Owner switching | `REASSIGN OWNED` / `DROP OWNED` |

<a id="建表规范create-table"></a>
## Table creation specification (CREATE TABLE)

Creating a new business table must: 4 audit columns + enable RLS + 4 default policies, **placed in the same `+db-execute` call** (RLS / policy / COMMENT / INDEX together). Bare table name; do not write `public.` or a schema prefix.

```sql
CREATE TABLE IF NOT EXISTS <table> (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  -- ... business columns ...
  name varchar(100) NOT NULL,
  _created_at TIMESTAMP(3) WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  _created_by user_profile DEFAULT (
    CASE
      WHEN current_setting('app.user_id', TRUE) = '' THEN NULL
      ELSE concat('(', current_setting('app.user_id', TRUE), ')')::user_profile
    END
  ),
  _updated_at TIMESTAMP(3) WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  _updated_by user_profile DEFAULT (
    CASE
      WHEN current_setting('app.user_id', TRUE) = '' THEN NULL
      ELSE concat('(', current_setting('app.user_id', TRUE), ')')::user_profile
    END
  )
);

ALTER TABLE <table> ENABLE ROW LEVEL SECURITY;

CREATE POLICY service_role_bypass_policy ON <table>
  TO service_role USING (true);

CREATE POLICY "修改全部数据" ON <table>
  AS PERMISSIVE FOR ALL TO authenticated USING (true);

CREATE POLICY "查看全部数据" ON <table>
  AS PERMISSIVE FOR SELECT TO authenticated, anon USING (true);

CREATE POLICY "修改本人数据" ON <table>
  AS PERMISSIVE FOR ALL TO authenticated USING (
    (current_setting('app.user_id'::text) = ANY (ARRAY[]::text[]))
    AND (current_setting('app.user_id'::text) = ((_created_by).user_id)::text)
  );
```

Table creation flow: first `+db-table-list` / `+db-table-get` to confirm the table does not exist or to view the existing structure → generate DDL → show the user the impact and obtain authorization → `+db-execute ... --yes` execute.

<a id="审计列"></a>
## Audit columns

- The four columns automatically maintained by the platform are fixed as `_created_at` / `_updated_at` / `_created_by` / `_updated_by` (**starting with an underscore**). Queries / sorting / filtering always use these names; do not write `created_at`.
- `_created_at` / `_updated_at` may be omitted on INSERT (they have default values); when business attribution is needed, explicitly write `_created_by` / `_updated_by`.
- When UPDATEing business fields, it is recommended to also update `_updated_at = CURRENT_TIMESTAMP` and `_updated_by`.

<a id="user_profile-复合类型"></a>
## `user_profile` composite type

The platform has a built-in type `(user_id varchar, name varchar, email varchar, avatar text, status integer)`; no need to create it. **Business SQL is only allowed to access `(field).user_id`**; do not rely on `name` / `email` / `avatar` / `status` (they may be empty or stale).

```sql
-- Write / update: use ROW()::user_profile; on update, replace the entire field, do not change individual attributes
INSERT INTO teacher (teacher_profile, class_id)
VALUES (ROW('<user_id>')::user_profile, gen_random_uuid());

UPDATE teacher SET teacher_profile = ROW('<user_id>')::user_profile
WHERE (teacher_profile).user_id = '<old_user_id>';

-- Query / filter: dereference to get user_id; raw SQL must dereference before returning to the frontend; do not return the composite type directly
SELECT (teacher_profile).user_id AS teacher_profile, class_id FROM teacher;

-- Index / uniqueness: expression columns use triple parentheses; expression uniqueness uses CREATE UNIQUE INDEX,
-- cannot use ALTER TABLE ADD CONSTRAINT UNIQUE (does not support expression columns)
CREATE INDEX idx_teacher_user_id ON teacher (((teacher_profile).user_id));
CREATE UNIQUE INDEX uk_teacher_user_id ON teacher (((teacher_profile).user_id));
```

<a id="ddl-规则"></a>
## DDL rules

| Scenario | Approach |
|---|---|
| Add column | `ALTER TABLE <t> ADD COLUMN IF NOT EXISTS <col> <type>`, related `COMMENT ON` executed in the same call |
| Add index | `CREATE INDEX IF NOT EXISTS idx_<t>_<cols> ON <t>(...)` |
| JSONB type declaration | Must `COMMENT ON COLUMN <t>.<col> IS '@type { ... }'` declare the TypeScript type, in the same call as CREATE / ALTER |
| Add NOT NULL column | Must include `DEFAULT` so existing rows are automatically filled: `ADD COLUMN <col> <type> NOT NULL DEFAULT <值>` |
| Drop table / drop column | Prohibited by default when there is business data; execute only after the user explicitly authorizes, and explain the data loss risk |
| Strong constraints | `UNIQUE` / `FOREIGN KEY` / `NOT NULL` are cautious by default; if unsure, do not add |

**Before adding constraints to a multi-environment database, first check the online existing data**: `dev` being clean does not mean `online` is clean; publishing the constraint to online will fail by colliding with online existing data. Before publishing, always first use `--environment online` to check clearly; there are three types by constraint type:

- **Adding a unique constraint (`UNIQUE` / unique index)**: online must not have duplicate values. First check for duplicates; if any, clean them up first and then add:

  ```bash
  lark-cli apps +db-execute --app-id app_xxx --environment online --sql \
    "SELECT <cols>, count(*) FROM t GROUP BY <cols> HAVING count(*) > 1" --yes
  ```

- **Changing an existing column to `NOT NULL` (tightening the constraint)**: online, that column must not have NULLs. First check the NULL row count; if any, backfill first (`UPDATE t SET <col> = <默认值> WHERE <col> IS NULL`) and then add the constraint:

  ```bash
  lark-cli apps +db-execute --app-id app_xxx --environment online --sql \
    "SELECT count(*) FROM t WHERE <col> IS NULL" --yes
  ```

- **Adding a new `NOT NULL` field**: must include `DEFAULT`, and requires that the online table **has no existing data**, otherwise publishing will error. When online already has data, do not add it directly; instead use the three-step safe change: first `ADD COLUMN <col> <type>` (nullable) → backfill `UPDATE t SET <col> = <值>` → then `ALTER COLUMN <col> SET NOT NULL`. First check the online row count to determine which path to take:

  ```bash
  lark-cli apps +db-execute --app-id app_xxx --environment online --sql \
    "SELECT count(*) FROM t" --yes
  ```

<a id="select-规则"></a>
## SELECT rules

| Rule | Requirement                                                               |
|---|------------------------------------------------------------------|
| Row count | The result set has a hard limit (platform limit 1000 rows); exceeding the limit **errors rather than silently truncating**; large tables must explicitly `LIMIT`, aggregate, or use cursor pagination       |
| Pagination | For large tables, prefer cursor pagination `WHERE id > <last_id> ORDER BY id LIMIT n`, avoiding large `OFFSET` |
| user_profile | Dereference before returning to the frontend: `(owner).user_id AS owner`                             |
| Statistics | Use `count(*)` for totals and `GROUP BY` for grouping; do not pull the full set to the agent side and then compute statistics                  |
| Slow queries | Use `EXPLAIN (ANALYZE, BUFFERS)`; for large-table Seq Scan, consider adding an index                 |

<a id="dml-规则"></a>
## DML rules

**INSERT**
- Omit the UUID primary key; leave it to `DEFAULT gen_random_uuid()`; for foreign key UUIDs, use a subquery to get the parent table id; do not hand-write it.
- Columns that are NOT NULL and have no default value must be given values; in batch INSERT, each row must have the same number of columns.
- For idempotency, use `ON CONFLICT ... DO NOTHING / DO UPDATE`.
- Scalar subqueries must guarantee a single row; for non-unique conditions, add `ORDER BY ... LIMIT 1`.

**UPDATE**
- **Must have an explicit `WHERE`; unconditional UPDATE is prohibited**.
- When the user says "modify / update / change" data, use UPDATE; the **DELETE + INSERT** pattern is prohibited.
- When updating `user_profile` / composite types, replace the entire field.
- Before batch updates, if the impact scope is unclear, first `SELECT count(*)` for user confirmation.

**DELETE / TRUNCATE** (these are high-impact operations that lose data; follow the confirmation flow in "Agent rules" above)
- Prohibited by default for existing tables / existing data; first `SELECT count(*)` to show the number of matched rows, obtain the user's explicit authorization, then execute with `--yes`.
- `TRUNCATE` affects the entire table; treat it as a high-risk deletion.

```sql
UPDATE task
SET status = 'done', _updated_at = CURRENT_TIMESTAMP, _updated_by = ROW('<user_id>')::user_profile
WHERE id = (SELECT id FROM task WHERE title = '梳理需求' ORDER BY _created_at DESC LIMIT 1);
```

<a id="常见-postgresql-陷阱"></a>
## Common PostgreSQL pitfalls

| Pitfall | Correct approach |
|---|---|
| Table name with schema prefix | Business tables always use bare table names `FROM orders`; do not write `public.orders` |
| Reserved words as identifiers | Avoid `user` / `order` / `desc` / `offset` / `references` etc. |
| Inline COMMENT | Prohibited `col TEXT COMMENT 'xx'`; use a separate `COMMENT ON COLUMN` |
| Hand-writing system table structure queries | For conventional structure queries use `+db-table-list` / `+db-table-get`; do not hand-write `information_schema` / `pg_indexes` to simulate |
| Empty array type unclear | Write `ARRAY[]::text[]` or `'{}'::text[]` |
| `ROUND` error | Use `ROUND(num::numeric, n)` or `ROUND(num::double precision)` |
| `DISTINCT` + window functions | Query in two layers: first DISTINCT, then window functions |
| MySQL dialect | Do not use `SHOW TABLES` / `DESCRIBE` / inline `COMMENT`; use `+db-table-*` and `COMMENT ON` |
| Assuming multiple statements auto-rollback | `A; B; C` does not automatically wrap a transaction; when B fails, A has already been committed; for atomicity, explicitly `BEGIN; ... COMMIT;` (see "Command skeleton" and "Agent rules" above) |

<a id="数据类型与设计"></a>
## Data types and design

| Item | Rule |
|---|---|
| Primary key | Default `id uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| Naming | Table names singular, all lowercase, snake_case, no redundant suffixes |
| Enum / status | Use `varchar(255)`, values in lowercase English + underscores |
| JSONB | Must `COMMENT ON COLUMN ... IS '@type { ... }'` declare the type |
| Attachments / images | URLs use `TEXT`, named `xxx_url` |
| Constraints | `UNIQUE` / `FOREIGN KEY` / `NOT NULL` are cautious by default; for newly added NOT NULL columns, prefer including `DEFAULT` |
