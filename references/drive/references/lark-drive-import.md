# drive +import


Import local files (such as Word, TXT, Markdown, Excel, PPTX, etc.) and convert them into Feishu online cloud documents (docx, sheet, bitable, slides). Under the hood, it uniformly creates an import task through the `POST /open-apis/drive/v1/import_tasks` API, and performs a limited number of polls of `GET /open-apis/drive/v1/import_tasks/:ticket` within the shortcut.

> [!IMPORTANT]
> When the user says "import a local Excel / CSV / `.base` snapshot into a Base / Bitable / bitable document", the first step must use `drive +import --type bitable`.
> This is a Drive import scenario, not the table creation / record writing scenario of `lark-base`.
> Only after the import completes and you obtain the new document's `token` / `url` do subsequent in-table operations such as fields, records, and views switch to `lark-cli base +...`.

<a id="导入后标题确认"></a>
## Title confirmation after import

> [!IMPORTANT]
> When the user **does not pass `--name`**, the document title defaults to the source file name (with the extension removed). Before executing the import, first give the user a friendly prompt: "No document title is currently specified, so 'xxx' will be used as the title by default. If the file content also contains the same title, it may cause visual duplication after import. Do you want to rename it?" Let the user confirm before continuing.

<a id="批量导入串行规则"></a>
## Serial rules for batch import

> [!IMPORTANT]
> When executing `drive +import` in batch and the target is the same location, execution must be serial; do not initiate import tasks concurrently. Here, "same location" includes the same `--folder-token`, omitting `--folder-token` for all to import into the default root directory, or using the same `--target-token` to import into an existing bitable.
>
> If imports are concurrent under the same location, the server may return a concurrency conflict error. When you see an error message or `job_error_msg` contains any of the error codes `232140101`, `232140100`, `233523001`, handle it as a same-location concurrent operation: stop concurrent imports and switch to serial processing of the failed items; before each retry of each failed item, wait a few seconds, with a maximum of 3 retries in total; if it still fails, stop and report the conflict to the user.

<a id="命令"></a>
## Commands

```bash
# Import Word as a new-version document (docx)
lark-cli drive +import --file ./report.docx --type docx
lark-cli drive +import --file ./legacy.doc --type docx

# Import Markdown as a new-version document (docx)
lark-cli drive +import --file ./README.md --type docx

# Import plain text as a new-version document (docx)
lark-cli drive +import --file ./notes.txt --type docx

# Import HTML as a new-version document (docx)
lark-cli drive +import --file ./page.html --type docx

# Import Excel as a spreadsheet (sheet)
lark-cli drive +import --file ./data.xlsx --type sheet

# Import Excel 97-2003 (.xls) as a spreadsheet (sheet)
lark-cli drive +import --file ./legacy.xls --type sheet

# Import CSV as a spreadsheet (sheet)
lark-cli drive +import --file ./data.csv --type sheet

# Import Excel as a Bitable / Base (bitable)
lark-cli drive +import --file ./crm.xlsx --type bitable --name "客户台账"

# Import a .base snapshot as a Bitable / Base (bitable) (file must not exceed 20MB)
lark-cli drive +import --file ./snapshot.base --type bitable --name "快照还原"

# Import PPTX as Feishu Slides (slides) (file must not exceed 500MB)
lark-cli drive +import --file ./deck.pptx --type slides --name "项目汇报"

# Import to a specified folder, and specify the file name after import
lark-cli drive +import --file ./data.csv --type bitable --folder-token <FOLDER_TOKEN> --name "导入数据表"

# Import data into an existing Bitable (do not create a new one; data is mounted to the target Bitable)
lark-cli drive +import --file ./data.xlsx --type bitable --target-token <BASE_TOKEN>

# Preview the underlying call chain (upload -> create task -> poll)
lark-cli drive +import --file ./README.md --type docx --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file` | Yes | Local file path; `file_extension` is automatically inferred from the file extension; the file must satisfy the import size limit for the corresponding format, and when it exceeds 20MB but is still within the allowed range, it automatically switches to multipart upload |
| `--type` | Yes | Target cloud document format for import. Possible values: `docx` (new-version document), `sheet` (spreadsheet), `bitable` (Bitable), `slides` (Feishu Slides) |
| `--folder-token` | No | Target folder token; if not passed, `point.mount_key` in the request is an empty string, and the Import API interprets it as importing to the root directory of the cloud space (Drive/cloud storage) |
| `--name` | No | Name of the online cloud document after import; if not passed, the local file name with the extension removed is used by default |
| `--target-token` | No | Token of an existing Bitable, to import data into that Bitable (**only supports `--type bitable`**); once passed, data is mounted to the target Bitable instead of creating a new one |

<a id="行为说明"></a>
## Behavior description

- **Complete execution flow**: This shortcut encapsulates the complete flow internally:
  1. Automatically upload the source file to obtain `file_token`:
     - 20MB and below: call the material upload API `POST /open-apis/drive/v1/medias/upload_all`
     - Over 20MB: automatically switch to multipart upload `upload_prepare -> upload_part -> upload_finish`
  2. Call the `import_tasks` API to initiate the import task, automatically extracting the extension from the local file and constructing the mount point (`mount_point`) parameter
  3. Automatically poll to query the import task status; if it completes within the built-in polling window, return the import result directly; if it is still not complete, return `ticket`, the current status, and the follow-up query command
- **Default root directory behavior**: When `--folder-token` is not passed, the shortcut keeps `point.mount_key` empty, and the Lark Import API treats it as "import to the caller's root directory".
- **Import into an existing bitable**: When `--type bitable` and `--target-token` is passed, a `token` field is added to the request body pointing to the target Bitable's token, and the point mount logic remains unchanged. Data is mounted to that existing Bitable rather than creating a new document.

