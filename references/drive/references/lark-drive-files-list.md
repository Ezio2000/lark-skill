<a id="drive-files-list原生-api读取-drive-文件夹清单"></a>
# drive files list (native API: read Drive folder listing)

`drive files list` is a native API command, not a shortcut. It is used to read the direct children of the Drive root directory or a Drive folder; if you want to recursively inventory a directory tree, the Agent must continue calling this command based on the returned subfolder tokens.

<a id="什么时候使用"></a>
## When to use

| Scenario | Use | Description |
|------|----------|------|
| Inventory a confirmed Drive folder tree | Use | Recursively list starting from the target `folder_token` |
| Inventory a Drive root directory explicitly confirmed by the user | Use | Use an empty `folder_token` for the first level, and continue recursing into subfolders as normal folders |
| Verify the actual location after a move / create | Use | Read the direct children of the target directory, then recursively verify as needed |
| Find resources by keyword, title, time, or owner | Do not use | Prefer `drive +search` |
| Read Docx body content | Do not use | Use `docs +fetch` |
| Read internal Sheet / Base data | Do not use | Switch to `lark-sheets` / `lark-base` |

<a id="标准命令模板"></a>
## Standard command template

Read a normal folder:

```bash
lark-cli drive files list \
  --params '{"folder_token":"<folder_token>","page_size":200}' \
  --format json
```

Continue paginating:

```bash
lark-cli drive files list \
  --params '{"folder_token":"<folder_token>","page_size":200,"page_token":"<PAGE_TOKEN>"}' \
  --format json
```

Read the direct children of the current user's Drive root directory:

```bash
lark-cli drive files list \
  --params '{"folder_token":"","page_size":200}' \
  --format json
```

You can also omit the `folder_token` field to request the root directory, but in Agent orchestration it is recommended to explicitly pass an empty string, to avoid conflating "forgot to pass the parameter" with "confirmed request for the root directory".

<a id="按时间排序"></a>
## Sorting by time

By default, do not pass `order_by` / `direction`; the server returns results in the default order. Only when the user explicitly requests sorting by creation time or edit time should you use the server-side sorting parameters.

List the direct children of the current folder in ascending order by creation time:

```bash
lark-cli drive files list \
  --params '{"folder_token":"<folder_token>","order_by":"CreatedTime","direction":"ASC","page_size":200}' \
  --format json
```

List the direct children of the current folder in descending order by edit time:

```bash
lark-cli drive files list \
  --params '{"folder_token":"<folder_token>","order_by":"EditedTime","direction":"DESC","page_size":200}' \
  --format json
```

The above examples return the sorted current page; if `has_more=true` is returned, keep the same `folder_token` / `order_by` / `direction` / `page_size`, put `next_page_token` into `page_token` and continue paginating.

<a id="参数规则"></a>
## Parameter rules

1. `folder_token` must be placed in the `--params` JSON; do not use a nonexistent `--folder-token` flag.
2. `page_token` must be placed in the `--params` JSON; do not rely on shell variable concatenation to build incomplete JSON.
3. By default, do not pass `order_by` / `direction`; only use the server-side sorting parameters when the user explicitly requests sorting by creation time / edit time.
4. Sorting parameter mapping: creation time -> `order_by:"CreatedTime"`; edit time / modification time -> `order_by:"EditedTime"`; ascending -> `direction:"ASC"`; descending -> `direction:"DESC"`. Do not omit the sorting parameters and then substitute with Python / shell client-side sorting.
5. Sorted queries should include `page_size:200` to reduce pagination; only add `page_token` when the user requests complete pagination, recursive inventory, full export of a large directory, or continuing pagination after the current page returns `has_more=true`.
6. `page_size` should be explicitly set to `200` during pagination, recursive inventory, or full export. If the server or environment returns a parameter error, then downgrade to a value allowed by the server, and record the reason for the downgrade.
7. Before calling, if you are unsure of the field structure, first run `lark-cli schema drive.files.list` to inspect the `--params` structure.

<a id="返回结构与解析"></a>
## Return structure and parsing

In the `--format json` output, the Agent only uses the API return fields in `data` that match `schema drive.files.list`.

Common fields:

| Field | Purpose |
|------|------|
| `data.files` | List of direct children on the current page |
| `data.has_more` | Whether the current directory has a next page |
| `data.next_page_token` | Next page token; when `has_more=true`, put it back into `--params.page_token` |
| `data.files[].type` | File type; when equal to `folder`, it can be recursed into |
| `data.files[].token` | Current resource token; used as the next level's `folder_token` when recursing into folders |
| `data.files[].name` | Generate paths and display titles |
| `data.files[].url` | Resource browser link |
| `data.files[].owner_id` | Resource owner |
| `data.files[].created_time` / `data.files[].modified_time` | Creation / update time |

Field names are based on `schema drive.files.list`. The Agent MUST rely on the actual return; if a field is missing, first confirm the structure with `schema drive.files.list` or a one-page sample, do not guess.

<a id="根目录语义"></a>
## Root directory semantics

1. When `folder_token` is an empty string or omitted, the request is for the direct children of the current calling user's Drive root directory.
2. The root directory return value is not a recursive result; you cannot treat the first page of the root directory or the number of direct children as the total amount of resources in the entire cloud space.
3. The root directory only serves as the starting point of the directory tree. Returned subfolders must continue to be called with `drive files list` using their own `folder_token`.
4. According to the schema description, the first-level listing of the root directory does not support pagination and does not return shortcuts; do not infer subfolder contents, first-level root directory shortcuts, or that the remaining non-paginable root directory items have already been covered based on the root directory response.

