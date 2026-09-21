# Genre Contract: SOP / Runbook (`workplace.sop_tutorial`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Imperative, specific, stable order, one action per step with an immediately adjacent observable criterion; do not write unconditional "as appropriate / when necessary" |
| Content Logic | First determine routine / controlled / high-risk, and identify whether it is a response plan; then proceed by "version → trigger / scope / end state → roles / prerequisites → actions / criteria / evidence → exceptions / stop / recovery → completion record / review" |
| Facts / Boundaries | Owner, version, environment, qualifications, permissions, tools, commands, thresholds, expected results, and recovery paths must all be verified; warnings precede actions; command success does not equal business end state; flowcharts / diagrams cannot replace executable steps, criteria, and exception paths, and must have textual equivalents; critical unknowns make the publishable draft `blocked` |
| Errors | A tutorial masquerading as an SOP, no risk classification, missing owner / version / prerequisites, multiple actions in one step, fabricated entry points / thresholds / permissions / commands, unknown state after stop, only writing "roll back when necessary" or unverified end state; a response plan lacking tiered triggers, alternate commander, degradation paths, or release conditions—any one of these appearing means failure |

<a id="适用与风险分类"></a>
## Applicability and Risk Classification

Used for organization-mandated repetitive operations, runbooks that follow an approved route to a definite end state, or response / business continuity paths that are pre-established and authorized for known event categories. One-off self-service how-to / learning goes to Knowledge; future design trade-offs, active unknown failures, or on-the-spot root cause investigation go to `technical-doc.md`; establishing only organizational authority, responsibilities, or release requirements without providing on-site steps goes to `formal-doc.md`. The words "tutorial / operation / manual / emergency plan" by themselves do not trigger.

| Classification | Incremental Proof Obligations |
|-|-|
| `routine` | Stage or end-state verification, common exceptions, and escalation |
| `controlled` | Additionally includes approval, acceptance / rejection, deviation records, change review, and representative trial run |
| `high-risk` | Additionally includes precheck, hold point, go / no-go, stop conditions, and executable rollback / fallback / roll-forward and recovery verification |

<a id="响应预案增量"></a>
## Response Plan Increment

- When personal safety or legally mandated direct reporting is involved, its priority is higher than business and property; set entry, escalation, degradation, and release conditions according to verified risks, and clarify command / decision authority, alternate roles, first-round actions, information reporting, and external communication boundaries. Contact sequences, wait durations, and retry counts must be pre-approved; when unknown, retain placeholders and only release safety actions that require no authorization wait.
- Pre-set degradation scenarios such as designated responsible person unreachable, network or power outage, primary resource unavailable, and reachable safe end states; recovery must verify the true business end state. Before release, conduct tabletop exercises or representative drills according to risk; high-risk scenarios include fault injection and record gaps, owners, and re-verification.

<a id="文控与证据"></a>
## Document Control and Evidence

State the trigger, target end state, scope, owner / qualifications, current version / environment, prerequisites, permissions, tools, and inputs. Commands, parameters, thresholds, expected outputs, backup / recovery assets, and trial run results must come from the real environment; after process changes, update, review, and mark superseded status.

For critical gaps, use specific placeholders such as `[待环境 owner 验证]` nearby. When commands, permissions, thresholds, stop or recovery criteria are unknown, retain only a safe read-only precheck; do not create an executable draft.

<a id="步骤异常与恢复"></a>
## Steps, Exceptions, and Recovery

- Write only one action per critical step, with immediately adjacent observable results, thresholds, and evidence; when verification requires an operation, list it as a separate step. Stop at a known safe state for unknown deviations, record evidence, and escalate.
- For high-risk, set a hold point before irreversible actions: list go / no-go signals, decision maker, and the safe end state when signals are missing. For rollback, write trigger conditions, applicable scope, steps, thresholds, stop points, and post-recovery business verification; do not write only command receipts.
- For state transitions, separately list irreversible points, write ownership, checkpoint / idempotency, and complete, non-duplicate, ordered, or equivalent verification; before closing fallback, you must prove the new end state is stable.

<a id="高质量写法"></a>
## High-Quality Writing

Make it independently reproducible by someone with the specified baseline qualifications but unfamiliar with the process; write selection conditions before actions, link out stable principles, and do not mix in principle lessons or on-the-spot diagnosis. Trim length according to risk but do not delete proof obligations; conduct trial runs by representative executors according to applicable governance requirements, and do not release without any actual verification.
