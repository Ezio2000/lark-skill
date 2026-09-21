<a id="svg-编辑路径"></a>
# SVG Editing Path

Implement visual editing of an existing whiteboard by exporting the whiteboard's SVG → editing the SVG → writing it back to the whiteboard.

---

<a id="️-有损性警告"></a>
## ⚠️ Lossy Warning

SVG export is a **purely visual snapshot**; after re-importing, whiteboard semantics (mind map hierarchy/table structure/connector bindings/container types/mention/node ID/lock/comments) will be lost.

**Information preserved**: shape geometry (position/size/path), text content and basic formatting (font size/bold/italic/alignment), fill color/stroke color/opacity (linear gradients are downgraded to a solid color using the first stop-color), connector path shape and arrow style, basic grouping relationships nested in `<g>` (rebuilt as a DirectFocusGroup when there are ≥2 child elements).

---

## Workflow

<a id="0-用户确认强制"></a>
### 0. User Confirmation (Mandatory)

Before performing any edit, first determine whether the **immediately preceding user message** has explicitly confirmed the lossy edit:

- **Confirmed** (including proactive user pre-authorization, such as "I know it's lossy, just change it") → go directly to Step 1 without repeating the warning.
- **Not confirmed or ambiguous reply** → send the following sentence to the user verbatim, **then immediately end this turn and wait for a reply** — no export/edit/write-back commands or tool calls may be included in the same message:

> SVG editing only guarantees visual-layer alignment; whiteboard semantics (hierarchy/node types/mind map structure/table structure/connector bindings/container types/mention, etc.) will be unrecoverable. Continue?

This is **informed confirmation** (letting the user cut losses on semantic loss before acting); the actual destructive write will also go through a `--overwrite` dry-run confirmation once more in Step 4. The two have different responsibilities and neither can be omitted.

<a id="1-导出当前画板-svg"></a>
### 1. Export the Current Whiteboard SVG

```bash
lark-cli whiteboard +export \
  --whiteboard-token <TOKEN> \
  --output-type svg \
  --output <dir>/original.svg \
  --as user
```

<a id="2-编辑-svg"></a>
### 2. Edit the SVG

Make modifications on the exported SVG. Refer to [`svg.md` § How the Whiteboard Handles SVG](./svg.md#画板怎么处理-svg) to learn about recognizable elements and unsupported decorative features.

**Technical constraints**:
- New text must use `<text>` (not `<path>`), and leave enough container width (CJK ≈ 1em / Latin ≈ 0.6em)
- Avoid `skewX` / `skewY` / `matrix(...)` transforms
- Do not use `<radialGradient>` / `<filter>` / `<pattern>` / `<clipPath>` / `<mask>`

**Editing principles** (different from creating from scratch):

- **Consistent style**: newly added/modified elements should match the existing color scheme, font size, line width, and spacing style in the exported SVG, without introducing jarring visual differences
- **Minimal changes**: only modify the parts the user requested; do not proactively "optimize" or rearrange unrelated areas
- **Stable structure**: preserve the original `<g>` hierarchy as much as possible, avoiding unnecessary reorganization that changes grouping relationships
- **Connector coordination**: connector endpoint bindings have been lost; if a shape is moved, you must manually and synchronously adjust the endpoint coordinates of the connector path visually connected to that shape, otherwise the connector will "break"
- **Internal reference integrity**: do not arbitrarily delete or modify elements in `<defs>` that are referenced by `url(#id)` (`<marker>`/`<linearGradient>`, etc.) or modify their `id`, otherwise the referencing party will fail

<a id="3-渲染审查"></a>
### 3. Render Review

```bash
# Render PNG preview
npx -y @larksuite/whiteboard-cli@^0.2.13 -i <dir>/edited.svg -o <dir>/edited.png -f svg

# Geometry check (text-overflow / node-overlap)
npx -y @larksuite/whiteboard-cli@^0.2.13 -i <dir>/edited.svg -f svg --check
```

Adjust based on the PNG visual effect and the `--check` report; if there are issues, modify the SVG and re-render (at most 2 rounds).
- When previewing the SVG with local rendering, images in the whiteboard cannot display properly due to session reasons; this is expected behavior.

<a id="4-写回画板"></a>
### 4. Write Back to the Whiteboard

`--overwrite` will clear the original whiteboard content; execute only after confirmation

```bash
# dry-run probe
lark-cli whiteboard +update \
  --whiteboard-token <TOKEN> \
  --source @<dir>/edited.svg \
  --input_format svg \
  --idempotent-token <10+字符唯一串> \
  --overwrite --dry-run --as user

# Execute after user confirmation
lark-cli whiteboard +update \
  --whiteboard-token <TOKEN> \
  --source @<dir>/edited.svg \
  --input_format svg \
  --idempotent-token <10+字符唯一串> \
  --overwrite --as user
```
