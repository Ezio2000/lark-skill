
# approval instances initiated

Query the list of approval instances initiated by the current user (a user-level read-only operation). Suitable for use when you need to view "which approvals have I initiated", filter by a certain approval definition, or obtain `instance_code` for use in subsequent commands such as `instances get` / `instances cancel` / `instances cc`.

Required scopes: ["approval:instance:read"]

<a id="命令"></a>
## Command

```bash
# Query the list of approvals I initiated
lark-cli approval instances initiated --params '{"page_size":20}' --as user

# View only the instances I initiated under a certain approval definition
lark-cli approval instances initiated --params '{"definition_code":"<DEFINITION_CODE>","page_size":20}' --as user

# Search the instances I initiated by keyword
lark-cli approval instances initiated --params '{"keyword":"测试","page_size":10}' --as user

# Filter by initiation time range (second-level timestamp)
lark-cli approval instances initiated --params '{"start_timestamp":"<START_SECONDS>","end_timestamp":"<END_SECONDS>","page_size":20}' --as user

# Paginate using page_token
lark-cli approval instances initiated --params '{"page_size":20,"page_token":"example_page_token"}' --as user

# Table format output, for quick browsing
lark-cli approval instances initiated --params '{"page_size":20}' --format table --as user

# Preview the API call without executing
lark-cli approval instances initiated --params '{"page_size":20}' --as user --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--params '{...}'` | No | Query parameters, passed in as JSON; when not passed, default pagination and filtering are used |
| `definition_code` | No | Approval definition Code, used to view only the instances I initiated under a certain approval definition |
| `keyword` | No | Search keyword; when non-empty, the search path is used, when empty or only spaces, the normal list path is kept |
| `start_timestamp` | No | Filter by initiation time, start value of the time range, second-level timestamp |
| `end_timestamp` | No | Filter by initiation time, end value of the time range, second-level timestamp |
| `locale` | No | Return language: `zh-CN`, `en-US`, `ja-JP` |
| `page_size` | No | Page size |
| `page_token` | No | Pagination token; leave empty on the first request, then use the `page_token` returned last time |
| `user_id_type` | No | User ID type: `user_id`, `union_id`, `open_id` |
| `--as user` | No | It is recommended to explicitly specify the user identity; queries of the initiated approval list should usually use the user identity |
| `--format` | No | Output format: `json` (default), `ndjson`, `table`, `csv` |
| `--dry-run` | No | Preview the API call without executing |

<a id="输出重点字段"></a>
## Key output fields

Common fields in the returned result:

| Field | Description |
|------|------|
| `count` | List count, returned only on the first page; returns `99` when there are 100 or more instances |
| `has_more` | Whether there is more data |
| `page_token` | Next page pagination Token |
| `instances[].instance_code` | Approval instance Code; usually needed for subsequent detail queries or for performing withdrawal / cc |
| `instances[].definition_code` | Approval definition Code |
| `instances[].definition_name` | Approval definition name |
| `instances[].definition_group_id` | Approval definition group ID |
| `instances[].definition_group_name` | Approval definition group name |
| `instances[].initiator` | Initiator ID |
| `instances[].initiator_name` | Initiator name |
| `instances[].instance_status` | Approval instance status, see "instance_status enum" below |
| `instances[].instance_external_id` | Third-party approval instance ID (exists only for third-party approval instances) |
| `instances[].link` | Third-party approval redirect link |
| `instances[].summaries` | List of summary fields |

<a id="instance_status-枚举"></a>
## instance_status enum

| Value | Meaning |
|----|------|
| `0` | No process status, the corresponding label is not displayed |
| `1` | Process instance in progress |
| `2` | Approved |
| `3` | Rejected |
| `4` | Withdrawn |
| `5` | Terminated |

<a id="常见使用场景"></a>
## Common use cases

<a id="1-找到我要操作的审批实例"></a>
### 1) Find the approval instance I want to operate on

```bash
lark-cli approval instances initiated --params '{"page_size":20}' --format table --as user
```

After obtaining `instances[].instance_code`, you can continue with:

```bash
# View approval instance details
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user

# Withdraw an approval instance
lark-cli approval instances cancel --data '{"instance_code":"<INSTANCE_CODE>"}' --as user --yes
```

<a id="2-只看某类审批"></a>
### 2) View only a certain type of approval

```bash
lark-cli approval instances initiated \
  --params '{"definition_code":"<DEFINITION_CODE>","page_size":20}' \
  --as user
```


<a id="使用建议"></a>
## Usage recommendations

- **This is the preferred command for locating "approval instances I initiated"**: if your goal is to withdraw, cc, or view an already-initiated approval, get `instance_code` from here first.
- **Prefer using `definition_code` to narrow the scope**: when you already know the approval definition, filter out irrelevant instances first, which can significantly improve readability.
- **Pass `keyword` when search is needed**: search sorting differs from normal list sorting; rely on the search service results.
- **Use `start_timestamp` / `end_timestamp` when troubleshooting by time**: both values are second-level timestamps, used to narrow the result range by initiation time.
- **Prefer `--format table` when there are many results**: suitable for quick manual browsing.
- **`count` is returned only on the first page**: when handling pagination, do not assume that subsequent pages will also carry the total count.
- **`instance_status` can directly determine the next step**: for example, when the status is `1`, you can usually continue to view details or consider withdrawal; a status of `4` means it has already been withdrawn, so there is no need to withdraw again.
- **The summary field `summaries` is very suitable for list previews**: when the approval title is not clear enough, the summary value can help identify the target instance.

<a id="输出与后续操作"></a>
## Output and follow-up operations

After obtaining the list, common next steps:

```bash
# View details of a single approval instance
lark-cli approval instances get --params '{"instance_code":"<INSTANCE_CODE>"}' --as user

# Withdraw an approval instance
lark-cli approval instances cancel --data '{"instance_code":"<INSTANCE_CODE>"}' --as user --yes

# Add cc recipients to an approval instance
lark-cli approval instances cc --data '{"instance_code":"<INSTANCE_CODE>","cc_user_ids":["<USER_ID>"]}' --params '{"user_id_type":"open_id"}' --as user --yes
```
