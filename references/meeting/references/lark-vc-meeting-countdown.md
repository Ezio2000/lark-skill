# vc +meeting-countdown

Set, extend, end early, or close the in-meeting countdown window.

This module corresponds to shortcut: `lark-cli vc +meeting-countdown` (calls `POST /open-apis/vc/v1/bots/countdown`).

<a id="适用场景"></a>
## Applicable Scenarios

- The user requests setting a countdown in an ongoing meeting, for example "set a 5-minute countdown".
- The user requests extending the current countdown, for example "extend by 2 more minutes".
- The user requests ending early or closing the current countdown.
- Only for ongoing meetings; ended meetings are not supported.

<a id="身份规则"></a>
## Identity Rules

Whichever identity path `meeting_id` was obtained from, use that same identity when operating the countdown:

| meeting_id source | Identity when operating |
| --- | --- |
| `+meeting-list-active --as user` | `+meeting-countdown --as user` |
| `+meeting-list-active --as bot --user-id <user_open_id>` | `+meeting-countdown --as bot` |
| `+meeting-join --as bot` returned `meeting.id` | `+meeting-countdown --as bot` |

Do not switch a `meeting_id` discovered with user identity to operate with app identity, and do not switch a `meeting_id` discovered with app identity to operate with user identity, unless the user explicitly requests a switch.

<a id="参数"></a>
## Parameters

| Parameter | Description |
| --- | --- |
| `--meeting-id` | Required, long numeric `meeting_id`, not the 9-digit meeting number |
| `--action` | Required, `set`, `prolong`, `end_in_advance`, or `close_window` |
| `--duration` | Countdown duration, in minutes; `set` and `prolong` are required |
| `--need-play-audio-at-end` | Only available for `set`, indicates playing a notification sound when the countdown ends |
| `--reminder-before-end` | Only available for `set`, reminder point unit is minutes; only supports passing one value |

Both `duration` and `reminder_before_end` are in minutes; the reminder time must be greater than 0 and less than `duration`.

<a id="设置倒计时"></a>
## Set Countdown

```bash
lark-cli vc +meeting-countdown --as user \
  --meeting-id <meeting_id> \
  --action set \
  --duration 5 \
  --need-play-audio-at-end \
  --reminder-before-end 1
```

Dry-run request body example:

```json
{
  "meeting_id": "<meeting_id>",
  "action": "set",
  "duration": 5,
  "need_play_audio_at_end": true,
  "reminder_before_end": 1
}
```

<a id="延长倒计时"></a>
## Extend Countdown

```bash
lark-cli vc +meeting-countdown --as bot \
  --meeting-id <meeting_id> \
  --action prolong \
  --duration 2
```

<a id="提前结束或关闭倒计时"></a>
## End Early or Close Countdown

```bash
lark-cli vc +meeting-countdown --as user --meeting-id <meeting_id> --action end_in_advance
lark-cli vc +meeting-countdown --as user --meeting-id <meeting_id> --action close_window
```

When ending early or closing the countdown window, do not pass `--duration`, `--need-play-audio-at-end`, or `--reminder-before-end`.

<a id="9-位会议号处理"></a>
## Handling 9-Digit Meeting Number

If the user provides a 9-digit meeting number and requests operating the countdown:

1. First execute `+meeting-list-active` with the current identity.
2. In the returned results, match the 9-digit meeting number by `meeting_no`.
3. After matching a unique meeting, take the long numeric `meeting_id`.
4. Execute `+meeting-countdown` with the same identity used when discovering that meeting.

Do not automatically join the meeting when matching fails. Only when the user explicitly requests "have the app bot join/listen in/attend on behalf" should you switch to `+meeting-join`.

<a id="权限和前置条件"></a>
## Permissions and Prerequisites

- User identity: the current user must be in that meeting.
- App identity: the app bot must be in that meeting.
- Requires `vc:meeting.interaction:write` permission; app identity also requires the app to be installed and the data scope to be configured.

When there is an app identity permission error, do not guide the user to repeatedly `auth login`. Handle it according to the main skill's "App Identity Permission Configuration Check".

<a id="相关"></a>
## Related

- [lark-vc-meeting-list-active](lark-vc-meeting-list-active.md) — discover the current ongoing meeting ID
- [lark-vc-meeting-events](lark-vc-meeting-events.md) — read in-meeting events
- [lark-vc-meeting-message-send](lark-vc-meeting-message-send.md) — send in-meeting text or reaction
- [lark-vc-agent-meeting-join](lark-vc-agent-meeting-join.md) — app bot joins meeting
