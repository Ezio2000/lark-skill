<a id="genre-contract-prd--产品需求-workplaceprd"></a>
# Genre Contract: PRD / Product Requirements (`workplace.prd`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Concrete, behavior-oriented, consistent terminology and states; do not use fixed large templates to manufacture a sense of completeness |
| Visual Constraints | When there is a clear content purpose, use scenarios, state flows, tables, diagrams, and other components to reduce comprehension and acceptance costs, but they must not replace requirements, evidence, or acceptance |
| Content Logic | Once the direction is set, proceed in the order of "user problem / evidence → goal / outcome → scope / non-goals → scenarios → behavioral requirements / acceptance → exceptions / boundaries → applicable quality constraints → dependencies / open questions" |
| Facts / Boundaries | User needs, metrics, research, thresholds, feasibility, owner, status, and scheduling must be traceable; requirement descriptions state observable outcomes, acceptance criteria verify outcomes; security, privacy, accessibility, etc. are included only according to actual risks and standards |
| Errors | A feature list without user problems, a Proposal argument that swallows the requirements, missing scope / non-goals, requirements that hide implementation, untestable acceptance, no exceptions on the normal path, fabricated research / thresholds / approvals, or mechanically filling in quality templates — any one of these constitutes failure |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Used after the direction and investment principles are set, to let product, design, engineering, and testing reach consensus on the user problem, scope, observable behavior, and completion criteria. Whether to initiate a project / choose a direction / approve resources goes to `proposal.md`; architecture, interfaces, and implementation trade-offs go to `technical-doc.md`; approved repetitive operations go to `sop-tutorial.md`. The words "requirement / feature" alone do not trigger this.

<a id="证据与需求写法"></a>
## Evidence and Requirement Writing

- Clarify the target users, task context, problem, and research / behavioral / supporting evidence; internal preferences and presupposed features must not masquerade as user needs.
- Product goals connect to observable outcomes; metrics specify definition, source, and time window. For unknown target values, use `[目标值待产品 / 数据确认]` and give a confirmation owner / time point; do not fabricate usage volumes or thresholds.
- Write key requirements as actor + trigger / precondition + observable outcome + failure / edge; terminology and states must be consistent. The user story format is only a tool, not a section quota.
- Give each quality constraint a verifiable threshold or an explicit item to be confirmed; when not applicable, do not fill in a template. Keep requirements, acceptance / tests, and sources traceable.

<a id="结构与高质量写法"></a>
## Structure and High-Quality Writing

First define scope, non-goals, priorities, dependencies, assumptions, and open questions to prevent scope creep; then write normal, exceptional, and boundary behavior according to key scenarios. Break down large, untestable requirements into acceptance-ready granularity; do not use adjectives such as "better experience / high performance." When there is no user evidence, narrow it down to assumptions and a research plan; when key compliance / security gates are missing, `blocked`; open questions must not be hidden in footnotes.
