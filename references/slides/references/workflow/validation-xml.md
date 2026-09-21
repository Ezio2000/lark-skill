# Validation Checklist

After creating, substantially rewriting a presentation, or writing back a full page, an explicit validation must be performed. The goal is to find blank pages, XML corruption, truncated content, obvious overflow, weak visual hierarchy, and unverified output.

Small edits to existing pages also require validation of the corresponding scope: at minimum, read the modified page or the full XML to confirm the target element has been updated and the surrounding structure has not been broken.

## Required Flow

1. Record the `xml_presentation_id` returned by creation or editing, as well as the known `slide_id` / `revision_id`.
2. Use `slides +xml-get` to read back the full XML to a local file.
3. Check whether the actual page count matches the plan or the user's requirement.
4. Check whether each page's `<data>` contains the expected main elements.
5. Check that there are no obvious blank pages, broken pages, missing titles, or missing main visuals.
6. Check that the pages have not all degenerated into a title plus bullet list.
7. Check the visual hierarchy: title, main visual, and supporting information are distinguishable.
8. Check for obvious overflow and layout risks: overlap, out-of-bounds, bottom crowding, long text boxes.
9. Provide a brief verification record in the final reply.

Read-back command:

```bash
lark-cli slides +xml-get --as user \
  --presentation "YOUR_ID" \
  --output .lark-slides/plan/<deck-or-task-id>/readback.xml \
  --json
```

## Automated XML Layout Lint

After `slides +xml-get` saves the XML, run only the unified layout gate. First obtain the parent directory of the currently loaded `lark-slides/index.md`, recorded as `<lark-root>/references/slides`; do not guess the global installation path.

```bash
uv run python "<lark-root>/references/slides/scripts/xml_lint.py" --input <presentation.xml>
```

It checks in one pass: XML/SXSD validity, element out-of-bounds, text overlap, blank pages, text height risk, full-page content sparsity, and large-card content coverage. The estimated text area of a large card's own `<content>` participates in the coverage union calculation together with peer elements inside the card.

Gate rules:

- `summary.error_count > 0` or `summary.release_ready == false`: blocks creation, replacement, or delivery; must be fixed first.
- `summary.warning_count > 0`: static checks do not directly block, but `summary.screenshot_review_required == true`, and the corresponding page screenshot must be reviewed.
- When `slides[].status` is `blocked`, `needs_screenshot_review`, or `passed`, it can directly determine the per-page follow-up action.
- The CLI exits with code 1 when `error` exists; when there is only `warning`, it still outputs JSON and exits 0, allowing the screenshot review chain to continue.

Each `error` / `warning` contains:

- `element_ids`: the relevant XML element ID;
- `rule`: rule ID, name, threshold, and comparison relationship;
- `measurement`: measured values such as out-of-bounds amount, overlap area, coverage rate;
- `related_objects`: the type, coordinate box of the relevant object, and an XPath-like `xml_path` pointing to the current input XML node;
- `target`, `message`, `hint`: page number, semantic description, and handling suggestion.

When `sparse_container_content.measurement.content_coverage_ratio < rule.threshold`, you need to judge together with the same-page screenshot whether the whitespace is intentional design; do not automatically expand content based on a warning alone.

Handling directions for common codes:

| code | meaning | handling |
|------|------|----------|
| `xml_not_well_formed` | XML syntax error or unescaped text | Fix tag closure, attribute quotes, `&` / `<` / `>` escaping |
| `sml_prefixed_tag` | SML element uses a namespace prefix, such as `<ns0:slide>` or `<sml:shape>` | Use the default namespace of `<slide xmlns="https://www.larkoffice.com/sml/2.0">`, or use unprefixed tags |
| `sxsd_unsupported_tag` | A tag not supported by SXSD is used | Replace with a supported tag according to lint `hint`; common examples include `textbox -> <shape type="text">`, `image -> <img>` |
| `sxsd_unsupported_attr` | An unsupported attribute is used on a supported tag | Change to a supported attribute according to lint `hint`; common examples include `x -> topLeftX`, `fontColor -> color` |
| `iconpark_unsupported_icon_type` | `<icon>` uses a `iconType` that does not exist in `iconpark-index.json` | Change to a `iconType` in the list according to lint `hint`, or first search with `scripts/iconpark_tool.py` |
| `icon_missing_fill_color` | The visual specification requires `<icon>` to set `<fill><fillColor color="..."/></fill>`, to avoid the icon being invisible | Add an explicit non-transparent fill color to `<icon>`, for example `rgba(37, 99, 235, 1)` |
| `icon_transparent_fill_color` | `<icon>`'s `fillColor` is a transparent color, which does not meet the visual visibility requirement | Change it to a non-transparent color with sufficient contrast against the background |
| `bbox_overlap` | The estimated drawing areas of text elements clearly overlap | Separate the text coordinates, shrink the text box/font size, or change to a clear column/group structure |
| `*_out_of_canvas` | Element boundaries exceed the page canvas | Move back onto the canvas or reduce the size according to `measurement.overflow` |
| `blank_slide` | The page has no visible content within the canvas | Add main content; only an empty background or empty shapes cannot pass the gate |
| `sparse_container_content` | Large-card content coverage is below the threshold | Locate the card according to `related_objects[].xml_path`; when `element_id` exists and is unique, it can also be located by ID, then judge together with the screenshot whether to add or enlarge content |
| `sparse_slide_content` | Full-page effective content coverage is low | Review the screenshot to confirm whether it is intentional whitespace |

