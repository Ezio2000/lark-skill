<a id="查询会议及其产物"></a>
# Query meetings and their artifacts

Perform queries around a target meeting: first obtain the unique `meeting_id`, then query participants, AI Notes, Minutes, or recordings according to the user's goal. When a `note_id` or `minute_token` is already available, start directly from the corresponding artifact; do not go back to meeting search.

<a id="定位会议"></a>
## Locate the meeting

Before deciding on batch commands and batch size, you must normalize all input identifiers:

- Exactly 9 pure digits is a `meeting_no`, even if the user calls it a "meeting ID".
- `meeting_no` must first be converted one by one via `vc +search --query` into the `id` in the search results.
- `vc +search` does not support batch meeting numbers; multiple `meeting_no` are resolved one by one in input order, or a script can be used for batch conversion.

Prefer reusing existing identifiers; do not search repeatedly:

| Existing information | Action |
|---|---|
| `meeting_id` | Directly query the meeting or related artifacts |
| `meeting_no` / 9-digit meeting number | Use `vc +search --query "<meeting_no>" --format json --as <source_identity>` to search for the meeting, and obtain the `meeting_id` from the `id` in the results |
| Calendar `event_id` | Use `calendar +meeting` to obtain the `meeting_id` and the user-bound `meeting_note` |
| `note_id` | Go directly to the [AI Note scenario](query-note-and-artifacts.md) |
| `minute_token` / Minutes URL | Go directly to the [Minutes scenario](query-minutes-and-artifacts.md); for the URL, take the last path segment and remove query parameters |

When there is no identifier, use `vc +search` to search for meetings that have already ended:

```bash
lark-cli vc +search --query <query> --start <start> --end <end> --format json --as <source_identity>
```

- Provide at least one condition among keywords, time range, organizer, participants, or meeting room; do not treat action words such as "summarize", "review", or "all meetings" as a `--query`.
- "What meetings are there today" requires merging two parts: `vc +search` queries meetings that have ended today, and lark-calendar queries schedules that are in progress or have not yet started.
- When there is only a natural-language note title and no meeting clues such as meeting ID, time, or participants, switch to Drive/Doc search for the note document; do not treat the note title as a meeting keyword.
- Paginate according to `has_more` and `page_token`. When full retrieval is not explicitly required, after the cumulative results exceed 50, first confirm whether to continue; when the user explicitly requests "all, statistics, sorting", retrieve all results directly.
- When there are multiple candidates, display the topic, time, organizer, and `meeting_id` and let the user choose; do not arbitrarily choose the most recent one.

When you only need to find the meeting, return the unique `meeting_id` and stop.

For search parameters, date semantics, and pagination details, see [`lark-vc-search`](../references/lark-vc-search.md).

<a id="选择查询身份"></a>
## Choose the query identity

- `vc +search`, `vc +detail`, `vc +recording`, `vc meeting get`, and `note +detail` all support user or app identity. When there is no existing identity context, use user identity by default; when the user explicitly requests the app perspective or the current flow already uses app identity, use `--as bot`.
- When a `meeting_id`, `note_id`, or `minute_token` already exists, continue using the identity from which it came; subsequent Minutes, Note, Doc, and Drive commands must all explicitly pass the same `--as`. Do not switch identity on your own to query participants or to bypass permission errors.
- `note +transcript` supports only user identity. When app identity finds a unified Note, first explain the limitation, and switch identity only after the user explicitly agrees.

<a id="获取参会人"></a>
## Get participants

When querying "who attended, when they joined or left, whether a certain person attended", read the meeting's participant snapshot:

```bash
lark-cli vc meeting get --params '{"meeting_id":"<meeting_id>","with_participants":true}' --as <source_identity>
```

This is a server-side snapshot; it does not require the app bot to join the meeting, and it can also be queried after the meeting ends. Do not use in-meeting events as a substitute for the complete participant snapshot.

<a id="获取会议产物标识"></a>
## Get meeting artifact identifiers

Use `vc +detail` to obtain the meeting's associated `note_id` and `minute_token`:

```bash
lark-cli vc +detail --meeting-ids <meeting_id> --as <source_identity>
```

Note and Minutes come from mutually independent AI summary and recording pipelines, and may exist at the same time, only one may exist, or neither may exist:

- When the user explicitly specifies "AI Note" or "Minutes", follow the specified pipeline; do not divert.
- When only one type of artifact exists, use the one that exists; do not treat the missing Note or Minutes as an error because of default priority.
- When both exist and the user has not specified, prefer Note. Note and its transcript are usually directly readable by participants after the meeting; Minutes contains the original audio and video and is controlled by an independent resource ACL, often requiring owner authorization or an explicit permission request by the user.
- AI artifacts such as summaries and to-dos from Note and Minutes may overlap in content. Choose one primary pipeline according to the above rules; unless the user explicitly requests a comparison, do not automatically concatenate, merge, or deduplicate the two AI artifacts.
- When the user only wants artifact identifiers, return the obtained `note_id` / `minute_token` and stop; when artifact links are needed, enter the corresponding downstream scenario to resolve them, and do not continue reading the body.
- `meeting_note` is a Doc bound by the user on a Calendar event and can only be obtained from `event_id` via `calendar +meeting`; it is independent of AI Notes, and must not be inferred from `meeting_id` or `note_id`.
- When the user asks "what notes are there" or "note links" and the context contains `event_id`, keep the `meeting_note` returned by `calendar +meeting`; if `note_id` exists, enter the AI Note scenario to obtain the `note_doc_token`, then return both so the user can distinguish and choose.

For meeting detail fields, see [`lark-vc-detail`](../references/lark-vc-detail.md).

<a id="转交智能纪要场景"></a>
## Hand off to the AI Note scenario

After obtaining the `note_id`, enter [Query AI Notes and related artifacts based on note_id](query-note-and-artifacts.md), and pass the `note_id` and the `source_identity` used to obtain that ID. `note +detail`, body and cover reading, `note_display_type` transcript routing, shared documents, and Doc metadata queries are all governed by that scenario and are not redefined in this scenario.

<a id="转交妙记场景"></a>
## Hand off to the Minutes scenario

After obtaining the `minute_token`, enter [Query Minutes and their artifacts](query-minutes-and-artifacts.md), and pass the `minute_token` and the `source_identity` used to obtain that Token. Minutes basic information, AI artifacts, Transcript, media download, related Note, and resource permission handling are all governed by that scenario and are not redefined in this scenario.

If you need to additionally query recordings from `meeting_id` or Calendar `event_id`, first obtain the `minute_token` according to [`vc +recording`](../references/lark-vc-recording.md), then switch to the Minutes scenario.

<a id="基于会议内容回答或分析"></a>
## Answer or analyze based on meeting content

- When the user only wants ready-made AI summaries, to-dos, or chapters, directly return the corresponding AI artifacts from the selected pipeline, and do not additionally read the transcript for this. To-dos usually include the proposer or owner, and chapters are organized by topic, so these structured AI artifacts should be preferred when viewing to-dos or meeting structure.
- When the user requests extraction, re-summarization, review, dispute analysis, or "who said what", read the original dialogue from the Note transcript or Minutes Transcript and analyze it independently; it is forbidden to repackage ready-made AI summaries and pass them off as independent conclusions.
- When both Note and Minutes have original records and the user has not specified, prefer the Note transcript; when the user explicitly says "based on Minutes", use the Minutes Transcript.
- If the artifact does not exist or there is no permission, state this truthfully, and retain the already obtained `meeting_id`, `note_id`, `minute_token`, or document token so the user can continue processing.
