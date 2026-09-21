
# drive +export


Export `doc` / `docx` / `sheet` / `bitable` / `slides` (also supports automatic unwrapping of Wiki URL / Wiki node token) to a local file. This shortcut has built-in limited polling:

- If the export task completes within the polling window, it will be downloaded directly to the local directory
- If polling ends and the task is still not complete, it will return `ticket`, `ready=false`, `timed_out=true`, and `next_command`
- To continue checking the result later, switch to `drive +task_result --scenario export`
- After obtaining `file_token`, switch to `drive +export-download`

<a id="命令"></a>
## Command

```bash
# Recommended: pass the URL directly; the CLI automatically parses the type and token
lark-cli drive +export \
  --url "https://example.feishu.cn/docx/<DOCX_TOKEN>" \
  --file-extension pdf

# For Wiki URLs, passing them directly is also recommended; the CLI will first resolve to the underlying obj_token/obj_type
lark-cli drive +export \
  --url "https://example.feishu.cn/wiki/<WIKI_NODE_TOKEN>" \
  --file-extension pdf

# When you only have a bare Wiki node token, explicitly pass --doc-type wiki so the CLI first resolves to the underlying document type
lark-cli drive +export \
  --token "<WIKI_NODE_TOKEN>" \
  --doc-type wiki \
  --file-extension pdf

# Export a new-version document as pdf, saved to the current directory by default
lark-cli drive +export \
  --token "<DOCX_TOKEN>" \
  --doc-type docx \
  --file-extension pdf

# Export a legacy document as docx
lark-cli drive +export \
  --token "<DOC_TOKEN>" \
  --doc-type doc \
  --file-extension docx

# Export docx as markdown (Lark-flavored Markdown)
# Note: markdown only supports docx
lark-cli drive +export \
  --token "<DOCX_TOKEN>" \
  --doc-type docx \
  --file-extension markdown

# Export a spreadsheet as xlsx
lark-cli drive +export \
  --token "<SHEET_TOKEN>" \
  --doc-type sheet \
  --file-extension xlsx \
  --output-dir ./exports

# Export slides as pptx
lark-cli drive +export \
  --token "<SLIDES_TOKEN>" \
  --doc-type slides \
  --file-extension pptx \
  --output-dir ./exports

# Export slides as pdf
lark-cli drive +export \
  --token "<SLIDES_TOKEN>" \
  --doc-type slides \
  --file-extension pdf \
  --output-dir ./exports

# Specify the local file name (the extension will be automatically appended based on the export format)
lark-cli drive +export \
  --token "<DOCX_TOKEN>" \
  --doc-type docx \
  --file-extension pdf \
  --file-name "weekly-report.pdf" \
  --output-dir ./exports

# When exporting a spreadsheet or Base as csv, sub_id must be passed
lark-cli drive +export \
  --token "<SHEET_OR_BITABLE_TOKEN>" \
  --doc-type "<sheet|bitable>" \
  --file-extension csv \
  --sub-id "<SUB_ID>" \
  --output-dir ./exports

# Export a Base as a .base snapshot (only supports bitable)
lark-cli drive +export \
  --token "<BITABLE_TOKEN>" \
  --doc-type bitable \
  --file-extension base \
  --output-dir ./exports

# Export the Base structure as a .base snapshot (only exports the table structure, not the record data)
lark-cli drive +export \
  --token "<BITABLE_TOKEN>" \
  --doc-type bitable \
  --file-extension base \
  --only-schema \
  --output-dir ./exports

# Allow overwriting existing files
lark-cli drive +export \
  --token "<DOCX_TOKEN>" \
  --doc-type docx \
  --file-extension pdf \
  --overwrite
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--url` | Choose one of `--token` | Source document URL, recommended as the preferred option; the CLI automatically parses the type and token, and Wiki URLs will be resolved to the underlying `obj_token/obj_type` |
| `--token` | Choose one of `--url` | Source document bare token; a bare token requires also passing `--doc-type`. A bare Wiki node token requires passing `--doc-type wiki`, and the CLI will first resolve to the underlying `obj_token/obj_type` |
| `--doc-type` | Conditionally required | Source document type: `doc` / `docx` / `sheet` / `bitable` / `slides` / `wiki`; required only when using a bare `--token`, and automatically inferred when using `--url`. `wiki` is only used for a bare Wiki node token, and after resolution the export will be initiated based on the real underlying type |
| `--file-extension` | Yes | Export format: `docx` / `pdf` / `xlsx` / `csv` / `markdown` / `base` / `pptx` |
| `--sub-id` | Conditionally required | Required when `sheet` / `bitable` is exported as `csv` |
| `--only-schema` | No | Available only when `--doc-type bitable --file-extension base`; exports only the Base structure, not the record data |
| `--file-name` | No | Overrides the default local file name; if no extension is included, it will be automatically appended based on `--file-extension` |
| `--output-dir` | No | Local output directory, defaults to the current directory |
| `--overwrite` | No | Overwrite existing files |

