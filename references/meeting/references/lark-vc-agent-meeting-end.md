# vc +meeting-end

End the meeting as the current Host app Bot.

```bash
lark-cli vc +meeting-end --as bot --meeting-id 7628568141510692381 --yes
lark-cli vc +meeting-end --as bot --meeting-id 7628568141510692381 --dry-run
```

For normal execution, `--yes` must be explicitly passed; `--dry-run` will not end the meeting.

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| `--meeting-id` | Yes | Long numeric Meeting ID, not the 9-digit meeting number. |

Only app identity is supported; call `POST /open-apis/vc/v1/bots/end`; only the current Host Bot can end an in-progress meeting.

Required app Scope: `vc:meeting.bot.manage:write`.

<a id="常见失败原因"></a>
## Common failure reasons

- The current app Bot is not in the meeting: first use the same app Bot to start or join the Calendar meeting, then execute the end.
- The app Bot is in the meeting but is not the current Host: transfer Host to that Bot, or have the current Host/Owner end the meeting.
- The meeting has not enabled the Agent meeting capability: confirm the meeting settings and the necessary gradual rollout switch for the meeting Owner.
