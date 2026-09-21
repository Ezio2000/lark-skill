# mail +lint-html


<a id="作用"></a>
## Purpose

`+lint-html` is a local pre-check tool for email HTML bodies (read-only, no network IO).

- Validates whether HTML meets Feishu Mail's compatibility / security / native-writing requirements;
- Automatically fixes illegal or non-standard writing (autofix is always enabled), outputting `cleaned_html`;
- Does not write any mailbox state, does not call any OAPI.

The compose chain (`+send` / `+draft-create` / `+reply` / `+reply-all` / `+forward` / `+draft-edit` body op) has this same lint **mandatorily built in**, and automatically sanitizes HTML before submission. The default envelope carries no lint fields to keep responses small; adding `--show-lint-details` gives you the full `lint_applied[]` / `original_blocked[]` Finding arrays (no `*_count` field is returned anymore; when the caller needs a count, `len(arr)` suffices, see [Email HTML Writing Guide](./lark-mail-html.md#写信-shortcut-的-lint-返回值)). This command is a preview version of the compose-chain lint, with identical behavior and a lighter invocation, suitable for:

- AI / users to self-check how HTML will be rewritten before creating a draft;
- CI pipelines to validate HTML templates as artifacts.

<a id="命令"></a>
## Command

```bash
# Pass HTML directly
lark-cli mail +lint-html --body '<p>正文</p>'

# Read HTML from a file (the path must be within the cwd subtree)
lark-cli mail +lint-html --body-file ./template.html

# View full lint details
lark-cli mail +lint-html --body-file ./template.html --show-lint-details
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--body <html>` | Choose one | The HTML content to check |
| `--body-file <path>` | Choose one | Read HTML from a file, only supports the cwd subtree (absolute paths / `..` escaping cwd will be rejected) |
| `--show-lint-details` | No | Defaults to `false`. When `true`, the envelope also returns the full `warnings[]` / `errors[]` Finding arrays; by default only `cleaned_html` is returned, to avoid complex templates triggering dozens of decorative warnings that bloat the response by thousands of tokens |
| `--format <fmt>` | No | `json` (default) / `pretty` / `table` / `csv` / `ndjson` |
| `--jq <expr>` | No | Filter the returned JSON with a jq expression |
| `--dry-run` | No | Do not run lint, only return a dry-run description |

<a id="返回值"></a>
## Return Values

**Default envelope** (only `cleaned_html`, token-frugal):

```json
{
  "ok": true,
  "data": {
    "cleaned_html": "<p>...</p>"
  }
}
```

**After adding `--show-lint-details`**:

```json
{
  "ok": true,
  "data": {
    "cleaned_html": "<p>...</p>",
    "warnings": [
      { "rule_id": "...", "severity": "warning", "tag_or_attr": "...", "excerpt": "...", "hint": "..." }
    ],
    "errors": [
      { "rule_id": "...", "severity": "error", "tag_or_attr": "...", "excerpt": "...", "hint": "..." }
    ]
  }
}
```

| Field | Description |
|------|------|
| `cleaned_html` | The fixed HTML (autofix is always enabled); warnings have been automatically rewritten, errors have been removed |
| `warnings[]` | Array of warning-level findings (**returned only when `--show-lint-details`**). Outputs `[]` when there are no violations |
| `errors[]` | Array of error-level findings (**returned only when `--show-lint-details`**). Outputs `[]` when there are no violations |

Each finding contains:

| Field | Description |
|------|------|
| `rule_id` | Rule number (UPPER_SNAKE_CASE) |
| `severity` | `"warning"` or `"error"` |
| `tag_or_attr` | The tag / attribute / `style.<property>` that triggered the rule |
| `excerpt` | HTML snippet (at most 200 bytes, truncated if exceeded) |
| `hint` | Readable fix description |

<a id="调用示例"></a>
## Invocation Examples

Below are typical cases obtained by actually running `lark-cli mail +lint-html --body '<INPUT>' --show-lint-details` (you need to add `--show-lint-details` to see findings; by default only `cleaned_html` is returned), covering error types (forcibly removed) and warning types (automatically fixed).

<a id="error-类强制删除写信链路也会拒"></a>
### Error Types (forcibly removed, the compose chain also rejects them)

<a id="1--整段删除"></a>
#### 1. `<script>` entire block removed

Input:

```html
<script>alert(1)</script>正文
```

Output:

```html
正文
```

Reason: `<script>` has XSS risk, the entire block is discarded.

<a id="2-javascript-url-删除"></a>
#### 2. `javascript:` URL removed

Input:

```html
<a href="javascript:void(0)">click</a>
```

Output:

```html
<a class="not-doclink" style="cursor:pointer;text-decoration:none;color:rgb(20,86,240)">click</a>
```

Reason: the `javascript:` scheme is an XSS entry point, the `href` attribute is stripped.

<a id="3-on-事件-handler-删除"></a>
#### 3. `on*` event handler removed

Input:

```html
<p onclick="alert(1)">hi</p>
```

Output:

```html
<div style="margin-top:4px;margin-bottom:4px;line-height:1.6"><div dir="auto" style="font-size:14px">hi</div></div>
```

Reason: inline event handlers (`onclick` / `onerror`, etc.) are script injection entry points, the attribute is stripped.

<a id="warning-类自动修复视觉无差异"></a>
### Warning Types (automatically fixed, no visual difference)

#### 4. `<font>` → `<span style>`

Input:

```html
<font color="red" size="3">字</font>
```

Output:

```html
<span style="color:red; font-size:16px">字</span>
```

Reason: `<font>` is an obsolete HTML4 tag; Feishu mail-editor uses inline style to express font size / color.

<a id="5--段落容器原生化"></a>
#### 5. `<p>` paragraph container nativized

Input:

```html
<p>正文</p>
```

Output:

```html
<div style="margin-top:4px;margin-bottom:4px;line-height:1.6"><div dir="auto" style="font-size:14px">正文</div></div>
```

Reason: a Feishu mail-editor paragraph is actually a double-layer div (the outer layer sets margin / line-height, the inner layer sets font-size).

<a id="6--列表原生化"></a>
#### 6. `<ul>/<li>` list nativized

Input:

```html
<ul><li>第一项</li></ul>
```

Output:

```html
<ul style="margin-top:0px;margin-bottom:0px;margin-left:0px;padding-left:0px;list-style-position:inside" data-list-bullet="true"><li class="temp-li bullet1" data-li-line="true" data-list="bullet1" style="line-height:1.6;margin-top:0px;margin-bottom:0px;padding-left:0px;display:list-item;list-style-type:disc;font-family:inherit;font-size:14px;margin-left:0px;list-style-position:inside" dir="auto"><span style="font-family:inherit"><span style="color:rgb(0,0,0)">第一项</span></span></li></ul>
```

Reason: Feishu native list-block requires `<ul>` / `<li>` to be completed with class + data marker + double-layer span wrapping, otherwise visible blank lines appear between li elements.

<a id="7--加灰边--灰文字"></a>
#### 7. `<blockquote>` add gray border + gray text

Input:

```html
<blockquote>引用</blockquote>
```

Output:

```html
<blockquote style="padding-left:0px;color:rgb(100,106,115);border-left:2px solid rgb(187,191,196);margin:0px">引用</blockquote>
```

Reason: adds Feishu native quote styling (2px gray border on the left + gray text).

<a id="8--链接补-not-doclink--larksuite-蓝"></a>
#### 8. `<a>` link add not-doclink + LarkSuite blue

Input:

```html
<a href="https://example.com">link</a>
```

Output:

```html
<a href="https://example.com" class="not-doclink" style="cursor:pointer;text-decoration:none;color:rgb(20,86,240)">link</a>
```

Reason: adds the `not-doclink` class (to prevent misidentification as an internal doc share) + LarkSuite brand blue + no underline.

<a id="9-非白名单-css-property-删除"></a>
#### 9. Non-whitelisted CSS property removed

Input:

```html
<p style="position:absolute;color:red">x</p>
```

Output:

```html
<div style="color:red;margin-top:4px;margin-bottom:4px;line-height:1.6"><div dir="auto" style="font-size:14px">x</div></div>
```

Reason: `position` is not in the inline style whitelist and is removed, `color` is retained.

<a id="相关命令"></a>
## Related Commands

- Compose shortcuts (the same lint is already built in): [`+send`](./lark-mail-send.md) / [`+draft-create`](./lark-mail-draft-create.md) / [`+reply`](./lark-mail-reply.md) / [`+reply-all`](./lark-mail-reply-all.md) / [`+forward`](./lark-mail-forward.md) / [`+draft-edit`](./lark-mail-draft-edit.md)
- Knowledge doc: [Email HTML Writing Guide](./lark-mail-html.md)
