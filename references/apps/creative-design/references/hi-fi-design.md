<a id="高保真设计"></a>
# High-Fidelity Design

Create high-fidelity, finely polished designs.

Follow this general design process (keep it in mind with a todo list):
1. Clarify key information: if it can be reasonably inferred from requirements, attachments, screenshots, or common patterns, just continue; only ask the user when key information is missing and would affect the design direction
2. Find existing UI kits and gather design context—copy all relevant components, read all relevant examples; if none can be found and it would affect the core design direction, then ask the user
3. Write down assumptions, context, and design reasoning at the beginning of the file, place design placeholders, and show them to the user as early as possible
4. Produce the design as quickly as possible, show it to the user again, and include suggestions for next steps
5. Use tools to inspect, validate, and iterate on the design

Good high-fidelity designs do not start from scratch—they are rooted in existing design context. Find suitable UI kits / design resources, or extract design rules from screenshots, code, and brand assets. You must spend time obtaining design context, including components. If materials are missing but do not affect the core direction, continue first with reasonable assumptions; only ask the user when the missing information would change the design direction. Mocking an entire product from scratch is a last resort and will lead to low-quality designs. Using starter components (device frames, etc.) gives you high-quality scaffolding for free.

When presenting multiple options or exploration directions side by side, keep the layout clear: give the page a neutral gray background, place each option in its own labeled box (a small heading + a white rounded card whose size adapts to the content), and group related options together.

When designing, asking good questions is important—but only ask when the question would materially affect the design direction, and avoid interrupting the user frequently.

Provide options: by default, offer 2-3 options with clear differences (consistent with the default in the "Ask Questions" section of [`../creative-design.md`](../creative-design.md)); when the user explicitly requests broad exploration, expand to more variants across multiple dimensions. Mix safe options that follow existing patterns with novel interaction approaches, including interesting layouts, metaphors, and visual styles. Have some options use color or advanced CSS, some with icons, and some without. Variants should start from the basics and gradually move toward more advanced and more creative directions! Try remixing brand assets and visual DNA in interesting ways—play with scale, fill, texture, visual rhythm, hierarchy, novel layouts, and typography treatments. The goal is not to find the perfect option, but to explore atomic-level variants that users can mix and match.

CSS, HTML, JS, and SVG are powerful. Users often do not know what they can do. Surprise the user.
