# minutes +update


Modify the title (topic) of a Feishu Minutes.

This module corresponds to shortcut: `lark-cli minutes +update`.

<a id="典型触发表达"></a>
## Typical trigger expressions

- "Change the title of this Minutes to xxx"
- "Rename this Minutes"
- "Modify the Minutes title"

<a id="命令示例"></a>
## Command example

```bash
lark-cli minutes +update --minute-token xxx --topic "周会纪要 2026-05-18"
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--minute-token <token>` | Yes | The unique identifier of the Minutes, which can be extracted from the trailing path of the Minutes URL |
| `--topic <string>` | Yes | The new Minutes title |

<a id="认证与权限"></a>
## Authentication and permissions
- Required scope: `minutes:minutes:update`.

<a id="输出结果"></a>
## Output result

| Field | Description |
|------|------|
| `minute_token` | The modified Minutes Token, which is consistent with the input `--minute-token` and can continue to be used to query Minutes information, download media, or obtain Minutes artifacts |
| `topic` | The modified Minutes title, which is consistent with the input `--topic` |

<a id="相关场景"></a>
## Related scenarios
- [Generate and modify Minutes](../scenes/create-and-edit-minutes.md)
