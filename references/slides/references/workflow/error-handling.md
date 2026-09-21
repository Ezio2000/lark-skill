# Troubleshooting

This document covers general pre-creation self-checks, XML troubleshooting, and common failure handling for lark-slides. For command-specific issues, refer to the corresponding reference first, such as `+replace-slide`, `+media-upload`.

## XML Preflight

Before actually creating or replacing, at minimum check:

- Special characters are escaped: `&`, `<`, `>` in body text and titles must not be written bare; bare `&` in attribute values must also be written as `&amp;`.
- Attribute quote safety: XML attributes, shell quotes, and JSON string wrapping do not break each other.
- Structure is valid: under `<slide>` only place `<style>`, `<data>`, `<note>`, and all text is inside `<content>`.
- Image paths are correct: `<img src="@...">` placeholders are handled by `+create` and `+add-slide`.

## Failure Order

When encountering `invalid param`, a failed page creation, a blank page, or a broken layout, handle in order:

1. Record `xml_presentation_id`; do not assume that a failure means nothing was created.
2. Use `slides +xml-get` to read back and confirm whether some pages have already been written.
3. Check whether the failed page contains unescaped characters: `Q&A -> Q&amp;A`, text `<` / `>` written as `&lt;` / `&gt;`, attribute URL `a=1&b=2 -> a=1&amp;b=2`.
4. Check tag closure, attribute quotes, `<content>` structure, and `<slide>` direct child elements.
5. When a page is blank, overflows, overlaps, or goes out of bounds, run `xml_lint.py` according to [validation-xml.md](validation-xml.md); first fix all `error`, then take screenshots to review the pages and elements pointed to by `warning`.
6. If using `--slides '[...]'` literals, when suspecting shell escaping or truncation, switch to file input: `+create --slide @page-01.xml --slide @page-02.xml`.
7. For local issues, use `+replace-slide` for block-level corrections; when the entire page structure needs to change, use `+delete-slide` to delete the old page + `+add-slide` to create a new page.

## Symptom Fixes

| Symptom | Fix |
|-----------|----------|
| Text is truncated / not fully visible | Increase the shape's `width` or `height`, or reduce the amount of text |
| Elements overlap | Adjust `topLeftX` / `topLeftY` to increase spacing |
| Large blank areas on the page | Read back to confirm whether content was written; if content exists, then reduce spacing or add main body elements |
| Text and background color are too similar | Use light text on dark backgrounds, dark text on light backgrounds |
| Table column widths are unreasonable | Adjust the `width` value of `col` in `colgroup` |
| Chart does not display | Check whether both `chartPlotArea` and `chartData` are included, and whether the data counts for `dim1` / `dim2` match |
| Image is partially cropped | `width` / `height` of `<img>` are the cropped dimensions; to display the full image, make `width:height` match the original image ratio |
| Image does not display / `<img src>` is still `@path` | `@` placeholders are replaced by `+create` and `+add-slide` |
| Newly inserted `<img>` blocks existing elements | Use `+xml-get --slide-id` to read the original page, and pick blank positions by comparing existing block coordinates; if space is insufficient, first move/shrink existing blocks in the same batch of `--parts`, then insert the image |
| Gradient background becomes white | Gradients must use `rgba()` format + percentage stop points, e.g. `linear-gradient(135deg,rgba(30,60,114,1) 0%,rgba(59,130,246,1) 100%)` |
| Overall style is inconsistent | Use the same background for the cover page and ending page, and keep a consistent color scheme and font size system for content pages |

## Common Errors

| Error code / signal | Meaning | Solution |
|--------------|------|----------|
| 400 XML format error | XML syntax error | Check tag closure, attribute quotes, special character escaping |
| 400 XML input error | XML was not passed in according to the parameters of the shortcut used | Check the values of `--slides`, `--slide`, or `--content` according to the `+create` / `+add-slide` / `+update-slide` reference |
| Creation succeeds but page is blank / content is missing / layout is broken | Commonly seen with shell escaping or long parameter passing issues for `--slides '[...]'` literals | Switch to `--slide @file` (one file per page) or `--slides @deck.json`, and read the XML immediately after creation to verify |
| 403 insufficient permissions | Scope or document permissions do not match | Confirm scope and document permissions; when there are no permissions, guide the user to resolve based on the error response |
| 404 presentation does not exist | `xml_presentation_id` is incorrect or there are no permissions | Check the token; wiki URLs need to first resolve the real `obj_token` |
| 404 slide does not exist | `slide_id` is incorrect | Re-read the presentation or slide to confirm the latest ID |
| 1061002 media upload params error | Slides media upload parameters do not conform to the convention | Use `slides +media-upload`; the shortcut handles the media parameters required by Slides |
| 1061004 forbidden | The current user does not have edit permission for the presentation | Confirm the current user has edit permission for the target PPT |
| 3350001 | XML is not well-formed, the XML structure does not meet server requirements, or there is a replace fragment issue | First check for unescaped characters; for replace scenarios, then check `block_id` and `<content/>` |
| 3350002 | `revision_id` is greater than the current version | Use `-1` to get the current version, or use `slides +xml-get` again to get the latest `revision_id` |
| validation: unsafe file path | `--file` was given an absolute path or parent path | `--file` must be a relative path within the CWD; first `cd` to the asset directory, then execute |

## Command-Specific References

- Image upload, `@path` placeholders, `file_token`: see [lark-slides-media-upload.md](../cli/lark-slides-media-upload.md) and [lark-slides-create.md](../cli/lark-slides-create.md).
- Block-level replacement, `block_id`, 3350001 replace details: see [lark-slides-replace-slide.md](../cli/lark-slides-replace-slide.md).
- Append/insert a single page, `--before-slide-id` and `--slide @file` to bypass escaping: see [lark-slides-add-slide.md](../cli/lark-slides-add-slide.md).
