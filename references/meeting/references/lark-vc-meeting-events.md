
# vc +meeting-events

Query the list of in-meeting events for an ongoing video meeting. This command is a **read operation** and must use the same source identity as `meeting_id`: meetings discovered with user identity continue to be read with user identity, and meetings discovered with app identity or joined by the app bot continue to be read with app identity. For ended meetings, there is a **5-minute grace window after the meeting ends**; when reading with app identity, the app bot is required to have appeared in this meeting.

This module corresponds to the shortcut: `lark-cli vc +meeting-events` (calls `GET /open-apis/vc/v1/bots/events`).

Visibility boundaries:

- `meeting_id` comes from `+meeting-list-active --as user`: subsequent event reads continue with `--as user`.
- `meeting_id` comes from `+meeting-list-active --as bot --user-id <user_open_id>` or `+meeting-join --as bot`: subsequent event reads continue with `--as bot`.
- Under app identity, the app bot must be in or have attended the meeting; the app identity active meeting returns meetings where "the target user is in the meeting and the app bot is also in the meeting," which does not mean any `meeting_id` can be read.

<a id="命令"></a>
## Command

```bash
# Default usage: pull all events visible to the current identity; output a readable timeline
lark-cli vc +meeting-events --as <same_identity> --meeting-id <id> --page-all --format pretty

# Specify a time range, and pull all events currently visible within that time window
lark-cli vc +meeting-events --as <same_identity> --meeting-id <id> --start 2026-04-17T15:00:00+08:00 --end 2026-04-17T16:00:00+08:00 --page-all --format pretty

# Continue querying new events based on the last saved page_token
lark-cli vc +meeting-events --as <same_identity> --meeting-id <id> --page-token <last_page_token> --page-all --format pretty
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--meeting-id <id>` | Yes | Meeting ID (long numeric ID, not the 9-digit meeting number) |
| `--start <time>` | No | Start time, supports ISO 8601 / `YYYY-MM-DD` / Unix seconds |
| `--end <time>` | No | End time, supports ISO 8601 / `YYYY-MM-DD` / Unix seconds |
| `--page-token <token>` | No | Continue pulling the next page from the specified pagination cursor |
| `--page-size <n>` | No | Page size per page in single-page mode. The CLI automatically clamps it to `20-100`; when `--page-all` is passed, `100` is used fixed |
| `--page-all` | No | Auto-paginate until there are no more pages (there is an internal safety limit) |

<a id="核心约束"></a>
## Core Constraints

<a id="1-输入必须是-meeting_id不是-9-位会议号"></a>
### 1. The input must be meeting_id, not the 9-digit meeting number

`--meeting-id` must be the meeting's long numeric ID. It usually comes from:
- `meeting.id` in the `+meeting-join` response body
- `meeting_id` in the `+meeting-list-active` response body
- `id` in the `+search` result

**Do not** pass the 9-digit meeting number (`--meeting-number`) to this command.
If `meeting_id` comes from `+meeting-list-active`, subsequent `+meeting-events` must use the same identity; if multiple meetings are returned, first let the user choose the specific `meeting_id`.

If the user provides a 9-digit meeting number and does not explicitly request the app bot to join, first query active meetings using the current scenario identity and match by `meeting_no`. After matching a unique item, take that item's long numeric `meeting_id`, then call this command with the same identity; if matching fails, do not automatically join the meeting unless the user explicitly says "join / have the app bot listen in / attend on my behalf."

<a id="2-身份来源是读取事件的权限锚点"></a>
### 2. Identity source is the permission anchor for reading events

- `+meeting-events` supports `--as user` and `--as bot`.
- User identity path: meetings discovered with user identity continue to be read with user identity.
- App identity path: the app bot must be in or have attended the meeting; do not directly query any `meeting_id`.
- Do not arbitrarily switch identities after obtaining `meeting_id`. When identities are inconsistent, common results are an empty list, `no permission`, or `bot is not in meeting`.

<a id="3-应用身份的可见性窗口"></a>
### 3. Visibility window for app identity

