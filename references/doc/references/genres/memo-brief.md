# Genre Contract: Memo / Brief (`workplace.memo_brief`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Direct, restrained, information density controlled for the named reader; lead with the conclusion, status, or ask; no fixed length |
| Content Logic | First choose one of three modes—informational, decision, or pre-meeting—then proceed as "core matter / ask → necessary facts → impact / trade-offs → risks / unknowns → actions"; write options only when there are genuine choices |
| Facts / Boundaries | Facts, numbers, positions, approval status, and timing must all be verifiable; mark unknowns and assumptions nearby; a Memo may serve only as the decision cover for a complete Proposal, not as a replacement for its argumentation |
| Errors | Any of the following constitutes failure: no conclusion or ask on the first screen, compressing a complete Proposal into a summary, fabricating approvals / positions, deleting evidence to fit a fixed length, or failing to explain the impact of details |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Used to let a named internal reader quickly learn, judge, or complete pre-meeting preparation. Requests to approve a complete direction, budget, resources, or execution commitment go to `proposal.md`; periodic judgment of position relative to goals goes to `weekly-report.md`; the words "summary / brief" alone do not trigger this genre.

<a id="子类型与证据"></a>
## Subtypes and Evidence

- Informational Brief: change → impact → current status / risks → next steps; when no action is needed, state explicitly "for information only."
- Decision Memo: decision matter / timing → current state → genuine options and their impacts on a consistent basis → recommendation and evidence → clear decision entry point.
- Pre-meeting Brief: meeting objectives → verified participant positions / interests → key points and no-go areas → expected outcomes; unknown positions must not be fabricated.
- Mark readers, author / responsible team, date, and information cutoff time as needed. When continuously updated, explain changes relative to the previous version and the next update point.

<a id="结构与高质量写法"></a>
## Structure and High-Quality Writing

Organize by importance rather than by order of materials; one point per paragraph; do not hide key judgments in attachments. It is recommended to state clearly who does what, why, and how completion will be judged, and to present risks, counterexamples, and uncertainties sufficient to change the judgment. When key facts are missing, use specific placeholders such as `[关键结论待确认]` and `[数据口径待核]`, or narrow it to a list of questions to be verified; if approval is still required on that basis, you must `blocked`.
