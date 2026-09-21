<a id="图标枚举"></a>
# Icon Enumeration

Used for `header.icon`, `div.icon`, `markdown`'s `<link icon=...>`, etc.

<a id="结构"></a>
## Structure

```json
// System icons (recommended): use token
{ "tag": "standard_icon", "token": "info_outlined", "color": "blue" }
// Custom icons: use the uploaded img_key
{ "tag": "custom_icon", "img_key": "img_v3_xxx" }
```

`color` takes a color enumeration (see `colors.md`), and only takes effect for `standard_icon`.

<a id="token-命名"></a>
## token Naming

- Linear: suffix `_outlined`; filled (solid): suffix `_filled`.
- The main body is kebab-case, such as `calendar-add_outlined`, `delete-trash_outlined`.

<a id="常用-token业务卡片"></a>
## Common tokens (business cards)

| Meaning | token | Meaning | token |
|---|---|---|---|
| Complete/checkmark | `done_outlined` | Close/cross | `close_outlined` |
| Add | `add_outlined` | Edit | `edit_outlined` |
| Delete | `delete-trash_outlined` | Search | `search_outlined` |
| Settings | `setting_outlined` | Info | `info_outlined` |
| Warning | `warning_outlined` | Time | `time_outlined` |
| Calendar | `calendar_outlined` | Member | `member_outlined` |
| Group | `group_outlined` | Chat | `chat_outlined` |
| Mail | `mail_outlined` | Link | `link-copy_outlined` |
| Share | `share_outlined` | Download | `download_outlined` |
| Notification/bell | `bell_outlined` | Location | `pin_outlined` |
| Attachment | `attachment_outlined` | Approval | `approval_outlined` |

<a id="彩色图标精确-token"></a>
## Colored icons (exact tokens)

Colored icons must be selected from the table below by **complete string**; it is forbidden to assemble them yourself based on naming patterns. Colored tokens carry their own color; do not derive other suffixes or variants.

| Meaning | token | Meaning | token |
|---|---|---|---|
| Calendar | `calendar_colorful` | To-do | `todo_colorful` |
| Poll | `vote_colorful` | Feishu Minutes | `file-lark-minutes_colorful` |
| Base | `wiki-bitable_colorful` | Form | `file-form_colorful` |
| Feishu Community | `larkcommunity_colorful` | Recruitment | `hirelogo_colorful` |
| Feishu Brand | `lark-logo_colorful` | Meego | `meego_colorful` |
| AI | `myai_colorful` | aPaaS | `apaas_colorful` |
| Approval | `approval_colorful` | General AI | `ai-common_colorful` |

> The token must match the official one exactly, otherwise the icon will not render. The table above lists common items; for the full set (hundreds, categorized into system/business/communication/user/media/document, etc.), refer to the official icon library:
> https://open.larkoffice.com/document/feishu-cards/enumerations-for-icons
