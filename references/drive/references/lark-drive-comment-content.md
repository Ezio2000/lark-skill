<a id="drive-评论内容格式--content"></a>
# Drive comment content format (--content)

> This document describes the `--content` content format shared by the write-type comment commands (`+add-comment` / `+add-reply` / `+update-reply`), and is referenced by the refs of these three commands.

The `--content` of `drive +add-comment`, `drive +add-reply`, and `drive +update-reply` use the same `reply_elements` JSON array format. This document focuses on the schema, element types, escaping, and length limits; each command ref keeps only the most common plain-text example.

## Schema

`--content` is a JSON array string with at least one element. Each element carries its value in the corresponding field according to `type`:

| type | field | value |
|---|---|---|
| `text` | `text` | Plain text body |
| `mention_user` | `mention_user` | open_id of the @-mentioned user |
| `link` | `link` | Feishu cloud document link (cloud document URL such as docx/doc/sheet/bitable/wiki; corresponds to wire `docs_link`) |

The most common case is a single plain-text element:

```bash
--content '[{"type":"text","text":"评论正文"}]'
```

Combining multiple elements:

```bash
--content '[
  {"type":"text","text":"请 "},
  {"type":"mention_user","mention_user":"ou_xxx"},
  {"type":"text","text":" 看下 "},
  {"type":"link","link":"https://your-tenant.feishu.cn/docx/<TOKEN>"}
]'
```

- The `text` of `type=text` cannot be empty; unknown `type` will be rejected, and only `text` / `mention_user` / `link` are allowed.
- For convenience, the values of `mention_user` / `link` can also be placed directly in the `text` field (e.g. `{"type":"mention_user","text":"ou_xxx"}`), and the CLI will recognize them; using the dedicated fields in the table above is recommended, as the semantics are clearer.
- `link` is a **Feishu cloud document link** (the wire type is called `docs_link`), not an arbitrary web page link. Reply-type commands (`+add-reply` / `+update-reply`) will validate this, and passing an external URL is rejected by the server (`1069302`); only Feishu cloud document URLs are accepted. `+add-comment` is more lenient with external URLs (they can be written), but external links may not render as cloud document links, so it is still recommended to only put cloud document URLs.


<a id="长度限制"></a>
## Length limit

- The total number of characters (runes) across all `type=text` elements is capped at 10000, counted by the number of characters in the original input (Chinese and English, symbols are all treated the same; it is not the byte count, nor the length after escaping).
- This is a limit on the **total**: splitting a long text into multiple text elements cannot bypass it; they share the same 10000-character budget.
- `mention_user` / `link` are not counted toward this length.
- When the limit is exceeded, the shortcut rejects it before sending and points out the elements whose cumulative length exceeds the limit; the server returns an opaque `[1069302]` for over-limit cases, so this is a pre-check.

<a id="参考"></a>
## References

- [lark-drive-add-comment](lark-drive-add-comment.md) -- Add a comment
- [lark-drive-add-reply](lark-drive-add-reply.md) -- Reply to a comment
- [lark-drive-update-reply](lark-drive-update-reply.md) -- Update a reply
