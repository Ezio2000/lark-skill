# drive reactions


Handle reactions (likes, emojis, per-emoji counts, who reacted with what, adding/removing emojis) on document comments / replies. This scenario is uncommon, but the rules are fairly concentrated: when querying, only include `--need-reaction` on `drive +list-comments` / `+batch-query-comments` / `+list-replies` when the user explicitly needs reaction information; for writes, prefer `drive +react-reply` (see [`lark-drive-react-reply.md`](lark-drive-react-reply.md) for command parameter details), and the operation target is always `reply_id`. This document is a cross-cutting topic that consolidates the query rules, semantic associations, and complete enumeration for reactions.

> [!IMPORTANT]
> **`reaction_type` can only use the enum values defined in the "Complete `reaction_type` List" below.**
> Do not fill in values freely, do not improvise based on natural language, and do not rewrite the mixed-case values in the list into any other casing. When writing, you may only select and pass values exactly as they appear in the enumeration below.

<a id="何时使用"></a>
## When to Use

- The user explicitly asks to view reactions (emojis) on a comment / reply.
- The user wants to count which emojis are on a comment card, the count of each emoji, or see who reacted with what.
- The user wants to add / remove a reaction on a comment or reply.

<a id="查询规则"></a>
## Query Rules

- `drive +list-comments`, `drive +batch-query-comments`, and `drive +list-replies` all support `--need-reaction`.
- Only include `--need-reaction` when the user explicitly needs reaction information; if the user only cares about comment body, reply body, comment count / reply count, do not include it by default.
- To iterate over comment cards and fetch reactions along the way: use `drive +list-comments --need-reaction`.
- When the comment ID is known, to view reactions in bulk: use `drive +batch-query-comments --need-reaction`.
- To continue paginating and pull reply reactions under a comment card: use `drive +list-replies --need-reaction`, and keep including it on every page.
- Return shape: `items[].reactions[]` is `{reaction_key, count, ahead_users[]}`; **entries in `count=0` are remnants of deleted reactions, so both counting and determining existence must filter by `count>0`**.

<a id="查询示例"></a>
## Query Examples

```bash
# Iterate over comment cards and fetch reactions along with them
lark-cli drive +list-comments --url '<DOC_URL>' --need-reaction

# Given a comment_id, query comment card reactions in bulk
lark-cli drive +batch-query-comments --url '<DOC_URL>' --comment-ids '<COMMENT_ID>' --need-reaction

# Continue paginating replies under a comment card and fetch reactions along with them
lark-cli drive +list-replies --url '<DOC_URL>' --comment-id '<COMMENT_ID>' --need-reaction
```

<a id="写入规则"></a>
## Write Rules

- For adding / removing reactions, prefer `drive +react-reply`; for command parameters, target location, and dry-run, see [`lark-drive-react-reply.md`](lark-drive-react-reply.md).
- The operation target is `reply_id` (the `items[].reply_id` from `drive +list-replies`), not `comment_id`.
- If the user says to add / remove a reaction on "this comment", take the `reply_id` of the comment card's root reply (the first page's `items[0]`) and then operate.
- add / delete are idempotent: repeatedly adding an existing reaction or deleting a nonexistent reaction both return success with no side effects; delete only removes reactions added by the current identity itself.
- **The server does not validate `reaction_type`: any string will be accepted and persisted as a corrupted reaction**; `+react-reply --emoji` performs local validation against the platform enumeration as a fallback, and when calling the native command directly you must ensure the value is valid yourself.
- The native `drive file.comment.reply.reactions update_reaction` is only used as a fallback when you need fields not exposed by the shortcut; `--params` takes `file_token`/`file_type`, and `--data` passes `action=add|delete`, `reply_id`, `reaction_type`.

<a id="写入示例"></a>
## Write Examples

```bash
# Add a like reaction to a reply
lark-cli drive +react-reply --url '<DOC_URL>' \
  --reply-id '<REPLY_ID>' --emoji THUMBSUP --action add

# Remove an existing DONE reaction on a reply (wiki URL is automatically unwrapped)
lark-cli drive +react-reply --url '<WIKI_URL>' \
  --reply-id '<REPLY_ID>' --emoji DONE --action delete

# Native command fallback (note: the native path has no local enum validation)
lark-cli drive file.comment.reply.reactions update_reaction \
  --params '{"file_token":"<DOC_TOKEN>","file_type":"docx"}' \
  --data '{"action":"add","reply_id":"<REPLY_ID>","reaction_type":"THUMBSUP"}'
```

