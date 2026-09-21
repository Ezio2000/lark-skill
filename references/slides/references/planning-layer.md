# Planning Layer

For a new deck or major page rewrite, write `.lark-slides/plan/<deck-or-task-id>/slide_plan.json` before XML. Use a task-specific temporary working directory unless the user requested retained project artifacts. The plan records narrative, page roles, geometry, visual focus, and text density.

Small existing-page edits (one title, number, block, or image) do not need a new plan. A new deck, multi-page restructuring, or full-page redesign does.

## Required Flow

1. Resolve the requested topic, audience, page count, and style; ask only for material missing choices.
2. Create a unique task/deck plan directory and write `slide_plan.json`.
3. Read the [XML quick reference](xml/xml-schema-quick-ref.md), [visual planning](visual-planning.md), and [asset planning](asset-planning.md).
4. Translate layout/focus/density into actual XML geometry, with task-appropriate fallbacks for missing assets.
5. After creation, read back with `slides +xml-get` and verify page count, key elements, and plan correspondence. A blank presentation contains no slide elements.


## Plan Path

Use a separate plan directory per deck or task so multiple presentations in the same workspace cannot overwrite each other.

Recommended IDs:

- New deck before creation: title slug plus date/time, such as `q3-review-20260507-1805`.
- Existing PPT rewrite: the `xml_presentation_id`.
- Ambiguous or untitled task: short task slug plus date/time.

Rules:

- Do not reuse `.lark-slides/plan/slide_plan.json` as a shared path.
- Create the directory before writing the file.
- Reuse the same plan path for XML generation and post-create verification for that deck.

## Artifact Lifecycle

`.lark-slides/` is local agent state. It supports recovery, iteration, and later edits, but it should not be treated as source code or committed by default.

Keep the plan and resource IDs while creation, recovery, or current follow-up editing is in progress. After successful delivery, retain files only when they are requested deliverables or necessary for a continuing task; otherwise clean the temporary plan along with transient XML/screenshots. Do not automatically add a manifest to the user's project.

Clean or avoid keeping:

- Transient XML payloads after successful creation and verification. Prefer `/tmp` for throwaway XML, or delete generated XML files after success.
- Stale XML drafts that no longer match the current presentation state.

Exception:

- If creation fails or partially succeeds, keep the relevant XML/debug payloads until recovery is complete. Record `xml_presentation_id` first, then fetch current state before retrying.

## JSON Shape

```json
{
  "presentation_goal": "Explain the proposal and secure approval for the next phase.",
  "audience": "Product and engineering leaders who know the domain but need a concise decision narrative.",
  "theme_style": "Clean business style, light background, restrained blue accent, strong visual hierarchy.",
  "visual_system": {
    "background_strategy": "Content pages use one light base; cover and closing may use a related dark treatment with the same accent system.",
    "motif": "Consistent card style and numbered anchors.",
    "color_roles": {
      "primary": "Used for the dominant structural motif and about 60-70% of visual weight.",
      "secondary": "Used for grouped regions, comparison panels, or supporting categories.",
      "accent": "Used only for key numbers, conclusions, or focus markers."
    }
  },
  "typography_constraints": {
    "title_max_lines": 2,
    "body_max_lines_per_box": 2,
    "footer_max_lines": 1,
    "long_text_handling": "Shorten, split into multiple boxes, or move detail to speaker notes instead of shrinking into a tight box."
  },
  "verification_plan": {
    "check_background_consistency": true,
    "check_text_fit": true,
    "check_visual_focus": true,
    "check_asset_rendering": true
  },
  "slides": [
    {
      "page": 1,
      "title": "Proposal Title",
      "key_message": "The initiative is ready for a focused pilot.",
      "layout_type": "title-cover",
      "visual_focus": "Large title area with one concise supporting statement.",
      "asset_need": {
        "asset_type": "logo",
        "purpose": "Signal product or team identity on the opening page.",
        "suggested_query": "product logo",
        "fallback_if_missing": "Use the actual product name as text; do not invent a replacement brand mark."
      },
      "text_density": "low",
      "speaker_intent": "Frame the decision and establish the deck's point of view."
    }
  ]
}
```

## Required Fields

