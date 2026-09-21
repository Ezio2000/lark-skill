# calendar +room-find


Find/search available meeting rooms for one or more time blocks. A meeting room is a resource-type attendee of a calendar event and cannot be booked separately from a calendar event.

<a id="适用场景"></a>
## Applicable Scenarios

- One or more candidate time blocks are known, and available meeting rooms need to be found
- Available rooms need to be searched in bulk across a set of consecutively numbered meeting rooms (e.g., "help me book a meeting room between No. 16 and No. 20")

<a id="命令"></a>
## Command

```bash
lark-cli calendar +room-find \
  --slot "2026-03-27T14:00:00+08:00~2026-03-27T15:00:00+08:00" \
  --slot "2026-03-27T16:00:00+08:00~2026-03-27T17:00:00+08:00" \
  --attendee-ids "ou_xxx,ou_yyy" \
  --city "北京" \
  --building "学清嘉创大厦B座" \
  --floor "F2" \
  --event-rrule "FREQ=DAILY;INTERVAL=1"
```

<a id="批量会议室名称查询"></a>
### Batch Meeting Room Name Query

When the user wants to pick an available room from a set of numbered meeting rooms, multiple meeting room names can be joined with English commas and passed to `--room-name`:

```bash
# Scenario: help me book a meeting room between No. 16 and No. 20
lark-cli calendar +room-find \
  --slot "2026-03-27T14:00:00+08:00~2026-03-27T15:00:00+08:00" \
  --room-name "16,17,18,19,20"
```

