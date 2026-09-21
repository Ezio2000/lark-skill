<a id="drive-member-add添加协作者授权成员权限"></a>
# drive +member-add (add collaborators/grant member permissions)

> This is a high-risk write operation. Real execution modifies document permissions and requires explicitly adding `--yes`

<a id="命令"></a>
## Command

```bash

# Batch add (same member-type and perm, up to 10 people)
lark-cli drive +member-add \
  --token "<bare_token_or_url>" \
  --type bitable \
  --member-id "ou_a,ou_b" \
  --member-type openid \
  --perm view \
  --yes
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description                                                                                                                                                                                  |
|------|----|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--token` | Yes | Bare token or full URL. Path supports `/drive/folder/`, `/docx/`, `/doc/`, `/sheets/`, `/base/`, `/bitable/`, `/wiki/`, `/file/`, `/mindnotes/`, `/slides/`, `/minutes/`, `/page/`; URL input can infer `--type` from the path, bare tokens do not perform prefix inference |
| `--type` | Required | Target resource type: `docx` / `doc` / `sheet` / `bitable` / `file` / `folder` / `wiki` / `mindnote` / `slides` / `minutes` / `apps`. Can be omitted when passing a URL; must be explicitly passed for bare tokens; if both a URL and `--type` are passed, the explicit `--type` overrides the URL inference |
| `--member-id` | Yes | Collaborator ID; comma-separated for batch add, up to 10 |
| `--member-type` | Yes | Type of member-id; supports `email` / `openid` / `unionid` / `openchat` / `opendepartmentid` / `groupid` / `appid` / `wikispaceid`. In actual use, granting permissions to the current application still preferentially recommends bot `open_id` + `openid`.                               |
| `--member-kind` | Conditionally required | Fill in only when `--member-type=wikispaceid`, maps to the `type` field of the request body. Values: `wiki_space_member` / `wiki_space_viewer` / `wiki_space_editor`. Passing this parameter is prohibited for other member-types. |
| `--perm` | No | Authorization role: `view` (default) / `edit` / `full_access`                                                                                                                                             |
| `--perm-type` | No | Only applies to the wiki node permission scope: `container` (default, current page + subpages) / `single_page` (current page only)                                                                                                                      |
| `--need-notification` | No | Whether to notify the other party. Only available for `--as user`; when not passed it is not written to the query, `--need-notification=false` means explicitly do not notify                                                                                                           |
| `--dry-run` | No | Only print the request, do not actually grant permissions                                                                                                                                                                         |
| `--yes` | Yes for real execution | Confirm the high-risk write operation                                                                                                                                                                            |

<a id="输出"></a>
## Output

Batch success:

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "resource_token": "doc_token_or_url",
    "resource_type": "docx",
    "requested_count": 2,
    "succeeded_count": 2,
    "partial": false,
    "members": [
      {"resource_token": "doc_token_or_url", "resource_type": "docx", "member_id": "ou_a", "member_type": "openid", "member_kind": "user", "perm": "view"},
      {"resource_token": "doc_token_or_url", "resource_type": "docx", "member_id": "ou_b", "member_type": "openid", "member_kind": "user", "perm": "view"}
    ],
    "missing_member_ids": []
  }
}
```

On batch partial failure, `partial` is `true`, and the same result is written to **stdout** as a `ok:false` partial-failure envelope (stderr no longer outputs a separate error envelope), and the CLI exits with a non-zero exit code. Check `requested_count`, `succeeded_count`, `members`, `missing_member_ids`, and the optional `mismatched_member_ids` in `data`. Response order does not affect matching results.

<a id="行为说明"></a>
## Behavior notes

- **Identity support**: Both `--as user` and `--as bot` can be used.
- **Department collaborators**: `--member-type=opendepartmentid` must be used together with `--as user`; the bot identity does not support adding department collaborators.
- **Notification**: `--need-notification` is only valid when `--as user`; when `--as bot`, passing this parameter will be rejected.
- **Batch constraints**: Batch requests share the same `--member-type`, `--perm`, and `--perm-type`; scenarios mixing users/groups/departments need to be split into multiple calls.
- **Wiki space ID**: When `--member-type=wikispaceid`, `--member-kind` must also be passed, otherwise the API will lack the required body `type` field. `wiki_space_member` corresponds to the knowledge base member role; if the knowledge base has split members into readable/editable member groups, use `wiki_space_viewer` or `wiki_space_editor` instead.
- **ID resolution**: Prefer `open_id` + `--member-type openid`; use `email` only when `open_id` cannot be resolved. For groups, prefer `openchat`, and for departments use `opendepartmentid`.
