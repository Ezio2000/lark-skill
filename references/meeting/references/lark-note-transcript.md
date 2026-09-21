# note +transcript

Use only when `note +detail` has confirmed `note_display_type=unified`. A regular Minutes transcript is a separate Docx document; go back to [lark-doc](../../doc/index.md) to read `verbatim_doc_token`.

`note +transcript` supports only `--as user`, not `--as bot`. If `note +detail --as bot` returns `unified`, do not silently omit `--as` or switch to the user identity to continue; first explain this limitation, and only retry with a switched identity after the user explicitly agrees.

```bash
lark-cli note +transcript --note-id <note_id>
```

<a id="行为契约"></a>
## Behavior contract

- The CLI first verifies whether the Note is `unified`; if it is not unified, the transcript is not fetched.
- The CLI automatically paginates internally and concatenates the complete content; if any page fails, the whole operation errors out, and no partial transcript is saved.
- By default, it saves to `./notes/{note_id}/unified_transcript.md`; when `--transcript-format plain_text`, it saves as `.txt`.
- It fails if the target file already exists; add `--overwrite` only when the user explicitly wants to overwrite.

<a id="相关场景"></a>
## Related scenarios
- [Query Minutes, transcripts, shared documents, etc. by note_id](../scenes/query-note-and-artifacts.md)
