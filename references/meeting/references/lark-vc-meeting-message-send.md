# vc +meeting-message-send

Send an in-meeting text message or an in-meeting reaction emoji.

This module corresponds to shortcut: `lark-cli vc +meeting-message-send` (calls `POST /open-apis/vc/v1/bots/message`).

<a id="适用场景"></a>
## Applicable Scenarios

- The user asks to "send a message in the meeting", "notify everyone", or "send a message to the current meeting".
- The user asks to send an in-meeting emoji, for example "send a thumbs up", "send an OK", or "send a heart".
- The user asks to express in-meeting feedback, for example "can't hear", "can't see", "sound is clear", or "looks good".
- Only for meetings that are in progress; ended meetings are not supported.

<a id="身份规则"></a>
## Identity Rules

Whichever identity path `meeting_id` was obtained from, use that same identity when sending the message:

| meeting_id source | Identity when sending |
| --- | --- |
| `+meeting-list-active --as user` | `+meeting-message-send --as user` |
| `+meeting-list-active --as bot --user-id <user_open_id>` | `+meeting-message-send --as bot` |
| `meeting.id` returned by `+meeting-join --as bot` | `+meeting-message-send --as bot` |

Do not switch a `meeting_id` discovered via user identity to send with app identity, and do not switch a `meeting_id` discovered via app identity to send with user identity, unless the user explicitly requests a switch.

<a id="参数"></a>
## Parameters

| Parameter | Description |
| --- | --- |
| `--meeting-id` | Required, long numeric `meeting_id`, not the 9-digit meeting number |
| `--msg-type` | Optional, `text` or `reaction`; can be inferred automatically when only `--text` or only `--emoji-type` is passed |
| `--text` | Text message content |
| `--emoji-type` | In-meeting reaction emoji key, case-sensitive, must be selected from the "Complete `emoji_type` List" in this document |
| `--uuid` | Optional, idempotency key; if not passed, the server generates one |

The CLI maps `--text` or `--emoji-type` uniformly to the `content` field of the OpenAPI request body; `meeting_id` is also passed in the request body.

<a id="文本消息"></a>
## Text Message

```bash
lark-cli vc +meeting-message-send --as user --meeting-id <meeting_id> --text "稍等，我在看文档"
```

The text message appears in the in-meeting text interaction area. Do not treat it as a bound group message sending capability; if the user explicitly requests sending to a group chat, route to `lark-im`.

<a id="会中表情"></a>
## In-Meeting Emoji

In-meeting reactions support regular Feishu reaction emoji, and also support 4 VC feedback keys.

Common semantics:

| User expression | Recommended `emoji_type` |
| --- | --- |
| Thumbs up, give a like, approve | `THUMBSUP` |
| +1, plus one, agree, same as above | `JIAYI` |
| OK, alright | `OK` |
| Received, understood | `Get` |
| Heart, red heart | `HEART` |
| Like, love it | `LOVE` |
| Finger heart | `FINGERHEART` |
| Looks fine, can continue | `LGTM` |
| Done, completed | `DONE` |
| -1, minus one | `MinusOne` |
| Disagree, thumbs down | `ThumbsDown` |
| Can't hear, no sound | `VC_NoSound` |
| Can't see, screen has a problem | `VC_CanNotSee` |
| Sound is clear | `VC_SoundsClear` |
| Meeting screen looks good, screen looks fine | `VC_LooksGood` |

```bash
lark-cli vc +meeting-message-send --as bot --meeting-id <meeting_id> --msg-type reaction --emoji-type LOVE
lark-cli vc +meeting-message-send --as bot --meeting-id <meeting_id> --msg-type reaction --emoji-type VC_NoSound
```

Do not fabricate a `emoji_type` outside the list, and do not change mixed-case values to all uppercase; for example, `EatingFood`, `CheckMark`, and `StatusInFlight` must all be passed as their original values.

If the user provides natural language semantics, you may select the key with the closest semantics from the list below; if uncertain, confirm with the user first.

<a id="完整-emoji_type-列表"></a>
### Complete `emoji_type` List

The following list is consistent with the official IM reaction emoji list, and additionally includes VC in-meeting specific feedback keys:

