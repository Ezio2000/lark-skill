<a id="drive-member-remove移除协作者权限"></a>
# drive +member-remove (remove collaborator permission)

> This is a high-risk write operation. Real execution removes permissions; you must verify the resource and member and then explicitly add `--yes`.

<a id="命令"></a>
## Command

```bash
lark-cli drive +member-remove \
  --token "<bare_token_or_url>" \
  --type docx \
  --member-id "ou_xxx" \
  --member-type openid \
  --yes
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--token` | Yes | Bare token or full URL. Paths support `/drive/folder/`, `/docx/`, `/doc/`, `/sheets/`, `/base/`, `/bitable/`, `/wiki/`, `/file/`, `/mindnotes/`, `/slides/`, `/minutes/`, `/page/`; the type can be inferred from the URL path, but a bare token requires also passing `--type`. |
| `--type` | Conditionally required | Resource type: `docx` / `doc` / `sheet` / `bitable` / `file` / `folder` / `wiki` / `mindnote` / `slides` / `minutes` / `apps`. Can be omitted for a full URL. |
| `--member-id` | Yes | The single collaborator ID to remove. Comma-separated multi-member input is rejected; batch scenarios should call this one by one. |
| `--member-type` | Yes | ID type: `email` / `openid` / `openchat` / `opendepartmentid` / `userid` / `unionid` / `groupid` / `appid` / `wikispaceid`. |
| `--member-kind` | Conditionally required | Used only by `--member-type=wikispaceid`: pass `wiki_space_member` when Wiki member grouping is not enabled, and after it is enabled pass `wiki_space_viewer` or `wiki_space_editor` depending on the permission. |
| `--perm-type` | No | Used only by wiki collaborators: `container` (default, current page and subpages) or `single_page` (current page only). |
| `--dry-run` | No | Only preview the DELETE URL, query, and body; do not call the API. |
| `--yes` | Yes for real execution | Confirm the high-risk permission removal operation. |

<a id="输出"></a>
## Output

Taking the removal of a user collaborator of type `openid` as an example, on success it returns:

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "removed": true,
    "resource_token": "doxcnxxx",
    "resource_type": "docx",
    "member_id": "ou_xxx",
    "member_type": "openid",
    "member_kind": "user"
  }
}
```

A regular Wiki collaborator also returns `perm_type`; `wikispaceid` returns the passed `member_kind`.

`removed: true` indicates that the delete request completed successfully; it does not guarantee that the permission previously existed.

<a id="行为说明"></a>
## Behavior notes

- **Identity support**: Supports `--as user` and `--as bot`.
- **App collaborators**: Use `--member-type=appid`, and pass the app ID (usually `cli_xxx`) for `--member-id`.
- **Department collaborators**: `--member-type=opendepartmentid` can only be used with `--as user`; the bot identity is rejected early on the client side.
- **Safe encoding**: Both the resource token and member ID are encoded as independent path segments.
- **Wiki scope**: Regular wiki collaborators remove the `container` permission by default; to remove only the current page permission, explicitly pass `single_page`.
- **Wiki space members**: `--member-type=wikispaceid` supports only `--type=wiki`; you must use `--member-kind` to specify the member role, and you cannot pass `--perm-type` at the same time.
- **Error handling**: Typed errors returned by the OpenAPI are passed through as-is; you can handle them based on the subtype, code, hint, and permission information in the error envelope.
