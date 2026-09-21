<a id="baseapp应用模式操作指引"></a>
# BaseApp (App Mode) Operations Guide

> Read [`../../shared/index.md`](../../shared/index.md) first. Interface and component fields are subject to the CLI's current version of API metadata, the [component configuration reference](lark-base-app-block-data-config.md), and server-side validation results; do not infer additional constraints from component names.

<a id="不支持能力先判断并停止"></a>
## Unsupported Capabilities: Determine First and Stop

<a id="复制-baseapp"></a>
### Copying a BaseApp

There is no BaseApp copy command in this release. When a user wants to copy or clone an existing BaseApp, directly state that the current CLI cannot do this and stop; do not continue exploring alternative channels such as the browser, OpenAPI, or creation-type commands, and do not initiate any write requests.

- `+base-copy` only supports Base, not BaseApp; do not pass `app_token` to it, and do not describe the copied Base as an app copy.
- `+app-create` only creates a brand-new empty BaseApp; it does not copy existing pages or components.
- Do not use Drive copy or other Base shortcuts to assemble, simulate, or impersonate a BaseApp copy.

<a id="创建或归属-pagegroup"></a>
### Creating or Assigning a PageGroup

The page hierarchy capability in the current first phase only supports top-level Page nodes. Creating PageGroups, setting their assignment, and moving existing Pages into page groups are all unsupported.

The final response must state both the positive support scope above and the negative limitations; it cannot only say that PageGroup is unsupported. When a user hits these requests, directly state that the current CLI cannot do this and stop; do not continue exploring alternative channels such as the browser, OpenAPI, or ordinary Page commands, and do not read pages and then claim grouping can be done or initiate any write requests.

<a id="从-workspace-移出或移除资源"></a>
### Moving Out or Removing Resources from a Workspace

The current CLI only supports using `+workspace-move-in` to move a Base or BaseApp into a Workspace; it does not support moving out or removing resources from a Workspace, and there are no `workspace move-out` / `workspace remove` commands. For such requests, you must first complete read-only locating, then state the limitation and stop; the order cannot be swapped:

1. When the Workspace URL contains `/base/workspace/<workspace_token>`, extract the real `workspace_token` from it; do not treat the full URL as a command parameter.
2. In the same turn, immediately execute `lark-cli base +workspace-entity-list --workspace-token <workspace_token> --page-size 30 --as user`; if `has_more=true`, continue paginating until complete. This query is a necessary read-only locating step; do not leave it as an optional item waiting for the user to choose again, and do not use `--help` instead of a real query.
3. Use the server-returned `entities[].name`, `entity_type`, `token`, and `url` to faithfully determine the target. When the name matches exactly, report the real object; when there is no exact match, clearly state that no entity with the exact same name exists, and list possibly related candidates as-is. Do not automatically strip or add prefixes/suffixes, and do not claim the target has been located merely because the name is similar. When the user directly provides a token, still faithfully report the actual name corresponding to that token.
4. After reporting the locating result, clearly state that the current CLI cannot perform Workspace move-out/removal, and stop; do not initiate any write requests. If the user cancels at any step, stop immediately; after cancellation, do not call tools again.

`lark-cli drive +move` only changes the directory location of a Base or BaseApp in Drive; it does not change its Workspace membership and cannot serve as a substitute for moving out of a Workspace. Do not continue exploring Drive move/delete, another Workspace's `+workspace-move-in`, the browser, OpenAPI, or source code to assemble or impersonate this operation; only when the user subsequently explicitly requests another supported operation should you perform a new write.

<a id="token-与命令"></a>
## Tokens and Commands

| Object | Identifier | Command |
|---|---|---|
| Workspace | `workspace_token` | `+workspace-create` / `+workspace-entity-list` / `+workspace-move-in` |
| BaseApp | `app_token` | `+app-create/get`; see below for rename and delete |
| Base | `base_token` | Returned by `+base-create`; table, field, and record commands use it |
| Page | `page_id` | `+app-page-list/get/create/update/delete` |
| Block | `block_id` | `+app-block-list/get/create/update` |

