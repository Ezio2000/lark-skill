# Documents and mindnotes

Use explicit `--as user` for personal document operations. Read the reference for the current operation; do not preload all formatting or authoring material.

## Content operations

- **Read or summarize:** read [+fetch](references/lark-doc-fetch.md), then fetch the document.
- **Short new document, complete supplied content, or empty document:** use [+create](references/lark-doc-create.md) directly. Choose Markdown or XML to match the content, and read only that format reference.
- **Long document, complex components, or strict layout:** use the [authoring workflow](references/lark-doc-create-workflow.md). Read genre guidance only when it materially affects the output.
- **Edit or follow a block link:** use [+update](references/lark-doc-update.md) for rewriting, restructuring, adding content, or changing layout.

Local paths follow each command's file-access rules. XML relative resources are first resolved against cwd, then against the source XML directory only if absent in cwd. Inline content, stdin, and remote documents have no source-file-directory fallback.

## Supporting operations

- [Draft initialization, parsing, and statistics](references/lark-doc-script.md): handles document URLs/tokens and local XML; does not parse Markdown.
- [Version history and restoration](references/lark-doc-history.md): list or restore revisions and inspect restoration status.
- [Insert media](references/lark-doc-media-insert.md): append a local image or attachment.
- [Preview media](references/lark-doc-media-preview.md) and [download media](references/lark-doc-media-download.md): document/comment resources and board previews.
- [Document cover](references/lark-doc-resource-cover.md): download, replace, or remove a Docx cover.
- [Whiteboard workflow](references/lark-doc-whiteboard.md): reuse an existing board token when editing; write through [whiteboard update](../whiteboard/references/lark-whiteboard-update.md).
- [Existing mindnotes](references/lark-doc-mindnote.md): list/read/update their nodes. For a newly requested visual mind map, follow the documented whiteboard route.

## Boundaries

[Drive](../drive/index.md) handles discovery, imports/exports, file-level upload/download, permissions, native copying, and standalone comment operations. Preserve native structure by copying through Drive, not by fetch/create reconstruction.

Default JSON document fetch can include compact comment context. Dedicated comment pagination, replies, edits, or reactions use Drive.

Do not run auth status or login as a routine preflight. Use [diagnostics](../shared/index.md) only for authentication requests or actual identity/token/scope errors.
