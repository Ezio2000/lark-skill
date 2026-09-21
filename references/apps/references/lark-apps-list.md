# apps +list

List the Miaoda apps visible to the current user, used to locate `app_id` from an app name. For runtime command facts, `lark-cli apps +list --help` is authoritative.

<a id="何时用"></a>
## When to use

When a downstream operation requires `app_id` but the user has only given an app name/description, use `--keyword` to locate it. A full enumeration with no clear purpose wastes context; prefer narrowing the scope by keyword.

<a id="命令骨架"></a>
## Command skeleton

- Supports `--keyword` for fuzzy search by app name.
- `--ownership` enumeration: `all` / `mine` / `shared` (default `all` = created by me + shared with me; `mine` = only created by me; `shared` = only shared with me).
- `--app-type` enumeration: `html` / `frontend` / `full_stack`.
- Pagination: `--page-size` defaults to 20, `--page-token` passes the previous page's cursor.

<a id="示例"></a>
## Examples

```bash
lark-cli apps +list --keyword "审批"
lark-cli apps +list --ownership mine --app-type full_stack
lark-cli apps +list --page-token "<cursor>"
```

<a id="输出契约"></a>
## Output contract

- Successfully reads `data.items[]`; the retained fields are `description`, `app_id`, `name`, `is_published`, `online_url`, `updated_at`, and the core fields for candidate display are `name`, `app_id`, `updated_at`.
- `is_published=true` only means the app has had a published version historically; it does not mean the latest cloud session, latest code commit, or latest HTML artifact has been deployed.
- `online_url` is the currently existing published-state entry point; if you have not confirmed in this round that publishing is complete, do not describe it as the "latest version link".
- The default output has already trimmed `icon_url` (image URL, which the agent cannot render) and `created_at` (redundant with `updated_at`); when needed, you can use `--jq` to filter the above retained fields.
- `data.items` may be empty; do not treat an empty list as a failure.
- If there is a `has_more=true`, use the returned `page_token` / `next_page_token` to continue paging.

<a id="agent-规则"></a>
## Agent rules

When there are multiple candidates, display the name, app_id, and updated_at for the user to confirm. If the user's description already contains a `app_xxx` or a Miaoda link, extract it directly and do not `+list` again.

Treat `+list` as a locating tool and a published-state snapshot tool; do not treat `is_published` as proof that deployment is complete. When you need to prove that "the latest content is live", use the completion status of the corresponding publish command: check `+release-get`'s `finished`.
