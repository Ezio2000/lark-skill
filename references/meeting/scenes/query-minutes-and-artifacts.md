<a id="查询妙记及其产物"></a>
# Query Minutes and Their Artifacts

Execute queries around the target Minutes: first obtain the unique `minute_token`, then query basic information, AI artifacts, transcripts, raw media, or associated smart meeting notes according to the user's goal. When meeting context or `meeting_id` is already available, first obtain `minute_token` from the meeting chain; do not search for Minutes again.

<a id="定位妙记"></a>
## Locate Minutes

- When `minute_token` is already available, use it directly.
- The last path segment of a Minutes URL is `minute_token`; remove query parameters.
- When there is no token, search by title/keyword, owner, participant, or time range:

  ```bash
  lark-cli minutes +search --query <query> --start <start> --end <end> --as user
  ```

- `minutes +search` supports user identity and app identity. Use user identity by default; use `--as bot` only when the user explicitly requests the app perspective or the context is already app identity.
- `me` applies only to user identity; app identity has no "current user" and must pass an explicit `ou_` open_id. Token or scope issues with app identity cannot be fixed via `auth login`.
- "Minutes I participated in" defaults to the union of two queries: "I own" and "I am a participant". For specific filter semantics, see [`lark-minutes-search`](../references/lark-minutes-search.md).
- Paginate based on `has_more` and `page_token`. When the user has not explicitly requested the full set, confirm whether to continue once cumulative results exceed 50 and there are still more results; when the user explicitly requests "all, every, statistics, sort", directly fetch all pages, deduplicate by `token` in the results, then return or compute statistics.
- When there are multiple candidates, display title, time, owner, URL, and token, and let the user choose; do not pick on your own.

When only search results are needed, stop after returning the matches.

Once `minute_token` is searched or resolved using a certain identity, all subsequent Minutes details, artifact reads, media downloads, permission requests, and associated Note / Doc queries must explicitly use the same `--as`. Do not rely on the profile default identity, and do not switch identities to bypass resource permissions.

<a id="查询基础信息"></a>
## Query Basic Information

When the user only wants the title, duration, cover, owner, or URL, use the basic information command:

```bash
lark-cli minutes minutes get --params '{"minute_token":"<minute_token>"}' --as <source_identity>
```

When basic information already satisfies the goal, do not continue reading AI artifacts or transcripts. When command parameters are insufficient, run `lark-cli minutes minutes get --help`.

<a id="获取-ai-产物和逐字稿"></a>
## Obtain AI Artifacts and Transcripts

Use `minutes +detail`, passing only the artifact flags the user needs:

```bash
lark-cli minutes +detail --minute-tokens <minute_token> --summary --todo --chapter --keyword --transcript --as <source_identity>
```

- Optional `--summary`, `--todo`, `--chapter`, `--keyword`, `--transcript`.
- Not passing artifact flags returns only basic information and any top-level `note_id`.
- When the user only wants ready-made summaries, to-dos, or chapters, return the corresponding AI artifacts.
- When the user requests extraction, re-summarization, analysis, or review, read only the Transcript and independently analyze based on the original speech; copying `--summary` is prohibited.

For artifact flags, return fields, and local output, see [`lark-minutes-detail`](../references/lark-minutes-detail.md).

<a id="下载原始音视频"></a>
## Download Raw Audio and Video

When the user needs the raw media file or download link, use `minutes +download`. Download artifacts for the same Minutes are consolidated under `./minutes/<minute_token>/`, unless the user specifies another safe relative path.

For media types, paths, link validity periods, and permissions, see [`lark-minutes-download`](../references/lark-minutes-download.md).

<a id="获取关联的智能纪要"></a>
## Obtain Associated Smart Meeting Notes

Read `note_id` from the top level of `minutes +detail`, and directly execute `note +detail`:

```bash
lark-cli note +detail --note-id <note_id> --as <source_identity>
```

- Do not treat `minute_token` as `note_id`, and do not go back to VC.
- If there is no `note_id` at the top level, it means the Minutes has no associated Note; stop here.
- After obtaining `note_doc_token`, `verbatim_doc_token`, or `shared_doc_tokens`, continue according to the rules for smart meeting notes and Docs.

<a id="处理无权限结果"></a>
## Handle No-Permission Results

When there is no view permission, explain that authorization from the Minutes owner is required; do not automatically execute `minutes +apply-permission`. Only when the user explicitly requests to apply for view or edit permission, enter the edit Minutes scenario to initiate a request, and use the same identity that triggered the no-permission error. For details, see [`lark-minutes-apply-permission`](../references/lark-minutes-apply-permission.md).
