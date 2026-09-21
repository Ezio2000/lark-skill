<a id="aily-工具参考"></a>
# Aily Tool Reference

This document lists the harness-specific tools that [`../creative-design.md`](../creative-design.md) depends on, for you to use when running in **Aily**. The main prompt only names capabilities ("ask the user a question", "show a file", etc.); this document gives the Aily invocation method. General tools (`Bash`, file read/write/edit, grep/glob search) are the same in any environment and are not covered here.

<a id="web-工具--aily-对应项"></a>
## Web Tools → Aily Equivalents

The upstream prompt references some Claude.ai web tools that do not exist in Aily. Whether they appear in prose or in code, always replace them according to the table below:

| Web Tool | Aily Equivalent |
|---|---|
| `ask_user_question` | `ask_user` (pose a structured decision question to the user; ask first, wait for the user's reply before continuing). |
| `done`, `fork_verifier_agent` | Use `submit` to deliver the result and give the file path. |
| `write_file` (and its `asset:` parameter) | Aily's "create/edit local file" tool. There is no asset review pane; discard this concept. |
| `copy_files` | `Bash cp`. |
| `read_file`, `list_files`, `view_image` | "Read local file"; use glob to find by filename and grep to search content; for images go directly through "parse binary file (...image...)" — Aily natively supports image input. |
| `show_to_user` | Use `submit` to deliver and give the absolute local file path. |
| `eval_js`, `eval_js_user_view`, `run_script` | Use `Bash` for scripts. |
| `web_fetch`, `web_search` | `fetch`, `web_search`. Used for time-sensitive facts, supplementing content material, or queries requested by the user. |
| `generate_image` | `aily-image-generate_workbench` (Seedream V4.5 model): supports text-to-image, image-to-image (given a reference image), infographics, image editing, and image sets (generating multiple images at once as a stylistically unified, character-consistent image sequence). |
| `search_images` | `doubao_image_search` (search images by keyword, suitable for finding reference images and stock images). |
| `copy_starter_component` | `Bash cp <本模块 所在目录>/starter-components/<file> .` (cwd is usually the application project directory rather than the skill directory, so you need to use the skill directory's actual path; or read it and adapt it). |
| Document parsing (docx / pdf) | Aily's native "parse binary file" capability directly reads the full text of Word / PDF / Excel / PPT; for PDF you can also use the dedicated `aily-pdf` tool. |
| `invoke_skill("X")` / `invoke the "X" skill` | Use `get_skills("X")` to load the corresponding media skill (e.g. `get_skills("frontend-design")`). These skills are also bundled as local files with this module under `references/<X>.md`, so when `get_skills` cannot retrieve them, read the file directly. |

<a id="提出澄清性问题"></a>
## Asking Clarifying Questions

Use `ask_user` to ask focused, structured questions — it returns the user's decisions inline; ask first, wait for the reply before continuing. It is best suited to high-impact, load-bearing decisions: delivery format, fidelity, design context, reference apps, number of variants. Keep a round of questions concise and actionable. Do not invent fake tool names.

<a id="交付与发布"></a>
## Delivery and Publishing

- Use `submit` to submit the delivery result and give the absolute local file path.
- After the artifact is complete and submitted, publish to Miaoda according to the "Publishing" section of [`../creative-design.md`](../creative-design.md) — the shareable link delivered to the user is the `online_url` returned by `+release-get`.

<a id="aily-专属注意事项"></a>
## Aily-Specific Notes

- **Prefer dedicated tools over hand-rolling.** Besides the general `Bash`, Aily also comes with a set of dedicated tools (`aily-xlsx`, `aily-chart`, `aily-diagram`, `aily-pdf`, `aily-image-generate_workbench`, etc.). When tables, charts, flowcharts, PDF, or image generation are involved, prefer the corresponding dedicated tool rather than scripting from scratch with `Bash`.
- **Prefer generation / search for image assets.** The `generate_image` / `search_images` in the "Image Assets and External Information" section of [`../creative-design.md`](../creative-design.md) both have real equivalents under Aily (see the table above); when a design artifact needs a hero image, illustration, infographic, consistent image set, or reference image, you should actively use them rather than defaulting to CSS/SVG fallbacks for everything. Save searched / generated images locally first, then use `lark-cli apps +file-upload` to upload them and reference the returned remote URL in code; do not commit to git.
- The `slide` subtype of `agent` is used to generate **Feishu Slides**, which is a different path from the self-contained HTML deck produced by this module (`starter-components/deck-stage.js`); do not mix them — this module's deck is always HTML.
- Delivery uniformly goes through `submit`; when project context needs to be preserved across turns, you can use `aily-work-memory`.
