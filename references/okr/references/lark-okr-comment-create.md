# okr +comment-create

Create an OKR comment, or reply to an existing comment. Only the user identity is supported.

<a id="推荐命令"></a>
## Recommended Commands

```bash
# Create an entity-level comment under a cycle.
lark-cli okr +comment-create --target-type cycle --target-id 3456789012345678901 --content '{"text":"进展不错"}'

# Create a text-selection comment for the specified text in the Objective body.
lark-cli okr +comment-create --target-type objective --target-id 2345678901234567890 --content '{"text":"请补充数据"}' --selected-text '提升核心接口稳定性'

# Create a text-selection comment in the Objective body.
lark-cli okr +comment-create --target-type objective --target-id 2345678901234567890 --content '{"text":"请补充数据"}' --select-all

# Append a reply to an existing text-selection comment thread on a KeyResult.
lark-cli okr +comment-create --target-type key_result --target-id 4567890123456789012 --content '{"text":"已回复"}' --ref-comment-id 7000000000000000004

# Use a richtext file as the comment body.
lark-cli okr +comment-create --target-type progress --target-id 3456789012345678901 --style richtext --content '@comment.json'
```

```bash
# Preview the URL, parameters, and request body for creating a comment before writing.
lark-cli okr +comment-create --target-type progress --target-id 3456789012345678901 --content '{"text":"进展不错"}' --dry-run
```

<a id="常用表述"></a>
## Common Expressions

Below are some expressions commonly found in user requests:

- Global comment/cycle comment/OKR comment: refers to an entity-level comment on an OKR cycle. When the user asks to create a global comment, or to comment on the OKRs of a cycle (without specifically referring to an Objective or KeyResult), a cycle entity-level comment can be created.
- Text-selection comment: refers to a text-selection comment under an Objective/KeyResult. Note that entity-level comments cannot be created under an Objective/KeyResult (selected-text or select-all must be provided). If the user does not specifically designate the paragraph to comment on, use --select-all

<a id="参数"></a>
## Parameters

| Parameter        | Required | Default | Description                                                                                                          |
|------------------|------|---------|---------------------------------------------------------------------------------------------------------------|
| --target-type    | Yes   | —       | cycle, progress, objective, or key_result.                                                                    |
| --target-id      | Yes   | —       | Comment target ID, an int64 positive integer.                                                                                   |
| --content        | Yes   | —       | Comment body; input style: `simple` (semi-plain-text JSON, recommended) \| `richtext` (full ContentBlock JSON), supports @file paths. |
| --selected-text  | No   | —       | The complete plain text when creating a new text selection on an Objective/KeyResult.                                                                  |
| --select-all     | No   | false   | Select the full text when making a text selection on an Objective/KeyResult.                                                                          |
| --ref-comment-id | No   | —       | Reply to a Progress/Cycle comment, or attach an Objective/KeyResult comment to an existing text-selection thread.                                       |
| --style          | No   | simple  | Input/output style: simple or richtext.                                                                           |
| --user-id-type   | No   | open_id | open_id, union_id, user_id, or user_key.                                                                      |
| --dry-run        | No   | —       | Preview the API call without actually executing it.                                                                                   |
| --format         | No   | json    | Output format.                                                                                                    |

<a id="评论场景参数组合"></a>
## Comment Scenario Parameter Combinations

| Scenario                           | target-type             | Must provide                                                        | Must not provide                                                |
|--------------------------------|-------------------------|---------------------------------------------------------------|-------------------------------------------------------|
| Create cycle/progress entity-level comment        | cycle or progress       | `--content`                                                   | `--selected-text`, `--select-all`, `--ref-comment-id` |
| Reply to an existing cycle/progress comment          | cycle or progress       | `--content`, `--ref-comment-id`                               | `--selected-text`, `--select-all`                     |
| Create Objective/KR text-selection comment     | objective or key_result | `--content`, and choose one of `--selected-text` / `--select-all` | `--ref-comment-id`                                    |
| Append to an Objective/KR text-selection comment thread | objective or key_result | `--content`, `--ref-comment-id`                               | `--selected-text`, `--select-all`                     |

<a id="工作流程"></a>
## Workflow

1. Determine the comment target: use [+cycle-detail](lark-okr-cycle-detail.md) to get the Objective/KeyResult ID, use [+progress-list](lark-okr-progress-list.md) to get the Progress ID; when a comment thread already exists, use [+comment-list](lark-okr-comment-list.md) or [+comment-get](lark-okr-comment-get.md) to get the comment-id.
2. Choose the comment form based on target-type:
   - cycle/progress: do not provide selected-text or select-all; provide ref-comment-id when a reply is needed.
   - objective/key_result: choose exactly one of selected-text, select-all, and ref-comment-id; selected-text and select-all are mutually exclusive, and both are also mutually exclusive with ref-comment-id.
3. Prepare content: content is required by the business. It is usually recommended to use the simple format. When precise control over the position of an @user is needed, the richtext format can be used; see [ContentBlock Format](lark-okr-contentblock.md)
4. Execute the command; before actually writing, you can first use --dry-run to check the URL, query, and body.
5. When creating (rather than replying to) an Objective/KeyResult text-selection comment, if the user does not specify the exact position of the comment, select-all can usually be used instead of specifying selected-text yourself, unless the user's request explicitly states a specific paragraph.
   - If selected-text is needed to precisely select a text-selection range, only a contiguous plain-text fragment that actually exists in the body may be provided; do not include or span mention placeholders, otherwise the specific content cannot be matched.
   - selected-text selects the first match of the corresponding text. If selected-text does not match any content, it falls back to selecting the full text.

<a id="输出"></a>
## Output

On successful creation, returns JSON:

```json
{
  "comment_id": "7000000000000000004",
  "selection_id": "8000000000000000002"
}
```

- comment_id is the new comment ID.
- selection_id is returned only when creating a text-selection comment, and is used to identify the comment thread.
- The create API does not directly return the complete Comment; when details are needed, use [+comment-get](lark-okr-comment-get.md).

<a id="注意事项"></a>
## Notes

- The ref-comment-id of an Objective/KeyResult is only used to locate an existing text-selection thread; it does not establish a reference relationship in the ref_comment_id field of the new comment.
- `--ref-comment-id` must be passed the `id` of the comment entity itself, and must not be passed the `selection.id`. `selection.id` is only used to identify the same text-selection comment thread; if you want to reply to a text-selection thread, you should first find the `id` of any Comment in that thread from +comment-list or +comment-detail, then pass this `id` to `--ref-comment-id`.
- Progress/Cycle are entity-level comments; the ref-comment-id of a Progress establishes a reference relationship between ordinary comments.
- The content of a comment does not support the docs/images fields; it is recommended to fill it in using the simple format

<a id="参考"></a>
## References

- [lark-okr](../index.md) — OKR commands, routing, and general conventions
- [OKR Entity Definitions](lark-okr-entities.md) — Comment, comment threads, and target types
- [ContentBlock Format](lark-okr-contentblock.md) — simple/richtext input formats
- [okr +comment-list](lark-okr-comment-list.md) — query existing comments and selection.id
- [okr +comment-get](lark-okr-comment-get.md) — get comment details
- [okr +comment-solve / +comment-reopen](lark-okr-comment-solve-reopen.md) — manage comment status
- [lark-shared](../../shared/index.md) — authentication, identity, permissions, and security rules
