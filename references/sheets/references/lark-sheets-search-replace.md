# Lark Sheet Search & Replace

<a id="替换前-dry-run--范围明确替换前建议"></a>
## Dry-run before replacement + clear scope (recommended before replacement)

The side effects of `+cells-replace` are irreversible (unless you write separate code to roll back). Before executing, you must:

1. **Clarify the replacement scope**: It is recommended to explicitly state "only replace column X / range X, or replace the entire sheet". Avoid defaulting to whole-sheet replacement—it is easy to mistakenly modify unrelated columns. The scope should be determined by the user's instruction; when ambiguous, proactively ask.
2. **Dry-run hit count**: First use `+cells-search` with the same scope, same keyword, and same matching options (case / exact / regex) to count the number of hits. Compare the count against the **expected hit count** (explicitly stated by the user or inferred from business understanding); if they do not match, investigate first (is the keyword too broad? is the scope too large?).
3. **Full verification after replacement**: After executing, use `+cells-search` again with the old keyword; the expected result is 0. When a complete range and an enumeration of old values are specified, search item by item; random sampling cannot substitute for this. **Exception**: When the new value itself contains the old value (such as `v1`→`v1.1`, or when the new value still contains the keyword after substring replacement), substring search will still hit, so the zero-hit criterion does not hold—instead use whole-cell exact matching (`--match-entire-cell`-type options) to verify, or directly read back representative cells to confirm they are already the new value. Do not judge that replacement did not occur based on non-zero hits and execute repeatedly (which would produce `v1.1.1`). Only when the user explicitly requests local xlsx / download / print, or when verifying a local Excel file before import, should you run the local artifact check script.

<a id="使用场景"></a>
## Use cases

Read and write. Search and replace text in Lark Sheets. This reference covers 2 shortcuts:

| Operation need | Tool to use | Description |
|---------|---------|------|
| Search/locate text | `+cells-search` | Returns the positions of matching cells; supports regex, exact matching, etc. |
| Find and replace text | `+cells-replace` | Batch replace text; in `--regex` mode, `--replacement` can use `$1` and `$2` to reference capture groups of `--find` |

**Common configuration mistakes (note)**:
- **Do not treat operation verbs as search terms**: When the user says "sum the amount", it is an operation action (summation), not a request to search for the text "sum the amount". Only use `+cells-search` when you actually need to locate the position of a text value.
- **Do not use search to understand sheet structure**: To understand headers and data structure, use `+csv-get` to read the first few rows, rather than using `+cells-search` to guess field names one by one.
- **Watch out for regex special characters**: When using regex matching, special characters such as `.`, `*`, `(`, and `)` need to be escaped.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+cells-search` | read | Cell |
| `+cells-replace` | write | Cell |

## Flags

### `+cells-search`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--find` | string | required | Text to find (interpreted as regex when used with `--regex`) |
| `--range` | string | optional | Search range (A1 format); whole sheet when omitted |
| `--match-case` | bool | optional | Case sensitive |
| `--match-entire-cell` | bool | optional | Match the entire cell exactly |
| `--regex` | bool | optional | Interpret `--find` as regex |
| `--include-formulas` | bool | optional | Also search within formula text |
| `--max-matches` | int | optional | Blast protection, default 5000 (hidden flag: not listed in `--help`, but can be passed normally) |
| `--offset` | int | optional | Skip the first N matches (for pagination), default 0 |

### `+cells-replace`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--find` | string | required | Text to replace |
| `--replacement` | string | required | Replace with; passing an empty string `""` is equivalent to "delete content" |
| `--range` | string | optional | Replacement range (A1 format); whole sheet when omitted |
| `--match-case` | bool | optional | Case sensitive |
| `--match-entire-cell` | bool | optional | Match the entire cell exactly |
| `--regex` | bool | optional | Interpret `--find` as regex |
| `--include-formulas` | bool | optional | Also replace within formula text |

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` arranged at the top (XOR rule).

### `+cells-search`

Example:

```bash
# Plain search
lark-cli sheets +cells-search --url "https://example.feishu.cn/sheets/shtXXX" \
  --sheet-name "Sheet1" --find "张三"

# Regex + range restriction
lark-cli sheets +cells-search --spreadsheet-token shtXXX --sheet-id "$SID" \
  --find "^[A-Z]{2}-\\d{4}$" --regex --range "A2:A1000"
```

Output contract (envelope.data):

- `matches` — list of hit cells, each containing `address` (A1) + `value` + `sheet_id`
- `total_matches` — total number of matches
- `has_more` / `next_offset` — pagination cursors (used to continue reading when the number of hits exceeds the single-page limit)

### `+cells-replace`

Example:

```bash
# Dry-run preview first
lark-cli sheets +cells-replace --url "https://example.feishu.cn/sheets/shtXXX" \
  --sheet-name "Sheet1" --find "v1" --replacement "v2" --dry-run

# Execute after confirmation
lark-cli sheets +cells-replace --url "https://example.feishu.cn/sheets/shtXXX" \
  --sheet-name "Sheet1" --find "v1" --replacement "v2"

# Regex capture groups: rearrange "2026-03" into "03/2026" ($1/$2 reference the capture groups of --find)
lark-cli sheets +cells-replace --url "https://example.feishu.cn/sheets/shtXXX" \
  --sheet-name "Sheet1" --regex --find "(\\d{4})-(\\d{2})" --replacement "$2/$1" --dry-run
```

> Although `+cells-replace` has Risk = write, a large scope or an incorrect regex may batch-modify a large number of non-target cells. **Recommended workflow**: first use `+cells-search` to check the match count, then use `+cells-replace --dry-run` to preview, and finally actually execute.

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute constraints

- `Validate`: XOR common four-piece set; `--find` is non-empty; in regex mode, `--find` must be a valid regex.
- `DryRun`: `+cells-search` outputs the request template; `+cells-replace` additionally returns the estimated replacement count (`would_replace_count`).
- `Execute`: After replacement, you must use `+cells-search` to recheck the remaining hits of the old value, and read back representative cells at the beginning, middle, and end; the goal is for old-value hits to be zero or for unreplaced items to be explicitly listed.
