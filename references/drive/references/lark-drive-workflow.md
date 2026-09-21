<a id="lark-drive-workflow-总框架"></a>
# lark-drive Workflow General Framework

This document is the operating protocol and registry for the `lark-drive` workflow general framework. It is intended for AI Agent execution and is only responsible for routing workflows that have been incorporated into this general framework.

`Workflow Registry` is the sole registration source for this general framework. Requests that do not match the registry must be handled as "unregistered workflow handling"; do not extend by analogy based on existing workflows.

<a id="必读上下文"></a>
## Required Context

Follow the execution and authorization rules in the unified entry point. Only read [General Diagnostics](../../shared/index.md) when an authentication error occurs.

Downstream references may only be loaded progressively on demand. Do not preload all workflow files or related skills just because this general framework is matched.

<a id="能力边界"></a>
## Capability Boundaries

`lark-drive` workflow general framework uses `lark-drive` as the general entry point for Drive / Docs / Wiki asset orchestration. Other domain skills are loaded as auxiliary capabilities only when a workflow already incorporated into this general framework explicitly requires them.

| Layer | Owns | Must Not Own |
|-------|------|--------------|
| `../index.md` | Short routing from user intent to a specific workflow entry | Long-flow logic, unregistered scenarios |
| `lark-drive-workflow.md` | Shared operating protocol, Artifact Contract, Workflow Registry, loading rules | Non-runtime background explanations, broad roadmaps, scenario-specific execution details |
| Registered workflow file | Scenario scope, state machine, Command Map, confirmation thresholds, verification rules | Other scenarios, hidden writes, capability claims not supported by CLI/API |

<a id="执行协议"></a>
## Execution Protocol

Every workflow incorporated into this general framework must follow the same execution skeleton:

```text
route -> scope -> read -> assess/plan -> confirm -> execute -> verify -> done
```

Operating rules:

1. Before reading or writing assets, first resolve the user intent to exactly one workflow incorporated into this general framework.
2. Before expensive reads or write planning, first resolve and confirm `target_scope`.
3. Facts must come from executable CLI commands or referenced skills; do not infer governance conclusions from directory structure alone.
4. Checks that cannot be executed must be recorded in `unsupported_checks` and must not be silently omitted.
5. A plan must be produced before writing. Writes within the same authorized plan are executed consecutively; additional confirmation is only needed when scope is added or actions are materially changed.
6. When CLI/API supports verification, writes must be verified with a fresh read afterward.
7. At the end, enter `done` and return completed items, verification results, and remaining limitations. Do not describe external approvals that are not yet complete as completed.

## Artifact Contract

Every workflow incorporated into this general framework must maintain the following internal fields:

| Field | Meaning |
|-------|---------|
| `workflow_id` | The workflow name registered in this general framework, for example `permission_governance` |
| `current_state` | Current workflow state |
| `target_scope` | Confirmed target scope and the user's original input |
| `identity` | Current identity and execution perspective, usually `user` |
| `facts` | Evidence obtained from CLI reads or referenced skills |
| `plan_items` | Candidate actions; each item includes command family, target, risk, verification method |
| `unsupported_checks` | Checks that cannot be executed due to CLI/API coverage, target type, authentication, or scope limitations |
| `partial` | Whether the result is incomplete, and the reason for incompleteness |
| `execution_results` | Execution results of confirmed writes |
| `verification_results` | Fresh read verification results, or explicit asynchronous approval limitations |

User-visible output defaults to a concise chat summary. Only create local files or Feishu documents when the user requests it, when the result is too large to display appropriately in chat, or when the current workflow explicitly requires a shared artifact.

## Workflow Entry Contract

Every workflow entry file incorporated into this general framework must enable the Agent to directly judge and execute:

- When to enter the workflow, and which requirements do not belong to the workflow;
- How to map to the state machine of the shared execution skeleton;
- Which references need to be loaded on demand for the current state;
- Which command families are available, and the read/write risk boundaries;
- How to confirm before writing, and how to verify after writing;
- Which fields the final reply must include, or which output templates to use.

Each workflow incorporated into this general framework starts by default with a single independent reference file. Only when the write, rollback, or verification flow is complex enough to affect readability should phase files be split out further.

## Risk / Structure Gate

