# base +dashboard-block-get-data

> **Prerequisite:** Read [lark-base-dashboard.md](lark-base-dashboard.md) first to understand the overall dashboard workflow.

Get the **final computed result** of a dashboard chart block, returning a chart protocol JSON suitable for direct AI consumption.

This command is suitable for the following scenarios:

1. Reading the **actual computed results** of bar charts / horizontal bar charts / line charts / pie charts / donut charts / area charts / combo charts / scatter charts / funnel charts / radar charts / ranking lists / word clouds / metric cards;
2. Handing chart results to AI for subsequent summarization, trend explanation, year-over-year/month-over-month descriptions, and anomaly extraction;
3. Directly consuming results already aggregated at the chart layer **without reading raw records**;
4. Verifying whether the data currently displayed by a chart matches expectations.

> [!IMPORTANT]
> - This command returns the **chart result protocol**, not block metadata;
> - If you need configurations such as `name`, `type`, `layout`, `data_config`, use `+dashboard-block-get` first;
> - Text components (`text`) do not involve computation and are not applicable to this command;

<a id="一句话理解"></a>
## One-sentence understanding

`+dashboard-block-get-data` = **get the chart's "computed result"**, not the chart's "configuration".

---

<a id="支持的图表类型"></a>
## Supported chart types

The following chart types currently support data computation and return:

<a id="二维图表11-种"></a>
### Two-dimensional charts (11 types)

- Bar chart
- Horizontal bar chart
- Line chart
- Pie chart
- Donut chart
- Area chart
- Combo chart
- Scatter chart
- Funnel chart
- Radar chart
- Ranking list

<a id="特殊类型2-种"></a>
### Special types (2 types)

- Word cloud
- Metric card (statistics)

> [!CAUTION]
> Although text components also belong to dashboard blocks, they do not produce computable data, so this protocol will not be returned for them.

---

<a id="推荐命令"></a>
## Recommended commands

```bash
lark-cli base +dashboard-block-get-data \
  --base-token bascn***************CtadY \
  --block-id chtxxxxxxxx
```

If you do not yet know the target block's ID, the typical order is:

```bash
# First see which components are in the dashboard
lark-cli base +dashboard-block-list \
  --base-token bascn***************CtadY \
  --dashboard-id blkxxxxxxxx \
  --page-size 100

# Then read the final computed result of a component
lark-cli base +dashboard-block-get-data \
  --base-token bascn***************CtadY \
  --block-id chtxxxxxxxx
```

If the user wants to read multiple components, first obtain the real IDs via `+dashboard-block-list --page-size 100`; if `has_more=true` is returned, continue passing the `page_token` returned by this page to `--page-token` until `has_more=false`. After collecting the target components and skipping text components that have no computed results, execute serially within **a single shell tool call**. Each command will output a complete JSON envelope in sequence; do not split each block into separate model turns.

```bash
set -euo pipefail

block_ids=(cht_block_1 cht_block_2)
for block_id in "${block_ids[@]}"; do
  lark-cli base +dashboard-block-get-data \
    --base-token bascn***************CtadY \
    --block-id "$block_id"
done
```

The IDs in the array must come verbatim from what `+dashboard-block-list` returns; do not execute names or unverified user text as shell code. The loop is still serial API calls, only reducing model round trips, without trimming any component results.

If you need to first confirm the component type, name, or `data_config`, execute first:

```bash
lark-cli base +dashboard-block-get \
  --base-token bascn***************CtadY \
  --dashboard-id blkxxxxxxxx \
  --block-id chtxxxxxxxx
```

---

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--base-token <token>` | Yes | Base Token, identifies the target Base |
| `--block-id <id>` | Yes | Chart Block ID, i.e., the unique identifier of the target component |
| `--format <fmt>` | No | Output format, follows the CLI global output format rules |
| `--dry-run` | No | Only preview the API call, do not actually execute |

> [!TIP]
> This command **does not need** `--dashboard-id`. Only `base_token + block_id` is needed to locate and read the chart result.

---

<a id="返回结构总览"></a>
## Return structure overview

Successful CLI output uses the standard `{ok, identity, data}` envelope:

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "dimensions": [],
    "measures": [],
    "main_data": []
  }
}
```

