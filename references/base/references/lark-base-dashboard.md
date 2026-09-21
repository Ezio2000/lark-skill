<a id="dashboard仪表盘数据看板模块指引"></a>
# Dashboard (Dashboard/Data Dashboard) Module Guide


Dashboard is the data visualization dashboard in Base, which can turn table data into **components** (charts, metric cards, etc.) for display.

<a id="核心概念"></a>
## Core Concepts

- **Dashboard**: A container that holds multiple components
- **Block (Component)**: A single visualization element in the dashboard (bar chart, line chart, pie chart, metric card, etc.)
- **data_config**: The data source configuration for a component (table name, fields, grouping, etc.)

<a id="能力速览"></a>
## Capability Overview

| What you want to do | Use these commands | Key documentation |
|------|-----------|---------|
| Create/delete/rename | `+dashboard-create/delete/update` | "Dashboard Management" below on this page |
| Add a component to a dashboard | `+dashboard-block-create` | First locate the dashboard, table, and fields, then read [Dashboard Block Configuration](lark-base-dashboard-block-config.md) to construct `data_config` |
| Modify a component | `+dashboard-block-update` | First read the current block state, then read [Dashboard Block Configuration](lark-base-dashboard-block-config.md) to decide which top-level keys to replace |
| Specify exact position and size of a component on create/update | `+dashboard-block-create/update --position` | "Exact Layout --position vs +dashboard-arrange" below on this page |
| View which components a dashboard has | `+dashboard-get` or `+dashboard-block-list` | "View Dashboard" below on this page |
| Read chart computation results | `+dashboard-block-get-data` | Returns the final chart data protocol; if you need block metadata, first use `+dashboard-block-get` |
| Intelligently rearrange component layout | `+dashboard-arrange` | When the user explicitly requests rearrangement, or as final cleanup for a dashboard newly created in this session; cannot specify `x/y/w/h`, exact position, or size |

<a id="精确布局---position-vs-dashboard-arrange"></a>
## Exact Layout --position vs +dashboard-arrange

create/update optionally accepts `--position`, using 12-column grid coordinates to precisely specify the placement and size of a single component: `{"x","y","w","h"}`, where `x`/`y` are the top-left coordinates (>=0), `w` is the width (1..12, and `x+w<=12`), and `h` is the height (>=1). It is attached at the top level of the request body, at the same level as `name`/`type`/`data_config`.

> [!IMPORTANT]
> - **All four keys must be present and all must be numbers**: `position` is submitted as a whole and does not merge field by field, so passing only `{"x":6}` does not mean "only move the position without changing the size"; it is a position missing three items. Incomplete objects are rejected locally (including an explicit `null`).
> - Coordinate **values are not validated locally**: out-of-bounds, negative, or overlapping coordinates are sent to the server as-is, and the server automatically rearranges them. Callers should still prioritize planning coordinates within the 12-column range and non-overlapping, to avoid automatic rearrangement changing the expected placement.
> - Do not pass `--position`: create automatically packs on the server side, and update keeps the current layout unchanged.
> - Only use `--position` when the user explicitly provides `x/y/w/h`, specific rows/columns/order, each component's width and height, or size ratios that can be directly converted. "Adjust the layout", "beautify", "fill", and "tile" by themselves do not count as exact constraints; when there are no component-level coordinates or sizes, prioritize using `+dashboard-arrange` for whole-dashboard arrangement.
> - A successful command is considered a successful write; generally there is no need to call `+dashboard-block-get` / `+dashboard-block-list` just to read back the position; a successful response does not mean the final rendered position has been verified by read-back.

<a id="statistics-指标卡数值格式"></a>
## statistics Metric Card Value Format

The `statistics` component can set `formatName` and `precision` in `data_config.number_format` during create/update. create validates the component type and subfields; update does not accept `--type`, only validates the `number_format` subfields, and then the server decides based on the existing block type. For enums, precision ranges, update semantics, and copyable templates, read [Dashboard Block Configuration](lark-base-dashboard-block-config.md).

<a id="典型场景工作流"></a>
## Typical Scenario Workflows

<a id="场景-1从-0-到-1-创建仪表盘"></a>
### Scenario 1: Create a Dashboard from Scratch

When creating a dashboard from scratch, plan the types and number of components according to user needs, and note the following key points:

