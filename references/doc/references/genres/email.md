<a id="genre-contract-email--邮件-platformemail"></a>
# Genre Contract: Email (`platform.email`)

<a id="核心定位硬约束"></a>
## Core Positioning (Hard Constraints)

- The deliverable is an email draft that can be copied into an email client; it does not mean it has been sent, and it does not perform recipient lookup, email sending, drafts folder, or mailbox management; actual email operations switch to `lark-mail`.
- The visual strategy defaults to `formal`; adjust only when the user requests it and it does not violate organizational norms or the selected content contract. Emoji, highlight blocks, and decorative components are prohibited throughout.
- By default, only use basic structures such as short paragraphs, lists, and plain links. Only when it has been confirmed by the user, platform documentation, or trusted configuration that the target platform fully supports Feishu rich text may `rich` or rich blocks be used; do not infer support on your own based on "email," "HTML email," Feishu Docs hosting, or the platform name.
- One email carries only one primary communication task; the subject, opening paragraph, body, and action request revolve around the same purpose. Do not fabricate sender identity, recipient relationships, facts, permissions, commitments, deadlines, attachments, or completed actions; use clear placeholders for missing but necessary information.
- Do not use a cover page or table of contents. Even if platform capabilities have been confirmed, tables, images, `callout`, whiteboards, and other rich blocks may only be used when the information genuinely requires them, and ensure semantic integrity after copying, delivery, and receipt.

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Use when the user explicitly asks to "write an email, email draft, email copy, email wording, email, e-mail," or requests drafting a reply, follow-up, notification, invitation, or outreach email; where the content is stored does not affect this contract taking effect.

Viewing, searching, sending, replying to, or managing real emails in a mailbox belongs to `lark-mail` operations; email system descriptions, email data analysis, marketing plans, or using email as an information source do not trigger this contract. If a task requires both drafting and actual sending, first form and confirm the content according to this contract, then switch to `lark-mail` to execute the sending.

<a id="邮件主任务"></a>
## Email Primary Tasks

| Primary Task | Content Spine |
|-|-|
| Request / Decision | Purpose or conclusion → necessary background → clear request / options → expected time or next step |
| Notification / Sync | Key change → scope of impact → what recipients need to know / do → time point and contact entry |
| Reply / Follow-up | Corresponding prior context → new information or direct answer → pending items → next step |
| Invitation / Outreach | Reason for contact → relevance to the recipient → specific proposal → low-cost way to respond |
| Apology / Issue Communication | Acknowledge impact → confirmed facts → remedial actions → follow-up arrangements and boundaries |

<a id="成稿要求"></a>
## Drafting Requirements

- The draft gives the subject first, then the body; only list envelope fields such as recipients and CC when the user requests it or the materials make it clear. The subject accurately expresses the object, matter, or required action; do not use clickbait, empty pleasantries, or uninformative "important notice."
- Choose the salutation based on known relationships and context; when the relationship is unclear, use a safe neutral salutation or an explicit placeholder, and do not arbitrarily apply intimate, rank-based, or gendered titles.
- The opening paragraph states the purpose, conclusion, or relationship to the existing thread as soon as possible. Background retains only the information the recipient needs to understand, judge, or act; do not copy the full report, meeting minutes, or thought process verbatim into the email.
- The action request clearly states who needs to complete what, when, and in what manner; when the materials do not provide an owner or time, do not invent them. Use lists for multiple parallel items, prioritizing so the recipient can respond to each item directly.
- When mentioning links, attachments, or referenced materials, explain their purpose; materials not actually provided or uploaded should be written as placeholders to be filled in, and do not claim "see attachment." Reply and follow-up emails only add new information and do not mechanically restate the entire thread.
- The ending matches the email's purpose: request-type emails specify the response method, notification-type emails state that no action is needed or give the next milestone, and outreach-type emails leave room to easily decline or adjust. The signature uses only known identity; when identity is unclear, use a placeholder and do not fabricate names, teams, or contact information.

<a id="交付前检查"></a>
## Pre-Delivery Checklist

Confirm that the recipient can tell from the subject and opening paragraph "why they received it, what they need to know or do," that facts, responsible parties, times, and attachment status are all grounded, that the body has no irrelevant filler or repetition, that the tone matches the relationship and risk, and that there is no emoji throughout; if rich blocks are used, there is confirmation that the target platform supports Feishu rich text; after copying into an email client it remains clearly readable, and "draft" is not mistakenly written as "sent."
