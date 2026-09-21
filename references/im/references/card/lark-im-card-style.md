# Card Style Guide

A decision guide for choosing component combinations and visual styles. For field syntax, see `card-2.0-schema.md`.

---

<a id="好看的标准p0p7唯一裁判基准"></a>
## The Standard for Looking Good (P0–P7, the sole judging baseline)

**Read this section first.** The "intent → component" table and "visual specifications" below are all means serving this set of standards; when constructing and self-checking cards, **P0–P7 are authoritative**.

**Objective function**: a good card = lets the recipient grasp "what this is + what matters most + whether action is needed" within **about a 2-second glance**, and the look is **orderly, restrained, and not noisy**. Efficient communication and visual comfort are unified here.

**Effort allocation**: P0 must pass (front gate) → P1–P3 strong constraints (blocking) → P4–P5 basic hygiene → P6–P7 bonus points.

Each item comes with a **structured verification sentence**—cards cannot be rendered as images, so reasoning can only be done on the JSON structure; therefore verification relies on "counting structure" rather than "squinting at it".

| | Criterion | Actionable requirement | Structured verification (self-check sentence) |
|---|---|---|---|
| **P0** | **Meets the requirement** (front gate · blocking) | Precisely carries the information/intent/action the user wants, no missing, no extra, no off-topic; intent type matches component combination | Break the requirement into a list of information points, and find the carrying component for each point in the JSON; for action requirements, find the interactive component for each one. Any missing = fail |
| **P1** | **Hierarchy** (strong constraint · blocking) | header carries "what this is"; within body there is **exactly one** strongest focus (largest font size/heaviest color/large number in metric card), the rest are supporting; titles use `**加粗**`, secondary information uses grey | List the "font size + weight + color" triples of all text, and check whether three tiers of primary > secondary > auxiliary can be ordered; check whether the focus is unique |
| **P2** | **Grouping** (strong constraint · blocking) | Fields on the same topic go into the same container (`column_set`/`interactive_container`/background block), different topics go into separate containers; block boundaries rely on container background color/stroke/spacing, **not on a flat run of `hr`** | Count the number of top-level visual blocks; check whether there is the anti-pattern of "multiple topics crammed into the same undivided markdown / a flat run of hr" |
| **P3** | **Moderate complexity** (strong constraint · blocking · two-sided band) | Lower bound: must not be a plain text running account, at least has blocks + hierarchy + moderate color/icons; upper bound: visual blocks 2–5, primary color families ≤3, components not piled up, focus unique | ①Whether there is >1 visual block and it contains ≥1 non-plain-text structural element (background block/metric card/icon/table); ②block count ≤5, primary color families ≤3. Pass only if both ends are satisfied |
| **P4** | **Contrast** (basic hygiene) | Title and body text differ by at least one tier in font size or weight; emphasis uses color/enlargement; body text does not overuse `#/##/###` (except for enlarged numeric focus, see P1) | Whether title and body text differ by at least one tier in "font size or weight" |
| **P5** | **Alignment** (basic hygiene) | Spacing is preferably delegated to container `vertical_spacing`/`horizontal_spacing`/`padding`, **do not overuse scattered margin settings causing irregular density**; spacing values converge to one set of tiers (2/4/8/12px); top-level container spacing is consistent | Whether there are irregular scattered margins; whether the number of spacing value types is ≤4 |
| **P6** | **Semantic consistency** (bonus) | Red=down/warning/failure, green=up/success/pass, grey=secondary; the starting color of the primary color family is determined by header, taking adjacent colors on the color wheel; same color same meaning | Whether the same color corresponds to the same semantics; whether the header template color and block colors are in the same color family |
| **P7** | **Robust** (bonus) | Parallel/metric columns default to `weighted` or `none`, **use `stretch` with caution** (to prevent mobile stretching); when needed, pair with `config.style.color` light/dark; do not rely on fixed pixel widths for hard layout | Whether there is a stretch risk; whether both light and dark colors are readable |

---

<a id="意图--组件组合"></a>
## Intent → Component Combination

<a id="通知类无交互或只读"></a>
### Notification type (no interaction or read-only)

