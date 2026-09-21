# apps +access-scope-get

View the runtime visibility scope of a Miaoda app. For runtime command facts, refer to `lark-cli apps +access-scope-get --help`.

<a id="何时用"></a>
## When to use

Use this to confirm who the app runtime is visible to. It does not indicate who can develop or manage the app; collaborators and repository permissions are not determined from here.

<a id="命令骨架"></a>
## Command skeleton

- Required: `--app-id`.
- The server-returned enum is `All` / `Tenant` / `Range`.
- Under `Range`, users, departments, and groups are in the `users` / `departments` / `chats` arrays respectively; the CLI does not merge them back into `targets`.

<a id="示例"></a>
## Example

```bash
lark-cli apps +access-scope-get --app-id app_xxx
```

<a id="输出契约"></a>
## Output contract

- On successfully reading `data.scope`: `All`, `Tenant`, `Range`.
- When `scope=All`, focus on `data.require_login`; when `scope=Range`, read `users` / `departments` / `chats` / `apply_config` (`apply_config.approvers` contains only one user open_id).

<a id="agent-规则"></a>
## Agent rules

When explaining to the user, map as follows: `All` = public, `Tenant` = tenant, `Range` = specific; summarize `Range` grouped by user, department, and group before presenting. When the user wants to modify, go to [`+access-scope-set`](lark-apps-access-scope-set.md).
