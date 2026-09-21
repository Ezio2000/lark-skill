# Lark Sheet Formula Verify (+formula-verify)

> **Scope of this document**: The diagnostic entry point for "whether a Feishu Sheet formula truly has zero errors after being written." The rules for writing formulas and the semantic rules for Excel→Feishu migration are all governed solely by `references/lark-sheets-formula-translation.md` as the single authority, and are not repeated here; this document focuses on "how to discover formula errors with a single call after writing" and the delivery of a one-time full-range asynchronous status check for AI formulas.
>
> **Boundaries**: This document does not cover how to write formulas (go to `references/lark-sheets-formula-translation.md`), nor how to write formulas into a sheet (go to `references/lark-sheets-write-cells.md` / `references/lark-sheets-batch-update.md`). This document covers only two things:
>
> - **Ordinary formulas**: When a task involves writing formulas to a sheet, batch-filling formulas, `--copy-to-range` extending formulas, or importing a workbook containing formulas, run `+formula-verify --exit-on-error` segment by segment over the formula range for this operation; `errors_found` fixes and `partial` splitting for continued scanning are only considered complete after all segments are `status='success'`.
> - **AI formulas** (`=AI(...)`): Do not use the ordinary-formula "poll until zero-error" logic; instead use `+formula-verify --ai-only --range` to deliver according to the one-time full-range asynchronous status check rules of "AI Formula Verification."

<a id="为什么需要自检"></a>
## Why self-check is needed

Feishu Sheets already computes results in real time, but "computed" and "computed correctly" are two different things. Common gaps:

- Formula compilation failure → the cell falls back to text (the `formula_errors[]` returned by write-type shortcuts is a **compilation failure** signal).
- Formula compiles successfully but has a **runtime error**: `#REF!` / `#DIV/0!` / `#VALUE!` / `#NAME?` / `#NULL!` / `#NUM!` / `#N/A`—this category cannot be seen by looking only at `formula_errors[]`; you must scan the cell values.

`+formula-verify` merges the two signal paths into a single unified JSON: one call aggregates the formula error list + compilation failure list + the location and samples for each error type, so the caller can locate and fix them accordingly. Whenever a task writes formulas to a sheet, use it as a formula error code health check; limit it to the newly added / modified formula range for this operation, scan segment by segment, and include `--exit-on-error`. `status='success'` only indicates the absence of compilation/runtime errors; it does not judge whether field mappings, thresholds, units, definitions, or business results are correct—for business semantic sentinels see `references/lark-sheets-formula-translation.md`.

<a id="调用契约"></a>
## Invocation contract

Minimal invocation form:

| Parameter | Meaning |
|---|---|
| `--url` / `--spreadsheet-token` | Sheet locator (XOR, choose one, required) |
| `--sheet-id` / `--sheet-name` | Limit to sub-sheets (mutually exclusive; if omitted, scan all visible sub-sheets) |
| `--range` | Limit to an A1 range; if omitted, use each sheet's `current_region` |
| `--max-locations` | Upper limit of samples per error type, default 20 |
| `--exit-on-error` | Return a non-zero exit code when `status='errors_found'`; with `partial` the caller still needs to check status and split for continued scanning |
| `--ai-only` | Only check `=AI(...)` asynchronous computation status; used separately from the ordinary-formula 7-category error scan |

Core returned fields:

- `status` ∈ `success` / `errors_found` / `partial`—the **only machine-readable health criterion**.
- `total_errors` / `total_formulas` / `scanned_cells`—scale metrics for this scan.
- `has_more`—when true, indicates the scan was truncated by an internal limit (see "Truncation and continued reading" below), and the full range was not covered.
- `error_summary[<错误类型>]`—the `count` / `locations[]` / `samples[].{address,formula,depends_on}` for each error type.
- `compile_errors[]`—merges the compilation failure list left by the most recent write; appears together with runtime errors when both exist.
- `warning_message`—appears only when `has_more=true`, informing the caller to narrow `--range` / split `--sheet-id` for continued reading.

<a id="写入后诊断规则"></a>
## Post-write diagnostic rules

After any batch formula / formula-containing column write completes, you must call `+formula-verify --exit-on-error` segment by segment over the newly added / modified formula range for this operation. Do not wait for the user to explicitly say "verify the formulas" before executing; as long as the task action includes writing formulas, this step is part of the completion path. AI formulas do not follow this rule: `=AI(...)` is asynchronous computation, so deliver according to the one-time full-range asynchronous status check rules of "AI Formula Verification," and do not wait for `status='success'`. Trigger scenarios:

