# minutes +todo

> **Routing**: This command operates on **AI todos within Minutes**, not Feishu Tasks (Task). When the user says "create a todo in Minutes", you **must** use this command, and **must not** use `lark-cli task` / `tasklists list` / `task +create`. See [Generate and modify Minutes](../scenes/create-and-edit-minutes.md) for details.


Add / update / delete todos in Minutes (single or batch). Write operation.

This module corresponds to shortcut: `lark-cli minutes +todo` (calls `POST /open-apis/minutes/v1/minutes/{minute_token}/todo`).

<a id="典型触发表达"></a>
## Typical trigger expressions

- "Add one/multiple todos to this Minutes"
- "Change a certain todo to..."
- "Mark a certain todo as completed / unmark completed"
- "Delete a certain todo"

<a id="命令"></a>
## Command

**Single mode**: `--operation` + corresponding fields.
**Batch mode**: `--todos` JSON array (mutually exclusive with single-item flags); a single request can mix `add` / `update` / `delete`.

```bash
# Single: add
lark-cli minutes +todo --minute-token obcnxxxxxxxxxxxxxxxxxxxx --operation add --todo "跟进预算审批" --is-done=false --as user

# Batch: add two at once
lark-cli minutes +todo --minute-token obcnxxxxxxxxxxxxxxxxxxxx --as user --todos '[{"operation":"add","content":"晚上好1","is_done":true},{"operation":"add","content":"晚上好2","is_done":false}]'

# Batch: mixed add/delete/update
lark-cli minutes +todo --minute-token obcnxxxxxxxxxxxxxxxxxxxx --as user --todos '[{"operation":"add","content":"新待办","is_done":false},{"operation":"update","todo_id":"1234567890","content":"已更新","is_done":true},{"operation":"delete","todo_id":"9876543210"}]'

# Read from file
lark-cli minutes +todo --minute-token obcnxxxxxxxxxxxxxxxxxxxx --as user --todos @todos.json

# Single: update / delete
lark-cli minutes +todo --minute-token obcnxxxxxxxxxxxxxxxxxxxx --operation update --todo-id 1234567890 --todo "整理会议纪要" --is-done --as user
lark-cli minutes +todo --minute-token obcnxxxxxxxxxxxxxxxxxxxx --operation delete --todo-id 1234567890 --as user

# Preview
lark-cli minutes +todo --minute-token obcnxxxxxxxxxxxxxxxxxxxx --operation add --todo "新待办" --is-done --dry-run --as user

# Add a todo and specify the assignee (the assignee is written into the --todo content as an inline @ mention; this is the established way Minutes todos indicate ownership)
lark-cli minutes +todo --minute-token obcnxxxxxxxxxxxxxxxxxxxx --operation add --todo "跟进预算审批 @张三" --is-done=false --as user
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--minute-token <token>` | Yes | Minutes Token |
| `--operation <op>` | Single mode | `add` / `update` / `delete`; mutually exclusive with `--todos` |
| `--todo <text>` | Single add/update | Todo plain text |
| `--is-done` | Single add/update | `--is-done` = true, `--is-done=false` = false |
| `--todo-id <id>` | Single update/delete | Existing todo id |
| `--todos <json>` | Batch mode | JSON array, supports `@file` / `@-`; mutually exclusive with single-item flags |
| `--dry-run` | No | Preview the API call without executing |

<a id="单条模式"></a>
## Single mode

| `--operation` | Required parameters | Forbidden parameters |
|---------------|----------|----------|
| `add` | `--todo` + `--is-done` | `--todo-id` |
| `update` | `--todo-id` + `--todo` + `--is-done` | — |
| `delete` | `--todo-id` | `--todo`, `--is-done` |

<a id="批量模式--todos"></a>
## Batch mode: `--todos`

Each element's fields are consistent with API `todo_items[]`:

| JSON field | add | update | delete |
|-----------|-----|--------|--------|
| `operation` | Required | Required | Required |
| `content` | Required | Required | Forbidden |
| `is_done` | Required | Required | Forbidden |
| `todo_id` | Forbidden | Required | Required |

Example `todos.json`:

```json
[
  {"operation": "add", "content": "晚上好1", "is_done": true},
  {"operation": "add", "content": "晚上好2", "is_done": false}
]
```

The array order is written into the request body as-is; the display order on the client may still be affected by completion status grouping.

<a id="核心约束"></a>
## Core constraints

<a id="1-先读后写待办-id-如何获取"></a>
### 1. Read before write: how to obtain the todo id

Before updating / deleting, first use `lark-cli minutes +detail --minute-tokens <token> --todo` to read the current todos. Each returned todo carries an `todo_id` field.

