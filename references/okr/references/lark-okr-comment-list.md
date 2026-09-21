# okr +comment-list

Paginate through comments under a single Cycle, Objective, KeyResult, or Progress. To query all comments under an entire cycle, use [+comment-detail](lark-okr-comment-detail.md).

<a id="推荐命令"></a>
## Recommended Commands

```bash
# Get the first page of comments under an Objective.
lark-cli okr +comment-list --target-type objective --target-id 2345678901234567890

# Use the previous page token to get the next page of comments under a Progress.
lark-cli okr +comment-list --target-type progress --target-id 3456789012345678901 --page-size 100 --page-token "7000000000000000002"

# Output KeyResult comments in richtext, but only preview the request without actually fetching.
lark-cli okr +comment-list --target-type key_result --target-id 4567890123456789012 --style richtext --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter      | Required | Default | Description                                                                                          |
|----------------|----------|---------|------------------------------------------------------------------------------------------------------|
| --target-type  | Yes      | —       | cycle, objective, key_result, or progress.                                                           |
| --target-id    | Yes      | —       | Comment target ID, a positive int64 integer.                                                         |
| --page-size    | No       | 100     | Number per page, range 1-100.                                                                        |
| --page-token   | No       | ""      | Token from the previous response; omit for the first page.                                           |
| --user-id-type | No       | open_id | open_id, union_id, user_id, or user_key.                                                             |
| --style        | No       | simple  | simple returns a semi-plain-text format, recommended when font/color information is not involved; richtext returns ContentBlock. |
| --dry-run      | No       | —       | Preview the API call without actually executing it.                                                  |
| --format       | No       | json    | Output format.                                                                                       |

<a id="工作流程"></a>
## Workflow

1. Choose target-type based on the user's needs: use cycle for a cycle, objective for an objective, key_result for a key result, and progress for a progress.
2. If the ID is missing, use [+cycle-list](lark-okr-cycle-list.md), [+cycle-detail](lark-okr-cycle-detail.md), or [+progress-list](lark-okr-progress-list.md) to obtain it.
3. Execute +comment-list --target-type "..." --target-id "...".
4. When has_more is true and page_token is non-empty, pass page_token as-is as the --page-token for the next call; do not parse or modify the token yourself.

<a id="输出"></a>
## Output

```json
{
  "comments": [
    [
      {
        "id": "7000000000000000001",
        "target": {"target_type": "objective", "target_id": "2345678901234567890"},
        "commentator_id": "ou_xxx",
        "status": "open",
        "create_time": "2025-01-15 10:30:00",
        "update_time": "2025-01-15 10:30:00",
        "selection": {"id": "8000000000000000001", "selected_text": "提升核心接口稳定性"},
        "content": {"text": "请补充指标", "mention": [], "docs": [], "images": []}
      }
    ]
  ],
  "has_more": true,
  "page_token": "7000000000000000002",
  "style": "simple"
}
```

comments is a two-dimensional array grouped by comment thread for the current page; it does not automatically fetch all pages. The simple style returns a simple semi-plain-text format, and the richtext style returns native ContentBlock.

<a id="注意事项"></a>
## Notes

- Entity-level comments have no selection; text-selection comments on Objective/KeyResult carry a selection.id.
- Comment thread grouping is only performed for comments within the current page; if the same comment thread spans a page boundary, you need to merge it yourself with adjacent pages, or use +comment-detail to get the aggregated result for the entire cycle.
- Comment threads are sorted in ascending order by the create_time of the first comment, and comments within a thread are also sorted in ascending order by create_time; if the times are the same, they are sorted in ascending order by comment ID.
- This command is a read-only operation and does not change comment status.

<a id="参考"></a>
## References

- [lark-okr](../index.md) — OKR commands, routing, and general conventions
- [OKR entity definitions](lark-okr-entities.md) — Comment, comment thread, and target types
- [okr +comment-detail](lark-okr-comment-detail.md) — Aggregate and fetch cycle comments
- [okr +cycle-detail](lark-okr-cycle-detail.md) — Get Objective and KeyResult IDs
- [okr +progress-list](lark-okr-progress-list.md) — Get Progress IDs
- [lark-shared](../../shared/index.md) — Authentication, identity, permissions, and security rules
