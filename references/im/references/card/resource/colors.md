<a id="颜色枚举"></a>
# Color Enumeration

All color fields on cards (`font_color` / `text_color` / `background_style` / `border_color` / icon `color`, etc.) share the same enumeration, with usage distinguished by property name; there is no separate text/background color table.

<a id="基础色名14-色系"></a>
## Base Color Names (14 Color Families)

`blue` `carmine` `green` `indigo` `lime` `orange` `purple` `red` `sunflower` `turquoise` `violet` `wathet` `yellow` `grey`

> **Tag exception**: The gray for `text_tag` / `<text_tag>` uses `neutral` (not `grey`); the tag enumeration has no `grey`.

<a id="深浅后缀"></a>
## Light/Dark Suffixes

- Color families (13 non-grey): `-50 -100 -200 -300 -350 -400 -500 -600 -700 -800 -900`, the larger the number, the darker.
- **Base name without suffix (e.g., `blue`) = `-600`** (same color value).
- grey has a finer range: `-00 -50 -100 … -650 … -950 -1000`.
- Usage semantics: `-50` block background · `-100` tag background · `-500` body text · `-600/-700` emphasized text.

<a id="特殊值"></a>
## Special Values

`white` (white) · `bg-white` (background white: light mode #ffffff / dark mode #1A1A1A). There is no `transparent` enumeration.

<a id="自定义-rgba"></a>
## Custom RGBA

Define a token in `config.style.color` and then reference it:

```json
"config": { "style": { "color": {
  "cus-0": { "light_mode": "rgba(5,157,178,0.52)", "dark_mode": "rgba(...)" }
} } }
```

In the component, write `"font_color": "cus-0"`. The properties supported by RGBA are the same as the enumeration (font/text_color, background_style, border_color, icon color, etc.).

> `column`'s `background_style` requires client v7.9+. For color matching rules, see `../lark-im-card-style.md` visual guidelines.