Here `identity` is the identity actually used for this call, and `data` is the CLI chart protocol body. The `data` structure differs slightly across chart types:

| Chart type | Always present | May be present |
|----------|--------|--------|
| Two-dimensional charts | `dimensions` / `measures` / `main_data` | None |
| Word cloud | `dimensions` / `measures` / `main_data` | None |
| Metric card | `dimensions` / `measures` / `main_data` | `comparison_data` / `trend_data` |

---

<a id="协议字段说明"></a>
## Protocol field descriptions

### 1) `dimensions`

Dimension definition array, telling you what field each `dim_*` key in the main result represents.

```json
[
  {
    "field_name": "文本",
    "alias": "dim_5bKp"
  }
]
```

Field meanings:

| Field | Description |
|------|------|
| `field_name` | Dimension field display name |
| `alias` | Dimension alias, used as the key in `main_data` / `trend_data` |

### 2) `measures`

Measure definition array, telling you what aggregate measure each `me_*` key represents.

```json
[
  {
    "field_name": "Count",
    "aggregation": "count_all",
    "alias": "me_Y291bnRfYWxsX0NvdW50"
  }
]
```

Field meanings:

| Field | Description |
|------|------|
| `field_name` | The field name used when computing this measure; when `aggregation = count_all`, it is fixed to `Count`, indicating a count of total records |
| `aggregation` | Aggregation method, common values: `count_all` / `count` / `sum` / `avg` / `min` / `max` |
| `alias` | Measure alias, used as the key in `main_data` / `comparison_data` / `trend_data` |

For example:

- If computing the sum of "Sales", then `field_name = 销售额`, `aggregation = sum`
- If computing the total record count, then `field_name = Count`, `aggregation = count_all`

### 3) `main_data`

Main result set. Each row is an object; the key is not the field name itself, but the `alias` declared in `dimensions` / `measures`.

```json
[
  {
    "dim_5bKp": {"value": "A"},
    "me_Y291bnRfYWxsX0NvdW50": {"value": 3}
  }
]
```

### 4) `comparison_data`

Only metric cards may return this. Represents the two values for year-over-year/month-over-month comparison, in a fixed order:

1. Current period value
2. Comparison period value

> [!NOTE]
> The raw protocol usually **does not directly show the period name**, only the corresponding values. Therefore, interpreting whether it is "year-over-year" or "month-over-month", and what the comparison window specifically is, usually requires understanding it in combination with the component configuration or UI context.

### 5) `trend_data`

Only metric cards may return this. Represents a time series trend; each row usually contains one time dimension and one measure value.

---

<a id="alias-规则与读取方式"></a>
## Alias rules and how to read them

You should not treat aliases as human-readable field names, but rather as **column IDs in the result table**.

Common generation rules:

- Dimension alias: `dim_` + `base64(field_name)`
- Measure alias: `me_` + `base64(aggregation + "_" + field_name)`

> [!NOTE]
> For readability, some examples in this document use **simplified aliases** (such as `dim_xxx`, `me_xxx`, or shorter example values), and are not guaranteed to match real return values character by character.
> When actually reading results, always rely on the aliases declared in `dimensions` / `measures`, and do not assume that all examples strictly expand into fully encoded values.

For example:

```json
{
  "dimensions": [
    {"field_name": "文本", "alias": "dim_5bKp"}
  ],
  "measures": [
    {"field_name": "Count", "aggregation": "count_all", "alias": "me_xxx"}
  ],
  "main_data": [
    {
      "dim_5bKp": {"value": "A"},
      "me_xxx": {"value": 3}
    }
  ]
}
```

This should be interpreted as:

- `dim_5bKp` corresponds to the field "Text", with value `A`
- `me_xxx` corresponds to the measure `count_all(Count)`, with value `3`

> [!TIP]
> When reading results, **first look at `dimensions` / `measures`, then decode `main_data`**. Do not guess the meaning from the alias name alone.

