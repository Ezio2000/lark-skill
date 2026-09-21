# apps +create

Create a Miaoda app. For runtime command facts, `lark-cli apps +create --help` is authoritative.

<a id="何时用"></a>
## When to use

Use it to create an app asset and obtain `app_id`. It is not responsible for handing natural-language requirements to the cloud Agent: when the user wants to "help me generate/iterate an app", first create the app according to the `--app-type` determined by "Choose a development path" in index.md (has database requirements → `full_stack`; pure frontend interaction with no database mentioned → default `frontend`), then go to [`lark-apps-cloud-dev.md`](lark-apps-cloud-dev.md) and use `+session-create` / `+chat` to submit the requirement.

<a id="命令骨架"></a>
## Command skeleton

- Required: `--name`, `--app-type`.
- app type values are lowercase `html` / `frontend` / `full_stack`; the framework validates exactly against the enum (no case normalization), and invalid values error out directly.
- Optional: `--description`, `--icon-url`.

<a id="示例"></a>
## Examples

```bash
lark-cli apps +create --name "客户调研问卷" --app-type html

lark-cli apps +create --name "JSON 格式化工具" --app-type frontend \
  --description "纯前端交互工具，无需数据库"

lark-cli apps +create --name "审批系统" --app-type full_stack \
  --description "部门审批系统，支持登录、提交申请、多级审批"

lark-cli apps +create --name "Demo" --app-type html --dry-run
```

<a id="输出契约"></a>
## Output contract

- On success, read `data.app.app_id` from the default JSON envelope; you can also use `data.app.name` / `description` to confirm the result with the user.
- pretty output is only suitable for human viewing; when subsequent commands need app_id, use JSON or `--jq '.data.app.app_id'`.

<a id="app-type-与命名"></a>
## app type and naming

- For `--app-type` values and decision signals, see "Choose a development path" in index.md; not repeated here.
- When the user only provides a natural-language requirement, generate a concise `--name` and a one-sentence `--description` from it and create directly; if unsatisfied, use `+update` to change it.

After creation, continue according to the user's path:

- Local app development (including html / frontend / full_stack): read [`lark-apps-local-dev.md`](lark-apps-local-dev.md).
- Cloud Agent generation/iteration: read [`lark-apps-cloud-dev.md`](lark-apps-cloud-dev.md).