If the app bot has left the meeting, did not join, or the meeting can no longer determine identity, the backend usually reports:
- `bot is not in meeting, no permission`

More precisely, the backend's current judgment rules are:

- **Meeting in progress**: requires the app bot to **currently still be in the meeting**
- **Within 5 minutes after the meeting has ended**: as long as the app bot **has ever appeared in this meeting**, events can still be pulled
- **More than 5 minutes after the meeting ends**: treated as meeting ended, and the event stream is usually no longer returned
- **The app bot has never actually joined**: even if the meeting is still in progress or just ended, `10005 bot is not in meeting` is returned

<a id="4-自动分页规则"></a>
### 4. Auto-pagination rules

- **First distinguish two layers of defaults**:
  - The shortcut itself: when `--page-all` is not passed, only 1 page is queried.
  - This module's default policy: unless the user explicitly requests to view only one page, or you really need to control the response body size, by default you **must actively include `--page-all`** to pull all currently visible events in one go as much as possible.
- Passing `--page-all`: enables auto-pagination until there are no more pages.
- When `--page-all`, the CLI uses the maximum `page_size=100` fixed.

Execution guidelines:

- **Default command template**: `lark-cli vc +meeting-events --as <same_identity> --meeting-id <id> --page-all --format pretty`
- If you find that you executed a single-page query without `--page-all`, and the response contains `has_more=true` / `more available` / non-empty `page_token`, you should immediately realize that this is only a partial result.
- In the above situation, the default remedy is to continue pulling using the returned `page_token`, for example: `lark-cli vc +meeting-events --as <same_identity> --meeting-id <id> --page-token <returned_page_token> --page-all --format pretty`
- Only when the user explicitly requests "just look at the first page" or "do not paginate for now" should you not include `--page-all` by default
- As long as you are answering about **the content of an ongoing meeting** based on `+meeting-events`, you cannot directly reuse the previous query result. Whether the user is asking "who is speaking now," "what just happened," "what are the latest events," or asking you to "summarize what this meeting is about," you must first re-execute `+meeting-events` to confirm that you have the latest event stream, and then answer the user. Only when the user explicitly requests to continue analysis based on a certain historical snapshot may you reuse old results.

<a id="5-输出格式差异"></a>
### 5. Output format differences

- `--format pretty`: the default recommended format, outputs the current identity and an item-by-item timeline, suitable for quickly understanding "what happened."
- `--format json`: a structured contract, whose top level contains `meeting`, `identity`, `events`, `has_more`, `page_token`. `identity` indicates the current reading identity; event actors uniformly contain `participant_type`, `role`, `label`; each event retains `payload` for tracing details.
- `--format ndjson`: outputs event lines with metadata lines, suitable for streaming consumption.

**Selection principle**: by default use `--format pretty` first; only when `pretty` lacks the structured fields necessary to complete the task should you switch to `--format json`. When the user explicitly requests JSON or the rules explicitly require structured fields, you may directly use `--format json`; when streaming consumption is needed, use `--format ndjson`.

> **JSON cost**: JSON retains the complete payload, and the output is usually much larger than `pretty`; when pulling all events for a long meeting, it will significantly consume context space.

> **Note**: body text in pretty output is escaped to a single line, and real line breaks are displayed as `\n` to avoid disrupting the timeline layout.

<a id="6-内容理解模式共享文档不能只看标题"></a>
### 6. Content understanding mode: shared documents cannot be judged by title alone

When the user's intent is:

- "Summarize this meeting"
- "What was this meeting about"
- "What conclusions / to-dos / key discussions are there"
- "What is being discussed in the shared document"

Do not answer based only on the event timeline. At this point `+meeting-events` is only a **clue finder**, not the final information source.

Execution guidelines:

