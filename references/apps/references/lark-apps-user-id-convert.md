# apps +user-id-convert

Convert a batch of known IDs between **Miaoda user_id** and **Feishu Open Platform IDs** (open_id / union_id / Feishu user_id). For runtime command facts, `lark-cli apps +user-id-convert --help` prevails.

<a id="何时用"></a>
## When to use

A Code Agent in the sandbox often obtains a Feishu `open_id` through the `contact` / `im` domains, but downstream consumers (Miaoda plugins, approvals, gateways) consume the Miaoda `user_id` or Feishu `user_id`. This command fills in that intermediate conversion step. Typical scenarios:

- The feishu-approval plugin needs to initiate an approval, and `createApprovalInstance` requires a Feishu `user_id`, but you only have the Miaoda `user_id` → use `miaoda-to-feishu-user-id`.
- A plugin configuration form / people picker returns `open_id`, but ultimately you need to persist the Miaoda `user_id` → use `open-id-to-miaoda`.

It does only one thing—conversion. There is **no** local mapping table, cache, or permission pre-judgment, and it does not guess the direction. It does not replace permission checks: whether you can obtain the target ID is still determined by the upstream scope and the visibility scope of the document/approval itself; this command only converts the format of a known ID.

<a id="命令骨架"></a>
## Command skeleton

- Required `--convert-type`: conversion direction enum; if missing or invalid, it directly reports a readable validation error and does not guess a default direction.
- Required `--ids`: comma-separated, or `@文件` / `-` (stdin). 1–100 per call (server-side limit is 100; the CLI additionally rejects empty batches to avoid empty runs). **No deduplication**; returned in input order.
- Read-only command, no write side effects, does not require `--yes`.
- Requires scope `spark:directory.user.id_convert:read`. Rate limit 50 req/s; the CLI does not automatically retry.

<a id="--convert-type-方向表"></a>
### `--convert-type` direction table

| `--convert-type` | Meaning | Target form |
| --- | --- | --- |
| `miaoda-to-open-id` | Miaoda user_id → Feishu Open ID | `ou_…` |
| `miaoda-to-union-id` | Miaoda user_id → Feishu Union ID | `on_…` |
| `open-id-to-miaoda` | Feishu Open ID → Miaoda user_id | Numeric string |
| `union-id-to-miaoda` | Feishu Union ID → Miaoda user_id | Numeric string |
| `miaoda-to-feishu-user-id` | Miaoda user_id → Feishu user_id | Number (employee_id) |

<a id="示例"></a>
## Examples

```bash
# Batch convert open_id to Miaoda user_id
lark-cli apps +user-id-convert --convert-type open-id-to-miaoda --ids ou_abc123,ou_def456 --as user

# Read the ID list from stdin
printf 'ou_abc123,ou_def456' | lark-cli apps +user-id-convert --convert-type open-id-to-miaoda --ids - --as user

# Only view the request body to be sent, without actually calling
lark-cli apps +user-id-convert --convert-type miaoda-to-feishu-user-id --ids 1234567890123456 --dry-run --as user
```

<a id="输出契约"></a>
## Output contract

Standard apps stdout envelope; the agent uses `ok == true` to determine success (not `code == 0`). Response fields preserve the server-side `snake_case`.

- `data.convert_type`: echoes the passed `--convert-type`.
- `data.items[]`: `{index, source_id, target_id}`, where `index` is the 0-based position of that ID in `--ids`.
- `data.missed[]`: unresolved IDs silently dropped by the server; the CLI reconstructs them using an input-position diff, `{index, source_id, reason: "not_found"}`.
- `meta`: `{total, hit_count, missed_count}`, `total` = `--ids` input count (including duplicates, no deduplication), and `hit_count + missed_count = total`.

**Partial hits**: as long as any ID in the batch cannot be converted, it is not an error—the server omits that item, and the CLI places it into `missed` (`reason: not_found`), while preserving `index` = input position; duplicate IDs can also be backfilled by position.

<a id="agent-规则"></a>
## Agent rules

- **Direction mismatch is not an error**: for example, under `miaoda-to-open-id` you pass an ID starting with `ou_`; the server omits it → it falls into `missed`. When you see `missed`, first check whether the ID prefix is consistent with the `--convert-type` direction.
- **The entire batch being rejected** (server-side `code != 0`) is the only `api` error, with a pass-through code and `log_id`; do not retry. The same applies to rate limiting: reduce the call frequency.
- Results are returned only once on stdout; they are not written to disk or to session context.

<a id="边界"></a>
## Boundaries

Only converts ID formats; it does not determine whether the caller is authorized to obtain the target ID. Whether permission exists is determined by the upstream scope and the resource's own visibility scope; this command does not perform pre-checks.
