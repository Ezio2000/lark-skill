<a id="邮件-html-写法指南"></a>
# Email HTML Writing Guide


**CRITICAL Email is an important channel for external communication; please ensure your writing is concise and to the point**
**CRITICAL Email HTML is not web development HTML; you must follow the common email formatting conventions mentioned in this document**
**CRITICAL You must use shortcuts to edit email content (`+send` / `+draft-create` / `+reply` / `+reply-all` / `+forward`) or the body op of `+draft-edit`; it is strictly forbidden to assemble EML yourself**

You can refer to the **official template library** [`../assets/templates/`](../assets/templates) — it provides templates for some scenarios for reference

> Please note that the shortcuts related to email content editing have a built-in HTML lint tool; for security and format adaptation reasons, the HTML you input may be automatically adjusted

<a id="风格底线"></a>
## Style Baseline

- **Email subject under 50 characters**: The email subject line `--subject` should be kept within 50 characters to avoid comprehension difficulties caused by overly long subjects
- **Use lists and tables more**: Do not stack overly long text paragraphs; be good at using lists `<ul>` / `<ol>` or paragraphs `<p>`
- **List writing rules**: **Do not** use list styles like `<p>一、...</p><p>二、...</p>` that combine "Chinese numbering + paragraphs"; also abandon mechanical styles like "①②③" and "1) 2) 3)"; be good at using list formats `<ul>` / `<ol>`.
- **Body length adapts to content**: There is no limit on body length, but **key information must be visible on the first screen**.

<a id="格式书写规范"></a>
## Formatting Conventions

Email HTML is constrained by client compatibility and security sandboxes; it is not the same specification system as web browser HTML. Below are the purest and most aesthetically pleasing formats verified by Feishu Mail; please copy and use them directly.

<a id="段落"></a>
### Paragraph

```html
<p>文字</p>
```

<a id="标题"></a>
### Heading

```html
<h1>一级标题（26px，自动加粗）</h1>
<h2>二级标题（22px）</h2>
<h3>三级标题（20px）</h3>
<h4>四级标题（18px）</h4>
```

<a id="加粗"></a>
### Bold

```html
<b>加粗文字</b>
```

<a id="斜体"></a>
### Italic

```html
<i>斜体文字</i>
```

<a id="下划线"></a>
### Underline

```html
<u>下划线文字</u>
```

<a id="删除线"></a>
### Strikethrough

```html
<s>删除文字</s>
```

<a id="字号"></a>
### Font Size

```html
<span style="font-size:18px">放大到 18px</span>
```

<a id="字体"></a>
### Font

```html
<span style="font-family:'Courier New',monospace">等宽字体</span>
```

<a id="文字颜色"></a>
### Text Color

```html
<span style="color:rgb(245,74,69)">红色文字</span>
```

<a id="换行"></a>
### Line Break

```html
第一行<br>第二行
```

<a id="分隔"></a>
### Divider

```html
<hr>
```

<a id="列表"></a>
### List

