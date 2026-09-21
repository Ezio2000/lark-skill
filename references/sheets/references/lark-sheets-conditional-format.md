# Lark Sheet Conditional Format

<a id="真对象硬约束--触发词清单"></a>
## Real Object Hard Constraints + Trigger Word List

Use `+cond-format-{create|update|delete}` when the request calls for value/rule-based formatting or colors that change with data. Do not substitute static colors written with `+cells-set` for a requested conditional rule. The expressions below are routing cues only when they carry that conditional meaning; unconditional decoration or explicitly coloring a fixed selection can use static cell styles:

- **Color actions**: "mark red / mark yellow / mark green / color / dye / paint / make it red / make it yellow"
- **Visual emphasis**: "highlight / emphasize / mark / annotate / distinguish" — **limited to those with conditional semantics** (which cells get colored is determined by value / rule); purely decorative unconditional coloring (zebra stripes, fixed background color for an entire row) is not in the mandatory scope, and background color can be set directly per visual conventions
- **Conditional triggers**: "mark the duplicates / circle the anomalies / dye the expired ones red / mark yellow those greater than X / mark red those that don't meet the standard"
- **Linkage semantics**: "color changes with the data / linkage / auto-update / when the data changes the color changes too"
- **Numeric visualization**: "data bars / color scales / gradient colors / progress bar style"

Rule-dependent color marking in Lark Sheets needs conditional formatting, not static background color. Static colors written with `+cells-set` do not change with the source data: for example, static fill cannot keep an "expired cells are red" rule accurate as dates change. Fixed decorative colors do not require a conditional rule.

**Judgment criterion**: After delivery, `+cond-format-list` must be able to return that rule; otherwise the conditional format has not taken effect.

**Large rule-based formatting tasks**: For > 1000 rows, prefer native conditional formatting to "local script row-by-row calculation + `+cells-set` writing static background color". Lark renders the rules and keeps colors linked to the source data. Dataset size alone does not turn a static styling request into a conditional rule.

<a id="使用场景"></a>
## Usage Scenarios

Read and write conditional format objects, and read the **computed cell style results** of conditional formats. This reference covers these shortcuts:

| Operation need | Tool to use | Description |
|---------|---------|------|
| View existing conditional format rules | `+cond-format-list` | Get rule type, range, and style configuration; used to confirm the rule object already exists |
| Create/update/delete conditional format rules | `+cond-format-create` / `+cond-format-update` / `+cond-format-delete` | Perform write operations on conditional format rules |
| Verify conditional format computation results | `+cond-format-result-get` | Read the `cell_styles` after a hit, to confirm whether the conditional format actually applies to the sentinel cell |
| Temporarily include conditional formats during regular reads | `+cells-get --include conditional_format` | Merges conditional format styles equivalently to `+cond-format-result-get`, but still belongs to the regular cell read entry point |

Typical workflow: first read existing conditional formats to understand the configuration → perform create/update/delete → **you must first use `+cond-format-list` to verify the rule object, then use `+cond-format-result-get` to spot-check the computation results**.