---

<a id="各图表类型的协议细节"></a>
## Protocol details for each chart type

<a id="一二维图表"></a>
### I. Two-dimensional charts

Applicable to: bar charts, horizontal bar charts, line charts, pie charts, donut charts, area charts, combo charts, scatter charts, funnel charts, radar charts, ranking lists.

Ranking lists reuse the same `dimensions` / `measures` / `main_data` protocol and do not add dedicated response fields. The number and order of results are determined by `limit_size` and `group_by[0].sort` in the block configuration; when consuming the return, keep the server-side order of `main_data`, and do not reverse or rearrange it yourself.

<a id="结构特征"></a>
#### Structural characteristics

- `dimensions`: usually has `1~2` dimensions
  - Without grouped aggregation: usually 1 dimension
  - With grouped aggregation enabled: usually 2 dimensions
- `measures`: measure definition array
- `main_data`: row data expanded by "dimension combination"

<a id="这类数据代表什么"></a>
#### What this type of data represents

What two-dimensional charts return is essentially an **aggregated result table**:

- Each row represents one dimension value, or one set of dimension combinations;
- Each measure value represents the computed measure result under that dimension;
- If the chart has grouped aggregation enabled, then each row represents a combined result of "primary dimension + group dimension";
- If the chart is a line chart, area chart, or similar chart with a time axis, the first dimension can usually be understood as the horizontal axis, and the measure as the vertical axis value;
- If the chart is a pie chart, donut chart, or similar proportion chart, each row can usually be understood as the category and value corresponding to one sector.

In other words, when AI reads this type of result, it can treat it as a "statistical detail table aggregated by certain dimensions", suitable for further sorting, Top N, proportion explanation, grouped comparison, and trend summarization.

<a id="示例-1普通二维图表无分组聚合"></a>
#### Example 1: Ordinary two-dimensional chart (no grouped aggregation)

```json
{
  "dimensions": [
    {
      "field_name": "文本",
      "alias": "dim_5bKp"
    }
  ],
  "measures": [
    {
      "aggregation": "count_all",
      "field_name": "Count",
      "alias": "me_Y291bnRfYWxsX0NvdW50"
    }
  ],
  "main_data": [
    {
      "dim_5bKp": {"value": "A"},
      "me_Y291bnRfYWxsX0NvdW50": {"value": 3}
    },
    {
      "dim_5bKp": {"value": "B"},
      "me_Y291bnRfYWxsX0NvdW50": {"value": 2}
    },
    {
      "dim_5bKp": {"value": "C"},
      "me_Y291bnRfYWxsX0NvdW50": {"value": 2}
    }
  ]
}
```

This can be interpreted as:

- The dimension field is "Text"
- The measure is "count of total records"
- When the "Text" field is `A`, the corresponding `Count` measure value is `3`
- When the "Text" field is `B`, the corresponding `Count` measure value is `2`
- When the "Text" field is `C`, the corresponding `Count` measure value is `2`

<a id="示例-2二维图表开启分组聚合"></a>
#### Example 2: Two-dimensional chart (grouped aggregation enabled)

```json
{
  "dimensions": [
    {
      "field_name": "文本",
      "alias": "dim_5bKp"
    },
    {
      "field_name": "单选",
      "alias": "dim_5aSl"
    }
  ],
  "measures": [
    {
      "aggregation": "count_all",
      "field_name": "Count",
      "alias": "me_YW91bnR"
    }
  ],
  "main_data": [
    {
      "dim_5bKp": {"value": "A"},
      "dim_5aSl": {"value": "a-1"},
      "me_YW91bnR": {"value": 2}
    },
    {
      "dim_5bKp": {"value": "A"},
      "dim_5aSl": {"value": "a-2"},
      "me_YW91bnR": {"value": 1}
    },
    {
      "dim_5bKp": {"value": "B"},
      "dim_5aSl": {"value": "b-1"},
      "me_YW91bnR": {"value": 1}
    },
    {
      "dim_5bKp": {"value": "C"},
      "dim_5aSl": {"value": "c-1"},
      "me_YW91bnR": {"value": 2}
    }
  ]
}
```

