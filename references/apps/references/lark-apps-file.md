<a id="apps-file-域命令应用存储"></a>
# apps file domain commands (app storage)

Manage file storage for Miaoda apps: upload / download local files, list and view stored files, generate temporary share links, batch delete, and view usage. For runtime command facts, `lark-cli apps +<cmd> --help` is authoritative; for authentication, `--as user`, exit codes, `_notice`, and other common handling, see [`../../shared/index.md`](../../shared/index.md) and this domain's [`index.md`](../index.md).

<a id="何时用"></a>
## When to use

When the user wants to upload / download / list / delete files in a Miaoda app, get a temporary share link for a file, or check storage usage. Regular Feishu Drive goes through [`lark-drive`](../../drive/index.md); table data in a database goes through `+db-*`.

<a id="命令一览"></a>
## Command overview

| Command | What it does | Key parameters |
|---|---|---|
| `+file-list` | List files, filterable by name/path/type/size/upload time | `--app-id`, filters, `--page-size`/`--page-token` |
| `+file-get` | Get metadata for a single file | `--app-id`, `--path` |
| `+file-sign` | Generate a time-limited download link (for sharing / direct download) | `--app-id`, `--path`, `--expires-in` |
| `+file-download` | Save a remote file locally | `--app-id`, `--path`, `--output` |
| `+file-upload` | Upload a local file to app storage | `--app-id`, `--file` |
| `+file-delete` | Batch delete files by path | `--app-id`, `--path` (repeatable), `--yes` |
| `+file-quota-get` | Check an app's file storage usage | `--app-id` |

<a id="寻址与约定先读"></a>
## Addressing and conventions (read first)

- **Remote files are always addressed precisely by `--path`** (remote path, with a leading `/`). When you only know the file name, first use `+file-list --name <名>` to locate it and get the `path`, then perform subsequent operations.
- **Local files / output paths use relative paths within the working directory** (such as `--file ./report.pdf`, `--output ./out.png`); if the path is elsewhere, first `cd` over there or change it to a relative path.
- Upload only accepts local `--file`: the file name follows the local file name, and the remote path is assigned by the platform and is globally unique (no need and no way to fill it in manually).
- The file domain does not distinguish environments and has no `--env`.

<a id="各命令"></a>
## Commands

### +file-list
List app files, with support for exact filtering: `--name` (file name), `--path` (remote path), `--type` (MIME type), `--size-gt`/`--size-lt` (bytes), `--uploaded-since`/`--uploaded-until` (upload time range; time format is at the end). Pagination `--page-size` (default 20, range 1..200) / `--page-token`. Each list item gives name, path, size, type, and upload time (the pretty table is exactly these 5 columns); uploader and download address (if any) appear only in JSON output, and single-file details use `+file-get`.

```bash
lark-cli apps +file-list --app-id app_xxx
lark-cli apps +file-list --app-id app_xxx --type image/png --uploaded-since 7d
```

### +file-get
Get metadata for a single file by `--path`. When the path does not exist, returns a clear "file does not exist" error.

```bash
lark-cli apps +file-get --app-id app_xxx --path /1858537546760216.png
```

### +file-sign
Generate a **time-limited download link** for the specified file—suitable for sending to users to share, or for direct download. `--expires-in` sets the validity period in seconds (default 1 day, maximum 30 days). `pretty` mode outputs only the link itself, making it easy to copy / pipe; when you need to tell the user the expiration time as well, use the default JSON output (which includes the expiration time).

```bash
lark-cli apps +file-sign --app-id app_xxx --path /1858537546760216.png --expires-in 3600
```

### +file-download
Save a remote file locally. `--output` specifies the save path; when omitted, it is saved to the current directory using the remote file name.

```bash
lark-cli apps +file-download --app-id app_xxx --path /1858537546760216.png --output ./logo.png
```

### +file-upload
Upload a local file. The file name follows the local file name (special characters are passed through with URL encoding; hidden file names starting with `.` get a `_` prefix to avoid overwriting hidden files when downloading back locally), and the remote path is assigned by the platform. The single-file limit is 100 MB.

```bash
lark-cli apps +file-upload --app-id app_xxx --file ./report.pdf
```

<a id="file-delete高危"></a>
### +file-delete (high risk)
Batch delete by path; `--path` can be passed repeatedly for multiple paths. Deletion is a high-risk operation and must include `--yes`; if omitted, it will be stopped by the confirmation checkpoint. **Results are returned item by item**: if some files fail to delete (for example, a path does not exist), it does not affect the remaining files, and the overall operation is still considered successful; failed items are marked separately in the results with the reason.

```bash
lark-cli apps +file-delete --app-id app_xxx --path /1858537546760216.png --yes
lark-cli apps +file-delete --app-id app_xxx --path /a.png --path /b.png --yes
```

### +file-quota-get
Check an app's file storage usage (used amount, file count; once quota integration is in place, it will also provide total quota and usage rate).

```bash
lark-cli apps +file-quota-get --app-id app_xxx
```

<a id="时间格式--uploaded-since----uploaded-until"></a>
## Time format (`--uploaded-since` / `--uploaded-until`)

Just pass it in naturally as the user speaks; the following are supported:
- Relative time `7d` / `2h` / `30s` (counting backward from now)
- Date `2026-04-15`
- Date-time `2026-04-15T10:00:00`
- ISO 8601 with time zone `2026-04-15T10:00:00Z` / `2026-04-15T10:00:00+08:00`

> **Time zone**: `日期` / `日期时间` without a time zone are parsed according to the **local time zone of the machine running it** (then normalized to UTC before being sent to the server). Running the same command in CI (UTC) and locally (such as UTC+8) will differ by a few hours at the filter boundary; when you need precision for a specific time zone, explicitly write ISO 8601 with an offset (such as `...+08:00` / `...Z`).

<a id="agent-规则"></a>
## Agent rules

- Always use `--path` for addressing; when the user gives only a file name, first use `+file-list --name <名>` to locate it, and if there are multiple files with the same name, ask the user to confirm.
- Use relative paths within the working directory for local upload / download paths; if not in the current directory, `cd` over there or change it to a relative path.
- When the user wants a "share link / temporary download address", use `+file-sign` and relay the returned link to the user.
- Before deleting, determine intent: if it is already clear what to delete and authorization is given, you can directly include `--yes`; if you are unsure what to delete, first use `+file-list` to get user confirmation. Partial failures in batch deletion do not raise an error; explain to the user item by item which succeeded, which were not deleted, and why.
