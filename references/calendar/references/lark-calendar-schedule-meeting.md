<a id="预约改约日程或会议查询搜索可用会议室的工作流"></a>
# Workflow for scheduling/rescheduling a calendar event or meeting, and querying/searching for available meeting rooms

<a id="执行摘要"></a>
## Executive Summary

- **The first step is always to determine the task type: create a new calendar event, or edit an existing one.**
- **When editing an existing calendar event, you must first locate the `event_id` of the target calendar event or instance.**
- **By default, act as an intelligent assistant, not a form-filling machine.** Fill in defaults that can be inferred from context directly, and only ask questions in scenarios involving conflicts that require a decision or that cannot be uniquely determined.
- **The create flow fills in defaults first; the edit flow inherits information from the located calendar event first.**
- **Clear time** → go to [Clear Time branch](./lark-calendar-schedule-clear-time.md)
- **Vague time or no time information** → go to [Vague Time branch](./lark-calendar-schedule-fuzzy-time.md)
- **BLOCKING REQUIREMENT**: When faced with a choice of time options or meeting room options, you must first present the options to the user and wait for confirmation; creating/updating a calendar event directly without confirmation is prohibited.
- **Must be executed in order.** Do not skip the prerequisite steps of "task type determination", "target calendar event location (edit flow)", "filling in defaults/inheriting baseline information", and "determining time clarity".

<a id="严禁行为"></a>
## Strictly Prohibited Actions

- **It is strictly prohibited to call a command directly without first reading the corresponding subcommand documentation.**
- **It is strictly prohibited to go directly into creating a calendar event or searching for meeting rooms before determining whether this is a "create" or an "edit".**
- **It is strictly prohibited to treat a request with an existing calendar event anchor + a modification verb as creating a new calendar event.**
- **It is strictly prohibited to skip the target location step when editing an existing calendar event.** Before obtaining a unique `event_id`, you must not call `+update`.
- **It is strictly prohibited to create/update a calendar event without user confirmation when faced with a choice of time/meeting room options.**

<a id="适用场景"></a>
## Applicable Scenarios

- "Help me schedule a meeting" / "Find a time to meet with XX next week"
- "Help me book/find/search for an available meeting room"
- "Schedule a calendar event for tomorrow at 3 PM"
- "Add Xiao Ming to tomorrow morning's calendar event"
- "Change the meeting room for next Monday's weekly meeting"
- "Move this calendar event to tomorrow afternoon, and add Xueqing F201"

<a id="核心概念"></a>
## Core Concepts

- **A meeting room is a type of attendee (attendee / resource) of a calendar event, and cannot be booked separately from the calendar event.**
- **To book or find a meeting room, the time block must be determined first.**
- **When the user says "check meeting rooms" or "find a meeting room", the default intent is to check meeting room availability, not to search the meeting room resource directory.**

<a id="任务类型判定"></a>
## Task Type Determination

| Type | Typical Language Signals | First Action |
|------|--------------|----------|
| Create new calendar event | "schedule a meeting" "arrange a meeting" "create a new calendar event" "book a meeting room for a meeting" | Fill in defaults, then proceed to time determination |
| Edit existing calendar event | "add/remove people to/from a calendar event" "move a calendar event to…" "change meeting room" | First locate the target `event_id` |

Rules:
- As long as both an **existing calendar event anchor** (title, time range, `这个日程`, `这场会`) and a **modification verb** (add, remove, move to, change) appear, it is by default determined to be an edit.
- For edits to recurring calendar events, you must first locate the `event_id` of the corresponding instance.

<a id="编辑流先定位目标日程"></a>
## Edit Flow: First Locate the Target Calendar Event

Location rules:
- Prioritize using anchors given by the user, such as title, date, and time range, to narrow the scope through `+agenda`, `+search-event`, or the instance view
- When multiple candidate calendar events match, you must present the candidates to the user and require confirmation
- For recurring calendar events, you must continue locating the `event_id` of that instance

Edit flow branch routing:

| Edit Sub-scenario | Next Step |
|-----------|--------|
| Only add/remove ordinary attendees/groups, do not change time, do not involve meeting rooms | Directly `+update` (see [lark-calendar-update.md](./lark-calendar-update.md) for details) |
| Add a meeting room, do not change time | Based on the located calendar event start/end → [Clear Time branch](./lark-calendar-schedule-clear-time.md) |
| Only change time, do not involve meeting rooms | Determine time clarity → corresponding branch |
| Both change time and add/change meeting rooms | First determine the final time → then check meeting rooms → finalize |

<a id="新建日程智能推断默认值"></a>
## Create New Calendar Event: Intelligently Infer Defaults

- **Title**: Automatically generate based on context; if it cannot be inferred, default to "Meeting"
- **Attendees**: If not specified, default to only the user themselves
- **Duration**: Infer based on context; default to 30 minutes
- **No time information**: By default, infer a reasonable range (such as "today" or "the past two days"), enter the time recommendation flow, and do not ask the user

When searching for attendees returns multiple results that cannot be uniquely determined, you must ask the user and record it in long-term memory.

<a id="判断时间是否明确"></a>
## Determine Whether the Time Is Clear

Time baseline rules:
- **Create flow**: Use the time given by the user, or the time range filled in by default
- **Edit flow without changing time**: The current `start/end` of the located calendar event is the clear time
- **Edit flow with time change**: The new time the user wants to change to; if the expression is vague, enter the vague time branch
**Note**: When performing the task of modifying the time of a calendar event/meeting, you must first obtain the duration of the original calendar event. If the user only provides a new start time, you must automatically calculate the new end time based on the original duration, strictly keeping the original duration unchanged; changing the duration of the original calendar event without authorization is prohibited.

<a id="分支路由"></a>
## Branch Routing

| Determination Result | Next Read |
|----------|-----------|
| Clear time | [schedule-clear-time.md](./lark-calendar-schedule-clear-time.md) |
| Vague time / no time information | [schedule-fuzzy-time.md](./lark-calendar-schedule-fuzzy-time.md) |

<a id="落地日程变更"></a>
## Finalize Calendar Event Changes

After user confirmation, call:
- Create → [`+create`](./lark-calendar-create.md)
- Edit → [`+update`](./lark-calendar-update.md)

```bash
lark-cli calendar +create \
  --summary "..." \
  --start "<start>" \
  --end "<end>" \
  --attendee-ids "ou_xxx,oc_xxx,omm_xxx"

lark-cli calendar +update \
  --event-id "<event_id>" \
  --start "<start>" \
  --end "<end>" \
  --add-attendee-ids "omm_new_room"
```

Finalization rules:
- The edit flow must always continue using the target `event_id` located earlier; it is prohibited to re-guess the target calendar event in the final step
- In the edit flow, "add meeting room" by default only appends `room_id`, and does not remove existing meeting rooms
- Only when the user explicitly says "change meeting room" should you both `--remove-attendee-ids` the old one + `--add-attendee-ids` the new one
- When a meeting room is needed, write the selected `room_id` into the attendee list

<a id="参考"></a>
## References

- [lark-calendar-schedule-clear-time.md](./lark-calendar-schedule-clear-time.md)
- [lark-calendar-schedule-fuzzy-time.md](./lark-calendar-schedule-fuzzy-time.md)
- [lark-calendar-room-find.md](./lark-calendar-room-find.md)
- [lark-calendar-suggestion.md](./lark-calendar-suggestion.md)
- [lark-calendar-create.md](./lark-calendar-create.md)
- [lark-calendar-update.md](./lark-calendar-update.md)
- [index.md](../index.md)
