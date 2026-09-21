<a id="应用机器人参会与会中互动"></a>
# App bot meeting attendance and in-meeting interaction

Orchestrate the complete in-meeting flow for an app bot: discover meetings it is already attending, or start or join a meeting after the user explicitly authorizes it; then pull in-meeting events, send text or in-meeting reactions, operate the countdown, and end the meeting or leave only when the user explicitly requests it.

<a id="选择入口"></a>
## Choose an entry point

| Current condition | Starting point |
|---|---|
| Already have a `meeting_id` obtained with the app identity | Pull events directly; do not query again or join the meeting |
| The app bot may already be in the meeting | When the target user `user_open_id` is known, first use `+meeting-list-active --as bot --user-id <user_open_id>` to discover the meeting |
| The user explicitly asks the bot to join, sit in on, or attend on behalf of someone | Use `+meeting-join --as bot` |
| The user explicitly asks the bot to start a calendar meeting | Use `+meeting-join --as bot --action start` |
| Only want to check the meeting the current user is in | Use the user identity path in [In-meeting events and in-meeting interaction](live-meeting-interact.md); do not have the app bot join the meeting |

The user only providing a 9-digit meeting number or asking about meeting content does not equal authorizing the bot to join the meeting.

<a id="发现应用机器人已在参加的会议"></a>
## Discover meetings the app bot is already attending

When the target user `ou_` open_id is known, first query active meetings where "the target user is currently in the meeting and the app bot is also in the same meeting":

```bash
lark-cli vc +meeting-list-active --as bot --user-id <user_open_id> --format json
```

- When multiple meetings are returned, show the topic, meeting number, and `meeting_id` for the user to choose; do not arbitrarily take the first one.
- An empty return does not mean the target user is not in a meeting; it only means no visible meeting was found where the app bot is also in the meeting.
- When the user provides a 9-digit meeting number, match it in the results by `meeting_no`; if matching fails, do not automatically join the meeting.
- Save the selected long integer `meeting_id`; subsequent event, message, countdown, and leave commands all continue to use `--as bot`.

For identity visibility scope, multi-meeting selection, and meeting number matching, see [`lark-vc-meeting-list-active`](../references/lark-vc-meeting-list-active.md).

<a id="发起或加入会议"></a>
## Start or join a meeting

Execute only when the user explicitly asks the app bot to start, join, sit in on, or attend on behalf of someone. The input is a 9-digit meeting number, not the long integer `meeting_id`.

```bash
# Start a calendar meeting and join it
lark-cli vc +meeting-join --as bot --meeting-number <9_digit_meeting_number> --action start

# Join an ongoing meeting
lark-cli vc +meeting-join --as bot --meeting-number <9_digit_meeting_number>
```

- Before joining, confirm the target meeting number and the user's intent; this is a write operation visible to other participants.
- `--action start` is only used to start a qualifying calendar meeting; when not passed, keep joining an ongoing meeting.
- Save the returned `meeting.id`; subsequent invitations, event pulling, in-meeting message sending, countdown operations, ending, or leaving all use this ID and `--as bot`.
- The app bot can join multiple meetings at the same time; it does not need to leave other meetings before joining a new one.
- Confirm successful joining based on the returned status; do not treat "request initiated" as already joined.

For meeting passwords, waiting rooms, write operation risks, and exception recovery, see [`lark-vc-agent-meeting-join`](../references/lark-vc-agent-meeting-join.md).

<a id="邀请参会人"></a>
## Invite participants

Execute only when the user explicitly requests an invitation. The input is the long number `meeting_id`, not a 9-digit meeting number.

```bash
# Invite specified users
lark-cli vc +meeting-invite --as bot --meeting-id <meeting_id> --type SELECTED --open-ids <open_id>

# Invite all eligible calendar participants
lark-cli vc +meeting-invite --as bot --meeting-id <meeting_id> --type ALL_SUGGESTED
```

- The app bot must already be in the target Calendar VC.
- `SELECTED` accepts user `open_id`; `ALL_SUGGESTED` has the server filter eligible calendar participants.
- Confirm the invitation status based on the returned result; do not treat request submission as participants having joined.

For invitation types, participant limits, and result semantics, see [`lark-vc-agent-meeting-invite`](../references/lark-vc-agent-meeting-invite.md).

<a id="拉取会中事件"></a>
## Pull in-meeting events

Use the `meeting_id` obtained from discovery or joining with the app identity:

```bash
lark-cli vc +meeting-events --as bot --meeting-id <meeting_id> --page-all --format pretty
```

- By default, use `--page-all` to pull the current complete event stream, and keep the returned `page_token` for subsequent incremental queries.
- Before answering "now, just now, latest" or summarizing the current meeting, pull the latest events again; do not directly reuse an old snapshot.
- The app bot must be in the meeting, or must have attended within the visible grace window after the meeting ended; do not attempt to read with an arbitrary `meeting_id`.
- In-meeting events cannot replace participant snapshots, minutes, transcripts, or recordings of an ended meeting.