| User intent | Recommended component combination | header.template |
|---|---|---|
| Plain text notification / system announcement | `column_set` (notification body, with `blue-50` background) + `button(open_url)` | `blue` |
| Event announcement (with key visual image) | `img` (main image) + `markdown` (time/location) + `column_set` (detail pairs) + `button(open_url)` | `turquoise` / `blue` |
| Success / completion status notification | `column_set` (key fields, with `green-50` background) + `markdown` (conclusion in bold) | `green` |
| Approval result feedback (approved / rejected) | `column_set` (application information) + `column_set` (approval conclusion + icon, with `green-50`/`red-50` background) | `green` / `red` |
| Birthday / holiday greeting | `img` (main image) + `column_set` (name/date) + `button(open_url)` | `orange` |
| Product / feature launch promotion | `img` (main image) + `markdown` (highlights) + `column_set` (feature highlight block) + `button(open_url)` | `blue` / `violet` |
| Multi-image display (image gallery, AI-generated images) | `img_combination` or multiple `img` + `markdown` (description) + `button(callback)` | `default` |

<a id="提醒--操作类"></a>
### Reminder + action type

| User intent | Recommended component combination | header.template |
|---|---|---|
| Reminder + one-click action | `column_set` (details, with `yellow-50` background) + `button(callback)` | `yellow` |
| Task list / to-do tracking | `checker` × N (each item with `behaviors: callback`) + `button(callback)` (mark-all-complete action) | `blue` |
| Alert triggered (requires immediate handling) | `column_set` (alert metric, with `red-50` background) + `column_set` (description + input quick note) + `button(callback)` | `red` |
| Alert resolved / status changed | `column_set` (resolution time / owner, with `green-50` background) + `markdown` (conclusion in bold) | `green` |
| Approval pending (with note input) | `column_set` (application information, with `grey-50` background) + `column_set` (input approval comment) + `button(callback)` × 2 (approve / reject) | `default` |
| Calendar / schedule reminder (with participants) | `column_set` (time / location, with `yellow-50` background) + `person_list` (participants) + `button(callback)` | `yellow` |
| Dangerous operation confirmation | `column_set` (description, with `red-50` background) + `button(callback)` + `confirm` dialog configuration | `red` |

<a id="数据--报告类"></a>
### Data / report type

| User intent | Recommended component combination | header.template |
|---|---|---|
| Daily report / work report | `column_set` (metrics, with background color) + `interactive_container` (progress blocks, with stroke) × N; for blocks with overly long content, use `collapsible_panel` to collapse secondary details | `blue` / `default` |
| Data dashboard (with charts) | `column_set` (metrics, with `blue-50` background) + `chart` + `table` (root node, cannot be nested) + `markdown` (description) | `blue` |
| Leaderboard | `column_set` fixed column widths (rank + avatar `img` + name + metric) looping entries | `grey` |
| Order / ticket details | `div.fields` (field pairs) or `column_set` (when a colored background block is needed) + `button(callback)` | `orange` |

<a id="表单--收集类"></a>
### Form / collection type

| User intent | Recommended component combination | header.template |
|---|---|---|
| Plain text form collection | `form` (containing `input` + `button(form_action_type: submit)`) | `blue` |
| Form with dropdown selection (single choice) | `form` (containing `select_static` / `select_person` + `input` + `button`) | `wathet` |
| Form with multiple choice | `form` (containing `multi_select_static` / `multi_select_person` + `input` + `button`) | `wathet` |
| Form with date / time | `form` (containing `date_picker` / `picker_time` / `picker_datetime` + `input` + `button`) | `blue` |
| Device / service feedback | `form` (containing `select_static` (satisfaction) + `input` (notes) + `button`) | `yellow` |
| Multi-step progress / guidance | `column_set` (horizontal steps, with `blue-50` background) + `markdown` (current status) + `button` | `blue` |

<a id="推荐--选择类"></a>
### Recommendation / selection type

| User intent | Recommended component combination | header.template |
|---|---|---|
| Recommendation list (clickable cards with images) | `interactive_container` (containing `img` + `markdown`) × N + `button(open_url)` | `blue` |
| AI guidance options / feature menu | `markdown` (welcome message) + `interactive_container` (containing `markdown` option descriptions) × N | No header |
| Bot feature guidance / tutorial | `column_set` (step descriptions, with background) + `button` × 2 (primary action / secondary action) | `blue` |
| Service desk / multi-action entry | `column_set` (description, with background) + `button` × N (≤3 primary actions, `type` distinguishes primary from secondary); when secondary actions exceed 3, switch to `overflow` (collapsed menu) | No header |

<a id="社交--互动类"></a>
### Social / interaction type

