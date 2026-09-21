<a id="明确时间分支room-find--freebusy--冲突处理"></a>
# Explicit-time branch: room-find + freebusy + conflict handling

> This document handles scenarios where the **time is already explicit**. Sources of "explicit time": direct user expression (e.g., "tomorrow at 3 PM"), the original start/end of an already-located event in the edit flow, or a suggestion time block confirmed by the user.

<a id="前置条件"></a>
## Prerequisites

Before entering this branch, the scheduler ([schedule-meeting.md](./lark-calendar-schedule-meeting.md)) has completed:
- Task type determination (create / edit)
- Edit flow: the target event_id has been located
- Create flow: defaults have been filled in
- The time has been determined to be **explicit**

<a id="流程"></a>
## Flow

<a id="1-查询会议室如需"></a>
### 1. Query meeting rooms (if needed)

If the user needs a meeting room, first call `+room-find`. See [`lark-calendar-room-find.md`](./lark-calendar-room-find.md).

```bash
lark-cli calendar +room-find \
  --slot "<start>~<end>" \
  --attendee-ids "<ids>" \
  --city "<city>" \
  --building "<building>" \
  --floor "<F2>" \
  --room-name "<room_name>"
```

Time block determination rules:
- **Edit flow without changing the time, only adding a meeting room**: `--slot` must come from the current `start/end` of the already-located event
- **Edit flow changing both the time and adding a meeting room**: `--slot` must come from the candidate new time, not the old time

See [`lark-calendar-room-find.md`](./lark-calendar-room-find.md).

<a id="2-查询忙闲"></a>
### 2. Query free/busy

```bash
# Single-person / multi-person free/busy query: --user-id can be repeated or comma-separated; the server has already merged adjacent/overlapping busy intervals
lark-cli calendar +freebusy --start "<start>" --end "<end>" --user-id "ou_a,ou_b"

# Directly find common free time (recommended for "find a time when several people are all free")
lark-cli calendar +freebusy --start "<start>" --end "<end>" \
  --user-id "ou_a,ou_b,ou_c" --type common_free --min-duration 30m
```

Rules:
- Participants include a **bot**: no need to query free/busy for the bot. A bot is a virtual identity that can attend multiple meetings in parallel and has no free/busy semantics; checking it is meaningless.
- Too many participants (more than 5 people): only query the free/busy of the **current user** and a few core people
- Participants include a **group**: no need to expand group members to query free/busy
- If the user entered this branch after confirming a time block from `+suggestion`, **there is no need to call `+freebusy` again**
- Finding common free time for multiple people: directly use `--type common_free [--min-duration <dur>]` and let the CLI compute the common free time in one pass; do not merge and intersect on your own

<a id="3-冲突处理"></a>
### 3. Conflict handling

- **No conflict**: directly let the user choose a meeting room (if needed), then proceed to the execution operation
- **Conflict**: you must first explain the conflict situation and ask the user:
  - **Continue with the current time** → let the user choose a meeting room (if needed), then proceed to the execution operation
  - **Change the time** → switch to the [fuzzy-time branch](./lark-calendar-schedule-fuzzy-time.md)

<a id="落地"></a>
## Execution

Depending on the task type:
- Create → [`+create`](./lark-calendar-create.md)
- Edit → [`+update`](./lark-calendar-update.md)

For execution rules, see [schedule-meeting.md § Executing schedule changes](./lark-calendar-schedule-meeting.md#落地日程变更).
