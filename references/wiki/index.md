# Wiki

Use explicit `--as user` for personal spaces/nodes. Use bot only when requested and preserve the identity used to resolve the object.

## Resolve the target

`wiki +node-get --node-token <URL-or-token>` resolves `space_id`, `node_token`, `obj_token`, and `obj_type`. A Wiki URL/name/doc token is not a numeric `space_id`; a document token is not a parent node token.

List spaces with `+space-list`, then nodes with `+node-list --space-id <id>`. For nested listing use the actual `--parent-node-token`. On invalid parameters, not found, or permission denied, fix the cause instead of repeating identical calls; rate limits permit backoff.

A personal document library (`my_library`, including the user's "personal knowledge library") is a Wiki personal library, not the Drive root. Resolve its real space ID. "My Space"/Drive folder instead means Drive.

## Operation routing

- Topic-based cross-container collection: [workflow routing](../drive/references/lark-drive-workflow.md) → [topic collector](../drive/references/lark-drive-workflow-topic-move-collector.md).
- Inventory/reorganize a knowledge library: [organization workflow](../drive/references/lark-drive-workflow-knowledge-organize.md). Planning alone is read-only.
- Move within/into Wiki: [move](references/lark-wiki-move.md).
- Move a Wiki node out to Drive: [move-to-drive](references/lark-wiki-move-to-drive.md), not `drive +move`.
- Rename a node in place: `drive +update-title --url <wiki_url> --title <title>`; do not copy/recreate it.
- Copy a node: [node-copy](references/lark-wiki-node-copy.md); create a new node: [node-create](references/lark-wiki-node-create.md).
- Upload a local file beneath a Wiki node: [Drive](../drive/index.md) `+upload --wiki-token`.
- Download an underlying file: Drive `+download --wiki-token` or `--url`. Online docx/sheet/bitable/slides require export or their content module.

## Delete a space

Read [delete-space](references/lark-wiki-delete-space.md). Resolve a URL through `+node-get`; resolve a name through paginated space listing. Do not stop at the first name match if duplicate names could exist on later pages. Use exact matches before loose matching, and show candidates when ambiguous.

A unique, fully resolved target plus an explicit deletion request is authorization; reuse a prior exact selection. Ask when scope/target is unresolved, not simply because a turn changed. Execute with the real ID and `--yes`, and track any asynchronous task.

## Members

Resolve member type before attempting a write:

| Target | Write type | ID source |
|---|---|---|
| User | `openid` | [Contacts](../contact/index.md) |
| Group | `openchat` | [Messaging](../im/index.md) |
| App | `appid` | Actual app ID, usually `cli_...` |
| Department | `opendepartmentid` | Department search with user identity |

Bot/tenant identity cannot add departments. Explain the limitation without trying the unsupported call or silently switching identity. Department lookup uses the documented contact departments search API; other ID forms such as `userid`/`unionid` need real conversion, not prefix guesses.

[Member-list](references/lark-wiki-member-list.md) defaults to one page; use `--page-all` for exhaustive lists. [Member-remove](references/lark-wiki-member-remove.md) requires the original granted `--member-type` and `--member-role`; read the existing grant if unknown.

Document-body work belongs to [Documents](../doc/index.md), cell work to [Sheets](../sheets/index.md), records to [Base](../base/index.md), and search/comments/document sharing to Drive.

## Operation references

- [wiki space list](references/lark-wiki-space-list.md)
- [wiki space create](references/lark-wiki-space-create.md)
- [wiki node list](references/lark-wiki-node-list.md)
- [wiki node get](references/lark-wiki-node-get.md)
- [wiki node delete](references/lark-wiki-node-delete.md)
- [wiki member add](references/lark-wiki-member-add.md)
