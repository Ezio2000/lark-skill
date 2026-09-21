# Drive

Use for cloud-file discovery, copying, moving, importing/exporting, folders, comments, versions, and sharing. Feishu, Lark, and supported doubao cloud-resource links follow the same resource-type routing.

## Routing and identifiers

- Copy an online native resource with [copy](references/lark-drive-copy.md). Do not simulate copying by export/import or document fetch/create. Copy into Wiki with [node-copy](../wiki/references/lark-wiki-node-copy.md).
- A clear resource URL can supply its type/token directly. For Wiki URLs, ambiguous tokens, titles, or canonical URLs use [inspect](references/lark-drive-inspect.md); a Wiki token is not its underlying file token.
- Move a Wiki node out to Drive through [Wiki](../wiki/index.md), not `drive +move`. Move a known Drive file/folder through [move](references/lark-drive-move.md).
- Document body operations belong to [Documents](../doc/index.md); cells to [Sheets](../sheets/index.md); records to [Base](../base/index.md); native Markdown to [Markdown](../markdown/index.md).
- `/page/<token>` is an Apps resource, not a docx document.
- Search [by title/filters](references/lark-drive-search.md) when no unique resource is known. `--created-by-me` means original creator; `--mine` means current owner.

## Files and conversion

| Source/intent | Operation |
|---|---|
| Local Excel/CSV/`.base` → Base | `drive +import --type bitable` |
| Local Markdown/Word/text/HTML → document | `drive +import --type docx` |
| Local PPTX → slides | `drive +import --type slides` (up to 500 MB) |
| Local XLSX/XLS/CSV → spreadsheet | `drive +import --type sheet` |
| Local file → Wiki node | `drive +upload --wiki-token <token>` |
| Online doc/docx/sheet/bitable/slides → local file | `drive +export` |
| Drive file content/converted preview | `drive +download` / `drive +preview` |
| Native Markdown read/write/patch/diff | [Markdown](../markdown/index.md) |

Read [import](references/lark-drive-import.md), [export](references/lark-drive-export.md), or the matching file reference before execution. Downloads/previews accept exactly one of file token, URL, or Wiki token resolving to a file; they are not online-document export commands. Updating an existing uploaded file should preserve its identity through overwrite upload when supported.

Serialize imports into the same folder/root/target. Import conflict codes `232140101`, `232140100`, and `233523001` permit bounded delayed retries, at most three; report continuing conflicts. Do not retry unchanged not-found/permission/scope failures as network errors.

## Organization and permissions

- [Workflow routing](references/lark-drive-workflow.md) selects [topic collection](references/lark-drive-workflow-topic-move-collector.md), [directory organization](references/lark-drive-workflow-knowledge-organize.md), or [permission governance](references/lark-drive-workflow-permission-governance.md) for those multi-resource tasks. A single known move or permission read does not require an audit workflow.
- A planning/report request is read-only. An authorized exact execution plan can proceed without repeated confirmations. "Delete useless files" or "share with everyone" needs candidate/scope resolution.
- [Permission settings](references/lark-drive-permission-get-setting.md) reads only the target's settings, not descendants; bare tokens need `--type`.
- [Permission guide](references/lark-drive-permission-guide.md) covers collaborators, sharing, owner transfer, and `91009–91012`. Tenant policy/secure-label failures are not necessarily missing scopes.
- [Remove member](references/lark-drive-member-remove.md) needs exact resource/member type/ID and Wiki permission scope; execute an authorized removal with `--yes`.
- [Access requests](references/lark-drive-apply-permission.md) contact the owner and require authorization. [Secure labels](references/lark-drive-secure-label.md) are Drive governance.
- Comments use the matching shortcut and [location guide](references/lark-drive-comment-location.md). Do not assume all comment commands support Apps; inspect their resource support.

## Native APIs and sync

Inspect `lark-cli schema drive.<resource>.<method>` when using a native API without a complete documented contract. Folder enumeration uses [files list](references/lark-drive-files-list.md), with explicit pagination; do not parse multi-page mixed output as one JSON object.

`+sync` only synchronizes `type=file`, skips online documents/shortcuts, and does not delete extra files. Conflicts use `--on-conflict=remote-wins|local-wins|keep-both|ask`; duplicate remote paths use `--on-duplicate-remote=fail|newest|oldest`. `--quick` compares timestamps instead of exact SHA-256. Read [status](references/lark-drive-status.md), [pull](references/lark-drive-pull.md), or [push](references/lark-drive-push.md) for the selected direction.

Statistics and view records accept typed `--file-token` / `--file-type` flags. Quota lookup is user-only and uses the current user's `user_id` as `quota_detail_id`. Preserve identity across version operations; user and bot are supported, but automation alone is not a reason to switch.

## Operation references

Read only the reference matching the current operation.

- [shared high risk approval](../shared/references/lark-shared-high-risk-approval.md)
- [drive update title](references/lark-drive-update-title.md)
- [wiki token routing](../shared/references/lark-wiki-token-routing.md)
- [index](../shared/index.md)
- [drive upload](references/lark-drive-upload.md)
- [drive create folder](references/lark-drive-create-folder.md)
- [drive download](references/lark-drive-download.md)
- [drive preview](references/lark-drive-preview.md)
- [drive cover](references/lark-drive-cover.md)
- [drive create shortcut](references/lark-drive-create-shortcut.md)
- [drive add comment](references/lark-drive-add-comment.md)
- [drive list comments](references/lark-drive-list-comments.md)
- [drive batch query comments](references/lark-drive-batch-query-comments.md)
- [drive resolve comment](references/lark-drive-resolve-comment.md)
- [drive restore comment](references/lark-drive-restore-comment.md)
- [drive add reply](references/lark-drive-add-reply.md)
- [drive list replies](references/lark-drive-list-replies.md)
- [drive update reply](references/lark-drive-update-reply.md)
- [drive delete reply](references/lark-drive-delete-reply.md)
- [drive react reply](references/lark-drive-react-reply.md)
- [drive export download](references/lark-drive-export-download.md)
- [drive version history](references/lark-drive-version-history.md)
- [drive version get](references/lark-drive-version-get.md)
- [drive version revert](references/lark-drive-version-revert.md)
- [drive version delete](references/lark-drive-version-delete.md)
- [drive delete](references/lark-drive-delete.md)
- [drive task result](references/lark-drive-task-result.md)
- [drive member add](references/lark-drive-member-add.md)
- [drive member list](references/lark-drive-member-list.md)
