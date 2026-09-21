<a id="docs-resource-docx-封面图资源"></a>
# docs +resource-* (Docx cover image resource)


A Docx cover image is not a `<img token="...">` material block in the body. When reading, updating, or deleting a document cover image, use `docs +resource-download/+resource-update/+resource-delete --type cover`; do not use `+media-insert` or `+media-download --token <cover.token>` to make the user assemble the steps manually.

<a id="选择规则"></a>
## Selection rules

- User wants to download the document cover image: `docs +resource-download --type cover`
- User wants to set/replace the document cover image: `docs +resource-update --type cover`
- User wants to delete the document cover image: `docs +resource-delete --type cover`
- User wants to download body images, attachments, or board thumbnails: continue using [`docs +media-download`](lark-doc-media-download.md)

<a id="命令"></a>
## Commands

```bash
# Download the cover image. The CLI first reads document.cover.token, then downloads the image content and saves it locally.
lark-cli docs +resource-download --doc doxcnXXX --type cover --output ./cover

# Update the cover image using a local file.
lark-cli docs +resource-update --doc doxcnXXX --type cover --file ./cover.png

# Update the cover image using a clipboard image.
lark-cli docs +resource-update --doc doxcnXXX --type cover --from-clipboard

# Update the cover image using an HTTPS URL. The CLI first downloads the URL content, then uploads it and writes cover.token.
lark-cli docs +resource-update --doc doxcnXXX --type cover --url "https://example.com/cover.png"

# Optional: set the cover image crop offset.
lark-cli docs +resource-update --doc doxcnXXX --type cover --file ./cover.png --offset-ratio-x 0.2 --offset-ratio-y 0.8

# Delete the cover image; also returns success when the document originally had no cover image.
lark-cli docs +resource-delete --doc doxcnXXX --type cover
```

<a id="参数"></a>
## Parameters

| Command | Parameter | Required | Description |
|------|------|------|------|
| all | `--doc <id>` | Yes | Document ID, docx URL, or wiki URL resolvable to docx |
| all | `--type cover` | No | Currently only `cover` is supported; the default value is also `cover` |
| download | `--output <path>` | Yes | Local save path; if no extension is given, it is automatically completed based on the response type |
| download | `--overwrite` | No | Overwrite an existing output file |
| update | `--file <path>` | Choose one of three | A real image file on disk; files larger than 20MiB automatically use multipart upload |
| update | `--from-clipboard` | Choose one of three | Read an image from the system clipboard |
| update | `--url <https-url>` | Choose one of three | Download an image from an HTTPS URL and then upload it |
| update | `--offset-ratio-x <number>` | No | Horizontal offset ratio of the view relative to the center of the original image: horizontal offset px / original image width px; 0 is centered, positive moves right, negative moves left |
| update | `--offset-ratio-y <number>` | No | Vertical offset ratio of the view relative to the center of the original image: vertical offset px / original image height px; 0 is centered, positive moves up, negative moves down |

<a id="输出契约"></a>
## Output contract

- On success, `+resource-download` stdout JSON's `data` contains `document_id`, `type`, `saved_path`, `size_bytes`, `content_type`, and `cover.token`. If the document has no cover image, the command exits with failure, the error contains `document has no cover` and a redacted `document_id`, and no output file is created.
- On success, `+resource-update` stdout JSON's `data` contains the complete `file_token` and `cover.token`; stderr prints only the redacted token.
- On success, `+resource-delete` stdout JSON's `data.deleted` indicates whether a deletion was actually initiated this time, and `data.already_empty` indicates whether there was no cover image before deletion. An empty cover image is an idempotent success and does not report an error.

<a id="url-来源安全边界"></a>
## URL source security boundary

`+resource-update --url` is only used to download public HTTPS images:

- Only `https://` is allowed; HTTP, empty host, and URL userinfo are rejected.
- Reject hosts that resolve to private, loopback, link-local, multicast, or unspecified addresses.
- Follow at most 3 redirects, and revalidate the URL on every redirect.
- The response `Content-Type` only allows `image/png`, `image/jpeg`, `image/gif`, and `image/webp`.
- The response body is at most 20MiB.

<a id="参考"></a>
## References

- [lark-doc-media-download](lark-doc-media-download.md) — download body materials or board thumbnails
- [lark-doc-media-insert](lark-doc-media-insert.md) — insert images/files into the body
- [lark-shared](../../shared/index.md) — authentication and global parameters
