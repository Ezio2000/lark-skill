# apps +get

Query details of a single app by app_id. For runtime command facts, refer to `lark-cli apps +get --help`.

<a id="何时用"></a>
## When to use

Use this when you need to view details of an app such as its type, name, description, and publish status. If you only need to fuzzy-search by app name to locate an app_id, use `+list --keyword`.

<a id="命令骨架"></a>
## Command skeleton

- Required: `--app-id`.
- Returns the app's complete information: `app_id`, `app_type`, `name`, `description`, `icon_url`, `created_at`, `updated_at`, `is_published`.

<a id="示例"></a>
## Examples

```bash
lark-cli apps +get --app-id app_xxx
lark-cli apps +get --app-id app_xxx --dry-run
lark-cli apps +get --app-id app_xxx -q '.data.app.app_type'
```

<a id="输出契约"></a>
## Output contract

- On success, reads the `data.app` object, containing the following fields:

| Field | Type | Description |
|------|------|------|
| `app_id` | string | Unique app identifier |
| `app_type` | string | App type (such as HTML, FRONTEND, FULL_STACK, MODERN_HTML) |
| `name` | string | App display name |
| `description` | string | App feature description |
| `icon_url` | string | App icon URL |
| `created_at` | string | Creation time (ISO 8601 UTC) |
| `updated_at` | string | Last update time (ISO 8601 UTC) |
| `is_published` | boolean | Whether it has been published |

- pretty output displays the core fields: `app_id`, `app_type`, `name`, `is_published`, `updated_at`.
- `is_published=true` only means the app has had a published version in its history; it does not mean the latest code has been deployed.

<a id="agent-规则"></a>
## Agent rules

- When the user already has `app_id` and wants to view details, use `+get`; when only the app name is available, use `+list --keyword`.
- Do not pass a Feishu app ID starting with `cli_` to `+get`; only app IDs starting with `app_` are accepted.
