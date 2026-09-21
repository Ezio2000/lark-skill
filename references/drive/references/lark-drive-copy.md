
# drive +copy


Copy a Drive file (online document, spreadsheet, Base, Slides, mind note, or regular file) to a target folder, generating a new copy with the same content.

<a id="命令"></a>
## Command

```bash
# Source document passed as URL (type and token automatically detected)
lark-cli drive +copy --url "https://example.larksuite.com/docx/<DOCX_TOKEN>" --name '副本名称' --folder-token <TARGET_FOLDER_TOKEN>

# Wiki URL (automatically unwraps the underlying resource, then copies to Drive)
lark-cli drive +copy --url "https://example.larksuite.com/wiki/<WIKI_TOKEN>" --name '副本名称' --folder-token <TARGET_FOLDER_TOKEN>

# Wiki token
lark-cli drive +copy --token <WIKI_TOKEN> --type wiki --name '副本名称' --folder-token my_space
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--url` | Choose one of `--token` | Source document URL, supports `doc` / `docx` / `sheet` / `file` / `mindnote` / `slides` / `base` / `bitable` / `wiki` paths; wiki automatically unwraps the underlying resource |
| `--token` | Choose one of `--url` | Source document token or URL; a bare token must be used together with `--type` |
| `--type` | Required when using a bare token | Source file type: `doc`, `docx`, `sheet`, `file`, `mindnote`, `slides`, `bitable` (`base` is a compatibility alias) or `wiki`; can be omitted when passing a URL, but if explicitly passed it must match the URL type |
| `--name` | Yes | Copy name, maximum 256 bytes |
| `--folder-token` | Yes | Target folder token, folder URL, or the constant `my_space` (copy to the root directory of the current identity's "My Space", the root token is automatically resolved internally) |
| `--extra` | No | Repeatable `key=value` pair, passed through as-is to the API's `extra` custom copy parameters; typical usage `--extra target_type=docx` (convert to a docx copy when copying a legacy doc) |

<a id="输入规则"></a>
## Input Rules

- `--url` and `--token` are mutually exclusive, pass only one
- `--type` must match the source file's actual type; if the type does not match, the server will return a failure
- `base` and `bitable` are the same concept; the CLI normalizes `base` to `bitable` before sending it to the server
- The target folder must be a cloud space (Drive/cloud storage) folder token; a wiki node token cannot be passed

<a id="wiki-场景"></a>
## Wiki Scenarios

`drive +copy` accepts a wiki URL, and also accepts `--token <WIKI_TOKEN> --type wiki`. The target only supports a Drive folder or the `my_space` root directory; to keep the copy in the Wiki, use `wiki +node-copy`.

<a id="行为说明"></a>
## Behavior Notes

- After a successful copy under bot identity, the CLI automatically attempts to grant the current CLI user `full_access` on the new copy; the result is in the `data.permission_grant` field of the output; a failed grant does not affect the success status of the copy itself

<a id="输出"></a>
## Output

```json
{
  "ok": true,
  "identity": "bot",
  "data": {
    "copied": true,
    "file_token": "<new_file_token>",
    "file_type": "docx",
    "name": "副本名称",
    "url": "https://example.larksuite.com/docx/<new_file_token>",
    "source_file_token": "<source_file_token>",
    "source_type": "docx",
    "source_wiki_token": "<source_wiki_token, only for wiki input>",
    "folder_token": "<target_folder_token>",
    "permission_grant": {
      "status": "granted",
      "perm": "full_access",
      "member_type": "openid",
      "user_open_id": "<current_user_open_id>",
      "message": "Granted the current CLI user full_access on the new document."
    }
  }
}
```

`source_wiki_token` appears only for wiki input; `permission_grant` appears only under bot identity, and when copying under user identity there is no such field under `data`.

<a id="常见错误"></a>
## Common Errors

| Error Code | Meaning | Handling |
|---|---|---|
| `99991672` / `99991679` | Missing scope | Request/authorize the required scope according to `missing_scopes` and `hint` in the error, then retry |
| `99991400` | API rate limit hit | Wait a while and retry; when copying in bulk, keep it serial and reduce the frequency |

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all cloud space (Drive/cloud storage) commands
- [lark-wiki](../../wiki/index.md) -- Wiki node copy (`wiki +node-copy`)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
