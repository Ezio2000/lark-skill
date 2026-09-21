# 来源与维护边界

本项目是飞书官方技能的社区整合与修改版，不是飞书官方发布的技能包。

## 上游基线

- 仓库：[larksuite/cli](https://github.com/larksuite/cli)。
- 基线：`v1.0.96`，commit [`cb5a3d704379552dc61e37898e5f74798783190d`](https://github.com/larksuite/cli/tree/cb5a3d704379552dc61e37898e5f74798783190d)。
- 来源范围：该 commit 的 `skills/lark-*/`，28 个目录、550 个文件。
- 核对日期：2026-09-21。整合前本地 550 个文件与固定 commit 的对应文件逐字节相同；不是根据当前 main 推定版本。
- 上游采用 [MIT License](https://github.com/larksuite/cli/blob/cb5a3d704379552dc61e37898e5f74798783190d/LICENSE)，本目录保留原版权声明，整合修改也按 MIT 提供。

## 本地改动

`skills/lark-<domain>/SKILL.md` 转为 `references/<domain>/index.md`，其余资源保留模块内相对布局。`lark-vc`、`lark-vc-agent`、`lark-note`、`lark-minutes` 四个纯转发入口合并到 meeting，不复制四份别名文件。CLI 内嵌文档仍使用原来的模块名。

修改包括统一路由、24 个英文模块入口、修复引用、合并通用授权规则、简化普通文档创作、限制非请求的妙搭发布，以及 uv 依赖管理和维护检查。清理幻灯片的强制设计偏好，修复日程嵌套重叠检查、会议内容总结路径和 Wiki 同名空间分页问题。详细参考仍有上游中文，迁移范围见 README。命令说明中的版本号、参数和平台限制继承自上游基线；真实使用遇到差异时以当前 CLI 的精确 help/schema 为准。

## 同步上游

不要将新上游目录直接覆盖本技能。分别取得上述基线和候选版本的 checkout，在本项目根目录执行：

```sh
uv run --locked python scripts/upstream_diff.py /path/to/baseline /path/to/candidate
```

工具只读取两份 checkout，向 stdout 输出新增、修改、删除文件及本地对应路径。它不执行安装、升级、删除或自动合并。按差异更新受影响模块，保留本地通用规则与路径；确认兼容性后更新本文件的基线，并重跑 README 中的检查。

外部链接中的 SDK、字体、图片 CDN 和模型服务没有被打包进本项目；本许可不代表对这些服务或远端内容另行授权。
