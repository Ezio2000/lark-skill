<a id="genre-contract-retrospective--复盘-workplaceretrospective"></a>
# Genre Contract: Retrospective (`workplace.retrospective`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Candid, blame-free, restrained about causality, centered on evidence and the next round of change; do not substitute "strengthen communication / keep monitoring" for verifiable experiments |
| Content Logic | Define the concluded cycle / event, then proceed through "goals / evidence → expected vs. actual → clustered observations → insights / causal hypotheses to verify → what to keep → a small number of improvement experiments → review" |
| Facts / Boundaries | Layer facts / observations, explanations / hypotheses, insights, and actions; link conclusions back to events, metrics, or deliverables; state root causes only when evidence is sufficient, otherwise write falsifiable hypotheses; protect necessary privacy |
| Errors | Retitling a weekly report, listing achievements / venting emotions, blaming individuals, speculating a single root cause, actions without an owner / verification / tracking, not reviewing the previous round, or treating template sticky notes as conclusions — any one of these means failure |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Use for looking back at a clearly defined iteration, phase, project, or event to form reusable learning and change how the next round is done. For current status and escalation needs, use `weekly-report.md`; for ongoing unknown situations involving loss-stopping, evidence gathering, recovery, or investigation of a production incident, use `technical-doc.md`. A production incident may be carried by a Technical main document covering impact / timeline / root cause / recovery, with a team-learning layer of this genre attached.

<a id="证据与因果"></a>
## Evidence and Causality

- At the beginning, define the scope, time, goals / original plan, participating perspectives, and known evidence; do not fabricate metrics, timelines, consensus, causes, or actions.
- Identify both the conditions to keep and the conditions to change, clustering them by impact; take systems, processes, tools, interfaces, and the conditions at the time as the object, and do not pass off a punitive narrative as a root cause.
- For personal work reflections / growth reflections, use one real event or turning point as evidence, presenting "judgment at the time → counterevidence / consequences → new understanding → next observable behavior"; do not ghostwrite emotions, motivations, inner journeys, or growth that the material does not provide.
- When evidence is insufficient, write "contributing conditions / hypotheses + verification method"; do not use a definitive tone. If a baseline is missing, use `[基线待补]`; if safety / legal matters are involved and evidence is insufficient, switch to Technical and `blocked`.

<a id="结构与高质量写法"></a>
## Structure and High-Quality Writing

Sticky notes, 4Ls, and Start / Stop / Continue are only collection methods; the final draft must synthesize them into themes and judgments. Improvement experiments should state the action, owner, target time, verification conditions, and tracking location, prioritizing changes to the system rather than asking people to "be more careful"; add the effects of the previous round's actions and the next round's review points as needed. Project wrap-ups may add cost, scope, stakeholders, and knowledge transfer, but do not mechanically expand sections.
