# `docs +script`

<a id="脚本列表"></a>
## Script List

| `--command` | Purpose |
|-|-|
| `init-draft` | Create an exclusive workspace with a Presentation Decision baseline, and reserve XML paths that do not yet exist. |
| `parse` | Parse a local or online document, return a profile, and check decisions and resources. |

Each script uses only the dedicated parameters listed in its subsection; all scripts can use the common parameters at the end of the document.

## `init-draft`

<a id="参数"></a>
### Parameters

| Parameter | Required | Usage |
|-|-|-|
| `--command init-draft` | Yes | Select this script. |
| `--presentation-decision` | Yes | Decision JSON; accepts inline JSON, `@相对或绝对路径`, or `-` (stdin). |

```bash
lark-cli docs +script --command init-draft \
  --presentation-decision '{}' \
  --format json
```

For path return values and usage, see [Create Workflow Step 4](lark-doc-create-workflow.md).

- Execute before generating the body; do not create the working directory or decision file yourself. The CLI always generates `draft_<8位十六进制字符>_folder/draft.xml`; use the actual returned path.
- The decision is a single JSON object; pass `{}` when there are no quantifiable constraints. `audience`, `reader_task`, `genre_contract`, `adapter`, `presentation_mode`, `visual_plan.reason`, and each block's `purpose` are optional descriptive information, and may be omitted, be an empty string, or be `null`; they do not participate in pass/fail determination.
- `visual_plan`, `visual_plan.blocks`, each item's `type`, and `min_count` may all be omitted or be `null`, indicating they are not set. Writing `[]` for `blocks` also indicates no quantity constraint; when an entry lacks `type` or `min_count`, that entry's quantity validation is not enabled.
- Explicitly filled fields must still be valid: `visual_plan` is an object, `blocks` is an array, `type` is a supported block type, and `min_count` is a positive integer. An empty string type, unknown block type, zero/negative, or non-integer quantity will report an error, even if the other field is missing. Only entries where both `type` and `min_count` are valid participate in quantity checking; enabled entries cannot declare the same type repeatedly. Compatible `list` constraints are checked by the combined quantity of `<ul>` and `<ol>`.
- For `word_count`, fill in `{min,max}` only when word count validation is needed; write `null` for the unspecified side, at least one side must be a positive integer, and `min <= max`. Omit the entire field when there is no word count requirement.
- Returns `data.cwd` (the absolute working directory for this file operation), `data.workspace` (relative to the workspace), `data.draft_path` (relative XML path), and the operation hint `data.tip`. The workspace and the `.presentation-decision.json` within it already exist, while the XML does not yet exist; write directly to `<cwd>/<draft_path>`, and do not read that path before the first write. Subsequent CLI uses the returned `cwd`; for resource path rules, see [lark-doc](../index.md).
- Always use `draft_path` subsequently; do not create another XML, reuse another task's path, or modify the `.presentation-decision.json` in the workspace; preserve `workspace` and the creative drafts within it.

## `parse`

<a id="参数-1"></a>
### Parameters

| Parameter | Required | Usage |
|-|-|-|
| `--command parse` | Yes | Select this script. |
| `--content` | Choose one of two | The literal content of the local XML, `@相对或绝对路径`, or `-` (stdin). |
| `--doc` | Choose one of two | Online Docx/Wiki URL or token; mutually exclusive with `--content`. |
| `--presentation-decision` | No | Decision JSON used to check the current input; supports inline, `@相对或绝对路径`, or `-`. |

```bash
lark-cli docs +script --command parse --content "@./document.xml" --format json
lark-cli docs +script --command parse --doc "<Docx/Wiki URL 或 token>" --format json
lark-cli docs +script --command parse --content "@./document.xml" --presentation-decision '<JSON>' --format json
```

- When `--content` and `--presentation-decision` are used together, at most one parameter reads stdin.
- The decision format is the same as `init-draft`: missing constraints are not checked, explicitly filled but invalid values report an error, and valid and complete constraints participate in checking. `passed` only indicates that the checks enabled this time passed; it does not mean that undeclared requirements have been satisfied.
- When using `--content "@./<init-draft 返回的 data.draft_path>"`, the saved decision is automatically loaded; an explicit `--presentation-decision` takes precedence.
- `--doc` requires `docx:document:readonly`; `--content` does not call OpenAPI.
- Returns `data.assessment.status`, `data.profile`, and `data.diagnostics[]` when present; the profile includes `word_count`, `char_count`, `block_count`, and `blocks[]`. The top-level `ok` only indicates whether the command executed successfully. When the profile, decision, or resource precheck does not pass, the command still returns with `ok:true` and exit code 0, but `assessment.status` is `failed`; each diagnostic provides `severity`, a stable `code`, `msg`, optional `expected` / `actual`, and `suggested`. Remote images that fail for the same reason are merged into one diagnostic, and the image indices are listed in `image_indices[]`, to avoid duplicate prompts. After fixing, parse again until `assessment.status` is `passed`.
- `parse` is not an XML/SDK schema validator. Success with no warning also does not guarantee that the server will accept it; before writing, you must still recheck according to the XML rules.

<a id="所有脚本通用参数"></a>
## Common Parameters for All Scripts

| Parameter | Usage |
|-|-|
| `--as user|bot` | Select identity. |
| `--dry-run` | Return only the execution plan, without networking, parsing, or writing files. |
| `--format` | Output format: `json|pretty|table|ndjson|csv`; the model uses the default `json`. |
| `--json` | Alias for `--format json`. |
| `--jq` / `-q` | Trim JSON; must not be used together with non-JSON formats. |
| `-h` / `--help` | View help. |
