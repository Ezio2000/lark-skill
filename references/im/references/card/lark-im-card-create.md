<a id="发送-interactive-卡片工作流"></a>
# Send Interactive Card Workflow

When the user needs to send a Feishu interactive card, follow this workflow. Every time, the steps must be executed strictly in order.

---

<a id="入口分支文字--图片--图片文字组合"></a>
## Entry Branch: Text / Image / Image + Text Combination

Determine the user input type:

- **Pure text request** (no image) → skip to Step 1 "Text Request Path".
- **Pure image** (screenshot / design mockup, with no additional text description content) → follow the "image as input" path; the image is both the content source and the style source.
- **Image + text combination** → follow the "image as input" path, but **the image serves only as a style/layout reference, and the content source is the text** (see point 5).

<a id="以图片为输入时的处理"></a>
### Handling When the Input Is an Image

1. **Analyze the image**: extract visual style information from the image—
   - Color scheme (color wheel positioning), spacing rhythm, hierarchy relationships, grouping method, component types
   - Image type (see point 2)

2. **Determine the image type** to decide the fidelity strategy:

   | Image Type | Basis for Determination | Construction Strategy |
   |---|---|---|
   | **Feishu card screenshot** | Feishu card structural features such as header / body / components can be identified | **High-fidelity reproduction**: map each visual structure in the screenshot to a similar Card 2.0 component; after reproduction, it must still pass the P0–P7 hard Gate |
   | **Other design mockups / posters / web UI** | No Feishu card structural features | **Style extraction + reconstruction by principles**: extract style tokens such as colors, spacing, and hierarchy relationships; reconstruct the layout according to P0–P7 principles (**not pixel-level imitation**), and explain deviations in the output |

3. **Determine the content source**:
   - **Pure image**: extract content/information points (text, fields, actions) from the image as the request (feed to P0)
   - **Image + text combination**: **use the text/document as the content source**; the image provides only style and layout references. Organize the text content into the card according to the image style

4. **Conflict handling**: when the image style conflicts with P0–P7 or card component capabilities—
   - Feishu card screenshot: **preserve fidelity as much as possible** within the component capability range; make minor adjustments at conflicts and inform the user of the reason for the deviation
   - Other design mockups / posters / UI: **P0–P7 take precedence**; the image serves only as a style reference, and conflicts should not be forcibly copied

5. After the analysis is clear, briefly explain to the user your **type determination conclusion + fidelity strategy + content source plan**. Then proceed to Step 2 to load component documentation and begin construction.

---

<a id="step-1文字诉求路径分析意图输出设计方案"></a>
## Step 1 (Text Request Path): Analyze Intent, Output Design Plan

**Goal**: Before writing JSON, clarify all decisions and inform the user. The amount of documentation loaded in Step 2 depends on the component list here, so try to think it through at this step.

Analyze the following content and briefly explain it to the user:

1. **Version**: Card 2.0 supports richer components, and **Card 2.0 is recommended**; use 1.0 only when the user explicitly requests 1.0.
2. **Component combination**: In the `lark-im-card-style.md` "intent → component combination" table, match the closest intent row, and refer to the recommended component combination and that row's `header.template` color (some rows are "no header"). The recommended combination is for reference only; **the final selection is based on what fits the user's intent**; when using Card 2.0, you may also refer to the component overview in `card-2.0-schema.md` to supplement or adjust the component selection.
3. **Interaction type** (if any): whether it contains interactive components that will call back to the server, and whether there are pure redirects (open_url). Callbacks fall into two categories: ① `select` / `multi_select` / `input` / `picker` / `overflow` actions call back by default; ② `button` / `checker` / `interactive_container` require explicit configuration of `behaviors`; `form` submission calls back uniformly. See Step 5 for details.
4. **Width mode**: `compact`(400px) is suitable for notifications/blessings/light reminders (concise content, single focus); `default`(≤600px) is suitable for most scenarios; `fill`(fill) is suitable for data dashboards and wide tables containing `table`. Default is `default`; deviate only with a clear reason.

> Output example: "Card 2.0, header green, `default`, components: `column_set` / `column` / `markdown`, no interaction."

---

<a id="step-2按需加载组件文档"></a>
## Step 2: Load Component Documentation on Demand

