<a id="claude-code-工具参考"></a>
# Claude Code Tool Reference

This document lists the harness-specific tools that [`../creative-design.md`](../creative-design.md) relies on, for you to use when running in **Claude Code**. The main prompt only names capabilities ("ask the user a question", "show a file", etc.); this document gives the exact Claude Code tools, signatures, and invocation methods. Common tools (`Bash`, `Read`/`Write`/`Edit`/`Glob`, `gh`) are the same in any environment and are not covered here.

<a id="web-工具--claude-code-工具对照表"></a>
## Web Tools → Claude Code Tools Mapping Table

The upstream prompt references some Claude.ai web tools that do not exist in Claude Code. Whether they appear in prose or in code, always replace them according to the table below:

| Web Tool | Claude Code Equivalent |
|---|---|
| `ask_user_question` | `AskUserQuestion` (answers are returned inline; at most 4 questions per call, call again if you need more) |
| `done`, `fork_verifier_agent` | `SendUserFile` to send the deliverable and give the file path |
| `write_file` (and its `asset:` parameter) | `Write`—completely discard the concept of the "asset review pane" |
| `copy_files` | `Bash cp` |
| `read_file`, `list_files`, `view_image` | `Read` (can also render images), `Glob` / `Bash ls`, `Grep` |
| `show_to_user` | `SendUserFile` (self-contained files can also use `open <path>`) |
| `eval_js`, `eval_js_user_view`, `run_script` | `Bash` |
| `web_fetch`, `web_search` | `WebFetch`, `WebSearch` |
| `generate_image` | No built-in equivalent. If an image generation MCP/tool is connected in the session, use it; otherwise skip AI image generation, fall back to inline SVG / CSS graphics, and note this in the delivery description. |
| `search_images` | No dedicated equivalent. Use `WebSearch` to search + `WebFetch` to fetch; use for assets that need real images (physical objects, locations, logos, etc.) and reference images to establish direction; when citing directly, pay attention to source and copyright. |
| `copy_starter_component` | `Bash cp <本模块 所在目录>/starter-components/<file> .` (cwd is usually the app project directory rather than the skill directory, so you need to use the actual path of the skill directory; or `Read` and then adapt) |
| Document parsing (docx / pdf) | For PDF use `Read` (use the `pages` parameter to read the whole thing in segments); for docx first convert to text with Bash and then read (`pandoc`, macOS `textutil -convert txt`, or `python-docx`) |
| `invoke_skill("X")` / `invoke the "X" skill` | The `references/<file>.md` corresponding to `Read` (the media skill is in the same `references/` directory as this file) |

<a id="askuserquestion澄清性提问"></a>
## AskUserQuestion (Clarifying Questions)

Replaces `ask_user_question`. `AskUserQuestion` **returns the user's answers inline**—ask first, then continue after the user replies. Each call displays at most 4 questions; for large new projects, first ask one round of focused questions, and if that is not enough, make another call.

- Preferences from memory can be given as *suggested* defaults in the questions, but they must still be confirmed by the user.
- Prefer using it rather than listing options as text bullet points in your reply.
- Project setup questions—**where** the project is **saved**, **which design system(s)** to use (one multiSelect)—are all ordinary `AskUserQuestion` calls.

<a id="交付与发布"></a>
## Delivery and Publishing

- Use `SendUserFile` to send the deliverable and give the file path (reading a file **does not** show it to the user).
- After the artifact is complete and committed, publish to Miaoda according to the "Publishing" section of [`../creative-design.md`](../creative-design.md)—the shareable link delivered to the user is the `online_url` returned by `+release-get`.