| User intent | Recommended component combination | header.template |
|---|---|---|
| Work circle / social sharing | `img_combination` (multiple images) + `markdown` (body text) + `button(open_url)` × 2 | `blue` |
| Deal / performance announcement | `img` (celebration image) + `markdown` (results) + `column_set` (key numbers) | `green` |

---

<a id="视觉规范实现-p0p7-的具体战术"></a>
## Visual Specifications (concrete tactics for implementing P0–P7)

Component selection only solves "whether it exists"; the items below are the concrete means of implementing P0–P7 above, with the principle they mainly serve noted in parentheses.

> **P3 special case — data dashboard type**: `chart + table + column_set + markdown` is four different components each appearing once, which does not count as "piling up", and the P3 upper bound is satisfied as usual; but it must still be ensured that each type appears only once.

<a id="0-header-图标服务-p3--视觉质感底线"></a>
### 0. Header icon (serves P3 · baseline of visual quality)

**Almost all cards should have a header icon**—this is the lowest-cost step to improve the "refined feel"; its absence makes the header look empty and cheap.

```json
"header": {
  "title": { "tag": "plain_text", "content": "卡片标题" },
  "template": "blue",
  "icon": { "tag": "standard_icon", "token": "calendar_colorful" }
}
```

- `token` must be selected from the exact enumeration of `resource/icons.md`; it is forbidden to concatenate tokens yourself based on naming patterns. When there is no suitable token, omit the icon.
- Scenario quick reference: calendar `calendar_colorful`, to-do `todo_colorful`, voting `vote_colorful`, Minutes `file-lark-minutes_colorful`, Base `wiki-bitable_colorful`, forms `file-form_colorful`, community `larkcommunity_colorful`, recruiting `hirelogo_colorful`, Feishu brand `lark-logo_colorful`, Meego `meego_colorful`, AI `myai_colorful`, aPaaS `apaas_colorful`, approval `approval_colorful`, general AI `ai-common_colorful`.

<a id="1-配色纪律服务-p6-语义一致"></a>
### 1. Color discipline (serves P6 semantic consistency)

- **Adjacent color wheel**: `Red → Carmine → Orange → Yellow → Green → Turquoise → Wathet → Blue → Violet → Purple →（回到）Red`. A card may only use colors that are **adjacent** on the color wheel; jumping is strictly forbidden (❌ blue + green + red).
- **At most 3 primary color families** (excluding grey / white).
- **The starting color is determined by header**:
  - header `blue` → blue / violet / purple
  - header `green` → green / turquoise / wathet
  - header `red` → red / carmine / orange
  - no header → default blue / violet / purple
- **Light/dark semantics** (syntax `blue-50`, `blue-600`, `grey-500`):
  - `-50` block background · `-100` tag background · `-500` body text · `-600`/`-700` emphasized text

<a id="2-间距纪律服务-p5-对齐--视觉决定性因素"></a>
### 2. Spacing discipline (serves P5 alignment · decisive visual factor)

- **Recommended body padding**: `"padding": "12px 12px 20px 12px"` (top right bottom left; 20px bottom whitespace is more comfortable).
- **Prefer not to use `markdown` / `column`'s `margin` to control spacing**: delegate to the parent container's `vertical_spacing` / `horizontal_spacing` / `padding` for unified management, and in most cases explicitly set `0px`; only set a non-zero value when fine indentation is needed (such as hierarchical left indentation).
- Recommended `vertical_spacing` values within a container: `2px` (title ↔ body within a highlight block) / `4px` (body paragraphs, list items) / `8px` (elements that need to be pulled apart).
- **Smart margin between containers**: if a top-level container is **not** the last element of body → set `"margin": "0px 0px 12px 0px"`; if it **is** the last → `"0px"` or leave unset, to avoid extra whitespace at the bottom of the card.

<a id="3-指标卡模式服务-p1-焦点--出现-kpi--数值--统计词时强制使用"></a>
### 3. Metric card pattern (serves P1 focus · mandatory when KPI / numeric / statistical terms appear)

Trigger: content contains numeric information such as `KPI/ROI/CTR/UV/PV/DAU/GMV/转化率/增长率/总数/营收`.