This can be interpreted as:

- The first dimension is "Text", the second dimension is "Single Select", and the measure is "count of total records"
- When the "Text" field is `A` and the "Single Select" field is `a-1`, the corresponding measure value is `2`
- When the "Text" field is `A` and the "Single Select" field is `a-2`, the corresponding measure value is `1`
- When the "Text" field is `B` and the "Single Select" field is `b-1`, the corresponding measure value is `1`
- When the "Text" field is `C` and the "Single Select" field is `c-1`, the corresponding measure value is `2`
- If aggregated by the "Text" field, then when the "Text" field is `A`, the total measure value is `3`; when it is `B`, the total measure value is `1`; when it is `C`, the total measure value is `2`

---

<a id="二词云"></a>
### II. Word cloud

<a id="结构特征-1"></a>
#### Structural characteristics

The word cloud protocol still follows the structure of `dimensions + measures + main_data`, but the semantics are slightly different:

- `dimensions` corresponds to the field being tokenized;
- Each row of `main_data` represents one word;
- The value of `measure` represents the statistical value computed after grouping by that word.

<a id="这类数据代表什么-1"></a>
#### What this type of data represents

What the word cloud returns is not a "list of original text", but an **aggregated statistical result grouped by word**:

- `dimensions` defines the source field being tokenized;
- `measure` corresponds to the statistical value for that word within the current chart's statistical scope; the specific meaning depends on the aggregation method and measure field;
- Each row of `main_data` can be understood as "a certain word + the statistical result corresponding to that word", where the specific value of that dimension is the split-out word;
- The returned result is usually already computed in combination with the chart's current filter conditions, time range, data permissions, and other context.

Therefore, when AI reads word cloud data, it is more suitable for "keyword ranking", "hot word explanation", "analysis of results aggregated by word", and "topic summarization", rather than understanding it as individual text records.

<a id="示例"></a>
#### Example

```json
{
  "dimensions": [
    {
      "field_name": "文本",
      "alias": "dim_5bKp"
    }
  ],
  "measures": [
    {
      "aggregation": "count_all",
      "field_name": "Count",
      "alias": "me_YW91bnR"
    }
  ],
  "main_data": [
    {
      "dim_5bKp": {"value": "A"},
      "me_YW91bnR": {"value": 3}
    },
    {
      "dim_5bKp": {"value": "B"},
      "me_YW91bnR": {"value": 2}
    },
    {
      "dim_5bKp": {"value": "C"},
      "me_YW91bnR": {"value": 2}
    }
  ]
}
```

This can be interpreted as:

- The tokenized field being counted is "Text"
- The measure in the current example is `count_all(Count)`, so the statistical value here can be understood as "the total record count after grouping by word"
- When the tokenization result is `A`, the corresponding statistical value is `3`
- When the tokenization result is `B`, the corresponding statistical value is `2`
- When the tokenization result is `C`, the corresponding statistical value is `2`
- Sorted by statistical value, the tokenization result `A` has the highest value
- The tokenization results `B` and `C` have the same statistical value, indicating they are in the same tier

---

<a id="三指标卡statistics"></a>
### III. Metric card (statistics)

In addition to the main value, a metric card may also contain year-over-year/month-over-month and trend results, making it the most structurally special type in this command.

<a id="结构特征-2"></a>
#### Structural characteristics

- `measures`: **has exactly one measure**
- `main_data`: usually only one row, representing the total measure value
- `comparison_data`: optional, represents the current period value and comparison period value
- `trend_data`: optional, represents the trend series
- `dimensions`: may contain year-over-year/month-over-month date fields and trend date fields

<a id="这类数据代表什么-2"></a>
#### What this type of data represents

What a metric card returns is essentially a **main measure summary**, plus optional comparison information and trend information:

- `main_data` represents the most core and prominent main value of the current card; it is usually the total record count of a table, or the aggregate value of a field, and itself **does not carry a time period concept**;
- `comparison_data` represents the two values used for year-over-year/month-over-month display, usually the "current period value" and the "comparison period value"; they represent the total record count under a certain time period, or the aggregate value of a field;
- `trend_data` represents the change trajectory of this measure over a period of time, used to support trend judgment;
- `dimensions` in a metric card is usually not used for primary grouping display, but rather provides semantic explanation for `trend_data` or year-over-year/month-over-month related date fields.

For example:

- `main_data = 7` can be understood as the main data displayed by the current card, for example, the current total record count of a table is `7`;
- `comparison_data[0] = 6` represents the current value under a certain comparison period, for example, "total records this month = 6";
- Therefore, `main_data` and `comparison_data[0]` **are not necessarily equal**, because the two express slightly different scopes.

Therefore, when interpreting a metric card, AI should prioritize answering these questions:

1. What is the current main value;
2. Compared with the comparison period, is it rising, falling, or flat;
3. Is the overall trend growing, fluctuating, or declining;
4. Are there obvious abnormal peaks or troughs.

> [!NOTE]
> When a metric card **specifies both year-over-year/month-over-month and trend**, the order of date dimensions in `dimensions` is fixed:
> 1. The first element is the date dimension corresponding to the **trend**;
> 2. The second element is the date dimension corresponding to **year-over-year/month-over-month**.
>
> Also note: `comparison_data` itself usually **does not directly carry date fields**; it only gives the "current period value / comparison period value".
> The first date dimension in `dimensions` will directly appear in `trend_data` as the time column of the trend series;
> The second date dimension is mainly used to supplement the semantics of "which type of comparison-related date field this card is configured with".

<a id="示例-1"></a>
#### Example

```json
{
  "dimensions": [
    {
      "field_name": "日期",
      "alias": "dim_ZGF0ZQ"
    },
    {
      "field_name": "日期2",
      "alias": "dim_ZGF0ZTI"
    }
  ],
  "measures": [
    {
      "aggregation": "count_all",
      "field_name": "Count",
      "alias": "me_YW91b"
    }
  ],
  "main_data": [
    {
      "me_YW91b": {"value": 7}
    }
  ],
  "comparison_data": [
    {
      "me_YW91b": {"value": 6}
    },
    {
      "me_YW91b": {"value": 0}
    }
  ],
  "trend_data": [
    {
      "dim_ZGF0ZQ": {"value": "2026-01-15"},
      "me_YW91b": {"value": 1}
    },
    {
      "dim_ZGF0ZQ": {"value": "2026-01-17"},
      "me_YW91b": {"value": 1}
    },
    {
      "dim_ZGF0ZQ": {"value": "2026-03-22"},
      "me_YW91b": {"value": 1}
    },
    {
      "dim_ZGF0ZQ": {"value": "2026-04-24"},
      "me_YW91b": {"value": 2}
    },
    {
      "dim_ZGF0ZQ": {"value": "2026-05-01"},
      "me_YW91b": {"value": 1}
    }
  ]
}
```

This can be interpreted as:

- Current main measure value = `7`
- The current main measure value does not carry a time period concept and can be understood as the current card's main data
- comparison_data[0] = current period value `6`, for example, the statistical value under a certain time period (such as this month)
- comparison_data[1] = comparison period value `0`
- `dimensions[0]` corresponds to the trend date dimension, so it actually appears in `trend_data`
- `dimensions[1]` corresponds to the year-over-year/month-over-month related date dimension, used to supplement comparison semantics
- trend_data shows the change series of this measure over time
- From comparison_data, the current period is rising compared with the comparison period, and the comparison period value is 0
- From trend_data, this measure does not have a value every day, but appears on several discrete dates
- The highest point in the trend series appears on `2026-04-24`, with value `2`
- Most of the other dates that appear are `1`, indicating overall fluctuation, but no sustained rapid growth trend for now

> [!NOTE]
> `comparison_data` only tells you the "current value / comparison value", and **does not additionally mark the date range text**. If the user needs a complete explanation of whether it is "compared with last week" or "compared with last month", it usually requires further judgment in combination with the component configuration or interface context.

---

<a id="如何正确解读返回值"></a>
## How to correctly interpret return values

