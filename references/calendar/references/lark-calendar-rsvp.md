# calendar +rsvp


Reply to the specified event, updating the current user's RSVP status (accept, decline, or tentative).

<a id="命令"></a>
## Command

```bash
# Reply to the event as accept (using the primary calendar)
lark-cli calendar +rsvp --event-id evt_xxx --rsvp-status accept

# Reply to the event as decline
lark-cli calendar +rsvp --event-id evt_xxx --rsvp-status decline

# Reply to the event as tentative
lark-cli calendar +rsvp --event-id evt_xxx --rsvp-status tentative

# Specify an event under another calendar
lark-cli calendar +rsvp --calendar-id cal_xxx --event-id evt_xxx --rsvp-status accept
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--event-id <id>` | **Yes** | Event ID |
| `--rsvp-status <status>` | **Yes** | Reply status, possible values: `accept` (accept), `decline` (decline), `tentative` (tentative) |
| `--calendar-id <id>` | No | Calendar ID (if omitted, the primary calendar is used) |
| `--dry-run` | No | Preview the API call without executing it |

<a id="提示"></a>
## Tips

- You can only reply to events you have been invited to.
- Before calling, you usually need to obtain the specific `event-id` through commands such as `+agenda`.

<a id="参考"></a>
## References

- [lark-calendar](../index.md) -- skill entry point and routing
