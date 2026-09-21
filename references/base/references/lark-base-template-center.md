<a id="base-模板中心"></a>
# Base Template Center

The Template Center is a **public Base template library**. When a user wants to "quickly build a Base using a ready-made template," this set of commands helps the AI find the most suitable template, and ultimately copy it into the user's own new Base via `+base-copy`.

The Template Center may also return BaseApp / app templates. If the template preview link `templates[].link` contains `/app/`, it is merely a displayable app template preview and does not support copy creation via `+base-copy`. When a user requests "create based on this app template / copy the app template," you should explicitly refuse and explain that the current CLI only supports copying Base templates, not app templates.

Three commands:

- `+template-categories`: List all template categories, used to align user intent to a category.
- `+template-list`: List templates under a category (if no category is passed, returns the "Recommended" category).
- `+template-search`: Search templates by keyword.

<a id="何时使用模板中心"></a>
## When to Use the Template Center

Use the Template Center when the following characteristics are met: the user has the **intent to create a new Base**, but **has no anchor pointing to an existing object** (no Base URL, no "my/recently visited tables," no specific existing Base name).

Typical triggers:

- "Help me build a CRM Base"
- "Are there any templates suitable for project management?"
- "Find a Base template for OKR tracking to follow"

Cases where you should **not** use the Template Center (even if the user says "template"):

- The user provides a Base/Wiki link or token → use `+url-resolve`.
- The user says "that table I had before / my template / recently visited" → use `+title-resolve` or switch to `lark-drive` search.
- The user wants to define the field schema from scratch rather than apply a ready-made template → use `+base-create --table-name --fields`.

The Template Center is an independent public dataset and **cannot** be found with `drive +search`; `drive +search` only searches cloud space objects accessible to the user themselves.

<a id="推荐命令"></a>
## Recommended Commands

```bash
# List all template categories
lark-cli base +template-categories --as user

# List templates under a category (if --category-key is not passed, returns the "Recommended" category)
lark-cli base +template-list --category-key template_center_tab_ai --limit 10 --as user

# Search templates by keyword
lark-cli base +template-search --keyword "项目管理" --limit 10 --as user

# Pagination: pass the offset returned by the previous page as-is to --offset
lark-cli base +template-search --keyword "AI" --limit 10 --offset <上一页返回的 offset> --as user

# After selecting a template, use the template token to copy it into the user's own new Base
lark-cli base +base-copy --base-token <模板 token> --name "<新 Base 名>" --as user
```

<a id="工作流"></a>
## Workflow

The Template Center has two paths; choose one based on how specific the user's intent is, and do not blindly use both.

<a id="路径-a分类浏览意图偏宽泛时首选"></a>
### Path A: Category Browsing (preferred when intent is broad)

When the user only gives a general direction (such as "project management" or "marketing"), first narrow down by category, then pick a template within the category.

1. `+template-categories` lists all categories; obtain `categories[].key` and `name`.
2. The AI matches the user's intent to the closest category `name`, and takes its `key`.
3. `+template-list --category-key <key>` lists the templates under that category.
4. Read each template's `name` / `introduction` / `scenarios`, pick the one that best fits the user's scenario, and take its `token`.
5. Use `+base-copy --base-token <token>` to copy a new Base based on the template (see "Creating Based on a Template" below).

```bash
# 1. See what categories exist
lark-cli base +template-categories --as user

# 2~3. After matching to the "AI Applications" category, list the templates in that category
lark-cli base +template-list --category-key template_center_tab_ai --limit 10 --as user
```

If no close category can be matched, or the user's intent itself spans categories / is very specific, switch to Path B.

<a id="路径-b关键词搜索意图有具体词时首选"></a>
### Path B: Keyword Search (preferred when intent has specific words)

When the user gives clear, searchable words (such as "financial reimbursement," "livestream retrospective," "AI customer service"), search directly without first looking at categories.

1. `+template-search --keyword "<词>"` searches templates.
2. Likewise read `name` / `introduction` / `scenarios` to select a template, and take its `token`.
3. `+base-copy` to copy.

```bash
lark-cli base +template-search --keyword "项目管理" --limit 10 --as user
```

The keyword cannot be empty; an empty search will be rejected. When the user only has a "general direction" without specific search terms, Path A's category browsing is more reliable.

<a id="分类-vs-搜索怎么选"></a>
### How to Choose Between Category and Search

| User Intent | Which Path |
|---|---|
| Only a broad category direction ("marketing type," "for office use") | Path A, first narrow down with `+template-categories` |
| Specific, searchable business terms ("reimbursement," "OKR," "livestream") | Path B, directly `+template-search` |
| Nothing suitable found under the broad direction | After A, use B with different keywords to supplement the search |

<a id="翻页"></a>
## Pagination

`+template-list` and `+template-search` both use cursor pagination:

- `--limit`: number per page, default 10, range 1-100; `--page-size` is an equivalent alias.
- `--offset`: pagination cursor, from the `offset` field of the previous response. **Do not pass it on the first request**.
- In the response, `has_more=true` indicates there is a next page; pass the response's `offset` as-is to the next `--offset`. `has_more=false` or `offset` being an empty string means there is no more.

`--offset` is an opaque cursor returned by the server; do not parse it, and do not construct it yourself.

