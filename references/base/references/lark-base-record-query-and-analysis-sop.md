<a id="base-record-数据语义与专业分析-sop"></a>
# Base Record Data Semantics and Professional Analysis SOP

This SOP does not cover general jq / Python / pandas syntax, statistical formulas, or data science algorithms. The Agent should use its existing data analysis capabilities; this document is only responsible for correctly mapping Base's query scope, NDJSON physical structure, Field / Record / View / Link semantics, and integrity constraints to professional analysis tasks.

For ordinary previews, reading known records, keyword searches, and small-scale direct processing, follow the main skill's [Record core path](../index.md#record-values-and-queries). Read this document in the following cases: full reads of large tables, `has_more=true`, View-scoped reads, complex multi-table JOINs, set or multi-value operations, grouping and Top-K, window or strict time series, time period alignment, hierarchical recursion, data reshaping, derivation and specified-rule cleaning, temporary semantic transformation, and descriptive or inferential analysis that requires a reliable sample scope.

<a id="1-先选数据路径"></a>
## 1. Choose the data path first

| Task condition | Path | Integrity requirement |
| --- | --- | --- |
| Current query is at most 2000 rows and `has_more=false` | NDJSON local analysis | Process the artifact directly |
| User specifies a View | Record tool adds `--view-id` to return records within the view scope | Conclusions only represent that View; record the record scope in `query_context` |
| More than 2000 rows and per-record raw records must be obtained | Adjust `--offset` and continue querying | Until `has_more=false` indicates all records have been read |
| More than 2000 rows, only single-table basic statistics, grouping, or Top-K needed | `+data-query` | Computed by Base cloud over the complete single-table scope |
| Multi-table JOIN, window, recursion, strict funnel, semantic analysis, or any advanced computation requiring per-record detail | Process with a suitable local analysis engine after complete NDJSON | Every participating table must be complete; `data-query` cannot replace raw detail |

Artifacts from partial previews, fixed first N rows, or `has_more=true` cannot support global conclusions. Sampling is used only when the user explicitly requests sampling, and the sampling scope and method must be stated.

<a id="2-范围view选择与投影"></a>
## 2. Scope, View, selection, and projection

Clarify the analysis population first, then export data:

- **Whole-table scope:** omit `--view-id`; `query_context.record_scope` should be `all_records` or `filtered_records`.
- **View scope:** pass the real `--view-id`. The View's filter determines the record scope, sort determines the order, and `query_context.record_scope` should be `view_filtered_records`; conclusions must be phrased as "within this View".
- **Temporary conditions:** `--filter-json` overrides the View filter, `--sort-json` overrides the View sort; sort example: `--sort-json '[{"field":"Updated","desc":true},{"field":"Title","desc":false}]'`, array order is sort priority, `desc=true` is descending. The two only override their corresponding parts; "specifying a View" and "a manually replaced scope" must not be conflated as the same basis. For complete examples and the protocol of tuple conditions, see [Filter condition structure](lark-base-filter-condition.md).
- **Keywords and structured conditions:** use `+record-search` for displayed text keywords; use `--filter-json` for numbers, dates, options, people, groups, Link, null values, etc. The two can be combined.
- **Field projection:** repeat `--field-id` to export only the fields needed for filtering, grouping, sorting, JOIN, interpretation, and lookup. The system `record_id` is automatically retained; cross-table tasks must also project Link or a verified business key.

The manifest's `query_context` is the record scope of this artifact, not a substitute for the complete query language. Before reusing an old artifact, verify `base_token`, `table_id`, View / filter / sort, projected fields, and `rev` at the same time.

<a id="3-大表完整读取"></a>
## 3. Full reads of large tables

A single NDJSON response returns at most 2000 records. When more than 2000 per-row raw records must be obtained:

1. Fix `base_token`, `table_id`, `view-id`, filter, sort, and field projection; the first chunk starts from `offset=0`, each chunk is `limit=2000`, and output to different artifacts.
2. For each chunk, read the manifest's `records_count`, `has_more`, `next_offset`, `rev`, and `query_context`; when `has_more=true`, continue using only the returned `next_offset`.
3. The `rev` and `query_context` of all chunks must be consistent. If `rev` changes during reading, it means the data snapshot has changed, which may cause omissions or duplicates; if strict completeness is required, re-read from the beginning, otherwise explicitly disclose that it is not snapshot-consistent.
4. Use the last chunk's `has_more=false` as the termination condition. The analysis engine can consume chunk by chunk; it is not necessary to concatenate all files into one giant file before analysis.
5. For multi-table tasks, complete the integrity check for each table separately; if any input is incomplete, JOIN, set, window, or statistical results are incomplete.

