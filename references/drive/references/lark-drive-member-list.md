<a id="drive-member-list查询协作者授权成员列表"></a>
# drive +member-list (query collaborator/authorized member list)

This module corresponds to shortcut: `lark-cli drive +member-list`. It reads the collaborator/authorized member list of a Drive document, file, folder, or wiki node.

<a id="命令"></a>
## Command

```bash
#  URL auto-infers type
lark-cli drive +member-list \
  --token 'https://example.feishu.cn/drive/folder/<folder_token>' \
  --as user --format json

# Query additional fields
lark-cli drive +member-list \
  --token '<token>' \
  --type docx \
  --fields 'name,type,external_label' \
  --as user --format json

```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--token` | Yes | Bare token or full URL. URL paths support `/folder/`, `/docx/`, `/doc/`, `/sheets/`, `/base/`, `/bitable/`, `/wiki/`, `/file/`, `/mindnotes/`, `/slides/`, `/minutes/`, `/page/`. |
| `--type` | Required for bare token | Target type: `doc` / `sheet` / `file` / `wiki` / `bitable` / `docx` / `mindnote` / `minutes` / `slides` / `folder` / `apps`. URL can auto-infer; if both a URL and a conflicting `--type` are passed, the CLI will reject it. |
| `--fields` | No | Not passed by default. Can be `name` / `type` / `avatar` / `external_label`, comma-separated; you can also pass `*` to request all currently supported additional fields. This parameter only declares the fields expected to be returned; it does not grant field-level permissions. |
| `--perm-type` | No | Only valid for `--type wiki`; values `container` / `single_page`. |
| `--dry-run` | No | Only prints the request, does not call the API. |

<a id="输出"></a>
## Output

JSON output passes through the API's `data` as-is:

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "items": [
      {
        "member_type": "openid",
        "member_id": "ou_xxx",
        "perm": "view",
        "perm_type": "container",
        "type": "user",
        "name": "zhangsan",
        "external_label": false
      }
    ]
  }
}
```

`--format pretty` lightly displays member ID, member type, permissions, wiki `perm_type`, and any returned additional fields. For machine reading, prefer `--format json`.

<a id="行为说明"></a>
## Behavior notes

- **Identity support**: Both `--as user` and `--as bot` are available; when scope or target permissions are missing, it is handled via the unified permission error path.
- **API scope**: Querying the member list requires `docs:permission.member:retrieve`.
- **fields default**: When `--fields` is not passed, the official API default applies, and additional fields such as name, avatar, and external tags are not requested; specify them explicitly when needed.
- **Field-level permissions**: `--fields` only controls which additional fields are requested; it does not guarantee the server will return them. When requesting a user's `name` / `avatar`, the app also needs `contact:user.base:readonly` enabled ("Get user basic info"; existing official-compatible historical contacts permissions can also satisfy the requirement).
- **Missing field semantics**: When field-level permissions or data visibility are insufficient, the API may still succeed but omit the corresponding sensitive fields. A requested field missing from the response means "the server did not return it"; it cannot be interpreted as the field value being empty, nor can it be used to conclude that member information is complete.
- **folder support**: The CLI supports `--type folder` and will send `type=folder` as needed; in some environments, if the backend has not yet enabled folder enumeration, it may return `99992402 field validation failed`.
