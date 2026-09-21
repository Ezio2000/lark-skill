# BaseApp Block `data_config`

This document describes the CLI mapping and operational constraints for the BaseApp component `data_config`, and does not reproduce the complete field schema. Each `data_sources[]` element of an App chart reuses the field value, filter, group, sort, and normalization rules of [Dashboard Block configuration](lark-base-dashboard-block-config.md); the difference is that Dashboard uses a flat single-data-source structure, whereas App charts use a shared `base_token` at the top level and multiple data sources `data_sources[]`. The list component is an App-only protocol and does not reuse the Dashboard chart structure. "Component protocol" as used in this document refers to the API metadata released with the CLI version, the constraints explicitly listed in this document, and the actual server-side validation results.

<a id="类型映射"></a>
## Type mapping

- Chart: `--type column|bar|line|pie|ring|area|combo|scatter|funnel|wordCloud|radar|statistics`
- Rich text: `--type text` (same name and meaning as the Dashboard text component)
- List: `--type list --sub-type standard|grouped|collapsible|card|detail`
- When a list omits `--sub-type`, it defaults to `standard`
- `type/sub_type` cannot be modified after creation

<a id="外层请求字段"></a>
## Outer request fields

- Create sends only `name`, `type`, and, as needed, `sub_type` and `data_config`. `name` and `type` are required; `data_config` is required for charts and lists, and may be omitted for rich text.
- When a standard list does not explicitly specify `--sub-type`, `sub_type` is not sent, and the server uses the `standard` default value; other list types must send the corresponding `sub_type`.
- Charts and rich text must not send `sub_type`.
- Update sends only `name` and `data_config`, and at least one must be provided; fields not passed remain unchanged, and modifying `type` or `sub_type` is not allowed.
- Display configurations such as layout, position, size, and `show_title` are not part of the public Create/Update request fields in this release, and the CLI does not provide or promote these fields.

<a id="列表配置"></a>
## List configuration

The common data source fields for lists are the single-value `base_token` and `table_name`. Each list can be associated with at most one Base, and that Base must be in the same Workspace as the App.

According to the component protocol, each subtype uses the following field groups:

- Common: `base_token`, `table_name`, `filter`, `sort_by`
- `standard/grouped/collapsible`: `columns`, `group_by`
- `card`: `fields`, `card_config`
- `detail`: `fields`, `detail_config`
- `columns` and `fields` are both optional fields. When not specified, the CLI does not send them, and the server uses the product default fields.
- They are sent only when the user explicitly specifies `columns` / `fields`; explicitly passing `[]` means explicitly sending an empty array, and it cannot be automatically filled in as a default value.
- `filter`, `sort_by`, `group_by`, `card_config`, and `detail_config` are also optional fields; when not specified, they are not sent.
- For list Create, `data_config` is required, of which only `base_token` and `table_name` are top-level required fields.
- Once an optional object is passed in, its internal required items must still satisfy the protocol; for example, `filter` must contain `conjunction` and 1 to 50 `conditions` items.

Do not add semantic validation not defined by the protocol, especially do not assume:

- detail/card must have a title;
- grouped/collapsible must have, or can only have, one group_by;
- fields have role or visible attributes.

Unknown top-level fields will be rejected by local validation; use `--no-validate` only when it is confirmed that CLI validation is inconsistent with the latest protocol.

<a id="创建示例"></a>
## Creation example

```bash
lark-cli base +app-block-create \
  --app-token <app_token> --page-id <page_id> \
  --name "订单列表" \
  --type list --sub-type standard \
  --data-config '{"base_token":"<base_token>","table_name":"订单"}'
```

The specific object structure and requiredness of fields are subject to the API metadata of the current CLI version and the server-side validation results; do not guess undisclosed attributes here.

<a id="更新语义"></a>
## Update semantics

The following is an example of updating only the top-level `filter`, applicable to components whose protocol defines `filter` at the top level of `data_config` (usable by all list subtypes). The component type cannot be modified after creation, so the update command no longer passes `--type`. For App charts, `filter` is defined in the corresponding `data_sources[]` element; when updating chart filters, the complete `data_sources` must be passed according to the chart structure, and `filter` must not be lifted to the top level.

