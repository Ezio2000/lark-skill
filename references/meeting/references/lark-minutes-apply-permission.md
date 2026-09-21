# minutes +apply-permission

Initiate a request to the Minutes owner for view or edit permission. **Write operation**, only call it when the user explicitly asks to apply for permission; calling it does not mean permission is granted immediately, it only submits a request.

This module corresponds to shortcut: `lark-cli minutes +apply-permission` (calls `POST /open-apis/minutes/v1/minutes/{minute_token}/permissions/apply`). Supports `--as user` / `--as bot`.

<a id="命令"></a>
## Command

```bash
# Apply for view permission as user
lark-cli minutes +apply-permission --minute-token obcnxxxxxxxxxxxxxxxxxxxx --perm view --as user

# Apply for edit permission as bot
lark-cli minutes +apply-permission --minute-token obcnxxxxxxxxxxxxxxxxxxxx --perm edit --as bot

# Preview the API call
lark-cli minutes +apply-permission --minute-token obcnxxxxxxxxxxxxxxxxxxxx --perm view --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--minute-token <token>` | Yes | Minutes Token |
| `--perm <view\|edit>` | Yes | The permission to apply for: `view` (view) or `edit` (edit) |
| `--dry-run` | No | Preview the API call without executing |

<a id="user--bot-身份与权限语义"></a>
## user / bot identity and permission semantics

- **user**: Apply to the Minutes owner as the currently logged-in user. The owner receives a request notification in the Feishu client, and after approval that user obtains the corresponding permission.
- **bot**: Apply to the Minutes owner as the application, representing "this application" rather than a specific user. After approval the application (bot) obtains the corresponding permission, and the user who triggered the request does not obtain the permission themselves.
- The requests of the two identities do not represent each other: after a user-identity request is approved the bot still has no permission, and vice versa.

<a id="核心约束"></a>
## Core constraints

<a id="1-必须继承触发无权限错误的来源身份"></a>
### 1. Must inherit the source identity that triggered the no-permission error

`+apply-permission` is not a generic "request permission" button: it applies for the permission of **the identity corresponding to the current `--as`**. If `--as bot` encountered no permission while reading a Minutes, apply with `--as bot`; if `--as user` encountered no permission, apply with `--as user`. Do not switch to another identity when applying—that applies for the permission of a different subject and will not solve the problem of the original call.

<a id="2-missing-scope-与资源-acl-是两类不同问题"></a>
### 2. missing scope and resource ACL are two different kinds of problems

- **missing scope** (the current identity completely lacks scopes such as `minutes:permission:apply` / `minutes:minutes.basic:read`): this is not "no permission for this Minutes", and `+apply-permission` cannot solve it. `--as user` uses `auth login --scope` to add permission; `--as bot` goes to the developer console to enable it, and it is **forbidden** to execute `auth login` for the bot. For the complete rules see [lark-shared](../../shared/index.md).
- **resource ACL** (all scopes are present, but there is no view/edit permission for **this specific Minutes**): this is the scenario `+apply-permission` is meant to solve.

First check whether the error's `error.subtype` is `missing_scope` or a resource-level permission denial, then decide whether to call this command.

<a id="3-只有用户明确要求才发起申请"></a>
### 3. Only initiate a request when the user explicitly asks

When encountering a no-permission error, first inform the user of the fact that "the current identity has no permission for this Minutes"; only call this command when the user explicitly says "help me apply for view/edit permission". Do not automatically initiate a request after detecting no permission.

<a id="4-禁止通过切换身份绕过资源权限"></a>
### 4. Do not bypass resource permissions by switching identities

If `--as bot` has no permission for a certain Minutes, do not switch to `--as user` to re-read in order to "bypass" this restriction (unless the user explicitly agrees to switch identities to continue the task). Applying for permission and switching identities are two different things: the former solves the bot's own insufficient permission, the latter switches to a completely different subject to access the resource.

<a id="所需权限"></a>
## Required permissions

| Identity | Required permission |
|------|---------|
| user / bot | `minutes:permission:apply` |

<a id="输出结果"></a>
## Output result

```json
{
  "minute_token": "obcnxxxxxxxxxxxxxxxxxxxx",
  "perm": "view"
}
```

| Field | Description |
|------|------|
| `minute_token` | Minutes Token |
| `perm` | The permission applied for (`view` / `edit`) |

<a id="如何获取-minute_token"></a>
## How to obtain minute_token

| Source | How to obtain |
|------|---------|
| Minutes URL | Extract from the end of the URL, e.g. `https://sample.feishu.cn/minutes/obcnxxxxxxxxxxxxxxxxxxxx` |
| Minutes search | `lark-cli minutes +search --query "关键词"` |
| Meeting artifact query | `lark-cli vc +recording --meeting-ids <id>`, obtain `minute_token` (reuse the same `--as`) |

<a id="常见错误与排查"></a>
## Common errors and troubleshooting

| Error symptom | Root cause | Solution |
|---------|---------|---------|
| `--perm` is not `view`/`edit` | Invalid parameter value | Only `view` or `edit` can be passed |
| `missing required scope(s)` | The current identity lacks `minutes:permission:apply` | See "missing scope and resource ACL" above |
| Still no permission after applying | The owner has not yet approved | This is an asynchronous request, you need to wait for the owner to process it; it does not mean the command failed |

<a id="相关场景"></a>
## Related scenarios
- [Generate and modify Minutes](../scenes/create-and-edit-minutes.md)
