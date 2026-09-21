# +search-bot

Search for bots visible to the current user by keyword. Only the user identity is supported, and the `search:bot` permission is required.

- ✅ Search for bots by keyword and get the open_id
- ✅ Search multiple keywords at once (`--queries`)
- ✅ Search for bots within a specified chat scope (`--chat-ids`)

<a id="参数"></a>
## Parameters

You must pass either `--query` or `--queries`. `--chat-ids` specifies the search scope, and `--has-chatted` filters for bots you have already chatted with; neither can be used on its own.

| Flag | Description |
|---|---|
| `--query <text>` | Search a single keyword, up to 50 characters |
| `--queries <csv>` | Search multiple keywords in parallel, up to 20; each up to 50 characters. Cannot be used together with `--query` |
| `--chat-ids <csv>` | Search only within specified chats, up to 100 chats; supports chat IDs or chat links |
| `--has-chatted` | Return only bots you have chatted with; do not pass this parameter when not needed |
| `--page-size <n>` | Number of results to return, 1–30, default 20 |

```bash
lark-cli contact +search-bot --query '会议助手' --as user
lark-cli contact +search-bot --query '助手' --has-chatted --as user
lark-cli contact +search-bot --queries '会议助手,日报助手,审批助手' --as user
```

<a id="输出"></a>
## Output

| Field | Type | Description | When empty |
|---|---|---|---|
| `open_id` | string | Bot ID | Always non-empty |
| `name` | string | Bot name | Empty string |
| `description` | string | Bot description | Field omitted |
| `chat_id` | string | Direct chat ID with the bot | Empty string |
| `enable_join_group` | bool | Whether it can be added to group chats | — |
| `is_agent` | bool | Whether it is an agent | — |
| `tenant_id` | string | Tenant identifier | Field omitted |
| `match_segments` | string[] | Matched text fragments | `[]` when there are no matches |

<a id="没有分页"></a>
### No pagination

Pagination is not supported. When `has_more=true`, use a more specific keyword instead, or adjust the search scope.

<a id="多条命中怎么选"></a>
### How to choose among multiple matches

When multiple bots match, use `description` and `is_agent` to decide. If you will later send a message or create a group, have the user confirm the target; do not simply pick the first one.

```bash
lark-cli contact +search-bot --query '会议助手' \
  --jq '.data.bots[] | select((.description // "") | contains("<功能关键词>"))' --as user
```

## fanout(`--queries`)

Output is `{bots[], queries[], notice?}`. `has_more` appears only in the results for each keyword.

- `bots[].matched_query`: the keyword corresponding to that result
- `queries[]`: the execution result for each keyword, in the format `{query, error?, has_more, notice?}`
- If some keywords fail, the other results are retained; if all fail, the command reports an error
- `--chat-ids` and `--has-chatted` apply to all keywords
