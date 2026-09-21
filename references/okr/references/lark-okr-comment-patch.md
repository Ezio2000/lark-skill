# okr +comment-patch

Modify the body of a specified comment. The comment target, selection anchor, and reference relationship cannot be modified once created. Only the user identity is supported.

`--content` is a business-required field: in the OpenAPI schema this field may appear optional, but actually modifying a comment requires providing a non-empty body.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Modify the comment body using the simple style.
lark-cli okr +comment-patch --comment-id 7000000000000000004 --content '{"text":"更新后的评论"}'

# Modify the comment body using a richtext file.
lark-cli okr +comment-patch --comment-id 7000000000000000004 --style richtext --content '@comment.json'

# Preview the API call for modifying the comment before writing, without actually executing it.
lark-cli okr +comment-patch --comment-id 7000000000000000004 --content '{"text":"预览更新"}' --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter      | Required | Default | Description                                                                                                                          |
|----------------|------|---------|-------------------------------------------------------------------------------------------------------------------------------|
| --comment-id   | Yes   | —       | Comment ID, int64 positive integer; can be obtained from [+comment-list](lark-okr-comment-list.md) or [+comment-detail](lark-okr-comment-detail.md). |
| --content      | Yes   | —       | New body; input style: `simple` (semi-plain-text JSON, recommended) \| `richtext` (full ContentBlock JSON), supports @file path.                   |
| --style        | No   | simple  | Input/output style: simple or richtext.                                                                                           |
| --user-id-type | No   | open_id | open_id, union_id, user_id, or user_key.                                                                                      |
| --dry-run      | No   | —       | Preview the API call without actually executing it.                                                                                                   |
| --format       | No   | json    | Output format.                                                                                                                    |

<a id="工作流程"></a>
## Workflow

1. Use [+comment-list](lark-okr-comment-list.md), [+comment-detail](lark-okr-comment-detail.md), or [+comment-get](lark-okr-comment-get.md) to confirm the comment-id and the target comment.
2. Prepare content: it is usually recommended to use the simple format; when you need precise control over the position of @user, you can use the richtext format, see [ContentBlock format](lark-okr-contentblock.md)
3. Execute +comment-patch; before actually writing, use --dry-run to check the request.
4. If you want to resolve or reopen a comment, do not use patch; instead use [+comment-solve](lark-okr-comment-solve-reopen.md) or [+comment-reopen](lark-okr-comment-solve-reopen.md).

<a id="输出"></a>
## Output

Returns JSON:

```json
{
  "comment": {
    "id": "7000000000000000004",
    "target": {"target_type": "progress", "target_id": "3456789012345678901"},
    "commentator_id": "ou_xxx",
    "status": "open",
    "create_time": "2025-01-15 10:30:00",
    "update_time": "2025-01-15 11:00:00",
    "content": {"text": "更新后的评论", "mention": [], "docs": [], "images": []}
  },
  "style": "simple"
}
```

The content in simple style is SemiPlainContent; the content in richtext style is ContentBlock.

<a id="注意事项"></a>
## Notes

- patch does not change the comment's target, selection, ref_comment_id, or status.
- simple input does not support docs/images; use richtext when rich text elements are needed.
- An empty body cannot be submitted; if you need to delete a comment, use [+comment-delete](lark-okr-comment-delete.md); deletion is irreversible.

<a id="参考"></a>
## References

- [lark-okr](../index.md) — OKR commands, routing, and general conventions
- [OKR entity definitions](lark-okr-entities.md) — Comment fields and comment thread rules
- [ContentBlock format](lark-okr-contentblock.md) — Comment body format
- [okr +comment-get](lark-okr-comment-get.md) — Get the comment before and after the update
- [okr +comment-delete](lark-okr-comment-delete.md) — Permanently delete a comment
- [lark-shared](../../shared/index.md) — Authentication, identity, permissions, and security rules
