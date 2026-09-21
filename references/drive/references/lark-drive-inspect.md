
<a id="drive-inspect文档-url-检视类型标题token-解析"></a>
# drive +inspect (document URL inspection: type, title, token resolution)


Given a Feishu document URL or bare token, return its type, title, and canonical token. For wiki URLs, automatically unwrap to the underlying document.

<a id="命令"></a>
## Command

```bash
# Inspect a docx URL
lark-cli drive +inspect --url 'https://xxx.feishu.cn/docx/doxcnXXX'

# Inspect a wiki URL (automatically unwrap to the underlying document)
lark-cli drive +inspect --url 'https://xxx.feishu.cn/wiki/wikcnXXX'

# A bare token requires specifying --type
lark-cli drive +inspect --url doxcnXXX --type docx

# Formatted output
lark-cli drive +inspect --url 'https://xxx.feishu.cn/base/bascnXXX' --format pretty
```

<a id="输出"></a>
## Output

The JSON output contains the following fields:

| Field | Description |
|------|------|
| `input_url` | Original input URL |
| `type` | Document type (docx, doc, sheet, bitable, wiki, file, folder, mindnote, slides) |
| `title` | Document title |
| `token` | canonical file token |
| `url` | Reconstructed canonical URL |
| `wiki_node` | Wiki URLs only: contains `space_id`, `node_token`, `obj_token`, `obj_type` |

<a id="典型场景"></a>
## Typical scenarios

| Scenario | Command |
|------|------|
| The user provided a URL and wants to know what type of document it is | `lark-cli drive +inspect --url '<url>'` |
| A wiki link needs the underlying document's token for subsequent operations | `lark-cli drive +inspect --url '<wiki_url>'`, take `token` from the output |
| Only a token is available, no URL | `lark-cli drive +inspect --url <token> --type <type>` |

<a id="注意事项"></a>
## Notes

- `--url` is a required parameter
- When `--url` is a bare token (not a full URL), `--type` is also required
- A wiki URL automatically calls the `node_by_token` API to unwrap; in the output, `type` and `token` are the underlying document's type and token
- `+inspect` is only used for identification/disambiguation; if the task can already determine routing based on the URL path form, there is no need to use it as a general prerequisite step for all Drive operations
- After `+inspect` fails, do not automatically switch to a write interface to keep trying; first handle the permission, scope, or link issue according to the error message
- Supports `--dry-run` to view the API steps that will be called
