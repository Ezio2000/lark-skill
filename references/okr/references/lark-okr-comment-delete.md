# okr +comment-delete

Permanently delete a comment. When deleting a text-selection comment, only the specified comment is deleted; other comments under the same selection.id are not deleted.

<a id="功能简介"></a>
## Feature Overview

Delete a specific comment. This shortcut is a high-risk interface; deleted comments cannot be recovered. If you only want to temporarily end a discussion, use +comment-solve. Only the user identity is supported.

<a id="推荐命令"></a>
## Recommended Commands
```bash
# Preview the delete request without actually performing the permanent deletion.
lark-cli okr +comment-delete --comment-id 7000000000000000004 --dry-run
# After confirming the deletion target, perform the irreversible deletion operation.
lark-cli okr +comment-delete --comment-id 7000000000000000004 --yes
```


<a id="参数"></a>
## Parameters

| Parameter    | Required              | Default | Description                                                                 |
|--------------|-----------------------|---------|-----------------------------------------------------------------------------|
| --comment-id | Yes                   | —       | The ID of the comment to delete, an int64 positive integer. It is recommended to verify it first with +comment-get. |
| --yes        | Yes for actual execution | —     | Confirm the high-risk-write operation. Not required with --dry-run.          |
| --dry-run    | No                    | —       | Preview the API call without actually executing it.                          |
| --format     | No                    | json    | Output format.                                                               |

<a id="工作流程"></a>
## Workflow

1. Use [+comment-list](lark-okr-comment-list.md), [+comment-detail](lark-okr-comment-detail.md), or [+comment-get](lark-okr-comment-get.md) to locate and confirm the comment-id.
2. Determine whether deletion is truly needed: use [+comment-solve](lark-okr-comment-solve-reopen.md) to resolve a comment; deletion is only for permanently removing content.
3. First run the command with --dry-run to check the URL and comment-id.
4. Clearly explain to the user that deletion is irreversible; after obtaining confirmation, append --yes to the end of the original command and execute it.
5. Confirm the result based on deleted=true and the returned comment_id.

<a id="输出"></a>
## Output

On successful deletion, returns JSON:
```json
{
  "deleted": true,
  "comment_id": "7000000000000000004"
}
```


<a id="注意事项"></a>
## Notes

- Deletion is a single-comment-level operation; even if the comment belongs to a text-selection comment thread, other comments are not deleted along with it.
- After deletion, +comment-reopen cannot be used to restore it; to temporarily close a discussion, use +comment-solve.
- This command does not require style, because the interface does not return the Comment body.

<a id="参考"></a>
## References

- [lark-okr](../index.md) — OKR commands, routing, and general conventions
- [OKR entity definitions](lark-okr-entities.md) — Comment, comment thread, and status rules
- [okr +comment-get](lark-okr-comment-get.md) — Verify a comment before deletion
- [okr +comment-solve / +comment-reopen](lark-okr-comment-solve-reopen.md) — Temporarily resolve and restore comments
- [lark-shared](../../shared/index.md) — High-risk operation confirmation protocol
