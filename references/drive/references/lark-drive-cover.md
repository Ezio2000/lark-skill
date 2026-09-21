## `drive +cover`


List or download stable cover presets for Drive files. This shortcut only exposes `spec`, and does not expose underlying `cover_option` details.

<a id="命令"></a>
### Command

```bash
# List built-in cover specs
lark-cli drive +cover \
  --file-token "<FILE_TOKEN>" \
  --list-only

# Download square spec cover
lark-cli drive +cover \
  --file-token "<FILE_TOKEN>" \
  --spec square \
  --output ./artifacts/report-cover

# Download the default large cover, and overwrite on file conflict
lark-cli drive +cover \
  --file-token "<FILE_TOKEN>" \
  --spec default \
  --output ./artifacts/report-cover.png \
  --if-exists overwrite
```

<a id="参数"></a>
### Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | Drive file token |
| `--spec` | Conditionally required | Cover preset: `default` / `icon` / `grid` / `small` / `middle` / `big` / `square` |
| `--version` | No | File version number |
| `--list-only` | No | Only return available specs, do not download |
| `--output` | Conditionally required | Local output path for download |
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
  - `selected_spec`
  - `output_path`
  - `status`

<a id="内置规格"></a>
### Built-in specs

- `default` -- Standard large cover
- `icon` -- List small icon
- `grid` -- Grid/card feed small cover
- `small` -- PC small image
- `middle` -- Medium-sized cover
- `big` -- Large cover leaning toward mobile
- `square` -- Square cropped cover

<a id="关键约束"></a>
### Key constraints

- When `--list-only` is not passed, `--spec` and `--output` must be passed explicitly
- `drive +cover` only returns static preset specs, and does not fabricate a backend "downloadable status"
- Does not return underlying implementation details such as `bus_type` / `platform` / `width` / `height` / `policy`
- When downloading, directly call `preview_download`
- When no extension is explicitly provided, it will first supplement the extension based on the response header, and fall back to `.png` when missing

<a id="错误提示"></a>
### Error prompts

- If downloading a certain `--spec` returns **HTTP 404**, it means this file **has no cover artifact corresponding to that spec**, and should be treated as "that spec is unavailable", rather than by default handling it as network jitter or a temporary failure

<a id="参考"></a>
### References

- [lark-drive](../index.md) -- Drive main entry
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
