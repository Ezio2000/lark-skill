<a id="图片准备-image-preparation"></a>
# Image Preparation

> This document explains how to use image nodes in the whiteboard DSL. Before entering any scenario that involves images, you must first complete the image preparation process.

<a id="概述"></a>
## Overview

The whiteboard DSL supports `type: 'image'` nodes, but images cannot directly use URLs or tokens from other domains. **You must first upload them to the target whiteboard to obtain a media token in the `whiteboard` domain**, and then reference it in the DSL.

**Core rule**: Regardless of where the image comes from (a local file, a URL, an `docx_image` token in a document, a Drive token from another domain), it must be uploaded via `docs +media-upload --parent-type whiteboard --parent-node <目标画板token>`. Only after obtaining the whiteboard-specific media token can it be used in the DSL. Directly using a token from a domain other than `whiteboard` will cause the whiteboard API to return 500 (error code 2891001) or the image to disappear from the document.

<a id="step-0图片准备流程"></a>
## Step 0: Image Preparation Process

<a id="1-获取图片到本地"></a>
### 1. Obtain the Image Locally

Choose the corresponding method based on the image source:

| Image Source | How to Obtain |
|---------|---------|
| Local file | Use directly |
| Web URL | `curl -L -o photo.jpg "<URL>"` |
| Image token in a document | `lark-cli docs +media-download --token <token> --output ./photo.png` |
| Drive token from another domain | `lark-cli docs +media-download --token <token> --output ./photo.png` |

**Image source selection (when image search is needed)**:

| Image Source Type | Description |
|-------|------|
| Free-license image library | Supports keyword search, images carry no copyright risk (CC0 or similar licenses), the library has a rich variety of categories (people/animals/landscapes/food/architecture, etc.), and keywords can precisely match image content |
| Direct URL | An image link provided by the user or already known, the most reliable |

**Necessary conditions for choosing an image library**:
- **Copyright compliance**: Images must carry no risk of copyright disputes; avoid using libraries that require paid licensing or have usage restrictions
- **Keyword search**: Supports keyword search and returns relevant images, ensuring the image content matches the topic
- **Rich content**: The library has many categories and a large quantity of images, capable of covering common topics (pets, food, attractions, products, etc.)

**Strictly prohibited to use random placeholder image services**: Some image libraries only provide random placeholder images; the keyword parameters in the URL do not affect the returned image content, and the downloaded images are completely unrelated to the topic.

<a id="2-校验图片"></a>
### 2. Validate the Images

```bash
ls -l *.jpg   # Confirm that each file has a different size; if the sizes are the same, the content may be duplicated and needs to be re-downloaded
```

**Image content review (must be performed)**:
- After downloading is complete, confirm that the file is a real image rather than an HTML error page: if a certain image is < 1KB in size, it is very likely that the download failed and returned an HTML error page, and it needs to be re-downloaded
- **Image content correctness can only be verified after rendering**: After generating the DSL and rendering the PNG locally, you must inspect the rendered result to confirm that each image's content is related to the topic (for example, images for a pet-themed topic are indeed pets, rather than unrelated content such as architecture/landscapes)
- If you find that the image content does not match the topic, you must re-download with more precise keywords and re-upload

<a id="3-上传到目标画板"></a>
### 3. Upload to the Target Whiteboard

You **must** use `docs +media-upload --parent-type whiteboard` to upload:

```bash
lark-cli docs +media-upload --file ./photo1.jpg --parent-type whiteboard --parent-node <whiteboard_token>
# Response: { "file_token": "<media_token>", ... }
```

Upload one by one, collecting each media token:

```bash
lark-cli docs +media-upload --file ./photo1.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_1>
lark-cli docs +media-upload --file ./photo2.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_2>
lark-cli docs +media-upload --file ./photo3.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_3>
```

<a id="4-在-dsl-中引用"></a>
### 4. Reference in the DSL

```json
{ "type": "image", "id": "img-1", "width": 240, "height": 160, "image": { "src": "<media_token_1>" } }
```

<a id="常见错误"></a>
## Common Errors

| Error Symptom | Cause | Solution |
|---------|------|------|
| Whiteboard API returns 500 (2891001) | A token from a domain other than `whiteboard` was used (such as `docx_image`, Drive file token) | After downloading the image, re-upload it using `docs +media-upload --parent-type whiteboard` |
| Whiteboard API returns 500 | The image was uploaded to another whiteboard | Re-upload to the target whiteboard |
| The whiteboard's image disappears from the document | The resource domain of the image token does not match the whiteboard | Ensure the image is uploaded via `--parent-type whiteboard --parent-node <画板token>` |
| Image is broken/cannot be displayed | The token is invalid or has expired | Re-upload to obtain a new token |
| Image content is unrelated to the topic | A random placeholder image service was used | Switch to a free-license image library service |