Every workflow incorporated into this general framework must declare both `Risk Level` and `Structure Level`. The risk level determines the safety threshold; the structure level determines file splitting. High-risk writes do not necessarily mean phase files must be split.

Risk Level:

| Level | Meaning | Runtime Requirement |
|-------|---------|---------------------|
| `R0` | read-only: read-only discovery, analysis, reporting | Record fact sources, `unsupported_checks`, and `partial` reasons |
| `R1` | low-risk write: low-risk writes such as creating drafts and generating temporary artifacts | Explain scope before writing, return result link or identifier after writing |
| `R2` | high-risk write: high-risk writes such as permission changes, batch moves, label modifications | Pre-write plan, accurate diff, explicit user confirmation, fresh read verification |
| `R3` | destructive / recovery-sensitive write: deletion, automatic archiving, bidirectional sync, rollback cleanup | Recovery boundaries, execution logs, batching strategy, failure stop conditions, and scope authorization |

Structure Level:

| Level | File Shape | When To Use |
|-------|------------|-------------|
| `S1` | compact entry only | Read-only, lightweight audits, simple plans, no complex writes |
| `S2` | entry + optional `commands` / `outputs` / `artifacts` references | Has command examples, output templates, a small number of high-risk writes, but the state chain can be expressed centrally |
| `S3` | entry + phase files + optional shared references | Multi-stage writes, complex verification, recovery / rollback, long tasks, or batched execution |

Escalation rules:

1. New workflows start by default from `S1`.
2. When an entry file exceeds about 300 lines, prioritize splitting out `commands`, `outputs`, or `artifacts` references.
3. Only escalate to `S3` phase files when the execution, verification, recovery, or rollback state chain is complex enough to affect readability.
4. Vertical business packages should preferentially serve as recipes / policies / templates for existing workflows, and should not by default add independent workflows.
5. Existing examples: `permission_governance` is `R2/S2`; `knowledge_organize` and `topic_move_collector` are `R2-R3/S3`.

<a id="加载与拆分边界"></a>
## Loading and Splitting Boundaries

- Each scenario incorporated into this general framework retains by default only one compact workflow entry file.
- Do not create placeholder references / registry entries for unregistered or future scenarios.
- Only when a workflow already has executable rules may it appear as a workflow of this general framework in `index.md` and be added to `Workflow Registry`.
- Multi-file phase splitting is only used for `S3` scenarios where the execution, rollback, or verification flow is complex enough to affect readability.

## Workflow Registry

| Workflow | Status | Risk | Structure | Entry File | Trigger                                                         |
|----------|--------|------|-----------|------------|-----------------------------------------------------------------|
| `permission_governance` | Registered | `R2` | `S2` | [`lark-drive-workflow-permission-governance.md`](lark-drive-workflow-permission-governance.md) | Permission audits, public links/external access, copy/download/comment/sharing settings, permission requests, owner transfer / batch owner transfer, confidentiality label adjustments |
| `knowledge_organize` | Registered | `R2-R3` | `S3` | [`lark-drive-workflow-knowledge-organize.md`](lark-drive-workflow-knowledge-organize.md) | Organize Drive / folders / document libraries / Wiki, inventory directory structure, categorize resources, generate an organization plan, and create directories or move resources after user confirmation      |
| `topic_move_collector` | Registered | `R2-R3` | `S3` | [`lark-drive-workflow-topic-move-collector.md`](lark-drive-workflow-topic-move-collector.md) | Search materials across containers by topic, keyword, or content clues, verify relevance and move eligibility, and archive to Drive folders or Wiki nodes after user confirmation    |

## Workflow Loading

When user intent matches a workflow registered in this general framework:

1. First read this general framework file.
2. Only read the entry file matched in `Workflow Registry`.
3. Continue loading additional references according to that workflow's progressive load map.
4. Unless the user changes intent, or the current workflow explicitly routes to another workflow, do not read other workflow files.

<a id="未注册-workflow-处理"></a>
## Unregistered Workflow Handling

`Workflow Registry` is the sole registration source for this general framework. When a user request is not listed in the registry as a workflow or is a combined governance scenario:

1. Break the request into operations that existing modules or CLI capabilities can complete, and first verify parameters and data dependencies.
2. Combine these operations within the user's authorization; there is no need to stop just because the registry has no preset flow.
3. Capabilities not supported by the interface or results that cannot be verified should be stated truthfully; do not invent APIs or governance conclusions.
