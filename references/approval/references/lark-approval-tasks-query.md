
# approval tasks query

Query the current user's approval task list; can be used to view groups such as to-do, done, and notified. Read-only operation; does not modify approval status.

Required scopes: ["approval:task:read"]

<a id="命令"></a>
## Command

```bash
# Query to-do approvals
lark-cli approval tasks query --params '{"topic":"1"}' --as user

# Query done approvals
lark-cli approval tasks query --params '{"topic":"2"}' --as user

# Search the task list by keyword
lark-cli approval tasks query --params '{"topic":"1","keyword":"测试","page_size":10}' --as user

# Filter by task time range (second-level timestamp)
lark-cli approval tasks query --params '{"topic":"1","start_timestamp":"<START_SECONDS>","end_timestamp":"<END_SECONDS>"}' --as user

# Paginate using page_token
lark-cli approval tasks query --params '{"topic":"1","page_token":"example_page_token"}' --as user

# Table format output for quick browsing
lark-cli approval tasks query --params '{"topic":"1"}' --format table --as user
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--params '{"topic":"..."}'` | Yes | Query parameters, passed in as JSON |
| `topic` | Yes | Task group topic, see "topic enum" below |
| `definition_code` | No | Approval definition Code, used to query only tasks under a certain approval definition |
| `keyword` | No | Search keyword; when non-empty, the search path is used; when empty or only spaces, the normal list path is kept |
| `start_timestamp` | No | Filter by task time, start value of the time range, second-level timestamp |
| `end_timestamp` | No | Filter by task time, end value of the time range, second-level timestamp |
| `locale` | No | Return language: `zh-CN`, `en-US`, `ja-JP` |
| `page_size` | No | Page size |
| `page_token` | No | Pagination token; leave empty on the first request, then use the `page_token` returned last time |
| `user_id_type` | No | User ID type: `user_id`, `union_id`, `open_id` |
| `--as user` | No | It is recommended to explicitly specify the user identity; approval task queries should usually use the user identity |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call without executing it |

<a id="topic-枚举"></a>
## topic enum

| Value | Meaning |
|----|------|
| `1` | To-do approvals |
| `2` | Done approvals |
| `17` | Unread notifications |
| `18` | Read notifications |

<a id="输出重点字段"></a>
## Key output fields

Common fields in the returned result:

| Field | Description |
|------|------|
| `count` | List count, returned only on the first page; returns `99` when the number of tasks is greater than or equal to 100 |
| `has_more` | Whether there is more data |
| `page_token` | Next page pagination Token |
| `tasks[].task_id` | Task ID, globally unique |
| `tasks[].instance_code` | Approval instance Code; when subsequently performing operations such as approve / reject / rollback, it usually needs to be used in pairs with `task_id` |
| `tasks[].title` | Task title |
| `tasks[].status` | Task status: `1` to-do, `2` done, `17` unread, `18` read, `33` in progress, `34` withdrawn |
| `tasks[].topic` | Group topic the task belongs to |
| `tasks[].instance_status` | Approval instance status: `0` no status, `1` in progress, `2` approved, `3` rejected, `4` revoked, `5` terminated |
| `tasks[].definition_code` | Approval definition Code |
| `tasks[].definition_name` | Approval definition name |
| `tasks[].initiator` | Initiator ID |
| `tasks[].initiator_name` | Initiator name |
| `tasks[].summaries` | List of form summary fields |
| `tasks[].support_api_operate` | Whether approving or rejecting this task via API is supported |
| `tasks[].user_id` | ID of the user the task belongs to |
| `tasks[].instance_external_id` | Third-party approval instance ID, exists only for third-party approval instances |
| `tasks[].task_external_id` | Third-party approval task ID, exists only for third-party approval tasks |
| `tasks[].link` | Third-party approval redirect link |

<a id="使用建议"></a>
## Usage recommendations

- Common processing chain: first use `tasks query` to get `task_id` and `instance_code`; if the user needs to view details, the current node, form content, process progress, etc., call `instances get` to view details, and finally execute `tasks approve` / `tasks reject` / `tasks transfer` / `tasks add_sign` / `tasks rollback`.
- If you only want to see "approval instances that have been initiated", use `instances initiated`; `tasks query` is more suitable for pulling lists around "task groups".
- Pass `keyword` when you need to search task titles, summaries, or related content; search sorting differs from normal list sorting, and the search service results take precedence.
- When troubleshooting tasks by time, use `start_timestamp` / `end_timestamp` to narrow the range; both values are second-level timestamps.
- When you need to continue paginating, directly put the `page_token` returned last time back into `--params`.
- When the result volume is large, prefer using `--format table` to improve readability.