- If the context does not clearly specify `meeting_id`, first choose the identity according to the user's current intent: for "me / the meeting the current user is in," use `lark-cli vc +meeting-list-active --as user --format json`; for "the target user's meeting visible to the app bot," use `lark-cli vc +meeting-list-active --as bot --user-id <user_open_id> --format json`. If multiple meetings are returned, first let the user choose.
- If the context only has a 9-digit meeting number, first execute `+meeting-list-active` using the current identity and match by `meeting_no`; after matching a unique meeting, then query events. Do not automatically call `+meeting-join` just to summarize the meeting.
- After confirming `meeting_id`, use its source identity to execute `lark-cli vc +meeting-events --as <same_identity> --meeting-id <id> --page-all --format pretty` to pull the latest event stream.
- If the event stream shows shared content (JSON event type is `magic_share_started`; the pretty timeline displays "started sharing" or "is sharing" according to `start_reason`), and contains clues such as the document title or URL, you must continue to read the shared document content before generating a summary, and cannot summarize the meeting content based only on the sharing event and document title.
- If there are multiple shared documents, read the relevant documents according to the user's question; when processing a document context event, you must precisely associate it by that item's `share_id`, and cannot substitute "the most recent sharing."
- If document reading fails, you must clearly state "the following summary is based only on the in-meeting event stream, and the shared document content was not successfully read."

<a id="7-文档上下文事件消费"></a>
### 7. Document context event consumption

`document_context_changed` is a read-only clue event. When subsequent processing such as comments, sections, or previews needs to be performed based on this event, you must use `+meeting-events --page-all --format json` to read complete fields such as `share_id`, `comment_id`, `element_token`; when only displaying the timeline to the user, still use pretty by default. `vc +meeting-events` retains the original payload and derives actor and pretty timeline according to the existing event output conventions; it will not expand the JSON/NDJSON common envelope for a single event type, nor will it query comments, download materials, or write files. Subsequent Drive/Docs commands can only be explicitly selected by the Agent according to the table below.

<a id="共享会话关联"></a>
#### Shared session association

`share_id` identifies one sharing session. The Agent consumes the complete event stream in event time order and maintains sharing session state:

1. Read `share_id` and `share_doc` from `payload.magic_share_started_items[]`, establish the `share_id -> share_doc` mapping, and mark the session as started. When the same `share_id` repeatedly carries the same document, treat it as an idempotent event; if it points to a different document, stop parsing and do not overwrite the old mapping.
2. `document_context_changed_items[]` precisely looks up this mapping through its own `share_id`. In the current contract, the item's own `share_doc` does not provide document information; only retain its original value, do not use it as a URL/title source, and do not perform conflict determination.
3. `payload.magic_share_ended_items[]` uses the same `share_id` to mark the end of this session. Historical mappings may be retained to explain context events that occurred before the end within this batch, but they can no longer serve as a new active sharing session.
4. When incremental pulling starts midway through a session and there is no corresponding local mapping, re-pull the complete event stream containing `magic_share_started`; if it still cannot be matched, mark it as unresolved. It is forbidden to fall back to the current document, the most recent sharing, or any other `share_id`.

<a id="字段合同"></a>
#### Field contract

| Path | Meaning and handling |
| --- | --- |
| `payload.magic_share_started_items[].share_id/share_doc` | Establish a mapping between one sharing session and the document URL/title. When `share_id` is missing, do not establish a mapping. |
| `payload.magic_share_started_items[].start_reason` | `share_started` or missing indicates a real start; `share_detected` indicates that an existing sharing was discovered when enabling the Agent join capability. Both establish a sharing mapping. |
| `payload.magic_share_ended_items[].share_id` | End the sharing session for the same `share_id`; must not end other mappings. |
| `payload.document_context_changed_items[]` | Structured consumption reads in original order; pretty timeline follows unified time sorting. Only when each item has exactly one known context is a pretty entry generated; unknown/ambiguous items retain only raw. |
| `item.operator` | The actor of the current item; when ID/name is missing, do not guess the sharing initiator. |
| `item.share_id` | The sharing session to which the current context belongs; use it to precisely look up the `share_doc` mapping established by `magic_share_started`. |
| `item.share_doc.url/title` | Currently not used as a document metadata information source; retain it in the raw payload for compatibility with future extensions. Document URL/title is obtained only from the `magic_share_started` mapping of the same `share_id`. |
| `item.time` | Unix millisecond string; when missing or invalid, the timeline falls back to the event time. |
| `item.comment_focus.comment_id/focused` | Only `focused=true` precisely queries one comment ID; `false` is clearing focus, zero queries. |
| `item.section_location.parent_titles/title/level` | `section_path` appends title after the original parent order, discards empty segments after trim, and joins with ` > `; `level` is only for diagnostics and does not participate in truncation or layer filling. |
| `item.element_preview.action/element_type/element_token/block_id` | Only `open + image + token` and `open + whiteboard + token` can be routed under explicit preview intent; other combinations result in zero calls. |
| Event common envelope | JSON/NDJSON uses only the existing `event_id/event_type/event_time/actors/payload`; do not add a new top-level `summary/section_path`, and do not invent `derived.document_context`. |
| Event `payload` | Original recovery surface; unknown fields are retained, top-level empty arrays follow the compression rules shared by all meeting events, and derived fields are not written back to the payload. |

