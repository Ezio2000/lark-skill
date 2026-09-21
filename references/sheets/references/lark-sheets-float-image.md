# Lark Sheet Float Image

> **Float image or cell image? One question decides**: Does this image **belong to a record and need to sort / filter / be added or removed along with that row**?
> - **Yes → cell image** (not in this reference): embedded in a cell, travels with the row. Use `+cells-set-image` (or `+cells-set`'s `rich_text` + `type: "embed-image"`, see lark-sheets-write-cells). Typical: receipts / ID photos / product images / avatars / QR codes / per-row images; if the wording contains binding words like "corresponding / per row / per record / this column", it belongs to this category.
> - **No → float image** (this reference): freely placed decoration / marking not bound to data (logo / watermark / large cover image / banner).
> - ⚠️ Don't choose it just because "float image position and size are easier to control / more familiar"—that's choosing by operational convenience, not by scenario; using a float image to carry an image that "corresponds to a record" will become misaligned after rows are added/removed / sorted.

<a id="真对象硬约束"></a>
## Real object hard constraint

When the user asks to "insert an image / add a logo / place an image", you **must** create a real image object via `+float-image-{create|update|delete}` (float image) or `+cells-set-image` / `+cells-set`'s `embed-image` (cell image). **It is forbidden** to only give an image link / describe the image content in a text reply instead of inserting it. Criterion: after delivery, `+float-image-list` or the cell `rich_text` must be able to read that image object.

<a id="使用场景"></a>
## Use cases

Read and write **float image** objects (images floating above cells, not part of cell content). This reference covers 4 shortcuts:

| Operation need | Tool to use | Description |
|---------|---------|------|
| View existing float images | `+float-image-list` | Get the position, size, and layer configuration of float images |
| Create/update/delete float images | `+float-image-{create|update|delete}` | Perform write operations on float images |

Typical workflow: first read existing float images to understand the configuration → perform create/update/delete → **must read again to verify the result**.

**Common configuration errors (must pay attention)**:
- **Wrong choice between cell image vs float image**: when an image corresponds one-to-one with a record and needs to sort / filter / be added or removed along with the row, you should use `+cells-set-image` (see the top discriminator); using a float image will cause misalignment.
- **Image position parameters must be precise**: the anchor cell's row and column indices and offsets determine the image position; improper settings will cause the image to cover data
- **Must verify after creation**: call `+float-image-list` to confirm the image position and size are correct

There are three ways to provide the image source; on `+float-image-create` the three are **XOR, exactly one must be given** (`--image` / `--image-token` / `--image-uri`):

- **`--image <本地路径>` (preferred, most convenient)**: directly give the local image file path (PNG/JPEG/GIF/BMP/HEIC, etc.). The CLI will automatically upload it as `parent_type=sheet_image`, get the file_token, and then create the float image, **no need for you to manually upload / get the token**. Path rules are the same as other local file flags: it must be a relative path within the current working directory (absolute paths will be rejected by Validate, and `--dry-run` will also block them).
- `--image-token`: reuse an **existing** image file_token. Common sources: ① the `image_token` returned by `+float-image-list` (suitable for "changing the skin without changing the position" to reuse the same image); ② the `file_token` in the successful return of `+cells-set-image` (it is also a `sheet_image` upload handle). Suitable for "reusing the same image in multiple places", saving repeated uploads.
- `--image-uri`: image URI (the handle returned by the upload chain), **not** an in-sheet object reference_id; the system automatically converts it to a file_token.

> ⚠️ **`--image` is only supported by `+float-image-create`**. `+float-image-update` changing the image still only accepts `--image-token` / `--image-uri`, and **the image source is the only part that can be omitted in update**—if none of the three are passed, the original image is kept. But `--image-name` / `--position-{row,col}` / `--size-{width,height}` are **required** in update just as in create (`+float-image-update` mandates this set of core fields, and `+float-image-list` does not return `image_name` for the CLI to backfill). To change to a new local image in update, first use `+cells-set-image` to upload it to any temporary cell, take the `file_token` from the return, then pass it to update's `--image-token`; after use, clear that temporary cell to avoid leaving an extra image behind.

## Shortcuts

| Shortcut | Risk | Group |
| --- | --- | --- |
| `+float-image-list` | read | Object |
| `+float-image-create` | write | Object |
| `+float-image-update` | write | Object |
| `+float-image-delete` | high-risk-write | Object |

## Flags

### `+float-image-list`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--float-image-id` | string | optional | Filter by id; when omitted, list all worksheets |

### `+float-image-create`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--image-name` | string | required | Image name, including extension (e.g. `logo.png`) |
| `--image-token` | string | xor | Image file_token (choose one of two with `--image-uri`). Common source: the `image_token` returned by `+float-image-list` |
| `--image-uri` | string | xor | Image URI (the handle returned by the upload chain, not an in-sheet object reference_id; choose one of two with `--image-token`); the system automatically converts it to a file_token |
| `--position-row` | int | required | Row of the image's top-left corner (0-based) |
| `--position-col` | string | required | Column of the image's top-left corner (column letter, e.g. `A` / `B`) |
| `--size-width` | int | required | Image width (pixels) |
| `--size-height` | int | required | Image height (pixels) |
| `--offset-row` | int | optional | In-row offset based on `--position-row` (pixels) |
| `--offset-col` | int | optional | In-column offset based on `--position-col` (pixels) |
| `--z-index` | int | optional | Image Z-axis layer, controls overlap order |
| `--image` | string | xor | Local image path (PNG/JPEG, etc.); the CLI automatically uploads it as sheet_image and uses the returned file_token, saving you from manually getting a token (choose one of three with --image-token / --image-uri) |

### `+float-image-update`

_Common four-piece set · System: `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--float-image-id` | string | required | Target image id |
| `--image-name` | string | required | Image name, including extension (e.g. `logo.png`) |
| `--image-token` | string | optional | Optional image file_token; mutually exclusive with `--image-uri`, when both are omitted the original image is kept. Common source: the `image_token` returned by `+float-image-list` |
| `--image-uri` | string | optional | Optional image URI (the handle returned by the upload chain, not an in-sheet object reference_id); mutually exclusive with `--image-token`, when both are omitted the original image is kept; the system automatically converts it to a file_token |
| `--position-row` | int | required | Row of the image's top-left corner (0-based) |
| `--position-col` | string | required | Column of the image's top-left corner (column letter, e.g. `A` / `B`) |
| `--size-width` | int | required | Image width (pixels) |
| `--size-height` | int | required | Image height (pixels) |
| `--offset-row` | int | optional | In-row offset based on `--position-row` (pixels) |
| `--offset-col` | int | optional | In-column offset based on `--position-col` (pixels) |
| `--z-index` | int | optional | Image Z-axis layer, controls overlap order |

### `+float-image-delete`

_Common four-piece set · System: `--yes`, `--dry-run`_

| Flag | Type | Required | Description |
| --- | --- | --- | --- |
| `--float-image-id` | string | required | Target image id |

## Examples

Common four-piece set: all shortcuts have `--url` / `--spreadsheet-token` / `--sheet-id` / `--sheet-name` at the top (XOR). Float images are sheet-level objects—unlike cell-embedded images (the latter go through `+cells-set`).

### `+float-image-list`

```bash
lark-cli sheets +float-image-list --url "..." --sheet-id "$SID"
```

### `+float-image-create`

All fields are flattened into independent flags: image source `--image` / `--image-token` / `--image-uri` (choose one of three XOR) / `--image-name` / `--position-{row,col}` / `--size-{width,height}` / `--offset-{row,col}` / `--z-index`.

```bash
# Preferred: directly give the local image path, the CLI uploads automatically (no need to manually get a token)
# Note: --image-name is required (even if the path basename is already logo.png, you must still pass it explicitly)
lark-cli sheets +float-image-create --url "..." --sheet-id "$SID" \
  --image ./logo.png --image-name "logo.png" \
  --position-row 2 --position-col B --size-width 300 --size-height 200 --z-index 1

# Use an existing file_token (from +float-image-list's image_token or the file_token returned by +cells-set-image)
lark-cli sheets +float-image-create --url "..." --sheet-id "$SID" \
  --image-name "logo.png" --image-token "$TOKEN" \
  --position-row 0 --position-col A --size-width 200 --size-height 150

# Use an image URI (the handle returned by the upload chain, not an in-sheet object reference_id; choose one of two with --image-token)
lark-cli sheets +float-image-create --url "..." --sheet-id "$SID" \
  --image-name "logo.png" --image-uri "$IMAGE_URI" \
  --position-row 2 --position-col B --size-width 300 --size-height 200 --z-index 1
```

### `+float-image-update`

> **update ≈ create, only the image source can be omitted**: `+float-image-update`'s update requires the same core fields as create—`--image-name`, `--position-{row,col}`, `--size-{width,height}` are **all required**; the only difference is that **the image source (`--image-token` / `--image-uri`) can all be omitted**, and omitting them keeps the original image. This is **not** a "only send the changed fields" patch: missing any core field will be rejected (`+float-image-list` does not return `image_name`, so the CLI cannot backfill it for you).
>
> Recommended flow: first `+float-image-list --float-image-id <id>` to read back the current position / size, then call `+float-image-update` once with `--image-name` and the complete position / size.

```bash
# Adjust position + size, keep the original image (do not pass an image source)
lark-cli sheets +float-image-update --url "..." --sheet-id "$SID" \
  --float-image-id "$IMG_ID" --image-name "logo.png" \
  --position-row 5 --position-col C --size-width 300 --size-height 200

# Change the image: additionally pass --image-token, and the core fields must also be given in full
lark-cli sheets +float-image-update --url "..." --sheet-id "$SID" \
  --float-image-id "$IMG_ID" --image-name "new-logo.png" --image-token "$NEW_TOKEN" \
  --position-row 5 --position-col C --size-width 300 --size-height 200
```

### `+float-image-delete`

```bash
lark-cli sheets +float-image-delete --url "..." --sheet-id "$SID" --float-image-id "$IMG_ID" --yes
```

<a id="validate--dryrun--execute-约束"></a>
### Validate / DryRun / Execute constraints

- `Validate`: XOR common four-piece set; `+float-image-create` requires `--image` / `--image-token` / `--image-uri` to **give exactly one**, `--position-row/col` and `--size-width/height` are required and must be valid integers; when `--image` is passed, path safety is also validated (absolute paths / paths outside the working directory will be rejected, and `--dry-run` blocks them as well). `+float-image-update` must be `--float-image-id`, and like create requires `--image-name` / `--position-{row,col}` / `--size-{width,height}` (missing any core field errors out locally, it will not silently send 0); the image source `--image-token` / `--image-uri` can be omitted (omitting keeps the original image), and if given, choose one of the two; `+float-image-delete` enforces `--yes` or `--dry-run`.
- `DryRun`: write operations output the "float_image request template about to be POST/PATCH/DELETE"; when `--image` is passed, it additionally prints one local image upload step (`POST /open-apis/drive/v1/medias/upload_all`, `parent_type=sheet_image`).
- `Execute`: does not automatically read back after writing; after create/update you must call `+float-image-list --float-image-id <id>` to compare position and size (it does not return `image_name`, so the name cannot be checked); after delete, list to confirm the target no longer exists.