If the task only needs single-table basic statistics, do not download in chunks just to get all raw rows; prefer the `+data-query` below.

<a id="4-data-query大规模单表基础统计逃生路径"></a>
## 4. `data-query`: escape path for large-scale single-table basic statistics

`+data-query`'s datasource is a single Base Table, suitable when more than 2000 rows need to be completed in the cloud:

- `filters`: filter before aggregation, similar to WHERE; it uses a LiteQuery-specific DSL, not the Record/View tuple filter, so be careful not to confuse them.
- `dimensions`: grouping fields.
- `measures`: `sum`, `avg`, `min`, `max`, `count`, `count_all`, `distinct_count`.
- `sort`: sort fields

After this SOP selects this path, read [data-query DSL](lark-base-data-query.md). Typical applicable scope is **single-table** totals, grouped counts, numeric summaries, distinct counts, grouped sorting, and Top-K.

Capability boundaries:

- Passing only dimensions returns deduplicated dimension combinations, does not return `record_id`, and cannot be regarded as per-record records.
- It does not handle multi-table JOIN, window functions, recursion, raw detail export, or semantic analysis.
- There is no independent HAVING semantics; you can first aggregate with `data-query`, then apply local condition filtering to the already-converged aggregation results.
- Conditional aggregation can be pushed down directly to `filters` only when all measures share the same precondition; when different measures use different conditions, split into reviewable queries or compute on complete detail.
- When raw records need to be displayed after aggregation, use the returned real business key / dimension values to look up via `+record-list --filter-json` or `+record-get`; do not fabricate `record_id` from aggregated rows.

<a id="5-manifest-与-ndjson-结构"></a>
## 5. Manifest and NDJSON structure

`--output ./records.ndjson` generates a record file and a same-named `.manifest.json`. High-frequency manifest fields:

| Field | Analysis use |
| --- | --- |
| `records_count` / `has_more` / `next_offset` | Determine current chunk size, whether it is complete, and the next chunk's starting point |
| `base_token` / `table_id` / `query_context` | Fix the source table and read scope |
| `rev` | Check data version consistency across multiple chunks or when reusing artifacts |
| `timezone` | Interpret Base local calendar boundaries |
| `columns.*.field_id/field_type/physical_type` | Confirm the actual NDJSON column types and stable field identifiers |
| `columns.*.stats/example/hint` | Estimate null values, array expansion scale, and text volume; describes only this export |
| `record_file_size_bytes` | Decide whether to read the artifact in one pass or process it in chunks |

Each NDJSON line is one Record, keyed by field `name`, and additionally contains the system `record_id`; `field_id` is located in the manifest. Renaming a field changes the NDJSON key; cross-batch or long-term scripts should verify `field_id → name` via the manifest.

| `field_type` | NDJSON structure | Base-specific analysis semantics |
| --- | --- | --- |
| `record_id` | `string` | Unique primary key within the table, used for locating and deduplication across chunks |
| `text`, `formula`, `lookup`, `auto_number`, `not_support` | `string|null` | Formula / Lookup do not retain the original computed type; when numeric operations are needed, conversion rules must be explicitly verified |
| `datetime`, `created_at`, `updated_at` | RFC3339 `string|null` | With offset; distinguish absolute instants from Base local calendar semantics |
| `number` | `number|null` | Null is not zero; whether to include it in the denominator is determined by the task basis |
| `checkbox` | `boolean` | Upstream null values are normalized to `false` in NDJSON |
| `select` | `array<string>` | Both single-select and multi-select are read as arrays of option names; null is `[]` |
| `location` | `{lng,lat,full_address}|null` | Use coordinates for geographic computation, addresses for textual range analysis |
| `user`, `group_chat`, `created_by`, `updated_by` | `array<{id,name}>` | Use `id` for joining and deduplication, `name` for display |
| `link` | `array<{id}>` | `id` is the `record_id` in the target table specified by the Field schema |
| `attachment` | `array<{file_token,size,name}>` | The file token is stable locating information; array expansion changes the grain |

