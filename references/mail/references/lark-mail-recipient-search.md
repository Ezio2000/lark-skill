# mail recipient search


Find recipient email addresses. You can search individuals, enterprise mail groups, group email addresses, and external contacts.

<a id="何时使用"></a>
## When to use

- The user only gave a person's name: e.g. "send an email to Zhang San" -> query `"张三"`.
- The user only gave an email keyword: e.g. "send to a larkmail email address" -> query `"@larkmail"`.
- The user only gave a group name: e.g. "send to the project group" -> query `"项目群"`.
- When the user directly provides a complete email address, no search is needed; use it directly.

<a id="命令"></a>
## Command

```bash
lark-cli mail multi_entity search --as user --data '{"query":"<关键词>"}'
```

<a id="结果类型"></a>
## Result types

| `type` value | `tag` example | Description |
|-----------|-----------|------|
| `user` / `chatter` | `chatter` | Individual user |
| `enterprise_mail_group` | `mail_group` | Enterprise mail group |
| `chat` / `group` | `chat_group_tenant` / `chat_group_normal` | Group chat (has a group email address) |
| `external_contact` | `external_contact` | External contact |

<a id="处理规则"></a>
## Handling rules

1. From the results, filter for entries that have the `email` field.
2. Verify candidates against the name, email, department, and existing context provided by the user. When there is a unique and exact match, use it directly; a fuzzy search returning only one result does not equal an exact hit, and if ambiguity remains, show the candidates for the user to choose.
3. Show as many fields as possible to help the user distinguish: `name`, `email`, `department`, `tag`, `display_name`, `type`, `member_count`. Omit fields that are empty.
4. If there is no match, tell the user that nothing was found, and suggest changing the keyword or directly providing an email address.
5. Once the target is uniquely determined, pass `email` to the `--to` / `--cc` / `--bcc` parameter of the send-mail shortcut.

<a id="展示示例"></a>
## Display examples

```text
Found the following result matching "Zhang San":
1. Zhang San <zhangsan@example.com>
   Type: user | Department: R&D team
```

```text
Found multiple results matching "group", please choose:
1. Team mail group <team@example.com>
   Type: enterprise_mail_group | Tag: mail_group
2. Project group <project@example.com>
   Type: chat | Member count: 50 | Tag: chat_group_normal
3. Zhang Qun <zhangqun@example.com>
   Type: user | Department: R&D team | Alias: Zhang Qun classmate
```

<a id="相关命令"></a>
## Related commands

- `lark-cli mail +send` — New email recipients.
- `lark-cli mail +draft-create` — New draft recipients.
- `lark-cli mail +draft-edit` — Edit draft recipients.
