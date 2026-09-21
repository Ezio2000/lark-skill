# calendar +list-attendees

List the attendees of a single event (users / meeting rooms / groups / third-party email addresses). Read-only.

<a id="命令"></a>
## Command

```bash
# View all types of attendees and meeting rooms for an event under the specified calendar (defaults to primary)
lark-cli calendar +list-attendees --calendar-id <calendar_id> --event-id <event_id>

# View only meeting rooms
lark-cli calendar +list-attendees --event-id <event_id> --type resource

# View both users and meeting rooms
lark-cli calendar +list-attendees --event-id <event_id> --type user --type resource

# Paginated continuation (the caller decides whether to call again based on has_more / page_token)
lark-cli calendar +list-attendees --event-id <event_id> --page-size 100 --page-token <page_token>
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--event-id <id>` | **Yes** | Target event ID |
| `--calendar-id <id>` | No | Calendar ID; if omitted, the primary calendar is used (`primary`) |
| `--type <type>` | No | Filter by attendee type; can be repeated or comma-separated. Enum: `user` / `resource` / `chat` / `third_party`. Leave empty to return all types |
| `--page-size <n>` | No | Upstream page size; defaults to `20` |
| `--page-token <token>` | No | Upstream pagination cursor, from the `page_token` returned last time |

<a id="提示"></a>
## Tips

- Group attendees of `type=chat` **do not return `rsvp_status`** (a group itself has no group-level RSVP status). For RSVP of group members, use the native OpenAPI.