Except for `record_id`, do not assume any column is non-null or unique. Scalar null values are usually `null`, multi-value column nulls are `[]`; do not rely on NDJSON row order unless explicitly sorted.

<a id="6-专业分析场景中的-base-映射"></a>
## 6. Base mapping in professional analysis scenarios

The table below does not teach algorithms; it only points out Base-specific issues that must be resolved before starting computation:

| Scenario | Base data structure mapping and correctness constraints |
| --- | --- |
| Complex multi-table JOIN | Link is first expanded into `(source_record_id, target_record_id)` edges, then joined by the target table's `record_id`; the target `table_id` comes from the Field schema. When there is no Link, only business keys with verified uniqueness and null rules can be used, and unmatched and duplicate keys must be counted. |
| Set operations | Select is an array of names, people/groups by `id`, Link by target `record_id`; first clarify whether it is record-level containment/intersection-union-difference or element-level sets, and do not compare arrays as stringified values. |
| Multi-value expansion and data reshaping | Select, people, groups, Link, and attachments are all nested relations. One expansion changes the grain from record to record-element; expanding two arrays simultaneously produces an in-row Cartesian product, so unless the task explicitly analyzes co-occurrence, expand separately and aggregate back to the target grain. |
| Grouping, conditional aggregation, and HAVING | First determine record / element / entity grain and the null basis. Single-table basic aggregation can use `data-query`; HAVING is filtered locally on the aggregation results. Measures with different conditions must not incorrectly share one global filter. |
| Sorting and Top-K | Use Record sort for raw-record Top-K; use `data-query` for large-table single-table aggregation Top-K. Whether all tied values are retained and how ties are stably broken must be clarified according to the task basis. |
| Window computation and strict time-series funnels | NDJSON does not guarantee default order; explicitly choose the entity key, event time, partition fields, and same-time tie-breaker. `data-query` does not provide window or per-event funnel semantics. |
| Time boundaries and period alignment | Use the complete RFC3339 instant for real duration and cross-time-zone sorting; for day/week/month grouping by the source Base, use the local date in the value and the manifest `timezone`, and do not convert to UTC first and then cut calendar periods. |
| Hierarchy and recursion | Link is a directed adjacency edge; preserve each Table's record-id domain hop by hop, record visited nodes to handle cycles, and clarify the depth or termination condition. |
| Derived variables and data quality handling for specified rules | Preserve original fields and `record_id`, and name derived columns separately; execute only missing, anomaly, deduplication, and standardization rules given by the user or confirmed by the business, and do not treat general cleaning habits as business facts. |
| Temporary semantic transformation | Labels, topics, or entity mappings produced by the LLM are linked back with `record_id` and retain the basis for judgment; by default they are only local temporary derived results and are not written back to Base unless the user requests it. |
| Descriptive statistics, variance decomposition, association analysis, and statistical inference | First confirm whether the population is the whole table or a View, whether the input is complete, whether the analysis grain has changed due to multi-value expansion, and whether Formula / Lookup require type recovery; treat selection bias, missingness, and duplicate entities as Base data basis issues, rather than silently handling them with algorithm defaults. |

When spanning multiple similar fact tables, first project to a consistent long-table structure, for example `(source_table, source_record_id, entity_id, metric...)`, then merge vertically; for horizontal comparison, first aggregate each table to the same entity grain before JOIN, avoiding many-to-many fan-out between raw facts.

<a id="7-交付前检查"></a>
## 7. Pre-delivery checklist

The final result should at least state:

- Which Base / Table / View the data comes from, and which filters, time ranges, and field projections were applied.
- Whether each input table was read to `has_more=false`, or whether complete single-table aggregation was performed in the cloud by `data-query`.
- Analysis grain, null basis, multi-value expansion method, JOIN key, duplicate keys, and unmatched count.
- Whether time uses instant or Base local-calendar semantics.
- Which user-specified rules were used for temporary derivation, cleaning, semantic labels, or inference; which results were not written back to Base.

Only give global conclusions when the scope is complete and the basis is consistent with the question.
