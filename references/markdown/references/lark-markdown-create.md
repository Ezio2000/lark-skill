# markdown +create


Create a native Markdown file (`.md`) in Drive, supporting creation into a regular Drive folder or under a Wiki node.

<a id="命令"></a>
## Command

```bash
# Create directly with inline content
lark-cli markdown +create \
  --name README.md \
  --content '# Hello'

# Create from a local .md file
lark-cli markdown +create \
  --file ./README.md

# Read content from a local file, but still go through --content
lark-cli markdown +create \
  --name README.md \
  --content @./README.md

# Read content from stdin
printf '# Hello\n\nfrom stdin\n' | \
  lark-cli markdown +create \
    --name README.md \
    --content -

# Create into a specified folder
lark-cli markdown +create \
  --folder-token fldcn_xxx \
  --file ./README.md

# Create into a specified folder (can pass a Drive folder URL directly)
lark-cli markdown +create \
  --folder-token "https://feishu.cn/drive/folder/fldcn_xxx" \
  --file ./README.md

# Create into a specified wiki node
lark-cli markdown +create \
  --wiki-token wikcn_xxx \
  --file ./README.md

# Create into a specified wiki node (can pass a wiki URL directly)
lark-cli markdown +create \
  --wiki-token "https://feishu.cn/wiki/wikcn_xxx" \
  --file ./README.md

# Preview the underlying request
lark-cli markdown +create \
  --name README.md \
  --content '# Hello' \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--folder-token` | No | Target Drive folder token or Drive folder URL; mutually exclusive with `--wiki-token`; when omitted, creates into the root directory |
| `--wiki-token` | No | Target wiki node token or wiki URL; mutually exclusive with `--folder-token`; when passed, automatically mapped to `parent_type=wiki` |
| `--name` | Conditionally required | File name, **must explicitly carry the `.md` suffix**; required when using `--content`; can be omitted when using `--file`, in which case the local file name is used by default |
| `--content` | Conditionally required | Markdown content; mutually exclusive with `--file`; supports passing a string directly, `@file`, `-` (stdin) |
| `--file` | Conditionally required | Local `.md` file path; mutually exclusive with `--content` |

<a id="关键约束"></a>
## Key Constraints

- Exactly one of `--content` and `--file` must be chosen
- `--folder-token` and `--wiki-token` are mutually exclusive
- `--folder-token` can only be a Drive folder; do not pass a wiki/doc/sheet/base/file token or URL
- `--wiki-token` can only be a Wiki node; if you only have a document URL such as docx/sheet/base, first use `lark-cli wiki +node-get --node-token <url>` to resolve the `node_token`
- `--name` must carry the `.md` suffix
- The local file name pointed to by `--file` must also carry the `.md` suffix
- When `--wiki-token` is passed, the return value will not include a `/file/<token>` URL, because a wiki-hosted file has no stable independent file URL

<a id="返回值"></a>
## Return Value

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "file_token": "boxcnxxxx",
    "file_name": "README.md",
    "size_bytes": 1234
  }
}
```

> [!IMPORTANT]
> If the Markdown file is **created with an app identity (bot)**, such as `lark-cli markdown +create --as bot`, after successful creation, the CLI will **attempt to automatically grant the current CLI user `full_access` (manageable permission) for that file**.
>
> When created with an app identity, the result will additionally return a `permission_grant` field that explicitly states the authorization result:
> - `status = granted`: the current CLI user has obtained manageable permission for the file
> - `status = skipped`: there is no available current user `open_id` locally, so no automatic authorization will be performed; you may prompt the user to complete `lark-cli auth login` first, then let the AI / agent continue to use the app identity (bot) to grant the current user permission
> - `status = failed`: the Markdown file was created successfully, but automatically authorizing the user failed; the failure reason will be included, and it will prompt to retry later or continue handling the file using the bot identity
>
> `permission_grant.perm = full_access` indicates that the resource has been granted "manageable permission".
>
> **Do not perform owner transfer on your own initiative.** Creation or import does not imply owner transfer; when the user has explicitly requested a transfer and the target has been determined, proceed with the authorization execution.

<a id="失败处理"></a>
## Failure Handling

- `not_found` / `1061044`: the parent directory or wiki node does not exist, or the token type was placed in the wrong parameter. Correct `--folder-token` / `--wiki-token` and retry; do not repeatedly submit the same parameters.
- `quota_exceeded` / `1061101`: the target storage quota is full. Free up space, switch the parent directory/node, or ask an administrator to expand capacity before retrying.
- `permission_denied` / `missing_scope`: handle by distinguishing identity. `--as user` depends on user authorization and the target ACL; `--as bot` depends on the app scope and the target directory/node ACL.
- `rate_limit`: stop retrying immediately and use backoff.
- `server_error` / `233523001`: limited retries later are acceptable; if they recur, keep the `log_id` / request id for server-side troubleshooting.

<a id="参考"></a>
## References

- [lark-markdown](../index.md) — Markdown domain overview
- [lark-shared](../../shared/index.md) — authentication and global parameters
