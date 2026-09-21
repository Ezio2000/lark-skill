<a id="genre-contract-formal-document--内部正式材料-workplaceformal_doc"></a>
# Genre Contract: Formal Document / Internal Formal Material (`workplace.formal_doc`)

<a id="体裁规则表硬约束"></a>
## Genre Rule Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Solemn, accurate, concise, direct; formality comes from genuine authority, facts, boundaries, responsibility, and lifecycle, not from boilerplate or mechanical hierarchy |
| Visual Strategy | Fixed `formal`; apply only after the format-neutral content draft is complete; highlight blocks, emoji, and decorative components are prohibited |
| Allowed Blocks | `title` (at most 1 per complete document), `p`, `h1`, `h2`, `h3`, `h4`; heading levels must be consecutive and no deeper than four levels |
| Restricted Blocks | `ul`, `ol` containers and `li` child blocks may only carry genuine parallel or sequential items; `table` containers and `thead`, `tbody`, `tfoot`, `tr` child blocks may only carry same-field information for multiple objects; `img`, `figure` may only carry material that serves necessary evidentiary purposes, source explanations, and text-equivalent information |
| Prohibited Blocks | Types not listed in the allowed/restricted lists are prohibited, including `callout`, `checkbox`, `grid` containers and `column` child blocks, `whiteboard`, `blockquote`, `pre`, root-level `code` and `hr`; decorative colors, stickers, fake letterheads, fake seals, and images without evidentiary purpose are prohibited |
| Content Logic | First choose one of the following based on the reader's task: rules/regulations, approved notice/arrangement, inspection rectification/ledger, or approved formal statement; write only the objects, basis, requirements/findings, responsibility, verification, and lifecycle needed to complete that task; do not mix subtypes |
| Facts/Boundaries | Only write confirmed authorization, requirements, facts, and positions as definitive conclusions; keep source statements, original records, verified facts, and inferences separate; before external distribution, confirm confidentiality, trade secrets, personal information, material rights, and publication permissions; do not create when key gaps remain unclosed |
| Errors | Any of the following constitutes failure: misjudging an official document as "formal," treating this leaf as a fallback for proposals/summaries/briefings, fabricating approval/effectiveness, smuggling unauthorized new rules through a notice, passing off online material as the organization's own facts, writing inspection leads as conclusions of responsibility, or measures not corresponding to findings |

<a id="适用与收口"></a>
## Applicability and Closure

Used to write authorized non-official-document organizational rules or arrangements, reviewable inspection rectification records, or approved organizational positions into a formal carrier, enabling readers to determine the scope of application, actions to take, record status, or core position.

Directions pending approval go to `proposal.md`; complex one-time execution goes to `execution-plan.md`; repeated operational steps go to `sop-tutorial.md`; Party and government official documents go to `official-redhead.md`; executive briefings go to `memo-brief.md`; periodic status goes to `weekly-report.md`; learning summaries go to Retrospective / Report. Words such as `正式、制度、通知、方案、计划、总结、简报、讲话稿` alone do not trigger this genre, and this genre is not a fallback for uncertain requests.

<a id="按读者任务选择唯一内容路径"></a>
## Choose the Single Content Path Based on the Reader's Task

| Reader's Task | Content Mainline |
|-|-|
| Judge ongoing rules | Purpose and authority → applicable/non-applicable scope → necessary definitions → normative requirements → responsibility, exceptions, and escalation → effectiveness, maintenance, review, and supersession |
| Execute an approved notice | Issuing entity and approval status → affected objects and scope → confirmed matters and effective time → actions, responsibility, and deadlines → exceptions, feedback, and contacts |
| Review inspection rectification | Objects, scope, methods, and evidence status → each observable finding, standard, impact, and supported cause → corresponding measures, responsibility, and deadlines → verification, closure evidence, and change traces |
| Understand an approved position | Speaker or issuing entity, occasion, audience, and duration → core position → necessary facts and reasons → expected understanding or action; do not mix in regulatory effect |

<a id="证据与高质量写法"></a>
## Evidence and High-Quality Writing

- For rule-type documents, write maintenance responsibility, version, approval, effectiveness, review, and supersession status as needed; stably describe what to do, who is responsible, and when it takes effect; link volatile operational methods to controlled SOPs. For normative terms, prefer the organization's existing definitions; when intensity is unclear, mark `[规范强度待确认]`.
- For inspection rectification, distinguish user statements, original records, verified facts, and leads pending further evidence; when key dates, quantities, or conclusions lack sufficient evidence, mark `[证据待补：补证动作]` nearby, and do not infer causes or responsibility; archiving corrections must preserve the original records.
- Inspection measures must correspond to specific findings and be verifiable; approved notices convey only matters within the authorized scope; formal speeches use only approved positions and are checked by reading aloud at the actual speaking pace.
- Use active sentences, explicit subjects, and consistent terminology; each sentence expresses only one fact, judgment, requirement, or permission; lists strictly follow the user-specified quantity and fields, without mechanically adding background or document-control fields.
- When the approver, basis, authority, scope of application, effectiveness status, or publication conditions are unclear, use specific placeholders and keep the document as a draft; do not use layout, titles, or signatures to imply that it has been approved, issued, or has taken effect.
