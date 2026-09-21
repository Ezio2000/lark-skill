<a id="genre-contract-technical-document--技术文档-workplacetechnical_doc"></a>
# Genre Contract: Technical Document (`workplace.technical_doc`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Precise, falsifiable, stable terminology and versions; normative words are used only for explicitly adopted interoperability, security, or acceptance semantics |
| Visual Constraints | Use components such as code, tables, architecture / state / sequence diagrams when they have a clear content role to reduce implementation and diagnostic costs, but they must not replace contracts, evidence, or operational instructions |
| Content Logic | Must and can only choose one primary mode among design_rfc, api_reference, incident_diagnostic; advance respectively according to "evidence → trade-offs / design → acceptance", "contract → errors / compatibility", and "impact → hypotheses / checks → verification / escalation" |
| Facts / Boundaries | Mark object, environment, version, time, scope, and evidence window; separate facts, inferences, decisions, and unknowns; examples / diagrams do not replace contracts; any state-changing action must have authorization, impact, stop, rollback, and recovery verification, and key gaps are handled according to reader impact |
| Errors | Routing by keywords, mixing the three modes, design without trade-offs / acceptance, reference missing permissions / errors / lifecycle / compatibility, directly determining root cause for unknown failures, state changes without authorization / stop / rollback, or diagrams as the sole evidence — any occurrence is a failure |

<a id="先选唯一主模式"></a>
## First Choose the Single Primary Mode

| Primary Mode | Reader Task | Exclusions |
|-|-|-|
| `design_rfc` | Reviewers can approve and implement a future technical state, understanding alternatives, consequences, and acceptance | Product-observable behavior goes to PRD; established paths go to SOP |
| `api_reference` | Callers do not need to guess version, permissions, input, behavior, side effects, errors, and lifecycle | When interface trade-offs are still under discussion, go to design_rfc |
| `incident_diagnostic` | Responders use safe, differentiated actions to narrow unknowns, stop loss, recover, or escalate | Pure team learning goes to Retrospective; known repeated handling goes to SOP |

<a id="共同证据边界"></a>
## Common Evidence Boundaries

Mark object, environment, version, time, scope / preconditions, and evidence location / window; conclusions link back to repositories, IDL / schema, logs, metrics, traces, change records, or verification experiments. For gaps, use specific placeholders, narrowing, or `blocked` nearby; data classification, access, retention, replay, owner, time limits, and escalation form gates only when applicable.

Code and command examples must be actually verified and marked with environment / version; architecture, state, or sequence diagrams must have textual equivalents and must not become the sole evidence or sole operational instructions.

## Design RFC

Advance according to problem evidence → goals / non-goals → constraints / invariants → real alternatives and trade-offs under the same criteria → interface / data / state design → failures, security, compatibility, and migration → launch / rollback → observability, testing / acceptance → unresolved decisions. For each key decision, write the why, rejected options, and consequences; do not hide low confidence or version deviations.

## API Reference

Clearly write version / environment / permissions / signatures, input constraints, behavior / side effects / idempotency, output, known errors and actionable recovery, rate limiting / pagination / retries, compatibility / deprecation. For events, async, CLI, SDK, and streaming, supplement as needed with channel / message, delivery / ordering, lifecycle / exhaustion, I/O, cancellation, and backpressure; explicitly mark unknown semantics as unspecified, and do not infer commitments from examples.

## Incident Diagnostic

Advance according to impact and expected / actual → current state and evidence chain → falsifiable hypotheses → checks with high information gain and low side effects → stop loss / recovery verification → escalation and follow-up RCA. For each check, write the expected observation and the hypotheses it supports / rules out.

Before changing state, you must confirm authorization, target scope, potential side effects, stop conditions, rollback path, and recovery criteria; separate stop loss, root cause, and permanent fix. When evidence, authorization, owner, rollback, or escalation path is missing, provide only safe read-only checks and `blocked`; when security / legal matters are involved, first preserve evidence and escalate.
