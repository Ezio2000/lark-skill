# apps cache 域命令（应用运行时缓存调试）

调试妙搭应用的运行时缓存：查看某个缓存 key 的内容、删除单个 key、清空某个环境的全部缓存。缓存是应用为了加速而临时存放的数据，删除或清空后，应用下次用到时会自动重新取最新数据。命令事实以 `lark-cli apps +<cmd> --help` 为准；认证、`--as user`、exit 码、`_notice` 等通用处理见 [`../../shared/index.md`](../../shared/index.md) 与本域 [`index.md`](../index.md)。

## 何时用

用户要排查「某个缓存 key 里存的是什么 / 有没有命中」、想删掉某个 key 让应用下次拿到最新数据、或想清空某个环境的缓存做快速恢复时。

## 命令一览

| 命令 | 做什么 | 关键参数 |
|---|---|---|
| `+cache-get` | 查一个缓存 key 的内容与信息 | `--key`、`--environment`、`--format` |
| `+cache-delete` | 删一个缓存 key（重复删不会报错；不需 `--yes`） | `--key`、`--environment` |
| `+cache-clear` | 清空指定环境下的全部缓存（CLI 要求 `--yes`，授权沿用会话） | `--environment`、`--yes` |

> 所有命令都需 `--app-id`。

## 约定（先读）

- **环境 `--environment dev|online`（可省略）**：缓存按运行环境隔离。不指定时按应用当前的环境配置自动选择——有多环境的应用默认落到开发环境 `dev`，没有多环境的就是线上 `online`；返回结果里的 `environment` 会告诉你这次实际操作的是哪个环境。想固定就显式传。
- **缓存 key 用 `--key` 传**：传业务里使用的那个 key；是否合法（非空、长度等）由服务端校验，不合法会返回错误。
- **风险分级**：`+cache-clear` 会清掉整个环境的缓存，是高危操作，不带 `--yes` 会被确认关卡拦下，执行前核对已有授权是否包含该应用与环境（判据见 [+cache-clear](#cache-clear高危)）；`+cache-delete` 只删单个 key、影响小，不需 `--yes`。
- **`+cache-get` 的内容有两种展示**：`--format json`（默认）原样返回缓存内容，适合精确比对；`--format pretty` 会把内容格式化展开，更便于阅读。

## 各命令

### +cache-get
按 `--key` 查单个缓存。命中时返回：是否存在、剩余有效期（TTL）、内容及其大小；未命中（或已过期）时只返回 `exists=false`、不带内容。

> 每次查询都会连内容一起返回（没有「只看信息、不取内容」的模式），内容可能较大——只是想确认「在不在 / 还有多久过期」时，留意别占用太多上下文。

```bash
lark-cli apps +cache-get --app-id app_xxx --key spotbonus:2026:winners:list:v1
lark-cli apps +cache-get --app-id app_xxx --environment online --key <key> --format pretty
```

### +cache-delete
删一个缓存 key。**重复删、或删一个本就不存在的 key，都算成功**（返回 `deleted_key_count=0`）、不会报错；删中则返回 `deleted_key_count=1`。删掉后应用下次会自动重新取最新数据，影响小，故不需 `--yes`。

**响应里的 `deleted_key_count` 别读错**——它是「本次是否真的删掉了东西」的唯一判据：

| `deleted_key_count` | 含义 | 该怎么向用户表述 |
|---|---|---|
| `1` | 命中并删掉了 | 「已删除该 key」 |
| `0` | 请求成功，但没有删掉任何 key——这个 key **本来就不存在或已过期** | 「该 key 原本就不存在／已过期，无需删除」——**不要说成「已成功删除」** |

要证明「删除生效了」，用「删前 `+cache-get` 确认存在 → `+cache-delete` 拿到 `deleted_key_count=1` → 删后 `+cache-get` 得到 `exists=false`」这条链；只靠删后一次 miss 是不够的，因为 key 从一开始就不存在时（`deleted_key_count=0`）结果完全一样。

```bash
lark-cli apps +cache-delete --app-id app_xxx --environment dev --key <key>
```

### +cache-clear（高危）
清空当前应用在**指定环境**下的全部缓存，用于定位不到具体 key 时的快速恢复。影响面是整个环境，必须带 `--yes`；返回本次清除的 key 数量。

清空前确定应用、环境和“全部缓存”的范围。用户已明确要求清空指定应用的指定环境时，可以首次调用就带 `--yes`；不需要再说“确认”二字。只说“清一下缓存”且环境无法从上下文确定时，先询问环境。已有授权在后续轮次和认证恢复后仍有效，除非目标或影响发生变化。

可用 `--dry-run` 核对请求；exit 10 按 [确认参数处理](../../shared/references/lark-shared-high-risk-approval.md) 处理。不要依赖服务端自动选择写入环境。

```bash
# 1) 未确认：只预览，不清理（--dry-run 不触发门禁、不产生真实动作）
lark-cli apps +cache-clear --app-id app_xxx --environment online --dry-run

# 2) 用户确认后：补 --yes 执行
lark-cli apps +cache-clear --app-id app_xxx --environment dev --yes
```

## 错误与边界

- **key 不合法 / 缓存服务暂时不可用**：命令会返回带说明的错误，按 `error.hint` 转述给用户；「服务暂时不可用」这类可稍后重试。

## Agent 规则

- **写操作先定环境**：`+cache-clear` / `+cache-delete` 不指定 `--environment` 时会落到自动选中的环境——**没有多环境的应用会直接作用到线上 `online`（生产）**。不确定应用有没有多环境时，写操作显式传 `--environment`；纯查看（`+cache-get`）影响小，可以省略。
- **清空必须显式带环境**：具体应用、环境和清空范围已获授权时直接执行；缺少范围时只做预览或询问。
- **排查缓存内容优先用 `+cache-get`**：想看结构化、易读的内容用 `--format pretty`；想拿原始内容做精确比对用默认 JSON。
- **删 key 前先对齐 key**：用户只描述了业务含义、没给准确 key 时，先确认再删——删错影响也有限（应用会自动重建），但仍应避免误删。
