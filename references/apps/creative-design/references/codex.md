<a id="codex-agent-工具参考"></a>
# Codex Agent Tool Reference

This document lists the harness-specific tools that [`../creative-design.md`](../creative-design.md) depends on, for you to use when running in the **Codex Agent**. The main prompt only names capabilities ("ask the user a question", "show a file", etc.); this document gives the Codex invocation method. General tools (shell, file read/write/edit/search, `gh`) are not covered here.

<a id="web-工具--codex-对应项"></a>
## Web Tools → Codex Equivalents

| Web Tool | Codex Equivalent |
|---|---|
| `ask_user_question` | In Codex Plan Mode, if `functions.request_user_input` is available, use it; otherwise ask a concise question in chat and wait for the user's reply. |
| `done`, `fork_verifier_agent` | Present the deliverable's file path in the final reply. |
| `write_file` (and its `asset:` parameter) | Codex's regular file editing tool. There is no asset review pane; discard this concept. |
| `copy_files` | Shell `cp`. |
| `read_file`, `list_files`, `view_image` | Codex's regular file reading/search tools. |
| `show_to_user` | Provide an absolute local file path; when helpful, embed the image in Markdown using the absolute path. |
| `eval_js`, `eval_js_user_view`, `run_script` | Use Shell for scripts. |
| `web_fetch`, `web_search` | Use Codex's web tools if available; for time-sensitive facts, supplementing content material, or web queries requested by the user. |
| `generate_image` | No built-in equivalent. If an image generation tool is connected in the session, use it; otherwise skip AI image generation, fall back to inline SVG / CSS graphics, and note this in the delivery description. |
| `search_images` | No dedicated equivalent. If web tools are available, use them to search for images, for material that needs real images and reference images to establish direction; if not, skip. |
| `copy_starter_component` | Shell `cp <本模块 所在目录>/starter-components/<file> .` (the cwd is usually the app project directory rather than the skill directory, so you need to use the skill directory's actual path; or read it and adapt it). |
| Document parsing (docx / pdf) | Use shell tools to convert to text and then read: `pdftotext` / `pandoc` / python scripts (`pypdf`, `python-docx`). |
| `invoke_skill("X")` / `invoke the "X" skill` | Read the corresponding `references/<file>.md` (the medium skill is in the same `references/` directory as this file). |

<a id="提出澄清性问题"></a>
## Asking Clarifying Questions

When Codex is in **Plan Mode** and `functions.request_user_input` is available, use it to ask focused, structured questions. It is best suited for high-impact design decisions, such as scope, fidelity, design context, reference apps, and number of variants.

If `request_user_input` is unavailable, or the session is not in Plan Mode, just ask the same questions directly in chat and wait for the user's answer. Keep a round of questions concise and actionable. Do not invent fake tool names.

<a id="交付与发布"></a>
## Delivery and Publishing

- Give the deliverable's absolute local file path in the final reply.
- After the artifact is complete and committed, publish it to Miaoda according to the "Publish" section of [`../creative-design.md`](../creative-design.md)—the shareable link delivered to the user is the `online_url` returned by `+release-get`.