Top-level fields:

- `presentation_goal`: what the whole deck is trying to achieve.
- `audience`: target readers or listeners and their assumed background.
- `theme_style`: visual tone, palette direction, and professional style.
- `visual_system`: deck-level visual rules that must stay stable across pages, including background strategy, recurring motif, and color roles.
- `typography_constraints`: deck-level limits for line count, text box density, and how to handle long text before XML generation.
- `verification_plan`: explicit checks to perform after creation or major edits; include background consistency, text fit, visual focus, and asset rendering when relevant.
- `slides`: ordered page plans.

Each slide must include:

- `page`: 1-based page number.
- `title`: slide title.
- `key_message`: the one idea this page must land.
- `layout_type`: planned page structure.
- `visual_focus`: dominant visual object or region.
- `asset_need`: planning-only structured asset metadata; no search, download, or upload required. Follow `asset-planning.md`.
- `text_density`: `low`, `medium`, or `high`.
- `speaker_intent`: why the speaker needs this page and how it advances the story.

Optional slide fields:

- `chart_contract`: required when the page plan includes a standard data chart that `<chart>` supports. Use this shape:

```json
{
  "chart_contract": {
    "required": true,
    "render_as": "native_chart",
    "chart_type": "line",
    "data_source": "mock_placeholder",
    "data_series_required": true,
    "placeholder_label_required": true,
    "manual_shape_fallback_allowed": false
  }
}
```

When `chart_contract.required == true`, XML generation must produce a `<chart>` element on that slide. A shape, line, or polyline approximation does not satisfy the plan.

`data_source` must be one of:

- `user_provided`: the user supplied concrete values, tables, CSV, or metric lists; use them and do not replace them with mock data.
- `mock_placeholder`: the user asked for a placeholder, template, example, or later-replaceable chart position; use mock data in native `<chart>`.
- `sourced`: values were obtained from a verifiable source within the task; retain that source. A factual chart request without data does not authorize inventing values. Retrieve a permitted source, ask for the missing data, or mark the chart as unavailable.

`data_series_required` means the XML must include `<chartData>`. Use real supplied/sourced values for factual charts. Labeled mock data is appropriate only for a requested example, template, or placeholder. Missing data must not silently become a fabricated series.

## Layout Vocabulary

Use one of these `layout_type` values unless the user explicitly needs a custom structure:

- `title-cover`
- `section-divider`
- `two-column`
- `image-left-text-right`
- `image-right-text-left`
- `big-number`
- `timeline`
- `comparison`
- `architecture-diagram`
- `process-flow`
- `quote-highlight`
- `conclusion`

The value must affect XML geometry, not just appear as a label. For example, `timeline` should create a horizontal or vertical sequence, `comparison` should create distinct side-by-side regions, and `big-number` should reserve dominant space for a large metric.

## Text Density Rules

- `low`: title plus 1 short statement, or 1-3 very short labels.
- `medium`: title plus 2-4 concise bullets or labeled regions.
- `high`: allowed only when the user needs detail; use tables, columns, or grouped regions instead of a long bullet list.

Do not let all pages become title + bullet slides. For decks of 4 or more pages, aim for at least 4 different `layout_type` values when the content allows it.

Text density must be realistic for the planned geometry. If a page needs long titles, bilingual labels, paper figure captions, legal disclaimers, or dense technical wording, record how the text will be shortened, split, or moved to speaker notes. Do not rely on small font sizes or tight boxes to make text fit.

## Visual System Planning

Before generating XML, define a visual system that can survive the whole deck:

- `background_strategy`: specify the default background for normal content pages, and which page roles may intentionally differ. Do not let pages drift through near-identical but inconsistent background colors.
- `motif`: choose one reusable structural device, such as numbered node, card treatment, half-bleed image zone, headline, or footer. The motif should appear consistently enough that pages feel related.
- `color_roles`: assign primary, secondary, and accent roles. The same color must not mean unrelated things across pages.
- `cover_content_relationship`: if the cover uses a different dark or image-led treatment, state how it connects to content pages through shared colors, motifs, or geometry.
- `closing_relationship`: if the closing page mirrors the cover, state that explicitly so it looks intentional rather than like a new theme.

