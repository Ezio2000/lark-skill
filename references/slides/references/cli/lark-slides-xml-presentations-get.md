<a id="slides-xml-get读取演示文稿-xml"></a>
# slides +xml-get (read presentation XML)

Read the full XML or a single page's XML. For full-document verification, prefer saving the result to a local file; for local edits, you can read a single page's XML and obtain the `block_id` needed by `+replace-slide` from the `id` attribute of the top-level block.

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--presentation` | Yes | `xml_presentation_id`, a Slides URL, or a wiki URL that can be resolved to Slides |
| `--revision-id` | No | Version number; `-1` means the latest version |
| `--output` | No | XML save path, must use a relative path within the CWD; when omitted, returns JSON |
| `--raw` | No | Output the XML directly to stdout; cannot be used together with `--output`, `--jq`, or a non-JSON `--format` |
| `--slide-id` | No | Read only the specified page; cannot be used together with `--slide-number` or `--remove-attr-id` |
| `--slide-number` | No | Read only the specified 1-based page number; cannot be used together with `--slide-id` or `--remove-attr-id` |
| `--remove-attr-id` | No | Available only for full-document reads; removes the XML `id` attribute, not suitable for subsequent precise block editing |

<a id="示例"></a>
## Examples

```bash
# Read the full document and save it, for post-creation verification
lark-cli slides +xml-get --as user \
  --presentation "$PRES_ID" \
  --output ".lark-slides/plan/$PRES_ID/readback.xml"

# Read a single page to obtain the block_id
lark-cli slides +xml-get --as user \
  --presentation "$PRES_ID" --slide-id "$SID" --raw

# Read a single page and also record the revision_id for subsequent optimistic locking
REV=$(lark-cli slides +xml-get --as user \
  --presentation "$PRES_ID" --slide-id "$SID" \
  --jq '.data.revision_id')
```

In the JSON output, the full-document XML is located at `.data.xml_presentation.content`, and the single-page XML is located at `.data.slide.content`; the `.data.revision_id` of both can be used for subsequent write operations.

Related commands:

- [slides +replace-slide](lark-slides-replace-slide.md) — block-level replace / insert
- [slides +update-slide](lark-slides-update-slide.md) — full-page overwrite