> The todo id is only used for internal programmatic location and does not need to be shown to the user.

<a id="2-待办内容为纯文本"></a>
### 2. Todo content is plain text

`content` is **not Markdown**; pass the todo description text directly.

<a id="3-负责人---提及既定写法必读"></a>
### 3. Assignee / `@` mention (established convention, must read)

When the user says "the assignee is so-and-so", the established convention is to append the assignee as an inline `@某某` into the `--todo` content:

- When the user has directly given a name (e.g. "the assignee is Zhang San"), **do not perform any lookup**; concatenate the original text as-is into the `--todo` content, written as plain text `@张三` (`--todo "xxx @张三"`).
- When the user says "the assignee is me", you **must** first obtain the current logged-in user's real name before concatenating; do not directly write the literal `@我`:
  - Execute `lark-cli contact +get-user --as user`, take the name field from the response as the real name, and concatenate it into `--todo "xxx @<真实姓名>"`.
  - If this step fails or the name cannot be obtained (no permission, error, etc.), **do not** write any `@` mention placeholder — directly create with the original todo text without the assignee suffix (`--todo "xxx"`), and do not keep the literal `@我`.
- **Do not** reroute to [lark-task](../../task/index.md) or perform further contact searches just to handle the assignee — the top priority is always to land this todo; name resolution only affects the appended `@` text and must never block or cancel todo creation.
- **Do not** use "who is the creator / under what identity it is created" as a substitute for the `@` mention — the `--as user`/`--as bot` identity used at creation and the "assignee" are two unrelated things; even if the current user's real name is known, it must be concatenated into the `content` text, and you must not fob the user off in the reply with statements like "creating under your identity means it belongs to you".
- In the reply, **do not** proactively mention or suggest switching to `lark-task` as an alternative for "wanting a clear assignee / assignable task" — the assignee the user mentions is merely a piece of text in this Minutes todo and is completely unrelated to Task; do not introduce Task and add to the user's confusion.
- The inline `@` is the established way Minutes todos indicate the assignee. The reply should only state the result (Minutes, todo content, assignee, completion status); **do not** include implementation-limit explanations or explanatory disclaimers such as "the interface only supports content and is_done", "there is no independent assignee field", or "so the assignee can only be written into the content".

**Result example**:

```bash
# Name resolution succeeded
lark-cli minutes +todo --minute-token obcnxxxxxxxxxxxxxxxxxxxx --operation add --todo "跟进预算审批 @王小明" --is-done=false --as user

# "me" resolution failed: do not write the @ mention, keep only the original content
lark-cli minutes +todo --minute-token obcnxxxxxxxxxxxxxxxxxxxx --operation add --todo "跟进预算审批" --is-done=false --as user
```

```json
{
  "minute_token": "obcnxxxxxxxxxxxxxxxxxxxx",
  "count": 1,
  "updated": true,
  "operation": "add"
}
```

The `content` field of this newly added todo in Minutes is the final concatenated text itself (`"跟进预算审批 @王小明"`, or `"跟进预算审批"` when resolution fails); neither the CLI nor this interface will, or needs to, convert it into a truly clickable user mention.

<a id="4-所需权限"></a>
### 4. Required permissions

| Identity | Required scope |
|------|-----------|
| user | `minutes:minutes:update` |

<a id="输出结果"></a>
## Output result

```json
{
  "minute_token": "obcnxxxxxxxxxxxxxxxxxxxx",
  "count": 2,
  "updated": true
}
```

Single mode additionally includes `"operation": "add"`.

<a id="常见错误与排查"></a>
## Common errors and troubleshooting

| Error symptom | Solution |
|---------|---------|
| No operation specified | In single mode pass `--operation`, or in batch pass `--todos` |
| `--todos` conflicts with single-item flags | Choose one of the two |
| `todos[i]` validation failed | Check that item's `operation` and field combination |
| `error.subtype` = `permission_denied` | **No edit permission on the Minutes resource**: request edit/collaboration permission for that Minutes from its owner; **do not** go through `auth login --scope` |
| `error.subtype` = `quota_exceeded` | **The ASR/AI quota was exhausted when this Minutes was generated**, so the AI todos were not fully generated and todo changes cannot be persisted: have the user check the quota details on that Minutes' detail page; the CLI cannot top up quota, and retrying will not succeed |
| Missing OAuth scope (`error.missing_scopes` contains `minutes:minutes:update`) | `lark-cli auth login --scope "minutes:minutes:update"` |

<a id="相关场景"></a>
## Related scenarios
- [Generate and modify Minutes](../scenes/create-and-edit-minutes.md)
