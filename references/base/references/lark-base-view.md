<a id="view类型选择与生命周期"></a>
# View: Type Selection and Lifecycle

Read this reference before editing any View, including creation, renaming, configuration changes, and deletion.

A View is a way to display and organize the same Table, sharing the underlying records; creating a view does not copy records. Only create views that satisfy the current need; do not create all five types by default. Use Record commands for one-off queries; create a View when users need to browse, process, or share over the long term.

<a id="选择视图"></a>
## Selecting a View

**Grid is the most commonly used default view, convenient for viewing, entering, and modifying data. Use Grid when there is no clear special display requirement; do not automatically create other types just because the data contains status, date, or attachment fields. Only when the user explicitly needs column-based processing, time-span comparison, calendar positioning, or card browsing should you choose Kanban, Gantt, Calendar, or Gallery respectively.**

| Type | Display method and advantages | When to choose | Priority configuration |
|---|---|---|---|
| `grid` Grid | One record per row, one field per column, in a familiar table format, convenient for viewing, entering, and modifying data; display can be adjusted via filter, group, and sort. | The most commonly used default view; prefer it for daily data reading and writing when there is no special display requirement. | Visible fields and their order; filter, group, and sort as needed. |
| `kanban` Kanban | Columns arranged horizontally by a grouping field, each column showing record cards for that group; sort controls the order of records within a group. | When items need to be processed in columns by status, stage, or category; prefer a single-select/multi-select field with clear options as the grouping basis. | Grouping field, visible card fields, in-group sort; optional cover when attachments exist. Multi-select grouping cannot be directly used as mutually exclusive partition statistics. |
| `gantt` Gantt | Table details on the left, time bars for the same set of records on the right; intuitively see start and end times, duration, and schedule overlaps. The left side supports visible fields, filter, group, and sort. | When each record represents a task, project, or other entity with a time span, with the focus on comparing schedules. | `timebar` Bind the start, end, and title fields; usually keep only 1–3 key fields on the left to leave space for the timeline. |
| `calendar` Calendar | Position records into calendar date cells by a time field, displayed as events; convenient for answering "what is happening on a given day". | Release plans, activities, appointments, task dates, etc., with the focus on browsing by day/week/month. | `timebar` Bind the start, end, and title fields; configure display fields and filter. Do not apply the generic grouping and sort of Grid. |
| `gallery` Gallery | Records are arranged directly as cards, not divided into columns by status; key content can be paired with an attachment cover. | Collections such as products, assets, cases, and people that need to be browsed card by card; does not require every record to have an image. | Card display fields, optional cover, filter, and sort. |

Selection shortcut: **daily data reading and writing, no special display requirement → grid; process by status/category → kanban; compare time spans → gantt; find events by date → calendar; browse card content → gallery.** Both Gantt and Calendar can display time-related entities; the difference is that the former emphasizes span and overlap, while the latter emphasizes date position.

<a id="few-shot按目的创建与配置"></a>
## Few-shot: Create and Configure by Purpose

The following are independent selection examples, not a set of steps that must all be executed. `BASE_TOKEN` and `TABLE_ID` use resolved real resource coordinates; field name examples assume the target table already has the corresponding fields, and before configuring, use `+field-list` to verify type and name. `--view-id` accepts a real ID or name; the examples use a unique name for a newly created view, and when the name is not unique, use the actual returned ID.

<a id="表格查看与维护grid"></a>
### Table viewing and maintenance: grid

Requirement: "View tasks grouped by project, prioritizing tasks with the earliest due date."

```bash
# Default view; supports filter, field show/hide, group, and sort; does not support time bars or card covers.
# The creation JSON supports objects/arrays, type defaults to grid; do not stuff in group_by/property, use Form commands for form.
lark-cli base +view-create --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --json '{"name":"任务明细","type":"grid"}' --as user
# visible_fields is a complete ordered list; omission means hidden, data is not deleted, and the primary field may be fixed in the first position.
lark-cli base +view-set-visible-fields --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "任务明细" --json '{"visible_fields":["任务名称","项目","状态","截止时间"]}' --as user
# group_config has at most 3 items, and the fields must be applicable to the target view; an empty array clears grouping.
lark-cli base +view-set-group --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "任务明细" --json '{"group_config":[{"field":"项目","desc":false}]}' --as user
# sort_config has at most 10 items; an empty array clears sorting. Wrap the configuration JSON in an object; do not pass a bare array.
lark-cli base +view-set-sort --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "任务明细" --json '{"sort_config":[{"field":"截止时间","desc":false}]}' --as user
```

