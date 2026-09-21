<a id="genre-contract-knowledge--知识与教程-routerknowledge"></a>
# Genre Contract: Knowledge / Knowledge and Tutorials (`router.knowledge`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule                                                                                                                                  |
|-|--|
| Writing Style | Concrete, actionable, explained according to reader level; popular science may be vivid and curious, but must not sacrifice accuracy or fabricate drama                                                                                     |
| Content Logic | First choose the single primary mode and the reader's starting point, then promise one understanding, learning, single operation, retrieval, or selection outcome; the first screen gives the applicable audience, goal, and key prerequisites, while concepts, steps, practice / verification, feedback, and exceptions unfold progressively as needed                                                    |
| Facts / Boundaries | Facts, versions, commands, UI paths, and links must be verified; examples and rules kept separate; screenshots / cases must not leak sensitive information; known self-service paths may be written, organization-controlled repetitive operations go to SOP, design, precise technical contracts, or unknown diagnosis go to Technical                                       |
| Errors | Not stating the reader's starting point; tutorial turns into theory lecture; learning plan has no baseline / completion criteria / adjustment rules; only principles without steps / examples; steps without results or verification; missing version, permissions, environment; fabricated commands, UI, or links; FAQ detached from real questions; resource collection without criteria / annotations / maintenance; visuals become the only information; writing unknown troubleshooting as a definitive answer |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Applies to self-directed understanding, learning / exam preparation planning, a single known task, or retrieval reuse. `科普`, `教程`, `指南`, `攻略`, `学习计划`, `FAQ`, `知识库`, `资源合集` are used only for recall; "knowledge base" is a container or channel and does not determine article genre. Organization requirements for multiple people to repeatedly execute an approved version with a record go to [`sop-tutorial.md`](sop-tutorial.md); future design, precise API contracts, production state changes, or unknown root causes go to [`technical-doc.md`](technical-doc.md); research or data forming new insights goes to Report.

<a id="主模式"></a>
## Primary Modes

| Mode / Reader Task | Structural Progression |
|-|-|
| Explanation / popular science: build a correct mental model | Phenomenon / misconception → conceptual model → mechanism and evidence → examples → controversies, limitations, and applicable boundaries |
| Tutorial: gain skills through guided practice | Learning objectives → starting point / environment → safe practice → checkpoint → review and next steps |
| Learning plan: continuously improve under real-world constraints | Baseline diagnosis → observable stage goals → practice / materials / time → completion criteria and feedback → adjustment rules |
| How-to: complete one known goal | Goal → prerequisites → shortest effective steps and observable results → variants / known errors → completion verification |
| FAQ / known troubleshooting: quickly find verified answers | Group by real question or symptom → direct answer → necessary conditions / operations → related content; when new hypotheses or root cause investigation are needed, switch to Technical |
| Resource guide: select resources by criteria | Use cases / selection criteria → categories → fit, cost, and access conditions for each item → maintenance information |
| Reference / KB article: retrieve and reuse facts or solutions | Context / applicable version → facts or issue-resolution → limitations / related items → mark owner / last verified when timeliness is critical |

<a id="事实步骤与维护"></a>
## Facts, Steps, and Maintenance

- Clarify the audience's existing knowledge, scope / non-scope, version, environment, permissions, and risks; explain terminology when first needed, rather than instilling complete theory upfront.
- Control the intensity of a learning plan by stage / ability, available time, existing tasks, and available materials; break goals into observable performance, and write practice, completion criteria, feedback, and adjustment conditions together for each stage. Gaps that would significantly change the arrangement should be asked about or made conditional first; do not fabricate foundations / time.
- For sequential tasks, write one clear action per item, with an observable result immediately adjacent; commands, inputs, outputs, and success verification must be reproducible in the declared environment, and dangerous or irreversible warnings must come before the action.
- FAQ should only include real user questions or retrieval needs; otherwise reorganize by user task. Resource guides should first state selection criteria, then give curated links with descriptions, and not use external links to replace core context.
- Time-sensitive content should mark the applicable version / time and explain maintenance boundaries; complex visuals must have body text that conveys equivalent information, and images, cases, and code must not become the sole basis without explanation.
- When version or permissions are unclear, use `[适用版本待核]`, `[所需权限待确认]` and write only the unaffected parts; unverified commands or links do not enter the published draft. When gaps may cause loss, security risk, or a critical fork, mark `blocked`.

<a id="高质量写法"></a>
## High-Quality Writing

Let readers know on the first screen what they can understand, learn, complete, or find; advance with reader language, concrete verbs, and verifiable results, adding only the necessary new understanding or action in each section. Give the shortest viable path first, then supplement principles, variants, and further reading where needed; examples serve transfer only, do not expand into a full set of content the user did not request, and do not use rich components to mask insufficient explanation.
