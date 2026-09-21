# drive +list-replies


Paginate through the replies under a comment.

<a id="命令"></a>
## Command

```bash
# Recommended: full URL + comment ID
lark-cli drive +list-replies --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --comment-id '<id>'
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|---|---|---|
| `--url` | Choose one of `--token` | Recommended entry point. Supports doc/docx/sheet/file/slides/base/bitable/apps/wiki URLs; for apps Miaoda URLs use `/page/<token>`; wiki URLs are automatically resolved to the real document. |
| `--token` | Choose one of `--url` | Bare token or URL. A bare token must be paired with `--type`; for a wiki token use `--type wiki`. |
| `--type` | Required when using a bare token | Pass the type corresponding to the token: `doc`, `docx`, `sheet`, `file`, `slides`, `bitable`, `base`, `apps`, `wiki`. For a wiki token use `wiki`; when `base` is passed, the CLI processes it as the `bitable` type. |
| `--comment-id` | Yes | Comment ID; comes from the `items[].comment_id` of `drive +list-comments` |
| `--page-size` | No | 1-100, default 50 |
| `--page-token` | No | The `page_token` from the previous output; use it to continue fetching when `has_more=true` |
| `--need-reaction` | No | Return reaction data on replies, see [`lark-drive-reactions.md`](lark-drive-reactions.md) |

<a id="行为说明"></a>
## Behavior notes

- The root reply carries the comment body itself and is the earliest-created item in the reply list: **only the `items[0]` on the first page (when `--page-token` is not passed) is the root reply**; after pagination (when `--page-token` is passed), the returned `items[0]` is just an ordinary reply, so do not treat it as the root reply by position when updating or deleting.
- Output fields: `items[].reply_id` / `user_id` / `create_time` / `update_time` / `content.elements`, for use by `+update-reply`, `+delete-reply`.
- Check reply ownership (before updating/deleting): compare `items[].user_id` (open_id) with the current identity to determine whether the reply was created by yourself.
- The output `items` is always a JSON array (normalized to `[]` when omitted by the server).

<a id="输出"></a>
## Output

```json
{
  "file_token": "docx_token",
  "file_type": "docx",
  "comment_id": "<comment_id>",
  "items": [],
  "has_more": false,
  "page_token": "",
  "count": 0
}
```

`items` is an array of replies; whether to continue paginating is determined by `has_more`, and when `has_more=true`, use the returned `page_token` to continue fetching.

<a id="参考"></a>
## References

- [lark-drive-list-comments](lark-drive-list-comments.md) -- comment card model and statistics conventions
- [lark-drive-update-reply](lark-drive-update-reply.md) -- update a reply
- [lark-drive-delete-reply](lark-drive-delete-reply.md) -- delete a reply
- [lark-drive-reactions](lark-drive-reactions.md) -- reaction query and write