These are planning constraints, not decoration notes. They must affect coordinates, background fills, shape styles, and text placement in generated XML.

## Iterative Deck State

When continuing an existing deck, update the same plan path rather than creating a new disconnected plan. Keep the plan aligned with what has actually been created.

Recommended optional fields for long-running work:

- `deck_status`: current slide count, target slide count if known, and last verified revision or timestamp.
- `created_slides`: page number, slide id when known, and the page role.
- `assets_used`: source, local path when applicable, uploaded token when known, and which page uses it.
- `open_issues`: known layout, text fit, asset, or consistency risks that still need correction.

Do not hard-code a page number just because a previous deck used that pattern. Plan by page role and evidence need, such as "method overview pages should use a figure when the source has a readable figure" instead of binding screenshots, charts, or diagrams to a fixed page index. The plan should describe decision rules, not a rigid template sequence.

## Asset Planning

`asset_need` is metadata. It can describe a desired figure, diagram, chart, icon, logo, screenshot, or fallback visual.

Use an object for one planned asset, an array for multiple real needs, or `asset_type: "none"` when no asset is useful. Each planned asset must include:

- `asset_type`: one of `paper_figure`, `architecture_diagram`, `icon`, `logo`, `chart`, `infographic`, `screenshot`, `flow_diagram`, or `none`.
- `purpose`: why this asset helps the page's key message.
- `suggested_query`: short future lookup hint only; do not execute it unless separately requested.
- `fallback_if_missing`: a concrete alternative consistent with user style and evidence, such as typography, a native diagram, a labeled mock in an illustrative task, or an explicit data gap. Generated imagery is optional, not mandatory.
- `chart_contract`: when `asset_type` is `chart` and the visual is a supported standard data chart, set this optional slide-level field so generation is locked to native `<chart>`.

For detailed rules and examples, read `asset-planning.md`.

Good examples:

- `{"asset_type":"architecture_diagram","purpose":"Explain component relationships.","suggested_query":"service architecture diagram","fallback_if_missing":"Render the component diagram with <shape> + <line>."}`
- `{"asset_type":"logo","purpose":"Identify the customer context.","suggested_query":"customer logo","fallback_if_missing":"Use the customer's name in text; do not invent its logo."}`
- `{"asset_type":"chart","purpose":"Show adoption trend.","suggested_query":"monthly adoption trend chart","fallback_if_missing":"Use a native chart with supplied or sourced values; if unavailable, report the missing series."}`

## XML Generation Contract

Before writing each slide XML, map the plan fields to concrete decisions:

- `key_message` determines the headline, dominant claim, or main takeaway.
- `layout_type` determines the coordinate structure and element types. Use `visual-planning.md` for concrete layout rules.
- `visual_focus` determines the largest visual region or emphasized object.
- `text_density` caps visible text volume.
- `asset_need` informs placeholder diagrams, icons, charts, screenshots, or fallback visuals only. Missing real assets must use `fallback_if_missing`, not blank regions.
- `chart_contract` locks supported standard data charts to native `<chart>` output. Manual approximations are allowed only when the planned chart type is unsupported by `<chart>` or when the visual is explicitly non-data/decorative.

After creating the PPT, fetch the presentation and verify:

- Page count matches the plan.
- Every page has the planned title and key message represented.
- At least several pages have visibly different XML layout structures.
- Planned `visual_focus` appears as a dominant visual region or object.
- Asset planning is proportional to the deck topic and length: technical, research, product, and analytical decks should include meaningful planned visuals where they clarify the story, and each planned asset has a visible fallback if no real asset was used.
- `text_density` is reflected in the amount of visible text.
- Pages are not crowded, and any planned `timeline`, `comparison`, or `architecture-diagram` page uses its matching visual structure.
- The actual backgrounds match `visual_system.background_strategy`; any dark, image-led, or emphasis page has an intentional relationship to the rest of the deck.
- Text boxes respect `typography_constraints`; long labels, captions, footer text, and conclusion bars are not squeezed into boxes that are too short for the intended line count.
- If real assets are used, the final XML contains renderable asset tokens or supported local placeholders for creation, not http URLs, stale local paths, or blank image boxes.