- `+cells-set` / `+csv-put`
- `+cells-set --copy-to-range` / extending a template cell's formula to an entire column or block
- `+workbook-import`
- `+batch-update` contains a write sub-operation
- `+table-put` (when any column contains formulas)
- `+workbook-import` (when the imported xlsx contains formulas)

Handling rules:

1. `status='success'` → the current segment has no compilation/runtime errors; but you must still verify fields, thresholds, units, full range, and business sentinels according to the business semantic contract of `references/lark-sheets-formula-translation.md`. Only after all target segments are success and the sentinel values are correct is it complete.
2. `status='partial'` → the scan was truncated by an internal limit; narrow `--range` or split `--sheet-id` for continued scanning; the unscanned area is still unknown, and a delivery note cannot substitute for verification.
3. `status='errors_found'` and `compile_errors[]` is non-empty → fix the formula syntax according to `compile_errors[].reason` (Feishu function names / range syntax / reference style); only when it truly cannot be expressed should you downgrade to a static value, and explain the reason and the risk of not being linked.
4. `status='errors_found'` and only runtime errors remain → troubleshoot the root cause according to `error_summary`'s `samples[].formula` + `depends_on` (division by zero? empty values participating in operations? out-of-bounds references? date difference syntax? array semantics?), then re-verify after fixing.
5. If the same error still fails after 3 consecutive fixes → you may use `IFERROR` as a fallback or revert to a pure value, but the downgraded target cell is no longer a formula; you need to read back to confirm there is no residual erroneous formula, and clearly state in the delivery note that it will not update with the source data.

Notes:

- Calling `+cells-set --copy-to-range` to continue extending while in the `status='errors_found'` state will copy and amplify the errors; it is recommended to handle critical errors first.
- "Compilation failed but no runtime error" is not zero-error (a cell that failed to compile is text, not a formula, at this moment, and once the source data changes it can never compute a value again).
- Confirming by visually reading only the first and last 5 rows is unreliable—errors in the middle of the sheet, in hidden rows, or in merged areas simply cannot be seen this way; `+formula-verify` can supplement this diagnostic perspective.
- Verifying only the first row of the write area is not enough: after batch-filling formulas, spot-check the first row, middle section, tail, and summary row at the same time; the goal is to discover problems like "only the first N rows were filled," "detail formulas were written into the total row," or "the tail is still empty/error values."
- When fixing formulas, locate the root-cause cell first, then look at the downstream chain. Do not rewrite all downstream cells contaminated by upstream errors; for formulas of the same type, prefer copying/changing references from an adjacent correct cell, and after writing, read back the key downstream cells to check whether `#VALUE!` / `#REF!` still remain.
- Lookup/match formulas must have error handling: do not write bare `VLOOKUP` / `XLOOKUP`. When there is no match, return explicit text (e.g., "no match found"); do not silently return an empty string, unless the user explicitly requests an empty value.
- Ranking/sorting formulas must handle empty values, 0 values, and items that do not participate in ranking; these items should remain empty/0, rather than entering the general ranking formula and getting a positive integer rank.

<a id="截断与续读"></a>
## Truncation and continued reading

The backend has an internal hard limit that truncates the total number of scanned cells (not exposed to the caller); once exceeded, it immediately returns `has_more=true` + `warning_message`, and `error_summary` / `compile_errors` only cover the already-scanned portion. Handling path:

- Prioritize splitting key output areas into multiple calls by `--sheet-id` / `--sheet-name`.
- Within the same sheet, slice by `--range` (e.g., first `A1:Z200` then `AA1:AZ200`), and diagnose block by block.
- Continued scanning is part of the completion condition: the formula range written in this operation must all be split and scanned to `success`; you cannot end by merely listing the uncovered range in the delivery note due to insufficient time (same as handling rule 2). If it truly cannot be fully scanned in this round, downgrade the unverified formulas to static values and declare it according to handling rule 5, rather than leaving unverified live formulas.

<a id="ai-公式校验--ai-only"></a>
## AI Formula Verification (`--ai-only`)

Feishu Sheets provides a unified **`AI` formula** (`=AI(prompt, [range])`, driven by natural language for translation / classification / sentiment analysis / information extraction / summarization / polishing, etc.; for syntax and the list see `references/lark-sheets-formula-translation.md`). AI formulas are written the same way as ordinary formulas (reusing `+cells-set` / `set_cell_range`, no special interface needed), but **computation is asynchronous**: after writing, you must wait for the AI to finish computing before there is a result. The ordinary `+formula-verify` only scans local cell values (7 categories of Excel errors) and cannot see the computation status of AI formulas.

