# Meetings

Owns video-meeting history, live interactions, AI Notes, and Minutes. Preserve the identity that discovered the source; default to explicit `--as user` unless the requested operation is an application/bot workflow. If a downstream command cannot use that identity, explain the limitation rather than silently switching.

## Object relationships

| Object | Identifier | Relationship |
|---|---|---|
| Calendar event | `event_id` | May schedule/link a meeting; its `meeting_note` is a manually attached document |
| Video meeting | `meeting_id` | Actual meeting; may have Note, Minutes, both, or neither |
| AI Note | `note_id` | AI summary artifact set; transcript routing depends on `note_display_type` |
| Minutes | `minute_token` | Recording/upload artifact, possibly independent of a meeting |
| Document | doc token | Content carrier, not a meeting or Note ID |

Keep identifiers as strings. `meeting_id` is a long numeric ID, not the nine-digit `meeting_no` passed as `--meeting-number`. Minutes tokens usually come from `/minutes/<token>`. Never infer one artifact ID from another.

Note can link `note_doc_token`, `shared_doc_tokens`, and (for `normal`) `verbatim_doc_token`. For `unified`, use `note +transcript`; no separate transcript-document link exists. Minutes may contain summary, todos, chapters, keywords, transcript, and original audio/video. Missing Note does not imply missing Minutes.

## Current meeting content

```sh
lark-cli vc +meeting-list-active --as user
lark-cli vc +meeting-events --as user --meeting-id <meeting_id> --page-all --format pretty
```

When one active meeting is returned, use it directly. Disambiguate multiple meetings. An explicitly selected bot workflow uses `vc +meeting-list-active --as bot --user-id <open_id>`, then preserves bot identity. Bot results only include meetings where both that user and the bot participate; an empty result does not prove the user is not in a meeting.

## Scenario routing

Read only the scenario matching the task; open command references when exact fields, constraints, or error handling are missing.

- [Find meetings and artifacts](scenes/query-meeting-and-artifacts.md): history, participants, recordings, summaries/reviews, or event/meeting IDs.
- [Find Minutes artifacts](scenes/query-minutes-and-artifacts.md): Minutes URL/token or search by title/owner/participant.
- [Create/edit Minutes and permissions](scenes/create-and-edit-minutes.md): local recordings, title/content/speaker edits, access requests, collaborators.
- [Find Note artifacts](scenes/query-note-and-artifacts.md): Note ID, Note document link, transcripts, and shared documents.
- [Bot participation](scenes/live-meeting-attend.md): discover/start/join/invite/end/leave a meeting as the bot.
- [Live content and interaction](scenes/live-meeting-interact.md): read events/screenshots or send authorized messages/reactions/countdowns without implicitly joining/leaving.

A read or summary request does not authorize joining as a bot, ending a meeting, sending messages, requesting access, or creating documents/tasks. If a scenario already supplies the exact command, do not also fetch its help unless the contract is incomplete or inconsistent with actual CLI behavior.

For `vc meeting get`, `minutes minutes get`, and `minutes +word-replace`, use exact command help when needed; detailed shortcut references are below.

## Operation references

Read only the reference matching the current operation.

- [index](../shared/index.md)
- [vc search](references/lark-vc-search.md)
- [vc detail](references/lark-vc-detail.md)
- [vc recording](references/lark-vc-recording.md)
- [vc meeting list active](references/lark-vc-meeting-list-active.md)
- [vc meeting events](references/lark-vc-meeting-events.md)
- [vc meeting message send](references/lark-vc-meeting-message-send.md)
- [vc meeting screenshot](references/lark-vc-meeting-screenshot.md)
- [vc meeting countdown](references/lark-vc-meeting-countdown.md)
- [vc agent meeting join](references/lark-vc-agent-meeting-join.md)
- [vc agent meeting invite](references/lark-vc-agent-meeting-invite.md)
- [vc agent meeting end](references/lark-vc-agent-meeting-end.md)
- [vc agent meeting leave](references/lark-vc-agent-meeting-leave.md)
- [minutes search](references/lark-minutes-search.md)
- [minutes detail](references/lark-minutes-detail.md)
- [minutes download](references/lark-minutes-download.md)
- [minutes upload](references/lark-minutes-upload.md)
- [minutes update](references/lark-minutes-update.md)
- [minutes speaker replace](references/lark-minutes-speaker-replace.md)
- [minutes summary](references/lark-minutes-summary.md)
- [minutes todo](references/lark-minutes-todo.md)
- [minutes apply permission](references/lark-minutes-apply-permission.md)
- [drive member list](../drive/references/lark-drive-member-list.md)
- [drive member add](../drive/references/lark-drive-member-add.md)
- [note detail](references/lark-note-detail.md)
- [note transcript](references/lark-note-transcript.md)