Page and component commands use `app_token`; Base data commands use `base_token`. `+app-block-get-data` uses `app_token + base_token + chart_token`: the CLI parameter name is still `--block-id`, but you must pass the `chart_token` returned by the component, not an ordinary `block_id`. The request path is the same as the dashboard chart data interface.

BaseApp / AppMode is a Base domain capability. When the user provides a `/app/` link, first use `+url-resolve`; it returns `app_token`, and faithfully extracts the `workspace_token` and `page_id` actually carried by the link. Directly use this guide and `lark-cli base +...`; do not first try `lark-cli apps`.

<a id="查询应用"></a>
## Querying Apps

```bash
lark-cli base +app-get --app-token <app_token>
```

- There is no `lark-cli base +app-list`. When you need to list BaseApps within a Workspace, the only list entry point is:

  ```bash
  lark-cli base +workspace-entity-list \
    --workspace-token <workspace_token> \
    --type baseapp \
    --page-size 30
  ```

- `pages` in the response is a page summary.
- The structure of `ref` is `Base token -> 当前组件引用的 Table 名称数组`. When you need to operate on a referenced Base, use the key of `ref` as `base_token`.
- `ref` only describes data sources already referenced by the current component; Bases not referenced by any component will not appear in it.

<a id="查询页面与组件"></a>
## Querying Pages and Components

```bash
lark-cli base +app-page-list --app-token <app_token> --page-size 100
lark-cli base +app-block-list \
  --app-token <app_token> \
  --page-id <page_id> \
  --page-size 100
```

- When `+app-get` has already returned sufficient page summaries, you can directly obtain the target `page_id`; use `+app-page-list` again only when you need the complete page directory or pagination confirmation.
- If a Page returned by `+app-page-list` has `name` as an empty string, it means the current user has no permission for that Page, not that the Page has no title. Report that permission status, and do not use its `page_id` for subsequent page or component reads/writes.
- When you only need list summaries, do not call `+app-block-get` one by one to double-check; use get only when the user needs details of a single component.
- When `+app-block-list` returns a component of `type=unsupported`, you can only identify its existence through the list summary. The current CLI does not support reading details, reading computed data, or modifying such components; do not call `+app-block-get`, `+app-block-get-data`, or `+app-block-update`, as these requests will error.

<a id="创建-workspace"></a>
## Creating a Workspace

```bash
lark-cli base +workspace-create \
  --name "AppMode-空白评测空间" \
  --as user
```

<a id="创建应用"></a>
## Creating an App

```bash
lark-cli base +app-create \
  --name "销售应用" \
  --workspace-token <workspace_token> \
  --as user
```

- `+app-create` has no `--base-token`.
- `--workspace-token` is required; `+app-create` only calls the App creation interface; it does not create a Workspace or Base, nor move resources.
- `--theme-style` is optional and supports `default|cloudBlue|fresh|softLight|future|technology`.
- Record the `app_token` and `workspace_token` in the output.

<a id="新建应用的默认-page-复用"></a>
### Default Page Reuse for Newly Created Apps

`+app-create` also generates a system default Page, but the creation response does not return its `page_id`. When the user has not explicitly requested another page structure, after creating the App first read the app to obtain that Page, rename it, and directly use it as the user's required first page; do not use `+app-page-create` to create another first page:

```bash
lark-cli base +app-get --app-token <app_token> --as user
lark-cli base +app-page-update \
  --app-token <app_token> \
  --page-id <default_page_id> \
  --name "<page_name>" \
  --as user
```

In the above default flow, then execute `+app-block-create` **serially, one by one** on this Page; multiple components on the same Page must not be created concurrently. Only when the user truly needs an additional page should you call `+app-page-create` after reusing the default Page. When the user explicitly requests keeping the default Page, creating a separate independent page, or adopting another page structure, handle it according to the user's request.

If `+app-get` temporarily does not return the default Page, re-execute `+app-get` or `+app-page-list` to obtain it; do not create a replacement Page. If creating a component returns a layout overlap, first stop other concurrent writes on the same page, use `+app-block-list` to confirm the components that already succeeded, then stay on the original Page and serially retry the failed step; do not work around the conflict by creating a new Page, deleting the default Page, or rebuilding the entire page.

<a id="创建应用的自然语言编排"></a>
### Natural Language Orchestration for Creating an App