<a id="按状态处理任务kanban"></a>
### Process tasks by status: kanban

Requirement: "One column each for To Do, In Progress, and Completed, with each column sorted by due date." Prerequisite: the status field is a single-select field containing the corresponding options.

```bash
# Supports filter, field show/hide, group, sort, and card cover; does not support time bars.
# Prefer grouping into columns by one single-select/multi-select field; group's desc arranges the groups, and sort arranges the records within a group.
lark-cli base +view-create --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --json '{"name":"任务看板","type":"kanban"}' --as user
lark-cli base +view-set-group --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "任务看板" --json '{"group_config":[{"field":"状态","desc":false}]}' --as user
lark-cli base +view-set-visible-fields --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "任务看板" --json '{"visible_fields":["任务名称","负责人","截止时间"]}' --as user
lark-cli base +view-set-sort --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "任务看板" --json '{"sort_config":[{"field":"截止时间","desc":false}]}' --as user
```

<a id="比较任务排期gantt"></a>
### Compare task schedules: gantt

Requirement: "View the schedule from task start to end, keeping only the task and assignee on the left."

```bash
# Supports filter, field show/hide, group, sort, and time bars; does not support card covers.
# timebar requires start, end, and title; the start and end fields must be date/time and the records must have values, chosen according to the business schedule.
lark-cli base +view-create --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --json '{"name":"任务排期","type":"gantt"}' --as user
lark-cli base +view-set-timebar --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "任务排期" --json '{"start_time":"开始时间","end_time":"结束时间","title":"任务名称"}' --as user
# Usually keep 1–3 key fields on the left to leave space for the timeline.
lark-cli base +view-set-visible-fields --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "任务排期" --json '{"visible_fields":["任务名称","负责人"]}' --as user
```

<a id="按日期浏览活动calendar"></a>
### Browse activities by date: calendar

Requirement: "View the arrangement of each activity on the calendar."

```bash
# Supports filter, field show/hide, and time bars; does not support generic grouping, sort, or card covers.
# timebar requires start, end, and title; the start and end fields must be date/time and the records must have values.
lark-cli base +view-create --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --json '{"name":"活动日历","type":"calendar"}' --as user
lark-cli base +view-set-timebar --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "活动日历" --json '{"start_time":"活动开始","end_time":"活动结束","title":"活动名称"}' --as user
```

<a id="浏览产品卡片gallery"></a>
### Browse product cards: gallery

Requirement: "Browse products as image cards, showing name, category, and price." Prerequisite: the product image is an attachment field.

```bash
# Supports filter, field show/hide, sort, and card cover; does not support grouping or time bars.
# cover_field uses an attachment field; pass null to clear the cover.
lark-cli base +view-create --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --json '{"name":"产品画册","type":"gallery"}' --as user
lark-cli base +view-set-card --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "产品画册" --json '{"cover_field":"产品图片"}' --as user
lark-cli base +view-set-visible-fields --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "产品画册" --json '{"visible_fields":["产品名称","分类","价格"]}' --as user
```

<a id="通用生命周期发现筛选改名清理"></a>
### Generic lifecycle: discover, filter, rename, clean up

```bash
# All five view types support query, rename, and delete; when a target view already exists, configure it directly.
# To modify existing configuration, first read the corresponding get (such as +view-get-group); read it back again when acceptance is needed.
# Batch creation is executed item by item and may partially succeed; after an exception or same-name conflict, first run list to confirm, to avoid blind retries.
lark-cli base +view-list --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --as user
lark-cli base +view-get --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "$VIEW_ID" --as user

# Only show records that are in progress; for complex conditions see the filter reference below
lark-cli base +view-set-filter --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "$VIEW_ID" --json '{"logic":"and","conditions":[["状态","intersects",["进行中"]]]}' --as user

# Use --name to rename; use name in --json to create
lark-cli base +view-rename --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "$VIEW_ID" --name "进行中任务" --as user

# Delete the view when the user explicitly requests it and the target is confirmed; do not delete the underlying records.
lark-cli base +view-delete --base-token "$BASE_TOKEN" --table-id "$TABLE_ID" --view-id "$VIEW_ID" --as user --yes
```

For detailed filter syntax, see [View filter](lark-base-view-set-filter.md); that document continues to route the common condition protocol.