- Aggregation method: When creating metric cards or distribution charts, prioritize writing the aggregation into `data_config`; only use `+data-query` first for Top N, field value exploration, complex filter validation, or helper summary table scenarios.
- Dry-run boundary: Simple metric cards, distribution charts, and trend charts already constructed from templates do not need to be `--dry-run` one by one before actual creation; only dry-run when debugging JSON, checking the request body, complex self-made `data_config`, or handling API validation errors.
- Verification method: A successful return from the create API means the write succeeded. Only when the result is uncertain, use `+dashboard-get` or `+dashboard-block-list` once to confirm that the dashboard and components exist; do not call `+dashboard-block-get-data` component by component just to confirm creation.
- Layout method: When the user has not provided component-level coordinates or sizes, after creation use `+dashboard-arrange` once for whole-dashboard arrangement; only include `--position` in create when the user explicitly provides executable exact layout constraints, in which case arrange is usually no longer needed.

Example: Build a sales data analysis dashboard

```bash
# Step 1: Create a blank dashboard
lark-cli base +dashboard-create --base-token xxx --name "销售数据分析"
# Record the returned dashboard_id

# Step 2: Get data source information
lark-cli base +table-list --base-token xxx
lark-cli base +field-list --base-token xxx --table-id <table_id>

# Step 3: Plan which components should be created (determine component types and count based on user needs)
# For example: total sales (metric card), monthly trend (line chart), owner Top N (ranking)

# Step 4: Create each component in order (must be executed serially, not concurrently)
# Important: Before creating a component, first determine dashboard_id, component name/type, and real table fields
# Then read lark-base-dashboard-block-config.md to understand the data_config structure, component types, and filter rules

# Component 1
lark-cli base +dashboard-block-create \
  --base-token xxx \
  --dashboard-id blk_xxx \
  --name "总销售额" \
  --type statistics \
  --data-config '{"table_name":"订单表","series":[{"field_name":"金额","rollup":"SUM"}]}'

# Component 2 (execute after the previous one completes)
lark-cli base +dashboard-block-create \
  --base-token xxx \
  --dashboard-id blk_xxx \
  --name "月度趋势" \
  --type line \
  --data-config '{"table_name":"订单表","series":[{"field_name":"金额","rollup":"SUM"}],"group_by":[{"field_name":"月份","mode":"integrated"}]}'

# Continue creating other components...

# Ranking component: when limit_size and sort are omitted, they default to 10 and value desc respectively
lark-cli base +dashboard-block-create \
  --base-token xxx \
  --dashboard-id blk_xxx \
  --name "负责人销售额 Top 10" \
  --type ranking \
  --data-config '{"table_name":"订单表","series":[{"field_name":"金额","rollup":"SUM"}],"group_by":[{"field_name":"负责人"}]}'

# Step 5: After components are created, optionally use arrange for intelligent rearrangement (optional when --position is not used)
# The default layout may not be aesthetically pleasing; arrange automatically optimizes the layout based on the number and types of components
# If any component uses an explicit --position, skip this step; unless the user explicitly agrees to give up the exact layout
# If the user has not requested beautification/rearrangement, you may also skip this; this does not affect whether the dashboard and components were created successfully
lark-cli base +dashboard-arrange \
  --base-token xxx \
  --dashboard-id blk_xxx
```

<a id="场景-2在已有仪表盘上添加新组件"></a>
### Scenario 2: Add New Components to an Existing Dashboard

```bash
# Step 1: List dashboards and locate the current dashboard
lark-cli base +dashboard-list --base-token xxx
# Get the target dashboard_id

# Step 2: Plan component types and data sources based on user requirements
# It is recommended to first view the existing components of the current dashboard to avoid duplicate creation, or to use them as reference
lark-cli base +dashboard-get --base-token xxx --dashboard-id blk_xxx

# Step 3: Get data source information
lark-cli base +table-list --base-token xxx
lark-cli base +field-list --base-token xxx --table-id <table_id>

# Step 4: Create each new component in order (must be executed serially, not concurrently)
# Important: First determine dashboard_id, component name/type, and real table fields
# Then read lark-base-dashboard-block-config.md to understand the data_config structure
lark-cli base +dashboard-block-create \
  --base-token xxx \
  --dashboard-id blk_xxx \
  --name "新组件名" \
  --type column \
  --data-config '{...}'
```

<a id="场景-3编辑已有组件"></a>
### Scenario 3: Edit an Existing Component

> [!IMPORTANT]
> `+dashboard-block-update` **cannot modify the component's `type`** (chart type); it can only update `name`, `data_config`, and the optional `position`.
> If you need to change the component type, you must first delete it and then recreate it.