## Screenshot QA

After obtaining page screenshots, visual acceptance must be performed; do not claim that screenshot acceptance passed based only on XML read-back or static lint conclusions. During acceptance, assume the pages have problems, and actively look for and report all risks, including minor issues.

```text
Please visually inspect these slide screenshots page by page. First assume problems exist, and try to find them.

Key checks:
- Element overlap: text and shapes, images, or charts obscuring each other, lines crossing through text, cards or labels stacking.
- Text overflow or clipping: truncated near page edges, text box boundaries, or card boundaries.
- Decorative elements in the wrong position: divider lines, emphasis lines, or label backplates are laid out for a single line of text, but after the title or body text wraps, they press on the text or the distance becomes abnormal.
- Source annotations, footers, or page numbers colliding with the content above.
- Elements too close together: spacing between adjacent elements is clearly insufficient, cards or sections are almost touching; estimated on a 960x540 canvas, gaps smaller than about 15 px usually need to be flagged.
- Uneven spacing: local whitespace is too large, while another area is too crowded.
- Insufficient page margins: main content is close to the slide edge; estimated on a 960x540 canvas, outer margins smaller than about 30 px usually need to be flagged.
- Columns, cards, icons, or similar elements are not stably aligned.
- Image or chart rendering abnormalities: blank, distorted, low-resolution, key content unreadable, or expected graphics missing.
- Insufficient text contrast, for example light gray text on a beige or light background.
- Insufficient icon contrast, for example dark icons on a dark background without a light circle or backplate supporting them.
- Text boxes too narrow, causing unnecessary frequent line wrapping.
- Residual placeholders, template default text, or unreplaced content.

For each page, list the problems or suspicious areas found separately, and record them even if they are only minor issues.

Report all problems found, including minor issues.
```

Whether to fix must be decided based on problem severity: blank pages, broken images, text occlusion, obvious clipping, unreadable low contrast, residual placeholders, etc. must be fixed before delivery; if minor spacing or alignment issues are not fixed, the final verification record must state the known risks.

## Page Count And Structure

- The actual page count must equal the user's requirement or the page count of `slide_plan.json`.
- If the creation process partially fails, first record the `xml_presentation_id` already created, then read back to confirm which pages have been written.
- Each page should contain `<data>`, and `<data>` should contain at least one non-background main element.
- Cover pages, section pages, and summary pages may have less text, but cannot have only an empty background.
- Technical explanation pages, comparison pages, process pages, and architecture pages must have matching structural elements, such as group boxes, connectors, timelines, tables, or graphical areas.

## Expected Elements

Check page by page according to `slide_plan.json` and the user's requirements:

- The title or main conclusion exists and can correspond to `key_message`.
- The main structure corresponding to `layout_type` has been generated.
- `visual_focus` is one of the most prominent or largest information areas on the page.
- `text_density` affected the amount of text; a long bullet box was not used to replace planning.
- When real assets are available, `asset_need` has been placed in the correct area; when there are no real assets, `fallback_if_missing` has been covered with XML shapes, lines, labels, tables, or charts.

If the user specified key pages, such as "architecture explanation", "Self-Attention mechanism explanation", "comparison or evolution perspective", "summary page", the final verification record must state item by item that these pages exist.

## Blank Or Broken Page Signals

Treat the following situations as requiring fixes before delivery:

- `<data/>` is empty, or contains only background, decorative lines, or empty `<content/>`.
- Key text does not appear in the read-back XML.
- Images are still `@./path`, or `<img src>` is an http(s) external link.
- The image area the page depends on is empty, and there is no fallback visual.
- The returned XML is missing pages, the page order is clearly wrong, or some page content was truncated by the shell.
- A large number of shapes have exactly the same coordinates, causing main content to overlap.
- The gradient background falls back to blank or a white background, making text unreadable.

## Layout And Overflow Risk

Prioritize fixing these obvious risks:

- Body text or label boxes have insufficient height, and text is very likely to be clipped.
- Multiple main elements overlap in the same area, rather than intentionally layering backgrounds.
- Important content crosses the canvas boundary, or is close to the bottom beyond `y=500`.
- High-density pages use a single long bullet list, without columns, tables, or grouping.
- The font size and color differences among title, main visual, and body text are too weak, and the visual hierarchy is unclear.
- All content pages use the same set of title-plus-bullets coordinates.

## Verification Record

The final reply must include a brief verification record; suggested format:

```text
Verification record:
- Read-back: executed slides +xml-get, actual page count N / expected N.
- Key pages: architecture explanation / Self-Attention / comparison or evolution / summary page all exist.
- Structure: checked main shape/img/table/chart elements, no obvious blank pages or broken pages.
- Layout: checked title hierarchy, main visual, overlap/out-of-bounds/text overflow risks.
```

Do not claim that manual visual acceptance has been completed unless the visual result was actually opened or obtained. Conclusions derived only from static XML checks should be stated as "static checks found no obvious problems".
