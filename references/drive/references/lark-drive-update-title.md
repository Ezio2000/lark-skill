# drive +update-title


Rename a file, folder, online document, or wiki node in cloud space (Drive/cloud storage).

<a id="命令"></a>
## Command

```bash
# Recommended: pass a URL (automatically detects type and token)
lark-cli drive +update-title \
  --url 'https://example.larksuite.com/docx/<DOCX_TOKEN>' \
  --title '<NEW_TITLE>'

# A bare token must explicitly pass --type
lark-cli drive +update-title \
  --token <FILE_TOKEN> \
  --type file \
  --title '<NEW_TITLE>.xlsx'

# Wiki node: pass the node_token from the /wiki/ URL
lark-cli drive +update-title \
  --url 'https://example.larksuite.com/wiki/<NODE_TOKEN>' \
  --title '<NEW_TITLE>'
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--url` | Choose one of `--token` | Target URL, supports `/docx/`, `/sheets/`, `/base/`, `/bitable/`, `/slides/`, `/file/`, `/drive/folder/`, `/wiki/` |
| `--token` | Choose one of `--url` | Target token or URL; a bare token must be used with `--type` |
| `--type` | Required when using a bare token | `docx`, `sheet`, `bitable` (`base` is a compatible alias), `slides`, `file`, `folder`, `wiki`; can be omitted when passing a URL, but if explicitly passed it must match the URL type |
| `--title` | Yes | New title, alias `--new-title`; cannot be empty or pure whitespace, leading and trailing spaces are stripped |
| `--on-extension-mismatch` | No | Only for `--type file`: `keep` (default, automatically appends the current suffix when the title lacks a suffix, errors when the suffix is inconsistent) / `allow` (skip validation, submit as-is). Passing it to other `--type` will error |

<a id="行为说明"></a>
## Behavior notes

- **Empty titles are rejected**: the CLI rejects an empty or pure-whitespace `--title`
- **`file` types validate the suffix**: the title of `--type file` is the complete file name. The CLI compares the suffix of `--title` with the current file name: when there is no suffix, it appends the current suffix by default (indicated in the output with `extension_appended`), and when the suffix is inconsistent it blocks (`a.md` → `a.txt`). To skip validation, add `--on-extension-mismatch=allow`
- **wiki is not unwrapped**: `--type wiki` uses the `wiki_token` from the `/wiki/` URL; passing the underlying document token will `981003`
- **Legacy doc and mind notes are not supported**: the server does not support changing the titles of these two types (`type=doc` / `type=mindnote` return `981002 params error`), and the CLI rejects them locally, so it will not waste a write request
- **Miaoda apps are not supported**: to change a Miaoda app title, switch to the [`lark-apps`](../../apps/index.md) business domain to handle it

<a id="输出"></a>
## Output

```json
{
  "updated": true,
  "file_token": "<file_token>",
  "type": "docx",
  "title": "<new_title>",
  "url": "https://example.feishu.cn/docx/<file_token>"
}
```

When `--type file` and `allow` is not used, the file name before renaming is additionally returned, so if the rename was wrong you can change it back with a single command based on it; if a suffix was automatically appended, `extension_appended` is also included:

```json
{
  "updated": true,
  "title": "<new_title>.txt",
  "previous_title": "<old_title>.txt",
  "extension_appended": ".txt"
}
```

<a id="常见错误"></a>
## Common errors

| Error code | Meaning | Handling |
|---|---|---|
| `99991672` / `99991679` | Missing scope | Apply for/authorize the required scope according to `missing_scopes` and `hint` in the error, then retry |
| `99991400` | Interface rate limit hit | Wait a while and retry; when renaming in batches, keep it serial and lower the frequency |

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for cloud space (Drive/cloud storage)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