```text
OK, THUMBSUP, THANKS, MUSCLE, FINGERHEART, APPLAUSE, FISTBUMP, JIAYI
DONE, SMILE, BLUSH, LAUGH, SMIRK, LOL, FACEPALM, LOVE
WINK, PROUD, WITTY, SMART, SCOWL, THINKING, SOB, CRY
ERROR, NOSEPICK, HAUGHTY, SLAP, SPITBLOOD, TOASTED, GLANCE, DULL
INNOCENTSMILE, JOYFUL, WOW, TRICK, YEAH, ENOUGH, TEARS, EMBARRASSED
KISS, SMOOCH, DROOL, OBSESSED, MONEY, TEASE, SHOWOFF, COMFORT
CLAP, PRAISE, STRIVE, XBLUSH, SILENT, WAVE, WHAT, FROWN
SHY, DIZZY, LOOKDOWN, CHUCKLE, WAIL, CRAZY, WHIMPER, HUG
BLUBBER, WRONGED, HUSKY, SHHH, SMUG, ANGRY, HAMMER, SHOCKED
TERROR, PETRIFIED, SKULL, SWEAT, SPEECHLESS, SLEEP, DROWSY, YAWN
SICK, PUKE, BETRAYED, HEADSET, EatingFood, MeMeMe, Sigh, Typing
Lemon, Get, LGTM, OnIt, OneSecond, VRHeadset, YouAreTheBest, SALUTE
SHAKE, HIGHFIVE, UPPERLEFT, ThumbsDown, SLIGHT, TONGUE, EYESCLOSED, RoarForYou
CALF, BEAR, BULL, RAINBOWPUKE, ROSE, HEART, PARTY, LIPS
BEER, CAKE, GIFT, CUCUMBER, Drumstick, Pepper, CANDIEDHAWS, BubbleTea
Coffee, Yes, No, OKR, CheckMark, CrossMark, MinusOne, Hundred
AWESOMEN, Pin, Alarm, Loudspeaker, Trophy, Fire, BOMB, Music
XmasTree, Snowman, XmasHat, FIREWORKS, 2022, REDPACKET, FORTUNE, LUCK
FIRECRACKER, StickyRiceBalls, HEARTBROKEN, POOP, StatusFlashOfInspiration, 18X, CLEAVER, Soccer
Basketball, GeneralDoNotDisturb, Status_PrivateMessage, GeneralInMeetingBusy, StatusReading, StatusInFlight, GeneralBusinessTrip, GeneralWorkFromHome
StatusEnjoyLife, GeneralTravellingCar, StatusBus, GeneralSun, GeneralMoonRest, MoonRabbit, Mooncake, JubilantRabbit
TV, Movie, Pumpkin, BeamingFace, Delighted, ColdSweat, FullMoonFace, Partying
GoGoGo, ThanksFace, SaluteFace, Shrug, ClownFace, HappyDragon
VC_CanNotSee, VC_NoSound, VC_LooksGood, VC_SoundsClear
```

<a id="9-位会议号处理"></a>
## Handling a 9-Digit Meeting Number

If the user provides a 9-digit meeting number and requests sending an in-meeting message:

1. First execute `+meeting-list-active` using the current identity.
2. In the returned results, match that 9-digit meeting number by `meeting_no`.
3. After matching a unique meeting, take the long numeric `meeting_id`.
4. Execute `+meeting-message-send` using the same identity that discovered the meeting.

Do not automatically join the meeting when matching fails. Only when the user explicitly requests "have the app bot join the meeting/observe/attend on behalf" should you switch to `+meeting-join`.

<a id="权限和前置条件"></a>
## Permissions and Prerequisites

- User identity: the current user must be in that meeting.
- App identity: the app bot must be in that meeting.
- The meeting needs the in-meeting agent/Agent capability switch enabled.
- The `vc:meeting.message:write` permission is required; for app identity, the app must also be installed and the data scope configured.

When there is an app identity permission error, do not guide the user to repeatedly `auth login`. Handle it according to the main skill's "App Identity Permission Configuration Check".

<a id="相关场景"></a>
## Related Scenarios
- [In-Meeting Events and In-Meeting Interaction](../scenes/live-meeting-interact.md)
- [App Bot Meeting Participation and In-Meeting Interaction](../scenes/live-meeting-attend.md)
