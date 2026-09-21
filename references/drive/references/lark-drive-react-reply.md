# drive +react-reply


Add or remove an emoji reaction on a reply. The operation target is always `reply_id`.

<a id="命令"></a>
## Command

```bash
# add reaction
lark-cli drive +react-reply --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --reply-id '<id>' --emoji THUMBSUP --action add

# delete a reaction you added yourself: you still need to pass the --emoji to delete
lark-cli drive +react-reply --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --reply-id '<id>' --emoji THUMBSUP --action delete
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|---|---|---|
| `--url` | Choose one of this and `--token` | Recommended entry point. Supports doc/docx/sheet/file/slides/base/bitable/apps/wiki URLs; for apps Miaoda URLs use `/page/<token>`; wiki URLs are automatically resolved to the real document. |
| `--token` | Choose one of this and `--url` | A bare token or URL. A bare token must be paired with `--type`; for a wiki token use `--type wiki`. |
| `--type` | Required when using a bare token | Pass the type corresponding to the token: `doc`, `docx`, `sheet`, `file`, `slides`, `bitable`, `base`, `apps`, `wiki`. For a wiki token use `wiki`; when `base` is passed, the CLI processes it as the `bitable` type. |
| `--reply-id` | Yes | The reply ID to operate on; comes from `items[].reply_id` of `drive +list-replies`. To add/remove an emoji on "this comment", take the `reply_id` of that comment's root reply (the first page's `items[0]`) |
| `--emoji` | Yes | The `reaction_type` value, case-sensitive; validated locally against the platform enum. For the full list and semantic mapping, see [`lark-drive-reactions.md`](lark-drive-reactions.md) |
| `--action` | Yes | `add` adds; `delete` deletes a reaction added by the current identity itself |

<a id="行为说明"></a>
## Behavior notes

- `--emoji` is case-sensitive (for example `THUMBSUP` and `ThumbsDown`), and local enum validation serves as a fallback. The server does not validate `reaction_type`: any string will be accepted and persisted as a corrupted reaction, so local validation is the only line of defense; when calling the native command directly, you must ensure the value is valid yourself.
- add / delete are idempotent: repeatedly adding an existing reaction or deleting a nonexistent reaction both return success with no side effects; delete only removes a reaction added by the current identity itself.
- Operating on the root reply is equivalent to adding/removing an emoji on the comment itself.
- To read back reactions: include `--need-reaction` on `drive +list-replies` / `drive +batch-query-comments`; entries in `count=0` are remnants of deleted reactions, so filter by `count>0` to determine whether one exists.

<a id="输出"></a>
## Output

```json
{
  "file_token": "docx_token",
  "file_type": "docx",
  "reply_id": "<reply_id>",
  "reaction_type": "THUMBSUP",
  "action": "add",
  "updated": true
}
```

<a id="参考"></a>
## References

- [lark-drive-reactions](lark-drive-reactions.md) -- reaction query rules, semantics, and the full enum
- [lark-drive-list-replies](lark-drive-list-replies.md) -- get reply_id
