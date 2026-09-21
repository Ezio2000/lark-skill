# Lark Sheet History

<a id="概念回顾"></a>
## Concept Overview

Each Feishu spreadsheet retains a series of historical versions (`minor_histories`). Each version is identified by `history_version_id` and comes with a creation time (`create_time`), an action (`action`), and block revision information (`all_block_revision`). History is **workbook-level** (for the entire spreadsheet, not for individual sheets).

Revert overwrites the spreadsheet's current content back to a historical version—this is a **high-risk write** operation and is **asynchronous**: it immediately returns an acceptance identifier upon initiation, and the actual revert happens in the background, requiring polling via status query for the final result (in progress / success / failure).

`+history-list` reads the version list to select a target; `+history-revert` initiates the revert; `+history-revert-status` polls the revert result. If you just want to get the **current document version number (revision)** as a starting anchor for recover / undo / `+changeset-get`, using `+revision-get` directly is more lightweight.

<a id="使用场景"></a>
## Use Cases

Read historical versions, initiate a revert, query revert status. This reference covers 3 shortcuts:

| Operation Need | Tool to Use | Description |
|---------|---------|------|
| View historical version list | `+history-list` | Returns `minor_histories`, each containing four fields: `history_version_id` / `create_time` / `action` / `all_block_revision`; supports forward pagination (optional `--end-version`) |
| Revert to a specified historical version | `+history-revert` | Pass in `--history-version-id`; asynchronous acceptance, returns a queryable identifier |
| Query revert status | `+history-revert-status` | Pass in `--transaction-id` (taken from the asynchronous acceptance identifier of `+history-revert`); poll the in progress / success / failure status of a revert |

Typical workflow: `+history-list` gets the `history_version_id` of the target version (paginate to fetch earlier history if necessary) → `+history-revert` initiates the revert and retrieves `transaction_id` → `+history-revert-status --transaction-id <transaction_id>` polls until success or failure.

**Notes (must understand)**:
- **Revert is a high-risk write operation**: it will overwrite the current spreadsheet with historical version content; you should clearly inform the user of the impact before executing.
- **Revert is asynchronous**: `+history-revert` returns `transaction_id` (acceptance identifier), which does not mean the revert is complete; you must use `+history-revert-status --transaction-id <transaction_id>` to confirm the final result.
- **`history_version_id` and `transaction_id` are not the same**: `history_version_id` is used for `+history-revert` (taken from `+history-list`); `transaction_id` is used for `+history-revert-status` (taken from the output of `+history-revert`).
- **History is workbook-level**: locating only requires `--url` / `--spreadsheet-token` (XOR), no sheet selector needed.
- **`+history-list` reverse-order pagination**: omit `--end-version` on the first query, which returns the latest page; if the response includes `next_end_version` and `has_more=true`, pass `next_end_version` as the next `--end-version` to continue paging to earlier versions; when the response **does not include** these two fields, it means you have reached the earliest page and no further paging is needed.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+history-list` | read | Historical Versions |
| `+history-revert` | high-risk-write | Historical Versions |
| `+history-revert-status` | read | Historical Versions |

## Flags

### `+history-list`

_Common: URL/token (no sheet locator) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--end-version` | int | optional | The maximum version for paginated queries (reverse order); omit on the first query, and pass the next_end_version returned by the previous page for the next page. |

### `+history-revert`

_Common: URL/token (no sheet locator) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--history-version-id` | string | required | The historical version to revert to (taken from +history-list) |

### `+history-revert-status`

_Common: URL/token (no sheet locator) · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--transaction-id` | string | required | The acceptance identifier of the asynchronous revert (taken from +history-revert) |

## Examples

Common locator: all shortcuts have `--url` / `--spreadsheet-token` at the top (XOR, choose one). `+history-revert` uses `--history-version-id` (taken from `+history-list`); `+history-revert-status` uses `--transaction-id` (taken from the asynchronous acceptance identifier of `+history-revert`).

### `+history-list`

```bash
# List the latest page of historical versions for a spreadsheet
lark-cli sheets +history-list --url "https://sample.feishu.cn/sheets/SHTxxxxxx"

# Locate using the raw spreadsheet token
lark-cli sheets +history-list --spreadsheet-token "SHTxxxxxx"

# Page to the next page: pass the next_end_version from the previous response as --end-version
lark-cli sheets +history-list --url "https://sample.feishu.cn/sheets/SHTxxxxxx" --end-version 12345
```

### `+history-revert`

```bash
# Revert to a specified historical version (asynchronous acceptance)
lark-cli sheets +history-revert --url "https://sample.feishu.cn/sheets/SHTxxxxxx" --history-version-id "<id-from-history-list>"
```

### `+history-revert-status`

```bash
# Query the current status of a revert (in progress / success / failure)
lark-cli sheets +history-revert-status --url "https://sample.feishu.cn/sheets/SHTxxxxxx" --transaction-id "<transaction-id-from-history-revert>"
```
