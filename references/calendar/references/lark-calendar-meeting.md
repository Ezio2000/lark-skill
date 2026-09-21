
# calendar +meeting

Get the associated video meeting information (`meeting_id`, `meeting_note`) via a calendar event ID (`event_id`). Read-only.

<a id="命令"></a>
## Command

```bash
# Single / batch (comma-separated, up to 50)
lark-cli calendar +meeting --event-ids <event_id1>,<event_id2>

# Uses the primary calendar by default; pass --calendar-id explicitly when needed
lark-cli calendar +meeting --event-ids <event_id> --calendar-id <calendar_id>
```

<a id="输出字段"></a>
## Output fields

| Field | Description |
|------|------|
| `event_id` | Calendar event ID |
| `meeting_id` | Associated video meeting ID |
| `meeting_note` | Token of the Minutes document that the user actively bound to the calendar event (`MeetingNotes`, manually added by the user on the calendar event page;). **It is a different document from the AI Note `note_doc_token` generated during the meeting**; to get the AI Note, continue through `vc +detail` → `note +detail`. |

<a id="下游链路"></a>
## Downstream chain

`calendar +meeting` only translates the calendar event ID into `meeting_id` / `meeting_note`. To get the artifacts generated during the meeting (AI Note, verbatim transcript, Minutes), you need to continue calling:

```bash
# 1. meeting_id → note_id + minute_token (two artifacts from the same meeting, each may be empty)
lark-cli vc +detail --meeting-ids <meeting_id>

# 2a. note_id → Minutes document token (note_doc_token / verbatim_doc_token / shared_doc_tokens)
lark-cli note +detail --note-id <note_id>

# 2b. minute_token → Minutes AI artifacts (fetched on demand; if not passed, no AI content is returned)
lark-cli minutes +detail --minute-tokens <minute_token> --summary --todo --chapter --keyword --transcript

# 3. Any document token (meeting_note / note_doc_token / verbatim_doc_token / shared_doc_token) → body
lark-cli docs +fetch --api-version v2 --doc <doc_token> --doc-format markdown
```
