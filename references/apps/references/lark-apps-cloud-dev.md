<a id="lark-apps-云端会话开发"></a>
# lark-apps Cloud Session Development

Applicable: the user wants a cloud Miaoda Agent to generate or iterate on an app, rather than pulling the code locally for development.

<a id="核心流程"></a>
## Core Flow

The entire development happens in the cloud: locally you only "send messages + poll status"; you do not pull source code, do not produce code, and do not start a local dev server. All session/chat commands are executed as the user (`--as user`).

<a id="资源模型app--session--turn"></a>
### Resource Model: app → session → turn

A three-level parent-child relationship, where each lower level hangs under the level above it:

- **app (application asset)**: a Miaoda app, created by `+create` and yielding `app_id`. `--app-type` follows the type determined by "Choosing a Development Path" in index.md (has database requirements → `full_stack`; pure frontend interaction, no database mentioned → defaults to `frontend`); cloud generation does not hardcode `full_stack`.
- **session**: an independent conversation context under one app, created by `+session-create` and yielding `session_id`. One app can have multiple sessions; `is_active` indicates whether that session is currently writable (can start a conversation).
- **turn**: one round of interaction within a session = one user message + the Miaoda Agent's generation/iteration in response to it. `+chat` sends one message to start one turn; the turn's handle is `turn_id`, and its status is read from `latest_turn.status`.

<a id="执行模型异步--轮询"></a>
### Execution Model: Asynchronous + Polling

`+chat` enqueues the message and then **returns immediately without waiting for generation to complete; the response does not include `turn_id`**; the turn's status and polling cadence rely entirely on `+session-get` reading `latest_turn.status` / `is_streaming` / `next_poll_after_ms`.

`+session-get` key fields:

- `is_streaming`: whether a turn is currently running (`true` = still generating).
- `latest_turn.status`: the status of the most recent turn; only `running` / `completed` / `failed` / `cancelled`.
- `latest_turn.turn_id`: the handle of the most recent turn (`+session-stop --turn-id` uses it).
- `latest_turn.user_message`: the message the user sent in this turn.
- `latest_turn.messages`: the message list for reviewing the full picture after this turn completes, arranged in chronological order, each entry carrying `role` (user messages, model replies, tool calls, etc. are all included; role values such as `user` / `assistant` / `tool`). Note that it may be empty while `latest_turn` is still running/initializing—for real-time progress of the turn **in progress**, read `+session-messages-list --turn-id <latest_turn.turn_id>` instead (see the polling rules below).
- `queued_messages` / `queued_count`: messages that have not started running yet and are queued behind.
- `next_poll_after_ms`: the suggested next polling interval (in milliseconds, a fixed value); when non-empty, prefer using it.

Polling rules:

- Cadence is determined by [Initialization vs Incremental Modification](#初始化-vs-增量修改): incremental 5-10 seconds; initialization 60-120 seconds; when `next_poll_after_ms` is non-empty, use it.
- `is_streaming=true`, `building` / `running` / `streaming` indicate still generating; keep polling, neither waiting blindly nor giving up early; during the initialization phase, stretch a single sleep to 60-120 seconds, and when entering `streaming` or when it is an incremental modification, switch back to 5-10 seconds.
- `is_streaming=false` and `latest_turn.status=completed` indicate this turn is complete and the next message can be sent.
- On `failed` / `cancelled`, relay the error field or hint and let the user decide whether to retry; do not silently resend.
- When you do not know which sessions an app has, first `+session-list --app-id <id>`, then choose the most recently active one or have the user confirm; do not directly guess `session_id`.
- To abort a running turn, take the value from `latest_turn.turn_id` in `+session-get`, then call `+session-stop --turn-id <turn_id>`.
- Status and cadence come from `+session-get`; real-time content of this turn comes from `+session-messages-list`: if you want to report to the user during running "what the cloud Agent is doing right now", use `+session-messages-list --turn-id <latest_turn.turn_id>` to read the incremental messages already produced (readable during running, no need to wait for the turn to end). Reuse the polling cadence above; do not start a separate, denser polling loop; when continuing to pull, pass the previous response's `next_page_token` as `--page-token` to fetch only new messages; when relaying, briefly describe progress and do not print entire messages or tool output verbatim.

<a id="典型链路"></a>
### Typical Chain

```bash
# 1) Create an app, get app_id (--app-type uses the type determined by the main routing; in this example "to-do app" needs to store to-dos → full_stack,
#    if it is a pure frontend interaction tool and no database is mentioned, use frontend)
lark-cli apps +create --name "待办应用" --app-type full_stack \
  --description "支持新增、完成、筛选待办"

# 2) Create a session under that app, get session_id
lark-cli apps +session-create --app-id app_xxx

# 3) Send a message to start a turn (asynchronously enqueued, returns immediately, no turn_id)
lark-cli apps +chat --app-id app_xxx --session-id sess_xxx --message "做一个待办清单页面"

# 4) Poll this turn's status; after completion, read the result from latest_turn.messages
lark-cli apps +session-get --app-id app_xxx --session-id sess_xxx

# Find existing sessions for that app (used when continuing a chat / when the session is uncertain)
lark-cli apps +session-list --app-id app_xxx
```

<a id="完成态不等于发布态"></a>
## Completion State Is Not the Same as Published State

For general published-state determination (is_published semantics, development-state link concatenation, published-state link sources), see "Published-State Guardrails" in index.md. This reference only adds wording specific to cloud sessions:

- `+session-get` returning `is_streaming=false` and `latest_turn.status=completed` only means this round of cloud generation/iteration has ended; it does not mean it has been published and deployed.
- If only the cloud session has completed and publication completion has not been confirmed, explicitly tell the user "the development-state link can be entered to continue editing; whether the published state is the latest version has not yet been confirmed."

<a id="需求发送"></a>
## Sending Requirements

- Enter this reference only when the user explicitly chooses the cloud path, or explicitly says "let the Miaoda Agent / cloud AI generate/iterate"; do not default to the cloud just because the user only says "make an X" or "give me a link."
- After entering the cloud path, even a minimal requirement can directly start generation, for example "make a voting tool" or "make a small standup app." First create the app according to the `--app-type` determined by the main routing (has database requirements → `full_stack`; pure frontend interaction with no database mentioned → defaults to `frontend`), then use `+chat --message "<用户原话>"` to pass the requirement through; do not invent entities, fields, or business details.
- If the requirement is too broad, you may keep the original wording in `+chat --message` and add only one sentence: "Please generate a general version first; it can be iterated on later"; do not block generation with multiple rounds of follow-up questions.

<a id="会话落点"></a>
## Session Placement

| Situation | Action |
|---|---|
| Brand-new app + cloud generation | First `+create --app-type <frontend\|full_stack>` according to the type determined by the main routing (defaults to frontend when no database is mentioned) to get `app_id`, then `+session-create` -> `+chat` |
| app_id known, user did not specify a session | First `+session-list`; if there is an active session, ask the user whether to continue the existing one or start a new one |
| User says "start a new one / change the topic" | `+session-create`, then `+chat` |
| User says "continue from just now" | Reuse the context session_id; if unavailable, `+session-list` and let the user choose |
| User asks about a session's "what step it is at / current status / latest progress" | Use `+session-get --session-id <sid>` to read status. `+session-list` is only responsible for discovering/selecting sessions and does not include execution status; its returning empty does not mean there is no status to query (session_id may also come from context); do not use `+session-list`/`+release-list` instead of `+session-get` to answer about progress |

<a id="初始化-vs-增量修改"></a>
## Initialization vs Incremental Modification

`+chat` single-turn duration varies greatly, depending on whether the target app is **already initialized**. The polling cadence differs between the two; **determine the status clearly before `+chat`**; do not use "is this the first message sent" as a proxy judgment—a newly created session does not mean the app has never been initialized.

<a id="判定规则"></a>
### Determination Rules

**Already initialized** (satisfying any one counts as initialized):

1. A project directory for that app exists locally (already `+init` or cloned), **and** the git commit count > 2;
2. At the application level (cloud), there is at least one committed version, determined by any of the following signals:
   - Committed version information appears in the return of `lark-cli apps +session-get --app-id <app_id> --session-id <session_id>`;
   - In the target app entry of `lark-cli apps +list` (with `--keyword <name>` to locate it if necessary), `is_published: true`.

**Not initialized** (both conditions hold simultaneously):

1. No project directory for that app exists locally;
2. There is no committed version at the application level (that is, both cloud signals above evaluate to false).

<a id="两种-chat-的行为"></a>
### Behavior of the Two `+chat`

| State | Server-side Action | Single-turn Duration | Polling Recommendation |
|---|---|---|---|
| Already initialized → **Incremental Modification** | The cloud Agent makes local modifications to **committed code** on the existing cloud workspace, skipping solution design and first-time generation | Usually minute-level | When `next_poll_after_ms` is empty, once every 5-10 seconds |
| Not initialized → **First Initialization + Generation** | The server runs the full app initialization flow: requirement analysis, technical solution, data model, UI and backend code generation, first version of code committed to the cloud workspace | Depends on requirement complexity, **usually 20~50 minutes** | When `next_poll_after_ms` is empty, once every 60-120 seconds |

During the initialization phase, `+session-get` may keep returning `building` / `running` for a long time; this is a normal state, **do not treat it as a failure, and do not rush the user**.

<a id="字段注意"></a>
## Field Notes

All fields uniformly use snake_case, both top-level and nested turn fields: `session_id`, `is_active`, `is_streaming`, `next_poll_after_ms`, `latest_turn.turn_id`, `latest_turn.status`, `latest_turn.user_message`, `latest_turn.messages`.

`+session-stop` only stops the currently running turn; it does not close the session; after stopping, you can still continue `+chat`.

<a id="不适用"></a>
## Not Applicable

- The user wants to write code locally, modify the repository, or run a dev server: read [`lark-apps-local-dev.md`](lark-apps-local-dev.md).
