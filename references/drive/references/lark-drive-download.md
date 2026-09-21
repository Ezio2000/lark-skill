
# drive +download


Download files from Feishu Drive (cloud drive/cloud storage) to local. The download targets are Drive **files** (uploaded PDF/zip/image/audio/video files, etc.), and Wiki URL / Wiki token are also supported.

<a id="命令"></a>
## Command

```bash
# Download to a specified path
lark-cli drive +download --file-token boxbc_xxx --output ./report.pdf

# Provide only the token; by default saves to the current directory
lark-cli drive +download --file-token boxbc_xxx

# Pass the URL directly; the CLI automatically parses the type and token
lark-cli drive +download --url "https://example.feishu.cn/file/<FILE_TOKEN>" --output ./report.pdf

# A Wiki URL can also be passed directly; the CLI will first resolve it to the underlying obj_token/obj_type (obj_type must be file)
lark-cli drive +download --url "https://example.feishu.cn/wiki/<WIKI_NODE_TOKEN>" --output ./report.pdf

# When you only have a bare Wiki node token, explicitly pass --wiki-token to let the CLI first resolve the underlying file
lark-cli drive +download --wiki-token "<WIKI_NODE_TOKEN>" --output ./report.pdf
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Conditionally required | Drive file token; choose one of three with `--url` / `--wiki-token` |
| `--url` | Conditionally required | Feishu file URL or Wiki URL; the CLI automatically parses the type and token |
| `--wiki-token` | Conditionally required | Bare Wiki node token; the CLI first resolves it to the underlying Drive file |
| `--output` | No | Local output path; if not passed, saves to the current directory by default |
| `--overwrite` | No | Overwrite an existing output file; if not passed, an error is reported when the target already exists |

<a id="url-解析"></a>
## URL Parsing

Extract the token from a Feishu file URL:

```
https://xxx.feishu.cn/drive/file/boxbc_xxx
                                  ^^^^^^^^^
                                  file_token
```

A Wiki URL / bare Wiki node token is first resolved to the underlying document, and after resolution the output includes `wiki_token` and `wiki_node` (including the underlying `obj_token`/`obj_type`).

<a id="关键约束"></a>
## Key Constraints

- After a Wiki node is resolved, `obj_type` must be `file`; when unsure of the token type, first check with `lark-cli drive +inspect --url <TOKEN> --type wiki`.

<a id="排障"></a>
## Troubleshooting

- If `permission_denied` is returned, or the final download returns `HTTP 403`, use `lark-cli drive +preview --file-token <FILE_TOKEN> --type source_file --output <path>` according to the error `hint` to obtain the preview artifact.
- If a rate limit error is returned, stop retrying immediately and retry later with exponential backoff.
- If the target (or the underlying document resolved from the Wiki) is an online document such as `docx` / `sheet` / `bitable` / `slides`, `+download` cannot download it directly and will return a typed validation error; instead use [lark-drive-export](lark-drive-export.md) to render it into pdf / xlsx / pptx / markdown and other formats.

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for Drive (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