<a id="评论聚焦只查一个-id"></a>
#### Comment focus: query only one ID

First read the current item's `share_id` and `comment_focus.comment_id`, then obtain `share_doc.url` according to "shared session association." Prefer passing the complete URL to the existing shortcut and let it parse the actual `file_token/file_type` (including Wiki unwrapping); if the upstream leaves only a bare token, you must also provide the parsed and supported `file_type`.

```bash
# Recommended: share_doc.url is complete and usable
lark-cli drive +batch-query-comments \
  --as <same_identity> \
  --url "<share_doc.url>" \
  --comment-ids "<comment_focus.comment_id>" \
  --format json

# Use only when a bare token/type has already been reliably parsed
lark-cli drive +batch-query-comments \
  --as <same_identity> \
  --token "<file_token>" \
  --type "<file_type>" \
  --comment-ids "<comment_focus.comment_id>" \
  --format json
```

This shortcut corresponds to `drive.file.comments.batch_query`, and the request body must contain only `comment_ids:["<当前comment_id>"]`. Response handling rules:

1. The entire response `items` length must be exactly 1, and `items[0].comment_id` must be exactly equal to the request ID. If `items` is empty, has more than 1 item, or the unique item's ID differs, stop; even if exactly one item among multiple matches, you must not select that item and continue. On failure, retain `share_doc/comment_id`, and it is forbidden to switch to `drive +list-comments` to scan the entire document.
2. `item.quote` is the reference position; the comment body and replies are in `item.reply_list.replies`, of which the first is the root comment.
3. For completeness, look at the **`item.has_more`** of the matched comment card, not the outer comment pagination, and not guessing based on non-empty `page_token`. When `item.has_more=false`, directly use the embedded list, with zero `+list-replies` calls.
4. When `item.has_more=true`, ignore the truncated list and rebuild complete replies starting from **the first page without `--page-token`**:

```bash
lark-cli drive +list-replies \
  --as <same_identity> \
  --url "<share_doc.url>" \
  --comment-id "<comment_focus.comment_id>" \
  --page-size 100 \
  --format json

lark-cli drive +list-replies \
  --as <same_identity> \
  --url "<share_doc.url>" \
  --comment-id "<comment_focus.comment_id>" \
  --page-size 100 \
  --page-token "<returned_page_token>" \
  --format json
```

The first page's `items[0]` is the root comment; `items[0]` on subsequent pages are ordinary replies. Accumulate in original page order until the page-level `has_more=false`. If `has_more=true` but `page_token` is empty, duplicates an already-used token, API/permission fails, or the comment ID changes, stop immediately and mark it as `partial`; retain the content already obtained and the original identifier, do not loop, do not repeat the root comment, and do not claim completeness.

<a id="章节定位"></a>
#### Section location

Structured consumption directly reads the current `section_location` item. The pretty timeline appends `title` in the original order of `parent_titles`, discards empty segments after trim, and joins with ` > `; multiple section items are displayed separately, and one of them is not selected to override event-level scalars; when all titles are empty, no pretty entry is generated and only raw is retained. This path is a local display derivation, does not write back to JSON/NDJSON, and does not need or allow new API queries for it.

