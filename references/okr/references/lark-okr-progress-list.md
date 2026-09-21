# okr +progress-list


Get a paginated list of progress records for an Objective or Key Result, with external control over pagination.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Get the first page of Objective progress records (default page size is 100, generally no need to paginate)
lark-cli okr +progress-list \
  --target-id 1234567890123456789 \
  --target-type objective

# Get the next page of progress records
lark-cli okr +progress-list \
  --target-id 1234567890123456789 \
  --target-type objective \
  --page-size 100 \
  --page-token "7000000000000000002"

# Get the first page of Key Result progress records
lark-cli okr +progress-list \
  --target-id 9876543210987654321 \
  --target-type key_result
```

<a id="参数"></a>
## Parameters

| Parameter                    | Required | Default value             | Description                                             |
|-------------------------|----|--------------------|--------------------------------------------------|
| `--target-id`           | Yes  | —                  | Objective ID or Key Result ID (int64 type, positive integer)       |
| `--target-type`         | Yes  | —                  | Target type: `objective` \| `key_result`            |
| `--user-id-type`        | No  | `open_id`          | User ID type: `open_id` \| `union_id` \| `user_id` |
| `--department-id-type`  | No  | `open_department_id` | Department ID type: `department_id` \| `open_department_id` |
| `--page-size`           | No  | `100`              | Number per page, range `1-100`.                           |
| `--page-token`          | No  | `""`               | The `page_token` from the previous response; leave empty to indicate the first page.        |
| `--dry-run`             | No  | —                  | Preview the API call without actually executing it.                       |
| `--format`              | No  | `json`             | Output format.                                        |

<a id="工作流程"></a>
## Workflow

1. Use `+cycle-list` and `+cycle-detail` to get the ID of the Objective or Key Result.
2. Execute `lark-cli okr +progress-list --target-id "..." --target-type objective --page-size 100`.
3. If the response contains `has_more=true`, continue by calling the next page with the returned `page_token`.
4. Get the list of progress records under that Objective or Key Result.

<a id="输出"></a>
## Output

Returns JSON:

```json
{
  "progress_list": [
    {
      "progress_id": "1234567890123456789",
      "modify_time": "2025-01-15 10:30:00",
      "content": "{...}",
      "progress_rate": {
        "percent": 80.0,
        "status": "done"
      }
    }
  ],
  "has_more": true,
  "page_token": "7000000000000000002"
}
```

Where:

- `progress_list` — array of progress records
- `has_more` and `page_token` are used for external control of pagination; when `has_more=true`, pass the `page_token` returned this time as-is via `--page-token` to get the next page.
- The `content` field is a JSON string in the OKR ContentBlock rich text format. Please refer to [lark-okr-contentblock.md](lark-okr-contentblock.md) for details.
- `progress_rate.status` returns a readable string: `normal` (normal), `overdue` (overdue), `done` (completed).

<a id="与-progress-get-的区别"></a>
## Difference from +progress-get

| Command             | Purpose                               | API version |
|------------------|------------------------------------|----------|
| `+progress-list` | Paginated retrieval of progress records for an Objective/Key Result | v2       |
| `+progress-get`  | Get a single record by progress record ID        | v1       |

The structure of each record in the `progress_list` array returned by `+progress-list` is the same as the `progress` structure returned by `+progress-get`.

<a id="参考"></a>
## References

- [lark-okr](../index.md) -- all OKR commands (shortcuts and API interfaces)
- [ContentBlock format](lark-okr-contentblock.md) -- the rich text format used for progress content
- [lark-okr-progress-get](lark-okr-progress-get.md) -- get a single progress record by ID
- [lark-okr-progress-create](lark-okr-progress-create.md) -- create a progress record
- [lark-shared](../../shared/index.md) -- authentication and global parameters
