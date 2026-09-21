# minutes +search


Search the Minutes list, supporting multi-condition filtering by keyword, owner, participant, and time range. Supports user identity and bot / app identity; both owner and participant support passing multiple open\_id values, and under user identity you can also pass `me` to indicate the current user. Read-only operation; does not modify any Minutes data.

This module corresponds to shortcut: `lark-cli minutes +search` (calls `POST /open-apis/minutes/v1/minutes/search`).

<a id="典型触发表达"></a>
## Typical Trigger Phrases

The following expressions should usually prioritize `minutes +search`:

- My Minutes
- Minutes I own
- Minutes I participated in
- Recent Minutes
- Minutes with a certain keyword
- Minutes within a certain time period

<a id="命令"></a>
## Command

```bash
# Keyword search
lark-cli minutes +search --query "预算复盘"

# Query Minutes within a single day (for a single-day query, it is recommended to set both start and end to the same day)
lark-cli minutes +search --start 2026-03-10 --end 2026-03-10

# Search by time range
lark-cli minutes +search --start "2026-03-10T00:00+08:00" --end "2026-03-17T00:00+08:00"
lark-cli minutes +search --start 2026-03-10 --end 2026-03-17

# Keyword + time range
lark-cli minutes +search --query "预算复盘" --start "2026-03-10T00:00+08:00" --end "2026-03-17T00:00+08:00"
lark-cli minutes +search --query "预算复盘" --start "2026-03-10T00:00+08:00"
lark-cli minutes +search --query "预算复盘" --end "2026-03-17T00:00+08:00"

# Filter by participant (open_id, comma-separated)
lark-cli minutes +search --participant-ids "ou_x,ou_y"

# Filter by owner (open_id, comma-separated)
lark-cli minutes +search --owner-ids "ou_owner,ou_owner_2"

# Strictly query only Minutes where I am a participant (excluding ones I own)
lark-cli minutes +search --participant-ids "me"

# Query Minutes I own
lark-cli minutes +search --owner-ids "me"

# Broad query for Minutes I participated in (natural language default: I own ∪ I participated in)
lark-cli minutes +search --owner-ids "me" --start 2026-03-10 --end 2026-03-10
lark-cli minutes +search --participant-ids "me" --start 2026-03-10 --end 2026-03-10
# Then deduplicate and merge the two results by token

# Multi-condition combined query
lark-cli minutes +search --owner-ids "ou_owner" --participant-ids "ou_x" --start "2026-03-10T00:00+08:00"

# Paginated query
lark-cli minutes +search --query "预算复盘" --page-size 20
lark-cli minutes +search --query "预算复盘" --page-size 20 --page-token '<PAGE_TOKEN>'

# Output as structured JSON
lark-cli minutes +search --query "预算复盘" --format json
```

<a id="参数"></a>
## Parameters

| Parameter                        | Required | Description                                   |
| ------------------------- | -- | ------------------------------------ |
| `--query <text>`          | No  | Search keyword                                |
| `--owner-ids <ids>`       | No  | Owner open\_id list, comma-separated; multiple values use OR semantics; supports passing `me` to indicate the current user |
| `--participant-ids <ids>` | No  | Participant open\_id list, comma-separated; multiple values use OR semantics; supports passing `me` to indicate the current user |
| `--start <time>`          | No  | Start time (ISO 8601 or date only)                  |
| `--end <time>`            | No  | End time (ISO 8601 or date only)                  |
| `--page-size <n>`         | No  | Number per page, default `15`, maximum `30`                 |
| `--page-token <token>`    | No  | Next page token                          |
| `--dry-run`               | No  | Preview the API call without executing                        |

<a id="核心约束"></a>
## Core Constraints

<a id="1-至少提供一个过滤条件"></a>
### 1. Provide at least one filter condition

All parameters are optional, but at least one filter condition must be provided: `--query`, `--owner-ids`, `--participant-ids`, `--start`, or `--end`.

<a id="2-支持-user-和-bot-身份"></a>
### 2. Supports user and bot identities

This interface supports `--as user` and `--as bot`. User identity requires completing `lark-cli auth login` and having `minutes:minutes.search:read` permission; bot identity uses the app's tenant access token, and you need to confirm that the current app has the `minutes:minutes.search:read` scope enabled and that the runtime environment can obtain a valid TAT.

<a id="3-me-表示当前用户"></a>
### 3. `me` indicates the current user

In `--owner-ids` and `--participant-ids`, you can use `me` to indicate the currently logged-in user. This value is resolved locally to the current user's `open_id`, so there is no need to manually query your own user ID first. `me` is only suitable for user identity; bot identity has no "current user", so pass the `ou_` open_id directly.
If the current environment has not yet completed user login, or the CLI cannot resolve the current user's `open_id`, you should first run `lark-cli auth login`, then run the search again. This recovery method only applies to user identity and `me` resolution; for bot identity, check the tenant access token and app scope, and do not fix it via `auth login`.

<a id="4-自然语言中的参与的妙记默认按并集理解"></a>
### 4. "Minutes I participated in" in natural language is understood as a union by default

When the user says "Minutes I participated in", "Minutes I have attended", or "Minutes I've been involved in", the default understanding is "all Minutes I am involved in":

- Minutes I own: `--owner-ids me`
- Minutes where I am a participant: `--participant-ids me`

