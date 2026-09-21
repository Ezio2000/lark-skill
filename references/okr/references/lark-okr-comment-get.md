# okr +comment-get

Get a single OKR comment by comment ID, and view the comment body, status, comment target, reference relationship, and selection information. This shortcut is suitable for confirming the final state of a comment after editing it.

<a id="推荐命令"></a>
## Recommended Commands

```bash
# Get the simplified body and metadata of a comment.
lark-cli okr +comment-get --comment-id 7000000000000000001

# Get the comment body in raw ContentBlock format.
lark-cli okr +comment-get --comment-id 7000000000000000001 --style richtext

# Preview the API call for getting a comment without actually executing it.
lark-cli okr +comment-get --comment-id 7000000000000000001 --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter      | Required | Default | Description                                                                                              |
|----------------|----------|---------|----------------------------------------------------------------------------------------------------------|
| --comment-id   | Yes      | —       | Comment ID, an int64 positive integer.                                                                   |
| --user-id-type | No       | open_id | open_id, union_id, user_id, or user_key.                                                                 |
| --style        | No       | simple  | simple returns a semi-plain-text format, recommended when font/color information is not involved; richtext returns ContentBlock. |
| --dry-run      | No       | —       | Preview the API call without actually executing it.                                                      |
| --format       | No       | json    | Output format.                                                                                           |

<a id="工作流程"></a>
## Workflow

1. If you only have the target ID, first use [+comment-list](lark-okr-comment-list.md) or [+comment-detail](lark-okr-comment-detail.md) to locate the comment-id.
2. Run +comment-get --comment-id "...".
3. Check selection, status, and ref_comment_id according to subsequent operations: selection.id indicates a selection comment, status being solved indicates it is resolved, and ref_comment_id indicates a reference relationship.

<a id="输出"></a>
## Output

```json
{
  "comment": {
    "id": "7000000000000000001",
    "target": {"target_type": "progress", "target_id": "3456789012345678901"},
    "commentator_id": "ou_xxx",
    "status": "open",
    "create_time": "2025-01-15 10:30:00",
    "update_time": "2025-01-15 10:30:00",
    "content": {"text": "进展不错", "mention": [], "docs": [], "images": []},
    "ref_comment_id": "7000000000000000000"
  },
  "style": "simple"
}
```

selection, solver_id, solved_time, and ref_comment_id are retained depending on whether the API returns them.

<a id="注意事项"></a>
## Notes

- Selection comments on Objective/KeyResult belong to a comment thread via selection.id; entity-level comments have no selection.
- To resolve or reopen, use [+comment-solve / +comment-reopen](lark-okr-comment-solve-reopen.md).

<a id="参考"></a>
## References

- [lark-okr](../index.md) — OKR commands, routing, and general conventions
- [OKR entity definitions](lark-okr-entities.md) — Comment fields and comment thread rules
- [ContentBlock format](lark-okr-contentblock.md) — Comment body format
- [okr +comment-list](lark-okr-comment-list.md) — Query comments under a target
- [lark-shared](../../shared/index.md) — Authentication, identity, permissions, and security rules
