# Lark 统一技能

一个技能入口，按需读取 24 个业务模块。覆盖文档、云空间、表格、会议、消息、邮箱、审批、日程、任务和妙搭等飞书能力。基于官方资料整理，属于社区修改版；来源、固定版本与 MIT 许可见 [SOURCES](SOURCES.md) 和 [LICENSE](LICENSE)。

项目由 [Ezio2000/lark-skill](https://github.com/Ezio2000/lark-skill) 管理。当前是重构预览版，不代表所有线上业务已验收。

## 语言分工

中文用于本 README、来源说明和用户界面文案；英文用于 `SKILL.md`、全部 24 个模块入口、详细执行参考、XML 说明及脚本中的说明性注释。用户内容、示例字面量、资源名称和兼容锚点保留原语言，助手仍按用户语言回复。

详细参考正文已完成英文化，仍按需加载，不把全部参考塞入技能入口。语言检查区分执行说明与中文界面文案、字段名和示例数据，不以清除所有汉字为目标。

## 安装与使用

需要可用的 `lark-cli`；本版本以 **1.0.96** 为核对基线，不声称已兼容所有后续版本。安装 CLI 可参考 [官方说明](https://github.com/larksuite/cli/tree/v1.0.96#installation--quick-start)。已有可用 CLI 时无需重新安装或登录。

把本目录整体复制到宿主读取的技能目录，目录名保持 `lark`。例如 Codex 可使用 `~/.agents/skills/lark`，Claude Code 可使用 `~/.claude/skills/lark`。同一宿主只保留一个可发现的 Lark 入口，不同时安装旧的拆分技能或 `lark-suite`。已有目录时先比较差异，不盲目覆盖。

仓库已公开，可先克隆到任意开发目录，再复制到技能目录或建立名为 `lark` 的符号链接；不要直接将仓库名 `lark-skill` 当作技能名：

```sh
git clone https://github.com/Ezio2000/lark-skill.git
```

```sh
lark-cli --version
```

通过 `$lark` 或飞书任务自然触发。首次使用需要配置或授权时，按 [认证模块](references/shared/index.md) 操作；不会因普通业务请求预先申请所有权限。

示例：读取一个飞书文档、查看今天的日程与待办、总结某段时间的会议、修改明确指定的表格区域。普通本地开发或设计不会自动切换到妙搭。

## 加载结构

`SKILL.md` 只提供通用规则和路由；`references/<domain>/index.md` 选择具体操作；详细参考、脚本和素材需要时才读取。业务任务无需读取本 README、来源文件或全部模块。

## Python 与路径

仅 CLI 业务不需要 Python。运行附带的 Python 辅助脚本需要 **uv + Python 3.11 或以上**，通过 uv 管理环境，不使用系统 Python 或 pip。

本目录包含 `pyproject.toml` 与 `uv.lock`。在项目根目录准备验证环境：

```sh
uv sync --locked --group dev
```

大部分辅助脚本只依赖标准库；`references/sheets/scripts/lark_sheets_df.py` 使用 pandas，需要额外启用 `dataframe`：

```sh
uv sync --locked --extra dataframe
```

模块示例中的 `scripts/`、`assets/` 指该模块的目录，不是当前任务目录。不要为了定位脚本改变任务 cwd；可使用脚本的完整路径。下面的 `<lark-root>` 替换为实际安装路径：

```sh
uv run --project "<lark-root>" --locked python "<lark-root>/references/slides/scripts/iconpark_tool.py" search --query "增长"
```

使用 pandas 的脚本在上述命令加 `--extra dataframe`。`--project` 选择依赖环境而不改变 cwd；CLI 对 `@file` 和输出路径的限制仍以具体命令为准。本文 shell 示例面向 bash/zsh；PowerShell 使用同等 argv 调用，避免直接照搬 heredoc。

## 验证

在项目根目录执行：

```sh
uv run --locked python scripts/check_skill.py --english
uv run --locked --extra dataframe python -m unittest discover -s tests -p 'test_*.py'
uv run --locked python -m unittest discover -s references/slides/scripts -p '*_test.py'
```

第一项检查唯一入口、模块路由、本地文件及章节链接、Markdown 代码块、英文说明覆盖、Python 语法和资源结构；第二项验证检查器、上游差异工具和可选 DataFrame 协议转换；第三项是继承的幻灯片脚本测试。这些检查不登录、不发送消息、不修改飞书资源，也不证明所有线上接口均已通过验证。GitHub Actions 配置复用这些命令，覆盖 Linux / Windows 和 Python 3.11 / 3.14；工作流是否通过以实际运行结果为准。

[行为场景](tests/scenarios.json) 用于独立前向评估：把每个场景的 `request` 与 `context` 单独交给评估者，只提供本技能和模拟数据，隐藏 `expected`；记录其实际选择的模块、读取文件和计划执行的动作，再对照预期。评估中禁止真实远端调用。文字检查不能替代这类行为评估或真实业务验收。

## 维护

上游同步按 [SOURCES](SOURCES.md) 执行，只更新有差异的操作说明。CLI 更新可能重新安装上游技能；更新后需要核对技能目录，避免出现重复入口。保留本技能副本并手动合并，不把更新提示视作自动安装授权。

本包不附带账号、token 或租户配置，使用本机 CLI 已有配置。测试和示例中的占位 ID 不可用于实际业务调用。

代码变更使用 Git 提交和 Pull Request；缺陷、未完成迁移和业务验收范围使用 GitHub Issues 跟踪。提交前运行上述离线检查，合并前查看 Actions 的实际结果。发布前确认语言覆盖、目标 CLI 版本和已完成的线上验收范围，再创建版本标签；不要把离线测试通过等同于完整发布验收。