It is recommended to read in the following order:

1. **First look at `dimensions`**: confirm which field each `dim_*` alias corresponds to;
2. **Then look at `measures`**: confirm what aggregation method each `me_*` alias is;
3. **Finally read `main_data` / `comparison_data` / `trend_data`**: restore aliases to "field name + measure name" before interpreting.

<a id="推荐解释模板"></a>
### Recommended interpretation templates

If you want to convert results into natural language, it is recommended not to merely "restate the values", but to cover the following levels as much as possible:

1. **First explain the measure meaning**: state whether the measure represents "total record count", "sum of a certain field", "average value", etc.;
2. **Then give the core result**: clarify the current main value, main categories, main combinations, or main word items;
3. **Do sorting or Top N extraction**: point out the highest, lowest, top few, and same tier;
4. **Supplement grouping/comparison relationships**: if there is a second dimension or comparison_data, explain the comparison objects and differences;
5. **Analyze trends or anomalies**: if there is a time series, point out rises, falls, fluctuations, peaks, and troughs;
6. **Finally give a one-sentence conclusion**: summarize the most noteworthy information.

You can refer to the following templates:

- Two-dimensional charts:
  - Basic template: `按 <维度字段> 统计，当前指标 <指标含义>；其中 <维度值1>=<指标值1>，<维度值2>=<指标值2> ...`
  - Enhanced template: `按 <维度字段> 统计，当前指标表示 <指标含义>。从结果看，<Top1维度值> 的值最高，为 <Top1值>；<Top2维度值> 和 <Top3维度值> 紧随其后。若按 Top N 看，前 <N> 项合计贡献了 ...；若看低值项，<低值维度值> 最低，为 <低值>。整体上，<一句总结>`

- Grouped aggregation charts:
  - Basic template: `按 <维度1> 统计，并以 <维度2> 分组，得到 <组合1>=<值1>，<组合2>=<值2> ...`
  - Enhanced template: `当前指标表示 <指标含义>。按 <维度1> 拆分后，不同 <维度2> 组之间存在明显差异：例如 <组合1> = <值1>，<组合2> = <值2>。如果按 <维度1> 汇总，<Top1维度1值> 总值最高，为 <汇总值>；如果看组内对比，<某组> 在 <某维度1值> 下表现最强 / 最弱。整体说明 <一句总结>`

- Word cloud:
  - Basic template: `按分词结果统计，当前指标表示 <指标含义>；其中 <词1>=<统计值1>，<词2>=<统计值2> ...`
  - Enhanced template: `当前词云反映的是“按词分组后的 <指标含义>”。从结果看，<Top1词> 的值最高，为 <值1>，说明它是当前最突出的关键词；<Top2词>、<Top3词> 处于第二梯队。如果按 Top N 看，主要关注词集中在 <主题A>、<主题B>；如果有多个词数值接近，可归为同一热点层级。整体上，这组词更适合用来总结 <主题/热点/关注点>`

- Metric card:
  - Basic template: `当前主指标值为 <main_data>；当前周期值为 <comparison_data[0]>；对比周期值为 <comparison_data[1]>；趋势上 ...`
  - Enhanced template: `当前主指标表示 <指标含义>，主值为 <main_data>。若看周期比较，当前周期值为 <comparison_data[0]>，对比周期值为 <comparison_data[1]>，因此整体表现为 <上升/下降/持平>。若看趋势序列，最高点出现在 <日期>，值为 <峰值>；最低点出现在 <日期>，值为 <低值>；整体走势表现为 <持续增长/阶段波动/明显回落>。如果需要给出结论，可总结为：<一句总结>`

> [!TIP]
> When the user explicitly requests "help me analyze", "help me summarize", or "help me find anomalies / Top N / trends", prioritize the enhanced template rather than merely restating the raw values one by one.

---

<a id="常见工作流"></a>
## Common workflows

<a id="场景-1用户要拿这个图表当前展示的数据"></a>
### Scenario 1: The user wants to "get the data currently displayed by this chart"

