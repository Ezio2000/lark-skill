# Contacts

Choose the identity before choosing the command. User and bot lookup paths are different.

| Need | User identity | Bot identity |
|---|---|---|
| Find an employee by name/email | [+search-user](references/lark-contact-search-user.md) | Not supported |
| Find a visible bot/agent by keyword | [+search-bot](references/lark-contact-search-bot.md) | Not supported |
| Read another user's known open_id | `+search-user --user-ids <id>` | [+get-user --user-id](references/lark-contact-get-user.md) |
| Read the current user | `+get-user` or `+search-user --user-ids me` | Not supported |
| Personal status or profile description | `user_profiles batch_query` | Not supported |

If an open_id is already known and the user only wants to send a message or schedule an event, go directly to [Messaging](../im/index.md) or [Calendar](../calendar/index.md).

A name can identify either a person or a bot. If its wording suggests a bot/agent/assistant, search bots first; search both when the type is unclear. Before a downstream write, disambiguate multiple candidates rather than picking the first.

For batch personal-status lookup, inspect `lark-cli schema contact.user_profiles.batch_query`. Use `user_id_type: open_id` and request the relevant query options.

Error `41050` / permission denied may reflect the current identity's visibility. Cross-tenant users can have empty business fields; this is not necessarily a failed lookup. `+get-user` supports open_id, union_id, and user_id through `--user-id-type`; `+search-user` uses user open_ids, while `+search-bot` searches keywords and returns bot open_ids.

Department trees, department member enumeration, and organization structures use [OpenAPI discovery](../openapi-explorer/index.md). For actual identity/scope errors, use [diagnostics](../shared/index.md).
