<a id="读取会中事件与会中互动"></a>
# Read in-meeting events and in-meeting interactions

Perform read-only queries or in-meeting write operations explicitly authorized by the user for an ongoing meeting. Use the app bot join scenario for real join/leave; use the meeting query scenario for ended meetings and post-meeting artifacts.

If the task includes "after the app bot joins, continue to fetch events or interactions," only read and execute the complete flow of [App bot participation and in-meeting interactions](live-meeting-attend.md); do not switch back and forth between the two scenarios.

<a id="发现进行中的会议"></a>
## Discover ongoing meetings

When there is no `meeting_id`, query by the perspective the user needs:

```bash
# Meetings the currently logged-in user is attending
lark-cli vc +meeting-list-active --as user --format json

# Meetings the target user is attending and where the app bot is also in the meeting
lark-cli vc +meeting-list-active --as bot --user-id <open_id> --format json
```

- `--user-id` must be the target user's `ou_` open_id.
- An empty result for the app identity does not mean the target user is not in a meeting; it only means no meeting was found where the target user and the app bot are both in the meeting.
- When multiple meetings are returned, show the title, meeting number, and `meeting_id` for the user to choose; do not arbitrarily pick the "most recent" one.
- When the user provides only a 9-digit meeting number, match it by `meeting_no` in the active meeting results; if matching fails, do not automatically join the meeting.
- Whichever identity `meeting_id` is obtained from, use that same identity for subsequent event reads, message sending, and countdown operations.

For identity visibility scope and meeting number matching, see [`lark-vc-meeting-list-active`](../references/lark-vc-meeting-list-active.md).

<a id="读取最新会中事件"></a>
## Read the latest in-meeting events

```bash
lark-cli vc +meeting-events --as <same_identity> --meeting-id <meeting_id> --page-all --format pretty
```

- By default, use `--page-all` to get the current complete event stream, and keep the returned `page_token` for the next incremental query.
- Before answering "now, just now, latest" or summarizing the current meeting, re-query the events; reuse old results only when the user explicitly asks for a historical snapshot.
- By default, use pretty to understand the timeline; use JSON when precise structured fields, document context, or forwarding to IM is needed.
- Do not use in-meeting events as a substitute for participant snapshots of ended meetings or post-meeting reviews.

For event types, pagination, the five-minute window, and error codes, see [`lark-vc-meeting-events`](../references/lark-vc-meeting-events.md).

<a id="读取共享内容和文档上下文"></a>
## Read shared content and document context

Precisely associate by `share_id`, `share_doc`, `comment_id`, `element_token`, and `block_id` in the event:

- When reading comments, query only the current `comment_id`; do not scan comments across the entire document.
- For multiple shared documents, select the relevant document based on the user's question; do not use "the most recent share" as a substitute for the current item's `share_id`.
- Download only when the user explicitly requests a preview and the event provides a supported `element_type` and token, and explicitly choose the output path.
- If association or reading fails, mark it partial and preserve the original identifier and raw payload; do not automatically download or guess the document type as a fallback.

For the precise event schema and subsequent commands, see the document context section of [`lark-vc-meeting-events`](../references/lark-vc-meeting-events.md).

<a id="读取当前会议画面"></a>
## Read the current meeting view

Read the view only when the user's question must read visual information from the current meeting composite view and the structured content is insufficient to answer. Applicable tasks include identifying the web address, interface state, or error actually displayed on screen share, understanding information that depends on layout or images such as charts and slides, and viewing the camera feed.

When events, captions, chat, or directly readable shared documents are already sufficient to answer, do not take a screenshot; meeting content queries, summaries, or shared document location should also not fall back to screenshots, and do not read the view merely because the meeting is ongoing.

When reading is needed, execute:

```bash
lark-cli vc +meeting-screenshot --as <same_identity> --meeting-id <meeting_id>
```

For identity, meeting ID, output file, and failure handling, see [`lark-vc-meeting-screenshot`](../references/lark-vc-meeting-screenshot.md).

<a id="发送会中文本或表情"></a>
## Send in-meeting text or reactions

Execute only when the user explicitly requests sending and confirms the target meeting and content:

```bash
lark-cli vc +meeting-message-send --as <same_identity> --meeting-id <meeting_id> --msg-type text --text <message>
```

- Sending uses the source identity of `meeting_id`; do not automatically join the meeting or first query meeting details in order to send.
- For reactions, use the case-sensitive complete emoji key from the Reference; do not invent keys.
- If sending fails, stop and report; do not automatically switch identities or resend, to avoid duplicate visible side effects.
- When the user wants to send a bound group or IM message, use `lark-im` instead; do not treat in-meeting message commands as group message capabilities.

For text, reactions, and permission rules, see [`lark-vc-meeting-message-send`](../references/lark-vc-meeting-message-send.md).

<a id="操作会中倒计时"></a>
## Operate the in-meeting countdown

Execute only when the user explicitly requests to set, extend, end early, or close the countdown:

```bash
lark-cli vc +meeting-countdown --as <same_identity> --meeting-id <meeting_id> --action set --duration <minutes>
```

- This is a write operation visible in the meeting; confirm the target meeting and action before executing.
- The operation uses the source identity of `meeting_id`; do not automatically join the meeting or switch identities for the countdown.
- When the user provides only a 9-digit meeting number, first execute `+meeting-list-active` with the current identity and match by `meeting_no`.
- `set` and `prolong` require `--duration`; when ending early or closing, do not include duration, reminder points, or ending audio parameters.

For actions, reminder points, and permission rules, see [`lark-vc-meeting-countdown`](../references/lark-vc-meeting-countdown.md).

<a id="处理未发现会议或权限错误"></a>
## Handle no meeting found or permission errors

- When no active meeting is found for the user identity, you may query the most recently ended meeting of the day; if there is still no result, ask for the time, topic, or meeting number, and do not expand the time range on your own.
- When no active meeting is found for the app identity, only explain the empty result for the current identity; do not automatically query historical meetings or perform a real join.
- When the user identity calls active meeting or event queries, for a missing ordinary scope, apply for `vc:meeting.meetingevent:read` according to the CLI hint; a missing ordinary scope does not mean the API does not support the user identity, and only switch to the app identity flow when the CLI explicitly states it is unsupported.
- When the app identity lacks permissions, do not execute `auth login`. Prefer handling according to the `missing_scopes`, `hint`, and `console_url` returned by the CLI; when judging manually, configure scopes by capability: app identity active meeting query requires `vc:meeting.bot.join:write`, in-meeting message sending requires `vc:meeting.message:write`, and in-meeting countdown requires `vc:meeting.interaction:write`. Then check in order the app release, tenant installation, and "data scope accessible by permission"; the data scope should be "filter by condition," with the condition "meeting owner contains matches the app's available scope."
- If it still fails after the scope, installation, and data scope are all correct, preserve the error code and `log_id` returned by the CLI, and troubleshoot as a server-side permission anomaly; do not repeatedly log in or retry with another identity.
