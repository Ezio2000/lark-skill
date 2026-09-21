
# approval approvals search

Search for approval definitions that **the current user can initiate** (launchable approvals). This is a read-only operation and does not create approval instances.

Required scopes: ["approval:approval:read"]

<a id="命令"></a>
## Command

```bash
# Search launchable approval definitions by keyword
lark-cli approval approvals search --data '{"keyword":"请假"}' --as user

# Paginate using page_token
lark-cli approval approvals search --data '{"keyword":"请假", "page_token":"example_page_token"}' --as user

# Output in table format for quick browsing of candidate definitions
lark-cli approval approvals search --data '{"keyword":"出差"}' --format table --as user

# Preview the API call without executing it
lark-cli approval approvals search --data '{"keyword":"请假"}' --as user --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--data '{...}'` | Yes | Query parameters, passed in as JSON |
| `keyword` | Yes | Search keyword, for example `请假`, `报销`, `出差`, `采购` |
| `locale` | No | Return language, for example `zh-CN`, `en-US`, `ja-JP` |
| `page_size` | No | Page size |
| `page_token` | No | Pagination token; leave empty on the first request, then use the `page_token` returned by the previous request |
| `--as user` | No | It is recommended to explicitly specify the user identity; "launchable approval definitions" is a query scoped to the current user |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call without executing it |

<a id="这个命令解决什么问题"></a>
## What problem does this command solve

When the user only has a natural-language intent and does not yet have an `approval_code`, use this first to find "candidate launchable approval definitions".

Typical scenarios:

- "Help me find the leave approval"
- "What reimbursement forms can be initiated?"
- "First search for the business trip approval, then help me submit the request"

<a id="输出重点字段"></a>
## Key output fields

In the returned results, focus on the following fields first:

| Field | Description |
|------|------|
| `approval_code` | Approval definition Code; both `approvals get` and `instances create` will need it later |
| `approval_name` | Approval definition name; most important when presenting candidates to the user for selection |
| `is_external` | Whether it is a third-party approval definition; `true` means it cannot go through the native `instances.create` |
| `create_link` | The initiation link for a third-party approval definition; when `is_external=true`, return it to the user first |

<a id="使用规则"></a>
## Usage rules

- **This is the first step of the approval initiation workflow.** The standard order is: `approvals search` -> `approvals get` -> `instances create`.
- **When the search result is empty, do not guess.** Directly tell the user that there is no launchable definition under the current keyword, and suggest that the user try a different keyword.
- **When multiple results match, do not make the decision for the user.** First list the candidate definitions and let the user choose the target approval definition.
- **When `is_external=true`, do not call `approval instances create`.** Such definitions are third-party approvals; return `create_link` first and explain that it needs to be initiated through the link.
- **Only for native definitions with `is_external=false` should you continue to `approvals get`.**
- **If the user has already explicitly provided `approval_code`, do not search again.** Directly execute `approval approvals get`.

<a id="结果整理方式"></a>
## How to organize the results

**Organize the results into a candidate list, prioritizing "name + approval_code + whether it is a third-party definition + next-step suggestion".**

It is recommended to output in the following structure:

```text
Found 3 launchable approval definitions:

1. Leave Request
   - approval_code: 7C468A54-8745-2245-9675-08B7C63E7A85
   - is_external: false
   - next: You can continue to read the definitions details (approvals get)

2. Travel Reimbursement
   - approval_code: 99887766-xxxx
   - is_external: true
   - next: Return create_link and guide the user to initiate through the link
```

<a id="常见后续操作"></a>
## Common follow-up operations

<a id="1用户选中了某个定义继续查看详情"></a>
### 1) The user selected a definition; continue to view details

```bash
lark-cli approval approvals get --params '{"approval_code":"<APPROVAL_CODE>"}' --as user
```

<a id="2确认是原生定义后再准备发起审批实例"></a>
### 2) After confirming it is a native definition, prepare to initiate an approval instance

```bash
lark-cli approval instances create --data '{"approval_code":"<APPROVAL_CODE>","form":"[...]"}' --as user --yes
```

<a id="3确认是三方定义时直接返回链接"></a>
### 3) When confirming it is a third-party definition, directly return the link

When `is_external=true`, prioritize returning `create_link` to the user, explaining that this approval needs to be initiated in the third-party system or on a redirect page, rather than through the native `instances.create`.
