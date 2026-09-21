
# drive +create-shortcut


Create a shortcut for an existing Drive file in a target folder.

<a id="命令"></a>
## Command

```bash
# Create a shortcut for a regular file
lark-cli drive +create-shortcut \
  --folder-token <TARGET_FOLDER_TOKEN> \
  --file-token <FILE_TOKEN> \
  --type file

# Create a shortcut for a new version document
lark-cli drive +create-shortcut \
  --folder-token <TARGET_FOLDER_TOKEN> \
  --file-token <DOCX_TOKEN> \
  --type docx

# Create a shortcut for a spreadsheet
lark-cli drive +create-shortcut \
  --folder-token <TARGET_FOLDER_TOKEN> \
  --file-token <SHEET_TOKEN> \
  --type sheet

# Only preview the request to be made, without actually executing it
lark-cli drive +create-shortcut \
  --folder-token <TARGET_FOLDER_TOKEN> \
  --file-token <DOCX_TOKEN> \
  --type docx \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--folder-token` | Yes | Target parent folder token |
| `--file-token` | Yes | Source file token, representing the original file being referenced |
| `--type` | Yes | Source file type, recommended values: `file`, `docx`, `doc`, `sheet`, `bitable`, `mindnote`, `slides` |

<a id="输入规则"></a>
## Input Rules

- The minimum input for this shortcut is `--folder-token` + `--file-token` + `--type`
- The CLI layer assembles `--file-token` and `--type` into the `refer_entity` required by the underlying API
- `--file-token` must be a Drive file token; do not pass a wiki node token directly
- If the source is a `/wiki/...` link, you must first follow the wiki resolution process in [`lark-drive`](../index.md) to obtain the real `obj_token`, then create the shortcut
- The target location must be a cloud space (cloud drive/cloud storage) folder; this shortcut is not "copying file content", but "mounting a reference entry in another folder"

<a id="类型说明"></a>
## Type Descriptions

| Type | Description |
|------|------|
| `file` | Regular file |
| `docx` | New version cloud document |
| `doc` | Legacy cloud document |
| `sheet` | Spreadsheet |
| `bitable` | Base |
| `mindnote` | Mind note |
| `slides` | Slides |

<a id="行为说明"></a>
## Behavior Description

- On success, it calls `POST /open-apis/drive/v1/files/create_shortcut`
- This shortcut inherits common capabilities and can be used with `--as user|bot|auto`, `--format`, `--jq`, `--dry-run`
- `--dry-run` only outputs the request method, path, identity, and request body preview; it does not actually create the shortcut
- This is a write operation; before executing, confirm that both the target folder and source file are correct

<a id="限制"></a>
## Limits

- This API does not support concurrent calls
- The call frequency limit is 5 QPS, and 10000 times/day
- Creating shortcuts across tenants or across regions is not supported
- Creating shortcuts across brands is not supported
- If the number of single-level mounts in the target parent folder exceeds the limit, `1062507` is returned

<a id="权限要求"></a>
## Permission Requirements

- The current calling identity needs to be able to access the source file
- The current calling identity needs to have edit permission on the target folder
- If permissions are insufficient, a common symptom is `1061004 forbidden`

<a id="常见错误"></a>
## Common Errors

| Error Code / Error Message | Cause | Suggested Handling |
|------|------|------|
| `1061002 params error` | Missing required parameter, or the combination of `--file-token` / `--type` cannot form valid source file information | Check whether `--file-token` and `--type` are complete and match; if `--folder-token` was explicitly passed, then confirm its value is valid |
| `1061003 not found` | The source file or target folder does not exist | Reconfirm whether the token is correct and whether the resource has been deleted |
| `1061004 forbidden` | No access permission to the source file, or no edit permission on the target folder | Switch to an identity with permissions, or first grant document / folder permissions |
| `1061005 auth failed` | Incorrect identity type or access token | Check the identity used by `--as` and the current login state |
| `1061007 file has been delete` | The source file has been deleted | Confirm the original file still exists, then execute again |
| `1062507 parent node out of sibling num` | The number of single-level mounts in the target folder exceeds the upper limit | Clean up the target directory, or switch to another parent folder |
| `1061045 resource contention occurred, please retry` | Internal platform resource contention | Retry later; do not make concurrent repeated calls |
| `1064510 cross tenant and unit not support` | Cross-tenant or cross-region request | Switch to operating within the same tenant and same region |
| `1064511 cross brand not support` | Cross-brand request | Switch to operating within the same brand environment |

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for cloud space (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
