# drive +add-reply


Add a reply to an existing comment.

<a id="命令"></a>
## Command

```bash
# Recommended: full URL + target comment ID + reply content
lark-cli drive +add-reply --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --comment-id '<id>' --content '[{"type":"text","text":"回复内容"}]'
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|---|---|---|
| `--url` | Choose one of `--token` | Recommended entry point. Supports doc/docx/sheet/file/slides/base/bitable/apps/wiki URLs; for apps Miaoda URLs use `/page/<token>`; wiki URLs are automatically resolved to the real document. |
| `--token` | Choose one of `--url` | Bare token or URL. A bare token must be paired with `--type`; for a wiki token use `--type wiki`. |
| `--type` | Required when using a bare token | Pass the type corresponding to the token: `doc`, `docx`, `sheet`, `file`, `slides`, `bitable`, `base`, `apps`, `wiki`. For a wiki token use `wiki`; when `base` is passed, the CLI processes it as type `bitable`. |
| `--comment-id` | Yes | The ID of the comment to reply to; comes from `items[].comment_id` of `drive +list-comments` |
| `--content` | Yes | `reply_elements` JSON, `type=text` text is automatically escaped; for the full schema, mention_user/link, and the 10000-character limit, see [`lark-drive-comment-content.md`](lark-drive-comment-content.md) |

<a id="回复限制"></a>
## Reply restrictions

- You cannot reply to whole-document comments in `is_whole=true` or resolved comments in `is_solved=true`.
- The target's `is_whole` / `is_solved` are usually already present in the results of the previous step's `+list-comments` / `+batch-query-comments`, so you can judge based on that; only query again when the information is insufficient.
- When querying again, note that `+list-comments` by default returns only unresolved comments: to verify whether a comment has been resolved, you need to include `--solved-status all`, otherwise resolved comments will not appear in the results at all, making it look like the comment does not exist.
- When a restriction is hit, report it truthfully ("whole-document comments do not support replies" / "this comment has been resolved and cannot be replied to"), and do not automatically redirect the user's reply to a different comment.

<a id="输出"></a>
## Output

```json
{
  "file_token": "docx_token",
  "file_type": "docx",
  "comment_id": "<comment_id>",
  "created": true,
  "reply_id": "<reply_id>"
}
```

<a id="参考"></a>
## References

- [lark-drive-comment-content](lark-drive-comment-content.md) -- `--content` format
- [lark-drive-batch-query-comments](lark-drive-batch-query-comments.md) -- query is_whole/is_solved by ID
- [lark-drive-list-replies](lark-drive-list-replies.md) -- get replies
