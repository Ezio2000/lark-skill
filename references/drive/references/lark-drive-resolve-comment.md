# drive +resolve-comment


Mark a comment as resolved. The reverse operation—reopening a resolved comment—is a separate command [`lark-drive-restore-comment.md`](lark-drive-restore-comment.md).

When a user says "mark this comment as handled / completed / closed", it corresponds to this command.

<a id="命令"></a>
## Command

```bash
# Recommended: full URL + comment ID
lark-cli drive +resolve-comment --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --comment-id '<id>'
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|---|---|---|
| `--url` | Choose one of `--token` | Recommended entry point. Supports doc/docx/sheet/file/slides/base/bitable/apps/wiki URLs; apps Miaoda URLs use `/page/<token>`; wiki URLs are automatically resolved to the real document. |
| `--token` | Choose one of `--url` | Bare token or URL. A bare token must be paired with `--type`; wiki tokens use `--type wiki`. |
| `--type` | Required when using a bare token | Pass the type corresponding to the token: `doc`, `docx`, `sheet`, `file`, `slides`, `bitable`, `base`, `apps`, `wiki`. Wiki tokens use `wiki`; when `base` is passed, the CLI processes it as the `bitable` type. |
| `--comment-id` | Yes | The comment ID to resolve; comes from the `items[].comment_id` of `drive +list-comments` |

<a id="行为说明"></a>
## Behavior Notes

- This is a write operation.
- Repeatedly toggling the resolved state of the same comment may trigger server-side rate limiting (HTTP 429); leave an interval between consecutive calls or retry after a short delay.

<a id="输出"></a>
## Output

```json
{
  "file_token": "docx_token",
  "file_type": "docx",
  "comment_id": "<comment_id>",
  "action": "resolve",
  "is_solved": true,
  "updated": true
}
```

<a id="参考"></a>
## References

- [lark-drive-restore-comment](lark-drive-restore-comment.md) -- Restore (reopen) a comment
