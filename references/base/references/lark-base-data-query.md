
# Base data-query DSL reference

> **Prerequisite routing**: [Record query and analysis SOP](lark-base-record-query-and-analysis-sop.md) | **Authentication or authorization issues**: [`../../shared/index.md`](../../shared/index.md)

<a id="限制"></a>
## Limitations

- **Permission requirements** (routed by document type):
  - **Standard Base**: the caller only needs **read permission** on the document
  - **Advanced-permission Base**: the caller must be a document admin with **FA (Full Access)**

  When permissions are insufficient, a permission error is returned.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Group by field and count
lark-cli base +data-query \
  --base-token MAGObxxxxx \
  --dsl '{
    "datasource": {"type": "table", "table": {"tableId": "tblxxxxxxxx"}},
    "dimensions": [{"field_name": "城市", "alias": "dim_city"}],
    "measures": [{"field_name": "城市", "aggregation": "count", "alias": "count"}],
    "shaper": {"format": "flat"}
  }'

# With filter conditions + sort + limit count
lark-cli base +data-query \
  --base-token MAGObxxxxx \
  --dsl '{
    "datasource": {"type": "table", "table": {"tableId": "tblxxxxxxxx"}},
    "dimensions": [{"field_name": "城市", "alias": "dim_city"}],
    "measures": [{"field_name": "金额", "aggregation": "sum", "alias": "total_amount"}],
    "filters": {
      "type": 1,
      "conjunction": "and",
      "conditions": [{"field_name": "城市", "operator": "isNot", "value": [""]}]
    },
    "sort": [{"field_name": "total_amount", "order": "desc"}],
    "pagination": {"limit": 100},
    "shaper": {"format": "flat"}
  }'

# Use tableName (table name) instead of tableId
lark-cli base +data-query \
  --base-token MAGObxxxxx \
  --dsl '{
    "datasource": {"type": "table", "table": {"tableName": "销售数据"}},
    "measures": [{"field_name": "金额", "aggregation": "sum", "alias": "total"}],
    "shaper": {"format": "flat"}
  }'

# After an aggregation or dimension query, if you need to read individual records, first have data-query return a business key that can be used for lookup
lark-cli base +data-query \
  --base-token MAGObxxxxx \
  --dsl '{
    "datasource": {"type": "table", "table": {"tableId": "tblxxxxxxxx"}},
    "dimensions": [{"field_name": "业务编号", "alias": "biz_key"}],
    "measures": [{"field_name": "指标值", "aggregation": "max", "alias": "max_value"}],
    "filters": {
      "type": 1,
      "conjunction": "and",
      "conditions": [{"field_name": "状态", "operator": "is", "value": ["有效"]}]
    },
    "sort": [{"field_name": "max_value", "order": "desc"}],
    "pagination": {"limit": 10},
    "shaper": {"format": "flat"}
  }'