For event types, pagination, the five-minute window after ending, and document context handling, see [`lark-vc-meeting-events`](../references/lark-vc-meeting-events.md).

<a id="发送会中文本或表情"></a>
## Send in-meeting text or reactions

Each send is a write operation visible to in-meeting participants. Execute only when the user explicitly requests sending and the target meeting and content have been confirmed.

```bash
# Text message
lark-cli vc +meeting-message-send --as bot --meeting-id <meeting_id> --msg-type text --text "<message>"

# Regular in-meeting reaction
lark-cli vc +meeting-message-send --as bot --meeting-id <meeting_id> --msg-type reaction --emoji-type THUMBSUP
```

- Always continue to use the app identity that produced `meeting_id`; do not switch to a user identity.
- The reaction must use the complete case-sensitive `emoji_type` list from the Reference; do not invent keys.
- When sending fails, stop and report; do not automatically retry or switch identities, to avoid producing duplicate visible messages.
- When the user wants to send a bound group or IM message, switch to `lark-im` instead of using the in-meeting message command.

For text, reaction semantics, the complete emoji key list, and idempotency parameters, see [`lark-vc-meeting-message-send`](../references/lark-vc-meeting-message-send.md).

<a id="操作会中倒计时"></a>
## Operate the in-meeting countdown

Each countdown operation is a write operation visible to in-meeting participants. Execute only when the user explicitly requests setting, extending, ending early, or closing the countdown.

```bash
# Set countdown
lark-cli vc +meeting-countdown --as bot --meeting-id <meeting_id> --action set --duration <minutes>

# Extend countdown
lark-cli vc +meeting-countdown --as bot --meeting-id <meeting_id> --action prolong --duration <minutes>
```

- Always continue to use the app identity that produced `meeting_id`; do not switch to a user identity.
- When the user only provides a 9-digit meeting number, first match it against the app identity's active meeting list; if matching fails, do not automatically join the meeting just for the countdown, unless the user explicitly asks the bot to join.
- `end_in_advance` and `close_window` do not carry `--duration`, reminder points, or ending audio parameters.
- When an operation fails, stop and report; do not automatically retry or switch identities, to avoid duplicate visible side effects.

For actions, reminder points, and permission rules, see [`lark-vc-meeting-countdown`](../references/lark-vc-meeting-countdown.md).

<a id="结束会议"></a>
## End the meeting

Execute only when the user explicitly requests ending the entire meeting; do not confuse ending the meeting with the bot leaving the meeting.

```bash
lark-cli vc +meeting-end --as bot --meeting-id <meeting_id> --yes
```

- The input is the long number `meeting_id`.
- The current app bot must be the Host; a successful end will end the entire meeting.
- Confirm the meeting has ended based on the returned status.

For identity, permissions, and failure reasons, see [`lark-vc-agent-meeting-end`](../references/lark-vc-agent-meeting-end.md).

<a id="离开会议"></a>
## Leave the meeting

Execute only when the user explicitly requests the bot to exit, leave, or end attendance:

```bash
lark-cli vc +meeting-leave --as bot --meeting-id <meeting_id>
```

- Use the `meeting_id` obtained from joining or from the app identity's active meeting query, and confirm the bot is currently in that meeting.
- Do not automatically leave just because the task is complete.
- When the user only wants post-meeting artifacts, switch to the meeting artifacts scenario; do not leave the meeting first for this purpose.
- Confirm leaving is complete based on the returned status.

For leave parameters, visible side effects, and completion determination, see [`lark-vc-agent-meeting-leave`](../references/lark-vc-agent-meeting-leave.md).

<a id="应用身份权限配置检查"></a>
## App identity permission configuration check

When the app identity returns `no permission`, `missing required scope(s)`, or `missing_scopes`, do not execute `auth login`. Check in order:

1. Handle according to the `hint` in the CLI error; when `console_url` is returned, provide it to the user as-is.
2. Confirm the app has enabled the corresponding permissions, and has been published and installed to the current tenant. Joining and app identity meeting queries require `vc:meeting.bot.join:write`; sending in-meeting messages requires `vc:meeting.message:write`; the in-meeting countdown requires `vc:meeting.interaction:write`.
3. On the open platform, confirm that "data scope accessible by permission" has been saved as "filter by condition", with the condition "meeting owner contains matches the app's available scope".
4. If the above configurations are all correct and it still fails, keep the error code and `log_id` returned by the CLI, and troubleshoot as a server-side permission exception; do not repeatedly log in or retry with another identity.

<a id="会后边界"></a>
## Post-meeting boundaries

- For searching ended meetings, participant snapshots, smart minutes, transcripts, Minutes, or recordings, switch to [Query meetings and their artifacts](query-meeting-and-artifacts.md).
- To send post-meeting artifacts to a group or private chat, first use the meeting artifacts scenario to obtain the results, then switch to `lark-im`.
