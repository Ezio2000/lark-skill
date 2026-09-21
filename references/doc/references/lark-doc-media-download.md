
<a id="docs-media-download下载文档素材画板缩略图"></a>
# docs +media-download (Download document media/whiteboard thumbnails)


Download image/file media in a document (`file_token`), or download a whiteboard thumbnail (`whiteboard_id`). When `--output` has no extension, the extension is automatically appended based on the response's `Content-Type`.

<a id="选择规则"></a>
## Selection rules

- When the user explicitly says "download media", use `docs +media-download`
- When the user only wants to view or preview image or file media, prefer [`docs +media-preview`](lark-doc-media-preview.md)
- If the target is explicitly a whiteboard / whiteboard thumbnail, continue to use `docs +media-download --type whiteboard`; `+media-preview` does not support whiteboards

<a id="命令"></a>
## Command

```bash
# Download image/file media (default type=media)
lark-cli docs +media-download --token "Z1Fjxxxxxxxx" --output ./asset

# Specify the output file name (if it has an extension, it will not be auto-completed)
lark-cli docs +media-download --token "Z1Fjxxxxxxxx" --output ./asset.png

# Download whiteboard thumbnail (whiteboard token)
lark-cli docs +media-download --type whiteboard --token "wbcnxxxxxxxx" --output ./whiteboard
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--token <token>` | Yes | Resource token: for media it is `file_token`, for whiteboards it is `whiteboard_id` |
| `--output <path>` | Yes | Local save path; if it has no extension, it will be auto-completed |
| `--type <type>` | No | `media` (default) or `whiteboard` |

<a id="token-从哪里来"></a>
## Where does the token come from

- If you are extracting it from document content: the content returned by `lark-doc-fetch` may contain:
  - Images: `<img token="..." .../>`
  - Files: `<source token="..." name="..."/>`
  - Whiteboards: `<whiteboard token="..."/>`

<a id="排障"></a>
## Troubleshooting

- If `permission_denied` is returned, or the final download returns `HTTP 403`, follow the error `hint` and switch to [`docs +media-preview`](lark-doc-media-preview.md) to preview the content.
- If a rate limit error is returned, stop retrying immediately and retry later with exponential backoff.

<a id="参考"></a>
## References

- [lark-doc-fetch](lark-doc-fetch.md) — Fetch document content (used to extract tokens)
- [lark-doc-media-preview](lark-doc-media-preview.md) — Preview media
- [lark-shared](../../shared/index.md) — Authentication and global parameters
