
# drive +export-download


Download a local file based on the `file_token` of the export task output. Usually used together with `drive +task_result --scenario export`.

<a id="命令"></a>
## Command

```bash
# Download to the current directory using the filename returned by the server
lark-cli drive +export-download \
  --file-token "<EXPORTED_FILE_TOKEN>"

# Download to the specified directory
lark-cli drive +export-download \
  --file-token "<EXPORTED_FILE_TOKEN>" \
  --output-dir ./exports

# Specify the local filename
lark-cli drive +export-download \
  --file-token "<EXPORTED_FILE_TOKEN>" \
  --file-name "weekly-report.pdf" \
  --output-dir ./exports

# Allow overwrite
lark-cli drive +export-download \
  --file-token "<EXPORTED_FILE_TOKEN>" \
  --overwrite
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | The output token after export completes |
| `--file-name` | No | Override the default filename |
| `--output-dir` | No | Local output directory, defaults to the current directory |
| `--overwrite` | No | Overwrite existing files |

<a id="使用顺序"></a>
## Usage Order

1. Use `drive +export` to initiate the export
2. If `ticket` / `next_command` is returned, use `drive +task_result --scenario export --ticket <ticket> --file-token <source_token>` to continue checking
3. After `file_token` is found, use `drive +export-download` to download

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- All commands for Drive (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
