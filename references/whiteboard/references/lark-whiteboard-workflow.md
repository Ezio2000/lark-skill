<a id="画板创作编辑工作流"></a>
# Whiteboard Creation/Editing Workflow

<a id="创作-workflow"></a>
## Creation Workflow

> This workflow is used to **independently create a single whiteboard**.
> When multiple whiteboards need to be created in bulk within a document, lark-doc handles the orchestration; see the `lark-doc` skill's `references/lark-doc-whiteboard.md`.

**Step 1: Obtain board_token**

| What the user provided | How to obtain it |
|---|---|
| Directly provided a whiteboard token (`wbcnXXX`) | Use it directly |
| Document URL or doc_id, and the document already contains a whiteboard | `lark-cli docs +fetch --doc <URL> --as user`, extract from the returned `<whiteboard token="xxx"/>` |
| Document URL or doc_id, and a new whiteboard needs to be created | `lark-cli docs +update --doc <doc_id> --command append --content '<whiteboard type="blank"></whiteboard>' --as user`, obtain from the response `data.new_blocks[0].block_token` (the one for `block_type == "whiteboard"`; for parameters see lark-doc index.md) |

**Step 2: Render & Write**

→ Go to the **[§ Render & Write Whiteboard](#渲染--写入画板)** section, complete the process, and return the result directly to the user.

---

<a id="编辑-workflow"></a>
## Editing Workflow

**Step 1: Obtain board_token** (same as Creation Workflow Step 1)

**Step 2: Detect editability / whether it was drawn by code**

- `+export --output-type source` — If it returns a single Mermaid/PlantUML source, the whiteboard was drawn by code and path ① can be used; if it returns no code/multiple diagrams, use paths ②③④

**Step 3: Choose an editing path** (match from top to bottom, stop at the first hit; if the user has explicitly specified, follow the user)

| Path | Match condition | How to modify | Write method | Lossy? |
|---|---|---|---|---|
| ① Source refactoring | `+export source` returns a single Mermaid/PlantUML (i.e., the whiteboard was drawn by code) | Modify the source → use `+update --input_format mermaid` or `+update --input_format plantuml` depending on the source type | overwrite (full board rebuild) | ⚠️ **Not strictly lossless, confirm before executing** |
| ② Attribute fine-tuning | Only changing the text/color of existing nodes | `+export --output-type raw --output <file>` (**must write to file**) → edit the target node fields in the file; if only `+update --input_format raw --source @<file> --overwrite` can be used to write back, first explain that it will rebuild the entire board and wait for user confirmation | overwrite (full board rebuild) | ⚠️ **Lossy risk, must not execute without confirmation** |
| ③ Incremental append | Add new diagrams/elements on top of the original, preserving the original content | `+export --output-type preview` → understand the original → `+export --output-type raw` → determine new node coordinates → [§ Render & Write Whiteboard](#渲染--写入画板) create & write | append (**do not add `--overwrite`**) | Lossless (original nodes untouched) |
| ④ Structural redraw | Requires geometric changes/adding or removing elements/structural adjustments/mixed editing | [`../routes/svg-edit.md`](../routes/svg-edit.md) | overwrite (clear and start over) | ⚠️ **Lossy, must first be confirmed by the user** |

**⚠️ Stop-loss**: Try a path at most 2 rounds; if it doesn't work, switch to another path and try once; if it still doesn't work, stop and truthfully tell the user where you're stuck. Do not jump back and forth between paths.

---

<a id="渲染--写入画板"></a>
## Render & Write Whiteboard

<a id="渲染路由"></a>
### Rendering routing

**First declare your identity**: Based on your training source, which family do you belong to? `Claude` / `Gemini` / `GPT` / `GLM` / `Doubao 或 Seed` / `Other`. Identity determines the SVG / DSL split (different families have uneven capabilities for these two expression languages), so do not skip this step.

**Then choose a path based on the current artifact type / diagram type × identity**, read the corresponding file, and execute according to its complete workflow (including reading the scene guide, generating content, render review, and delivery):

Current artifact routing matches from top to bottom, stop at the first hit:

| Diagram type               | Identity                                  | Path                                             |
|--------------------|-------------------------------------|------------------------------------------------|
| The content to be generated/appended currently contains @user mentions or images/illustrations | Any identity                                | [`../routes/dsl.md`](../routes/dsl.md)         |
| Mind map, sequence diagram, class diagram, pie chart, Gantt chart | Any identity                                | [`../routes/mermaid.md`](../routes/mermaid.md) |
| Fishbone diagram, pyramid diagram, flowchart    | `Doubao` / `Seed`                   | [`../routes/dsl.md`](../routes/dsl.md)         |
| Other diagrams               | `Claude` / `Gemini` / `GPT` / `GLM` / `Doubao` / `Seed`  | [`../routes/svg.md`](../routes/svg.md)         |
| Other diagrams               | `Other`                             | [`../routes/dsl.md`](../routes/dsl.md)         |

> **⚠️ SVG path failure fallback**: When using `routes/svg.md`, if you encounter any of the following → **discard the current SVG and instead read `routes/dsl.md` to redraw from scratch; do not patch line by line**:
> - The render command directly errors out (syntax-level crash, not a warn/error from `--check`)
> - Two rounds of rewriting still cannot eliminate the `text-overflow` error from `--check`
> - The PNG visually looks severely corrupted (large-scale text overflow, elements overlapping and covering key information, overall layout collapse)
>
> Patching SVG source often introduces new bugs; switching to DSL and redrawing from scratch is often more stable. This is the hard fallback for free-form SVG path work; do not intrude into `routes/svg.md`'s creation workflow.

<a id="产物规范"></a>
### Artifact specifications

Artifact directory: `./diagrams/YYYY-MM-DDTHHMMSS/` (local time, without colons and timezone suffix). If the user specifies a path, follow the user.

Fixed file names within the directory:

```
diagram.svg           ← SVG source (SVG path)
diagram.mmd           ← Mermaid source (Mermaid path)
diagram.json          ← DSL source file (DSL path) / OpenAPI JSON (SVG path exported from diagram.svg)
diagram.gen.cjs       ← Coordinate calculation script (only for the DSL script build method)
diagram.png           ← Render result
```

<a id="写入画板"></a>
### Write to whiteboard

When writing to the whiteboard, choose `+update --input_format` based on the final artifact type:

- When writing Mermaid / PlantUML / SVG artifacts directly, `--input_format` takes the single value `mermaid` / `plantuml` / `svg`; when writing to a non-empty existing whiteboard and overwrite is needed, first confirm that it will rebuild the entire board; when modifying an existing whiteboard with SVG, first go through the confirmation workflow in [`../routes/svg-edit.md`](../routes/svg-edit.md).
- Only when the artifact is DSL or OpenAPI native node format is explicitly needed, first convert with `npx -y @larksuite/whiteboard-cli@^0.2.13 --to openapi --format json`, then write with `raw`.

For specific command examples and how to use `--overwrite`, `--idempotent-token`, and `--as user/bot`, refer uniformly to [`whiteboard +update`](./lark-whiteboard-update.md).
