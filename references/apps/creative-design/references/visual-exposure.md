<a id="可视化报告与专题表达"></a>
# Visual reports and feature presentation

Create content-driven HTML visual works. It can be a one-page long report, a feature visual page, a visual long image, an infographic, a canvas-style design draft, or a browsing-oriented report with a small amount of light interaction; the specific form is determined by the user's goals, the volume of material, and the reading scenario, and no fixed template is presupposed.

<a id="工作方式"></a>
## Working approach

1. First read the user's material, and extract the theme, audience, reading scenario, core conclusions, facts that must appear, and details that can be omitted.
2. Determine the purpose of the report: reporting, explaining, disclosing, persuading, communicating, archiving, or exploring a visual direction.
3. Choose the delivery form: long-page report, feature page, visual long image, single-screen summary, canvas-style multiple options, text-image mixed report, formal report with a print feel, etc. Do not compress all requirements into the same layout.
4. Organize the content according to the logic of the material, rather than applying a fixed table of contents, fixed modules, or a fixed visual template. Reference styles can only inspire the mode of expression; they cannot replace judgment about the current material.
5. Break the material into specific reading tasks: what judgment should this section lead the reader to make, what relationship should they understand, what fact should they remember, what difference should they compare, what process should they track, what evidence should they believe. Do not turn these task names directly into a table of contents or module titles.
6. Generate suitable components, visuals, and layouts on the spot for each reading task: first explain what mode of expression this section of content needs, then turn it into a concrete combination of UI / graphics / typography / charts / screenshots / text. You may create new structures and visual metaphors, unrestricted by existing component names; avoid having all sections share the same set of component combinations.
7. First write a style brief: thematic metaphor, audience stance, material language, color logic, and signature elements. A financial report can resemble a formal report booklet, an employee survey can resemble an organizational research archive, and a product launch summary can resemble a brand battle report; these are only inspirations, and must be derived from the user's material.
8. Establish a layout system: canvas size, grid, font-size hierarchy, color, icon/line language, emphasis methods, and section rhythm. The layout system must explain how different sections vary, rather than having all sections use the same top-to-bottom structure.
9. Produce a single HTML document. When the user's requirements are clear, do it directly; only when the theme, materials, or delivery form are completely impossible to determine should you ask a small number of necessary questions.

<a id="内容组织"></a>
## Content organization

The report forms, modes of expression, components, and layouts that appear in this module are only illustrative, not a checklist that must be referenced. The most important thing is to generate, based on the user's needs and the material content, a structure that can explain the report clearly: why the reader should look, what to look at first, how to understand relationships, where the evidence is, and what judgment is ultimately formed should all naturally hold within the structure.

A visual report is not about filling the page with charts, nor about cutting text into many cards. Each information block must serve a real reading action in the current material: letting the reader confirm the object, grasp the key point, understand relationships, compare differences, locate evidence, see the process, identify risks, or form a next-step judgment. Translate these reading actions into a visual structure exclusive to this requirement, rather than reusing fixed module names.

You are allowed to reinvent the expression structure for the current requirement: you may merge, split, enlarge, weaken, expand horizontally, narrate vertically, turn into graphics, turn into tables, turn into screenshots, or create a completely different layout. As long as it can explain the report content more clearly, it takes priority over any example component or common layout.

If the material is very long, first compress it into a report narrative; do not lay out the full original text. When precise number lookup is needed, use tables or an appendix; when rapid communication is needed, use summaries and visual highlights; when formal reporting is needed, retain section numbering, chart titles, and scope notes.

Do not compress key content into an appendix fragment in the corner. The parts the user explicitly asks to display should be given sufficient layout weight according to the report's goals, and a suitable information structure should be chosen to carry them.

<a id="版式策略"></a>
## Layout strategy

A visual report should feel like a feature that has undergone editorial design, not a long page pieced together from identical cards. First decide the reading rhythm, then place components:

