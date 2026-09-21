# +search-user

Only supports user identity.

## When to use

- ✅ You know a name / email / "people you've chatted with" and want to find the open_id
- ✅ You know a set of open_ids and want to batch-validate them or backfill fields (`--user-ids`, max 100, supports `me`)
- ✅ Filter employees by dimensions such as chat relationship / employment status / tenant boundary / enterprise email
- ❌ You know an open_id and want to send a message → go directly through `lark-im`, do not go through this command

## Key flags

At least one of `--query` / `--queries` / `--user-ids` / a bool filter must be passed. Explicitly passing `=false` for a bool filter will error — not passing it is equivalent to no filtering.

| Flag | Purpose |
|---|---|
| `--query <text>` | Keyword (name / email / phone number), ≤ 50 runes |
| `--queries <csv>` | Search multiple keywords in parallel, **max 20 items**; mutually exclusive with `--query` / `--user-ids`; outputs a new shape (see below) |
| `--user-ids <csv>` | open_id list, ≤ 100; supports `me` meaning yourself; when passed together with `--query`, limits the search scope to that set |
| `--has-chatted` | Search only those you have chatted with |
| `--has-enterprise-email` | Search only those with an enterprise email |
| `--exclude-external-users` | Search only the same tenant (exclude external contacts) |
| `--left-organization` | Search only those who have resigned |
| `--lang <locale>` | Overrides the language of `localized_name` (such as `zh_cn` / `en_us` / `ja_jp`) |
| `--page-size <n>` | Page size 1-30, default 20 |

## Common examples

```bash
# Search by name, then inspect candidates to identify the intended Zhang San
lark-cli contact +search-user --query "张三" --has-chatted

# Search by full email (the hit is usually unique, suitable as input for subsequent commands)
lark-cli contact +search-user --query "alice@example.com"

# View yourself
lark-cli contact +search-user --user-ids me

# Batch backfill: given a set of open_ids, fetch name / email / department
lark-cli contact +search-user --user-ids "ou_a,ou_b,ou_c" --format json

# Combine filters: same-tenant employees with enterprise email and the surname Wang
lark-cli contact +search-user --query "王" --exclude-external-users --has-enterprise-email

# filter-only enumeration: list all "resigned colleagues you have chatted with" (no keyword)
lark-cli contact +search-user --has-chatted --left-organization
```

## Batch parallel query (fanout)

Query multiple names at once:

```bash
lark-cli contact +search-user --queries "Alice,Bob,张三"
```

- Each user row carries `matched_query`, identifying which query it came from
- `queries[]` has one `{query, error?, has_more}` per input, with `error` for the failed ones
- A partial failure does not affect the other queries; only when all fail does it exit non-zero

```bash
# The bool filter takes effect for every query
lark-cli contact +search-user --queries "Alice,Bob" --has-chatted

# Mutually exclusive with --query / --user-ids
lark-cli contact +search-user --queries "a" --query "b"   # ❌ exit 2
```

Constraints:
- Max 20 items; each ≤ 50 characters
- Duplicate entries are silently deduplicated; an all-empty csv (`,,,`) raises an error

## Disambiguating identical names

Searching a common name often returns multiple results with the same name. If the follow-up operation has side effects (sending a message, inviting to a meeting, etc.), present the candidates to the user to choose from; **do not choose on your own**.

Filtering signals (reliability from high to low): `chat_recency_hint` (contacted recently) > `enterprise_email` prefix > `department` keyword. `localized_name` has no distinguishing effect when the names are identical.

```bash
# Use jq to filter precisely by department
lark-cli contact +search-user --query "张三" \
  --jq '.data.users[] | select(.department | contains("<部门关键词>"))'
```

## Notes

- **No automatic pagination**. `has_more=true` means the query needs to be refined.
- **`--lang` only affects the output display name**, not the matched fields.
- **When `--query` and `--user-ids` are set at the same time**: `--user-ids` limits the search scope, and `--query` matches within that set.

## Output field contract

For cross-tenant users (`is_cross_tenant=true`), business fields may be empty strings, so a null-value fallback is required.

| Field | Type | Description | Cross-tenant |
|---|---|---|---|
| `open_id` | string | Stable identifier, input for subsequent commands | Always non-empty |
| `localized_name` | string | Display name chosen by `--lang` / brand | Always non-empty (falls back to open_id) |
| `email` | string | Personal email | May be empty |
| `enterprise_email` | string | Enterprise email | May be empty |
| `is_activated` | bool | Whether the Feishu account is activated (messages can still be delivered when not activated, but the user may not see them) | May be false |
| `is_cross_tenant` | bool | Whether the user is cross-tenant (same company = false, external contact = true) | — |
| `p2p_chat_id` | string | P2P chat ID with the current user (`oc_...`); empty means you have never had a private chat. Can be used as input for IM commands that accept `--chat-id` | May be empty |
| `has_chatted` | bool | Derived field of `p2p_chat_id != ""` | — |
| `department` | string | Department path; the server may join levels with `-`, and the number of levels is not fixed. **Treat it as a string that supports substring matching** | May be empty |
| `signature` | string (optional) | User's personal signature; the field is absent when empty | May be absent |
| `chat_recency_hint` | string | Hint text about the most recent contact, for display only | May be empty |
| `match_segments` | string[] | String fragments matched by the keyword, used for highlighting; an empty array if there is no match | — |

### Extra fields in `--queries` mode

Each `data.users[]` has an extra `matched_query` (string), indicating which query this row came from.

`data.queries[]` in input order, one per query after dedup:

| Field | Type | Description |
|---|---|---|
| `query` | string | That input |
| `error` | string (optional) | Failure reason; absent on success |
| `has_more` | bool | Whether that query has more results |

fanout mode has no top-level `data.has_more`.
