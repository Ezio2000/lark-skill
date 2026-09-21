# okr +patch


Partially update the content, notes, score, or deadline fields of an OKR Objective or Key Result. Supports incremental updates; only provide the fields you want to modify.

<a id="推荐命令"></a>
## Recommended Commands

```bash
# Update the Objective's content (default simple style, semi-plain-text format)
lark-cli okr +patch \
  --level objective \
  --target-id 1234567890123456789 \
  --content '{"text":"更新后的目标内容","mention":["ou_123"]}'

# Update the Key Result's score (one decimal place, 0.0-1.0)
lark-cli okr +patch \
  --level key-result \
  --target-id 2345678901234567890 \
  --score 0.7

# Update multiple fields of the Objective at once (richtext style, full ContentBlock format)
lark-cli okr +patch \
  --level objective \
  --target-id 1234567890123456789 \
  --style richtext \
  --content '{"blocks":[{"block_element_type":"paragraph","paragraph":{"elements":[{"paragraph_element_type":"textRun","text_run":{"text":"更新后的目标内容"}}]}}]}' \
  --notes '{"blocks":[{"block_element_type":"paragraph","paragraph":{"elements":[{"paragraph_element_type":"textRun","text_run":{"text":"更新后的备注"}}]}}]}' \
  --score 0.5 \
  --deadline 1735776000000

# Preview the API call without actually executing it
lark-cli okr +patch \
  --level objective \
  --target-id 1234567890123456789 \
  --content '{"text":"测试更新"}' \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter             | Required | Default       | Description                                                                                                                                   |
|----------------|----|-----------|--------------------------------------------------------------------------------------------------------------------------------------|
| `--level`      | Yes  | —         | Update level: `objective` (Objective) \| `key-result` (Key Result)                                                                                    |
| `--target-id`  | Yes  | —         | Objective ID or Key Result ID (int64 type, positive integer)                                                                                                         |
| `--style`      | No  | `simple`  | Input style: `simple` (semi-plain-text JSON, recommended) \| `richtext` (full ContentBlock JSON). Please refer to [ContentBlock Format](lark-okr-contentblock.md) to learn about the two formats.          |
| `--content`    | No¹ | —         | Content. Format specified according to `--style`. Supports `@文件路径` to read from a file.                                                                                                |
| `--notes`      | No¹ | —         | Notes (only supported when `--level=objective`). Format specified according to `--style`. Supports `@文件路径` to read from a file.                                                                           |
| `--score`      | No¹ | —         | Score value, between 0-1, at most one decimal place (e.g., 0.5, 1.0).                                                                                                            |
| `--deadline`   | No¹ | —         | Deadline, millisecond-level timestamp (e.g., 1735776000000).                                                                                                      |
| `--user-id-type` | No  | `open_id` | User ID type: `open_id` \| `union_id` \| `user_id`                                                                                        |
| `--dry-run`    | No  | —         | Preview the API call without actually executing it.                                                                                                                     |
| `--format`     | No  | `json`    | Output format.                                                                                                                                |

> ¹ At least one of `--content`, `--notes`, `--score`, `--deadline` must be provided.

<a id="工作流程"></a>
## Workflow

1. Use `+cycle-list` and `+cycle-detail` to obtain the Objective or Key Result ID.
2. Determine the fields to update:
   - **content/notes**: Construct the content
     - **Recommended**: Use `simple` style (default), construct SemiPlainContent JSON: `{"text":"内容","mention":["ou_xxx"]}`
     - For complex formats: Use `richtext` style, construct ContentBlock JSON. Please refer to [ContentBlock Format](lark-okr-contentblock.md).
   - **score**: A number between 0-1, at most one decimal place (e.g., 0.3, 0.7, 1.0)
   - **deadline**: Millisecond-level timestamp
3. Execute `lark-cli okr +patch --level objective --target-id "..." --content "..."`.
4. Report the result: the updated level, Objective ID, and which fields were updated.

<a id="输出"></a>
## Output

Returns JSON:

```json
{
  "level": "objective",
  "target_id": "1234567890123456789",
  "patched": {
    "content": true,
    "notes": true,
    "score": true,
    "deadline": true
  }
}
```

Each field in the `patched` object indicates whether that field was updated.

<a id="注意事项"></a>
## Notes

- **`--notes` only applies to Objectives**: Key Results (key-result) do not support the notes field; using it will cause an error.
- **score format**: Must be between 0-1, with at most one decimal place (e.g., 0.5 is correct, 0.51 is incorrect).
- **Strict validation**: The input format is strictly validated according to the `--style` value and is not auto-detected. When using ContentBlock JSON, you must specify `--style richtext`.
- **simple style input limitations**: simple style input does not support the `docs` and `images` fields. If you need to include documents or images, use `richtext` style.

<a id="关于-1001001-错误"></a>
## About the 1001001 Error

Sometimes, when you are modifying the score of an Objective or Key Result, +patch returns a 1001001 error (invalid parameters) even if the input parameters are completely correct.
This may be because the score feature for Objectives/Key Results is disabled in the user's tenant settings, or manual calculation of Objective scores is disabled. In this case, you can first remove the --score parameter and try again, and confirm with the user whether the corresponding feature is enabled.

<a id="参考"></a>
## References

- [lark-okr](../index.md) -- All OKR commands (shortcuts and API interfaces)
- [ContentBlock Format](lark-okr-contentblock.md) -- The rich text format used by content/notes
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