**Common configuration errors (must pay attention)**:
- **After creation, two-stage verification is required**: After creating a conditional format, first call `+cond-format-list` to verify whether the rule object (rule_type / ranges / style / attrs) exists and is configured correctly; then call `+cond-format-result-get --range "<哨兵范围>"` to read the `cell_styles` after a hit, to verify whether the conditional format actually applies to cells according to the computation results. If either stage does not meet expectations, fix it immediately and retry
- **Verification must cover sentinel cells**: Do not just confirm that the rule object exists; also spot-check 2-3 cells/rows that should hit / should not hit according to the user's rule (including boundary rows, empty values, duplicate values, non-legend states), using `+cond-format-result-get` to read results such as `cell_styles.background_color` / `font_color` / `font_weight`, and confirm that the formula, range, and color semantics can explain these sentinels. If the rule exists but the sentinel styles/hit logic are wrong, continue fixing
- **Range must be precise**: The application range of the conditional format must precisely cover the columns/rows specified by the user, with no omissions
- **Chinese semantics of `style.back_color` vs `style.fore_color`**: In a Chinese-language context, "**mark red / dye / mark**" refers to **cell background color**, so use `back_color`; only "**red text / red font / make the text red**" uses `fore_color`. When there is no explanation by default, choose `back_color`. When the user says "**mark red**", use standard red `back_color: "#FF0000"`; only when they say "**highlight / emphasize**" use a light background (such as `#FFE6E6`) with an optional `fore_color` to deepen the font — making "mark red" into light pink will be considered as not marking the color as required
- **Date/empty value comparisons must guard against blanks**: When the user says "mark expired ones red", in addition to `TODAY()`, the formula must exclude empty cells; otherwise blank cells will also be misjudged as "earlier than today" and the entire sheet will be marked red. Correct formula: `=AND(E1<>"", E1<=TODAY())`; incorrect formula: `=E1<=TODAY()` (empty values will be treated as 0 and judged as expired)
- **Pay attention to reference style in formula conditions**: Cell references in custom formula conditions need to choose relative/absolute references according to the actual scenario (such as `=E1<=TODAY()` rather than `=$E$1<=TODAY()`, which only compares one cell)
- **`duplicateValues` only detects duplicates by a single column**: The user's statement that "multiple fields must be completely identical to count as duplicates" cannot be expressed directly — first create a helper key column (concatenate the columns participating in duplicate detection into one key using a separator), then use `expression` referencing that key column (such as `COUNTIF` key column >1) to apply the rule to the entire row of the data area; only when you want to mark the key column itself should you use `duplicateValues`

⚠️ **When the user explicitly requests the two-step approach of "helper column + conditional format", it is forbidden to bypass it with `expression`**: When the user says any of the following expressions, you must follow the two-step approach (first create the helper column → then do conditional formatting based on the helper column), and are **forbidden** from directly completing it in one step with a single `rule_type: "expression"` formula:

- "**Add a helper column**, then/and then mark..."
- "**First calculate/determine** whether XX **is** YY, **then** mark..."
- "**Create a new column** to hold the result, then use the result to color"
- Explicitly request the use of "helper column", "helper field", "judgment column", "marker column"

**Correct approach (two-step)**:

For Step 1, `+cells-set` and flags such as `--copy-to-range` are based on `references/lark-sheets-write-cells.md`.

```
Step 1: `+cells-set` Write a judgment formula in a new column (forming a "yes/no" or boolean helper column)
  range="H2", cells=[[{formula: "=IF(A2>B2, \"是\", \"否\")"}]], --copy-to-range="H2:H100"

Step 2: Apply conditional formatting based on the helper column value (using cellIs or an expression that references the helper column)
  `+cond-format-{create|update|delete}` create
    rule_type: "expression"
    ranges: ["A2:H100"]  // highlight the entire row
    attrs: [{formula: ["=$H2=\"是\""]}]  // reference the helper column
    style: {back_color: "#FFECEC"}
```

**Incorrect approach (one-step bypassing the helper column)**:

```
`+cond-format-{create|update|delete}` create
  rule_type: "expression"
  ranges: ["2:145"]
  attrs: [{formula: ["=$O2>$H2"]}]   ← Although logically equivalent, the output lacks the helper column → does not satisfy the user's explicitly requested "helper column" requirement
```

Why the one-step approach is forbidden: the user's explicit request for a helper column has a **business intent** — to let people visually see the "yes/no" column in the sheet; the conditional format is only visual assistance. Although the one-step expression achieves the right effect, when the user opens the sheet they cannot see the helper column, which is regarded as "incomplete operation / formula not adopted".

The scenario for using `expression` alone is: when the user has **not** explicitly requested a helper column and only wants to "mark rows meeting the condition red".