> ⚠️ **Only applicable to Card 2.0**: The details of `card-2.0-schema.md` and `components/` are all 2.0 structures. If Step 1 determines **Card 1.0** (including the downgrade scenario in Step 4), these **cannot be referenced**; skip this step and construct directly according to the 1.0 structure.

**Goal**: Read component details + "standards for good-looking" without loading everything.

> Source of the component list: **text path** = the design plan from Step 1; **image path** = the component list determined during the image analysis stage of the entry branch.

1. Read `card-2.0-schema.md` — it serves two purposes at once: ① understand the component overview to assist component selection; ② find the routing links to each component's detail documentation. **Read only once; do not load repeatedly.**
2. Read `components/<tag>.md` one by one according to the routes (such as `components/column_set.md`, `components/button.md`)
3. Read the "**Standards for Good-Looking (P0–P7)**" and "Visual Specifications" at the beginning of `lark-im-card-style.md` — these are the judging criteria for construction and self-check in Step 3, and **must be internalized before construction**.

---

<a id="step-3构造卡片-json"></a>
## Step 3: Construct the Card JSON

Construct the card according to the root structure skeleton of the corresponding version in Step 2, and follow the design plan from Step 1 (or the image analysis stage) for component selection.

- Card 2.0 must have `"schema": "2.0"`, otherwise the card will not render
- Buttons inside the `form` container use `form_action_type: "submit"`; do not write `behaviors`
- The child nodes of `column_set` can only be `column`; other components cannot be placed directly
- `table` **can only be placed at the body root node** and cannot be nested into containers such as `column_set` / `interactive_container`
- `collapsible_panel` **cannot contain `form`**; `interactive_container` **cannot contain `form`/`table`**

<a id="发送前硬-gate按-p0p7-自检不过不许进-step-4"></a>
### Pre-Send Hard Gate (Self-Check According to P0–P7; Do Not Proceed to Step 4 If Not Passed)

After construction is complete, perform a **structured self-check** item by item using the "Standards for Good-Looking" in `lark-im-card-style.md`. **P0 + P1–P3 are blocking items; if any one fails, you must return to this step to fix it and re-evaluate**, and must not send a defective card.

**Blocking items (all must pass):**
- [ ] **P0 Meets the request**: Break the user's request into a list of information points, and find the component carrying each point in the JSON; all required actions (buttons/forms/redirects) are present; there is no filler unrelated to the request
- [ ] **P1 Hierarchy**: There is exactly **one** strongest focus in the body; titles use `**加粗**` to create separation from the body text, and secondary information uses grey
- [ ] **P2 Grouping**: Fields on the same topic are collected into the same container, and different topics are placed in separate containers; **there is no "flat tiling with hr all the way" or multiple topics crammed into the same markdown**
- [ ] **P3 Moderate complexity**: **2–5** visual blocks, primary color family ≤3; and >1 block, containing at least one non-plain-text structural element (background block/metric card/icon/table) — **it must be neither a plain-text running account nor an overloaded pile-up**

**Basic hygiene (should be satisfied):**
- [ ] **P4 Contrast**: Titles and body text differ by at least one level in font size or weight; body text does not abuse `#/##/###` (except for enlarged metric card values)
- [ ] **P5 Alignment**: Do not abuse scattered `margin` settings; prefer delegating spacing to containers; spacing value types ≤4; non-final top-level containers have consistent spacing

**Bonus items (satisfy as much as possible):**
- [ ] **P6 Semantic consistency**: Same color, same meaning (red=decline/alert, green=rise/success, grey=secondary); the starting color of the primary color family is consistent with the header and uses adjacent color wheel positions
- [ ] **P7 Robustness**: Parallel/metric columns default to `weighted`/`none`, use `stretch` with caution; configure `config.style.color` light/dark when necessary

---

<a id="step-4发送卡片"></a>
## Step 4: Send the Card

```bash
# Send to group chat
lark-cli im +messages-send --chat-id oc_xxx --msg-type interactive --content '<card_json>'

# Send to a specified user (direct message)
lark-cli im +messages-send --user-id ou_xxx --msg-type interactive --content '<card_json>'
```

