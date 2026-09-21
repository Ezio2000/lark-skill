# OKR

Default to `--as user`. Bot reads are available for an explicitly selected application workflow with appropriate access. Resolve people through [Contacts](../contact/index.md), then use `+cycle-list` and `+cycle-detail`; reuse known IDs.

## Choose the operation

- Read objectives/KRs: [cycles](references/lark-okr-cycle-list.md), [detail](references/lark-okr-cycle-detail.md), then indicators/progress only if needed.
- Create one objective or KR: [create](references/lark-okr-create.md). Create a set: [batch-create](references/lark-okr-batch-create.md).
- Edit content/notes/deadline: [patch](references/lark-okr-patch.md).
- Change order/weight: [reorder](references/lark-okr-reorder.md), [weight](references/lark-okr-weight.md).
- Numeric progress/completion: [indicator-update](references/lark-okr-indicator-update.md). To change units/targets, read [indicators](references/lark-okr-indicators.md).
- Narrative progress: [progress-create](references/lark-okr-progress-create.md); combine percentage updates only when the reference supports the intended unit.
- Align objectives: [alignments](references/lark-okr-alignments.md).
- Comments across a cycle: `+comment-detail`; one entity or cycle-global comments: `+comment-list`.

## Non-interchangeable values

Score is not progress. Use `+patch --score` only for an explicit scoring request; score ranges from 0 to 1 with at most one decimal place. "75% complete" normally means a quantitative indicator, not score `0.75`.

Reordering must include all IDs required by the target collection. Updating KR weights must include every KR under the objective and sum to 1. Alignments cannot target the caller's own objectives, and the two cycles must overlap.

Handle categories only when requested or when objective creation fails because the tenant requires one. Query enabled user categories; choose a semantically clear match, asking only if that choice matters and is ambiguous.

Read [entities](references/lark-okr-entities.md) for unfamiliar relationships and [ContentBlock](references/lark-okr-contentblock.md) when building rich content. Comment writes are user-only. Progress/comment deletion is permanent: scope it to the authorized object.

Ordinary todos belong to [Tasks](../task/index.md), scheduling to [Calendar](../calendar/index.md), and unsupported performance-review APIs to [OpenAPI discovery](../openapi-explorer/index.md).

## Operation references

- [okr progress list](references/lark-okr-progress-list.md)
- [okr progress update](references/lark-okr-progress-update.md)
- [okr comment list](references/lark-okr-comment-list.md)
- [okr comment create](references/lark-okr-comment-create.md)
- [okr comment solve reopen](references/lark-okr-comment-solve-reopen.md)
- [okr progress get](references/lark-okr-progress-get.md)
- [okr progress delete](references/lark-okr-progress-delete.md)
- [okr image upload](references/lark-okr-image-upload.md)
- [okr comment detail](references/lark-okr-comment-detail.md)
- [okr comment get](references/lark-okr-comment-get.md)
- [okr comment patch](references/lark-okr-comment-patch.md)
- [okr comment delete](references/lark-okr-comment-delete.md)

