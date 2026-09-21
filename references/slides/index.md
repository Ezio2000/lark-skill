# Slides

Use for native Lark presentations, with explicit user identity by default. Preserve a selected bot workflow's identity. Reuse login; do not authenticate as a routine preflight.

## Choose the smallest edit

| Intent | Operation / reference |
|---|---|
| Read deck or one slide | [XML get](references/cli/lark-slides-xml-presentations-get.md) |
| New deck | [Create](references/cli/lark-slides-create.md); [add-slide](references/cli/lark-slides-add-slide.md) for incremental pages |
| Edit named text/image/block | [Replace-slide](references/cli/lark-slides-replace-slide.md), preserving other blocks/page order |
| Extensive page/background changes | [Update-slide](references/cli/lark-slides-update-slide.md), full-page replacement |
| Add/delete one page | [Add](references/cli/lark-slides-add-slide.md), [delete](references/cli/lark-slides-delete-slide.md) |
| User template or supplied PPTX | [Template editing](references/workflow/template-editing.md) |
| Screenshots | [Screenshot](references/cli/lark-slides-screenshot.md) |
| History/rollback | [History](references/cli/lark-slides-history.md) |

Read [editing](references/workflow/slides-editing.md) before existing-page edits. Full-page replacement deletes omitted elements; preserve their IDs/content unless removal was requested. Never create a replacement deck merely to edit the original.

## Planning and verification

For new decks or major rewrites, read [planning](references/planning-layer.md), [visual planning](references/visual-planning.md), and [asset planning](references/asset-planning.md). Keep the reusable plan in a task-specific temporary working directory; plan before XML. A tiny block edit does not need a deck-wide plan.

User style/template takes precedence. Choose density, images, diagrams, charts, and whitespace to fit the material and audience. Do not force every slide to contain stock imagery, a fixed number of cards, or hundreds of words. Avoid invented facts and meaningless decoration.

Before generating XML, read the [quick reference](references/xml/xml-schema-quick-ref.md); the [XML definition](references/xml/slides_xml_schema_definition.xml) is the authoritative grammar. Before submitting complete slides through create/add/update, save XML and run [xml_lint.py](scripts/xml_lint.py) via uv. Correct structural/layout errors. After substantial writes, read back XML, check page count and key elements, and follow [validation](references/workflow/validation-xml.md). Inspect screenshots when assessing actual rendered layout. Use [error handling](references/workflow/error-handling.md) for partial writes, blank pages, or `3350001`; query existing state before retrying creation.

Deliver the real presentation link in the conversation; no particular notification tool is required. Clean temporary planning/XML/screenshot artifacts after use unless requested as deliverables.

## XML invariants

- Canvas is 960 × 540; keep content in bounds.
- Direct children of `<slide>` are `<style>`, `<data>`, and `<note>`. Put visible elements in `<data>`.
- Text uses `<content><p>...</p></content>`, with explicit `fontSize` and `color` (not `fontColor`). For long/large text use `wrap="true" autoFit="normal-auto-fit"`. Line spacing uses `multiple:<value>` or `fixed:<value>`.
- Images use `<img>`, not `<image>`. Rectangles are shapes, not containers; place text/images/icons as siblings with coordinates.
- Native supported charts use `<chart>`; read the [chart example](references/xml/slides_chart_demo.xml). Omit `<chartLegend>` to hide it; `position="none"` is invalid. Other diagrams may use shapes/lines.
- Tables use `<table>`, not `<shape type="table">`. Set table width/height and explicit row/column dimensions when preserving them. A cell accepts fill/content/borders, not nested shapes/images/icons.
- Gradients use `<fill><fillColor color="linear-gradient(135deg, rgba(15,23,42,1) 0%, rgba(56,97,140,1) 100%)"/></fill>`; RGB without alpha or missing percentage stops may render white.
- Resolve IconPark names with [iconpark_tool.py](scripts/iconpark_tool.py), not guesses; read [IconPark](references/xml/iconpark.md). Set icon fills and sufficient contrast.
- For block patches, `block_replace` uses JSON field `replacement`; `block_insert` uses `insertion`. These are not the XML `<content>` element.

## Tokens, media, and paths

Preserve `xml_presentation_id`, `slide_id`, and `revision_id`. History rollback needs `history_version_id`, not revision ID. `--presentation` shortcuts resolve Slides/Wiki URLs; a bare Wiki node token is not a presentation ID. Manual node resolution must use the same identity and verify `obj_type == "slides"`.

Images require uploaded `file_token` values; external HTTP URLs do not render reliably. Use [media upload](references/cli/lark-slides-media-upload.md) (maximum 20 MB), or supported `<img src="@./path">` placeholders. Downloads return the actual local `path`; do not guess filenames. Screenshots take at most ten pages per serial batch and return actual output paths.

CLI output files are cwd-relative. Run in a temporary task directory where appropriate; invoke packaged Python helpers through `uv run --project "<lark-root>" --locked python "<lark-root>/references/slides/scripts/<script>.py"` without changing cwd just to locate helpers.

## Operation references
