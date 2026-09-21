# Whiteboards

Use `--as user` unless the task specifically requires application identity. Determine whether the request is read-only or changes a board, then choose one workflow.

## Read or export

Use [export](references/lark-whiteboard-export.md) with `--output-type preview` for an image, `svg` for vectors, or `source` for Mermaid/PlantUML source. Read-only exports do not require installing the local whiteboard drawing tool.

## Create or edit

- User-supplied Mermaid, PlantUML, or SVG can go through [update](references/lark-whiteboard-update.md) with the matching single `--input_format`.
- New complex diagrams use the [authoring workflow](references/lark-whiteboard-workflow.md).
- Existing boards use its editing workflow. Reuse the existing token, inspect the current structure, and keep changes within the request.
- SVG-based modification uses the [SVG edit route](routes/svg-edit.md). Replacing a populated board may rebuild it and lose unsupported content; establish that the user's requested scope covers that effect, or obtain the missing choice before overwriting.

For workflows that render or manipulate local board geometry, check the documented tool version with `npx -y @larksuite/whiteboard-cli@^0.2.13 -v` when needed. Do not install it as a routine export preflight.

Document body editing belongs to [Documents](../doc/index.md); inserting a board into a document uses the [document whiteboard workflow](../doc/references/lark-doc-whiteboard.md). Spreadsheet and Base data belong to their own modules.