> [!CAUTION]
> `update_reaction` is a write operation. You must confirm the user's intent before executing; do not react with an emoji on the user's behalf by default.

<a id="reaction_type-使用规则"></a>
## `reaction_type` Usage Rules

- `reaction_type` must be passed the platform-defined enum string, and it is case-sensitive; `drive +react-reply`'s `--emoji` performs local validation (the native command does not validate, and neither does the server).
- Do not arbitrarily change mixed-case values to all uppercase; for example, `Yes`, `No`, `Get`, `EatingFood`, `CheckMark`, and `CrossMark` must all be passed as their original values.
- **Do not invent `reaction_type` outside the list, and do not fabricate natural-language descriptions into new enums undefined by the platform**.
- If the user provides natural-language semantics (such as "like", "in progress", "confirm"), you may choose the closest existing value from the enumeration list below; if it is an approximate mapping, you should clearly inform the user when executing.

<a id="常见语义联想"></a>
## Common Semantic Associations

- `Yes`: confirm / agree / approve.
- `No`: reject / disagree / deny.
- `DONE`: completed / handled.
- `Typing`: typing / in progress / following up (approximate semantics).
- `OK`: OK / received / confirm.
- `THUMBSUP`: like / approve.
- `LGTM`: looks fine / can continue.

<a id="完整-reaction_type-列表"></a>
## Complete `reaction_type` List

The following enumeration is maintained according to the current Drive comment reaction guidance; keep it as-is when using:

```text
ANGRY, APPLAUSE, ATTENTION, AWESOME, BEAR, BEER, BETRAYED, BIGKISS
BLACKFACE, BLUBBER, BLUSH, BOMB, CAKE, CHUCKLE, CLAP, CLEAVER
COMFORT, CRAZY, CRY, CUCUMBER, DETERGENT, DIZZY, DONE, DONNOTGO
DROOL, DROWSY, DULL, DULLSTARE, EATING, EMBARRASSED, ENOUGH, ERROR
EYESCLOSED, FACEPALM, FINGERHEART, FISTBUMP, FOLLOWME, FROWN, GIFT, GLANCE
GOODJOB, HAMMER, HAUGHTY, HEADSET, HEART, HEARTBROKEN, HIGHFIVE, HUG
HUSKY, INNOCENTSMILE, JIAYI, JOYFUL, KISS, LAUGH, LIPS, LOL
LOOKDOWN, LOVE, MONEY, MUSCLE, NOSEPICK, OBSESSED, OK, PARTY
PETRIFIED, POOP, PRAISE, PROUD, PUKE, RAINBOWPUKE, ROSE, SALUTE
SCOWL, SHAKE, SHHH, SHOCKED, SHOWOFF, SHY, SICK, SILENT
SKULL, SLAP, SLEEP, SLIGHT, SMART, SMILE, SMIRK, SMOOCH
SMUG, SOB, SPEECHLESS, SPITBLOOD, STRIVE, SWEAT, TEARS, TEASE
TERROR, THANKS, THINKING, THUMBSUP, TOASTED, TONGUE, TRICK, UPPERLEFT
WAIL, WAVE, WELLDONE, WHAT, WHIMPER, WINK, WITTY, WOW
WRONGED, XBLUSH, YAWN, YEAH, FIREWORKS, BULL, CALF, AWESOMEN
2021, CANDIEDHAWS, REDPACKET, FORTUNE, LUCK, FIRECRACKER, Yes, No
Get, LGTM, Lemon, EatingFood, Hundred, MinusOne, ThumbsDown, Fire
OKR, Drumstick, BubbleTea, Loudspeaker, Pin, Coffee, Alarm, Trophy
Music, Typing, Pepper, CheckMark, CrossMark
```

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for cloud space (cloud drive/cloud storage)
- [lark-drive-react-reply](lark-drive-react-reply.md) -- `+react-reply` command parameters
- [lark-shared](../../shared/index.md) -- authentication and global parameters
