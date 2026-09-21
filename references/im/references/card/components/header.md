<a id="标题-header"></a>
# Header `header`

The title area at the top of the card (main/subtitle, suffix tags, icon, theme color). **Card 2.0**. It is attached under the `header` key at the card root, not inside `body.elements`, and there is only one per card.

<a id="最小示例"></a>
## Minimal example

```json
{
  "header": {
    "title": { "tag": "plain_text", "content": "卡片标题" },
    "template": "blue"
  }
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Description |
|---|---|---|---|
| `title` | Yes | Object | Main title, `{tag:"plain_text"\|"lark_md", content}`, up to 4 lines |
| `subtitle` | No | Object | Subtitle, same as title, up to 1 line; if only the subtitle is configured, it is displayed as the main title |
| `template` | No | String | Theme color enum, see below; default `default` |
| `text_tag_list` | No | Array | Suffix tags, up to 3, each item `{tag:"text_tag", text:{tag:"plain_text",content}, color}` |
| `i18n_text_tag_list` | No | Object | Multilingual suffix tags; choose one of this and `text_tag_list`, and if both are configured, the multilingual one takes precedence |
| `icon` | No | Object | Prefix icon (same as `div.icon`) |
| `padding` | No | String | Inner padding, default 12px, [0,99]px |

**template enum** (13 colors): `blue` / `wathet` / `turquoise` / `green` / `yellow` / `orange` / `red` / `carmine` / `violet` / `purple` / `indigo` / `grey` / `default`.

**Tag color enum**: `neutral`/`blue`/`turquoise`/`lime`/`orange`/`violet`/`indigo`/`wathet`/`green`/`yellow`/`red`/`purple`/`carmine`. For light/dark levels and RGBA, see `../resource/colors.md`.

<a id="选色建议"></a>
## Color selection suggestions

For choosing template colors by scenario, see the intent table in `../lark-im-card-style.md`. Common semantics: green=success/completed, orange=warning, red=error/danger, grey=disabled/archived, blue=general information.