- Design the layout according to how the material unfolds: it may need continuous narrative, dense evidence, spatial relationships, process progression, comparative judgment, an immersive key visual, a formal report booklet, or a completely different structure. First name a layout concept for the current requirement, then determine the grid, density, visual center of gravity, and section variation.
- Layout variation comes from content relationships, not from padding out components. Key sections can be enlarged, split across pages, turned into full-bleed layouts, turned into graphics, or turned into precise tables; secondary sections can be compressed, placed side by side, tucked into notes, or weakened.
- Each section's structure can differ, but it must belong to the same visual system. The variation must be explainable: why a wide image suits this place, a dense table suits that place, and segmented narrative suits another place.

Do not place decorations randomly just to be "rich." Variation should come from content relationships and reading tasks, not from padding the page with items from a component list.

<a id="视觉原则"></a>
## Visual principles

- Clarity first, beauty second. Readers should first understand the structure, then feel the style.
- Light and dark themes are determined by the requirement, brand, material, audience, and reading scenario; light, dark, neutral, or partially dark are all acceptable. After choosing, ensure contrast, readability, and information hierarchy, and be able to explain why it suits the current theme.
- Default to a flat treatment: content areas should prioritize thin borders, divider lines, light background colors, color blocks, table zebra striping, numbering, and labels to establish hierarchy; do not add all kinds of `box-shadow` to sections, cards, or chart containers.
- Use decorative gradients, glows, and glassmorphism sparingly. Visual effects should help group, emphasize, or guide the eye.
- Style follows content, audience, and brand: it can be formal, gentle, technical, editorial, branded, or experimental, but do not inherit fixed colors, a fixed table of contents, or fixed components from some sample scenario.
- Each report should have an explainable signature element. The signature element should be generated from the user's theme, the texture of the material, and the reading tasks, rather than reusing a fixed technique; it can be any visual rule that can organize content, create a memorable point, and maintain consistency.
- Real material first: screenshots, logos, images, icons, and data snippets provided by the user should be used first. When there is no material, use clear placeholder structures and replaceable copy.
- A small amount of motion is allowed, but only for entrance, emphasis, or guiding reading; do not use continuous animation that interferes with understanding.
- Numbers, charts, and tables may be included, but they serve the report narrative; do not turn all content into graphics just for the sake of "visualization."
- Dark areas can be used for the cover, conclusion, action area, or the key visual of the entire report; as long as it serves the thematic tone and reading experience, rather than being an unfounded decoration.

<a id="画布与交付"></a>
## Canvas and delivery

- Multiple options, design drafts, direction exploration: use `design-canvas.jsx`, with one `<DCArtboard>` per direction.
- A single visual report, visual long image, or feature visual draft: make it a complete HTML page, maintaining a clear canvas size, rhythm, and hierarchy.
- If the user wants a "design draft," prioritize canvas-style delivery; if the user wants something "directly presentable/shareable," it can be made into a complete page-style visual work.
- All text should be written directly in the HTML, making it easy for the user to edit later.

<a id="检查清单"></a>
## Checklist

- The delivery form matches the user's needs: long-page report, feature page, long image, canvas design draft, or single-screen summary, rather than being bound by a fixed template.
- The theme, boundaries, and most important information of the current requirement are clearly visible on the first screen or in the opening.
- Section order follows the logic of the material, and does not apply a table of contents based on evaluation set samples or preset scenarios.
- Section layouts have rhythmic variation, and the variation comes from material relationships; there is no uniform top-to-bottom card layout throughout, and no structure is forced together because of a preset component list.
- There are no large blank areas, misalignment, low contrast, unreadable text, or abrupt style differences between modules.
- Content areas remain flat, without abuse of shadows, glows, glassmorphism, or heavy floating effects.
- All expression carriers perform their own roles; there is no piling up of charts for the sake of data, and no filling of space with vague text or preset components.
- Text density is readable, with no stacking of tiny text.
- Icons, lines, colors, and card styles belong to the same visual language.
- The light/dark choice can explain why it suits this theme; whether light or dark, long text, charts, and tables remain readable.
- Factual content is not fabricated; uncertain content uses neutral descriptions or placeholder notes.