```html
<!-- Unordered list -->
<ul><li>项</li></ul>

<!-- Ordered list -->
<ol><li>条</li></ol>

<!-- General rules for multi-level lists (applicable to the two examples below):
     - The direct child node of <ul>/<ol> must be <li>; the HTML specification does not allow <ul> to directly contain <ul>
     - Sublists must be nested inside the parent <li>; do not split them into multiple independent sibling ol/ul
     - Use different symbols for each level's list-style-type to distinguish hierarchy (disc/circle/square or decimal/lower-alpha/lower-roman)
     - Use margin-left:24px for visual indentation of sublevels -->

<!-- Multi-level ordered list (all ol, three-level nesting: decimal → lower-alpha → lower-roman) -->
<ol data-list-number="true" style="margin:0px;padding-left:0px;list-style-position:inside">
   <li class="temp-li number1" data-li-line="true" data-list="number1" data-ol-id="demo-ol" style="line-height:1.6;margin:4px 0;padding-left:0px;display:list-item;list-style-type:decimal;font-family:inherit;font-size:14px;list-style-position:inside" dir="auto">
      <b><span style="font-family:inherit"><span style="color:rgb(31,35,41)">第一级（decimal）</span></span></b>
      <ol data-list-number="true" style="margin:0px 0px 0px 24px;padding-left:0px;list-style-position:inside">
         <li class="temp-li number2" data-li-line="true" data-list="number2" data-ol-id="demo-ol" style="line-height:1.6;margin:4px 0;padding-left:0px;display:list-item;list-style-type:lower-alpha;font-family:inherit;font-size:14px;list-style-position:inside" dir="auto">
            <span style="font-family:inherit"><span style="color:rgb(31,35,41)">第二级（lower-alpha，缩进 24px）</span></span>
            <ol data-list-number="true" style="margin:0px 0px 0px 24px;padding-left:0px;list-style-position:inside">
               <li class="temp-li number3" data-li-line="true" data-list="number3" data-ol-id="demo-ol" style="line-height:1.6;margin:4px 0;padding-left:0px;display:list-item;list-style-type:lower-roman;font-family:inherit;font-size:14px;list-style-position:inside" dir="auto">
                  <span style="font-family:inherit"><span style="color:rgb(31,35,41)">第三级（lower-roman，再缩进 24px）</span></span>
               </li>
            </ol>
         </li>
         <li class="temp-li number2" data-li-line="true" data-list="number2" data-ol-id="demo-ol" style="line-height:1.6;margin:4px 0;padding-left:0px;display:list-item;list-style-type:lower-alpha;font-family:inherit;font-size:14px;list-style-position:inside" dir="auto">
            <span style="font-family:inherit"><span style="color:rgb(31,35,41)">第二级（同层）</span></span>
         </li>
      </ol>
   </li>
   <li class="temp-li number1" data-li-line="true" data-list="number1" data-ol-id="demo-ol" style="line-height:1.6;margin:4px 0;padding-left:0px;display:list-item;list-style-type:decimal;font-family:inherit;font-size:14px;list-style-position:inside" dir="auto">
      <b><span style="font-family:inherit"><span style="color:rgb(31,35,41)">第一级（接续编号）</span></span></b>
   </li>
</ol>

<!-- Multi-level unordered list (all ul, three-level nesting: disc → circle → square) -->
<ul data-list-bullet="true" style="margin:0px;padding-left:0px;list-style-position:inside">
   <li class="temp-li bullet1" data-li-line="true" data-list="bullet1" style="line-height:1.6;margin:4px 0;padding-left:0px;display:list-item;list-style-type:disc;font-family:inherit;font-size:14px;list-style-position:inside" dir="auto">
      <span style="font-family:inherit"><span style="color:rgb(31,35,41)">第一级（disc）</span></span>
      <ul data-list-bullet="true" style="margin:0px 0px 0px 24px;padding-left:0px;list-style-position:inside">
         <li class="temp-li bullet2" data-li-line="true" data-list="bullet2" style="line-height:1.6;margin:4px 0;padding-left:0px;display:list-item;list-style-type:circle;font-family:inherit;font-size:14px;list-style-position:inside" dir="auto">
            <span style="font-family:inherit"><span style="color:rgb(31,35,41)">第二级（circle，缩进 24px）</span></span>
            <ul data-list-bullet="true" style="margin:0px 0px 0px 24px;padding-left:0px;list-style-position:inside">
               <li class="temp-li bullet3" data-li-line="true" data-list="bullet3" style="line-height:1.6;margin:4px 0;padding-left:0px;display:list-item;list-style-type:square;font-family:inherit;font-size:14px;list-style-position:inside" dir="auto">
                  <span style="font-family:inherit"><span style="color:rgb(31,35,41)">第三级（square，再缩进 24px）</span></span>
               </li>
            </ul>
         </li>
         <li class="temp-li bullet2" data-li-line="true" data-list="bullet2" style="line-height:1.6;margin:4px 0;padding-left:0px;display:list-item;list-style-type:circle;font-family:inherit;font-size:14px;list-style-position:inside" dir="auto">
            <span style="font-family:inherit"><span style="color:rgb(31,35,41)">第二级（同层）</span></span>
         </li>
      </ul>
   </li>
   <li class="temp-li bullet1" data-li-line="true" data-list="bullet1" style="line-height:1.6;margin:4px 0;padding-left:0px;display:list-item;list-style-type:disc;font-family:inherit;font-size:14px;list-style-position:inside" dir="auto">
      <span style="font-family:inherit"><span style="color:rgb(31,35,41)">第一级（同层）</span></span>
   </li>
</ul>
```

<a id="表格"></a>
### Table

