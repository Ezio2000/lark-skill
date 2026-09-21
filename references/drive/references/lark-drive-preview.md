## `drive +preview`


View or download Drive file content, or list and retrieve available preview artifacts for a file. The object is a Drive **file**, and Wiki URLs / node tokens are also supported (the CLI first resolves the Wiki node to the underlying file, and `obj_type` must be `file`). This shortcut does not guess a default type:

- If you only need to view or download file content, or do not care about conversion previews such as PDF/text/image, prefer `--type source_file --output <path>`
- If you only want to see the candidates, use `--list-only`
- If you need a server-generated preview, such as the PDF layout preview of a doc/docx, first use `--list-only` to view the candidates, then choose `--type pdf` / `text` / `image` etc. according to the candidates
- If you want to download, you must explicitly pass `--type` and `--output`
- If `--list-only` has no available preview candidates, or the error message explicitly suggests using `--type source_file`, you can switch to `--type source_file --output <path>` to view the file content; terminal errors such as a nonexistent resource or invalid token require fixing the input first
- If a candidate is still being generated, a structured error is returned and prompts you to re-run `--list-only` first

<a id="命令"></a>
### Command

```bash
# View file content
lark-cli drive +preview \
  --file-token "<FILE_TOKEN>" \
  --type source_file \
  --output ./artifacts/source

# Recommended: pass the URL directly; the CLI automatically resolves the type and token
lark-cli drive +preview \
  --url "https://example.feishu.cn/file/<FILE_TOKEN>" \
  --list-only

# A Wiki URL can also be passed directly; the CLI first resolves it to the underlying obj_token/obj_type (obj_type must be file)
lark-cli drive +preview \
  --url "https://example.feishu.cn/wiki/<WIKI_NODE_TOKEN>" \
  --type source_file \
  --output ./artifacts/source

# When you only have a bare Wiki node token, explicitly pass --wiki-token
lark-cli drive +preview \
  --wiki-token "<WIKI_NODE_TOKEN>" \
  --list-only

# List available preview candidates
lark-cli drive +preview \
  --file-token "<FILE_TOKEN>" \
  --list-only

# Download the PDF preview
lark-cli drive +preview \
  --file-token "<FILE_TOKEN>" \
  --type pdf \
  --output ./artifacts/report

# Download the text preview, and automatically rename if the target already exists
lark-cli drive +preview \
  --file-token "<FILE_TOKEN>" \
  --type text \
  --output ./artifacts/report \
  --if-exists rename

# Query/download by specifying a version number
lark-cli drive +preview \
  --file-token "<FILE_TOKEN>" \
  --version "12" \
  --type html \
  --output ./artifacts/report.html
```

<a id="参数"></a>
### Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Conditionally required | Drive file token; choose one of three with `--url` / `--wiki-token` |
| `--url` | Conditionally required | Feishu file URL or Wiki URL; the CLI automatically resolves the type and token |
| `--wiki-token` | Conditionally required | Bare Wiki node token; the CLI first resolves it to the underlying Drive file |
| `--type` | Conditionally required | Preview type; prefer the `type` returned by `--list-only`, such as `pdf` / `html` / `text` / `png` / `jpg` / `source_file` |
| `--version` | No | File version number |
| `--list-only` | No | Only return candidates, do not download |
| `--output` | Conditionally required | Local output path for the download |
| `--if-exists` | No | Output conflict policy: `error` (default) / `overwrite` / `rename` |

<a id="输出约定"></a>
### Output conventions

- Query mode returns:
  - `mode=list`
  - `file_token`
  - `candidates[]`
  - `next_action`
- Download mode returns:
  - `mode=download`
  - `file_token`
  - `selected_type`
  - `output_path`
  - `status`

<a id="候选项字段"></a>
### Candidate fields

Each object in `candidates[]` contains:

- `type`
- `type_code`
- `label`
- `status`
- `status_code`
- `downloadable`
- `reason` (optional)

<a id="关键约束"></a>
### Key constraints

- When `--list-only` is not passed, you must explicitly pass `--type` and `--output`
- It will not implicitly select the "first candidate" as the default download target
- `--type source_file` is used to view file content and does not depend on the candidates returned by `--list-only`; it is suitable for reading or saving the source content and is not equivalent to conversion previews such as PDF/text/image
- Candidate status comes from the backend `preview_status` enum, such as `READY` / `PROCESSING` / `FAILED` / `NO_SUPPORT`
- When no extension is explicitly provided, the local file name will automatically have an extension appended based on the response headers
- A Wiki URL / bare Wiki node token is first resolved to the underlying document, and after resolution the output includes `wiki_token` and `wiki_node` (including the underlying `obj_token`/`obj_type`); `obj_type` must be `file`. If the Wiki points to an online document such as `docx` / `sheet` / `bitable` / `slides`, `+preview` cannot handle it directly, and the CLI returns a typed validation error and hints in the hint to use [lark-drive-export](lark-drive-export.md)

<a id="参考"></a>
### References

- [lark-drive](../index.md) -- Drive main entry point
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
