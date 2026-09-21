# 更新与 _notice

本地使用自维护的单技能 `lark`，业务资料在 `references/<domain>/`。CLI 自带的 `lark-suite` 是另一个受 CLI 管理的布局名称，不是本技能的别名。

`_notice.update`、`_notice.skills` 或废弃命令提示不应中断业务任务，也不授权自动升级、安装或恢复已删除的拆分技能。先完成用户请求；只有用户询问或需要升级时再处理。

核对当前 CLI 文档时可直接读取内嵌资料：

```bash
lark-cli skills read lark-doc references/lark-doc-fetch.md
lark-cli skills list
lark-cli update --help
```

内嵌文档随二进制构建，不包含脚本、素材。用它核对命令差异，按需更新本技能对应模块，保留本地路径、统一入口和用户规则。

用户要求升级时，先核实安装方式及当前 `update --help`。当前 CLI 的 update 会涉及 AI Skills，并提供 `--skills-layout separate|suite`：不要默认执行后留下拆分技能，也不要在 `lark` 旁再留下重复的 `lark-suite`。需要运行 CLI 管理的更新时，在临时目录保存本技能，升级后检查实际生成目录，将必要变更合并回本技能并移除本次生成的重复入口。不要覆盖无关技能或个人修改。

`_notice.deprecated_command` 的 replacement 可用于下一次同类调用，先确认参数兼容；无需因此重做已成功的操作。

需要稳定 JSON 时，可以仅为该次命令设置：

```bash
LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1 <lark-cli command>
```
