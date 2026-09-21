# okr +cycle-list


List one page of OKR cycles for a specified user, supporting external pagination control and optional post-filtering by time range.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Get the first page of the user's cycles (default page size is 100, sorted in reverse chronological order; pagination is generally not needed)
lark-cli okr +cycle-list --user-id "ou_xxx"

# Get the next page
lark-cli okr +cycle-list --user-id "ou_xxx" --page-size 100 --page-token "7000000000000000002"

# List cycles using a specific user ID type
lark-cli okr +cycle-list --user-id "xxx" --user-id-type user_id

# List cycles in the currently returned page that overlap with the time range (for example, 2025-01 to 2025-06)
lark-cli okr +cycle-list --user-id "ou_xxx" --time-range "2025-01--2025-06"

# Preview the API call without actually executing it
lark-cli okr +cycle-list --user-id "ou_xxx" --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter               | Required | Default value       | Description                                                               |
|------------------|----|-----------|------------------------------------------------------------------|
| `--user-id`      | Yes  | —         | User ID of the OKR owner                                                    |
| `--user-id-type` | No  | `open_id` | User ID type: `open_id` \| `union_id` \| `user_id`                    |
| `--time-range`   | No  | —         | Post-filter condition: first request one page by `--page-size`/`--page-token`, then locally keep the cycles that overlap with this time range. Format: `YYYY-MM--YYYY-MM` (for example, `2025-01--2025-06`). |
| `--page-size`    | No  | `100`     | Number per page, range `1-100`.                                               |
| `--page-token`   | No  | `""`      | The `page_token` from the previous response; leave empty to indicate the first page.                            |
| `--dry-run`      | No  | —         | Preview the API call without actually executing it.                                                 |
| `--format`       | No  | `json`    | Output format.                                                            |

<a id="工作流程"></a>
## Workflow

1. Get the target user's `open_id` (or another ID type). If the user says "my OKR cycles", first get the current user's
   ID via `lark-cli contact +get-user`.
2. Execute `lark-cli okr +cycle-list --user-id "ou_xxx" --page-size 100`, optionally using `--time-range`.
3. If the response contains `has_more=true`, continue calling the next page with the returned `page_token`.
4. Report the results: each cycle's ID, start/end time, and status.

`--time-range` is a post-filter condition and does not change the server-side pagination window. In other words, the command first fetches the specified page, then filters the cycles in that page; if you need complete results for a time range, you need to pull page by page according to `has_more`/`page_token` and merge them.

<a id="输出"></a>
## Output

Returns JSON:

```json
{
  "cycles": [
    {
      "id": "1234567890123456789",
      "start_time": "2025-01-01 00:00:00",
      "end_time": "2025-06-30 00:00:00",
      "cycle_status": "normal"
    }
  ],
  "has_more": true,
  "page_token": "7000000000000000002",
  "current_active_cycles": [
    {
      "id": "1234567890123456789",
      "start_time": "2025-01-01 00:00:00",
      "end_time": "2025-06-30 00:00:00",
      "cycle_status": "normal"
    }
  ]
}
```

In this cycle information, these fields are worth noting:

- `id` is this cycle's ID; you usually need to use it later with `okr +cycle-detail` to get OKR content details
- `has_more` and `page_token` are used for external pagination control; when `has_more=true`, pass the `page_token` returned this time as-is via `--page-token` to get the next page.
- `start_time` `end_time` are the cycle's start and end times, always starting from the 1st day of some month and ending on the last day of that month or a later month.
    - In the OKR system, we only care about the year and month parts of this time. For example, a cycle that "starts 2025-01-01 and ends 2025-06-30" is called the "January-June 2025" cycle, while
      a cycle that "starts 2025-01-01 and ends 2025-01-31" is called the "January 2025" cycle.
    - If a cycle starts on January 1 of a year and ends on December 31 of a year, then it is that year's annual cycle. For example, a cycle that "starts 2025-01-01 and ends 2025-12-31" is
      the annual cycle for "2025".
- `cycle_status` is the cycle status value; see below.
- `current_active_cycles` is the currently effective cycle list, though depending on the user's cycle settings, it may be empty.

If you need to get information such as the cycle's creation time/total score, you can get it via the native API `okr cycles list`.

<a id="周期状态值"></a>
### Cycle status values

| Value         | Description       |
|-----------|----------|
| `default` | Default status (0) |
| `normal`  | Effective (1)   |
| `invalid` | Invalid (2)   |
| `hidden`  | Hidden (3)   |

In the OKR system, cycles in default/normal status are currently effective normally, cycles in invalid status are no longer effective but can usually still be filled in, and cycles in hidden status are hidden and invisible.

<a id="参考"></a>
## References

- [lark-okr](../index.md) -- all OKR commands
- [lark-shared](../../shared/index.md) -- authentication and global parameters
