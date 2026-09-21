# okr +create


Create a single OKR Objective or Key Result. This is the preferred shortcut for single-record write scenarios; if you need to create multiple Objectives and their KRs at once, use [`+batch-create`](lark-okr-batch-create.md).

<a id="推荐命令"></a>
## Recommended Commands

```bash
# Create an Objective under the specified period (default simple style)
lark-cli okr +create \
  --level objective \
  --cycle-id 7000000000000000001 \
  --content '{"text":"提升北极星指标","mention":["ou_xxxxxxxx"]}' \
  --notes '{"text":"重点关注活跃用户和转化漏斗"}' \
  --as user

# Create a KR under an existing Objective
lark-cli okr +create \
  --level key-result \
  --objective-id 7000000000000000002 \
  --content '{"text":"季度留存率提升到 45%"}' \
  --as user

# Create an Objective using richtext style (full ContentBlock JSON)
lark-cli okr +create \
  --level objective \
  --cycle-id 7000000000000000001 \
  --style richtext \
  --content '{"blocks":[{"block_element_type":"paragraph","paragraph":{"elements":[{"paragraph_element_type":"textRun","text_run":{"text":"建立跨部门协作机制"}}]}}]}' \
  --as user

# Preview the API call without actually executing it
lark-cli okr +create \
  --level key-result \
  --objective-id 7000000000000000002 \
  --content '{"text":"完成 3 次核心流程优化"}' \
  --dry-run \
  --as user
```

<a id="参数"></a>
## Parameters

| Parameter               | Required | Default       | Description                                                                                                                 |
|------------------|----|-----------|--------------------------------------------------------------------------------------------------------------------|
| `--level`        | Yes  | —         | Creation level: `objective` (create Objective) \| `key-result` (create KR under an existing Objective)                                                                 |
| `--cycle-id`     | Conditional | —         | OKR period ID (int64 type). **Required** when `--level=objective`.                                                                 |
| `--objective-id` | Conditional | —         | Objective ID (int64 type). **Required** when `--level=key-result`.                                                             |
| `--style`        | No  | `simple`  | Content input style: `simple` (semi-plain-text JSON, recommended) \| `richtext` (full ContentBlock JSON). See [ContentBlock format](lark-okr-contentblock.md). |
| `--content`      | Yes  | —         | Content. Format specified according to `--style`. Supports `@文件路径` to read from a file or `-` to read from stdin.                                                             |
| `--notes`        | No  | —         | Objective notes, only supported by `--level=objective`. Format specified according to `--style`, supports `@文件路径` or `-` to read from stdin.                               |
| `--category-id`  | No  | —         | Objective category ID, only supported by `--level=objective`. Usually does not need to be passed; see "Category Tips" below.                                                        |
| `--user-id-type` | No  | `open_id` | User ID type: `open_id` \| `union_id` \| `user_id`. Affects how user IDs in mentions are interpreted.                                             |
| `--dry-run`      | No  | —         | Preview the API call without actually executing it.                                                                                                   |
| `--format`       | No  | `json`    | Output format.                                                                                                              |

> **Category Tips**: When the user explicitly requests setting an Objective category, or when creating an Objective returns `invalid parameters` and you suspect the tenant has category enforcement enabled, you can configure the --category-id parameter to create it. First run `lark-cli okr categories list --as user` to view available categories, then choose a category ID that is semantically appropriate and has `enabled=true` as `--category-id`. The category can be adjusted after creation; there is no need to stop and wait for user confirmation over the category choice.

<a id="输入格式"></a>
## Input Format

<a id="--style-simple默认"></a>
### `--style simple` (Default)

It is recommended to use the `simple` style for most creation scenarios. Both `--content` and `--notes` use `SemiPlainContent` JSON:

```json
{
  "text": "提升北极星指标",
  "mention": ["ou_xxxxxxxx"]
}
```

Rules:

- `text` is required and cannot be a blank string
- `mention` is optional; if passed, each user ID in the array cannot be an empty string
- `--notes` only applies to Objectives; passing `--notes` when creating a KR will cause an error
- Only one flag in the same command can use `-` to read from stdin; if `--content -`, use inline JSON or `@文件路径` for `--notes`

### `--style richtext`

Use the `richtext` style when you need precise control over paragraph structure, need to insert document links, or need to use the full rich-text block structure:

```json
{
  "blocks": [
    {
      "block_element_type": "paragraph",
      "paragraph": {
        "elements": [
          {
            "paragraph_element_type": "textRun",
            "text_run": {
              "text": "建立跨部门协作机制"
            }
          }
        ]
      }
    }
  ]
}
```

Rules:

- `blocks` requires at least one non-empty paragraph or image block
- You cannot pass an empty `blocks`, nor content containing only empty paragraph elements
- For more structural details, see [ContentBlock rich-text format](lark-okr-contentblock.md)

<a id="工作流程"></a>
## Workflow

1. If creating an Objective, first use `+cycle-list` to get the `cycle_id` of the target period.
2. If adding a KR to an existing Objective, first obtain the `objective_id` via `+cycle-detail` or another OKR query command.
3. Choose the input style:
   - **Recommended**: `simple`, suitable for plain text and mentions.
   - When complex rich text is needed: `richtext`.
4. Execute `lark-cli okr +create ...`.
5. Report the result:
   - When creating an Objective, return the new `objective_id`
   - When creating a KR, return the new `key_result_id`, along with the parent `objective_id`

<a id="dry-run-对应接口"></a>
## Dry-run Corresponding Interfaces

- `--level=objective`:
  - `POST /open-apis/okr/v2/cycles/:cycle_id/objectives`
- `--level=key-result`:
  - `POST /open-apis/okr/v2/objectives/:objective_id/key_results`

<a id="输出"></a>
## Output

<a id="创建-objective-成功"></a>
### Objective Created Successfully

```json
{
  "level": "objective",
  "objective_id": "7000000000000000002"
}
```

<a id="创建-kr-成功"></a>
### KR Created Successfully

```json
{
  "level": "key-result",
  "objective_id": "7000000000000000002",
  "key_result_id": "7000000000000000003"
}
```

<a id="常见错误与处理"></a>
## Common Errors and Handling

- `--level=objective` but `--cycle-id` was not passed
  - Provide a valid period ID
- `--level=key-result` but `--objective-id` was not passed
  - Provide the ID of an existing Objective
- `--content` is empty, is not valid JSON, or has an empty content structure
  - Fix the input according to the format corresponding to `--style`
- Passed `docs` or `images` in `simple` style
  - Switch to `--style richtext`, or remove these fields

<a id="何时用-create何时用-batch-create"></a>
## When to Use +create vs. +batch-create

| Command | Applicable Scenario |
|------|----------|
| `+create` | Create a single Objective, or add a single KR to an existing Objective |
| `+batch-create` | Create multiple Objectives at once, and optionally create multiple KRs for each Objective at the same time |

<a id="参考"></a>
## References

- [lark-okr](../index.md) -- all OKR commands
- [OKR business entities](lark-okr-entities.md) -- basic concepts such as Objective, KR, and period
- [ContentBlock format](lark-okr-contentblock.md) -- another input style for the content/notes fields, supporting the full rich-text format
- [okr +batch-create](lark-okr-batch-create.md) -- batch create multiple Objectives / KRs
- [lark-shared](../../shared/index.md) -- authentication and global parameters