<a id="递归盘点规则"></a>
## Recursive inventory rules

1. Only continue recursing into returned items of type `folder`.
2. Each directory maintains its own pagination state independently; one directory's `page_token` cannot be reused for other directories.
3. Keep requesting for each directory until `has_more=false` is returned. Listings of normal non-root folders may return `type=shortcut` entries; do not assume these entries carry `shortcut_info` target information.
4. Generate a stable `path` during recursion; do not save only titles, otherwise resources with the same name cannot be distinguished.
5. For URL, owner, creation time, and update time, prefer the fields returned by `files.list`; if fields are missing or need to be batch-filled, then use `drive metas batch_query`. Do not guess metadata from titles or paths.
6. Limits such as depth, count, and pages per directory can only serve as internal batch checkpoints; they cannot serve as recursion completion conditions.
7. When a depth checkpoint is reached, add deeper subfolders to the continuation queue, and continue from these subfolders in the next batch, preserving the original `path`.
8. When a count checkpoint is reached, save the current directory, current page token, remaining directory queue, and collected resource count, and immediately continue to the next batch; do not enter the analysis or planning phase.

<a id="递归算法"></a>
### Recursive algorithm

When the Agent inventories a Drive folder tree, execute in the following order:

1. Initialize the pending queue and put in the starting directory:
   - Normal folder: `{folder_token:"<folder_token>", path:"<folder_name>"}`
   - Drive root directory: `{folder_token:"", path:""}`
2. Take a directory from the queue and request the first page.
3. Use `(folder_token, page_token)` to generate the current page key; the same page key may only be appended once, to avoid double counting on retry.
4. Take the direct children of the current page from `data.files`, deduplicate by `dedupe_key`, then generate `path` and add it to the result set.
5. If the newly appended child is `folder`, add the subfolder token, subpath, and depth to the queue.
6. If `has_more=true`, take `data.next_page_token` and continue requesting the next page of the same directory.
7. After pagination for the same directory ends, then process the next directory in the queue.
8. If a depth, count, or pages-per-directory checkpoint is reached, write the current directory / page token / remaining queue / visited page keys / dedupe keys into the continuation queue, and continue to the next batch.
9. Only when both the normal queue and the continuation queue are empty, and there is no pagination blocker, can the inventory of this confirmed scope be considered complete.

Simplified pseudocode:

```text
queue = [root_or_start_folder]
visited_pages = set()
dedupe_keys = set()
while queue not empty:
  folder = queue.pop()
  page_token = folder.page_token or ""
  retry_without_token = 0
  while true:
    page_key = (folder.folder_token, page_token or "first")
    page = drive files list(folder.folder_token, page_token)
    if page_key not in visited_pages:
      append only files whose dedupe_key is not in dedupe_keys
      enqueue newly appended child folders with folder_token, path, and depth
      add page_key to visited_pages
    if page.has_more != true:
      break
    next = page.next_page_token
    if next is empty:
      retry_without_token += 1
      if retry_without_token >= 3:
        record pagination blocker for folder
        break
      continue
    page_token = next
    retry_without_token = 0
```

<a id="分页与异常"></a>
## Pagination and exceptions

1. By default, manually handle `has_more` and the `next_page_token` in the return.
2. Do not use `--page-all` as script JSON parsing input; automatic pagination output may not be suitable for direct `json.loads`.
3. If `has_more=true` but there is no usable `next_page_token`, retry the same page at most 3 times.
4. If there is still no continuation token after retrying, record the affected directory and pagination blocker, stop expanding that directory; do not loop infinitely, and do not claim that the directory has been fully covered.
5. If a depth, count, or pages-per-directory limit is triggered, treat it as a batch checkpoint; continue to the next batch within the confirmed scope, rather than describing the current results as complete.
6. Do not end the inventory just because `max_depth=3`, `max_items=500`, or a similar single-batch threshold is reached; only when the queue is exhausted or a permission / API / tool budget blocker is encountered can the inventory of the current confirmed scope end.

<a id="json-解析规则"></a>
## JSON parsing rules

1. stdout is the data channel. When a script parses JSON, only read stdout.
2. stderr may contain refresh tokens, progress, warnings, or other prompts; do not merge stderr into the JSON input, for example do not use `2>&1` followed by `json.loads`.
3. Use `--format json` to keep stdout as structured JSON; when parsing the Drive file listing, only read schema fields such as `data.files` / `data.has_more` / `data.next_page_token`.
4. Do not infer the recursive total from the root directory response count or the current page count; the recursive total must be calculated from the actually traversed and deduplicated resource set.

<a id="常见错误"></a>
## Common mistakes

| Incorrect usage | Problem | Correct approach |
|----------|------|----------|
| `lark-cli drive files list --folder-token <token>` | `files.list` does not provide the `--folder-token` flag | Use `--params '{"folder_token":"<token>"}'` |
| Assuming the cloud space only has N items because the root directory returns N items | The root directory only returns direct children, not recursive results | Continue recursing into the returned subfolders |
| `--page-all \| python json.loads(...)` | Automatic pagination output is not suitable for parsing as a single JSON object | Manually use `page_token` to paginate and parse page by page |
| Parsing JSON after `cmd 2>&1` | stderr prompts pollute the JSON input | Only parse stdout, and treat stderr as logs |