Do not just run `--participant-ids me` once and draw a conclusion, and do not stuff both `--owner-ids me` and `--participant-ids me` into a single query and gamble on the interface semantics. You should query separately, then perform a union and deduplicate by `token`.

Only when the user explicitly says "only ones I participated in but do not own", "owned by others but I participated", or "only look at participant identity" should you use only `--participant-ids`.

<a id="5-支持分页"></a>
### 5. Supports pagination

When `has_more=true` is returned, use the `page_token` from the response together with `--page-token` to get the next page of results.

<a id="6-日期型---end-包含当天整天"></a>
### 6. Date-type `--end` includes the entire day

When `--end` is passed in date-only format (such as `2026-03-10`), the CLI interprets it as `23:59:59` of that day, not `00:00:00` of that day.
The CLI first parses according to the local calendar-day semantics of the input, then normalizes it to an RFC3339 timestamp to send to the API; in dry-run or when troubleshooting the request body, the `Z` ending time you see represents the UTC representation of the same absolute point in time, and does not change the semantics of "query by the entire day".

This means:

- `--start 2026-03-10 --end 2026-03-10` means querying only `2026-03-10` that day
- `--start 2026-03-10 --end 2026-03-11` means querying both days `2026-03-10` and `2026-03-11`

If the user says "yesterday's Minutes", "today's Minutes", or "Minutes within a certain day", you should set both `--start` and `--end` to the same day, rather than setting `--end` to the next day.

<a id="时间格式"></a>
## Time Format

`--start` and `--end` support the following time formats:

| Format             | Example                          | Description                                 |
| -------------- | --------------------------- | ---------------------------------- |
| ISO 8601 (with timezone)  | `2026-03-10T14:00:00+08:00` | Recommended                                 |
| ISO 8601 (without timezone) | `2026-03-10T14:00:00`       | Parsed in local timezone                            |
| Date only            | `2026-03-10`                | Parsed at day granularity; if used for `--end`, means `23:59:59` of that day |

<a id="输出结果"></a>
## Output Results

- The default output includes `items`, `has_more`, and `page_token`.

## Pagination (`has_more` / `page_token`)

- When `has_more=true` is returned in the results, it means there are more pages available to fetch.
- To continue paging, use the `page_token` from the response together with `--page-token` to initiate the next query.
- Do not assume that increasing `--page-size` will get all results; when iterating through pages, rely on `has_more` and `page_token`.
- When the user has not explicitly requested the full set, accumulate the number of `items` read page by page: before the cumulative count reaches 50, you may automatically continue paging; once it exceeds 50 and there are still more results, first confirm with the user whether to continue fetching all results.
- When the user explicitly says "all / every / statistics / sorting", that full-set intent takes priority over the 50-item confirmation threshold; directly page through all pages according to `has_more`, deduplicate by `token` in the results, and then return, sort, or compute statistics.

```bash
# First page
lark-cli minutes +search --query "预算复盘" --page-size 20

# Next page
lark-cli minutes +search --query "预算复盘" --page-size 20 --page-token '<PAGE_TOKEN>'
```

<a id="常见错误与排查"></a>
## Common Errors and Troubleshooting

| Error Symptom                   | Root Cause                                                  | Solution                                         |
| ---------------------- | ----------------------------------------------------- | -------------------------------------------- |
| Command errors out directly, requiring a filter condition        | No `--query`, time range, or any filter ID was passed                           | Add at least one filter condition and retry                                |
| Time parameter validation fails               | `--start` or `--end` format is invalid                             | Switch to ISO 8601 or `YYYY-MM-DD`                   |
| `owner-ids` validation fails       | The value passed is not an open\_id, and is not `me` either; or `me` was passed but the current user's open\_id cannot be resolved | Change to a user ID starting with `ou_`, or complete `auth login` first and then pass `me` |
| `participant-ids` validation fails | The value passed is not an open\_id, and is not `me` either; or `me` was passed but the current user's open\_id cannot be resolved | Change to a user ID starting with `ou_`, or complete `auth login` first and then pass `me` |
| Insufficient permissions                   | `minutes:minutes.search:read` not authorized                     | For user identity, use `auth login` to complete user authorization; for bot identity, check the tenant access token and app scope |

<a id="提示"></a>
## Tips

- When the user says "my Minutes", prioritize understanding it as `--owner-ids me`.
- When the user says "Minutes I participated in" or "Minutes I have attended", the default understanding is the union of the two queries `--owner-ids me` and `--participant-ids me`.
- Only when the user explicitly says "only ones I participated in but do not own" should you prioritize understanding it as `--participant-ids me`.
- When the user mentions both "meeting / meeting / hold a meeting / a certain meeting" and "Minutes", prioritize locating the meeting first; if what is wanted is Minutes information, go through `vc +recording` to get `minute_token` → `minutes minutes get`, and only go through `minutes +detail --minute-tokens` when the content of the Minutes artifact is wanted.
- You must use `--format json` output; you are better at parsing JSON data.
- When troubleshooting parameters and request structure, prioritize using `--dry-run`.
- The maximum search time range is 1 month; if you need to search Minutes over a longer time range, you need to split it into multiple queries each with a time range of one month.

<a id="相关场景"></a>
## Related Scenarios
- [Query Minutes and their artifacts](../scenes/query-minutes-and-artifacts.md)
