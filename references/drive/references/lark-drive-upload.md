
# drive +upload


Upload a local file to Feishu cloud space (Drive/cloud storage). The target location can be a Drive folder or a wiki node.

<a id="快速决策"></a>
## Quick decision
- If the user wants to upload, create, read, partially patch, or overwrite-update a **native `.md` file** in Drive (not import it as a docx), switch to [`lark-markdown`](../../markdown/index.md).
- When the user is modifying/rewriting/updating an existing regular file, prefer the overwrite upload method rather than directly uploading a new file.

<a id="命令"></a>
## Command

```bash
# Upload to a Drive folder
lark-cli drive +upload --file ./report.pdf --folder-token fldbc_xxx

# Upload to a wiki node
lark-cli drive +upload --file ./report.pdf --wiki-token wikcn_xxx

# When no target is specified, upload to the caller's Drive root directory
lark-cli drive +upload --file ./report.pdf

# Customize the file name after upload
lark-cli drive +upload --file ./report.pdf --name "季度总结.pdf"

# Overwrite an existing file (overwrite in place, preserving the file_token)
lark-cli drive +upload --file ./report.pdf --file-token boxcn_existing_file

# Native commands (advanced/multipart upload): pre-upload + complete upload
lark-cli drive files upload_prepare --data '{
  "file_name": "report.pdf",
  "parent_type": "explorer",
  "parent_node": "fldbc_xxx",
  "size": 1048576,
  "file_token": "boxcn_existing_file"
}'
lark-cli drive files upload_finish --data '{
  "upload_id": "<UPLOAD_ID>",
  "block_num": 1
}'

# View the full parameter definitions
lark-cli schema drive.files.upload_prepare
```

> [!IMPORTANT]
> If the file is **newly created and uploaded as an app identity (bot)**, such as `lark-cli drive +upload --as bot`, after a successful upload the CLI will **attempt to automatically grant the current CLI user `full_access` (manageable permission) for that file**.
>
> If this call passes `--file-token`, it means this is **overwriting an existing file**, and the CLI will **not** additionally modify that file's permissions.
>
> When uploading as an app identity, the result will additionally return a `permission_grant` field that clearly states the authorization result:
> - `status = granted`: the current CLI user has obtained manageable permission for that file
> - `status = skipped`: there is no available current user `open_id` locally, so no automatic authorization will occur; you may prompt the user to complete `lark-cli auth login` first, then let the AI / agent continue using the app identity (bot) to grant the current user permission
> - `status = failed`: the file was uploaded successfully, but automatically authorizing the user failed; the failure reason will be included, and you will be prompted to retry later or continue handling the file using the bot identity
>
> `permission_grant.perm = full_access` indicates that the resource has been granted "manageable permission".
>
> **Do not perform owner transfer on your own initiative.** Creating or importing does not imply owner transfer; when the user has explicitly requested a transfer and the target has been determined, follow the authorization to execute it.

> [!TIP]
> When the underlying upload API returns a version number, the shortcut will additionally expose `version` in the result.

<a id="目标位置选择关键"></a>
## Target location selection (key)

- Upload to a Drive folder: pass `--folder-token <folder_token>`, and the shortcut will send `parent_type=explorer`
- Upload to a wiki node: pass `--wiki-token <wiki_token>`, and the shortcut will send `parent_type=wiki`
- Upload to the Drive root directory: pass neither `--folder-token` nor `--wiki-token`
- Overwrite an existing file: additionally pass `--file-token <existing_file_token>`; the shortcut will pass it through as-is to the underlying `upload_all` / `upload_prepare`, letting the backend write with overwrite semantics
- In bot mode, `--file-token` overwrite only changes the file content; it will not additionally grant the current CLI user `full_access`
- Do not pass an empty target value: `--folder-token ""` / `--wiki-token ""` will be treated as a parameter error; if you need to upload to the Drive root directory, simply omit these two parameters
- Do not pass an empty `--file-token`: if you need a new upload, simply omit this parameter; explicitly passing an empty string will cause an error
- `--folder-token` and `--wiki-token` are mutually exclusive; do not pass both
- `--wiki-token` passes a **wiki node token**, not `space_id`

Shortcut parameters:

| Parameter | Required | Description |
|------|------|------|
| `--file` | Yes | Local file path |
| `--file-token` | No | Token of an existing file; when passed, upload with "overwrite existing file" semantics |
| `--folder-token` | No | Target folder token; mutually exclusive with `--wiki-token`; defaults to the Drive root directory when omitted; explicitly passing an empty string will cause an error |
| `--wiki-token` | No | Target wiki node token; mutually exclusive with `--folder-token`; will be mapped to `parent_type=wiki`, `parent_node=<wiki_token>`; explicitly passing an empty string will cause an error |
| `--name` | No | File name after upload; defaults to the local file name |

Parameters (pre-upload `--data` JSON body):

| Field | Required | Description |
|------|------|------|
| `file_name` | Yes | File name |
| `parent_type` | Yes | Parent node type; use `"explorer"` when uploading to a folder / root directory, and `"wiki"` when uploading to a wiki node |
| `parent_node` | Yes | Parent node token; when `explorer`, pass the folder token (the root directory may be an empty string); when `wiki`, pass the wiki node token |
| `size` | Yes | File size (bytes) |
| `file_token` | No | Existing file token; when passed, overwrite that file's content |

> [!CAUTION]
> This is a **write operation** -- you must confirm the user's intent before executing.

<a id="参考"></a>
## Reference

- [lark-drive](../index.md) -- all commands for cloud space (Drive/cloud storage)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
