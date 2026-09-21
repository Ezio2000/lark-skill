# okr +upload-image


Upload a local image, used for the rich text content of OKR progress records.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Upload an image for the progress record of an objective
lark-cli okr +upload-image \
  --file ./progress_screenshot.png \
  --target-id 1234567890123456789 \
  --target-type objective

# Upload an image for the progress record of a key result
lark-cli okr +upload-image \
  --file ./chart.jpg \
  --target-id 9876543210987654321 \
  --target-type key_result
```

<a id="参数"></a>
## Parameters

| Parameter              | Required | Default | Description                                    |
|-----------------|----|-----|---------------------------------------|
| `--file`        | Yes  | —   | Local image path. **Must use a relative path** (e.g., `./photo.png`). |
| `--target-id`   | Yes  | —   | Objective ID or key result ID (int64 type, positive integer)          |
| `--target-type` | Yes  | —   | Objective type: `objective` \| `key_result`      |
| `--dry-run`     | No  | —   | Preview the API call without actually executing it.                      |

<a id="工作流程"></a>
## Workflow

1. Use `+cycle-list` and `+cycle-detail` to obtain the objective or key result ID.
2. Prepare the local image file and ensure the format is supported.
3. Execute `lark-cli okr +upload-image --file ./image.png --target-id "..." --target-type objective`.
4. Obtain the returned `file_token`, used to build the image content in the ContentBlock.

<a id="输出"></a>
## Output

Returns JSON:

```json
{
  "file_token": "example-file-token",
  "url": "https://example.larksuite.com/download?file_token=example-file-token",
  "file_name": "screenshot.png",
  "size": 102400
}
```

Where:

- `file_token` — used to reference the image in the ContentBlock's `ContentGallery`
- `url` — the image's access URL
- `file_name` — the uploaded file name
- `size` — file size (bytes)

<a id="在进展记录中使用上传的图片"></a>
## Using the uploaded image in a progress record

After uploading the image, use the returned `file_token` to build the gallery block of the ContentBlock:

```json
{
  "blocks": [
    {
      "block_element_type": "paragraph",
      "paragraph": {
        "elements": [
          {
            "paragraph_element_type": "textRun",
            "text_run": {
              "text": "本周进展截图："
            }
          }
        ]
      }
    },
    {
      "block_element_type": "gallery",
      "gallery": {
        "images": [
          {
            "file_token": "example-file-token",
            "width": 800,
            "height": 600
          }
        ]
      }
    }
  ]
}
```

Then use this ContentBlock when creating or updating a progress record:

```bash
lark-cli okr +progress-create \
  --content @content_with_image.json \
  --target-id 1234567890123456789 \
  --target-type objective
```

<a id="安全限制"></a>
## Security restrictions

- The `--file` parameter **must use a relative path** (e.g., `./photo.png` or `images/photo.png`); absolute paths are not supported
- The image file must exist in the current working directory or its subdirectories
- Symbolic links pointing to files outside the directory are not supported

<a id="参考"></a>
## References

- [lark-okr](../index.md) -- all OKR commands (shortcuts and API interfaces)
- [ContentBlock format](lark-okr-contentblock.md) -- the rich text format used for progress content, including instructions for using image blocks
- [lark-okr-progress-create](lark-okr-progress-create.md) -- create a progress record
- [lark-okr-progress-update](lark-okr-progress-update.md) -- update a progress record
- [lark-shared](../../shared/index.md) -- authentication and global parameters
