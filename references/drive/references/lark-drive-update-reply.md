# drive +update-reply


Fully replace the content of a reply.

<a id="命令"></a>
## Command

```bash
# Recommended: full URL + comment ID + reply ID + new content (full replacement, no partial editing)
lark-cli drive +update-reply --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --comment-id '<id>' --reply-id '<id>' --content '[{"type":"text","text":"新内容"}]'
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|---|---|---|
| `--url` | Choose one of this and `--token` | Recommended entry point. Supports doc/docx/sheet/file/slides/base/bitable/apps/wiki URLs; for apps Miaoda URLs use `/page/<token>`; wiki URLs are automatically resolved to the actual document. |
| `--token` | Choose one of this and `--url` | Bare token or URL. A bare token must be paired with `--type`; for a wiki token use `--type wiki`. |
| `--type` | Required when using a bare token | Pass the type corresponding to the token: `doc`, `docx`, `sheet`, `file`, `slides`, `bitable`, `base`, `apps`, `wiki`. For a wiki token use `wiki`; when `base` is passed, the CLI processes it as type `bitable`. |
| `--comment-id` | Yes | The ID of the comment to which the reply belongs; from `drive +list-comments` |
| `--reply-id` | Yes | The ID of the reply to update; from `items[].reply_id` of `drive +list-replies` |
| `--content` | Yes | The new `reply_elements` JSON; `type=text` text is automatically escaped; for the full schema see [`lark-drive-comment-content.md`](lark-drive-comment-content.md) |

<a id="行为说明"></a>
## Behavior notes

- Updates are full replacements: the new `content` completely overwrites the old content, with no partial-modification semantics.
- **You can only update replies created by the current identity**; updating someone else's reply returns API error `1069303 forbidden`. Before executing, first use `+list-replies` to verify `items[].user_id` (open_id), and execute with the same `--as` identity that created the reply.
- Updating the root reply of a comment card (the `items[0]` on the first page, i.e. the earliest-created reply) is equivalent to rewriting the body of the comment itself; before rewriting, confirm with the user whether you are changing the reply or the comment body.

<a id="输出"></a>
## Output

```json
{
  "file_token": "docx_token",
  "file_type": "docx",
  "comment_id": "<comment_id>",
  "reply_id": "<reply_id>",
  "updated": true
}
```

<a id="参考"></a>
## References

- [lark-drive-comment-content](lark-drive-comment-content.md) -- `--content` format
- [lark-drive-list-replies](lark-drive-list-replies.md) -- get replies and reply_id