`--ai-only` makes `+formula-verify` verify only AI formulas and skip the ordinary-formula Excel error scan, dedicated to the asynchronous status check after writing AI formulas. **It must be the first verification entry point; it is forbidden to first use `+cells-get` / `+csv-get` to poll for AI results.**

- **`--ai-only` returned fields** (the machine-readable criteria are based on these, all integers):
  - `ai_formula_total`—the AI formula summary count returned by the backend, **not the number of cells written in this operation** (multiple AI formulas written in the same batch may be counted as only 1), and `--range` does not narrow it either—**trust the cell locations in the return; do not compare it for equality against the expected count for this operation**.
  - `ai_formula_done`—the number that have already computed results.
  - `ai_formula_pending_count`—the number still computing in the background (`pending`).
  - `ai_formula_failed_count`—the number that failed / are unsupported.
- **Asynchronous expectation**: A small number of AI formulas usually compute results quickly; after a batch write, some formulas still being `pending` (computing) is normal, and Feishu will continue computing in the background.
- **`--exit-on-error` compatibility**: When `--ai-only --exit-on-error`, if `ai_formula_failed_count > 0`, return a non-zero exit code, making it easier for scripts / CI to converge.
- Can coexist with `--sheet-id` / `--sheet-name` / `--range`, meaning "verify AI formulas only within the specified range."
- **Do not include `--ai-only` for ordinary formulas**: including it will skip the 7-category Excel error scan, which means ordinary formulas are effectively unverified.

**`--range` uses the entire write range; do not sample**: `--ai-only` is a read-only operation with low cost, and `--range` should cover **all** AI formula ranges written in this operation (not a representative subset)—subset spot-checking will miss the case where "only the last batch in the column was written incorrectly." But do not use `--range` as a filter: it is only passed through to the backend, and the AI-only summary is not guaranteed to narrow by it; failed items must be checked against the returned cell locations to confirm whether they fall within the write range for this operation. If the range is too large and triggers truncation (`has_more=true`), split by `--range` / `--sheet-id` according to "Truncation and continued reading."

**Required step: one-time formula text verification (not polling)**. After writing AI formulas, first perform **one** `+cells-get --include formula` on the seed cell / first cell to confirm that quotes / parentheses were not broken at the shell / CSV / JSON layer, and that what actually landed in the cell is indeed a `=AI(...)` formula rather than a broken literal or `#ERROR`. This step is done only once and only looks at the text; what is forbidden is only **using `+cells-get` to repeatedly poll for computation results** (result status always goes through `--ai-only`).

Delivery criteria (machine-readable): `ai_formula_failed_count == 0` within the entire write range; fix `failed` / `unsupported` first before discussing delivery. Once satisfied, you may deliver even if there are still `ai_formula_pending_count > 0`; there is no need to poll until all are complete; when delivering, tell the user "AI formulas are still running in the background, and results will complete gradually." In addition, the silent failure of "the formula was broken at the write layer and was not counted as an AI formula at all" will not appear as `failed`; it is caught by the one-time formula text verification above—do not expect to reconcile `ai_formula_total` against the expected count (that total is not necessarily narrowed by `--range`).

`ai_formula_failed_count > 0`, or when the text verification reveals `#ERROR`, broken parentheses (e.g., `E2)`), a truncated function name, or full-width parentheses, it means the formula string was broken at the quote layer and was not written in as a formula—do not keep waiting for pending; go back to `+cells-set` and rewrite that cell using `\"` escaping (for a write example see the AI formula section of `references/lark-sheets-formula-translation.md`).

Typical usage:

```bash
# After writing a batch of AI formulas, verify the computation status for the entire write range
lark-cli sheets +formula-verify --url <表URL> --sheet-name <子表名> --range <整个写入区间> --ai-only
# ai_formula_failed_count==0 is sufficient for delivery; pending will continue computing in the background
```

<a id="常见陷阱"></a>
## Common pitfalls

| Pitfall | Response |
|---|---|
| Error string localization | The backend identifies error categories by internal `error_kind` / `compute_status` fields, not by string matching; the 7 categories of English error codes the caller receives are output uniformly by the backend and are independent of locale. |
| `formatted_value` may hide errors | Some conditional formatting / custom number formats display `#DIV/0!` as blank. The backend reads the cell `error_kind` directly, without relying on `formatted_value`, bypassing this kind of masking. |
| Treating `partial` as full health | `partial` only indicates that the **already-scanned portion** has no errors; the remaining area is unknown; narrow ranges or split by sheet until the entire ordinary-formula range for this operation is success. |
| Compilation failure vs runtime error | In the same report, `compile_errors[]` and `error_summary` coexist. At the semantic layer, resolve `compile_errors[]` first, then do the runtime self-check. |
