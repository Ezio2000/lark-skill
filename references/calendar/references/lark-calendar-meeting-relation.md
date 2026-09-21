<a id="日程与视频会议的关系"></a>
# Relationship Between Calendar Events and Video Meetings

When users say "meeting", they do not distinguish between "calendar events" and "video meetings"; in reality, these are two different types of entities. This document defines the relationship between the two and provides execution flows for the three query intents: "current / future / past".

<a id="核心概念"></a>
## Core Concepts

- **Calendar Event**: A reservation of a period of time for the user; when the time arrives, it may involve a video meeting, or it may simply be an offline meeting / personal time block.
- **VC Meeting**: An actual call that took place; `meeting_id` only exists after it is actually initiated.

| Scenario | `event_id` | `meeting_id` | Notes |
|------|:---:|:---:|------|
| Calendar event initiated a video meeting | ✓ | ✓ | One calendar event can initiate multiple calls, producing multiple `meeting_id` |
| Calendar event did not start a video meeting | ✓ | ✗ | Offline meeting / personal time block |
| Instant video meeting | ✗ | ✓ | No calendar event binding |

**Key invariant**: Video meetings only occur in the **present and past**; there is no such thing as a "future video meeting".

<a id="意图-1查询当前正在开的会议"></a>
## Intent 1: Query Meetings Currently in Progress

**Target coverage**: All activities the user may care about at the current point in time—video meetings currently in progress + calendar events at the current time (regardless of whether a video meeting was started).

**Execution steps**:

```bash
# 1. Calendar events at the current time
lark-cli calendar +agenda --start <now> --end <now>

# 2. Video meetings the user has joined
lark-cli vc +meeting-list-active --as user

# 3. For each calendar event in step 1, look up the associated meeting_id
#    The output is an event_id → meeting_id mapping; all subsequent cross-referencing is matched by meeting_id
#    (The id field in the results of vc +meeting-list-active / vc +detail is the meeting_id, with no event_id)
lark-cli calendar +meeting --event-ids <event_id1>,<event_id2>

# 4. Determine whether the video meeting is still in progress
#    Only for calls where "the meeting_id from step 3 is non-empty and not in step 2"
#    end_time is empty or <= start_time → still in progress; otherwise it has ended
lark-cli vc +detail --meeting-ids <meeting_id1>,<meeting_id2>
```

**Grouped result presentation**: Categorize in the following **four-group order**, with each group as its own section; empty groups may be omitted.

1. **Meetings the current user is participating in** (`meeting_id` matched in step 2)
   - **Instant meetings** (no associated `event_id`): Display only video meeting information.
   - **Calendar meetings** (can be associated with a `event_id` from step 3): Display calendar event information + video meeting information.
2. **Calendar events currently in a video meeting (user not joined)**: The calendar event has a `meeting_id`, step 4 determines it is still in progress, but it is not in step 2. Display calendar event information + video meeting information.
3. **Calendar events currently in progress (video meeting has ended)**: The calendar event is still within its time window and has a `meeting_id`, but step 4 determines it has ended. Display calendar event information + video meeting information (marked "ended").
4. **Calendar events currently in progress (no video meeting started)**: The calendar event is still within its time window, and step 3's lookup found no `meeting_id`. Display only calendar event information.

<a id="意图-2查询未来的会议"></a>
## Intent 2: Query Future Meetings

**Only the calendar event perspective**: Video meetings only occur in the present and past; what the user calls "future meetings" is equivalent to "future calendar events".

```bash
# Choose one of two: no keywords → +agenda; with keywords → +search-event
lark-cli calendar +agenda --start <future_start> --end <future_end>
lark-cli calendar +search-event --query <keyword> --start <future_start> --end <future_end>

# Disabled: vc +search returns empty for the future, easily misjudged as "no meetings"
# lark-cli vc +search --start <future> --end <future>   ← Do not do this
```

If the user explicitly asks for "future video meetings", still return the calendar event list and **proactively explain**: whether the video meeting actually takes place can only be determined once the time arrives.

<a id="意图-3查询过去的会议"></a>
## Intent 3: Query Past Meetings

**Target coverage**: Video meetings that occurred in the past time period (including instant meetings) + calendar events in the past time period (including those without video meetings).

**Execution steps**:

```bash
# 1. Past video meetings (including instant meetings—querying only calendar events would miss them)
lark-cli vc +search --start <past_start> --end <past_end>

# 2. Past calendar events
lark-cli calendar +agenda --start <past_start> --end <past_end>

# 3. For each calendar event in step 2, look up meeting_id to build a meeting_id → event_id mapping
#    Iterate over each result in step 1, using its id field (i.e., meeting_id) to look up this mapping:
#    Match → calendar event video meeting; no match → instant meeting without a calendar event
lark-cli calendar +meeting --event-ids <event_id1>,<event_id2>
```

**Result grouping**: Present in the following three-group order.

1. **Instant video meetings without a calendar event**: No associated `event_id` found in step 1. Display only video meeting information.
2. **Calendar event video meetings**: Calendar event + associated `meeting_id`. Display both calendar event information and video meeting information.
3. **Calendar events without a video meeting**: The calendar event exists but step 3's lookup found no `meeting_id`. Display only calendar event information.

<a id="常见判断路径"></a>
## Common Decision Paths

| User input | Action |
|----------|------|
| Only a "meeting title" is given | It is uncertain whether it is a calendar event title or an instant meeting title; query **both** the `calendar +search-event --query <标题>` and the `vc +search --query <标题>` of [`lark-meeting`](../../meeting/index.md), then cross-reference and route according to the intents above |
| A `meeting_id` is given directly | Go directly to [`lark-meeting`](../../meeting/index.md), skipping calendar events |
| Relative anchor ("that meeting at 3 PM today") | First use `+agenda` to locate the calendar event, then determine by intent 1 or 3 |
| Past anchor ("the meeting held yesterday") | **Do not query only `+agenda`**—you must also query `vc +search`, otherwise instant meetings will be missed |
| Future anchor ("tomorrow afternoon's meeting") | Query only calendar events, do not query `vc +search` (the future always returns empty) |
