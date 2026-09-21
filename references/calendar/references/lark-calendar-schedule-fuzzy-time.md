<a id="模糊时间--无时间信息分支suggestion--批量查询"></a>
# Fuzzy time / no time information branch: suggestion + batch query

> This document handles scenarios with **fuzzy time** (such as "tomorrow afternoon" or "find a time next week") or **completely no time information**. The core action is to call `+suggestion` to produce candidate time blocks, then decide subsequent steps based on whether a meeting room is needed.

<a id="前置条件"></a>
## Prerequisites

Before entering this branch, the scheduler ([schedule-meeting.md](./lark-calendar-schedule-meeting.md)) has completed:
- Task type determination (create / edit)
- Edit flow: target event_id has been located
- Create flow: default values have been filled in
- Time has been determined to be **fuzzy** or **no time information**

<a id="流程"></a>
## Flow

<a id="1-调用-suggestion"></a>
### 1. Call suggestion

See [`lark-calendar-suggestion.md`](./lark-calendar-suggestion.md) for details.

```bash
lark-cli calendar +suggestion \
  --start "<range_start>" \
  --end "<range_end>" \
  --attendee-ids "<ids>" \
  --duration-minutes <n> \
  --event-rrule "<rrule>"
```

Rules:
- When the user provides no time information at all, first default to a reasonable range (such as "the remaining time today" or "the next two days") before calling
- In the edit flow, if the user says "change it to tomorrow afternoon" or "find a time next week to reschedule", call based on the user's desired **new time range**; do not reuse the old time
- **Do not ask "when would you like to schedule it" when the user has given no time at all** — first fill in a reasonable range, then enter suggestion

<a id="2-分支处理"></a>
### 2. Branch handling

<a id="不需要会议室"></a>
#### No meeting room needed

After obtaining multiple recommended time blocks, directly show the candidate times to the user; after the user confirms, proceed to the finalization operation.

<a id="需要会议室"></a>
#### Meeting room needed

After obtaining candidate time blocks, **do not rush to have the user select only a time**. First pass these time blocks all at once to `+room-find` to batch query available meeting rooms, then present the [candidate times] and the [corresponding list of available meeting rooms] in a structured format, so the user can complete the selection in one go.

> **Note**: Even if the user initially only says "check meeting rooms" without a time, the suggestion → room-find path must still be enforced.

See [`lark-calendar-room-find.md`](./lark-calendar-room-find.md) for details.

<a id="3-用户确认后"></a>
### 3. After user confirmation

- After the user selects a time block returned by `+suggestion`, **there is no need to call `+freebusy` again**; proceed directly to the finalization operation
- **BLOCKING REQUIREMENT**: You must first show the options to the user and wait for confirmation; it is forbidden to directly create/update a calendar event without user confirmation

<a id="模糊语义消解与长期记忆"></a>
## Fuzzy semantics disambiguation and long-term memory

For time scenarios with ambiguity, subjective assumptions are strictly forbidden. Typical examples:
- "after work starts" / "before work ends"
- 12-hour clock times without a clear AM/PM

Handling rules:
- Proactively clarify the true intent; do not guess on your own
- After the user clarifies, persist the personalized definition as a long-term preference

<a id="用户展示格式"></a>
## User presentation format

When showing multiple time blocks and corresponding meeting rooms to the user, **structured line-by-line formatting is required**; it is strictly forbidden to put the time and meeting room on the same line:

```text
## 2026-03-27 Friday

[Option 1] 14:00 - 15:00 (all attendees free)
  Available meeting rooms:
  1. Xueqing Jiachuang Building Block B-F2-02🎦(7 people)
  2. Xueqing Jiachuang Building Block B-F2-05🎦(10 people)

[Option 2] 16:00 - 17:00 (all attendees free)
  Available meeting rooms:
  1. Xueqing Jiachuang Building Block B-F3-01🎦(6 people)
  2. Xueqing Jiachuang Building Block B-F3-06🎦(8 people)

💡 Please reply with the option number you prefer and the corresponding meeting room number, and I will complete the booking for you.
```

<a id="落地"></a>
## Finalization

Based on the task type:
- Create → [`+create`](./lark-calendar-create.md)
- Edit → [`+update`](./lark-calendar-update.md)

For finalization rules, see [schedule-meeting.md § Finalizing calendar changes](./lark-calendar-schedule-meeting.md#落地日程变更).
