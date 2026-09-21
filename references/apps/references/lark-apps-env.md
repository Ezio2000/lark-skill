# apps env


管理妙搭应用环境变量。查看用 `+env-list`，设置用 `+env-set`，删除用 `+env-delete`。没有单变量 get 命令；要确认某个 key 是否存在，使用 list 后用 `--jq` 过滤。

环境 flag 使用 `--environment`；不要使用旧的 `--env`，也不要使用短选项。

## 查看

`+env-list` 默认查 dev，且默认不返回 value。只有显式传 `--include-values` 后，响应中才可能出现变量值；不要在公开日志里展示带值输出。

接口契约：list 使用 `POST env_vars`，body 固定包含 `env` 和 CLI 场景 `scene=2`；set 使用 `POST create_or_update_env_var`；delete 使用 `POST delete_env_vars`。`--include-values` 只控制 CLI 输出是否展示 value，不作为服务端查询参数发送。

```bash
lark-cli apps +env-list --app-id <app_id>
lark-cli apps +env-list --app-id <app_id> --environment online
lark-cli apps +env-list --app-id <app_id> --include-values --jq '.data.items[] | select(.key == "FOO")'
```

## 设置

dev 环境设置不需要 `--yes`。设置 online 环境需要人类确认并显式传 `--yes`；如果当前会话已明确授权同一 app、环境、key 和 value，视为已授权，直接带 `--yes`，不要再次追问。`--dry-run` 可用于预览请求且不需要 `--yes`。变量值支持直接传 `<value>`，也支持 `@file` 或 stdin 输入。

回复中只说明 app/env/key 和执行结果；不要回显真实 value。需要举例时使用 `<value>`、`@file` 或 stdin。

```bash
lark-cli apps +env-set --app-id <app_id> --key FOO --value <value>
lark-cli apps +env-set --app-id <app_id> --key FOO --value @./secret.txt
lark-cli apps +env-set --app-id <app_id> --environment online --key FOO --value <value> --dry-run
lark-cli apps +env-set --app-id <app_id> --environment online --key FOO --value <value> --yes
```

## 删除

`+env-delete` 是 high-risk-write。核对会话授权覆盖 app、environment 和 key 后传 `--yes`；已有授权可跨轮次和认证恢复沿用。范围不清楚时先用只读查询或 dry-run 准备具体请求，再询问所缺选择。

```bash
lark-cli apps +env-delete --app-id <app_id> --key FOO --dry-run
lark-cli apps +env-delete --app-id <app_id> --key FOO --yes
lark-cli apps +env-delete --app-id <app_id> --environment online --key FOO --yes
```

## 反模式

- 不要把 `+env-pull` 当成环境变量管理命令；它只是刷新本地 `.env.local` 的兜底工具。
- 不要为了看一个变量臆造名为 env-get 的 apps shortcut；用 `+env-list --include-values` 加 `--jq`。
- 不要把真实 secret 写进示例或对话输出；需要示例时使用 `<value>`、`@file` 或 stdin。