```bash
# Step 1: List dashboards and locate the current dashboard
lark-cli base +dashboard-list --base-token xxx

# Step 2: List components and get the target component
lark-cli base +dashboard-block-list --base-token xxx --dashboard-id blk_xxx
# Get the target block_id
# Tip: Viewing existing components can serve as reference, or help check whether similar components were created repeatedly

# Step 3: Get the component's current details
lark-cli base +dashboard-block-get --base-token xxx --dashboard-id blk_xxx --block-id chtxxxxxxxx

# Step 4: Prepare the update based on the user's edit request
# If the edit request involves data source changes, you need to first get the data source information
lark-cli base +table-list --base-token xxx
lark-cli base +field-list --base-token xxx --table-id <table_id>

# Step 5: Execute the update
# Important: First read the current block's name/type/data_config
# Then read lark-base-dashboard-block-config.md to understand the data_config update rules
lark-cli base +dashboard-block-update \
  --base-token xxx \
  --dashboard-id blk_xxx \
  --block-id chtxxxxxxxx \
  --data-config '{...}' \
  --position '{...}'   # Optional; pass only when the layout needs to be adjusted

# Ranking only modifies Top N; it does not overwrite grouping, metrics, filters, or sorting
lark-cli base +dashboard-block-update \
  --base-token xxx \
  --dashboard-id blk_xxx \
  --block-id chtxxxxxxxx \
  --data-config '{"limit_size":20}'

```

<a id="场景-4重排仪表盘布局"></a>
### Scenario 4: Rearrange Dashboard Layout

Use this when the user requests adjusting the layout, rearranging, beautifying, filling, or tiling, but does not provide component-level coordinates or sizes. After locating the dashboard, use `+dashboard-arrange` once for whole-dashboard arrangement (for a dashboard newly created from scratch in this session, arrange once after all components are created).

> [!CAUTION]
> - The arrangement result is a **server-side intelligent recommendation** and may not fully match user expectations
> - `+dashboard-arrange` cannot specify `x/y/w/h`, exact position, or size; the arrangement logic is **adaptive**; only switch to `--position` when the user explicitly provides executable component-level coordinates, rows/columns, or size constraints
> - **Not recommended** to call automatically on an existing dashboard unless the user explicitly requests it
> - When the user only requests general rearrangement, beautification, filling, or tiling, use `+dashboard-arrange` for whole-dashboard arrangement
> - If the arrangement result is not ideal, you may adjust further based on user feedback; do not probe raw `lark-cli api`, source code, or undisclosed layout parameters just to achieve an effect

```bash
# Step 1: List dashboards and locate the target dashboard
lark-cli base +dashboard-list --base-token xxx

# Step 2: Execute intelligent rearrangement
lark-cli base +dashboard-arrange \
  --base-token xxx \
  --dashboard-id blk_xxx
```

<a id="场景-5读取仪表盘或组件现状"></a>
### Scenario 5: Read the Current State of a Dashboard or Component

**Choose the query method:**
- Want to see the overall dashboard structure (including theme, all component names and types) → use **Method A**
- Only want to quickly see which components exist → use **Method B**
- Want to see a component's detailed data_config → use **Method C**
- Want to see the actual computed data of a chart/metric card → use **Method D**

When the user requests reading "all charts" or the "complete dashboard", first use Method B to enumerate all blocks with pagination: use `--page-size 100`; if `has_more=true` is returned, continue passing the `page_token` returned on this page to `--page-token` until `has_more=false`. After collecting everything, finalize each block; do not return only the subset for which get-data succeeded:

1. Charts or metric cards: use Method D to read the computation results.
2. `text`: use Method C; the body is located in `data_config.text`; text has no computation results, but it is part of the complete dashboard content.
3. get-data returns an unsupported chart type: first use Method C to read the real `data_config`, confirm `table_name`, dimensions, metrics, aggregation, and filters, then follow the [Record Query and Analysis SOP](lark-base-record-query-and-analysis-sop.md) to use `+data-query` to reconstruct results with the same semantics. Fields must come from the real configuration and table structure, and must not be guessed; when equivalent reconstruction is impossible, clearly report the limitation and do not silently omit that block.

