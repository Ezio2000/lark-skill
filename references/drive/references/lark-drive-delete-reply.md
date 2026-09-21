# drive +delete-reply


Delete a reply. **High-risk write operation**: actual execution requires confirming with the user according to the high-risk approval protocol in [`../../shared/index.md`](../../shared/index.md), then appending `--yes`; deletion is irreversible.

<a id="命令"></a>
## Command

```bash
# Preview first (--dry-run does not require --yes)
lark-cli drive +delete-reply --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --comment-id '<id>' --reply-id '<id>' --dry-run

# After confirmation, actually delete (replace --dry-run with --yes)
lark-cli drive +delete-reply --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --comment-id '<id>' --reply-id '<id>' --yes
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|---|---|---|
| `--url` | Choose one of this or `--token` | Recommended entry point. Supports doc/docx/sheet/file/slides/base/bitable/apps/wiki URLs; for apps Miaoda URLs use `/page/<token>`; wiki URLs are automatically resolved to the real document. |
| `--token` | Choose one of this or `--url` | Bare token or URL. A bare token must be paired with `--type`; for wiki tokens use `--type wiki`. |
| `--type` | Required when using a bare token | Pass the type corresponding to the token: `doc`, `docx`, `sheet`, `file`, `slides`, `bitable`, `base`, `apps`, `wiki`. For wiki tokens use `wiki`; when `base` is passed, the CLI processes it as type `bitable`. |
| `--comment-id` | Yes | The comment ID to which the reply belongs; from `drive +list-comments` |
| `--reply-id` | Yes | The reply ID to delete; from `items[].reply_id` of `drive +list-replies`, or `items[].reply_list.replies[].reply_id` of `drive +list-comments` |
| `--yes` | Yes for actual execution | High-risk confirmation; not required for `--dry-run` preview |

<a id="行为说明"></a>
## Behavior

- Deletion takes effect permanently; replies have no recycle bin or undo.
- Deletion takes effect reply by reply: deleting a reply (including the first/root reply) does not affect other replies; only after all replies under that comment card are deleted does the comment card stop displaying on the frontend page.
- **There is no dedicated command for deleting an entire comment; you need to use this command to delete all replies under that card** (first use `drive +list-replies` to pull all reply IDs). Before deleting, confirm with the user whether you are deleting a single reply or the entire comment.

<a id="输出"></a>
## Output

```json
{
  "file_token": "docx_token",
  "file_type": "docx",
  "comment_id": "<comment_id>",
  "reply_id": "<reply_id>",
  "deleted": true
}
```

<a id="参考"></a>
## References

- [lark-drive-list-replies](lark-drive-list-replies.md) -- get replies and reply_id