```bash
# Scenario: find the Jupiter or Mars meeting room
lark-cli calendar +room-find \
  --slot "2026-03-27T14:00:00+08:00~2026-03-27T15:00:00+08:00" \
  --room-name "木星,火星"
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--slot <start~end>` | Yes | The desired time block to query, in the format defined by `开始时间~结束时间`. If there are multiple candidate time blocks, this parameter can be passed repeatedly. |
| `--city <text>` | No | Hard constraint on the city where the meeting room is located. Extract **only when** the user explicitly states a specific city (e.g., Beijing, Shanghai); **never** infer or fill it in based on a campus or building name. |
| `--building <text>` | No | Hard constraint on the building where the meeting room is located; carries the office area/campus/building description below the city and above the floor.|
| `--floor <text>` | No | Used only to filter the floor where the meeting room is located. Normalize first, then pass the canonical value; for example, `2楼` / `二楼` / `2F` are unified as `F2`. Note: this parameter only filters floors and must not be mixed with area positioning (e.g., "Zone A") or a specific meeting room number. |
| `--room-name <text>` | No | Constraint on meeting room names; supports passing multiple names separated by **English commas**. Use only when the user explicitly mentions a meeting room proper name, meeting room number, or number range. |
| `--min-capacity <n>` | No | Minimum meeting room capacity. When the user explicitly states the number of attendees or makes a request such as "seat at least N people", extract the number into this parameter; it must be a positive integer. |
| `--max-capacity <n>` | No | Maximum meeting room capacity. Used to filter out spaces that are too large; must be a positive integer. |
| `--attendee-ids <id_list>` | No | List of attendee IDs. Supports user IDs (`ou_` prefix) and group IDs (`oc_` prefix), with multiple IDs separated by commas. **Do not pass the bot's open_id**: the bot is a virtual identity, does not occupy a meeting room seat, and has no meeting room preferences; passing it in only interferes with recommendation results. |
| `--event-rrule <rrule>` | No | Recurrence rule for a recurring calendar event; for how to set the rule, refer to rfc5545. **【⚠️Note: COUNT is absolutely not supported by the system; if the number of recurrences needs to be limited, it must be converted to UNTIL】**. Example value: "FREQ=DAILY;INTERVAL=1" |
| `--timezone <tz>` | No | The time zone used by the calendar event being booked as explicitly mentioned in the conversation (defaults to the user's device time zone, e.g., `Asia/Shanghai`) |

<a id="规则"></a>
## Rules

- Before constructing `--attendee-ids`, first remove the bot attendee: the bot does not occupy a seat and has no preferences, so it should not participate in meeting room recommendations.
- Multiple `--slot` are called concurrently by the CLI internally against the single-time-block API, then aggregated into one output
- The time input for `+room-find` must be a **definite time block**, not a time range search.
- If it is a recurring calendar event, you must verify whether the `reserve_until_time` in the response (the latest bookable time for that meeting room) covers the recurrence range corresponding to `event-rrule`.
- `--city` is extracted only when the user explicitly states a city; do not automatically fill in a city based only on location names such as `望京办公室`, `漕河泾园区`, or `南山办公室`.
- If `--city` has already been extracted, do not carry the city prefix again in `--building`. For example, when the user says `北京学清嘉创大厦B座`, it should be extracted as `--city "北京"` and `--building "学清嘉创大厦B座"`; do not pass `北京学清嘉创大厦B座` as-is in its entirety into `--building`.
- Keep only one canonical value per semantic slot. For example, when the user says "2nd floor", it should be converted to `--floor "F2"`; it is **forbidden** to also pass duplicate floor information such as `2楼 F2`.
- The parameter classification order should be: `city/building/floor` > `floor + room-name` compound expression > `room-name`. If a short term looks more like a floor/area locator (e.g., `2L`, `2F`), prefer assigning it to `--floor` rather than defaulting to `--room-name`. Expressions like `学清2层` are usually split into `--building "学清"` and `--floor "F2"`.
- Perform lightweight normalization on meeting room names: `木星会议室` should be extracted as `--room-name "木星"`; `会议室 02` / `02会议室` should be extracted as `--room-name "02"`.
- When the user says "help me book a meeting room between No. XX and No. YY" or mentions multiple meeting room names at once, all target names should be joined with English commas and passed to `--room-name`. For example:
  - "help me book a meeting room from No. 16 to No. 20" → `--room-name "16,17,18,19,20"`
  - "check whether Jupiter and Mars are free" → `--room-name "木星,火星"`
  - "take a look at meeting rooms 01, 02, 03" → `--room-name "01,02,03"`
- For compound meeting room numbers, prioritize splitting out structured information: for expressions such as `F3-05` / `F5-07` / `3楼-08`, if the floor and meeting room number can be reliably identified, prefer extracting them as `--floor "F3"` + `--room-name "05"`, `--floor "F5"` + `--room-name "07"`, `--floor "F3"` + `--room-name "08"`, rather than passing the whole string directly as `--room-name`.
- When meeting room search filter conditions are provided, the returned results are also **not guaranteed** to match the search terms exactly and literally. The underlying system may make recommendations based on nearby floors; for example, if the user searches for `2层`, even if `2层` has no available meeting rooms, nearby `3层` candidates may still be returned. This should not be misjudged as an API return anomaly.

<a id="输出格式"></a>
## Output Format

**Organize the returned candidate meeting rooms into an easy-to-read structured layout for display to the user. It is strictly forbidden to display the time and meeting room names on the same line; available meeting rooms must be presented on separate lines using a numbered list, and it is strictly forbidden to mash them into a single blob of plain text.**

```text
## 2026-03-27 Friday

[Option 1] 14:00 - 15:00
  Available meeting rooms:
  1. Xueqing Jiachuang Building B-F2-02🎦(7 people)
  2. Xueqing Jiachuang Building B-F3-05🎦(11 people)

💡 Please reply with the option number you prefer and the corresponding meeting room number, and I will complete the booking for you.
```

> **AI Behavior Guidance:**
> - **Display time blocks and meeting rooms in a structured way**: By default, display them in a hierarchical structure of "time block -> meeting room candidates", and directly ask the user for their preference.
> - **`room_name` must be passed through verbatim**: The meeting room names shown to the user must directly use the original `room_name` value returned by the CLI/API. It is forbidden to extract the floor, meeting room number, capacity, or video capability and reassemble them into a new name, and forbidden to paraphrase, abbreviate, remove prefixes, remove suffixes, or keep only a "readable" summary name.
> - **For recurring calendar events, clearly state the blocking reason and automatically shorten**: If a candidate meeting room's `reserve_until_time` cannot cover the recurring calendar event, you **must** clearly explain to the user the latest time until which that meeting room can be booked. If the user confirms that they want to continue using that meeting room, you must **automatically shorten the recurrence rule end time** of the calendar event to that `reserve_until_time` to prevent the meeting room booking from failing. You cannot continue directly with the original rule.
> - **Correctly interpret recommendation results**: If the returned results do not exactly and literally match the user's input conditions, first explain that the underlying system may return recommended candidates from nearby locations or with similar conditions; do not directly judge it as an anomaly.
> - **Reduce the user's input cost by default**: Proactively guide the user that they do not need to provide very detailed meeting room search conditions from the start. As long as the time block is clear, the user can simply say they "want to book a meeting room", and you should first query candidates based on the current information; only when the user is dissatisfied with the results should you guide them to add more specific building, floor, meeting room name, or capacity conditions.

**Field Descriptions:**

| Field Name | Description |
| :--- | :--- |
| `room_id` | Unique identifier of the meeting room, used to add it as a meeting room attendee when creating a calendar event later. |
| `room_name` | Meeting room name; the original value must be used when displaying it to the user. |
| `capacity` | Maximum capacity of the meeting room. |
| `reserve_until_time` | The latest time point until which the meeting room can currently be booked, used to verify whether a recurring calendar event exceeds the limit. |

<a id="参考"></a>
## References

- [lark-calendar-create](lark-calendar-create.md)
- [lark-calendar-suggestion](lark-calendar-suggestion.md)
- [lark-calendar](../index.md) — skill entry point and routing
