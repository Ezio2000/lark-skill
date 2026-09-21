<a id="genre-contract-execution-plan--执行计划-workplaceexecution_plan"></a>
# Genre Contract: Execution Plan (`workplace.execution_plan`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Organized around deliverables and judgments, specific, compact, and actionable; plan credibility comes from dependencies, capacity, and a closed acceptance loop, not from the number of sections or dates precise beyond any basis |
| Content Logic | Start from approved outcomes, success criteria, scope, and constraints, and proceed through "deliverables / workflows → dependencies and critical path → milestones with exit conditions → owner / interfaces / resources → risk triggers and alternatives → governance, change, and acceptance" |
| Facts / Boundaries | Distinguish confirmed commitments, estimates, assumptions, and pending items; time, owner, budget, capacity, authority, dependencies, and acceptance parties must be traceable and arithmetically consistent; unapproved directions must not be written as commitments, and when key resources or safety prerequisites are unknown, narrow the plan or `blocked` |
| Errors | A task list masquerading as a plan, activities without deliverables / definitions of done, milestones that are only dates, schedules that do not obey dependencies and capacity, all items at the same priority, missing interfaces or acceptance parties, risks without warning signals / actions / owners, or failure to update the baseline after changes—any one of these constitutes failure |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Used after direction and goals are set, to organize a one-time project, migration, release, campaign, special governance effort, or cross-team change. When the main task is still choosing direction, requesting budget / resources, or authorization, use `proposal.md`; when comparing strategic options without forming an approval entry point, use `business-analysis.md`; when publishing authorized rules / notices, use `formal-doc.md`; when repeating a determined path, use `sop-tutorial.md`; when reporting current status, use `weekly-report.md`.

"Project plan, execution plan, implementation plan, marketing plan" serve only as recall terms. If a marketing plan is still deciding tactics or budget, disambiguate according to the Proposal / Business Analysis above; only coordinated execution of already-determined tactics falls under this contract.

<a id="可执行性与证据"></a>
## Executability and Evidence

- First write the acceptable outcomes, scope / non-scope, constraints, and latest decision points; then break down work packages by deliverable rather than by department name. Each key work package states its owner, inputs / outputs, dependencies, definition of done, and acceptance party.
- Mark the critical path, parallelizable items, phase entry / exit conditions, and resource bottlenecks; dates are derived from dependencies, capacity, and necessary approval / production / calibration time. When derivation is impossible, use relative time, ranges, or specific placeholders, and do not fabricate precise schedules.
- For risks, write warning signals, impact, prevention / response actions, decision owner, and alternative paths; alternatives must state when to switch and the safety or business end state after switching, and must not say "strengthen communication."
- Governance retains only the cadences that produce judgments: interfaces, escalation conditions, decision rights, scope / baseline changes, and re-acceptance. Dense correspondences may use a single schedule, dependency, or responsibility table, but tables cannot replace the critical path and trade-off explanations.

<a id="高质量写法"></a>
## High-Quality Writing

Let every goal trace back all the way to deliverables, milestones, and work packages; let every date trace back to dependencies and capacity; let every risk trace back to actions after triggering. When resources are insufficient, narrow scope, phase the work, or set decision gates, rather than manufacturing false feasibility with "all channels, full coverage, advance in parallel."