```html
  <table style="border-collapse:collapse">
    <thead>
      <tr style="background-color:rgb(242,243,245)">
        <th rowspan="2" style="border:1px solid rgb(222,224,227);padding:8px;vertical-align:middle">A</th>
        <th colspan="2" style="border:1px solid rgb(222,224,227);padding:8px;text-align:center">B</th>
        <th rowspan="2" style="border:1px solid rgb(222,224,227);padding:8px;vertical-align:middle">C</th>
      </tr>
      <tr style="background-color:rgb(242,243,245)">
        <th style="border:1px solid rgb(222,224,227);padding:8px">B1</th>
        <th style="border:1px solid rgb(222,224,227);padding:8px">B2</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="border:1px solid rgb(222,224,227);padding:8px">a1</td>
        <td style="border:1px solid rgb(222,224,227);padding:8px">b1-1</td>
        <td style="border:1px solid rgb(222,224,227);padding:8px">b2-1</td>
        <td style="border:1px solid rgb(222,224,227);padding:8px">c1</td>
      </tr>
      <tr>
        <td style="border:1px solid rgb(222,224,227);padding:8px">a2</td>
        <td style="border:1px solid rgb(222,224,227);padding:8px">b1-2</td>
        <td style="border:1px solid rgb(222,224,227);padding:8px">b2-2</td>
        <td style="border:1px solid rgb(222,224,227);padding:8px">c2</td>
      </tr>
    </tbody>
  </table>
```

<a id="链接"></a>
### Link

```html
<a href="https://www.larkoffice.com" style="color:rgb(20,86,240);text-decoration:none">链接文字</a>
```

<a id="at-用户"></a>
### AT User

```html
<a id="at-user-1" href="mailto:user@example.com" style="cursor:pointer;color:rgb(20,86,240);padding:2px;text-decoration:none;border-radius:999em;margin:0px 2px">@姓名</a>
```

**Required fields** `id="at-user-N"`, `mailto:`, and the name text

<a id="引用"></a>
### Quote

```html
<blockquote style="padding-left:12px;color:rgb(100,106,115);border-left:2px solid rgb(187,191,196);margin:0px">引用文字</blockquote>
```

<a id="文字高亮荧光笔风格"></a>
### Text Highlight (highlighter style)

```html
<span style="background-color:rgb(255,200,220);color:rgb(31,35,41)">关键里程碑</span>
<span style="background-color:rgb(255,225,140);color:rgb(31,35,41)">待跟进</span>
<span style="background-color:rgb(190,230,200);color:rgb(31,35,41)">已完成</span>
```

<a id="文字强调"></a>
### Text Emphasis

```html
<b><span style="font-family:inherit"><span style="color:rgb(245,74,69)">红色加粗</span></span></b>
<i><span style="font-family:inherit"><span style="color:rgb(0,0,0)">斜体</span></span></i>
<u><span style="font-family:inherit"><span style="color:rgb(0,0,0)">下划线</span></span></u>
<s><span style="font-family:inherit"><span style="color:rgb(0,0,0)">删除线</span></span></s>
```

<a id="居中--左对齐--右对齐"></a>
### Center / Left Align / Right Align

```html
<div style="text-align:center">居中</div>
<div style="text-align:left">左对齐（默认）</div>
<div style="text-align:right">右对齐</div>
```

<a id="盒模型"></a>
### Box Model

```html
<div style="margin:8px;padding:12px;width:300px">外边距 8px / 内边距 12px / 宽度 300px</div>
```

<a id="边框"></a>
### Border

```html
<div style="border:1px solid rgb(222,224,227);border-radius:8px;padding:8px">圆角描边</div>
```

<a id="透明"></a>
### Transparency

```html
<span style="opacity:0.5">半透明文字</span>
```

<a id="颜色推荐调色盘"></a>
### Colors (recommended palette)

```html
<!-- Primary black (body text) -->
<span style="color:rgb(31,35,41)">主文本</span>
<!-- Secondary gray (secondary notes / time / remarks) -->
<span style="color:rgb(100,106,115)">副文本</span>
<!-- Light gray (tertiary text / placeholder) -->
<span style="color:rgb(143,149,158)">浅灰文本</span>
<!-- LarkSuite blue (links / mention) -->
<span style="color:rgb(20,86,240)">蓝色文字</span>
<!-- LarkSuite dark blue (key headings) -->
<span style="color:rgb(36,91,219)">深蓝标题</span>
<!-- Warning red (errors / failures / red bold) -->
<span style="color:rgb(245,74,69)">警示红</span>
<!-- Urgent orange (urgent / blocked / period-over-period increase) -->
<span style="color:rgb(255,140,40)">紧急橙</span>
```

### URL scheme

```html
<a href="https://example.com">外链</a>
<a href="mailto:user@example.com">邮件链接</a>
<img src="cid:abc"> <!-- Inline image, used with the --inline parameter -->
<img src="data:image/png;base64,iVBOR..."> <!-- base64 inline image -->
```

<a id="官方-html-模板"></a>
## Official HTML Templates

The repository [`../assets/templates/`](../assets/templates/) contains several pre-made scenario templates, written in the native LarkSuite mail-editor format. **Note: The templates are static HTML and have no variable substitution capability; the AI needs to manually replace the sample text in the templates with the real content of this email.**

