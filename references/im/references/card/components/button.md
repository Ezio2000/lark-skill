<a id="按钮-button"></a>
# Button `button`

Interactive button, supporting three types of behavior: jump / callback / form submission. **Card 2.0**.

<a id="最小示例"></a>
## Minimal Example

```json
{
  "tag": "button",
  "text": { "tag": "plain_text", "content": "确定" },
  "type": "primary",
  "behaviors": [{ "type": "callback", "value": { "action": "ok" } }]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `button` |
| `text` | No | Object | / | `{tag:"plain_text", content}`, ≤100 characters |
| `type` | No | String | default | See the type enum below |
| `size` | No | String | medium | `tiny` / `small` / `medium` / `large` |
| `width` | No | String | default | `default` / `fill` / `[100,∞)px` |
| `behaviors` | Yes* | Array | / | Interactive behavior, see below; buttons inside a form do not use behaviors but instead use `form_action_type` |
| `icon` | No | Object | / | Prefix icon (same as `div.icon`) |
| `hover_tips` | No | Object | / | PC hover tooltip, plain_text |
| `disabled` | No | Boolean | false | Whether disabled |
| `disabled_tips` | No | Object | / | Hover tooltip when disabled, plain_text |
| `confirm` | No | Object | / | Secondary confirmation dialog `{title, text}` (all plain_text, title required) |
| `margin` | No | String | 0 | Outer margin [-99,99]px |
| `element_id` | No | String | / | Unique identifier, starts with a letter, ≤20 characters |

**type enum**: `default` (black text with border) / `primary` (blue text with border) / `danger` (red text with border) / `text` / `primary_text` / `danger_text` (no border) / `primary_filled` (blue background with white text) / `danger_filled` (red background with white text) / `laser` (laser).

<a id="按钮主次强制"></a>
## Button Hierarchy (Mandatory)

- Only 1 button on the entire card → `type: "primary_filled"`, and `width: "fill"` to fill the width and create a strong focal point.
- Multiple side-by-side buttons → the first one (primary action) `primary_filled`, and all others `default`, forming a "one primary, multiple secondary" hierarchy.
- Dangerous operations such as delete / reject use the `danger` family (`danger` or `danger_filled`).

<a id="behaviors交互行为"></a>
## behaviors (Interactive Behavior)

```json
// 1. Server-side callback
{ "type": "callback", "value": { "key": "v" } }
// 2. Jump link (can coexist with callback in the same array)
{ "type": "open_url", "default_url": "https://x", "pc_url": "", "ios_url": "", "android_url": "" }
```

Buttons inside a form container **do not use behaviors**; instead use the root fields:

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique identifier within the form |
| `form_action_type` | Yes | `submit` (submit form) / `reset` (reset) |

<a id="嵌套--易错点"></a>
## Nesting / Common Pitfalls

- Can be nested inside column_set / form / collapsible_panel / loop container / interactive_container.
- 2.0 has deprecated the `action` interaction module; place buttons directly in `elements` and control arrangement with spacing.
- The old-style `url`/`value` top-level fields are the 1.0 syntax; in 2.0 always use `behaviors`.
- Clicking triggers `card.action.trigger`, returning `action.tag="button"` + `action.value` (i.e., the callback's value).