<a id="元素预览显式白名单"></a>
#### Element preview: explicit whitelist

Execute only when the user or upper-layer Agent explicitly requests a preview and the item matches the table below. Both commands write to `--output`, so the output path must be explicitly selected by this call; do not overwrite existing files by default.

| action | element_type | token condition | exact command |
| --- | --- | --- | --- |
| `open` | `image` | `element_token` non-empty | `lark-cli docs +media-preview --as <same_identity> --token "<element_token>" --output "<explicit-path>"` |
| `open` | `whiteboard` | `element_token` non-empty | `lark-cli docs +media-download --as <same_identity> --type whiteboard --token "<element_token>" --output "<explicit-path>"` |
| `close` | `image`/`whiteboard` | any | zero calls; pretty only records preview disabled |
| unknown | any | any | zero calls; do not generate a pretty entry, retain only raw |
| `open` | unknown/empty | any | zero calls; forbidden to pass the original value through to `--type` |
| `open` | `image`/`whiteboard` | token empty | zero calls; retain `block_id/element_type/action` and indicate missing token |

<a id="失败恢复"></a>
#### Failure recovery

- If the parser encounters an unknown field, ambiguous one-of, or a single item missing a field: retain the entire event `payload`, `event_id/event_type/event_time`, and available siblings; that item does not generate a pretty entry, and no generic description is synthesized.
- If `share_id` is missing, the mapping is not matched, or `share_doc` conflicts: echo `share_id`, available `share_doc.url/title`, and `comment_id`; if necessary, re-pull the complete event stream, and if it still cannot be associated, stop, and do not fall back to the most recent sharing.
- If `share_doc` cannot be parsed: echo `share_id`, `share_doc.url/title`, and `comment_id`, and indicate that a valid document URL or confirmed `file_token/file_type` is required; do not guess the type.
- Drive API/permission failure: retain the exact batch-query command and `comment_id`, restore permissions according to the CLI's `missing_scopes/hint`, and retry; do not scan all comments.
- Docs preview failure: retain `action/element_type/element_token/block_id` and the output path selected by the user, fix permissions or token, and retry the same whitelist command; do not let `meeting-events` automatically download as a fallback.
- Unknown context/type/action: retain raw and explain that the current CLI has no safe route; do not automatically call overwrite, download, or any guessed shortcut.

<a id="8-关于-page_token-的返回与续拉"></a>
### 8. About the return and continued pulling of `page_token`

- Whether this time you only query 1 page, or you have already pulled all currently visible events through `--page-all`, you should retain the last obtained `page_token` and return it to the user as well.
- As long as `has_more=true` appears in the response, `more available` appears in pretty, or a non-empty `page_token` is returned, you must first determine whether the current result is complete; by default, this means you still need to continue paginating.
- If `--page-all` was not used, but the above pagination signals appear, by default you should continue pulling the next page using the returned `page_token`, rather than ending directly. Only when the user explicitly does not want to continue paginating may you stop and clearly state that the current result is incomplete.
- The next time you continue to "query new events," you should preferentially reuse the last saved `page_token`, rather than pulling everything again from the beginning.
- Only when the user explicitly requests "replay all events from the beginning" should you ignore the historical `page_token` and restart from the first page.
- However, if what the user wants you to answer is **what this current meeting is talking about**, rather than "what was newly added after the last time," you should also first perform a new event query, and then decide whether you need to continue pulling based on the old `page_token`.

<a id="返回结构"></a>
## Return structure

Common top-level fields:

| Field | Description |
|------|------|
| `meeting` | Meeting identity and time status, including `id/topic/meeting_no/start_time/end_time/status` |
| `identity` | Current reading identity, including `id/name/participant_type/label` |
| `events` | Structured event list; each event follows the `event_id/event_type/event_time/actors/payload` common envelope, and event-specific data is kept in `payload` |
| `warnings` | Non-blocking warning list; the event list itself is still usable |
| `has_more` | Whether there is a next page |
| `page_token` | Next page cursor |

