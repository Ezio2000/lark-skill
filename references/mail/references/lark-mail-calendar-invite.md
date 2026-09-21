<a id="发送日程邀请邮件"></a>
# Send a calendar invite email

Embed a calendar invite in an email (`text/calendar`); after receiving the email, recipients can directly accept or decline the calendar event. `To` / `Cc` recipients automatically become attendees (ATTENDEE), and the sender automatically becomes the organizer (ORGANIZER).

Applies to send-type shortcuts: `+send` / `+draft-create` / `+reply` / `+reply-all` / `+forward`.

<a id="命令示例"></a>
## Command example

```bash
# Send a new email with a calendar invite
lark-cli mail +send --as user \
  --to alice@example.com --cc bob@example.com \
  --subject '产品评审' \
  --body '<p>请参加本次产品评审会议。</p>' \
  --event-summary '产品评审' \
  --event-start '2026-05-10T14:00+08:00' \
  --event-end '2026-05-10T15:00+08:00' \
  --event-location '5F 大会议室' \
  --confirm-send
```

<a id="参数"></a>
## Parameters

- `--event-summary`: Calendar title. Setting this parameter enables calendar invite mode, and `--event-start` and `--event-end` must be set at the same time.
- `--event-start` / `--event-end`: Time in ISO 8601 format, such as `2026-05-10T14:00+08:00`.
- `--event-location`: Optional, calendar location.

<a id="约束"></a>
## Constraints

- `--event-summary`, `--event-start`, and `--event-end` must all be present or all be absent.
- `--event-*` and `--send-time` (scheduled sending) are mutually exclusive and cannot be used at the same time; calendar invites must be sent immediately, otherwise recipients may receive them only after the calendar event has already started.
- Cannot be used together with `--bcc`: Bcc recipients will not become calendar attendees, and this combination will cause sending to fail. To invite someone to a calendar event, use `--to` or `--cc`; if you only want to inform them without inviting them, send a separate email without a calendar invite.

<a id="读取日程邀请"></a>
## Read a calendar invite

When reading an email that contains a calendar invite, the `calendar_event` field contains the calendar details (`method`, `summary`, `start`, `end`, `organizer`, `attendees`, etc.). For details, see [lark-mail-message](lark-mail-message.md).
