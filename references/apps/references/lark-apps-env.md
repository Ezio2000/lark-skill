# apps env


Manage Miaoda app environment variables. Use `+env-list` to view, `+env-set` to set, and `+env-delete` to delete. There is no single-variable get command; to confirm whether a key exists, use list and then filter with `--jq`.

The environment flag uses `--environment`; do not use the old `--env`, and do not use short options.

<a id="查看"></a>
## View

`+env-list` queries dev by default, and by default does not return values. Variable values may appear in the response only after `--include-values` is explicitly passed; do not display output containing values in public logs.

API contract: list uses `POST env_vars`, and the body always includes `env` and, for CLI scenarios, `scene=2`; set uses `POST create_or_update_env_var`; delete uses `POST delete_env_vars`. `--include-values` only controls whether the CLI output displays values, and is not sent as a server-side query parameter.

```bash
lark-cli apps +env-list --app-id <app_id>
lark-cli apps +env-list --app-id <app_id> --environment online
lark-cli apps +env-list --app-id <app_id> --include-values --jq '.data.items[] | select(.key == "FOO")'
```

<a id="设置"></a>
## Set

Setting the dev environment does not require `--yes`. Setting the online environment requires human confirmation and explicitly passing `--yes`; if the current session has already explicitly authorized the same app, environment, key, and value, treat it as authorized, pass `--yes` directly, and do not ask again. `--dry-run` can be used to preview the request and does not require `--yes`. Variable values can be passed directly as `<value>`, or provided via `@file` or stdin.

In replies, state only the app/env/key and the execution result; do not echo the actual value. When an example is needed, use `<value>`, `@file`, or stdin.

```bash
lark-cli apps +env-set --app-id <app_id> --key FOO --value <value>
lark-cli apps +env-set --app-id <app_id> --key FOO --value @./secret.txt
lark-cli apps +env-set --app-id <app_id> --environment online --key FOO --value <value> --dry-run
lark-cli apps +env-set --app-id <app_id> --environment online --key FOO --value <value> --yes
```

<a id="删除"></a>
## Delete

`+env-delete` is high-risk-write. After verifying that the session authorization covers the app, environment, and key, pass `--yes`; existing authorization can be reused across turns and authentication recovery. When the scope is unclear, first use a read-only query or dry-run to prepare the specific request, then ask about the missing choices.

```bash
lark-cli apps +env-delete --app-id <app_id> --key FOO --dry-run
lark-cli apps +env-delete --app-id <app_id> --key FOO --yes
lark-cli apps +env-delete --app-id <app_id> --environment online --key FOO --yes
```

<a id="反模式"></a>
## Anti-patterns

- Do not treat `+env-pull` as an environment variable management command; it is only a fallback tool for refreshing the local `.env.local`.
- Do not invent an apps shortcut named env-get just to view one variable; use `+env-list --include-values` plus `--jq`.
- Do not write real secrets into examples or conversation output; when an example is needed, use `<value>`, `@file`, or stdin.
