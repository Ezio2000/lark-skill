<a id="drive-secure-label-list--secure-label-update云文档密级标签"></a>
# drive +secure-label-list / +secure-label-update (Drive secure labels)

<a id="何时使用"></a>
## When to use

- `drive +secure-label-list`: Query the secure labels available to the current user, and first obtain the target `id`.
- `drive +secure-label-update`: Adjust the target Drive document to a specified secure label.

Both shortcuts use user identity (`--as user`). Before modifying the secure label, usually run `+secure-label-list` first to confirm the available label ID.

<a id="查询可用密级标签"></a>
## Query available secure labels

```bash
lark-cli drive +secure-label-list --page-size 10 --lang zh
```

Optional parameters:

| Parameter | Description |
|------|------|
| `--page-size` | Page size, range `1..10`, default `10` |
| `--page-token` | `page_token` from the previous page response |
| `--lang` | Label language: `zh`, `en`, `ja` |

Underlying API: `GET /open-apis/drive/v2/my_secure_labels`.

<a id="修改文档密级"></a>
## Modify document secure label

```bash
lark-cli drive +secure-label-update \
  --token "https://example.feishu.cn/docx/doxcnxxxx" \
  --label-id '<label-id>' # replace $LABEL_ID before running
```

Parameters:

| Parameter | Description |
|------|------|
| `--token` | Target document URL or bare token; the URL can automatically infer `--type` |
| `--type` | Required for bare token; can be omitted when the input is a URL. Optional: `doc`, `docx`, `sheet`, `file`, `bitable`, `mindnote`, `slides` |
| `--label-id` | Secure label ID to set |

Underlying API: `PATCH /open-apis/drive/v2/files/:file_token/secure_label`, query parameter `type`, request body `{ "id": "<label-id>" }`.

<a id="错误处理"></a>
## Error handling

The CLI does not append a dedicated hint for secure label error codes in the shortcut; the agent must provide the following guidance based on the returned `error.code`.

| Error code | Meaning | Guidance |
|--------|------|------|
| `1063013` | Secure label downgrade requires approval | Prompt the user to open the target document and complete the secure label downgrade approval in the document interface, then retry; if the user passed in a document URL, that URL must also be given to the user as the entry point for the operation |

When encountering `1063013`, do not continue retrying the API, and do not prompt to add scopes; this is a document-side approval process requirement, and the user needs to perform the operation in the document.