```bash
lark-cli base +app-block-update \
  --app-token <app_token> --page-id <page_id> --block-id <block_id> \
  --data-config '{"filter":{"conjunction":"and","conditions":[{"field_name":"状态","operator":"is","value":"已完成"}]}}'
```

- The CLI sends only fields explicitly passed by the user.
- Fields not passed remain unchanged on the server side.
- Do not inject create defaults for update, and do not first read and then assemble a full configuration.
- The replacement granularity of array/object fields is subject to the component protocol and server-side validation results.

<a id="图表与富文本"></a>
## Charts and rich text

**App charts use a multi-data-source structure (`ChartDataConfig`), which differs from Dashboard's flat single-source structure.** The top level uses one `base_token` (shared by all data sources), while `table_name` / `series` / `count_all` / `group_by` / `filter` are pushed down into each `data_sources[]` element; the top level also has optional `data_source_mode` and `sort`. The value logic of each field within each data source is exactly the same as in [Dashboard Block configuration](lark-base-dashboard-block-config.md) (`series[].rollup` uppercase, `group_by[].sort` lowercase, etc.), and the CLI reuses the same set of normalization and validation for each `data_sources[]` element. Rich text uses `--type text`, is configured as `{"text":"..."}`, and has no data source; on Create, `data_config` may be omitted, which is equivalent to empty text.

> **How to retrieve text content**: the text component has no `/data` interface, and going through `+app-block-get-data` will be fallback-handled by the server as a generic 500. Instead, use `+app-block-get --block-id <widget_id>` to directly read `data_config.text` (the raw Markdown). Charts still go through `+app-block-get-data --block-id <chart_token>`.

Top-level parameters:

| Parameter | Required | Value | Description |
|-|-|-|-|
| `base_token` | Yes | `string` | Token of the Base where the data resides; all data sources share the same value. App commands do not carry `--base-token`, and it can only be written inside data_config |
| `data_sources` | Yes | `ChartDataSourceConfig[]` | Ordered array, at least one item |
| `data_source_mode` | No | `aggregate` / `compare` | `aggregate` (default) aggregates data sources on the horizontal axis; `compare` splits series by data source |
| `sort` | No | `{type: group\|value\|record, order?: asc\|desc}` | Top-level sort; `statistics` is not allowed |

Each `data_sources[]` element: `table_name` (required), one of `series` or `count_all=true`, `group_by` (at most 2 items, `statistics` is not allowed), `filter`.

```json
{
  "base_token": "A2f5boKjfazMzesI9zKbmugTc4T",
  "data_sources": [
    {
      "table_name": "数据表",
      "count_all": true,
      "group_by": [
        { "field_name": "文本", "mode": "integrated", "sort": { "type": "value", "order": "desc" } }
      ]
    }
  ]
}
```

Corresponding command (single-data-source count column chart):

```bash
lark-cli base +app-block-create \
  --app-token <app_token> --page-id <page_id> \
  --name "文本分布" --type column \
  --data-config '{"base_token":"A2f5boKjfazMzesI9zKbmugTc4T","data_sources":[{"table_name":"数据表","count_all":true,"group_by":[{"field_name":"文本","mode":"integrated","sort":{"type":"value","order":"desc"}}]}]}'
```

Multi-data-source example (two tables each produce one series, split by data source):

```bash
lark-cli base +app-block-create \
  --app-token <app_token> --page-id <page_id> \
  --name "销售与成本" --type combo \
  --data-config '{"base_token":"bas_xxx","data_source_mode":"compare","data_sources":[{"table_name":"销售表","group_by":[{"field_name":"月份","sort":{"type":"group","order":"asc"}}],"series":[{"field_name":"销售额","rollup":"SUM"}]},{"table_name":"成本表","group_by":[{"field_name":"月份","sort":{"type":"group","order":"asc"}}],"series":[{"field_name":"成本","rollup":"SUM"}]}],"sort":{"type":"group","order":"asc"}}'
```

Update semantics: passing `data_sources` fully replaces the entire ordered array; when modifying `base_token`, the complete `data_sources` must be passed at the same time. The request must not include `sub_type` (display variants such as smooth/stacked/percentage use product default values). Layout, position, size, and display configuration are not part of the public Create/Update protocol in this release. Other request fields are subject to the API metadata of the current CLI version and the server-side validation results.