⚠️ **Before creating a conditional format, you must read data rows to confirm column correspondence**: Reading only the first header row (`+csv-get range="A1:Z1"`) is not enough — if the header semantics are ambiguous (for example, multiple columns with synonyms like "time" and "date"), the column letters referenced in the formula may be mismatched. You must also read 3-5 rows of **data samples** (such as `range="A2:Z6"`) to confirm: ① the actual values corresponding to the column names; ② whether the field meanings match the user's description; ③ whether the data type is date/number/text. This is especially true for comparison-type conditional formats (such as `=$A2>$B2`); if the column letter is chosen incorrectly, the entire rule is ruined.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+cond-format-list` | read | Object |
| `+cond-format-result-get` | read | Object |
| `+cond-format-create` | write | Object |
| `+cond-format-update` | write | Object |
| `+cond-format-delete` | high-risk-write | Object |

## Flags

### `+cond-format-list`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--rule-id` | string | optional | Filter by rule id |

### `+cond-format-result-get`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--range` | string | required | A1 range, such as `A1:F10` (without sheet prefix; use `--sheet-id` / `--sheet-name` to specify the sheet) |
| `--max-chars` | int | optional | Character limit for a single return, default 500000 (fallback protection against explosion) |

### `+cond-format-create`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--properties` | string + File + Stdin (composite JSON) | required | Rule configuration JSON, including `style` (hit style, required) and `attrs?` (rule parameter list, whose structure varies by `rule_type`) / `has_ref?`. `rule_type` and `ranges` have been extracted as independent flags |
| `--rule-type` | string | required | Conditional format rule type; takes precedence over the same-named field in `--properties` (possible values: `duplicateValues` / `uniqueValues` / `cellIs` / `containsText` / `timePeriod` / `containsBlanks` / `notContainsBlanks` / `dataBar` / `colorScale` / `rank` / `aboveAverage` / `expression` / `iconSet`) |
| `--ranges` | string + File + Stdin (simple JSON) | required | JSON array of A1 ranges to which the conditional format applies (such as `["A1:A100","C2:C50"]`); takes precedence over the same-named field in `--properties` |

### `+cond-format-update`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--rule-id` | string | required | Target rule id |
| `--properties` | string + File + Stdin (composite JSON) | required | Rule configuration JSON, with the same structure as `+cond-format-create`'s `--properties`; update is whole-group overwrite |
| `--rule-type` | string | required | Conditional format rule type; takes precedence over the same-named field in `--properties` (possible values: `duplicateValues` / `uniqueValues` / `cellIs` / `containsText` / `timePeriod` / `containsBlanks` / `notContainsBlanks` / `dataBar` / `colorScale` / `rank` / `aboveAverage` / `expression` / `iconSet`) |
| `--ranges` | string + File + Stdin (simple JSON) | required | JSON array of A1 ranges to which the conditional format applies (such as `["A1:A100","C2:C50"]`); takes precedence over the same-named field in `--properties` |

### `+cond-format-delete`

_Common four-piece set · System: `--yes`, `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--rule-id` | string | required | Target rule id |

## Schemas

> Quick reference for composite JSON flag fields (only top level + one level of nesting). For deeper structures, see `## Examples` below, or use `--print-schema` to read the complete JSON Schema (usage see index.md "Common flag quick reference" and "Agent usage tips").

### `+cond-format-create` `--properties` / `+cond-format-update` `--properties`

_Conditional format attributes for create/update_

