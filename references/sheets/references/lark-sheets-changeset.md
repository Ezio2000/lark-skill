# Lark Sheet Changeset

<a id="使用场景"></a>
## Use Cases

Read the **changeset (list of change operations)** between two revisions, to **verify whether a given edit (especially an AI edit) actually satisfies the user's requirements**.

Typical scenario: after an AI agent makes a batch of edits to a sheet, it wants to confirm whether what it "said it did" matches what "actually landed on the sheet" — pull the changeset between the pre-edit revision and the post-edit revision, and check action by action whether the actions cover the modifications the user requested, and whether there are any extra or missing changes.

<a id="版本revision语义"></a>
## Revision Semantics

- "Revision" here refers to the sheet's **CS revision** (a revision number that increases monotonically with each commit), not a named version in the document history.
- `--start-revision` is the verification baseline, i.e. the revision you consider to be "before the edit".
- `--end-revision` is the "after the edit" revision; **when omitted, it defaults to the latest revision**, returning all changesets from start to latest.
- **Revision span limit 20**: `end - start + 1 ≤ 20`; exceeding it will be rejected (the server also enforces a fallback of 20). When verifying large-span changes, pull them in segments.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+changeset-get` | read | Change records |

## Flags

### `+changeset-get`

_Common: URL/token (no sheet targeting)_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--start-revision` | int | required | Start revision (pre-edit baseline, >= 1) |
| `--end-revision` | int | optional | End revision (omitted means latest) |

<a id="返回结构"></a>
## Return Structure

Returns a JSON object, with the `changesets` array ordered by revision, where each element is the **raw action list** of one commit plus metadata:

```json
{
  "spreadsheet_token": "shtcnXXXX",
  "latest_revision": 142,
  "start_revision": 120,
  "end_revision": 135,
  "changesets": [
    {
      "revision": 121,
      "create_time": "2026-06-12T10:00:00Z",
      "actions": [
        { "action": "setCellRange", "sheetId": "...", "value": { /* ... */ } }
      ],
      "is_self_edit": false,
      "is_ai_edit": true
    }
  ]
}
```

- The outermost `latest_revision` is the **current latest revision number of the sheet** (unrelated to the query range), useful for determining which revision the sheet is currently at and what value `--start-revision` should take.
- `actions` is the **raw operation object without semantic rendering**, ordered by execution order within the commit. During verification, compare item by item: which sheet, which range, and what value each action changed, and whether it corresponds to the user's requirements.
- `revision` / `create_time` are used to determine "which revision this change belongs to and when it was made".
- `is_self_edit` indicates whether the changeset was committed by the current requesting user (committer is the same as the requesting user), i.e. "whether this is an edit I committed myself".
- `is_ai_edit` indicates whether the changeset was committed by an AI client (`member_id` is 10 / 11). During verification, `is_ai_edit=true` are the edits written by the AI (rather than manual user edits), and are the main object for checking whether the AI fulfilled the requirements.

<a id="复核工作流判断-ai-是否真实完成诉求"></a>
## Verification Workflow (determining whether the AI actually fulfilled the requirements)

1. Note the revision before the AI starts editing (the pre-edit `+workbook-info`, or the revision returned by the previous tool call, can serve as `--start-revision`).
2. After the AI finishes editing, run `+changeset-get --url <表格> --start-revision <编辑前版本>` (without passing end → fetch up to latest).
3. Iterate over `changesets[].actions` and check:
   - Whether every modification requested by the user has a corresponding action;
   - Whether there are any unauthorized / extra modifications (touching sheets / ranges the user did not ask to touch);
   - Whether the target range and values of the actions are consistent with the requirements.
4. If the revision span may be > 20, pull in segments (e.g. `start..start+19`, `start+20..` …).

<a id="注意"></a>
## Notes

- `+changeset-get` is a **read-only** operation and does not modify the sheet.
- The changeset for large-span / large-batch edits may be large; the output is already gzipped at the transport layer. Narrow the revision range if necessary.
- This tool uses the read-only scope `sheets:spreadsheet:read` and requires view permission on the sheet.

## Examples

### `+changeset-get`

Common: `--url` / `--spreadsheet-token` (choose one, no sheet targeting). The changeset is workbook-level history and does not accept sheet targeting flags.

Example:

```bash
# Pass only the start revision → returns all changesets from that revision to latest (most common: verifying the diff before and after an AI edit)
lark-cli sheets +changeset-get --url "https://example.feishu.cn/sheets/shtXXX" --start-revision 120

# Pass start + end revision (revision span end-start+1 ≤ 20)
lark-cli sheets +changeset-get --spreadsheet-token shtXXX --start-revision 120 --end-revision 135
```

Output contract (envelope.data):

- `latest_revision` — current latest revision number of the sheet (unrelated to the query range)
- `start_revision` / `end_revision` — actual query range (when `--end-revision` is omitted, `end_revision` = latest revision)
- `changesets[]` — ordered by revision; each item contains `revision` / `create_time` / `actions` (raw operation list) / `is_self_edit` / `is_ai_edit`

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute Constraints

- The `Validate` stage only performs the XOR check (choose one of `--url` / `--spreadsheet-token`) and the revision upper-limit validation (`--start-revision ≥ 1`; when `--end-revision` is passed, `end ≥ start` and `end - start + 1 ≤ 20`); **network access is prohibited**.
- `DryRun` outputs the request template and does not actually pull the changeset.
- Only the `Execute` stage initiates the changeset query; when `--end-revision` is omitted, the server resolves it to the latest revision.
