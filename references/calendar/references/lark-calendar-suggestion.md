# calendar +suggestion


Based on an unspecified time or a time range, recommend multiple available time block options. Help users solve the challenge of coordinating time.

**When to invoke (Agent Guidance):**
- ✅ **When the user's need involves finding a time block and the time is not fully determined** (such as `今天`, `近三天`, `本周`, `下午`, `无时间描述`), invoke this tool to obtain recommended time blocks for the user to choose from (including but not limited to scheduling events).
- ❌ **When the user has already specified a concrete time point** (such as `今天下午3点`), this tool is **not needed**

<a id="命令"></a>
## Command

```bash
# Get the default time recommendation options (search range: from the current moment to the end of the day)
lark-cli calendar +suggestion

# Get recommendation options within the specified time interval (supports date shorthand or full ISO 8601)
lark-cli calendar +suggestion \
  --start "2026-03-19" \
  --end "2026-03-20"

# Get recommendation options based on attendees and meeting duration (duration unit: minutes)
# --attendee-ids supports passing a mixed list of users (ou_ prefix) and groups (oc_ prefix)
lark-cli calendar +suggestion \
  --start "2026-03-19T14:00:00+08:00" \
  --end "2026-03-19T18:00:00+08:00" \
  --attendee-ids ou_xxx,oc_yyy \
  --duration-minutes 60

# Exclude specific time ranges
lark-cli calendar +suggestion \
  --start "2026-03-19T08:00:00+08:00" \
  --end "2026-03-19T18:00:00+08:00" \
  --exclude "2026-03-19T12:00:00+08:00~2026-03-19T13:00:00+08:00"

# Output in JSON format
lark-cli calendar +suggestion \
  --start "2026-03-19T08:00:00+08:00" \
  --end "2026-03-19T18:00:00+08:00" \
  --format json
```

<a id="参数"></a>
## Parameters

| Parameter                              | Required    | Description                                                                  |
| ------------------------------- | ----- | ------------------------------------------------------------------- |
| `--start <time>`                | No     | Search interval start time (supports date/ISO 8601 and other formats, defaults to **current time**)                                |
| `--end <time>`                  | No     | Search interval end time (defaults to the same day as `--start`, automatically takes the end of that day)                                                     |
| `--attendee-ids <id_list>`     | No     | List of target attendee IDs. Extract the IDs of the corresponding entities. Supports users (`ou_` prefix) and groups (`oc_` prefix). Separate multiple IDs with English commas. **Do not pass the bot's open_id**: the bot is a virtual identity, can run multiple meetings in parallel, and has no busy/free semantics; passing it will interfere with the busy/free calculation for recommended time slots. |
| `--event-rrule <rrule>`         | No     | Recurrence rule for recurring events; for how to set the rule, refer to rfc5545. **[⚠️Note: the system absolutely does not support COUNT; if you need to limit the number of recurrences, you must convert it to UNTIL]**. Example value: "FREQ=DAILY;INTERVAL=1"                                              |
| `--duration-minutes <min>`      | No     | Meeting duration (minutes). Prefer the value explicitly specified by the user; if not specified, try to infer from context; if inference fails, do not pass it                                        |
| `--timezone <tz>`               | No     | The time zone used for the scheduled event explicitly mentioned in the conversation (defaults to the user's device time zone, for example `Asia/Shanghai`)                                |
| `--exclude <times>`             | No     | Excluded time blocks, supports the `start~end` format (such as `2026-03-19T12:00:00+08:00~2026-03-19T13:00:00+08:00`), separate multiple with commas |
| `--format <flag>`               | No     | Output format (fixed as `json`) |
| `--dry-run`                     | No     | Preview the API call without executing it                                                       |

<a id="时间格式"></a>
## Time Format

`--start`, `--end`, and `--exclude` support automatic parsing of the following formats:

| Format            | Example                          | Description                   |
| ------------- | --------------------------- | -------------------- |
| ISO 8601      | `2026-03-19T08:40:29+08:00` | Full format, precisely including date, time, and time zone offset with colon |
| Date + time       | `2026-03-19 08:40:29`       | Time zone automatically completed               |
| Date only          | `2026-03-19`                | start takes 00:00:00, end takes 23:59:59 |
| Unix timestamp     | `1741564800`                | Second-level timestamp               |

<a id="输出格式"></a>
## Output Format

**Organize the recommendation results into an easy-to-read list of options, and attach polished recommendation reasons:**

```text
## 2026-03-19 Thursday

- **Option 1: 10:00 - 10:30**
  Recommendation reason: All participants are free.

```
> **AI behavior guidance:**
> - **Present options and reasons in a structured way**: Present the recommended time options in a clear list, and directly ask the user for their preference. You **must** explain the advantages of each time block by combining the "user's original request" with the "recommendation reason"; the wording must be concise, direct, and unambiguous.
> - **Faithfully report conflicts**: Note that the returned recommendation options are not necessarily all completely free (even if the user explicitly asks to find free time, when it is difficult to satisfy, the system will still return options that include busy/free conflicts). To determine whether a recommendation option is completely free, you can judge from whether the recommendation reason expresses "completely free" or "no busy/free conflicts at all." If a recommendation option has busy/free conflicts, you **must** truthfully explain the conflict situation to the user when presenting the option, and must never mislead the user into thinking it is completely free.
> - **Proactively provide optimization suggestions**: When any of the following conditions is met (1. the returned result contains the content of the `ai_action_guidance` field; 2. the user asks to find a free time, but none of the recommendation options are completely free), you **must** proactively provide optimization suggestions. If the `ai_action_guidance` field exists, generate guidance wording strictly based on its core intent; otherwise, proactively provide reasonable alternatives based on the actual conflict situation (such as: suggest adjusting the time range, meeting duration, or attendees).

<a id="典型场景"></a>
## Typical Scenarios

<a id="1-查找多人的共同空闲会议时间"></a>
### 1. Find a common free meeting time for multiple people

```bash
# Specify two attendees and require finding a 45-minute free time slot
lark-cli calendar +suggestion \
  --start "2026-03-19T08:00:00+08:00" \
  --end "2026-03-19T18:00:00+08:00" \
  --attendee-ids ou_member_a,ou_member_b \
  --duration-minutes 45
```

<a id="2-用户对当前推荐不满意要求换一批"></a>
### 2. The user is dissatisfied with the current recommendations and asks to "show another batch"

```bash
# Pass the previously recommended time slots as exclusion conditions
lark-cli calendar +suggestion \
  --start "2026-03-19T08:00:00+08:00" \
  --end "2026-03-19T18:00:00+08:00" \
  --exclude "2026-03-19T10:00:00+08:00~2026-03-19T10:30:00+08:00"
```

<a id="与其他命令对比"></a>
## Comparison with Other Commands

| Command                     | Purpose       | Output Content                |
| ---------------------- | -------- | ------------------- |
| `calendar +suggestion` | Based on an unspecified time or a time range, recommend multiple available time block options | Returns multiple recommended time slots and their reasons, as well as follow-up suggestions |
| `calendar +freebusy`   | Query busy/free time slots   | Returns only the list of busy time slots and rsvp status (no event details)    |

**Selection advice**:

- **Looking for available time (including scenarios such as meetings)** → Prefer `+suggestion` to directly obtain intelligent recommendation options
- **Understanding an individual's current busy situation** → Use `+freebusy`

<a id="参考"></a>
## References

- [lark-calendar-create](lark-calendar-create.md) — Create an event
- [lark-calendar](../index.md) — Skill entry point and routing
