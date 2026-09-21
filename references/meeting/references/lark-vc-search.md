
# vc +search

Search ended historical meeting records, supporting multi-condition filtering by keyword, time range, organizer, participant, and meeting room. Read-only, supports `--as user` / `--as bot`.

<a id="关键词使用边界"></a>
## Keyword usage boundaries

`--query` is only used for 9-digit meeting numbers or real meeting keywords, such as meeting topics, project names, review names, and customer names. When the user merely says "all video meetings I attended this month", "all video meetings I organized in the last two weeks", "summarize the main topics / check the attendance", the essence is a historical meeting list and subsequent summarization; do not put action words like "review", "all video meetings", or "summarize the main topics" into `--query`. Such requests should first use a time range plus `--participant-ids` / `--organizer-ids` to search the full set of candidates, then continue to retrieve minutes or recording information based on the results.

The list stage is only responsible for finding meeting records; the summarization stage must continue to gather evidence. If the user requests "main topics", "main decisions", or "attendance", first confirm that the `meeting_id`, time, organizer/participants of the search results match the filter conditions, then use `vc +detail` or `minutes` to read the minutes, Minutes, or recording information. When there are no minutes or Minutes, truthfully explain that the summary can only be based on meeting titles/attendance data, and do not fabricate topics.

<a id="典型触发表达"></a>
## Typical trigger expressions

The following expressions should usually prioritize `vc +search`:

- Meetings held today
- What meetings were held today
- Which meetings have I attended recently
- Meetings I held this week
- Ended meetings
- Historical meeting records

<a id="命令"></a>
## Command

```bash
# Keyword search
lark-cli vc +search --query "周会"

# Query meeting ID by 9-digit meeting number
lark-cli vc +search --query "123456789" --format json --as user
lark-cli vc +search --query "123456789" --format json --as bot

# Query meetings held on a certain day (for a single-day query, start and end must be set to the same day)
lark-cli vc +search --start 2026-03-10 --end 2026-03-10

# Search by time range
lark-cli vc +search --start "2026-03-10T00:00+08:00" --end "2026-03-17T00:00+08:00"

# By organizer / participant / meeting room (comma-separated)
lark-cli vc +search --organizer-ids "ou_user1,ou_user2"
lark-cli vc +search --participant-ids "ou_user1,ou_user2"
lark-cli vc +search --room-ids "123,456"

# Multi-condition combination
lark-cli vc +search --organizer-ids "ou_user1" --room-ids "123" --start "2026-03-10T00:00+08:00"

# Pagination
lark-cli vc +search --query "周会" --page-token "<PAGE_TOKEN>"
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--query <text>` | No | 9-digit meeting number or search keyword |
| `--start <time>` | No | Start time (ISO 8601 or date only) |
| `--end <time>` | No | End time (ISO 8601 or date only) |
| `--organizer-ids <ids>` | No | Organizer open_id list, comma-separated; multiple values use OR semantics |
| `--participant-ids <ids>` | No | Participant open_id list, comma-separated; multiple values use OR semantics |
| `--room-ids <ids>` | No | Meeting room ID list, comma-separated; multiple values use OR semantics |
| `--page-size <n>` | No | Number per page, default `15`, maximum `30` |
| `--page-token <token>` | No | Pagination token, used to get the next page |
| `--dry-run` | No | Preview the API call without executing it |

<a id="核心约束"></a>
## Core constraints

<a id="1-至少提供一个过滤条件"></a>
### 1. Provide at least one filter condition

All parameters are optional, but at least one filter condition must be provided: `--query`, `--start`, `--end`, `--organizer-ids`, `--participant-ids`, or `--room-ids`.

When there is no real keyword, a time range or personnel filter already satisfies this constraint, and `--query` can be omitted.

When relative times such as "this month" or "the last two weeks" are involved, first calculate the `"<YYYY-MM-DD>"` placeholder based on the execution day, then run the command; do not reuse the specific dates from when the documentation examples were generated.

<a id="2-仅搜索历史会议"></a>
### 2. Only search historical meetings

`vc +search` can only search ended historical meeting records and is not used to query future schedules. To query future meeting arrangements, use [lark-calendar](../../calendar/index.md).

<a id="3-支持-user-和-bot-身份"></a>
### 3. Supports user and bot identities

