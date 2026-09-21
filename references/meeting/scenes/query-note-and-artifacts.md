<a id="基于-note_id-查询智能纪要及关联产物"></a>
# Query AI Notes and related artifacts by note_id

- Identity: `note +detail` supports `--as user` / `--as bot`; `note +transcript` supports only `--as user`. If `note_id` was obtained under a certain identity (for example, `vc +detail --as bot`), `note +detail` and subsequent Doc and Drive commands must explicitly continue using the same `--as`.
- If `note +detail --as bot` returns `unified`, do not silently switch to `--as user` and continue. First explain to the user that the note's verbatim transcript can only be read under the user identity, and only retry with a switched identity if the user explicitly agrees.

<a id="从智能纪要-docx-查询关联链接"></a>
## Query related links from an AI Note Docx

When the user provides an AI Note Docx URL/token and only needs the note type or related artifact links, execute directly:

```bash
lark-cli docs +fetch --doc "<docx_url_or_token>" --doc-format markdown --as <source_identity>
```

From the returned structure, extract only:

- Input document: as the AI Note main document, return the original URL provided by the user.
- `<vc-transcribe-tab vc-node-id="...">`: can serve as an explicit `note_id`.
- The Docx URL marked as "transcript".
- `/minutes/` Minutes URL.
- The shared document token in `<cite type="doc" doc-id="..." file-type="...">`.

If no explicit `note_id` is obtained from `<vc-transcribe-tab>`, but a Minutes URL exists, extract `minute_token` from the last segment of the URL path, then query the Minutes basic information:

```bash
lark-cli minutes +detail --minute-tokens "<minute_token>" --as <source_identity>
```

Continue the Note query from the corresponding `note_id`; if that field is empty or not returned, continue handling it as a Doc. Do not pass the Doc token or `minute_token` directly to Note commands.

<a id="确认-note_id"></a>
## Confirm note_id

The Note domain accepts only an explicit `note_id`:

- The `note_id` provided directly by the user.
- The `note_id` returned by `vc +detail` from `meeting_id`.
- The top-level `note_id` returned by `minutes +detail` from `minute_token`.
- The `vc-node-id` in the `<vc-transcribe-tab vc-node-id="...">` returned by `docs +fetch`.

Do not infer `note_id` from a Doc token, Docx URL, document title, body, or backlink. When there is only a natural-language note title or Docx link, first use Drive/Doc search or read the document; when there is no explicit `vc-node-id`, continue handling it as a Doc and do not enter the Note query. If the document body explicitly provides a Docx link for "verbatim transcript" or "transcript", continue using that link as a Doc under the current identity; that link is still not `note_id`.

If currently there is only `meeting_id`, `minute_token`, or a Calendar `event_id`, first use the meeting, Minutes, or calendar scenario to obtain `note_id`; do not pass these identifiers directly to Note commands.

<a id="查询关联产物标识"></a>
## Query related artifact identifiers

```bash
lark-cli note +detail --note-id <note_id> --as <source_identity>
```

Keep the following fields and choose subsequent operations according to the user's goal:

| Field | Meaning | Subsequent operation |
|---|---|---|
| `note_id` | Note unique identifier | Subsequent Note commands continue to use this value |
| `note_display_type` | `normal` / `unified` / `unknown` | Determines the verbatim transcript entry point |
| `note_doc_token` | AI Note body | Hand off to Doc to read the body, or to Drive to query the name and URL |
| `verbatim_doc_token` | The independent verbatim transcript Doc for `normal` or some `unknown` Notes | Use only according to the display type rules below |
| `shared_doc_tokens` | List of documents shared during the meeting | Query metadata or body according to the user's goal |

When the user only needs related artifact identifiers, return the above available tokens and `note_display_type`, then stop; do not read the document body.

<a id="读取智能纪要正文"></a>
## Read the AI Note body

When the user needs the summary, to-dos, sections, or body in the AI Note, read `note_doc_token`:

```bash
lark-cli docs +fetch --doc <note_doc_token> --doc-format markdown --as <source_identity>
```

After reading the body, check the first `<whiteboard token="...">` in the returned Markdown. That board is the AI Note cover; when it exists, extract the token, download it under the same identity to `./notes/<note_id>/cover`, group it into the same Note directory as the verbatim transcript of `note +transcript`, and display it together with the body:

```bash
lark-cli docs +media-download --type whiteboard --token <whiteboard_token> --output ./notes/<note_id>/cover --as <source_identity>
```

When there is no `<whiteboard>`, skip directly and do not treat it as a failure. Only the first `<whiteboard>` is handled as the cover; do not automatically download other boards in the body.

When only the document name or URL is needed, do not read the body; use the Drive metadata interface:

```bash
lark-cli drive metas batch_query --data '{"request_docs":[{"doc_type":"docx","doc_token":"<note_doc_token>"}],"with_url":true}' --as <source_identity>
```

<a id="读取逐字稿文字记录"></a>
## Read the verbatim transcript (transcript)

The verbatim transcript entry point is determined by the `note_display_type` returned by `note +detail`; do not judge only by whether `verbatim_doc_token` is empty:

A normal Note verbatim transcript is a Doc read result, a unified Note can be saved by `note +transcript` as Markdown or plain text, and a Minutes Transcript is the Minutes artifact text. They can all serve as raw speech records, but the serialization format is not a unified contract; rely on the actual returned content and do not hard-code fixed line formats such as "speaker + relative timestamp".

<a id="note_display_type--normal-且-有-verbatim_doc_token"></a>
### note_display_type = normal and verbatim_doc_token exists

```bash
lark-cli docs +fetch --doc <verbatim_doc_token> --doc-format markdown --as <source_identity>
```

<a id="note_display_type--unknown-且-有-verbatim_doc_token"></a>
### note_display_type = unknown and verbatim_doc_token exists

```bash
lark-cli docs +fetch --doc <verbatim_doc_token> --doc-format markdown --as <source_identity>
```

<a id="note_display_type--unknown-且-无-verbatim_doc_token"></a>
### note_display_type = unknown and no verbatim_doc_token

Stop and explain that the verbatim transcript entry point cannot be determined; do not repeatedly retry or guess it as unified

### note_display_type = unified

```bash
lark-cli note +transcript --note-id <note_id> --as user
```

`note +transcript` automatically fetches the complete pagination and saves the file; when the target file already exists, add `--overwrite` only if the user explicitly requests overwriting.

<a id="查询会中共享文档"></a>
## Query documents shared during the meeting

`shared_doc_tokens` is the document shared during the meeting associated with this Note, not a verbatim transcript or `meeting_note`. Handle it according to the user's goal:

- Only document names or URLs: use `drive metas batch_query`, querying at most 10 tokens per batch.
- Body needed: use `docs +fetch --doc <shared_doc_token>` one by one.
- When there are multiple shared documents, first return the titles and URLs for the user to choose; only read them one by one when the user explicitly requests reading all.
- When a shared document does not exist or there is no permission, keep that token and report item by item; do not misreport the entire group of results as a failure.

<a id="基于纪要内容回答"></a>
## Answer based on note content

- When the user only wants the ready-made AI summary, to-dos, or sections, read the AI Note body and return the corresponding content.
- When the user requests extraction, re-summarization, retrospective, dispute analysis, or "who said what", read the raw verbatim transcript content according to the display type and analyze it independently; directly rewriting the AI Note as an independent conclusion is prohibited.
- When the user only wants links or a list of related artifacts, do not read the body or verbatim transcript.
- `meeting_note` is a document manually bound by the user on a Calendar event; it does not belong to the Note's `shared_doc_tokens` and cannot be queried through `note_id`.
