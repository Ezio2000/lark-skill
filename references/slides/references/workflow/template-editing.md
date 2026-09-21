# PPT Template Rewrite Principles

Core principle: a template is not a style reference, but an editing base that must be followed.

## Import First

If the template provided by the user is in PPTX format, first import the template into Lark Slides. The subsequent writing target is the imported Slides, not a newly created deck detached from the template, and not a PPTX that is first redrawn locally and then imported.

Use the following command directly; there is no need to load the `lark-drive` Skill first:

```bash
lark-cli drive +import --as user --file "<template.pptx>" --type slides --json
```

Optional parameters: use `--name "<title>"` to specify the title of the imported Slides; use `--folder-token <FOLDER_TOKEN>` to specify the target folder. If `ready=false` / `timed_out=true` is returned, directly execute the `next_command` in the returned value; the equivalent form is:

```bash
lark-cli drive +task_result --scenario import --ticket <TICKET>
```

## Read Before Editing

After importing, you must read the Slides content and understand the actual layout, fonts, hierarchy, images, charts, shapes, tables, and text containers of each page. The reading result is the source of truth for subsequent editing.

When reading a page, at minimum determine:

- The role the page originally serves, such as cover, section page, table of contents, process, comparison, data, or summary.
- The main layout structure of the page, such as image-text relationships, arrows, timelines, nodes, tables, charts, left-right comparisons, background images, or product images.
- Which text boxes, shape labels, table cells, or chart labels carry content.
- The fonts, font sizes, colors, alignment, hierarchy, and whitespace relationships of the original page.

## Edit The Imported Slides Directly

After understanding the pages, edit directly on the imported Slides. Permitted operations include:

- Filling in, replacing, condensing, or deleting text.
- Replacing or adding images.
- Updating the content in charts, tables, numeric labels, or node labels.
- Copying, deleting, or rearranging template pages as needed.
- Making local, small-scale additions of elements when the source page has no suitable place to carry them.

Newly added elements may only fill content gaps and must not become a new main layout. The main body of the page should still be carried by the template's original layout.

## Preserve Design

Editing must strictly follow the original layout and fonts, changing only content and not doing design.

By default, preserve:

- Page layout, visual hierarchy, whitespace, and alignment relationships.
- The original fonts, font size system, colors, text box positions, and shape order.
- Background images, images, logos, charts, tables, decorative shapes, lines, icons, and page structure.
- The differences between different page types in the template.

Do not transform template pages into uniform generic cards, blank layout boards, title bars, three-column layouts, 2x2 cards, or large-area masks. Do not treat the template as a background image and then start a separate design system.

## Content Only

Content must preferentially go into the text boxes, shape labels, nodes, table cells, chart labels, or annotation containers already present on the original page.

If the original container has insufficient space, prioritize:

- Condensing the text.
- Reducing the font size while keeping the original font system.
- Splitting into existing nearby containers on the page.
- Using the template's existing annotation, label, or supplementary explanation areas.
- Copying the native container style from the same page or the same template for local supplementation.

Do not redraw the main page structure just to accommodate long copy. Do not use newly added large cards to cover the original charts, arrows, images, background, or key shapes.

## Readback And Tune

After completing the edits, you must read back the result and fine-tune page by page.

During readback, focus on checking:

- Whether text overflows, is truncated, crosses lines, or exceeds the container.
- Whether text obscures images, charts, shapes, arrows, nodes, or other text.
- Whether the shape order causes content to be covered or obscured.
- Whether new content still falls within the template's original layout, rather than covering the template structure.
- Whether fonts, font sizes, colors, alignment, and hierarchy still stay close to the original page.

When text overflow is found, prioritize condensing the text or reducing the font size. When obscuring is found, resolve it by adjusting the shape order, local positions, or reusing existing blank areas. Only when these methods cannot satisfy the content expression should you make local additions or deletions.

The completion standard is "the original template's layout, fonts, and visual structure still clearly exist, the content has been accurately replaced, and after readback there is no overflow or obscuring."