**Top-level fields**:
- `rule_type` (enum) — Conditional format rule type [duplicateValues / uniqueValues / cellIs / containsText / timePeriod / containsBlanks / notContainsBlanks / dataBar / colorScale / rank / aboveAverage / expression / iconSet] — ⚠️ Already extracted as an independent flag `--rule-type`, do not fill it in again in this JSON (for same-named fields, the independent flag takes precedence)
- `ranges` (array<string>) — List of A1 ranges to which the conditional format applies — ⚠️ Already extracted as an independent flag `--ranges`, do not fill it in again in this JSON (for same-named fields, the independent flag takes precedence)
- `style` (object) — Cell style applied when the rule is hit { back_color?: string, fore_color?: string, text_decoration?: enum, font?: enum }
- `attrs` (array<oneOf>?) — Rule parameter list
- `has_ref` (boolean?) — optional

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` arranged at the top (XOR).

### `+cond-format-list`

```bash
# List all conditional format rules in the current sheet (get rule_id for update/delete)
lark-cli sheets +cond-format-list --url "..." --sheet-id "$SID"
```

### `+cond-format-create`

`--rule-type` / `--ranges` are independent flags (do not put `--properties` again); structures such as `style` / `attrs` go through `--properties`:

```bash
# Duplicate value highlight
lark-cli sheets +cond-format-create --url "..." --sheet-id "$SID" \
  --rule-type duplicateValues --ranges '["A1:A100"]' \
  --properties '{"style":{"back_color":"#FFD7D7"}}'

# Data bars
lark-cli sheets +cond-format-create --url "..." --sheet-id "$SID" \
  --rule-type dataBar --ranges '["B2:B100"]' \
  --properties @rule.json

# After creation, first confirm the rule object exists
lark-cli sheets +cond-format-list --url "..." --sheet-id "$SID"

# Then spot-check the conditional format computation results: read the hit style of the sentinel cell
lark-cli sheets +cond-format-result-get --url "..." --sheet-id "$SID" \
  --range "B2:B10"
```

### `+cond-format-result-get`

Used to read the **computed style results** of conditional formats, not to read the rule object. After creating / updating a conditional format, you must use it to spot-check sentinel cells.

The CLI trims output for whitelisted fields: at the top level it keeps only warnings, pagination, and the returned cell count; for each range it keeps only the requested/actual range, real row/column coordinates, truncation markers, and the two-dimensional `cells`; for each cell it keeps only `cell_styles`, and does not return other cell data such as `value` / `formula` / `note` / `data_validation` / `border_styles`. `cell_styles` is the final merged style obtained after the underlying layer enables conditional format computation, and does not include `rule_id` or an independent hit marker.

```bash
# Read the conditional format hit styles for B2:B10, returning cell_styles.background_color / font_color, etc.
lark-cli sheets +cond-format-result-get --url "..." --sheet-id "$SID" \
  --range "B2:B10"

# If you only want to temporarily merge conditional formats in a regular read, you can also use +cells-get --include conditional_format
lark-cli sheets +cells-get --url "..." --sheet-id "$SID" \
  --range "B2:B10" --include conditional_format
```

### `+cond-format-update`

Whole-group overwrite: first use `+cond-format-list --rule-id <id>` to get the current complete configuration, then pass the whole group back after modification.

### `+cond-format-delete`

```bash
lark-cli sheets +cond-format-delete --url "..." --sheet-id "$SID" --rule-id "$RULE_ID" --yes
```

> Delete only one `--rule-id` at a time. To delete **multiple** conditional formats, first use `+cond-format-list` to get each `rule-id`, then use `+batch-update` to merge multiple `+cond-format-delete` into a single batch submission (fail-fast; for failure handling see `references/lark-sheets-batch-update.md`), and do not call them one by one.

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute Constraints

- `Validate`: XOR common four-piece set; `--rule-type` / `--ranges` required; `--properties` must be parseable as valid JSON; check required subfields according to `--rule-type` (`cellIs` requires `attrs.operator` + `attrs.value`, `expression` requires `attrs.formula`, `colorScale` requires `min/mid/max` color scheme, etc.); `+cond-format-delete` enforces `--yes` or `--dry-run`.
- `DryRun`: Write operations output the "conditional_format request template about to be POST/PATCH/DELETE".
- `Execute`: No automatic read-back after writing; after create/update you must call `+cond-format-list --rule-id <id>` to compare rules / ranges / styles, and use `+cond-format-result-get --range <2–3 个哨兵格>` to check the actually effective cell styles; after delete, list to confirm the target id does not exist.
