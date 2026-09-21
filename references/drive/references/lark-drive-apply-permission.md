
<a id="drive-apply-permission申请文档权限"></a>
# drive +apply-permission (Apply for Document Permission)


This module corresponds to the shortcut: `lark-cli drive +apply-permission`.

Initiate a `view` or `edit` permission request to the cloud document **Owner**. The request will be pushed to the Owner as a card, and the Owner decides whether to approve it.

> [!CAUTION]
> This is a **write operation** — it will send a push notification to the Owner. Do not call it in batches or automate it. You can preview first with `--dry-run`.

<a id="身份要求"></a>
## Identity Requirements

- **Only `user` identity is supported** (using `user_access_token`); `bot` / `tenant_access_token` are not supported. The shortcut has already enforced `user` in `AuthTypes`; using a bot will be rejected.
- Required scope: `docs:permission.member:apply` (if the user lacks permission, it will go through the unified permission error path).

<a id="命令"></a>
## Command

```bash
# Apply via URL (type is automatically inferred from the URL)
lark-cli drive +apply-permission \
  --token "https://example.larksuite.com/docx/doxcnxxxxxxxxx" \
  --perm view \
  --remark "安全评估：需查看需求文档内容" --as user

# Apply via bare token + explicit --type
lark-cli drive +apply-permission \
  --token "doxcnxxxxxxxxx" --type docx \
  --perm edit --as user
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--token` | Yes | Target document token or full URL (the token in `/docx/`, `/sheets/`, `/base/`, `/bitable/`, `/file/`, `/wiki/`, `/doc/`, `/mindnote/`, `/slides/`, `/page/` paths will be automatically extracted) |
| `--type` | No | Target type. Possible values: `doc` / `sheet` / `file` / `wiki` / `bitable` / `docx` / `mindnote` / `slides` / `apps`. When passing a URL, it is automatically inferred by the shortcut; if passed explicitly, it must match the URL path type. For a bare token, it must be passed explicitly |
| `--perm` | Yes | The permission being requested. Only `view` or `edit` is supported (**`full_access` is not supported**; the CLI side will reject it directly) |
| `--remark` | No | Remark, which will be displayed on the permission request card |
| `--dry-run` | No | Only print the request content; do not actually send it |

<a id="输出"></a>
## Output

On API success, an empty `data` is returned (only `code: 0, msg: "success"`), corresponding to the CLI output:

```json
{
  "ok": true,
  "identity": "user",
  "data": {}
}
```

<a id="频率限制"></a>
## Rate Limits

- **Application-level**: At most 10 times per minute per application per tenant.
- **User-level**: The same user may not exceed 5 times per day for **the same document**.

<a id="常见错误"></a>
## Common Errors

| Error Code | Meaning | CLI Handling |
|---|---|---|
| `1063006` | Request count has reached the limit (5 times/day) | CLI automatically adds hint: `permission-apply quota reached: each user may request access on the same document at most 5 times per day` |
| `1063007` | The current document cannot be applied for (e.g., external applications are disabled for the document, the applicant already has the corresponding permission, the target type does not support apply) | CLI automatically adds hint: `this document does not accept a permission-apply request ... contact the owner directly` |
| `1063002` | No operation permission (e.g., the tenant has disabled external applications) | Handled by the unified permission error path |
| `1063004` | The user's organization has no sharing permission | Handled by the unified permission error path |
| `1063005` | Resource has been deleted | Need to confirm whether the target document/node still exists |
| `1066001/1066002` | Server exception / concurrent conflict | Retry later |

<a id="与-wiki-url-的关系"></a>
## Relationship with wiki URLs

When a `/wiki/<node_token>` is passed in, the shortcut will directly use `node_token` as the path parameter and call the API with `type=wiki`. If you need to first resolve the wiki node into a `obj_token`, call the [`wiki +node-get` shortcut](../../wiki/references/lark-wiki-node-get.md) yourself first to get the `obj_token + obj_type`, then call this command with a bare `obj_token` + `--type <obj_type>`.

<a id="参考"></a>
## References

- OpenAPI endpoint: `POST /open-apis/drive/v1/permissions/:token/members/apply`