```

<a id="参数"></a>
## Parameters

| Parameter                     | Required | Description |
|------------------------|------|------|
| `--base-token <token>` | Yes | Base Token (base_token) |
| `--dsl <json>`         | Yes | LiteQuery Protocol JSON DSL query statement. Note that this tool's schema differs from the schema for record/view queries; read this document thoroughly before writing a correct DSL to avoid confusing it with DSLs from other scenarios. |

<a id="如何从链接中解析参数"></a>
## How to parse parameters from a link

Users usually provide a URL like the following:

```text
https://example.feishu.cn/base/<base_token>?table=<block_id>
```

Do not directly treat the `table=` in the URL as the table ID. It represents the currently selected Base top-level block, which may be a table, dashboard, workflow, folder, or document. Parse the link first:

```bash
lark-cli base +url-resolve --url "<url>" --as user
```

- `--base-token`: use the returned `base_token`
- Only when the returned `block_type` is `table` should the `tableId` in the DSL use the returned `table_id`
- If another block type is returned, continue processing according to `hint.next_step`; if only a neutral `block_id` is returned, first use `+base-block-list` to confirm the block type, then choose the actual table to query

<a id="api-入参详情"></a>
## API input details

**HTTP method and path:**

```
POST /open-apis/base/v3/bases/:base_token/data/query
```

**Path parameters:**

| Parameter | Required | Description |
|------|------|------|
| `base_token` | Yes | Base Token |

**Request Body — DSL structure:**

| Field | Type | Required | Description |
|------|------|------|------|
| `datasource` | object | Yes | Data source, containing `type` (fixed to `"table"`) and the `table` object |
| `datasource.table.tableId` | string | Choose one | Target table ID |
| `datasource.table.tableName` | string | Choose one | Target table name |
| `dimensions` | Dimension[] | No* | Grouping dimension fields (GROUP BY) |
| `measures` | Measure[] | No* | Aggregate measure fields |
| `filters` | FilterGroup | No | Filter conditions (WHERE) |
| `sort` | Sort[] | No | Sort rules |
| `pagination` | object | No | Limit the number of returned rows, `{limit: N}`, maximum 5000 |
| `shaper` | object | No | Result format, fixed to `{format: "flat"}` |

> \* At least one of `dimensions` and `measures` must be provided.

**Dimension fields:**

| Field | Type | Required | Description |
|------|------|------|------|
| `field_name` | string | Yes | Field name |
| `alias` | string | No | Output column alias, must be globally unique |

**Measure fields:**

| Field | Type | Required | Description |
|------|------|------|------|
| `field_name` | string | Yes | Field name |
| `aggregation` | string | Yes | Aggregate function: `sum`, `avg`, `min`, `max`, `count`, `count_all`, `distinct_count` |
| `alias` | string | No | Output column alias, must be globally unique |

**Field types applicable to aggregate functions:**

| Aggregate function | Applicable field types |
|----------|-------------|
| `sum` / `avg` | `number` |
| `min` / `max` | `number`, `datetime` |
| `count` | Applies to all fields, counts non-null values |
| `count_all` | Applies to all fields, counts all rows |
| `distinct_count` | Applies to all fields |

> `number` includes all subtypes where `style.type` is `progress` / `currency` / `rating`, etc.

**FilterGroup:**

```json
{
  "filters": {
    "type": 1,
    "conjunction": "and",
    "conditions": [
      {"field_name": "城市", "operator": "is", "value": ["北京"]}
    ]
  }
}
```

| Field | Type | Required | Description |
|------|------|------|------|
| `type` | int | Yes | Fixed to `1` |
| `conjunction` | string | No | Condition combination logic: `"and"` or `"or"`, default `"and"` |
| `conditions` | Condition[] | No | Condition list |

**Condition:**

| Field | Type | Required | Description |
|------|------|------|------|
| `field_name` | string | Yes | Field name (must exactly match the field name in the table) |
| `operator` | string | Yes | Operator (see the operator table below) |
| `value` | string[] | Yes | Condition value array; for `isEmpty`/`isNotEmpty`, an empty array `[]` **must** be passed |

**Operators:**

| Operator | Description |
|--------|------|
| `is` | Equals |
| `isNot` | Not equals |
| `contains` | Contains |
| `doesNotContain` | Does not contain |
| `isEmpty` | Is empty |
| `isNotEmpty` | Is not empty |
| `isGreater` | Greater than |
| `isGreaterEqual` | Greater than or equal to |
| `isLess` | Less than |
| `isLessEqual` | Less than or equal to |

> For the field types applicable to each operator, see "Detailed value format when filtering by each field type" below.

**Detailed value format when filtering by each field type:**

*`text`*

| Operator | value format | Number of elements | Example |
|--------|-----------|---------|------|
| `is` / `isNot` / `contains` / `doesNotContain` | `["文本内容"]` | Exactly 1 | `["Hello"]` |
| `isEmpty` / `isNotEmpty` | `[]` | 0 | `[]` |

> `isGreater` / `isGreaterEqual` / `isLess` / `isLessEqual` are **not supported**: text has no natural order, so comparison operations are meaningless.
> `text` also covers phone, hyperlink, email, and barcode fields; distinguish them via `style.type` (`plain` (default) / `phone` / `url` / `email` / `barcode`), and the operator set is the same.
> When `style.type=url`, value filters on the link display name, not the URL itself.

*`number`*

| Operator | value format | Number of elements | Example |
|--------|-----------|---------|------|
| `is` / `isNot` / `isGreater` / `isGreaterEqual` / `isLess` / `isLessEqual` | `["数字字符串"]` | Exactly 1 | `["23.4"]`, `["-100"]` |
| `isEmpty` / `isNotEmpty` | `[]` | 0 | `[]` |

> value must be a string representation of a valid number.
> `number` also covers currency, progress, and rating fields; distinguish them via `style.type` (`plain` (default) / `currency` / `progress` / `rating`), and the operator set is the same, with only the value interpretation differing:
> - When `style.type=progress`, 34% corresponds to 0.34 rather than 34.
> - When `style.type=rating`, an integer must be entered, representing the rating.

*`auto_number`*

| Operator | value format | Number of elements | Example |
|--------|-----------|---------|------|
| `is` / `isNot` / `contains` / `doesNotContain` | `["编号字符串"]` | Exactly 1 | `["00001"]` |
| `isGreater` / `isGreaterEqual` / `isLess` / `isLessEqual` | `["编号字符串"]` | Exactly 1 | `["00010"]` |
| `isEmpty` / `isNotEmpty` | `[]` | 0 | `[]` |

*`select`*

| Operator | value format | Number of elements | Example |
|--------|-----------|---------|------|
| `is` / `isNot` | `["选项名"]` | **Exactly 1** | `["选项A"]` |
| `contains` / `doesNotContain` | `["选项A", "选项B"]` | Multiple allowed | `["选项A", "选项B"]` |
| `isEmpty` / `isNotEmpty` | `[]` | 0 | `[]` |

> `isGreater` / `isGreaterEqual` / `isLess` / `isLessEqual` are **not supported**: options are enumeration values with no natural order.
> Distinguish single select (`multiple=false`, default) / multiple select (`multiple=true`) via `multiple`.

*`user` / `created_by` / `updated_by`*

| Operator | value format | Number of elements | Example                     |
|--------|-----------|---------|------------------------|
| `is` / `isNot` | `["用户ID1", "用户ID2"]` | **Multiple allowed** | `["ou_aaa", "ou_bbb"]` |
| `contains` / `doesNotContain` | `["用户ID1", "用户ID2"]` | Multiple allowed | `["ou_aaa", "ou_bbb"]` |
| `isEmpty` / `isNotEmpty` | `[]` | 0 | `[]`                   |

> `isGreater` / `isGreaterEqual` / `isLess` / `isLessEqual` are **not supported**: people cannot be compared by magnitude.
> User IDs use `open_id` (`ou_` prefix), and the API layer automatically performs ID conversion.

*`group_chat`*

| Operator | value format | Number of elements | Example |
|--------|-----------|---------|------|
| `is` / `isNot` | `["群组ID1", "群组ID2"]` | Multiple allowed | `["oc_aaa", "oc_bbb"]` |
| `contains` / `doesNotContain` | `["群组ID1", "群组ID2"]` | Multiple allowed | `["oc_aaa", "oc_bbb"]` |
| `isEmpty` / `isNotEmpty` | `[]` | 0 | `[]` |

> `isGreater` / `isGreaterEqual` / `isLess` / `isLessEqual` are **not supported**: groups cannot be compared by magnitude.

*`link`*

| Operator | value format | Number of elements | Example |
|--------|-----------|---------|------|
| `is` / `isNot` | `["recId1", "recId2"]` | Multiple allowed | `["recAAA", "recBBB"]` |
| `contains` / `doesNotContain` | `["recId1", "recId2"]` | Multiple allowed | `["recAAA", "recBBB"]` |
| `isEmpty` / `isNotEmpty` | `[]` | 0 | `[]` |

> `isGreater` / `isGreaterEqual` / `isLess` / `isLessEqual` are **not supported**: linked records cannot be compared by magnitude.
> value passes the `record_id` of the record in the linked table.
> Two-way links (with `bidirectional=true` set at creation) also belong to the `link` type, and their operators are the same as one-way links.

*`location`*

| Operator | value format | Number of elements | Example |
|--------|-----------|---------|------|
| `is` / `isNot` / `contains` / `doesNotContain` | `["地址文本"]` | Exactly 1 | `["北京市朝阳区..."]` |
| `isEmpty` / `isNotEmpty` | `[]` | 0 | `[]` |

> `isGreater` / `isGreaterEqual` / `isLess` / `isLessEqual` are **not supported**: geographic locations have no natural order.
> location is filtered by `full_address` string, and latitude/longitude spatial filtering is not supported; when querying cities/districts, prefer `contains` and avoid using `is` to match short address terms.

*`checkbox`*

| Operator | value format | Number of elements | Example |
|--------|-----------|---------|------|
| `is` | `["true"]` or `["false"]` | Exactly 1 | `["true"]` |

> Only the `is` operator is supported; other operators are not supported.

*`datetime` / `created_at` / `updated_at`*

Date fields support only five operators: `is`, `isEmpty`, `isNotEmpty`, `isGreater`, and `isLess`.

value uses a predefined keyword mechanism, where the first element is a string constant name:

| Keyword | Description | value format | Supported operators |
|--------|------|-----------|-------------|
| `ExactDate` | Exact date | `["ExactDate", "1773187200000"]` (millisecond timestamp) | `is`, `isGreater`, `isLess` |
| `Today` | Today | `["Today"]` | `is`, `isGreater`, `isLess` |
| `Tomorrow` | Tomorrow | `["Tomorrow"]` | `is`, `isGreater`, `isLess` |
| `Yesterday` | Yesterday | `["Yesterday"]` | `is`, `isGreater`, `isLess` |
| `CurrentWeek` | This week | `["CurrentWeek"]` | Only `is` |
| `LastWeek` | Last week | `["LastWeek"]` | Only `is` |
| `CurrentMonth` | This month | `["CurrentMonth"]` | Only `is` |
| `LastMonth` | Last month | `["LastMonth"]` | Only `is` |
| `TheLastWeek` | Past seven days | `["TheLastWeek"]` | Only `is` |
| `TheNextWeek` | Next seven days | `["TheNextWeek"]` | Only `is` |
| `TheLastMonth` | Past thirty days | `["TheLastMonth"]` | Only `is` |
| `TheNextMonth` | Next thirty days | `["TheNextMonth"]` | Only `is` |

> - **ExactDate time zone behavior**: The millisecond timestamp is converted to **midnight of the day in the document time zone** during actual filtering. In cross-time-zone scenarios, note that the date may shift by one day.
> - **Range-type keywords** (`CurrentWeek`, `LastWeek`, `CurrentMonth`, `LastMonth`, `TheLastWeek`, `TheNextWeek`, `TheLastMonth`, `TheNextMonth`) only support the `is` operator.
> - **Keywords are case-sensitive**: `ExactDate`, `Today`, `CurrentWeek`, etc. have a capitalized first letter. Incorrect casing will cause validation to fail.

*`attachment`*

| Operator | value format | Element count | Example |
|--------|-----------|---------|------|
| `isEmpty` / `isNotEmpty` | `[]` | 0 | `[]` |

> Attachment fields only support `isEmpty` and `isNotEmpty`; other operators are not supported.

*`formula` / `lookup`*

The operators and value formats for formula and lookup reference fields **depend on their result data type**. Refer to the rules for the corresponding field type above based on the result type. For example:

- Formula result is a number → follow `number` rules
- Formula result is a date → follow `datetime` rules
- Formula result is a single select → follow `select` rules

**Sort fields:**

| Field | Type | Required | Description |
|------|------|------|------|
| `field_name` | string | Yes | Field name or alias |
| `order` | string | No | `"asc"` (default) or `"desc"` |

**Pagination fields:**

| Field | Type | Required | Description |
|------|------|------|------|
| `limit` | int | No | Maximum number of records to return. Must be a positive integer, maximum 5000; if not provided, the system default is used. offset is not supported |

**Shaper fields:**

| Field | Type | Required | Description |
|------|------|------|------|
| `format` | string | Yes | Fixed to `"flat"`, indicating a flattened object array is returned |

<a id="cli-出参详情"></a>
## CLI output details

The CLI outputs the standard envelope `{ok, identity, data}` (`{ok:false, identity, error}` on failure).

**On success:**

```json
{"ok": true, "identity": "user", "data": {"main_data": [{"dim_city": {"value": "北京"}, "total_amount": {"value": 12345.00}}, ...]}}
```

**On failure:**

```json
{"ok": false, "identity": "user", "error": {"type": "api", "subtype": "unknown", "code": 800004006, "message": "...does not exist in table schema", "hint": "...", "log_id": "..."}}
```

**Response fields:**

| Field | Type | Description |
|------|------|------|
| `ok` | bool | Whether it succeeded |
| `identity` | string | Execution identity: `user` / `bot` |
| `data.main_data` | []object | Query result array; each element is a row of data (on success) |
| `error` | object | Typed error on failure, containing `type` / `subtype` / `code` / `message` / `hint` / `log_id` |

The field values of each row of data are wrapped in CellValue:

```json
{
  "dim_city": {
    "value": "北京"
  },
  "total_amount": {
    "value": 12345.00
  }
}
```

- `value`: Display value (person name, option name, formatted date, etc.)

<a id="返回值"></a>
## Return value

After the command succeeds, it outputs the contents of the `data` field:

```json
{
  "main_data": [
    {
      "dim_city": {"value": "直营"},
      "measure_count": {"value": 1}
    },
    {
      "dim_city": {"value": "加盟"},
      "measure_count": {"value": 2}
    }
  ]
}
```

<a id="工作流"></a>
## Workflow

1. Confirm the base-token and table-id
2. **Query the table schema first**: run `lark-cli base +field-list --base-token <base_token> --table-id <table_id>`
3. Obtain the field_name (the field name used in the DSL) from the returned field list
4. Construct the DSL JSON based on the field information
5. Run +data-query
6. Interpret the returned result:
   - The result is in the `data.main_data` array; each element represents one row
   - The key of each row object is the `alias` specified in the DSL; if no alias is specified, the key is the automatically generated column name
   - Each value is a CellValue object; the actual value is in the `value` field, such as `{"value": "北京"}` or `{"value": 12345.00}`
   - On failure, the result is in `data.error`, containing the specific error code and message

<a id="与记录读取组合"></a>
## Combining with record reading

`+data-query` can return aggregated results, and can also return dimension field rows when only `dimensions` is passed; these dimension rows are deduplicated by field combination, do not include `record_id`, and cannot be equated with individual raw records. When you need to output the raw record fields, display values, record location information, or linked table fields corresponding to the aggregated results, combine them as follows:

1. Use `+data-query` to perform global filtering, grouping, aggregation, sorting, and TopN in the Base cloud query service to obtain business keys, group values, or candidate field combinations.
2. If you already have the `record_id` of the candidate records, use `+record-get` to read the fields of individual records.
3. If what you have is a structured business key (such as an ID, status, date, amount, etc.), use `+record-list --filter-json` for exact filtering before reading; `+record-search` is used for text display value keywords.
4. Only when the candidate condition itself is a text display value keyword should you use `+record-search`, and use `search_fields` to limit the range and `select_fields` for projection.
5. If the candidate records contain link fields, extract the linked `record_id` and then use `+record-get` in the linked table to batch-read the display fields.
6. The final answer should display real business fields; internal `record_id` is used for joining or locating.

Do not interpret `data-query pagination.limit` as a paginated scan; it only limits the number of aggregated result rows returned by the Base cloud query service and does not support offset. When individual raw records are needed, handle them according to the full read or lookup path in the [Record query and analysis SOP](lark-base-record-query-and-analysis-sop.md).

<a id="坑点"></a>
## Pitfalls

- ⚠️ **You must query the table schema first**: The `field_name` in the DSL must exactly match the field name in the table (case-sensitive); do not construct it by guessing. First use `lark-cli base +field-list --base-token <base_token> --table-id <table_id>` to obtain the real field names
- ⚠️ **Permission requirements differ by document type**: An ordinary Base only requires document **read permission**; an advanced-permission Base requires being a document admin (**FA / Full Access**), otherwise a permission error is returned
- ⚠️ **alias does not support Chinese**: The alias of dimensions and measures must use English (such as `dim_city`, `total_amount`); a Chinese alias will cause an error
- ⚠️ **The API path is `base/v3`**: The path of this interface is `/open-apis/base/v3/bases/:base_token/data/query`, not `bitable/v1`. The two are completely different; using the wrong version number returns `[2200] Internal Error`
- ⚠️ **At least one of `dimensions` and `measures` must be provided**: If neither is provided, a DSL validation error is returned
- ⚠️ **`shaper` must be `{"format": "flat"}`**: If it is not provided or another value is provided, the result format will be unpredictable; it is recommended to always specify it explicitly
- ⚠️ **Data table identifier `tableId` vs `tableName`**: In datasource, you can use `tableId` (such as `tblXXX`) or `tableName` (the user-defined display name of the data table); choose one, do not mix them
- ⚠️ **`pagination.limit` maximum 5000**: Exceeding it will cause an error, and offset is not supported; only limit is supported
- ⚠️ **All aliases must be globally unique**: Aliases between dimensions and measures must not have duplicate names either

<a id="参考"></a>
## References

- [lark-base](../index.md) — all Base commands
- [lark-shared](../../shared/index.md) — authentication and global parameters
- [Field Schema](lark-base-field-schema.md) — field types and JSON structures
