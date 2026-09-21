<a id="卡片-20-组件大纲"></a>
# Card 2.0 Component Outline

Card 2.0 components fall into three categories: **container / display / interactive**, all declared via the `tag` field. First pick a component by purpose in the table below, then click the details to see its fields: for those with a detail file, click `components/<tag>.md` (full fields + examples + common pitfalls); for low-frequency components, click the link to view the official documentation.

<a id="根结构"></a>
## Root Structure

The top level has four fixed fields; build the skeleton first, then fill components into `body.elements`. Below is the **recommended complete skeleton** (including type scale, light/dark color tokens, and the header trio):

```json
{
  "schema": "2.0",
  "config": {
    "update_multi": true,
    "width_mode": "default",
    "style": {
      "text_size": {
        "title":   { "default": "heading-2", "pc": "heading-2", "mobile": "heading-3" },
        "body":    { "default": "normal",    "pc": "normal",    "mobile": "normal"    },
        "caption": { "default": "notation",  "pc": "notation",  "mobile": "notation"  }
      },
      "color": {
        "cus-primary":    { "light_mode": "rgba(30,120,255,1)",    "dark_mode": "rgba(80,150,255,1)"   },
        "cus-primary-bg": { "light_mode": "rgba(30,120,255,0.08)", "dark_mode": "rgba(80,150,255,0.12)" },
        "cus-muted":      { "light_mode": "rgba(100,106,115,1)",   "dark_mode": "rgba(150,155,163,1)"  }
      }
    }
  },
  "header": {
    "title":    { "tag": "plain_text", "content": "卡片标题" },
    "subtitle": { "tag": "plain_text", "content": "副标题：一句上下文（时间/来源/状态）" },
    "template": "blue",
    "icon": { "tag": "standard_icon", "token": "lark-logo_colorful" },
    "text_tag_list": [
      { "tag": "text_tag", "text": { "tag": "plain_text", "content": "状态标签" }, "color": "blue" }
    ]
  },
  "body": { "direction": "vertical", "padding": "12px 12px 20px 12px", "elements": [] }
}
```

> **Trim as needed**: `subtitle` / `text_tag_list` / color tokens can be kept or dropped based on actual needs; using all of them is not mandatory. In components, use `"text_size": "title"` / `"caption"` to reference tokens, and use `"font_color": "cus-muted"` to reference color tokens; when the primary color scheme changes, you only need to change the RGBA in config, and the whole card follows automatically.

- `schema` must be explicitly `"2.0"`, otherwise it renders as 1.0. For `header`, see `components/header.md`.
- **Common element fields** (all `elements[]` components): `tag` (required) · `element_id` (unique within the card, starts with a letter, ≤20 characters) · `margin` (outer margin [-99,99]px).
- `card_link` (whole-card jump): `{url, pc_url, ios_url, android_url}`, at least fill in `url`; to disable jumping on a certain platform, set `lark://msgcard/unsupported_action`.
- Hard limits: a single card ≤ **200** elements; requires client **≥ 7.20** (older versions only display the header).
- For color / icon enums, see `resource/colors.md` · `resource/icons.md`.

**config** (global behavior, can be omitted entirely):

| Field | Default | Description |
|---|---|---|
| `update_multi` | true | Shared card; v2 only supports true |
| `width_mode` | default | `default` (≤600px) / `compact` (400px) / `fill` (fill) |
| `enable_forward` | true | Whether forwarding is allowed |
| `summary` | — | Conversation list preview: `{content, i18n_content:{zh_cn,en_us,…}}` |
| `streaming_mode` | false | Streaming update mode (with `streaming_config`) |
| `style.text_size` | — | Custom font size token, format `{"<名称>":{default,pc,mobile}}`; the name can be customized (e.g. `title`/`caption`), and components reference that name via `text_size` |
| `style.color` | — | Custom color token, format `{"<名称>":{light_mode,dark_mode}}` (RGBA); the name can be customized (e.g. `cus-primary`), and fields such as `font_color`/`background_style` in components reference it |

> Multilingual: `config.locales` limits the languages in which it takes effect; `use_custom_translation` prefers the built-in i18n.

**body layout fields** (all new in v2): `direction` (vertical/horizontal) · `padding` ([0,99]px) · `horizontal_spacing`/`vertical_spacing` (`small`4/`medium`8/`large`12/`extra_large`16 or px) · `horizontal_align`/`vertical_align`.

---

<a id="容器类布局--组织交互"></a>
## Container Category (layout / organizational interaction)

| Component | Purpose |
|---|---|
| [column_set](components/column_set.md) | Horizontal columns, multi-column text-image alignment (data tables, field pairs, lists) |
| [collapsible_panel](components/collapsible_panel.md) | Collapsible panel, to hold secondary information such as notes/long text |
| [form](components/form.md) | Form container, batch-enter form items then submit all at once |
| [interactive_container](components/interactive_container.md) | Whole-block clickable area, can uniformly define styles and interactions |
| [Loop container](components/recycling_container.md) | Batch-render the same layout with different data (builder tools only) |

<a id="展示类无交互"></a>
## Display Category (no interaction)

| Component | Purpose |
|---|---|
| [header](components/header.md) | Card title area: main/subtitle, suffix tags, theme color |
| [div](components/div.md) | Plain text, with prefix icon, field pairs |
| [markdown](components/markdown.md) | Rich text, most commonly used; @mentions, colors, links, lists, tables, etc. |
| [img](components/img.md) | Single image |
| [img_combination](components/img_combination.md) | Multi-image arrangement (two-image/three-image/grid) |
| [person](components/person.md) | Single person avatar/name |
| [person_list](components/person_list.md) | Multiple person avatars/names |
| [chart](components/chart.md) | VChart charts (line/bar/pie/word cloud, etc.) |
| [table](components/table.md) | Multi-column data table (can only be placed at the root node) |
| [hr](components/hr.md) | Divider |

<a id="交互类"></a>
## Interactive Category

| Component | Purpose |
|---|---|
| [button](components/button.md) | Button: callback / jump / form submission |
| [input](components/input.md) | Text input box (mostly embedded within form) |
| [overflow](components/overflow.md) | Collapsible button group, to hold multiple actions |
| [select_static](components/select_static.md) | Dropdown single select |
| [multi_select_static](components/multi_select_static.md) | Dropdown multi-select |
| [select_person](components/select_person.md) | Person single select |
| [multi_select_person](components/multi_select_person.md) | Person multi-select |
| [date_picker](components/date_picker.md) | Date picker |
| [picker_time](components/picker_time.md) | Time picker |
| [picker_datetime](components/picker_datetime.md) | Date-time picker |
| [select_img](components/select_img.md) | Image selection (single/multi-select) |
| [checker](components/checker.md) | Checker, task-check callback |
