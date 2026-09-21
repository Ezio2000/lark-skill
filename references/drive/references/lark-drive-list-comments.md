# drive +list-comments


List comment cards for doc/docx/sheet/file/slides/base(bitable)/apps. Prefer passing the complete URL given by the user; the shortcut automatically identifies the type; apps is the Miaoda type and supports `/page/<token>` URLs; if a wiki URL or `--token <wiki_token> --type wiki` is passed, it is first resolved to the real document.

<a id="重要默认口径"></a>
## Important default behavior

- By default, only unresolved comments are queried, i.e., without additionally passing `--solved-status` or by explicitly passing `--solved-status false`. Even if the user says "all comments", "every comment", or "list all the comments", as long as they do not explicitly mention including resolved comments, still query unresolved comments according to the default behavior.
- Only when the user explicitly requests semantics such as "include resolved comments", "both resolved and unresolved", or "all historical comments" should `--solved-status all` be passed.
- Whether there is a next page is determined by `has_more` in the output; `page_token` is only used as the cursor to continue to the next page when `has_more=true`.

<a id="命令"></a>
## Command

```bash
# Recommended: pass the complete URL given by the user directly. By default, only unresolved comments are queried.
lark-cli drive +list-comments --url "<DOCUMENT_URL>"

# Only when the user explicitly requests including resolved comments should --solved-status all be passed.
lark-cli drive +list-comments --url "<DOCUMENT_URL>" --solved-status all
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--url` | Choose one of `--token` | Recommended entry point. Supports doc/docx/sheet/file/slides/base/bitable/apps/wiki URLs; apps Miaoda URLs use `/page/<token>`; wiki URLs are automatically resolved to the real document. |
| `--token` | Choose one of `--url` | Bare token or URL. A bare token must be paired with `--type`; wiki tokens use `--type wiki`. |
| `--type` | Required when using a bare token | Pass the type corresponding to the token: `doc`, `docx`, `sheet`, `file`, `slides`, `bitable`, `base`, `apps`, `wiki`. Wiki tokens use `wiki`; when `base` is passed, the CLI processes it as the `bitable` type. |
| `--solved-status` | No | `false` / `true` / `all`, default `false`. `false` queries unresolved comments; `true` queries resolved comments; `all` queries all comments. |
| `--comment-scope` | No | `all` / `whole` / `partial`, default `all`. `all` queries the full scope; `whole` queries full-text comments; `partial` queries local comments. |
| `--need-reaction` | No | Whether to return reaction data on comment cards; include it only when the user explicitly needs reactions. |
| `--need-relation` | No | docx comment location relation field; effective only for docx, silently ignored for non-docx. To locate body text, first read [`lark-drive-comment-location.md`](lark-drive-comment-location.md). |
| `--page-size` | No | Default 50, maximum 100. |
| `--page-token` | No | Pagination cursor; this shortcut does not automatically paginate, continue requesting the next page according to the returned `page_token`. |

<a id="行为说明"></a>
## Behavior notes

- `--comment-scope all` queries the full scope; `whole` queries full-text comments; `partial` queries local/selection comments.
- When the user has already provided a complete URL, pass it as-is to `--url`; do not first extract the token and then reassemble it into another type of URL. For example, keep `/sheets/<token>` for sheets, keep `/wiki/<token>` for wiki, and keep `/page/<token>` for Miaoda apps.
- When inputting a URL, there is no need to pass `--type`; if the URL type conflicts with an explicit `--type`, the shortcut returns a validation error, and it is recommended to remove `--type`.
- Wiki input is automatically resolved to the real document, and then the comment list is queried. The JSON output does not additionally return a wiki token or wiki node.
- `items` in the output preserves the comment card fields, and the outer layer supplements `file_token`, `file_type`, `has_more`, `page_token`, `count`; `count` is the number of comment cards returned on the current page. Whether to continue pagination is determined by `has_more`, not merely by whether `page_token` exists.

<a id="评论卡片模型"></a>
## Comment card model

- The returned `items` is a list of comment cards; each `item` corresponds to one comment card in the user interface, not a flattened list of interaction messages.
- When a comment is created, the first reply in that card is also created at the same time; what truly carries the body text is `item.reply_list.replies`, in which the first reply (root reply) is, from the user's perspective, the "comment itself" in this card. Updating the root reply rewrites the comment body text (see [`lark-drive-update-reply.md`](lark-drive-update-reply.md)); deletion takes effect reply by reply, and the card disappears only when the last reply is deleted (see [`lark-drive-delete-reply.md`](lark-drive-delete-reply.md)).
- `item.has_more=true` indicates that there are still replies under this comment card not included in this return; this is a different field from the outer `has_more` (whether there is a next page of comment cards). When complete replies are needed, continue using `drive +list-replies --comment-id <id>` pagination to fetch them all.

<a id="统计口径"></a>
## Counting rules

- To count the "number of comments" or "number of comment cards": count the length of `items`; for full counting, add up the lengths of `items` returned across all pages.
- To count the "number of replies": count the sum of the lengths of all `item.reply_list.replies`, then subtract the length of `items`.
- To count the "total number of interactions": count the sum of the lengths of all `item.reply_list.replies`, including the first comment in each comment card.
- When any `item.has_more=true`, first use `drive +list-replies --comment-id <id>` to fetch all replies for that card, then count replies or total interactions; otherwise the count will be too low.

<a id="排序"></a>
## Sorting

- Only when the user explicitly mentions "latest comment", "last comment", or "earliest comment" is it necessary to sort by `create_time`.
- Before sorting, all comment pages must be fully fetched; do not take only the first page.
- "Latest comment"/"last comment": sort by `create_time` in descending order and take the first one. "Earliest comment": sort by `create_time` in ascending order and take the first one.
- When the user only says "first comment", directly use the first one returned; no additional sorting is needed.

<a id="输出"></a>
## Output

```json
{
  "file_token": "docx_token",
  "file_type": "docx",
  "items": [],
  "has_more": false,
  "page_token": "",
  "count": 0
}
```

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for cloud space (Drive/cloud storage)
- [lark-drive-list-replies](lark-drive-list-replies.md) -- fetch all replies under a certain card (counting and `item.has_more` completion)
- [lark-drive-comment-location](lark-drive-comment-location.md) -- use `need_relation` to locate docx body text