- Multiple metrics placed side by side go into one `column_set`, and `flex_mode` **defaults to `"none"`, use `"stretch"` with caution** (to prevent mobile stretching and deformation, P7); use stretch only when the content of each column is equal width and it is confirmed that there is no deformation on mobile.
- Numeric value: enlarge with `##` (**the only special case where a markdown heading is allowed**), and may be colored with `<font>`.
- Description: `<font color='grey'>` + `text_size: "notation"`.
- Center `text_align: "center"`; column background `background_style: "grey-50"`; `padding: "12px"`; `vertical_spacing: "2px"`.

```json
{
  "tag": "column_set",
  "flex_mode": "none",
  "horizontal_spacing": "12px",
  "columns": [
    { "tag": "column", "width": "weighted", "weight": 1,
      "background_style": "grey-50", "corner_radius": "8px",
      "padding": "12px", "vertical_spacing": "2px",
      "elements": [
        { "tag": "markdown", "content": "## <font color='blue'>5,483</font>", "text_align": "center" },
        { "tag": "markdown", "content": "<font color='grey'>GMV($)</font>", "text_align": "center", "text_size": "notation" }
      ] }
  ]
}
```

<a id="4-描边卡片模式服务-p2-分组--进展--事项--列表项分块展示"></a>
### 4. Stroked card pattern (serves P2 grouping · block display of progress / items / list entries)

Use `interactive_container` to add a stroke + rounded corners to each item block; visually lighter than a colored background, suitable for "multi-entry" scenarios such as progress/ticket/task lists.

```json
{
  "tag": "interactive_container",
  "width": "fill",
  "has_border": true,
  "border_color": "blue-100",
  "corner_radius": "8px",
  "background_style": "blue-50",
  "padding": "12px 12px 12px 12px",
  "vertical_spacing": "4px",
  "margin": "0px 0px 12px 0px",
  "elements": [
    {
      "tag": "markdown",
      "content": "**<font color='blue'>事项标题</font>**"
    },
    {
      "tag": "markdown",
      "content": "事项正文内容……",
      "text_size": "normal"
    }
  ]
}
```

- `border_color` follows the primary color family (blue family uses `blue-100`, green family uses `green-100`).
- When interaction is not needed, `behaviors` may be omitted; when a click callback is needed, add `"behaviors": [{"type":"callback","value":{...}}]`.
- **`form` or `table` cannot be placed inside**.

<a id="5-高亮块模式服务-p2-分组--多分类信息成块展示"></a>
### 5. Highlight block pattern (serves P2 grouping · block display of multi-category information)

Two-layer structure: the outer `column_set` manages layout, the inner `column` manages style (colored background).

- Each `column` sets `background_style` to a light color (such as `blue-50` / `green-50`), `padding: "12px 12px 12px 12px"`, `vertical_spacing: "4px"`, `weight: 1`.
- The first line within the block uses `**<font color='blue'>分类标题</font>**` for color and bold, with the body text immediately following.
- **Layout choice**: categories ≤ 3 and content short → horizontal, preferably `flex_mode: "bisect"` (2 columns) or `"trisect"` (3 columns); use `stretch` only when the character counts of each column are strictly equal width and it is confirmed that there is no deformation on mobile (use with caution, see §9); **categories ≥ 4, odd number, or any block's content > 3 lines → vertical** (each block occupies its own row). Colors are taken in order according to the adjacent color wheel in item 1 above.
- ⚠️ **Version dependency**: `column.background_style` requires client **≥ v7.9**; older versions silently drop the background. When strong robustness is required, switch to `interactive_container`'s `background_style` (no version restriction) instead of the column background color.

<a id="6-header-三件套服务-p1-层级--语境补全"></a>
### 6. Header trio (serves P1 hierarchy · context completion)

header has three layers of capability; **use them as fully as possible** (at least use `title` + `icon`; `subtitle` and `text_tag_list` are chosen according to actual requirements)—this is the lowest-cost step with the clearest context:

- `title`: what this is (required)
- `subtitle`: one sentence of context (who sent it / what time / what status), ≤1 line, `plain_text`
- `text_tag_list`: status tags, ≤3, with color semantics consistent with P6 (`blue`=information, `yellow`=pending, `red`=urgent, `green`=completed)

```json
"header": {
  "title":    { "tag": "plain_text", "content": "发版审批" },
  "subtitle": { "tag": "plain_text", "content": "2026-06-25 · 后端服务" },
  "template": "blue",
  "icon": { "tag": "standard_icon", "token": "approval_colorful" },
  "text_tag_list": [
    { "tag": "text_tag", "text": { "tag": "plain_text", "content": "待审批" }, "color": "yellow" }
  ]
}
```

