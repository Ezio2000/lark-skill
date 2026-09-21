
<a id="docs-media-preview预览文档素材"></a>
# docs +media-preview (Preview document media)


Use this preferentially to view or preview image or file media in a document (`file_token`). The command saves the media to a local path so you can open and view the content afterward.

<a id="选择规则"></a>
## Selection rules

- When the user says "take a look at the media / image / attachment" or "preview it", use `docs +media-preview` preferentially
- When the user explicitly says "download", use [`docs +media-download`](lark-doc-media-download.md)
- If the target is explicitly a board / whiteboard / whiteboard thumbnail, do not use `+media-preview`; use `docs +media-download --type whiteboard` instead

<a id="命令"></a>
## Command

```bash
# Preview image/file media
lark-cli docs +media-preview --token "Z1Fjxxxxxxxx" --output ./asset

# Specify the output file name (if it includes an extension, it will not be auto-completed)
lark-cli docs +media-preview --token "Z1Fjxxxxxxxx" --output ./asset.png
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--token <token>` | Yes | Media token, i.e. `file_token` |
| `--output <path>` | Yes | Local save path; if it has no extension, it will be auto-completed |

<a id="token-从哪里来"></a>
## Where does the token come from

- If you are extracting it from document content: the content returned by `lark-doc-fetch` may include:
  - Image: `<img token="..." .../>`
  - File: `<source token="..." name="..."/>`

<a id="参考"></a>
## References

- [lark-doc-fetch](lark-doc-fetch.md) — Fetch document content (used to extract tokens)
- [lark-doc-media-download](lark-doc-media-download.md) — Explicitly download media, or download a whiteboard thumbnail
- [lark-shared](../../shared/index.md) — Authentication and global parameters
