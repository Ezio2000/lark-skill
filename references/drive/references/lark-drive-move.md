
# drive +move


Move a file or folder to another location in the user's cloud space (Drive/cloud storage).

<a id="与-wiki-移动-shortcut-的区别"></a>
## Difference from Wiki move shortcuts

- `drive +move` only handles position adjustments **within the Drive folder tree**, and the target location is represented by `--folder-token`
- `wiki +move` handles the **Wiki knowledge space / page hierarchy**: either moving an existing Wiki node, or migrating a Drive document into Wiki
- `wiki +move-to-drive` moves an **existing Wiki node out of the knowledge base**, placing it into a Drive folder or the "My Space" root directory
- If the user says "move to a certain folder" or "move to my space root directory", you also need to determine the source object: when the source object is already in Drive, use `drive +move`; when the source object is a Wiki node, use `wiki +move-to-drive`
- If the user says "move under a certain knowledge base / page" or "migrate into Wiki / knowledge space", use `wiki +move`
- If the user says "move to my document library / my knowledge base / personal knowledge base / my_library", do not use `drive +move`; handle it as a Wiki target first
- `我的文档库` is not the Drive root folder, nor is it the default destination when `--folder-token` is omitted
- `drive +move` does not support Wiki documents; for Wiki nodes to Drive, use `wiki +move-to-drive`, and when the target is Wiki, use `wiki +move`

<a id="不要误用到-我的文档库"></a>
## Do not mistakenly use `我的文档库`

The following phrasings should **not** trigger `drive +move`:

- `移动到我的文档库`
- `放到我的知识库`
- `迁入个人知识库`
- `move to My Document Library`

These targets should all go through the Wiki resolution flow first:

```bash
lark-cli wiki spaces get --params '{"space_id":"my_library"}'
```

After obtaining the real `space_id`, switch to `wiki +move`. Do not treat `drive +move` as an approximate target for "my document library" just because it can omit `--folder-token`.

<a id="命令"></a>
## Command

```bash
# Move a file to the specified folder
lark-cli drive +move \
  --file-token <FILE_TOKEN> \
  --type file \
  --folder-token <TARGET_FOLDER_TOKEN>

# Move a document to the specified folder
lark-cli drive +move \
  --file-token <DOCX_TOKEN> \
  --type docx \
  --folder-token <TARGET_FOLDER_TOKEN>

# Move a folder (asynchronous operation, automatically polls the task status a limited number of times)
lark-cli drive +move \
  --file-token <FOLDER_TOKEN> \
  --type folder \
  --folder-token <TARGET_FOLDER_TOKEN>

# Move to the root folder (do not specify --folder-token)
lark-cli drive +move \
  --file-token <FILE_TOKEN> \
  --type file
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | Token of the file or folder to move |
| `--type` | Yes | File type, possible values: `file` (regular file), `docx` (new version document), `bitable` (Base), `doc` (legacy document), `sheet` (Sheets), `mindnote` (mind note), `folder` (folder), `slides` (Slides) |
| `--folder-token` | No | Target folder token; if not specified, move to the root folder |

<a id="文件类型说明"></a>
## File type descriptions

| Type | Description |
|------|------|
| `file` | Regular file |
| `docx` | New version cloud document |
| `doc` | Legacy cloud document |
| `sheet` | Sheets |
| `bitable` | Base |
| `mindnote` | Mind note |
| `slides` | Slides |
| `folder` | Folder (moving a folder is an asynchronous operation) |

<a id="行为说明"></a>
## Behavior description

- **Regular file move**: synchronous operation, completes immediately
- **Folder move**: asynchronous operation; the API returns `task_id`, and the shortcut first performs limited polling; if it completes within the polling window, it directly returns a success result
- **Polling timeout is not a failure**: folder move polls at most 30 times with a 2-second interval each time; if the task is still not complete when polling ends, it returns `task_id`, `status`, `ready=false`, `timed_out=true`, and `next_command`
- **Continue querying**: when you see `next_command`, switch to `lark-cli drive +task_result --scenario task_check --task-id <TASK_ID>` to continue querying
- **Target folder**: if `--folder-token` is not specified, the file will be moved to the user's root folder ("My Space")
- **Do not confuse product concepts**: the "root folder / My Space" here belongs only to the Drive folder tree and is not equal to Wiki's "My Document Library"
- **Permission requirements**: manage permission on the file being moved, edit permission on the location of the file being moved, and edit permission on the target location

<a id="推荐续跑方式"></a>
## Recommended way to continue running

```bash
# Step 1: First move the folder directly
lark-cli drive +move \
  --file-token <FOLDER_TOKEN> \
  --type folder \
  --folder-token <TARGET_FOLDER_TOKEN>

# If it returns ready=false / timed_out=true, continue querying
lark-cli drive +task_result \
  --scenario task_check \
  --task-id <TASK_ID>
```

<a id="限制"></a>
## Limitations

- The file being moved does not support wiki documents
- This API does not support concurrent calls
- The call frequency limit is 5 QPS and 10000 times/day

> [!CAUTION]
> This is a **write operation** -- you must confirm the user's intent before executing.

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for cloud space (Drive/cloud storage)
- [wiki +move-to-drive](../../wiki/references/lark-wiki-move-to-drive.md) -- move a Wiki node out of the knowledge base and into Drive
- [lark-shared](../../shared/index.md) -- authentication and global parameters
