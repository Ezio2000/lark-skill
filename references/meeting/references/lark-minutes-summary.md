# minutes +summary


Replace the AI summary content of a Minutes. This is a write operation and will overwrite the current summary.

This module corresponds to shortcut: `lark-cli minutes +summary` (calls `PUT /open-apis/minutes/v1/minutes/{minute_token}/summary`).

<a id="典型触发表达"></a>
## Typical trigger expressions

- "Change the summary of this Minutes to..."
- "Update / replace the AI summary of a Minutes"
- "Correct the summary content and write it back to the Minutes"

<a id="命令"></a>
## Command

```bash
# Pass the summary content directly (Markdown subset)
lark-cli minutes +summary --minute-token obcnxxxxxxxxxxxxxxxxxxxx --summary "**会议结论**\n- 方案 A 通过\n- 下周跟进排期"

# Read the summary content from a file
lark-cli minutes +summary --minute-token obcnxxxxxxxxxxxxxxxxxxxx --summary @summary.md

# Read from stdin
echo "**结论**" | lark-cli minutes +summary --minute-token obcnxxxxxxxxxxxxxxxxxxxx --summary @-

# Preview the API call
lark-cli minutes +summary --minute-token obcnxxxxxxxxxxxxxxxxxxxx --summary @summary.md --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--minute-token <token>` | Yes | Minutes Token |
| `--summary <text>` | Yes | The replacement summary content, supports `@file` / `@-` (stdin) |
| `--dry-run` | No | Preview the API call without executing |

<a id="核心约束"></a>
## Core constraints

<a id="1-先读后写"></a>
### 1. Read before write

Before replacing, it is recommended to first use `lark-cli minutes +detail --minute-tokens <token> --summary` to read the current summary and confirm that the `minute_token` and the content to be replaced are correct.

<a id="2-markdown-展示说明"></a>
### 2. Markdown display notes

The API accepts any summary text and **will not reject the request due to Markdown format validation failure**. The Minutes client can usually only render the following Markdown subset well; unsupported syntax (such as links, code blocks, level-4 headings, etc.) will be **displayed as raw text** (the Markdown marker characters are preserved and will not be rendered into the corresponding style). When writing, the Agent should prefer displayable syntax to avoid users seeing literal `[链接](url)`, `` `code` ``, etc. in the Minutes:

| Supported | Syntax | Example |
|------|------|------|
| Plain text | Ordinary paragraph | `本次会议讨论了 Q2 预算` |
| Line break | `\n` or blank line | Write in separate paragraphs |
| Level-1 heading | `# ` + heading text | `# 会议结论` |
| Level-2 heading | `## ` + heading text | `## 行动项` |
| Level-3 heading | `### ` + heading text | `### 跟进事项` |
| Bold | `**文字**` | `**重点结论**` |
| Unordered list | `- ` or `* ` | `- 跟进预算审批` |
| Ordered list | `1. ` | `1. 确认需求` |

> Heading syntax recommendation: keep a space after `#`, and prefer levels 1 to 3 (`#` / `##` / `###`). Level 4 and above (`####`) cannot be rendered and will be displayed as raw text.

**Not recommended** (will be displayed as raw text): links, images, code blocks, tables, blockquotes, italics, strikethrough, level-4 and above headings, etc.

Valid example:

```markdown
# Meeting conclusions

## Core discussion

**方案 A 通过**，下周启动排期。

### To follow up
- 预算审批
- 排期确认

1. 张三负责预算
2. 李四负责排期
```

<a id="3-所需权限"></a>
### 3. Required permissions

| Identity | Required permission |
|------|---------|
| user | `minutes:minutes:update` |

<a id="输出结果"></a>
## Output result

```json
{
  "minute_token": "obcnxxxxxxxxxxxxxxxxxxxx",
  "updated": true
}
```

| Field | Description |
|------|------|
| `minute_token` | Minutes Token |
| `updated` | Whether the update succeeded |

<a id="如何获取-minute_token"></a>
## How to obtain minute_token

| Source | How to obtain |
|------|---------|
| Minutes URL | Extract from the end of the URL, e.g. `https://sample.feishu.cn/minutes/obcnxxxxxxxxxxxxxxxxxxxx` |
| Minutes search | `lark-cli minutes +search --query "关键词"` |
| Meeting artifact query | `lark-cli vc +detail --meeting-ids <id>` or `vc +recording`, get `minute_token`, then go through `minutes +detail` |

<a id="常见错误与排查"></a>
## Common errors and troubleshooting

| Error symptom | Error code | Root cause | Solution |
|---------|--------|---------|---------|
| Summary displayed as raw Markdown text | — | The summary contains syntax that the Minutes client cannot render, such as links or level-4 headings | Switch to displayable formats such as headings (# to ###), bold, and lists; the API will not error because of this |
| Invalid parameter | — | `minute_token` is missing or malformed | Check whether the token is complete |
| Insufficient permission | — | Missing `minutes:minutes:update` | Run `auth login --scope "minutes:minutes:update"` |
| `error.subtype` = `quota_exceeded` | 2091008 | When this Minutes was generated, the ASR/AI quota was already exhausted, the AI summary was not fully generated, and the replacement cannot be persisted | Ask the user to check the quota details on the Minutes detail page; the CLI cannot add quota, and retrying will not succeed |

<a id="相关场景"></a>
## Related scenarios
- [Generate and modify Minutes](../scenes/create-and-edit-minutes.md)
