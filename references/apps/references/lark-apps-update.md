# apps +update

Partially update Miaoda app metadata. For runtime command facts, refer to `lark-cli apps +update --help`.

<a id="何时用"></a>
## When to use

Only update app display metadata. When the user wants to change code, published content, visibility scope, or the database, do not use `+update`.

<a id="命令骨架"></a>
## Command skeleton

- Required: `--app-id`.
- Provide at least one of: `--name` or `--description`.
- Only the fields provided by the user are sent; fields not provided are not cleared.

<a id="示例"></a>
## Examples

```bash
lark-cli apps +update --app-id app_xxx --name "审批系统"
lark-cli apps +update --app-id app_xxx --description "用于部门审批流转"
lark-cli apps +update --app-id app_xxx --name "审批系统" --description "用于部门审批流转" --dry-run
```

<a id="输出契约"></a>
## Output contract

- On success, read `data.app`; the response is the complete app object, not just the modified fields.
- Missing `--app-id` or not providing `--name` / `--description` will fail local validation.

<a id="agent-规则"></a>
## Agent rules

Before updating, restate the fields to be changed; do not add default values for fields the user did not mention. After execution, only relay the new name/description and app_id; there is no need to expand the raw response.
