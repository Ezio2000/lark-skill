# note +detail

Query meeting note details via `note_id` to obtain attached document tokens (AI Note, transcript, in-meeting shared documents). Read-only, supports `--as user` or `--as bot`.

<a id="命令"></a>
## Command

```bash
lark-cli note +detail --note-id <note_id>
lark-cli note +detail --note-id <note_id> --as bot
```

When `note_id` is obtained from another command, the source identity must be explicitly carried over. Whether the app identity can read the data depends on the app's view permission for the note's main document. If `--as bot` returns `note_display_type=unified`, do not silently switch to the user identity to execute `note +transcript`; first explain to the user that this command only supports the user identity.

<a id="相关场景"></a>
## Related scenarios
- [Query notes, transcripts, shared documents, etc. based on note_id](../scenes/query-note-and-artifacts.md)
