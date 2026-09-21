<a id="genre-contract-proposal--方案提案-workplaceproposal"></a>
# Genre Contract: Proposal (`workplace.proposal`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Conclusion first, specific, deliberable; proactively present costs, counterexamples, and uncertainties; do not use grand background or false precision to manufacture a sense of approvability |
| Content Logic | Clarify the decision / decision-maker / timing first, then proceed in the order of "reasons for change and baseline of inaction → goals → comparison of real options on the same basis → recommendation → resources / delivery → risks / unknowns → decision entry point" |
| Facts / Boundaries | Distinguish facts, estimates, assumptions, and unknowns; benefits, costs, resources, user evidence, approvals, and scheduling must be traceable; only write governance / exit conditions when entering an execution decision, and unapproved items must not be written as existing commitments |
| Errors | No decision-maker / ask, no baseline of inaction, presupposing a single answer, options not on the same basis, costs and risks deferred to the end, committing before approval, fabricating benefits / approvals, or mixing with a PRD—any one of these means failure |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Used to request a named decision-maker to approve, reject, or choose a direction, budget, resource, pilot, or execution commitment. If the direction is already set and product behavior / acceptance criteria are being defined, use `prd.md`; for a short decision cover, use `memo-brief.md`; for a release of an already approved arrangement, use `formal-doc.md`. The word "proposal" itself does not trigger this genre.

<a id="子类型与证据"></a>
## Subtypes and Evidence

Can be used for concept / direction, investment / budget, resource requests, changes, pilots / experiments, and execution commitment proposals; depth is tailored to stage, amount, risk, and irreversibility. Must provide the case for change, goals / success criteria, a baseline of inaction or minimal change, and sufficient costs, benefits, dependencies, risks, and sensitivity factors for judgment.

When real choices exist, include feasible alternatives and compare them on the same scope, time, and evaluation criteria; when there are no real alternatives, explain how the constraints converge, and do not fabricate options. Non-quantifiable impacts may be qualitative, but the reasons and their decision impact must be explained.

<a id="结构与高质量写法"></a>
## Structure and High-Quality Writing

First frame the choice correctly, then argue for the recommendation; explicitly record discarded options and the costs of the recommendation. When numbers are insufficient, use ranges, basis, and a validation plan; do not fill in precise point estimates. When entering an execution decision, add owner, milestones, governance, measurement, and exit / retrospective as needed; when decision rights, key costs, or safety and compliance basis are missing, narrow it to an exploration draft, and if approval is still required, `blocked`.