Common event `event_type` types:

| event_type | Meaning |
|-----------|------|
| `participant_joined` | A participant joined the meeting |
| `participant_left` | A participant left the meeting |
| `chat_received` | An in-meeting chat message was received |
| `transcript_received` | A transcript text was received |
| `magic_share_started` | Sharing started, or an existing share was discovered when the Agent join capability was enabled; distinguished by `start_reason` |
| `magic_share_ended` | Sharing ended |
| `document_context_changed` | Comment focus, chapter positioning, or element preview context changed |
| `countdown_changed` | An in-meeting countdown was set, extended, ended early, had its window closed, or naturally ended, or a near-expiry reminder occurred |

### Forwarding meeting chat and reactions to IM

When forwarding to IM, the Agent must first use the structured events from `+meeting-events --format json` to construct complete Feishu `post` content, then call the IM send shortcut. Do not parse the pretty/Markdown output, and do not first generate plain text or Markdown and then expect the IM side to recognize reactions a second time.

For events of `event_type == "chat_received"`, process `payload.chat_received_items` item by item:

- `message_type == 3` is an in-meeting reaction; when constructing IM `post` content, use the [`lark-im` reaction emoji list](../../im/references/lark-im-reactions.md) as the IM `emotion` whitelist. Keys within the whitelist are written as `{"tag":"emotion","emoji_type":"<content>"}`, for example `JIAYI`, `THUMBSUP`, `OK`.
- For reaction keys not in the IM reaction emoji whitelist, keep the original key but write it as a text node, for example `{"tag":"text","text":"[<content>]"}`; do not write it directly into `emotion.emoji_type`, otherwise the IM send will fail.
- Do not normalize case or guess mappings; `content` is the original reaction key and must be judged as-is.
- Write other chat messages as text nodes: `{"tag":"text","text":"<content>"}`.
- Finally call `im +messages-send --msg-type post --content '<post-json>'`, where `<post-json>` should mix renderable `emotion` nodes and text fallback; do not use `--markdown` to carry in-meeting reactions.
- If IM returns `message_content_emotion_tag's emoji_type is invalid`, only downgrade the illegal reaction key; do not degrade the entire message to plain text.
- If the user's original request already explicitly says "send to me / push to me / send to my chat / send to my direct chat", this already covers the recipient, content, and send action for this time; send directly to the current user and do not ask again "whether to send".
- By default, send using the app identity `--as bot`; only switch to `--as user` when the user explicitly requests "send using my own identity / user identity".
- If the user asks to send to a certain group or another person but the recipient cannot be uniquely determined, only ask for the missing recipient information.

```bash
lark-cli vc +meeting-events \
  --as <same_identity> \
  --meeting-id <id> \
  --page-all \
  --format json
```

If the user has already requested "send to me", `<open_id>` uses the current user's open_id; when parsing is needed, first use the user query capability to obtain the current user information. When constructing the IM post, only send the in-meeting content within the scope of the user's request; do not treat the previous natural language preview as the content to send.

<a id="pretty-输出示例"></a>
## pretty output example

```text
Meeting topic: Zhang San's video meeting
Meeting time: 2026-04-17 15:28:52 (in progress)

[00:00:33] Tomorrow's Shrimp BOE(ou_xxx) joined the meeting
[00:00:41] Zhang San(ou_xxx): [text] 6666
[00:00:44] Zhang San(ou_xxx) started sharing "Smart Minutes: Feishu 20251022-140223 March 9, 2026"
           URL: https://...
[00:01:32] Zhang San(ou_xxx): [reaction] JIAYI
```

<a id="如何获取输入参数"></a>
## How to obtain input parameters

| Input parameter | How to obtain |
|---------|---------|
| `meeting-id` | The `meeting.id` returned by `+meeting-join`; or the `meeting_id` returned by `+meeting-list-active`; or the `id` in the `+search` result. The source identity must also be recorded |
| `start` / `end` | The time range given by the user; if not given, default to all visible events |
| `page-token` | The `page_token` saved from the previous page or previous query result; persisting it is recommended, to make it easier to continue pulling new events next time |