<a id="关键约束"></a>
## Key Constraints

- Prefer passing `--url` rather than manually extracting the token and type from the URL; this is especially true for Wiki URLs, where the CLI will automatically unwrap to the underlying resource
- `--url` and `--token` are mutually exclusive
- A bare `--token` requires passing `--doc-type`; a bare Wiki node token uses `--doc-type wiki`
- `doc` supports export as `docx` / `pdf`
- `docx` supports export as `docx` / `pdf` / `markdown`
- `sheet` supports export as `xlsx` / `csv`
- `bitable` supports export as `xlsx` / `csv` / `base`
- `slides` supports export as `pptx` / `pdf`
- `csv` only supports `sheet` / `bitable`, and must include `--sub-id`
- `--only-schema` only supports exporting `bitable` as `.base`, used to export only the table structure
- If the format does not match, the CLI will return a typed validation error and provide a retryable `--file-extension` suggestion in `hint`; for example, `docx + csv` will prompt to switch to `docx/pdf/markdown`, or to pass a sheet/bitable URL instead
- The shortcut has fixed built-in limited polling: at most 10 times, with an interval of 5 seconds each time
- Receiving `rate_limit` / `99991400` when creating an export task will not generate `ticket`; wait at least 1 minute before rerunning the original `drive +export`, and for persistent rate limiting, start exponential backoff from 1 minute
- Once status polling receives `rate_limit` / `99991400`, it will stop immediately and will not continue consuming the remaining polling attempts; the error will retain the original typed metadata and provide a continuation command for the existing `ticket` in `hint`
- Polling timeout is not a failure; it will return `ticket`, `timed_out=true`, and `next_command` for subsequent continued queries

<a id="错误码处理"></a>
## Error Code Handling

| Error Code | Meaning | Handling |
|--------|------|----------|
| `1069914` | The token is invalid or the token/type does not match; a common cause is using a Wiki node token as an underlying `docx` / `sheet` / `bitable` token without passing `--doc-type wiki` | Prefer switching to `--url <Wiki URL>`; when you only have a bare Wiki token, use `--token <WIKI_NODE_TOKEN> --doc-type wiki`. If you are unsure of the token type, first use `lark-cli drive +inspect --url <TOKEN> --type wiki` to check whether it can be unwrapped as a Wiki node; if it is not a Wiki token, then check the token source and whether `--doc-type` matches the actual resource type |
| `1069902` | No permission for the current export task | Do not directly retry the same command; first confirm whether the current `--as` identity can access the document, whether it has download/export permission, and whether the document is restricted by sharing, confidentiality level, or tenant policy. If permissions need to be added, have the document owner or administrator grant authorization before executing |
| `99991400` / `rate_limit` | OpenAPI request rate limited | Stop immediately and handle according to the error `hint`: if there is no `ticket`, wait at least 1 minute before rerunning the original `drive +export`; if there is already an `ticket`, only execute the `drive +task_result --scenario export` continuation query, and do not repeatedly create tasks. For persistent rate limiting, start exponential backoff from 1 minute |
| `9499` + `too many request(s)` | Another rate-limiting response for the export task API; the same `9499` may also indicate a parameter type error in other Drive APIs, and the CLI will distinguish based on the server message | Handle according to `rate_limit`: stop immediately, wait at least 1 minute, and use exponential backoff; if there is already an `ticket`, only continue querying that task, and do not recreate it |
| `99991679` | Missing OpenAPI scope | Complete authorization according to `missing_scopes` / `required_scope` / `hint` in the error envelope; a common approach is to re-execute `lark-cli auth login --scope "<缺失 scope>"`. Do not repeatedly retry the export command before adding the scope |

<a id="推荐续跑方式"></a>
## Recommended Continuation Approach

```bash
# Step 1: First try to export directly
lark-cli drive +export \
  --url "<DOCX_URL>" \
  --file-extension pdf \
  --file-name "weekly-report.pdf"

# If ready=false / timed_out=true is returned, continue querying
lark-cli drive +task_result \
  --scenario export \
  --ticket "<TICKET>" \
  --file-token "<DOCX_TOKEN>"

# After finding file_token, download it
lark-cli drive +export-download \
  --file-token "<EXPORTED_FILE_TOKEN>" \
  --file-name "weekly-report.pdf" \
  --output-dir ./exports
```

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for Drive (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
