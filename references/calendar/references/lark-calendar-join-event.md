# calendar +join-event

Join a calendar event using a **share token**.

<a id="命令"></a>
## Command

```bash
# User joins as themselves (default scenario)
lark-cli calendar +join-event --token <token> --as user

# Join as the app
lark-cli calendar +join-event --token <token> --as bot
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--token <token>` | **Yes** | Share token, the only input for joining (alias `--share-token`). |

<a id="token-从哪来"></a>
## Where the token comes from

| Token type | Source | How to obtain |
|-----------|---------|------|
| Link type | Share link / QR code | The `token` in the link `{{domain}}/calendar/share?token=<token>` |
| Card type | Share card / RSVP card | The calendar share token parsed from an IM calendar share card or RSVP card message |

- **Share link**: directly take the `token` value from the URL query and pass it in; no need to parse calendar fields. For example, `{{domain}}/calendar/share?token=29f762bdmsbd82ce9` → `--token 29f762bdmsbd82ce9`.
- **QR code**: first use OCR/scanning to parse it into a share link, then take the `token` from it—the CLI does not handle QR code images, only the parsed link token.
- **Card**: the token is in the card message content (share card `SHARE_CALENDAR_EVENT`, RSVP card `GENERAL_CALENDER`); after an RSVP card is forwarded it degrades into a share card, and can likewise be joined.

<a id="重复性日程"></a>
## Recurring events

The join scope depends on whether the event body reverse-resolved from the token is the "original recurring event" or an "exception" (see the key concepts in [lark-calendar-recurring](lark-calendar-recurring.md)):

- If what is shared is the **original recurring event** (`{event_uid}_0`): you join the **entire series** (including exceptions).
- If what is shared is an **exception** (a single instance of `originalTime > 0`): you join only this **one exception event**.

<a id="参考"></a>
## References

- [lark-calendar](../index.md) -- skill entry point and routing
- [lark-calendar-rsvp](lark-calendar-rsvp.md) -- reply accept/decline/tentative when already in the event (≠ join)
- [lark-calendar-recurring](lark-calendar-recurring.md) -- conventions for series vs instance operations on recurring events