This interface supports `--as user` and `--as bot`. The user identity requires completing `lark-cli auth login` and having the `vc:meeting.search:read` permission; the bot identity uses the app's tenant access token, and you need to confirm that the current app has enabled the `vc:meeting.search:read` scope and that the runtime environment can obtain a valid TAT.

After obtaining `meeting_id` from the search, subsequent `vc +detail`, `vc +recording`, `vc meeting get`, and `note +detail` must explicitly use the same identity used for this search. Do not automatically switch identities to bypass permission errors.

<a id="4-支持分页"></a>
### 4. Supports pagination

When `has_more=true` is returned, use the `page_token` in the response together with `--page-token` to get the next page of results.

<a id="5-日期型---end-包含当天整天"></a>
### 5. Date-type `--end` includes the entire day

When `--end` is passed in date-only format (such as `2026-03-10`), the CLI interprets it as `23:59:59` of that day, not `00:00:00` of that day.

This means:

- `--start 2026-03-10 --end 2026-03-10` means querying only `2026-03-10` that day
- `--start 2026-03-10 --end 2026-03-11` means querying both days `2026-03-10` and `2026-03-11`

If the user says "meetings held yesterday", "meetings held today", or "meetings held on a certain day", set both `--start` and `--end` to the same day, rather than setting `--end` to the next day.

<a id="时间格式"></a>
## Time formats

`--start` and `--end` support the following time formats:

| Format | Example | Description |
|------|------|------|
| ISO 8601 (with time zone) | `2026-03-10T14:00:00+08:00` | Recommended |
| ISO 8601 (without time zone) | `2026-03-10T14:00:00` | Parsed in the local time zone |
| Date only | `2026-03-10` | Parsed at day granularity; if used for `--end`, it means `23:59:59` of that day |

<a id="输出结果"></a>
## Output results

- By default, outputs JSON, including `items`, `has_more`, and `page_token`.

## Pagination (`has_more` / `page_token`)

- When `has_more=true` is returned in the results, it means there are more pages available to continue retrieving.
- When continuing pagination, use the `page_token` in the response together with `--page-token` to initiate the next query.
- Do not assume that increasing `--page-size` will retrieve all results; when iterating through pages, rely on `has_more` and `page_token`.
- When full results are not explicitly required, accumulate the number of `items` read page by page: before accumulating fewer than 50 records, you may automatically continue paginating (`has_more=true` means continue); when more than 50 records have been read and `has_more=true` still applies, first confirm with the user whether to continue retrieving all results.
- When the user explicitly says "all / everything / statistics / sort by time", that full-result intent takes precedence over the 50-record confirmation threshold; directly paginate through all pages according to `has_more` and deduplicate, then sort or calculate statistics, and do not answer using only the first page.

```bash
# First page
lark-cli vc +search --query "周会" --page-size 15

# Next page
lark-cli vc +search --query "周会" --page-size 15 --page-token "<PAGE_TOKEN>"
```

<a id="常见错误与排查"></a>
## Common errors and troubleshooting

| Error symptom | Root cause | Solution |
|---------|---------|---------|
| The command directly errors and requires a filter condition | No `--query`, time range, or any filter ID was passed in | Add at least one filter condition and retry |
| Time parameter validation fails | `--start` or `--end` has an invalid format | Switch to ISO 8601 or `YYYY-MM-DD` |
| Cannot find future meetings | `vc +search` only queries historical meetings | Use [lark-calendar](../../calendar/index.md) to query future schedules |
| Insufficient permissions | `vc:meeting.search:read` is not authorized | `--as user`: complete user authorization as prompted; `--as bot`: check the tenant access token and app scope, and do not execute `auth login` |

<a id="提示"></a>
## Tips
- Must use `--format json` output for stable parsing.
- When troubleshooting parameters and request structure, prioritize using `--dry-run`.
- The maximum search time range is 1 month. If you need to search meetings over a longer time range, split it into multiple queries each with a time range of one month.
- Do not use relative time literals such as `yesterday` or `today`; first convert them into explicit dates, for example `2026-03-10`.
- If the user explicitly asks about "Minutes information" rather than "minutes content", do not default to `vc +detail`; first use `vc +recording`.

<a id="相关场景"></a>
## Related scenarios
- [Query meetings and their artifacts](../scenes/query-meeting-and-artifacts.md)
