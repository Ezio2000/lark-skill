# Complex document creation

Use for long documents, strict layouts, mixed media, and multiple Lark components. Short prose/lists or complete supplied text can use [create](lark-doc-create.md) directly.

## Structure and format

Organize around the audience, evidence, and user's requirements. Preserve a supplied template. Load a genre only if it changes the structure:

- Decisions/execution: [workplace](genres/route-workplace.md); evidence/data: [report](genres/route-report.md); tutorials/reference: [knowledge](genres/route-knowledge.md).
- Reporting: [media](genres/route-media.md); argument: [opinion](genres/route-opinion.md); reviews: [consumer](genres/route-consumer.md); stories: [creative](genres/route-creative.md).
- Specific distribution needs: [platform](genres/route-platform.md), [marketing](genres/route-marketing.md), or [personal brand](genres/route-personal-brand.md).

Markdown is suitable for simple structures. Use [XML](lark-doc-xml.md) for precise styles, complex blocks, whiteboards, or HTML components; read [extended blocks](lark-doc-xml-extended-blocks.md) only when used. Add visuals when they aid understanding or are requested, not to meet an arbitrary quota.

## Optional quantified draft

If the user specifies word counts, component counts, or strict formats, `docs +script --command init-draft` can record the baseline; otherwise author XML directly in a temporary directory. Read [script commands](lark-doc-script.md) before using them.

Derive `presentation-decision` from the actual task. Set `word_count` only for an explicit requirement. `visual_plan.blocks` records count-constrained components; use an empty array when none are required. The CLI returns `data.cwd`, `data.workspace`, and `data.draft_path`, but does not generate XML body content. Keep later file references consistent with that cwd.

## Generate and validate

Write complete content and check facts, sources, and user constraints. Resolve local assets according to the selected format's cwd rules.

Validate XML through `docs +script --command parse`. Top-level `ok` means invocation success, while constraint results are in `data.assessment.status`; use diagnostics for focused repairs. Constraints not enabled in the parser still need checking, and local parsing does not replace server validation. A small existing-title edit uses [update](lark-doc-update.md), not the creation workflow.

## Create and deliver

Use [create](lark-doc-create.md) once and retain the returned document ID/URL. Inspect warnings and repair partial failures in that document instead of creating duplicates. Read back when necessary to confirm complex blocks, layout, or server conversion.

Return the real link and relevant limitations. Clean temporary drafts/parse output after verification unless they are requested deliverables or still required for ongoing editing.
