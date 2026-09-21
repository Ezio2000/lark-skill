# apps +release-list

Paginate through Miaoda app release history, with the latest release first. For runtime command facts, refer to `lark-cli apps +release-list --help`.

<a id="何时用"></a>
## When to use

Use when the user asks about "recent releases", "historical versions", or "why the last one failed", but does not provide `release_id`. After obtaining candidate releases, follow up with `+release-get`.

<a id="命令骨架"></a>
## Command skeleton

- Required: `--app-id`.
- Optional `--status`: `publishing` / `finished` / `failed`.
- Optional `--page-size`: default 20, maximum 500; always sent to the server.
- Optional `--page-token`: previous page cursor.

<a id="示例"></a>
## Example

```bash
lark-cli apps +release-list --app-id app_xxx --page-size 10
lark-cli apps +release-list --app-id app_xxx --status failed
```

<a id="输出契约"></a>
## Output contract

- On success, read `data.releases[]`; the key fields are `release_id`, `status`, `created_at`, `updated_at`.
- `release_id` is used to continue querying `+release-get`.
- If `has_more=true`, use `next_page_token` / `page_token` to paginate.

<a id="agent-规则"></a>
## Agent rules

When the user limits the view to only N items ("the most recent N", "the latest N", "only the first N"), use `--page-size N` (e.g., "the most recent release" → `--page-size 1`), rather than fetching the full set and truncating locally.