First choose the flow based on whether the user specified a Workspace and an existing Base, then call the atomic shortcut:

| Information provided by the user | Execution flow |
|---|---|
| Workspace + existing Base | Confirm the Base is in that Workspace → `+app-create`; do not create a backup Base |
| Workspace, no Base specified | `+app-create` → `+base-create` create an empty Base → `+workspace-move-in` |
| No Workspace specified, existing Base specified | First confirm the Workspace to which the Base belongs; when it can be determined, execute `+app-create` in that Workspace; when it cannot be determined, ask the user to provide the Workspace; do not create a backup Base |
| Neither Workspace nor Base specified | `+workspace-create` → `+app-create` → `+base-create` create an empty Base → `+workspace-move-in` |

A list component in App Mode can only reference one Base within the same Workspace. When the user specifies an existing Base, do not additionally create a Base just because `+app-create` did not receive `base_token`; subsequently reference that Base in the component's `data_config.base_token`.

In multi-step orchestration, each successful shortcut immediately produces resources and does not automatically roll back. When a subsequent step fails, clearly report the Workspace, App, or Base that were already successfully created and their tokens; when the user asks to continue, retry only the failed step and do not recreate resources that already succeeded.

<a id="读取图表计算结果"></a>
## Reading Chart Computation Results

```bash
lark-cli base +app-block-get-data \
  --app-token <app_token> \
  --base-token <base_token> \
  --block-id <chart_token>
```

- The value of `--block-id` must be taken from the `chart_token` in the chart component summary; you cannot use the component's ordinary `block_id`.
- `base_token` uses the current chart component's `data_config.base_token`; when one App references multiple Bases, do not arbitrarily choose a key from `+app-get ref`.
- `page_id` does not participate in the request.
- The return protocol is exactly the same as `+dashboard-block-get-data`.

<a id="重命名应用"></a>
## Renaming an App

```bash
lark-cli drive files patch \
  --file-token <app_token> \
  --type bitable \
  --data '{"new_title":"新名称"}'
```

Both BaseApp and Base use `type=bitable` in the Drive file interface. `new_title` only updates the app title; it does not rename the Base it references, nor modify Pages or Blocks.

<a id="删除应用"></a>
## Deleting an App

```bash
lark-cli drive +delete --file-token <app_token> --type bitable --yes
```

- Deleting the BaseApp app itself requires switching to `lark-drive`.
- Both BaseApp and Base use `--type bitable` in the Drive delete interface; when deleting a BaseApp, pass `app_token` for `--file-token`.
- This is a high-risk write operation; before executing, first confirm that `app_token` comes from `+app-get` or `+workspace-entity-list`.

## Page

<a id="本期不支持的-page-能力"></a>
### Page Capabilities Not Supported in This Release

Page copying and page icons are both out of scope for this release. When a user raises needs such as copying a Page, duplicating a page, cloning a page, reusing a page icon, or setting or modifying a page icon:

1. Clearly state that the current CLI does not support this capability, and confirm that no writes were performed this time.
2. Do not call `+app-page-create` to impersonate a full copy; an empty Page does not contain the original Page's content, components, or icon.
3. Do not attempt to use other shortcuts to assemble, simulate, or claim completion of Page copying or icon setting.
4. In the final response, explain the following alternative capability in a separate paragraph, but do not execute it automatically:

   > Available alternative capability (not executed this time): the current CLI can create a new empty Page, but it will not copy the original Page's content, components, or icon. If you need to create an empty Page, please tell me explicitly.

Only when the user subsequently explicitly requests creating an empty Page may you call `+app-page-create`.

```bash
lark-cli base +app-page-list --app-token <app_token>
lark-cli base +app-page-create --app-token <app_token> --name "总览"
lark-cli base +app-page-update --app-token <app_token> --page-id <page_id> --name "经营总览"
lark-cli base +app-page-delete --app-token <app_token> --page-id <page_id> --yes
```