```bash
lark-cli base +template-search --keyword "AI" --limit 10 --offset <上一页返回的 offset> --as user
```

<a id="数据结构"></a>
## Data Structures

<a id="templatecategory分类对象"></a>
### TemplateCategory (Category Object)

`+template-categories` returns `categories[]`, each element:

| Field | Type | Meaning |
|---|---|---|
| `key` | string | Unique category identifier, in the form `template_center_tab_ai` (`template_center_tab_` prefix + category name). This is what is passed to `+template-list --category-key` |
| `name` | string | Category display name, such as `AI 应用` / `办公通用`. The AI looks at this when matching user intent |

<a id="template模板对象"></a>
### Template (Template Object)

`+template-list` / `+template-search` returns `templates[]`, each element:

| Field | Type | Meaning |
|---|---|---|
| `token` | string | The template's Base token, which is the template's unique identifier. Used as the input for `+base-copy --base-token` when creating based on the template |
| `name` | string | Template name, such as `工作汇报` |
| `introduction` | string | Template introduction, explaining the template's purpose, content structure, and applicable direction. The AI mainly looks at this to judge whether the template fits the user's needs |
| `scenarios` | string[] | List of applicable scenarios, such as `["工作汇报","月报","项目进展"]`, used to quickly judge scenario match |
| `developer` | string | Template developer, such as `飞书` |
| `link` | string | Template preview link, which can be shown to the user, but copying the template uses `token` rather than `link` |
| `created_at` / `updated_at` | string | Creation / update time |

List / search responses also carry pagination fields:

| Field | Type | Meaning |
|---|---|---|
| `has_more` | boolean | Whether there is a next page |
| `offset` | string | Next page cursor; empty string when there is no more |

**Convention**: The template's unique identifier is called `token` (template Base token); do not rename it to `id` or `key` in output or paraphrase; `key` is the category's identifier (`category_key`).

<a id="模板列表模版搜索-响应示例"></a>
### Template List/Template Search - Response Example

```json
{
  "code": 0,
  "data": {
    "has_more": true,
    "offset": "1",
    "templates": [
      {
        "created_at": "2025-12-03T02:53:34Z",
        "developer": "Base Team",
        "introduction": "📊 品牌调研问卷  \n高效收集用户反馈，助力品牌优化决策  \n\n核心功能点  \n1 预设多维度调研问题模板  \n2 支持自定义问题类型与逻辑跳转  \n3 实时数据统计与可视化分析  \n\n适合场景  \n1 新品上市前市场需求调研  \n2 品牌形象与用户满意度评估  \n3 竞品对比与消费者偏好分析",
        "link": "https://example.com/base/<template_token>",
        "name": "品牌调研问卷",
        "scenarios": ["运营管理", "市场营销"],
        "token": "<template_token>",
        "updated_at": "2026-06-22T08:18:58Z"
      }
    ]
  },
  "msg": ""
}
```

When reading the template list, focus on:

- `templates[].name`: template name; when creating a Base based on the template and the user has not specified a new name, use it directly as `+base-copy --name`.
- `templates[].token`: template Base token; pass it to `+base-copy --base-token` when copying.
- `templates[].link`: template preview link; it can be shown to the user to help confirm, but do not use the link instead of the token when copying. If the link contains `/app/`, this is an app template preview, which can only be displayed and cannot be copied/created.
- `templates[].introduction` / `templates[].scenarios`: used to judge whether the template matches the user's business scenario.
- `data.offset`: next page cursor; only when `has_more=true` should you continue passing it to `--offset`.

<a id="基于模板创建-base"></a>
## Creating a Base Based on a Template

The Template Center is only responsible for "finding templates"; it does not itself create Bases. After selecting a template, use the template's `token` to copy out the user's own new Base:

```bash
lark-cli base +base-copy --base-token <模板 token> --name "<新 Base 名>" --as user
```

- `--name` uses the new Base name the user wants; if not passed, the template name is used.
- Only when the user explicitly says "only the structure / no content" should you add `--without-content`.
- For the return and permission description of `+base-copy`, see the relevant rules for `+base-copy` in index.md.
- If the selected template's `link` contains `/app/`, do not call `+base-copy`. Such app templates currently only support being displayed to the user and do not support copy creation; when the user requests creation based on an app template, you should refuse and explain the capability boundary.

<a id="注意事项"></a>
## Notes

- All three commands are read-only, default to `--as user`, and require the permission `base:template:read`.
- The Template Center is a public dataset and cannot be found with `drive +search`; when the user wants "my/recently visited/existing Base," do not go here.
- Category comes before list: the `--category-key` of `+template-list` must come from the return of `+template-categories`; do not guess the category key out of thin air.
- `+template-search` does not support empty keywords and will be rejected; when the user only has a broad direction and no specific search terms, switch to category browsing.
- The template's unique identifier is `token` (template Base token); do not rename it to `id` or `key`.
- `--offset` is an opaque cursor returned by the server; pass it back as-is when paginating, and do not parse or construct it yourself.
- The Template Center only queries templates and does not create Bases; creation always goes through `+base-copy --base-token <token>`, and do not use a template token to call current-user Base commands such as `+base-get`.
- App template links contain `/app/` and are only for preview display; `+base-copy` is not supported; do not promise that creation based on an app template is possible.