**Forbidden**: writing emoji in `header.title`; moving subtitle information into the first line of body markdown, leaving the header empty; using decorative emoji in the title or body heading in serious scenarios (approval/alert/finance).

<a id="7-字段对用-divfields不要用-column_set-模拟服务-p5-对齐"></a>
### 7. Use `div.fields` for field pairs, do not simulate with `column_set` (serves P5 alignment)

For detail-type "label: value" (order fields, approval information, schedule details), prefer `div.fields`—native alignment, lighter structure:

```json
{
  "tag": "div",
  "fields": [
    { "is_short": true, "text": { "tag": "lark_md", "content": "**提交人**\n张三" } },
    { "is_short": true, "text": { "tag": "lark_md", "content": "**部门**\n研发中台" } },
    { "is_short": true, "text": { "tag": "lark_md", "content": "**提交时间**\n2026-06-25 10:30" } },
    { "is_short": true, "text": { "tag": "lark_md", "content": "**优先级**\n<font color='red'>P0</font>" } }
  ]
}
```

Fields in `is_short: true` are automatically placed side by side in pairs, and alignment is guaranteed by the component. `column_set` is reserved for scenarios that **require colored background blocks / unequal widths / nested complex structures**; do not use it to simulate simple field pairs.

<a id="8-长文本必须设-lines-截断服务-p3-复杂度上限"></a>
### 8. Long text must set `lines` truncation (serves the P3 complexity upper limit)

Any text field that receives dynamic data must set a maximum number of lines to prevent the card from being stretched out:

| Location | Field | Recommended upper limit |
|---|---|---|
| `div.text` | `lines` | Body text ≤4, secondary explanation ≤2 |
| `person_list` | `lines` | ≤2 |
| `table.header_style` | `lines` | ≤1 |
| `collapsible_panel` | Collapsed by default | For long text, prefer a collapsible panel rather than truncation |

Dynamic text without `lines` set = a hidden risk of hitting the P3 upper limit.

<a id="9-flex_mode-决策表服务-p7-健壮"></a>
### 9. `flex_mode` decision table (serves P7 robustness)

| Scenario | Recommended flex_mode | Reason |
|---|---|---|
| Metric cards side by side (content of unequal length) | `none` + `width: weighted` | Prevents stretching on mobile; each column compresses proportionally |
| 2 columns of equal-width content (similar character counts) | `bisect` | The clearest semantic two-way equal split |
| 3 columns of equal-width content | `trisect` | Three-way equal split, do not write weight |
| Multiple tags / multiple icons in a horizontal row, wrapping allowed | `flow` | Automatically wraps on narrow screens without squeezing |
| Explicit requirement for justified full-width alignment and equal-width content | `stretch` | Use with caution: on narrow mobile screens, overly long content will stretch and deform |

> `stretch` is used only when the character counts and heights of each column are similar and it has been confirmed that there is no deformation on mobile; in all other scenarios, default to `none`.

<a id="10-chart-配色纳入-p6-纪律"></a>
### 10. `chart` color scheme included in P6 discipline

`chart.color_theme` must remain consistent with the overall card color system:

- **Default**: `brand` (single-color system, following the Feishu brand color) or `primary` (primary-color single-color system), safe options.
- **Prohibited**: `rainbow`—it will push all the jumping colors on the color wheel into the chart, directly breaking through P6's "primary color system ≤3 + adjacent color wheel" constraint.
- **Exception**: when there are ≥4 data dimensions/series and the series have no primary-secondary relationship (such as a regional comparison chart), you may use `complementary` or define a custom color array adjacent to the primary color system in `chart_spec`.

<a id="11-laser-样式的克制规则服务-p6-语义一致"></a>
### 11. Restraint rules for `laser` styles (serves P6 semantic consistency)

`button.type: "laser"` and `background_style: "laser"` are high-saturation gradient effects:

- **Allowed**: AI-generated, holiday celebration, and marketing promotion types, **≤1 place** per card, and the position must be the primary action button or visual focal block.
- **Prohibited**: serious scenarios such as approvals, alerts, finance, tickets, and schedules—laser appears frivolous and cheap in these scenarios.
- **Do not use by default**; if it is to be used in the Step 1 design plan, you must explicitly state "the ×× scenario is suitable for the laser style" and obtain confirmation.