<a id="支持的文件类型转换"></a>
### Supported file type conversions

The correspondence between local file extensions and target cloud document types is as follows:

| Local file extension | Can be imported as | Description |
|--------------|---------|------|
| `.docx`, `.doc` | `docx` | Microsoft Word document |
| `.txt` | `docx` | Plain text file |
| `.md`, `.markdown`, `.mark` | `docx` | Markdown document |
| `.html` | `docx` | HTML document |
| `.xlsx` | `sheet`, `bitable` | Microsoft Excel spreadsheet |
| `.xls` | `sheet` | Microsoft Excel 97-2003 spreadsheet |
| `.csv` | `sheet`, `bitable` | CSV data file |
| `.base` | `bitable` | Bitable snapshot file |
| `.pptx` | `slides` | Microsoft PowerPoint presentation |

> [!IMPORTANT]
> When the user verbally says "Base" / "Bitable" / "bitable", in commands it uniformly corresponds to `--type bitable`.
>
> The file extension and target document type must match, otherwise a validation error is returned:
> - Document-type files (.docx, .doc, .txt, .md, .html) **can only** be imported as `docx`
> - `.xlsx` / `.csv` files **can only** be imported as `sheet` or `bitable`
> - `.xls` files **can only** be imported as `sheet`
> - `.base` files **can only** be imported as `bitable`
> - `.pptx` files **can only** be imported as `slides`
> - For example: a `.csv` file cannot be imported as `docx`, and a `.md` file cannot be imported as `sheet`

> [!IMPORTANT]
> If the online document is **imported and created with an app identity (bot)**, such as `lark-cli drive +import --as bot`, then once a certain result **has already returned the final online document target**, the CLI will **attempt to automatically grant the current CLI user `full_access` (manageable permission) for that resource**.
>
> This automatic authorization has two trigger timings:
> - It has already completed within the built-in polling window of `drive +import`, and automatic authorization is performed directly in `+import`
> - `drive +import` first returns `ready=false` / `timed_out=true`, and afterward you execute `lark-cli drive +task_result --scenario import --ticket <TICKET>`; when that query obtains the final online document target for the first time, authorization is performed automatically
>
> Only in the result where the final online document target has already been obtained will the `permission_grant` field be returned, clearly stating the authorization result:
> - `status = granted`: the current CLI user has obtained manageable permission for the import result
> - `status = skipped`: there is no available current user `open_id` locally, or the current result does not yet have an authorizable target, so automatic authorization will not be performed; you may prompt the user to complete `lark-cli auth login` first, then let the AI / agent continue to use the app identity (bot) to grant the current user permission
> - `status = failed`: the import has successfully returned the final online document, but automatically authorizing the user failed; the failure reason is included, and it prompts to retry later or continue handling the document using the bot identity
>
> `permission_grant.perm = full_access` indicates that the resource has been granted "manageable permission".
>
> **Do not arbitrarily perform owner transfer.** Creation or import does not imply owner transfer; when the user has explicitly requested a transfer and the target is determined, follow the authorization to execute it.

<a id="文件大小限制"></a>
### File size limits

In addition to matching the extension with the target type, `drive +import` also validates format-level size limits locally before upload:

| Local file extension | Import target | Size limit |
|--------------|---------|---------|
| `.docx`, `.doc` | `docx` | 600MB |
| `.txt` | `docx` | 20MB |
| `.md`, `.mark`, `.markdown` | `docx` | 20MB |
| `.html` | `docx` | 20MB |
| `.xlsx` | `sheet`, `bitable` | 800MB |
| `.csv` | `sheet` | 20MB |
| `.csv` | `bitable` | 100MB |
| `.xls` | `sheet` | 20MB |
| `.base` | `bitable` | 20MB |
| `.pptx` | `slides` | 500MB |

- If the file exceeds the corresponding limit, the shortcut directly returns a validation error before the actual upload.
- "Automatically switch to multipart upload when over 20MB" only means the upload path switches to multipart; it does not mean all formats allow importing files over 20MB.

- If the import task fails, it returns the `job_status` at the time of failure and the error message.
- If the import failure message contains `232140101`, `232140100`, `233523001`, it usually indicates concurrent import / creation operations under the same location; for batch scenarios, switch to serial execution, wait a few seconds before each retry of each failed item, with a maximum of 3 retries in total, and if it still fails, stop and report the conflict.
- If the built-in polling times out but the task is still processing, the shortcut returns successfully with:
  - `ready=false`
  - `timed_out=true`
  - `next_command`: a follow-up query command that can be copied and executed directly, for example `lark-cli drive +task_result --scenario import --ticket <TICKET>`
- If `--as bot` is used and the final online document has already been obtained within the built-in polling window, the output additionally includes `permission_grant`, used to indicate whether manageable permission has been automatically granted to the current CLI user.
- If `--as bot` is used but currently only `ready=false` is returned, then `permission_grant` is not yet returned; you should continue executing `next_command` from the returned value, and wait until `drive +task_result --scenario import` obtains the final document before triggering automatic authorization.
- If the file extension is not supported, a validation error is thrown during execution.

<a id="超时后的继续查询"></a>
### Continuing to query after timeout

When the built-in polling window of `+import` ends but the task is not yet complete, use `ticket` from the returned result to continue querying:

```bash
lark-cli drive +task_result --scenario import --ticket <TICKET>
```

If this eventually returns `ready=true` and `--as bot` is used, the result additionally includes `permission_grant`, used to indicate whether manageable permission has been automatically granted to the current CLI user.

> [!CAUTION]
> `drive +import` is a **write operation** -- user intent must be confirmed before execution.

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- all commands for the cloud space (Drive/cloud storage)
- [lark-shared](../../shared/index.md) -- authentication and global parameters
