<a id="slides-delete-slide按-slide_id-删除单页"></a>
# slides +delete-slide (delete a single slide by slide_id)

Delete **one slide** from a presentation, specified by `slide_id`. To change only part of the content within a single slide, use [`+replace-slide`](lark-slides-replace-slide.md); do not delete and recreate.

`--presentation` accepts a token / `/slides/` URL / `/wiki/` URL, and the slide ID is passed via `--slide-id`.

> `--slide-id` accepts only a single ID — comma-separated lists are not supported (`+screenshot`'s `--slide-id` supports them, this one does not), and deleting by page number is also not supported.

<a id="命令"></a>
## Command

```bash
# Pass xml_presentation_id directly
lark-cli slides +delete-slide --as user \
  --presentation "$PRES_ID" \
  --slide-id "$SID"

# Both slides URL / wiki URL work (wiki is automatically resolved and validated with obj_type=slides)
lark-cli slides +delete-slide --as user \
  --presentation "https://xxx.feishu.cn/wiki/wikcnXXXXXX" \
  --slide-id "$SID"

# Before deleting, first confirm which PPT and which slide you are targeting
lark-cli slides +delete-slide --presentation "$PRES_ID" --slide-id "$SID" --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--presentation` | Yes | `xml_presentation_id`, `/slides/` URL, or `/wiki/` URL |
| `--slide-id` | Yes | ID of the slide to delete |
| `--revision-id` | No | Presentation version number, defaults to `-1` (latest); pass a specific version number for optimistic locking |
| `--dry-run` | No | Print the request that will be sent, without deleting |

<a id="成功输出"></a>
## Success output

```json
{
  "xml_presentation_id": "slides_example_presentation_id",
  "slide_id": "slide_example_id",
  "deleted": true,
  "revision_id": 43
}
```

<a id="怎么拿-slide_id"></a>
## How to get `slide_id`

`slide_id` is a server-side short ID and **cannot be derived from the XML**. Two sources:

1. Save it from the return value of `+create` / `+add-slide`;
2. Read it back afterward: `slides +xml-get --presentation "$PRES_ID" --output .lark-slides/plan/<deck>/readback.xml`.

The cost of deleting the wrong slide is higher than running one extra read-back — if unsure, read back first + take a look with `+screenshot` before deleting.

<a id="删错了怎么办"></a>
## What to do if you deleted the wrong one

Deletion is irreversible in place, but you can roll back via historical versions: `+history-list` to find `history_version_id` → `+history-revert` (only accepts `history_version_id`, cannot pass `revision_id`) → `+history-revert-status` polling. For command usage, see [lark-slides-history.md](lark-slides-history.md).

<a id="常见错误"></a>
## Common errors

| Symptom | Cause | Solution |
|------|------|------|
| `--slide-id cannot be empty` | An empty string or pure whitespace was passed | Check whether the variable actually got a value |
| 3350001 `invalid param` | `slide_id` is wrong or the slide has already been deleted | `+xml-get` read back to confirm `slide_id` still exists |
| 403 / insufficient permissions | The current identity does not have edit permission on this PPT | Check whether you have the `slides:presentation:update` or `slides:presentation:write_only` scope; a wiki link additionally requires `wiki:node:read`; `--as bot` also requires that the bot has edit permission on the target PPT |
