# Meeting summary

Read [Meetings](../meeting/index.md) for object relationships and artifact routing. Use user identity throughout. Read [authentication](../shared/index.md) only for an actual auth/scope failure; request only the domains needed by the selected path.

## Find meetings

Use the requested date range in the user's timezone; if none is given, state the assumption of the past seven days. Resolve relative dates with reliable date arithmetic. "This week" starts Monday; "last week" is the preceding Monday through Sunday.

```sh
lark-cli vc +search --start "<YYYY-MM-DD>" --end "<YYYY-MM-DD>" --format json --page-size 30 --as user
```

The end date is inclusive. Split ranges longer than one month, follow pagination, and deduplicate meeting IDs. Pages hold at most 30 results.

## Retrieve relevant artifacts

```sh
lark-cli vc +detail --meeting-ids "<id1,id2>" --as user
lark-cli note +detail --note-id "<note_id>" --as user
```

Batch meeting details in groups of at most 50. A missing `note_id` does not mean no meeting content: use `minute_token` when present. If both are absent, report that no linked artifact was returned.

- `normal` Note transcripts are documents addressed by `verbatim_doc_token`.
- `unified` Note transcripts are not standalone documents: use `note +transcript --note-id <note_id>`; do not fabricate a transcript document link.
- With Minutes but no Note, use `minutes +detail --minute-tokens <token> --transcript --output-dir ./transcripts --as user`. The output directory must be relative. Read downloaded content to derive findings; an AI-generated summary is not a substitute for the transcript when independent analysis is requested.
- Permission error `2091005` is not "no content." Report it. Requesting access contacts the owner and requires authorization; the command uses singular `--minute-token`. Retry only after approval.

For document URLs, inspect `lark-cli schema drive.metas.batch_query`, then query at most ten `docx` tokens per call with `with_url: true`. Use only actual `note_doc_token` and normal `verbatim_doc_token` values.

Metadata and links alone cannot support a substantive content summary. Fetch the selected document or transcript, distinguish inaccessible/missing content, and ground decisions/action items in what was read.

## Deliver

Match the requested output: a meeting/link inventory needs metadata; decisions, themes, and action items need content. Include dates, meeting names, source links, and access gaps as useful. Create or append to a [document](../doc/index.md) only if requested. Do not automatically create tasks or send messages.

## Conditional references

- [Meeting discovery and artifacts](../meeting/scenes/query-meeting-and-artifacts.md)
- [Minutes artifacts](../meeting/scenes/query-minutes-and-artifacts.md)
- [Note artifacts](../meeting/scenes/query-note-and-artifacts.md)
- [Search](../meeting/references/lark-vc-search.md), [details](../meeting/references/lark-vc-detail.md), [Note details](../meeting/references/lark-note-detail.md), [Note transcript](../meeting/references/lark-note-transcript.md), [Minutes details](../meeting/references/lark-minutes-detail.md), [access request](../meeting/references/lark-minutes-apply-permission.md)
