# apps +session-messages-list

Read the reply messages of a session turn by page_token pagination. For runtime command facts, `lark-cli apps +session-messages-list --help` is authoritative.

<a id="何时用"></a>
## When to use

Use this to fetch the list of reply messages produced by one round of conversation (turn) in a Miaoda app. Read-only, scope `spark:app:read`, user identity. It can also be read for a turn that is still running—messages appear incrementally as they are generated, and you can pair it with `--page-token` to continue pulling new messages, which is useful for real-time reporting of this round's progress during cloud development. It does not send messages, nor does it determine turn status; to know whether a turn has finished and to get `turn_id`, still use `+session-get` first.

<a id="命令骨架"></a>
## Command skeleton

```bash
lark-cli apps +session-messages-list --app-id <app_id> --session-id <session_id> --turn-id <turn_id> [--page-token <token>]
```

| Flag | Required | Description |
|------|:----:|------|
| `--app-id` | Yes | App ID |
| `--session-id` | Yes | Session ID |
| `--turn-id` | Yes | Turn ID, from `latest_turn.turn_id` of `+session-get` |
| `--page-token` | No | string, the `next_page_token` from the previous page's response; omit for the first page |

<a id="turn_id-来源"></a>
## turn_id source

`--turn-id` cannot be provided directly by the user; you must first run `+session-get` to get `latest_turn.turn_id`. When there is no `turn_id`, do not guess; run `+session-get` first.

<a id="示例"></a>
## Example

First get the `turn_id` of the latest turn, then pull the first page, and finally use `next_page_token` to continue pulling the next page:

```bash
# 1. Extract latest_turn.turn_id from +session-get
TURN_ID=$(lark-cli apps +session-get --app-id app_xxx --session-id conv_xxx -q '.data.latest_turn.turn_id')

# 2. Pull the first page (omit --page-token)
lark-cli apps +session-messages-list --app-id app_xxx --session-id conv_xxx --turn-id "$TURN_ID"

# 3. When has_more=true, use the previous page's next_page_token as --page-token to continue pulling
lark-cli apps +session-messages-list --app-id app_xxx --session-id conv_xxx --turn-id "$TURN_ID" --page-token tok_next
```

<a id="输出契约"></a>
## Output contract

- `data.messages[]`: each entry contains `message_id`, `role`, `content`.
- `data.next_page_token` (string): the next-page pagination token, to be used as `--page-token` in the next call. **Note that it is still non-empty on the last page** (decoded form like `{"offset":N}`); you cannot use whether it is empty to determine whether there is a next page.
- `data.has_more` (bool): whether there are more messages. **This is the only basis for deciding whether to continue pulling.**
- pretty output is a message table + a final line `next_page_token: <token>  has_more: <bool>`; for automated field extraction, use JSON or `-q`.
- Business failures (app/session/turn does not exist or the ID is written incorrectly) usually carry `error.hint` pointing to `+session-get`; prefer to relay the hint.

<a id="分页规则"></a>
## Pagination rules

A single call returns only one page. The Agent continues pulling on its own: use this response's `next_page_token` as the next call's `--page-token`, and stop only when `has_more` is `false`. Do not pass `--page-token` for the first page.

> ⚠️ **The termination condition depends only on `has_more`; do not judge by whether `next_page_token` is empty.** Even when `has_more=false` (already the last page), the backend still returns a non-empty `next_page_token` (decoded form like `{"offset":N}`); if you use "continue as long as the token is non-empty" as the loop condition, you will keep paging out empty pages after the last page (0 entries per page), wasting calls. Stop immediately upon reading `has_more=false`, and do not use that token to continue pulling.
