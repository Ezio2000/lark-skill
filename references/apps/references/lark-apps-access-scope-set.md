# apps +access-scope-set

Set the runtime visibility scope of a Miaoda app. For runtime command facts, `lark-cli apps +access-scope-set --help` prevails.

<a id="何时用"></a>
## When to use

Use this to modify an app's runtime visibility scope. Do not treat it as development collaborator management; only route here when the user says "who can access/open/use the app".

<a id="命令骨架"></a>
## Command skeleton

- Required: `--app-id`, `--scope`.
- `--scope` enum: `specific` / `public` / `tenant`.
- `specific` requires `--targets`, and JSON array elements take the form `{"type":"user|department|chat","id":"..."}`.
- `specific` optionally takes `--apply-enabled` and `--approver`; `--approver` must be used together with `--apply-enabled`, and only one user open_id may be passed (server-side restriction).
- `public` must explicitly pass `--require-login=true|false`.
- `tenant` does not allow extra target/apply/login flags.

<a id="示例"></a>
## Examples

```bash
lark-cli apps +access-scope-set --app-id app_xxx --scope tenant

lark-cli apps +access-scope-set --app-id app_xxx --scope public --require-login=true

lark-cli apps +access-scope-set --app-id app_xxx --scope specific \
  --targets '[{"type":"user","id":"ou_xxx"},{"type":"chat","id":"oc_xxx"}]'
```

<a id="输出契约"></a>
## Output contract

- On success, `data` may be empty; summarize the result for the user based on the `--scope` and targets that were executed.
- Mutually exclusive parameter errors fail during local validation and no request is sent.

<a id="agent-规则"></a>
## Agent rules

This is the runtime access scope, not development collaborator permissions. Before narrowing the visibility scope, explain the impact to the user, and confirm the target users, departments, or groups before executing.

If the server returns "the app is not published / it must be published before the visibility scope can be set", relay this situation to the user and ask whether to publish now; only after receiving consent, run `+release-create`. Do not treat this hint as an instruction to publish automatically.

When the user provides names, department names, or group names, first resolve them into IDs before assembling `--targets`: person name → `ou_` using `lark-cli contact +search-user --query <名字>`, group name → `oc_` using `lark-cli im +chat-search --query <群名>`, department → `od-` via contact/address book. When there are multiple candidates, show the names and IDs for the user to choose; do not ask the user to manually fill in `ou_` / `od-` / `oc_`.