- For a newly created App, when the user has not explicitly requested another page structure, you must use the system default Page as the user's required first page according to [Default Page Reuse for Newly Created Apps](#新建应用的默认-page-复用); `+app-page-create` is only used for additional pages requested by the user.
- Page names must be unique within the same App. Before creating or updating a name, the CLI reads the page list; when updating, it excludes the current Page.
- Component names must be unique within the same Page. `+app-block-create` paginates through all components of that Page and checks for duplicate names before creation.
- There is no Page arrange in this release, and no Block delete; a Block's `type/sub_type` cannot be modified after creation. See [Capabilities Not Supported in This Release](#本期不支持的能力) for details.

<a id="本期不支持的能力"></a>
## Capabilities Not Supported in This Release

The following capabilities do not exist in this release. When a user raises them, directly state that they are unsupported and give optional alternative directions; do not substitute same-named capabilities from Dashboard or other domains.

| User request | Status in this release | Correct action |
|---|---|---|
| Auto-layout / re-layout / beautify page components | No App page arrange | Directly state it is unsupported; do not call `+dashboard-arrange` |
| Delete page components | No App block delete | Directly state it is unsupported; it can only be handled in the UI; do not call `+dashboard-block-delete` |
| Modify component position / size / pin to top | Layout, position, and size are not part of the public Create/Update protocol | Directly state it is unsupported; do not use `+app-block-update` to perform an empty update disguised as a move |
| Modify an existing component's `type/sub_type` | `type/sub_type` cannot be modified after creation | First read the current Block; regardless of whether it is already the target type, the final response must state this constraint. When it already matches, state that no write is needed; when it does not match, state that it can only be handled in the UI; do not call or promise to use `+app-block-update` to modify the type |
| Modify the theme of an existing App | `--theme-style` only takes effect during `+app-create` | Directly state it is unsupported; if truly necessary, explain that the theme can only be specified when creating a new App |
| Read or modify components of `type=unsupported` | The list is only used to identify that the component exists; detail reading, computed data reading, and modification are all unsupported | Directly state it is unsupported; do not call `+app-block-get`, `+app-block-get-data`, or `+app-block-update`, as these requests will error |

`+dashboard-*` commands only act on dashboards within a Base; `dashboard_id` starts with `blk`, and component IDs start with `cht`; AppMode's `pge` pages and `wgt` components are not within their scope. When a capability is missing, do not use these commands to probe, including `--help` and `--dry-run`: one call is one incorrect capability-attribution judgment.

<a id="列表组件"></a>
## List Component

When creating a list, use `--type list` and `--sub-type standard|grouped|collapsible|card|detail`. When `--sub-type` is omitted, it defaults to `standard`.

```bash
lark-cli base +app-block-create \
  --app-token <app_token> \
  --page-id <page_id> \
  --name "待处理订单" \
  --type list \
  --sub-type standard \
  --data-config '{"base_token":"<base_token>","table_name":"订单"}'
```

- `data_config.base_token` is single-valued: each list can select at most one Base.
- The Base must be in the same Workspace as the current App; the CLI validates before writing.
- For the complete field protocol, read [lark-base-app-block-data-config.md](lark-base-app-block-data-config.md).

<a id="更新组件"></a>
## Updating Components

`+app-block-update` only sends the explicitly passed `data_config` fields. Fields not passed remain unchanged; whether array or object fields are replaced as a whole is subject to the [component configuration reference](lark-base-app-block-data-config.md) and server-side validation results. Do not first read and submit the full configuration just to "complete" it.

<a id="常见恢复"></a>
## Common Recovery

| Symptom | Action |
|---|---|
| `status=partial` | Report the completed/failed steps; when the user asks to continue, execute `retry.command` |
| Duplicate Page name | First `+app-page-list`, choose a unique name, then retry |
| Duplicate component name | First `+app-block-list`, choose a unique name for the new component within that Page, then retry |
| List Base not in the same Workspace | Use `+workspace-entity-list` to verify; choose a Base in the same Workspace |
| List protocol validation failure | Read the component protocol documentation; do not infer title, group_by count, or field role |
| Wrong Block type selected | It cannot be deleted in this release and the type cannot be changed; it can only be handled in the UI and then recreated |
| User wants arrange / delete component / adjust position / change theme | Directly state it is unsupported according to [Capabilities Not Supported in This Release](#本期不支持的能力); do not switch to `+dashboard-*` commands |