**When sending fails**: First troubleshoot against the common failure list below. If a match is found, fix it according to the corresponding handling method and resend; otherwise, fix the JSON according to the error message and resend. Try at most **3 times**. If it still fails after 3 times, **downgrade to a Card 1.0 card**, reconstruct it, and send it. **Do not refer to the memory of previously sending 2.0**; completely reconstruct the 1.0 card based on the user's intent. There is no local reference documentation for 1.0 (components/ and resource/ are both 2.0).
**Common failure list**

| # | Error message | Handling method |
|---|---|---|
| 1 | `there is an invalid user resource (at/person) in your card` | The card contains an at/person component, but an invalid user ID was used. Ask the user for their real open_id / user_id, replace it, and resend. |

---

<a id="step-5交互回调可选"></a>
## Step 5: Interaction Callback (Optional)

If the card contains **interactive components that will call back to the server**, then listening for `card.action.trigger` callbacks is **supported** (whether to listen is determined by actual requirements and is not mandatory):

**Explicit configuration of `behaviors: [{type:"callback"}]` is required for callbacks:**
- `button` (with callback behavior)
- `checker` — when behaviors are not configured, only local checking takes effect and no server callback is triggered
- `interactive_container` — behaviors are required and support callback / open_url

**Selection / input calls back by default, with no need for explicit `behaviors`:**
- `select_static` / `multi_select_static` / `select_person` / `multi_select_person`
- `overflow` / `input` / `date_picker` / `picker_time` / `picker_datetime`

**form submission calls back uniformly (buttons use `form_action_type: "submit"`, no behaviors required):**
- The values of all form components in the form are returned all at once through `action.form_value`

> Pure `open_url` redirect buttons redirect locally on the client and do not call back to the server.

If you need to handle callbacks (listen for events, read fields, update the card), see `../lark-im-card-action-reply.md`.

---

<a id="step-6用户反馈修正按需进入"></a>
## Step 6: User Feedback Correction (Enter as Needed)

When the user provides modification suggestions after seeing the sent card, follow the process below. **Do not redo the entire card; make surgical modifications.**

<a id="1-定位改动范围"></a>
### 1. Locate the Scope of Change

Map the user's feedback item by item to specific components and fields:

| User feedback type | Mapping target |
|---|---|
| Dissatisfied with copy/wording | Corresponding `markdown.content` / `button.text` / `header.title` |
| Dissatisfied with color/style | Corresponding `background_style` / `font_color` / `header.template` / config color token |
| Dissatisfied with layout/arrangement | Corresponding `column_set.flex_mode` / `width` / `weight` / `padding` |
| Missing a field/information | Add a `div.fields` entry or `markdown` row |
| A block is too crowded/too empty | Adjust `padding` / `vertical_spacing` / `margin` |
| Interaction behavior issue | Corresponding `behaviors` / `confirm` / `disabled` |

<a id="2-最小改动原则"></a>
### 2. Minimal Change Principle

- Only change the components pointed out; do not touch the surrounding structure.
- After the change, **re-run the self-check only for the P items involved in the modified components** (change color → pass P6; change grouping → pass P1+P2; change spacing → pass P5).

<a id="3-重发"></a>
### 3. Resend

After the correction is complete, resend a new card (same as Step 4), and tell the user "the corrected version has been resent."

<a id="4-执行前告知"></a>
### 4. Inform Before Execution

Restate to the user "I will modify ×××", and execute only after confirmation; do not make silent changes.

---

<a id="执行清单"></a>
## Execution Checklist

- [ ] Entry: Determine whether it is a text request (→ Step 1) or image input (→ image branch → determine type → fidelity strategy → component mapping)
- [ ] Step 1: Analyze intent, output design plan (version / width mode / color / components)
- [ ] Step 2: Read schema.md + component details + "Standards for Good-Looking P0–P7"
- [ ] Step 3: Construct JSON → pass P0–P7 hard Gate (P0+P1–P3 blocking); if not passed, fix first
- [ ] Step 4: Send; on failure, troubleshoot and retry according to the common failure table (≤3 times); if it still fails, downgrade to Card 1.0, reconstruct, and send
- [ ] Step 5: If there is interaction, refer to ../lark-im-card-action-reply.md
- [ ] Step 6: When the user provides modification suggestions, locate the component → minimal change → update in place or resend
