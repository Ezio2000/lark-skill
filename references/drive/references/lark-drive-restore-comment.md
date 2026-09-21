# drive +restore-comment


Restore / reopen a resolved comment. The reverse operation—marking a comment as resolved—is a separate command [`lark-drive-resolve-comment.md`](lark-drive-resolve-comment.md).

When the user says "reopen / unresolve / restore this comment", it corresponds to this command.

<a id="命令"></a>
## Command

```bash
# Recommended: full URL + comment ID
lark-cli drive +restore-comment --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --comment-id '<id>'
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|---|---|---|
| `--url` | Choose one of this and `--token` | Recommended entry point. Supports doc/docx/sheet/file/slides/base/bitable/apps/wiki URLs; for apps Miaoda URLs use `/page/<token>`; wiki URLs are automatically resolved to the real document. |
| `--token` | Choose one of this and `--url` | Bare token or URL. A bare token must be paired with `--type`; for a wiki token use `--type wiki`. |
| `--type` | Required when using a bare token | Pass the type corresponding to the token: `doc`, `docx`, `sheet`, `file`, `slides`, `bitable`, `base`, `apps`, `wiki`. For a wiki token use `wiki`; when `base` is passed, the CLI processes it as the `bitable` type. |
| `--comment-id` | Yes | The ID of the comment to restore; comes from `items[].comment_id` of `drive +list-comments` |

<a id="行为说明"></a>
## Behavior notes

- This is a write operation.
- **Finding the target comment requires `--solved-status`**: `drive +list-comments` by default returns only unresolved comments, and the target of this command is exactly a resolved comment, so querying with the default scope will find none at all. First use `drive +list-comments --solved-status true` (resolved only) or `--solved-status all` (all) to get `items[].comment_id`.
- Repeatedly toggling the resolved state of the same comment in succession may trigger server-side rate limiting (HTTP 429); leave an interval between consecutive calls or retry after a short delay.

<a id="输出"></a>
## Output

```json
{
  "file_token": "docx_token",
  "file_type": "docx",
  "comment_id": "<comment_id>",
  "action": "restore",
  "is_solved": false,
  "updated": true
}
```

<a id="参考"></a>
## References

- [lark-drive-resolve-comment](lark-drive-resolve-comment.md) -- Resolve (mark as resolved) a comment
