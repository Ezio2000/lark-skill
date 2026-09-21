# drive +batch-query-comments


Batch retrieve comment cards by comment ID. When comment_id is known, use it for precise retrieval; to paginate, do a full count, or find the latest/earliest comments, use [`lark-drive-list-comments.md`](lark-drive-list-comments.md).

<a id="命令"></a>
## Command

```bash
# Recommended: full URL + comment IDs (comma-separated or repeat --comment-ids, max 100 per call)
lark-cli drive +batch-query-comments --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --comment-ids '<id1>,<id2>'
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|---|---|---|
| `--url` | Choose one of `--token` | Recommended entry point. Supports doc/docx/sheet/file/slides/base/bitable/apps/wiki URLs; for apps Miaoda URLs use `/page/<token>`; wiki URLs are automatically resolved to the real document. |
| `--token` | Choose one of `--url` | Bare token or URL. A bare token must be paired with `--type`; for a wiki token use `--type wiki`. |
| `--type` | Required when using a bare token | Pass the type corresponding to the token: `doc`, `docx`, `sheet`, `file`, `slides`, `bitable`, `base`, `apps`, `wiki`. For a wiki token use `wiki`; when `base` is passed, the CLI processes it as type `bitable`. |
| `--comment-ids` | Yes | Comment ID, comma-separated or passed repeatedly, at most 100 per call; the `items[].comment_id` from `drive +list-comments` |
| `--need-reaction` | No | Return reaction data on the comment cards, see [`lark-drive-reactions.md`](lark-drive-reactions.md) |
| `--need-relation` | No | docx comment location relationship; only takes effect for docx, silently ignored for non-docx, see [`lark-drive-comment-location.md`](lark-drive-comment-location.md) |

<a id="行为说明"></a>
## Behavior notes

- `--need-relation` is sent via the request **body** (`+list-comments` is a query param), and is only sent when the resolved target is docx; this parameter is not included in the platform metadata, but the server supports it, returning `items[].relation` and the block location.
- The output `items` is always a JSON array (normalized to `[]` when omitted by the server), with `file_token`, `file_type`, and `count` added at the outer level.

<a id="输出"></a>
## Output

```json
{
  "file_token": "docx_token",
  "file_type": "docx",
  "items": [],
  "count": 0
}
```

`items` is the array of matched comment cards (with `file_token`/`file_type` added at the outer level, and `wiki_token` additionally for wiki input); `count` is the number of matches.

<a id="参考"></a>
## References

- [lark-drive-list-comments](lark-drive-list-comments.md) -- paginated retrieval of the comment list
- [lark-drive-comment-location](lark-drive-comment-location.md) -- `need_relation` comment location
