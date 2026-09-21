# okr +comment-solve / +comment-reopen


Solve/reopen a comment. Entity-level comments are handled as a single comment; selection comments operate on the entire comment thread. Only the user identity is supported.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Solve an entity-level comment or an entire selection comment thread.
lark-cli okr +comment-solve --comment-id 7000000000000000004

# Reopen a solved entity-level comment or selection comment thread.
lark-cli okr +comment-reopen --comment-id 7000000000000000004

# Preview the status change request for solving a comment without actually executing it.
lark-cli okr +comment-solve --comment-id 7000000000000000004 --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter      | Required | Default | Description                                                                                  |
|----------------|------|---------|---------------------------------------------------------------------------------------|
| --comment-id   | Yes   | —       | Comment ID, int64 positive integer. Can be obtained from +comment-list, +comment-detail, or +comment-get.     |
| --user-id-type | No   | open_id | open_id, union_id, user_id, or user_key.                                              |
| --style        | No   | simple  | Body style of affected_comments: simple (SemiPlainContent) or richtext (ContentBlock). |
| --dry-run      | No   | —       | Preview the API call without actually executing it.                                                           |
| --format       | No   | json    | Output format.                                                                            |

<a id="工作流程"></a>
## Workflow

1. Use [+comment-list](lark-okr-comment-list.md), [+comment-detail](lark-okr-comment-detail.md), or [+comment-get](lark-okr-comment-get.md) to obtain and confirm the comment-id.
2. Check whether the comment belongs to a selection thread: if the response has selection.id, solve/reopen will affect all comments under the same selection.id.
3. Choose +comment-solve or +comment-reopen based on the user action; first use --dry-run to check the target interface.
4. After execution, check affected_comments to confirm the scope of status changes for the entity-level comment or the entire comment thread.

<a id="输出"></a>
## Output

Returns JSON:

```json
{
  "affected_comments": [
    {
      "id": "7000000000000000004",
      "target": {
        "target_type": "objective",
        "target_id": "2345678901234567890"
      },
      "commentator_id": "ou_xxx",
      "status": "solved",
      "create_time": "2025-01-15 10:30:00",
      "update_time": "2025-01-15 11:30:00",
      "selection": {
        "id": "8000000000000000001",
        "selected_text": "提升核心接口稳定性"
      },
      "content": {
        "text": "请补充指标", "mention": [], "docs": [], "images": []
      }
    }
  ],
  "style": "simple"
}
```

- After a successful +comment-solve, the status of affected_comments is usually solved; after a successful +comment-reopen, it is usually open.
- The simple style returns SemiPlainContent; the richtext style returns ContentBlock.

<a id="注意事项"></a>
## Notes

- Selection comments are solved/reopened as a comment thread, but [+comment-delete](lark-okr-comment-delete.md) still deletes only a single comment.
- Solving is not deleting; it can later be restored with +comment-reopen; once deleted, it cannot be restored.
- This operation is a write operation; before executing, confirm the comment-id and the target action.

<a id="参考"></a>
## References

- [lark-okr](../index.md) — OKR commands, routing, and general conventions
- [OKR entity definitions](lark-okr-entities.md) — Comment, comment thread, and status rules
- [ContentBlock format](lark-okr-contentblock.md) — affected_comments body format
- [okr +comment-get](lark-okr-comment-get.md) — Get status and selection.id
- [okr +comment-delete](lark-okr-comment-delete.md) — Permanently delete a single comment
- [lark-shared](../../shared/index.md) — Authentication, identity, permissions, and security rules