<a id="常见错误与排查"></a>
## Common errors and troubleshooting

| Error symptom | Root cause | Solution |
|---------|---------|---------|
| `--meeting-id is required` | `--meeting-id` was not passed in | Pass in the long numeric `meeting.id` |
| `10005 bot is not in meeting` | Reading with app identity, but the app bot has never actually joined the meeting; or the meeting has ended but the app bot has never appeared in the meeting | If `meeting_id` came from user identity discovery, switch back to `--as user`; if app identity reading is really needed, first have the app bot join the meeting or confirm that it has attended, then use `--as bot`. **If you only want to see a participant snapshot, use `lark-cli vc meeting get --params '{"meeting_id":"<meeting.id>","with_participants":true}'` instead** |
| User identity has no permission / is not visible | The current user is not a visible participant of the meeting, or `meeting_id` was not obtained from the user identity path | Do not repeatedly execute `auth login`. First confirm whether `meeting_id` came from `+meeting-list-active --as user`; if the user explicitly wants to switch to app identity, then obtain the app-identity-readable `meeting_id` through `+meeting-list-active --as bot --user-id <user_open_id>`, or after the user explicitly agrees, have the app bot join the meeting, then read with `+meeting-events --as bot` |
| `20001 meeting_status_MEETING_END` | The meeting has ended and the backend-allowed 5-minute grace window has been exceeded | This interface is no longer suitable for continuing to pull events. First use `lark-cli vc +detail --meeting-ids <meeting.id>` to obtain meeting artifact information, then based on `note_display_type` / `note_id` / `minute_token` and the user's intent, choose the minutes body, verbatim transcript, or Minutes; for participants, use `lark-cli vc meeting get --params '{"meeting_id":"<meeting.id>"}' --with-participants` |
| `20002 meeting not exist` | `meeting_id` is wrong, or the meeting instance is currently unavailable (commonly caused by passing a 9-digit meeting number as meeting_id) | Confirm that what is passed in is the long numeric `meeting_id`, not a 9-digit meeting number |
| Insufficient app identity permissions | App permissions, tenant installation, or the data range accessible by permissions is not fully configured | Do not execute `auth login`. Ask the app developer to enable `vc:meeting.bot.join:write`; then check app publishing/installation and the data range accessible by permissions; if it still fails after correct configuration, keep the error code and `log_id`, and troubleshoot as a server-side permission exception |
| `HTTP 404` / `HTTP 500` | The server currently cannot find or process this meeting instance | Switch to a meeting_id that is in progress and visible to the bot, or troubleshoot the backend issue |

<a id="提示"></a>
## Tips

- This is an **in-meeting event stream** query, and is not suitable for searching historical meeting records; to search historical meetings, use `+search`.
- If the meeting has already ended, do not get stuck on `+meeting-events`:
  - First use `lark-cli vc +detail --meeting-ids <meeting.id>` to obtain meeting artifact information.
  - Then based on `note_display_type`, `note_id`, `minute_token`, and the user's intent, follow the artifact decision in `lark-meeting` to read the minutes body, verbatim transcript, or Minutes.
- Whether the event list is complete depends on when the app bot joined the meeting, when it left, and the range of in-meeting events currently visible to the backend. For ended meetings, events can usually still be pulled only **within 5 minutes after the end** and only when the app bot **was once in the meeting**.
- To query "who attended a certain meeting", use `vc meeting get --params '{"meeting_id":"<id>","with_participants":true}'` - this is a participant **snapshot** API, does not depend on whether the bot attended, and can also query ended meetings; **do not** use `+meeting-events` for participant queries.

<a id="相关场景"></a>
## Related scenarios
- [In-meeting events and in-meeting interactions](../scenes/live-meeting-interact.md)
- [App bot meeting attendance and in-meeting interactions](../scenes/live-meeting-attend.md)