```bash
# Step 1: List dashboards and locate the current dashboard
lark-cli base +dashboard-list --base-token xxx

# Step 2: View details based on user requirements

# Method A: View the overall dashboard situation (including the list of all components)
lark-cli base +dashboard-get --base-token xxx --dashboard-id blk_xxx

# Method B: List all components
lark-cli base +dashboard-block-list \
  --base-token xxx \
  --dashboard-id blk_xxx \
  --page-size 100

# Method C: View the detailed configuration of a component
lark-cli base +dashboard-block-get --base-token xxx --dashboard-id blk_xxx --block-id chtxxxxxxxx

# Method D: View the computation results of a chart component (AI-friendly chart protocol)
lark-cli base +dashboard-block-get-data --base-token xxx --block-id chtxxxxxxxx

# Finally: Organize the current state information obtained and tell the user
```

When you need to read the computation results of multiple components, first use Method B to get the real `block_id` (use `--page-size 100`; if `has_more=true`, continue passing the returned `page_token` to `--page-token` until `has_more=false`), then follow the multi-component paradigm in [lark-base-dashboard-block-get-data.md](lark-base-dashboard-block-get-data.md) to read serially within a single shell tool call; do not split each block into separate model turns. Text components have no computation results and should be skipped.

<a id="组件类型选择"></a>
## Component Type Selection

The component `type` determines the display form:

| What the user wants to see | Which type to choose | Description |
|-------------|------------|------|
| Data trends (changes over time) | line | Line chart component |
| Category comparison (which is higher or lower) | column | Bar chart component |
| Proportion distribution (share of each part) | pie | Pie chart component |
| A single key metric | statistics | Metric card component |
| Single-dimension Top N ranking | ranking | Ranking component, single grouping, single metric |
| Rich text description/title/annotation | text | Text component (supports Markdown) |

Detailed component types and complete data_config rules: [Dashboard Block Configuration](lark-base-dashboard-block-config.md)

<a id="常见问题"></a>
## FAQ

**Q: How do I write the command and data_config for creating a component?**
A:
1. First determine `dashboard_id`, component `name`, component `type`, and the real table fields
2. Then read [Dashboard Block Configuration](lark-base-dashboard-block-config.md) to understand:
   - Copyable templates for all component types
   - filter condition format
   - Field type and operator correspondence table

**Q: Why did component creation fail?**
A: Common reasons:
- `table_name` uses table_id instead of the table name (must use the table name, such as "Orders Table")
- `series` and `count_all` exist at the same time (must choose one, they are mutually exclusive)
- Field name spelling error (must use the real field name obtained via `+field-list`, guessing is prohibited)
- Component creation executed concurrently (must be serial, wait for the previous one to complete before executing the next)

**Q: Can I create multiple components at once?**
A: No, it must be executed serially. Wait for the previous `+dashboard-block-create` to complete before executing the next.

**Q: Can a component's `type` be changed after creation?**
A: No. `+dashboard-block-update` can only modify `name`, `data_config`, and `position`, and cannot modify `type`.

**Q: How do I write the command and data_config for updating a component?**
A:
1. First read the current block, confirm `block_id`, the current `type`, and the existing `data_config`
2. Then read [Dashboard Block Configuration](lark-base-dashboard-block-config.md) to understand the data_config structure

**data_config update strategy (top-level key merge)**:
- Only pass the top-level fields that need to be modified (such as `series`, `filter`)
- Top-level fields not passed (such as `group_by`) automatically retain their original values
- However, within each passed field it is usually a **full replacement** (for example, passing a new `filter` completely overwrites the old `filter`); `number_format` is the exception, merging by subfield, see the number_format section of [Dashboard Block Configuration](lark-base-dashboard-block-config.md)

**Q: What is the use of viewing existing components?**
A: Before "adding a new component" or "editing a component", viewing existing components can:
- Help you understand which visualizations the current dashboard already has
- Avoid repeatedly creating similar components
- Use the data_config structure of existing components as a template for reference

**Q: I want to directly take the chart's computed results for AI analysis; what should I use?**
A: Use `+dashboard-block-get-data`. It returns chart protocol JSON (common fields include `dimensions`, `measures`, `main_data`; metric cards may also have `comparison_data`, `trend_data`), and does not return block name, type, layout, or `data_config`; when you need this metadata, first use `+dashboard-block-get`.

<a id="写入前检查"></a>
## Pre-Write Checklist

- Before creating a block, you must know `base_token`, `dashboard_id`, component `name/type`, and `data_config`.
- Before updating a block, you must know `base_token`, `dashboard_id`, `block_id`, and have read the current block.
- In `data_config`, use table names and field names, not table_id / field_id; names must come from the real returns of `+table-list` / `+field-list`.
