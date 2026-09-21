<a id="okr-对齐关系管理"></a>
# OKR Alignment Management


Manage alignment relationships between OKR objectives, including querying, creating, and deleting alignments.

<a id="对齐关系说明"></a>
## Alignment Relationship Description

An OKR alignment relationship represents an association between two objectives:
- **aligning**: Objective A aligns to Objective B, meaning the completion of A contributes to the completion of B
- **aligned**: Objective B is aligned by Objective A

Each alignment relationship has a unique `alignment_id`, used for deletion operations.

---

<a id="一查询对齐关系"></a>
## 1. Query Alignment Relationships

<a id="命令"></a>
### Command

```bash
lark-cli okr objective.alignments list --objective-id "<目标ID>" [flags]
```

<a id="常用示例"></a>
### Common Examples

```bash
# Get all alignment relationships of an objective (including both aligning and aligned)
lark-cli okr objective.alignments list \
  --objective-id "7652569715131075772"

# Query only the relationships where this objective actively aligns to others
lark-cli okr objective.alignments list \
  --objective-id "7652569715131075772" \
  --align-type "aligning"

# Query only the relationships where others align to this objective
lark-cli okr objective.alignments list \
  --objective-id "7652569715131075772" \
  --align-type "aligned"

# Automatically paginate to get all data
lark-cli okr objective.alignments list \
  --objective-id "7652569715131075772" \
  --page-all
```

<a id="参数"></a>
### Parameters

| Parameter                   | Required | Default            | Description                                                                 |
|----------------------|----|----------------|--------------------------------------------------------------------|
| `--objective-id`     | Yes  | —              | Objective ID                                                              |
| `--align-type`       | No  | —              | Alignment type: `aligning` (this objective aligns to others)\| `aligned` (others align to this objective). Leave blank to return all. |
| `--user-id-type`     | No  | `open_id`      | User ID type: `open_id` \| `union_id` \| `user_id`                    |
| `--page-size`        | No  | `10`           | Page size, maximum 100                                                    |
| `--page-all`         | No  | —              | Automatically paginate to get all data                                                    |

<a id="返回字段说明"></a>
### Returned Field Description

- `items[].id`: Alignment relationship ID (required for deletion)
- `items[].from_entity_id`: ID of the objective that initiates the alignment
- `items[].to_entity_id`: ID of the objective being aligned
- `items[].from_owner` / `to_owner`: Owner information of both parties

---

<a id="二创建对齐关系"></a>
## 2. Create Alignment Relationship

<a id="命令-1"></a>
### Command

```bash
lark-cli okr objective.alignments create --objective-id "<发起对齐的目标ID>" --data '<JSON>'
```

<a id="常用示例-1"></a>
### Common Examples

```bash
# Create an alignment relationship: Objective 7652569715131075772 aligns to Objective 7652569715131075773
lark-cli okr objective.alignments create \
  --objective-id "7652569715131075772" \
  --data '{"to_entity_id":"7652569715131075773","to_entity_type":2}'

# Read request body from file
lark-cli okr objective.alignments create \
  --objective-id "7652569715131075772" \
  --data @alignment.json
```

<a id="参数-1"></a>
### Parameters

| Parameter               | Required | Description                                                                 |
|------------------|----|--------------------------------------------------------------------|
| `--objective-id` | Yes  | ID of the objective that initiates the alignment ("my" objective)                                          |
| `--data`         | Yes  | JSON request body, format shown below. Supports `@文件路径` to read from file.                           |

<a id="请求体格式"></a>
### Request Body Format

```json
{
  "to_entity_id": "7652569715131075773",  // Aligned objective ID
  "to_entity_type": 2                     // Fixed value 2, indicating the objective type
}
```

<a id="对齐规则"></a>
### Alignment Rules

- **Self-alignment prohibited**: Cannot align to oneself
- **Period time overlap**: The time ranges of the periods containing the two objectives must overlap
- **Permission requirement**: Edit permission is required for the objective that initiates the alignment

<a id="返回"></a>
### Return

On success, returns `alignment_id`. Save it for subsequent deletion.

---

<a id="三删除对齐关系"></a>
## 3. Delete Alignment Relationship

<a id="命令-2"></a>
### Command

```bash
lark-cli okr alignments delete --alignment-id "<对齐关系ID>"
```

<a id="常用示例-2"></a>
### Common Examples

```bash
# Delete the specified alignment relationship
lark-cli okr alignments delete \
  --alignment-id "7652569715131075780"
```

<a id="参数-2"></a>
### Parameters

| Parameter               | Required | Description                                   |
|------------------|----|--------------------------------------|
| `--alignment-id` | Yes  | Alignment relationship ID (returned from list or create) |

<a id="注意事项"></a>
### Notes

- Deletion is irreversible, please operate with caution
- Edit permission is required for the associated objectives

---

<a id="完整工作流示例"></a>
## Complete Workflow Example

<a id="场景将目标-a-对齐到目标-b"></a>
### Scenario: Align Objective A to Objective B

1. **Query existing alignment relationships** (confirm whether one already exists)
   ```bash
   lark-cli okr objective.alignments list \
     --objective-id "目标A的ID" \
     --align-type "aligning"
   ```

2. **Create alignment relationship**
   ```bash
   lark-cli okr objective.alignments create \
     --objective-id "目标A的ID" \
     --data '{"to_entity_id":"目标B的ID","to_entity_type":2}'
   ```

3. **Verify alignment result**
   ```bash
   lark-cli okr objective.alignments list \
     --objective-id "目标A的ID" \
     --align-type "aligning"
   ```

4. **(If needed) Delete alignment relationship**
   ```bash
   lark-cli okr alignments delete \
     --alignment-id "从步骤1返回的alignment_id"
   ```

<a id="参考"></a>
## References

- [lark-okr](../index.md) -- All OKR commands
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