```bash
# If block_id is already known, read the result directly
lark-cli base +dashboard-block-get-data \
  --base-token xxx \
  --block-id chtxxxxxxxx
```

<a id="场景-2用户说帮我分析这个图表但你还不知道它是什么组件"></a>
### Scenario 2: The user says "help me analyze this chart", but you do not yet know what component it is

```bash
# First look at the component configuration to confirm whether it is a chart type that supports computation
lark-cli base +dashboard-block-get \
  --base-token xxx \
  --dashboard-id blk_xxx \
  --block-id chtxxxxxxxx

# Then read the final computed result
lark-cli base +dashboard-block-get-data \
  --base-token xxx \
  --block-id chtxxxxxxxx
```

<a id="场景-3用户要找仪表盘里哪个图的结果异常"></a>
### Scenario 3: The user wants to find "which chart in the dashboard has abnormal results"

```bash
# First list the components
lark-cli base +dashboard-block-list \
  --base-token xxx \
  --dashboard-id blk_xxx

# Then fetch results one by one for suspicious blocks
lark-cli base +dashboard-block-get-data \
  --base-token xxx \
  --block-id chtxxxxxxxx
```

---

<a id="何时优先用这个命令"></a>
## When to prefer this command

- The user says "get me the data / results / metrics computed by this chart"
- The user already knows `block_id`, and the goal is to **read the results** rather than view the configuration
- The user subsequently wants the AI to explain, summarize, compare, or conclude on the chart results
- You only care about the aggregated output at the chart level and do not need to go back to the underlying table to read records one by one

<a id="何时不要误用"></a>
## When not to misuse it

- Want to see the block's `data_config`, name, type, or layout → use `+dashboard-block-get`
- Want to list which components are in the dashboard → use `+dashboard-block-list`
- Want to modify or create a component → use `+dashboard-block-update` / `+dashboard-block-create`
- Want to see raw record details rather than chart aggregation results → go back to `record-*`
- The target is a text component → this command does not apply

---

<a id="常见误区"></a>
## Common misconceptions

<a id="误区-1把这个命令当成获取-block-详情"></a>
### Misconception 1: Treating this command as "get block details"

It is not. This command does not return:

- block name
- block type
- layout
- `data_config`
- the dashboard it belongs to

All of these should be obtained via `+dashboard-block-get`.

<a id="误区-2以为它返回的是原始记录"></a>
### Misconception 2: Assuming it returns raw records

It does not. It returns the **final aggregated result of the chart**. If the chart itself applies filters, grouping, aggregation, or time window limits, the returned value reflects the chart's perspective, not the full raw details of the underlying table.

<a id="误区-3直接把-alias-当真实字段名读"></a>
### Misconception 3: Reading alias directly as a real field name

You should not. alias is merely a key in the protocol; you must combine it with `dimensions` / `measures` to restore the semantics.

<a id="误区-4看到指标卡的-comparison_data-就以为已经知道同比环比周期文本"></a>
### Misconception 4: Seeing a metric card's `comparison_data` and assuming you already know the "year-over-year/month-over-month period text"

Not necessarily. It only gives the comparison value, not necessarily the period label. To precisely explain the comparison window, component configuration or UI context is usually still needed.

---

<a id="dry-run-用途"></a>
## Purpose of dry-run

Can be used to confirm the API path that will ultimately be called:

```bash
lark-cli base +dashboard-block-get-data \
  --base-token bascn_example_token \
  --block-id chtxxxxxxxx \
  --dry-run \
  --format pretty
```

You should see something like:

```text
GET /open-apis/base/v3/bases/bascn_example_token/dashboards/blocks/chtxxxxxxxx/data
```

Suitable for the following scenarios:

- Verify whether `base_token` / `block_id` are passed correctly;
- Debug commands generated by the agent;
- Confirm the request structure when writing automated tests.

---

<a id="参考"></a>
## References

- [lark-base-dashboard.md](lark-base-dashboard.md) — dashboard module general guide
- `+dashboard-block-get` — get block metadata
- [Dashboard Block configuration](lark-base-dashboard-block-config.md) — data_config structure and component type descriptions
