# Calendar

Use explicit user identity for the user's calendar, bot identity for an explicitly selected bot-owned workflow. Event owner/attendee fields do not determine the caller. "You" addressed to the assistant alone is not a request to use bot identity.

## Select the operation

- Scheduling, rescheduling, time changes, or room searches: read [scheduling](references/lark-calendar-schedule-meeting.md).
- Only title/description changes or attendee changes: locate the existing event and read [update](references/lark-calendar-update.md). A request to change an existing event does not authorize creating a replacement.
- Recurring-event updates/deletion: read [recurrence](references/lark-calendar-recurring.md), then use `--apply-to=single|all|this-and-following`. Ask only if that scope is missing. Instances and exceptions have distinct IDs; whole-series operations must account for exceptions.
- Current or past meetings versus scheduled events: read [meeting relationships](references/lark-calendar-meeting-relation.md). Future meetings are calendar events.
- Ordinary todos go to [Tasks](../task/index.md).

## Direct reads

```sh
lark-cli calendar +agenda --as user
lark-cli calendar +get --calendar-id primary --event-id <event_id> --as user
lark-cli calendar +search-event --query "<keyword>" --start <date> --end <date> --as user
```

`primary` means the current identity's primary calendar. Agenda defaults to today, filters canceled events, and splits ranges over 40 days. Present events by date/start time. Search returns basic fields, not full detail. `--attendee-ids` uses OR within the same ID type; two user IDs do not mean both must attend. Search defaults to 30 results per page.

`+get` does not include attendees/rooms: use [list-attendees](references/lark-calendar-list-attendees.md), with `--type resource` for rooms. `description` is Markdown for both reads and writes. [Meeting](references/lark-calendar-meeting.md) resolves an event's historical `meeting_id` and manually attached `meeting_note`; obtain the video join link from `+get`.

## Availability and rooms

`+freebusy --type busy|raw_busy|free|common_free` reports occupancy. `raw_busy` preserves individual events and RSVP; the other modes merge intervals. `free` and `common_free` accept `--min-duration 30m`. Bot calls require explicit `--user-id`.

For recommended meeting times use [suggestion](references/lark-calendar-suggestion.md), which also considers work/rest periods. [Room-find](references/lark-calendar-room-find.md) needs definite time blocks; for an unspecified time, obtain suggestions first. Rooms are resource attendees, not independent reservations. Adding a room preserves existing rooms unless replacement/removal was requested.

## Time and links

- Compute relative dates/time conversions with a tool and explicit timezone, not the host default. Weeks start Monday. A named day covers the whole day.
- Do not schedule wholly past events; an event spanning the present is permitted. Preserve the CLI's inclusive all-day end-date semantics.
- Event share links come from `calendar events share_info --calendar-id <id> --event-id <id>`. Do not fabricate an applink. Video join links are different; recurring instances share the same video join link.
- Organizer transfer uses the current organizer's identity; read [transfer](references/lark-calendar-transfer.md) and use the authorized confirmation flag.
- Use successful write output for feedback. Read again only when required by the task or when that output leaves the outcome unclear.
- User/group name resolution uses user identity through [Contacts](../contact/index.md) or [Messaging](../im/index.md). Do not infer ID types from names.

## Operation references

Read only the reference matching the current operation.

- [calendar create](references/lark-calendar-create.md)
- [calendar rsvp](references/lark-calendar-rsvp.md)
- [calendar join event](references/lark-calendar-join-event.md)
- [index](../meeting/index.md)
- [vc detail](../meeting/references/lark-vc-detail.md)
- [note detail](../meeting/references/lark-note-detail.md)
- [minutes detail](../meeting/references/lark-minutes-detail.md)
