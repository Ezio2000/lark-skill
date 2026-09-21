<a id="drive-create-folder创建云空间云盘云存储文件夹"></a>
# drive +create-folder (create a cloud space/cloud drive/cloud storage folder)


Create a new folder in Feishu cloud space (cloud drive/cloud storage). This shortcut wraps the native `drive files create_folder` in a layer that is better suited for everyday use: `--folder-token` can be omitted, in which case the folder is created in the caller's root directory; if `--as bot` is used, after successful creation the CLI will attempt to automatically grant the new folder's manageable permission to the current CLI user.

<a id="命令"></a>
## Command

```bash
# Create a folder in the root directory
lark-cli drive +create-folder \
  --name "周报归档"

# Create a subfolder under the specified parent folder
lark-cli drive +create-folder \
  --folder-token <PARENT_FOLDER_TOKEN> \
  --name "2026-W16"

# Preview the underlying call
lark-cli drive +create-folder \
  --folder-token <PARENT_FOLDER_TOKEN> \
  --name "分析资料" \
  --dry-run
```

<a id="返回值"></a>
## Return value

On success, a JSON object is returned. Common fields include:

- `folder_token`: the new folder token, which can be used directly in subsequent commands such as `drive +move` and `drive +upload`
- `url`: the new folder link (if returned by the API)
- `name`: the folder name
- `parent_folder_token`: the parent folder token; an empty string means it was created in the root directory
- `permission_grant` (optional): returned only for `--as bot`, indicating whether manageable permission has been automatically granted to the current CLI user

> [!IMPORTANT]
> If the folder is **created with an app identity (bot)**, such as `lark-cli drive +create-folder --as bot`, after successful creation the CLI will **attempt to automatically grant the current CLI user `full_access` (manageable permission) for that folder**.
>
> When created with an app identity, the result additionally returns the `permission_grant` field, which explicitly states the authorization result:
> - `status = granted`: the current CLI user has obtained manageable permission for the folder
> - `status = skipped`: there is no available current user `open_id` locally, so authorization will not be performed automatically; you can prompt the user to complete `lark-cli auth login` first, then have the AI / agent continue to use the app identity (bot) to grant the current user permission
> - `status = failed`: the folder was created successfully, but automatically authorizing the user failed; the failure reason is included, and you are prompted to retry later or continue handling the folder using the bot identity
>
> `permission_grant.perm = full_access` indicates that the resource has been granted "manageable permission".
>
> **Do not perform owner transfer on your own initiative.** Creation or import does not imply owner transfer; when the user has explicitly requested a transfer and the target has been determined, proceed with the authorization execution.

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--name` | Yes | Folder name; cannot be empty; maximum 256 bytes |
| `--folder-token` | No | Parent folder token; when omitted, the folder is created in the caller's root directory |

<a id="行为说明"></a>
## Behavior notes

- **Root directory creation**: when `--folder-token` is not passed, the shortcut explicitly passes an empty string `folder_token=""` to the API, so the backend creates it with "root directory" semantics
- **Bot automatic authorization**: only when `--as bot` will the result additionally include `permission_grant`
- **The native API is still available**: if the user explicitly requests calling by the underlying API fields, `lark-cli drive files create_folder` can still be used

<a id="推荐场景"></a>
## Recommended scenarios

- When the user says "create a new folder / directory in cloud space (cloud drive/cloud storage)", prefer using `drive +create-folder`
- When the user provides a parent folder link or token and needs to continue creating directories hierarchically under it, pass `--folder-token`
- If files will subsequently be uploaded, moved, or subdirectories created, prefer reusing the `folder_token` from the return value

> [!CAUTION]
> `drive +create-folder` is a **write operation**; the user's intent must be confirmed before execution.

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for cloud space (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
