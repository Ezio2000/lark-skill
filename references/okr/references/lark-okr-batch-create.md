# okr +batch-create


Batch create OKR Objectives and Key Results.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Batch create 2 Objectives, each with 2 KRs.
lark-cli okr +batch-create \
  --cycle-id 7000000000000000001 \
  --input '[{"text":"提升产品用户体验","mention":["ou_xxxxxxxx"],"notes":"重点关注核心路径体验","krs":[{"text":"页面加载速度提升 50%","mention":["ou_yyyyyyyy"]},{"text":"用户满意度达到 4.8 分"}]},{"text":"拓展新市场份额","krs":[{"text":"新增 10 个城市覆盖"},{"text":"市场份额提升至 25%"}]}]' \
  --as user

# Read input from a file
lark-cli okr +batch-create \
  --cycle-id 7000000000000000001 \
  --input @okr_batch.json \
  --as user

# Preview the API call (Dry-run)
lark-cli okr +batch-create \
  --cycle-id 7000000000000000001 \
  --input @okr_batch.json \
  --dry-run \
  --as user
```
- mention is an optional parameter; do not pass it when you do not need to use "@" to mention other users.
  - The passed mention parameter will be added after the text in the form of @the corresponding user.
- The Objective's notes / notes_mention are optional parameters, used to create objective notes; KRs do not support notes.
- The Objective's category_id is an optional parameter; you can also use `--category-id` to specify a default category for all Objectives that do not have an explicit category set.

<a id="参数"></a>
## Parameters

| Parameter               | Required | Default value       | Description                                                         |
|------------------|----|-----------|------------------------------------------------------------|
| `--cycle-id`     | Yes  | —         | OKR period ID (int64 type)                                        |
| `--input`        | Yes  | —         | Objective list in JSON array format. Supports `@文件路径` to read from a file or `-` to read from stdin. |
| `--category-id`  | No  | —         | Default Objective category ID. Only used for Objectives in input that do not have `category_id` set. Usually does not need to be passed; see "Category tips" below. |
| `--user-id-type` | No  | `open_id` | User ID type used in mention: `open_id` \| `union_id` \| `user_id`  |
| `--dry-run`      | No  | —         | Preview the API call without actually executing it                                            |
| `--format`       | No  | `json`    | Output format                                                       |

> **Category tips**: When the user explicitly requests to set an Objective category, or when creating an Objective returns `invalid parameters` and you suspect the tenant has forcibly enabled categories, you can configure the category-id field to create it. First run `lark-cli okr categories list --as user` to view available categories, then select a category ID with suitable semantics and `enabled=true` as `category-id`. Categories can be adjusted after creation; there is no need to stop and wait for user confirmation because of category selection.

<a id="输入格式"></a>
## Input format

```json
[
  {
    "text": "Objective 内容",
    "mention": ["ou_xxxxxxxx", "ou_yyyyyyyy"],
    "notes": "Objective 备注",
    "notes_mention": ["ou_xxxxxxxx"],
    "category_id": "7249339036661170180",
    "krs": [
      {
        "text": "KR 内容",
        "mention": ["ou_zzzzzzzz"]
      }
    ]
  }
]
```

Field descriptions:

- `text`: Objective or KR content, required.
- `mention`: User mention appended after the content, optional.
- `notes`: Objective note text, optional, supported only for Objectives.
- `notes_mention`: User mention appended after the Objective note, optional, meaningful only when `notes` exists.
- `category_id`: Objective category ID, optional; overrides the command-level `--category-id`.
- `krs`: List of KRs to create under the current Objective, optional.

<a id="工作流程"></a>
## Workflow

1. Use `+cycle-list` to get available OKR period IDs
2. Construct the `--input` JSON array, containing the Objectives and KRs to create
3. Execute `lark-cli okr +batch-create --cycle-id <id> --input '...'`

<a id="输出"></a>
## Output

Returns JSON on success:

```json
{
  "ok": true,
  "data": {
    "created": [
      {
        "objective_id": "7000000000000000002",
        "krs": ["7000000000000000003", "7000000000000000004"]
      },
      {
        "objective_id": "7000000000000000005",
        "krs": ["7000000000000000006"]
      }
    ]
  }
}
```

<a id="参考"></a>
## References

- [OKR business entities](lark-okr-entities.md) -- OKR entity structure definition
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
