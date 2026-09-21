
# drive +delete


Delete a file or folder in Drive (cloud drive/cloud storage). After deletion, the resource will be moved to the trash.

> [!CAUTION]
> This is a **high-risk write operation**. The CLI layer requires explicitly passing `--yes`; if the user has already explicitly requested deletion and the target is clear, execute directly and include `--yes`.
> "Target is clear" means the user has provided a specific URL/token that can be resolved to `file-token` + `type`, or has confirmed deletion item by item or in bulk for a resolvable resource list you just listed. Candidates found by searching with descriptions such as "useless", "temporary", "suspected duplicates", "all old files" are targets pending confirmation; for such requests, first list the candidates, explain the filtering criteria and scope of impact, then stop and wait for confirmation.

<a id="删除前门槛"></a>
## Pre-deletion threshold

Before executing `drive +delete --yes`, both of the following must be satisfied:

| Condition | Executable signal |
|------|------------|
| Specific target | A single URL/token that can be resolved to `file-token` + `type`, or a resource list that the user has confirmed and that can be resolved |
| Execution confirmation | The user has explicitly authorized deletion of these specific targets in the current session |

If either condition is missing, use `drive +search`, `drive +inspect`, or read-only APIs to collect candidates and reply with a pending-confirmation list; heuristic rules (open time, title patterns, owner, file type, etc.) can only serve as candidate filtering criteria and cannot be escalated to deletion confirmation. When executing `drive +delete`, the resolved `--file-token` and `--type` must be used.

<a id="批量删除建议"></a>
## Batch deletion recommendations

When deleting files or folders in bulk, it is recommended to process them one by one serially; do not execute deletion commands concurrently. Concurrent deletion may trigger server-side locking or conflicts, causing some deletions to fail; such failures usually require waiting and then retrying the individual failed items.

<a id="命令"></a>
## Commands

```bash
# Delete a regular file (asynchronous operation, automatically polls task status a limited number of times)
lark-cli drive +delete \
  --file-token <FILE_TOKEN> \
  --type file \
  --yes

# Delete an online document (asynchronous operation, automatically polls task status a limited number of times)
lark-cli drive +delete \
  --file-token <DOCX_TOKEN> \
  --type docx \
  --yes

# Delete a folder (asynchronous operation, automatically polls task status a limited number of times)
lark-cli drive +delete \
  --file-token <FOLDER_TOKEN> \
  --type folder \
  --yes
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | Token of the file or folder to delete |
| `--type` | Yes | File type, possible values: `file`, `docx`, `bitable`, `doc`, `sheet`, `mindnote`, `folder`, `shortcut`, `slides` |
| `--yes` | Yes | Confirm execution of the high-risk deletion operation |

<a id="行为说明"></a>
## Behavior description

- **Deletion may require waiting**: The deletion operation may be processed asynchronously on the server side; the shortcut will automatically poll for the result a limited number of times within this command
- **Stop if already completed**: If `deleted=true` is returned and `next_command` is not returned, the deletion has completed and there is no need to call `drive +task_result` again
- **Continue checking if not completed**: If the built-in polling count is exceeded and it is still not completed, `ready=false`, `timed_out=true`, `task_id`, and `next_command` will be returned; in this case, continue querying the deletion result according to `next_command`
- **task_id is not a success condition**: `task_id` is only a credential for continued querying. When `task_id` is not present but `deleted=true` is returned, it also indicates that the deletion has completed
- **Failure handling**: If `failed=true` or `status=fail` is returned, report the deletion failure according to the error message and `task_id`; do not repeatedly delete the same resource

<a id="常见错误处理"></a>
## Common error handling

| Error code | Meaning | Suggested handling |
|--------|------|----------|
| `1061007` | File already deleted | Treat the target as unavailable; no need to retry deletion |
| `99991400` | API rate limit hit | Wait a period of time and retry; when deleting in bulk, keep it serial and reduce the frequency |
| `99991679` | Missing scope | Apply for/authorize the required scope according to `missing_scopes` and `hint` in the error, then retry |

<a id="推荐续跑方式"></a>
## Recommended way to continue

```bash
# Step 1: Delete the resource directly first
lark-cli drive +delete \
  --file-token <FILE_OR_FOLDER_TOKEN> \
  --type <TYPE> \
  --yes

# Only when ready=false / timed_out=true or next_command is returned do you need to continue checking
lark-cli drive +task_result \
  --scenario task_check \
  --task-id <TASK_ID>
```

<a id="限制"></a>
## Limitations

- This shortcut only supports files or folders in Drive (cloud drive/cloud storage); it does not support Wiki documents
- This API does not support concurrent calls
- The call rate limit is 5 QPS and 10,000 times/day

<a id="权限要求"></a>
## Permission requirements

- When deleting a file, the calling identity must satisfy one of the following:
- Be the file owner and have edit permission on the parent folder where the file is located
- Not be the file owner, but have owner or full access permission on the parent folder

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for Drive (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
