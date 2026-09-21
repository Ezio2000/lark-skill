# Wiki token routing

A token in `/wiki/<token>` identifies a Wiki node, not necessarily its underlying document, sheet, Base, file, or presentation. Resolve the underlying object before content operations, comments, exports, downloads, or table edits, unless the selected shortcut already resolves Wiki URLs.

## Inspect the underlying resource

```sh
lark-cli drive +inspect --url 'https://example.feishu.cn/wiki/<wiki_token>' --as user
```

The result's `type` is the underlying object type and `token` is the canonical token for downstream operations. `wiki_node` retains node-side fields such as `space_id`, `node_token`, `obj_token`, and `obj_type`.

## Resolve node-side fields

When the task needs node or space coordinates:

```sh
lark-cli wiki +node-get --node-token 'https://example.feishu.cn/wiki/<wiki_token>' --format json --as user
```

| Field | Meaning |
|---|---|
| `data.obj_type` | Underlying type: docx, doc, sheet, bitable, slides, file, mindnote, etc. |
| `data.obj_token` | Underlying object token for its business module/API |
| `data.node_token` | Wiki node token for hierarchy operations |
| `data.space_id` | Containing knowledge space |

Preserve the same identity for resolution and downstream calls. Use bot in both only for a selected bot workflow.

## Route by object

| Object | Module |
|---|---|
| `docx` / `doc` | Documents for body content; Drive for comments, sharing, export |
| `sheet` | Sheets for cells; Drive for comments, sharing, export |
| `bitable` | Base for records/structure; Drive for comments, sharing, export |
| `slides` | Slides for presentation content; Drive for comments, sharing, export |
| `file` | Drive for upload/download/comments/permissions |
| `mindnote` | Drive for move/delete/shortcuts/permissions/secure labels; Wiki for node hierarchy |
| Node hierarchy / space members | Wiki; do not substitute an underlying object token for a node token |
