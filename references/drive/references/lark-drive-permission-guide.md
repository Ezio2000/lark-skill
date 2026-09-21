<a id="drive-权限与授权指南"></a>
# Drive Permission and Authorization Guide

> Prerequisites: general authentication, scopes, and `--as` rules are described in [`../../shared/index.md`](../../shared/index.md).

<a id="何时读取"></a>
## When to Read

- The user wants to modify a document's public permissions, especially when `drive permission.public patch` returns `91009` / `91010` / `91011` / `91012`.
- The user wants to add collaborator permissions to a document, file, folder, Wiki, or slides, or grant access to the current application (bot) itself.
- The user encounters `permission denied`, but the error behavior looks more like tenant external sharing, security policy, or classification-level interception rather than a normal missing scope.

If the user only wants to request access from the document owner, prefer using [`lark-drive-apply-permission.md`](lark-drive-apply-permission.md).

<a id="公开权限修改前门槛"></a>
## Prerequisites Before Modifying Public Permissions

Modifying public permissions is a high-risk write operation. Before executing `drive permission.public patch --yes`, confirm all of the following:

| Condition | Executable Signal |
|------|------------|
| Specific target | A single URL/token, or a resource list the user has confirmed |
| Public scope | The user has explicitly chosen a specific `link_share_entity` level such as organization/internet, readable/editable |
| Execution confirmation | The user has authorized execution for that target and scope in the current session |

"Open it up", "share it with everyone", and "let everyone see it" only express the desired end state and do not include a specific public scope. First list the available scopes and stop to wait for the user to choose; the public level must come from the user's choice, and the CLI's `--yes` only indicates that the user's execution confirmation for that level has been obtained.

<a id="公开权限错误码"></a>
## Public Permission Error Codes

When calling `lark-cli drive permission.public patch` to update a document's public permissions fails, if the following error codes are returned, give the user clear next steps according to the table. Do not simply classify these errors as missing scopes; they usually indicate interception by tenant, external sharing, or document classification-level policies.

| Error Code | Meaning | Guidance for the User |
|--------|------|--------------|
| `91009` | External sharing is controlled by the tenant security policy, and the current user cannot enable it | Tell the user: the external sharing capability is uniformly controlled by the tenant security policy and cannot be enabled directly through the API or by the current user; they need to contact the tenant administrator to adjust the organization-level external sharing policy. |
| `91010` | External sharing for the document is not enabled | Tell the user: external sharing is not yet enabled for the current document; please first enable external sharing in the document permission settings, then retry `permission.public.patch`. |
| `91011` | External sharing is controlled by the document classification level | Tell the user: external sharing is intercepted by the classification-level policy; they need to open the target document, initiate a classification-level exemption or perform a classification-level downgrade within the document, and then retry; the reply must include the target document URL. |
| `91012` | Permission settings are controlled by the document classification level | Tell the user: this permission setting is intercepted by the classification-level policy; they need to open the target document, initiate a classification-level exemption or perform a classification-level downgrade within the document, and then retry; the reply must include the target document URL. |

When the user initially provided a document URL, upon encountering `91011` or `91012`, return that URL as-is to the user as the operation entry point; if the context only contains a token, first try to recover the target document URL through existing context, search results, or metadata as much as possible, then provide a clickable document URL.

<a id="授权当前应用访问文档"></a>
## Authorizing the Current Application to Access a Document

When the document permissions need to be granted to the current application (bot) itself:

1. First execute `lark-cli api GET /open-apis/bot/v3/info --as bot --jq '.data.open_id'` to directly obtain the current application's `open_id`.
2. Then call `lark-cli drive permission.members create`, authorizing with `member_type=openid` and `member_id=<bot_open_id>`.

```bash
lark-cli drive permission.members create \
  --params '{"token":"<doc_token>","type":"<resource_type>"}' \
  --data '{"member_type":"openid","member_id":"<bot_open_id>","perm":"view","type":"user"}'
```

This method is only applicable to authorizing the current application. When authorizing other users, directly use their open_id; there is no need to call the bot info API.

`<resource_type>` possible values: `doc`, `docx`, `sheet`, `bitable`, `file`, `folder`, `wiki`, `slides`.
