# Drive-native Markdown

This module handles ordinary `.md` files stored in Drive, not native Docx documents. Reuse the existing identity and authorization; use `--as user` for personal files and `--as bot` only when the application owns or can access the intended resource.

| Operation | Reference |
|---|---|
| Create/upload a native Markdown file | [+create](references/lark-markdown-create.md) |
| Compare remote versions or a remote file against a local draft | [+diff](references/lark-markdown-diff.md) |
| Read content | [+fetch](references/lark-markdown-fetch.md) |
| Replace text or apply a regex replacement | [+patch](references/lark-markdown-patch.md) |
| Replace the entire file | [+overwrite](references/lark-markdown-overwrite.md) |

Use [Drive](../drive/index.md) for searching, renaming, moving, deleting, permissions, comments, and version enumeration. Importing Markdown as a native document uses `drive +import --type docx`.

## Protocol constraints

- Both `--name` and a local `--file` filename require the `.md` suffix.
- `--content` accepts literal content, `@file`, or `-` for stdin.
- A patch fetches the complete file, replaces text locally, and overwrites the remote file. It is not an atomic server-side patch.
- A patch accepts one pattern/content pair. The final content cannot be empty because zero-byte Markdown uploads are unsupported.
- Escape regex metacharacters when matching literal text.
- Creation targets use `--folder-token` for a Drive folder and `--wiki-token` for a Wiki node. Do not trial unrelated resource URLs as folder tokens; supported target URLs are normalized by the CLI.
- Missing scope, permission denied, not found, quota exhaustion, and version limits require addressing the cause, not repeated writes. Only transient network, rate-limit, or server errors justify bounded backoff.
