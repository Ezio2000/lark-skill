# okr +progress-delete


Delete an OKR progress record by ID. This is a high-risk operation and cannot be recovered after deletion.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Delete the progress record with the specified ID
lark-cli okr +progress-delete --progress-id 1234567890123456789

# Preview the API call without actually executing it
lark-cli okr +progress-delete --progress-id 1234567890123456789 --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter              | Required | Default    | Description                    |
|-----------------|----|--------|-----------------------|
| `--progress-id` | Yes  | —      | Progress record ID (int64 type, positive integer) |
| `--dry-run`     | No  | —      | Preview the API call without actually executing it.      |
| `--format`      | No  | `json` | Output format.                 |

<a id="工作流程"></a>
## Workflow

1. Use `+progress-get` to confirm the ID and content of the progress record to be deleted.
2. Execute `lark-cli okr +progress-delete --progress-id "1234567890123456789"`.
3. Report the result: the deleted progress record ID.

> **Note**: This operation cannot be recovered. It is recommended to first use `+progress-get` to confirm the record content before deleting.

<a id="输出"></a>
## Output

Returns JSON:

```json
{
  "deleted": true,
  "progress_id": "1234567890123456789"
}
```

<a id="参考"></a>
## References

- [lark-okr](../index.md) -- all OKR commands (shortcuts and API interfaces)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
