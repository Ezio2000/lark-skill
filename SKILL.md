---
name: lark
license: MIT
description: "Operate Feishu/Lark through lark-cli: documents, Drive, tables, meetings, messages, mail, approvals, calendars, tasks, and Miaoda apps. Use for Lark resources, account authorization, events, and OpenAPI requests. Do not activate for unrelated local development, design, or files."
metadata:
  version: "0.1.0"
  requires:
    bins: ["lark-cli"]
---

# Lark

Read the relevant module's `index.md`, then only the operation references needed for the current task. Combine modules when the task crosses domains; do not preload the bundle. Scripts and assets are included locally. The old separate `lark-*` skills are not installation dependencies.

User-facing documentation is in Chinese. LLM-facing instructions, module guides, detailed references, and explanatory comments are in English. Respond in the user's language; preserve identifiers, CLI flags, filenames, compatibility anchors, and literal user content.

## Shared execution rules

- A specific action request is authorization. Reuse authorization across turns and authentication recovery when the target, parameters, and effects are unchanged; no extra confirmation phrase is required. Reading, analyzing, or summarizing does not authorize sending, publishing, or modifying remote data. If the target is ambiguous, effects expand, or an important choice is missing, complete the read-only preparation before asking for that missing information.
- Use explicit `--as user` for personal resources, and `--as bot` for a user-selected application/bot operation. Keep the identity that produced the source data. Do not silently switch identities after an empty result or permission failure: bot queries against personal resources may succeed with empty data.
- Prefer a matching shortcut, then a registered API, then raw OpenAPI. Use an exact command already documented in the module. When parameters are missing, read its operation reference or exact `--help`; inspect registered API fields with `lark-cli schema <service.resource.method>`. Do not invent flags or fields.
- Reuse the current login. Read [authentication and diagnostics](references/shared/index.md) for an authentication-management request or an actual identity/token/scope error, not as a routine preflight.
- Interpret JSON success using `ok == true` and the process exit status, not top-level `code == 0`. For wrappers and error parsing, read the [output contract](references/shared/references/lark-shared-output-contract.md). If a write's outcome is unknown, query state before repeating it.
- Exit `10` / `confirmation_required` requires the [confirmation-flag procedure](references/shared/references/lark-shared-high-risk-approval.md), not network or permission retries. Check whether the exact operation is already authorized.
- Resource tokens, task GUIDs, document IDs, and meeting numbers are not interchangeable. Follow the selected module's identifier, pagination, batch-size, and timestamp rules. Present times in the user's timezone.
- Local path support is command-specific. Some commands require cwd-relative paths; others support absolute paths. Reference links are relative to the containing file; module `scripts/` and `assets/` paths are relative to that module. Do not change the task cwd merely to locate a script.
- Run bundled Python helpers with uv and Python 3.11+: `uv run --project "<lark-root>" --locked python "<absolute-script-path>"`. Add `--extra dataframe` before `python` for the Sheets DataFrame helper. Replace `<lark-root>` with the installed skill directory; `--project` selects dependencies without changing cwd. Do not use system Python or pip. Use temporary directories for intermediate artifacts and clean them after use.

## Task routing

| Task | Module |
|---|---|
| Read, create, or edit document content; attachments and mindnotes | [Documents](references/doc/index.md) |
| Find, upload, download, import, export, copy, move, comment on, or share files | [Drive](references/drive/index.md) |
| Knowledge spaces, Wiki nodes, hierarchy, and space membership | [Wiki](references/wiki/index.md) |
| Spreadsheet cells, formulas, formatting, charts, and analysis | [Sheets](references/sheets/index.md) |
| Base tables, forms, dashboards, BaseApp/AppMode, and workflows | [Base](references/base/index.md) |
| Native Lark presentations | [Slides](references/slides/index.md) |
| Document whiteboards, diagram nodes, and board export | [Whiteboard](references/whiteboard/index.md) |
| Drive-native Markdown content and version comparisons | [Markdown](references/markdown/index.md) |
| Events, availability, invitations, scheduling, and meeting rooms | [Calendar](references/calendar/index.md) |
| Historical/live meetings, notes, transcripts, Minutes, and bot participation | [Meetings](references/meeting/index.md) |
| Tasks, task lists, subtasks, assignees, and task agents | [Tasks](references/task/index.md) |
| Approval definitions, submissions, pending approvals, and instances | [Approvals](references/approval/index.md) |
| Personal attendance records | [Attendance](references/attendance/index.md) |
| OKR cycles, objectives, key results, alignment, and progress | [OKR](references/okr/index.md) |
| Chat search, messages, groups, interactive cards, and callbacks | [Messaging](references/im/index.md) |
| Lark mail, drafts, sending, rules, and mail watching | [Mail](references/mail/index.md) |
| Resolve names/emails/open_ids; look up contacts or bots | [Contacts](references/contact/index.md) |
| Listen for IM, approval, task, meeting, or other real-time events | [Events](references/event/index.md) |
| Develop, design, deploy, or operate a Miaoda/Spark application | [Apps](references/apps/index.md) |
| Summarize a date range's agenda and incomplete tasks | [Agenda summary](references/workflow-standup-report/index.md) |
| Summarize meeting records and decisions over a date range | [Meeting summary](references/workflow-meeting-summary/index.md) |
| Login, identity, scopes, configuration, updates, and notices | [Authentication](references/shared/index.md) |
| A Lark API not covered by a module or registered CLI command | [OpenAPI discovery](references/openapi-explorer/index.md) |
| Turn a repeated Lark operation into reusable instructions | [Extend this skill](references/skill-maker/index.md) |

## Routing boundaries

- Approval todos belong to Approvals; ordinary todos belong to Tasks. Scheduling belongs to Calendar; meeting records and live content belong to Meetings. Legacy names `lark-vc`, `lark-vc-agent`, `lark-note`, and `lark-minutes` all map to Meetings.
- Route resource URLs by path and resolved type, including Lark, Feishu, and `doubao.com`: `/docx/` → Documents, `/sheets/` → Sheets, `/base/` and Base `/app/` → Base, `/slides/` → Slides, `/minutes/` → Meetings. A Wiki node may require [token resolution](references/shared/references/lark-wiki-token-routing.md) before using the underlying resource.
- Copy native files through Drive's copy operation to preserve structure; do not simulate copying with fetch followed by create. Standalone comments belong to Drive; comments accompanying document content can come from document fetch.
- BaseApp/AppMode is a Base capability. Use Apps only when the user selected Miaoda, supplied a Miaoda project/link, or is working in an existing Miaoda project. A generic webpage, deck, prototype, or local development request does not authorize creating or publishing a Miaoda application.
- After summarizing meetings or tasks, deliver the requested summary. Create documents, send messages, or create tasks only when requested.

## Maintenance

Keep one `SKILL.md`. Add capabilities to an existing module, or to `references/<domain>/index.md` with a routing-table entry. Old `lark-*` strings can still identify CLI-embedded documentation and reference filenames; they are not separate installed skills.

Before handling upgrades, read the [update guide](references/shared/references/lark-shared-update-notice.md). `lark-cli skills read <legacy-module> [path]` can inspect documentation embedded in the installed CLI; embedded documentation excludes scripts and assets and does not replace the bundled resources.

[README](README.md) and [provenance](SOURCES.md) are for installation, maintenance, and release work only.
