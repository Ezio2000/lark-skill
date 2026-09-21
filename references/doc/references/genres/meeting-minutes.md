<a id="genre-contract-meeting-minutes--会议纪要-workplacemeeting_minutes"></a>
# Genre Contract: Meeting Minutes (`workplace.meeting_minutes`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Neutral, precise, organized by agenda item and decision, using stable labels to distinguish decisions, recommendations, unresolved items, and items pending confirmation; do not replay the order of remarks |
| Content Logic | First state the meeting identity and record status, then write by agenda item the actual materials / necessary discussion summary → decisions and rationale / dissenting opinions → unresolved items → actions → review materials; depth should be commensurate with governance risk |
| Facts / Boundaries | Attendance, quorum, conflicts, motions, votes, decisions, owners, deadlines, and approval status must all come from meeting materials or confirmation; retain only personal information required for governance; drafts must not masquerade as approved versions; historical status is fixed as a text snapshot and must not be rewritten by mutable interactive blocks such as `checkbox`, `task` |
| Errors | A summary masquerading as a verbatim transcript, a running log of discussion, recommendations written as decisions, untrackable actions, claiming decisions are valid when quorum is unclear, a draft masquerading as approved, silently altering history, or leaking irrelevant personal information — any one of these constitutes failure |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Used for a citable governance record of a meeting that has already occurred, enabling absentees, executors, and reviewers to confirm decisions, unresolved items, and actions. Verbatim / per-speaker / replayable content is merely transcript source material; pre-meeting preparation goes to `memo-brief.md`; non-meeting status goes to `weekly-report.md`; statutory "minutes" of Party and government organs go to `official-redhead.md`.

<a id="子类型与治理证据"></a>
## Subtypes and Governance Evidence

Ordinary working meetings may be streamlined to meeting identity, decisions, unresolved items, and actions; project decision meetings add necessary rationale and review materials; board, committee, voting, or statutory meetings record attendance, quorum, conflicts of interest, motions, vote results, precise resolutions, and certification in accordance with the charter / applicable rules.

Evidence may come from the agenda, attendance records, actual review materials, motions / votes, and recordings / verbatim transcripts, but the body should only link key sources and not copy attachments in a way that drowns out decisions. Conflicting sources are retained side by side and referred to the chair / participants for confirmation.

<a id="结构与高质量写法"></a>
## Structure and High-Quality Writing

Indicate name / type, date and time, location / method, chair / recorder, and draft / approved status; each agenda item centers on outcomes rather than the order of remarks. Action items state deliverable / action, responsible person / unit, time requirements, and status. For missing information, use specific placeholders such as `[决议原文待确认]`, `[owner 待确认]`; when quorum or approval is unclear, do not claim validity, keep it as a draft, and enter the confirmation process.