| File                              | Description       |
|---------------------------------|----------|
| `newsletter--weekly-brief.html` | News weekly report     |
| `weekly--personal-report.html`  | Work weekly report (personal) |
| `weekly--team-report.html`      | Work weekly report (team) |
| `research--market-report.html`  | Research report     |
| `job-application--resume.html`  | Resume email     |

Unlike Feishu OAPI personal email templates (`mail.user_mailbox.templates`) — OAPI templates are "My Templates" in the user's mailbox and are visible across clients; here they are static HTML files in the repository, and the AI can apply them in a single pass.

<a id="ai-套用流程"></a>
### AI Application Process

1. **Determine whether a template can be used** — Check whether the type of email the user currently wants to write (weekly report / research / resume / news / ...) matches a file in [`../assets/templates/`](../assets/templates/); if it does not match, skip the template and write from scratch according to the writing conventions.
2. **Read the entire HTML** — Use the Read tool to fully read the selected template file and understand the skeleton (section headings / list hierarchy / placeholder text / mention chip / paragraph order).
3. **Replace text content** — Replace the sample text in the template with the real content of the user's current email; keep all structural attributes such as inline style / class / data-* unchanged; list items / table rows can be added or removed as needed; entire sections that are not needed (such as "Risks" or "Next Week's Plan") can simply be deleted entirely; do not leave an empty skeleton.
4. **Call the compose shortcut to generate a draft** — Pass the replaced HTML to the compose pipeline through the `--body` parameter (recommended: use `+draft-create` to save a draft first, and after the user reviews it, use `+send`):

   ```bash
   lark-cli mail +draft-create --as user \
     --to alice@example.com --subject 'Q3 团队周报' \
     --body "$(cat ./mail-draft.html)"
   ```

   `mail-draft.html` is the copy in the temporary working directory for this task after replacing the sample content; the template is read from this module's `assets/templates/`. Do not directly send the sample information from the original template.

5. **Get the draft link for user review** — The compose shortcut returns the `reference` field (draft open link); give it to the user to open and verify in the Feishu Mail UI, then decide the next step of sending / editing.

<a id="写信-shortcut-的-lint-返回值"></a>
## Lint Return Values of the Compose Shortcuts

The compose pipeline (`+send` / `+draft-create` / `+reply` / `+reply-all` / `+forward` / `+draft-edit` body op) forcibly lints and sanitizes HTML before calling `emlbuilder`, but **by default the envelope does not carry any lint fields** (neither `*_count` nor a findings array), keeping the envelope small for AI consumption. The default envelope field set for each compose shortcut:

| Field | Condition for appearance | Description |
|------|---------|------|
| `compose_hint` | Attached by default to all 6 shortcuts | Fixed English text, prompting the AI / user to read this document before assembling HTML |
| `draft_edit_hint` | Attached by default **only** to `+draft-create` (the other 5 shortcuts do not attach it) | Fixed English text, prompting that after obtaining `draft_id`, revisions should go through `+draft-edit --draft-id <id>` rather than rerunning `+draft-create` and producing duplicate drafts |
| `draft_id` / `message_id` | Written back after a successful OAPI write | `+draft-create` / `+draft-edit` return `draft_id`; `+send` / `+reply` / `+reply-all` / `+forward` return `message_id` |

When you need to see lint details, add `--show-lint-details`:

```bash
lark-cli mail +draft-create --show-lint-details \
  --to alice@example.com --subject 'Hi' --body '<p>正文</p>'
```

After adding `--show-lint-details`, the envelope simultaneously returns two complete Finding arrays, `lint_applied[]` / `original_blocked[]` (each entry contains `rule_id` / `severity` / `tag_or_attr` / `excerpt` / `hint`), and **no longer returns any `*_count` field** — when the caller needs a count, directly use `len(lint_applied)` / `len(original_blocked)`. **Do not add this flag in default scenarios**, as it only increases token consumption.

If you only want to preview how lint would modify the HTML, it is recommended to directly use the [`+lint-html`](./lark-mail-lint-html.md) command — it already returns the complete `warnings[]` / `errors[]` + `cleaned_html`, which is clearer than the compose pipeline's `--show-lint-details`.

<a id="相关文档"></a>
## Related Documents

- [`+lint-html` usage](./lark-mail-lint-html.md)
- Compose shortcuts: [`+send`](./lark-mail-send.md) / [`+draft-create`](./lark-mail-draft-create.md) / [`+reply`](./lark-mail-reply.md) / [`+reply-all`](./lark-mail-reply-all.md) / [`+forward`](./lark-mail-forward.md) / [`+draft-edit`](./lark-mail-draft-edit.md)
