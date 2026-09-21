# okr +comment-detail

Get all comments for Cycle, Objective, KeyResult, and Progress under a specified OKR cycle, organized by comment target and comment thread, then sorted in ascending time order. This shortcut is an aggregate query across multiple OKR APIs.

<a id="推荐命令"></a>
## Recommended Commands

```bash
# Get all comments for Cycle, Objective, KeyResult, and Progress under the specified cycle.
lark-cli okr +comment-detail --cycle-id 1234567890123456789

# Get the comment body in raw ContentBlock format.
lark-cli okr +comment-detail --cycle-id 1234567890123456789 --style richtext

# Preview the API calls of the aggregate query without actually executing them.
lark-cli okr +comment-detail --cycle-id 1234567890123456789 --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter  | Required | Default | Description                                                                                |
|------------|----------|---------|--------------------------------------------------------------------------------------------|
| --cycle-id | Yes      | —       | OKR cycle ID, int64 positive integer, can be obtained from +cycle-list.                    |
| --style    | No       | simple  | simple returns semi-plain text format, recommended when font/color information is not involved; richtext returns raw ContentBlock. |
| --dry-run  | No       | —       | Preview the aggregate query without actually executing it.                                 |
| --format   | No       | json    | Output format.                                                                             |

<a id="工作流程"></a>
## Workflow

1. Use +cycle-list to get the cycle ID; if the user has already provided a cycle ID, use it directly.
2. Execute +comment-detail --cycle-id "...". The shortcut will sequentially get the Objectives under the cycle, the KeyResults under each Objective, the Progress under each Objective/KeyResult, and the comments for the four types of objects.
3. The comment API automatically handles pagination; object reads and comment reads use bounded concurrency. If any underlying request fails, an error is returned as a whole, and no silently incomplete result is returned.
4. Comment threads are sorted in ascending order by the create_time of the first comment, and comments within a thread are also sorted in ascending order by create_time.

<a id="输出"></a>
## Output

The core structure of the returned JSON is as follows:

```json
{
  "cycle_id": "1234567890123456789",
  "comments": {
    "2345678901234567890": [
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
    ]
  },
  "style": "simple"
}
```

- The first-level key of comments is target_id; the value is an array of comment threads; each comment thread is an array of comments.
- In simple style, content is SemiPlainContent; in richtext style, content is ContentBlock.
- Comment timestamps are converted to readable date-time; selection, status, and reference fields are preserved.
- `comments` will preserve a target_id key for each target traversed in the cycle; even if the object has no comments, the corresponding value will be an empty comment thread array.

<a id="注意事项"></a>
## Notes

- This is an aggregate query, and the number of API calls depends on the number of Objectives, KeyResults, and Progress under the cycle.
- +comment-detail does not accept department-id-type; this API parameter is ignored by the shortcut.
- This command only reads comments and will not modify, resolve, or delete comments.

<a id="参考"></a>
## References

- [lark-okr](../index.md) — OKR commands, routing, and general conventions
- [OKR entity definitions](lark-okr-entities.md) — relationships among Cycle, Objective, KeyResult, Progress, and Comment
- [ContentBlock format](lark-okr-contentblock.md) — ContentBlock and SemiPlainContent formats
- [okr +cycle-detail](lark-okr-cycle-detail.md) — get Objectives and KeyResults under a cycle
- [okr +progress-list](lark-okr-progress-list.md) — get Progress under an Objective or KeyResult
- [lark-shared](../../shared/index.md) — authentication, identity, permissions, and security rules
