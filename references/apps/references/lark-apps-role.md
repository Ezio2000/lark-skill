<a id="apps-role-域命令应用角色"></a>
# apps role domain commands (app roles)

Manage platform roles and role members within a Miaoda app, and query the roles a user matches. Runtime command facts are governed by `lark-cli apps +<cmd> --help`; identity, authorization, and high-risk confirmation follow this domain's [`index.md`](../index.md).

<a id="何时用"></a>
## When to use

Use when the user wants to list, view, create, update, or delete a platform role within a Miaoda app, manage a role's user, department, or group members, or query the roles a user matches in an app. Roles and permissions for Bitable / Base go through `lark-base`; setting who can access an app goes through `+access-scope-*`, and should not be routed to this command domain.

<a id="命令一览"></a>
## Command overview

| Command | What it does | Key parameters |
|---|---|---|
| `+role-list` | Paginate through roles, or filter roles by name | `--app-id`, `--name`, `--page-size`/`--page-token` |
| `+role-get` | Read role details based on the real `role_id` | `--app-id`, `--role-id` |
| `+role-match-list` | Query the roles a specified user matches | `--app-id`, `--user-id` |
| `+role-create` | Create a role | `--app-id`, `--name`, `--description`, `--role-id` |
| `+role-update` | Update a role's name or description | `--app-id`, `--role-id`, `--name`/`--description` |
| `+role-delete` | Permanently delete a role | `--app-id`, `--role-id`, `--yes` |
| `+role-member-list` | Query a role's user, department, and group members | `--app-id`, `--role-id`, `--member-type` |
| `+role-member-add` | Add user, department, or group members to a role | `--app-id`, `--role-id`, `--users`/`--departments`/`--chats` |
| `+role-member-remove` | Remove specific members or clear all role members | `--app-id`, `--role-id`, member parameters or `--all`, `--yes` |

<a id="约定先读"></a>
## Conventions (read first)

- `app_...` identifies a Miaoda app; its roles and members only use `apps +role-*` / `apps +role-member-*`; do not switch to Base role commands or raw bitable APIs.
- A role name is not a `role_id`. When only a name is available, prefer `+role-list --name` for exact resolution; if the full paginated list has already been obtained, you may also prove from it that the exact name has a unique match. Report 0 results truthfully; for multiple results, have the user disambiguate; only after a unique match may you use the returned real ID.
- When `+role-list` returns `has_more=true`, use this page's `page_token` to continue querying until `has_more=false`; do not fabricate entries based on `total`.
- The role data for `+role-list`, `+role-get`, and `+role-match-list` is located in `data.items`, `data.role`, and `data.roles` respectively; do not mix them up.
- Writes to the same role and operations that depend on the result of that write must be serialized. Independent operations on different roles may be parallelized only when each write can be traced individually, a failure does not affect other targets, and each is verified separately; otherwise keep them serial. Name resolutions or read-only queries that do not depend on each other may be parallelized.

<a id="各命令"></a>
## Individual commands

<a id="查询角色"></a>
### Query roles

```bash
lark-cli apps +role-list --app-id <app_id> --page-size 100
lark-cli apps +role-list --app-id <app_id> --name '<exact_name>'
lark-cli apps +role-get --app-id <app_id> --role-id <role_id>
lark-cli apps +role-match-list --app-id <app_id> --user-id <ou_x>
```

When organizing the role list, preserve `role_id`, `name`, and `description`. Do not guess an unknown `role_id`, and do not silently choose among candidates with the same name.
When `items=[]`, directly report that there are currently no roles; do not fabricate a "none" or `N/A` placeholder row for the table.
`+role-match-list --user-id` only accepts `ou_...`; when the user provides a name, email, or phone number, first resolve the unique open ID, then query the matched roles.

<a id="创建与更新"></a>
### Create and update

```bash
lark-cli apps +role-create --app-id <app_id> --name '<name>' \
  --description '<description>'

# Only modify the name
lark-cli apps +role-update --app-id <app_id> --role-id <role_id> \
  --name '<new_name>' --as user --format json

# Only modify the description
lark-cli apps +role-update --app-id <app_id> --role-id <role_id> \
  --description '<new_description>' --as user --format json
```

- `--description` and the `--role-id` at creation time are optional; pass `--role-id` only when a stable ID is genuinely needed, and it cannot be modified after creation.
- When updating, pass only the fields the user explicitly requested to change.
- The role in a successful response is located in `data.role`. Only when the user requests independent verification, or the result will be used for a subsequent high-risk operation, additionally execute `+role-get`.

<a id="删除角色"></a>
### Delete a role

Before deletion, resolve the unique app, role, and affected members. If the user has explicitly requested deletion of that role and the impact matches the request, proceed with the existing authorization; if the candidate is not unique or the scope would be expanded, explain first and ask. There is no need to repeatedly request the same authorization in subsequent turns.

When only a name is available, still resolve uniquely per the above rules, preferring `+role-list --name`. If the target no longer exists before the write, stop immediately and truthfully state that this was a no-op and no deletion was performed; do not describe "currently does not exist" as "deleted successfully".

Before deletion, read the exact role and the complete member scope, and explain to the user the app, role, `users` / `departments` / `chats` impact; when the authorization covers that target and impact, use `--yes`:

```bash
lark-cli apps +role-get --app-id <app_id> --role-id <role_id>
lark-cli apps +role-member-list --app-id <app_id> --role-id <role_id>
lark-cli apps +role-delete --app-id <app_id> --role-id <role_id> --yes
```

A successful response contains the matching `data.role_id` and `data.deleted=true`. Only when the user explicitly requests independent verification of the deletion result, use `+role-list --name` again to check that the target ID no longer exists.

<a id="成员-id-解析"></a>
### Member ID resolution

Member flags only accept open IDs: user `ou_...`, department `od-...`, group `oc_...`. When the user has already provided a valid open ID of the corresponding type, use it directly; only resolve when only a name or email is available.
The object type is determined by the user's semantics, and resolvers must not be interchanged: users go through contacts user search, departments through department search, groups through group search.

```bash
# User: query each name or email separately.
lark-cli contact +search-user --query '<姓名或邮箱>' \
  --exclude-external-users --page-size 30

# Department: paginate fully, and only accept a unique open_department_id.
lark-cli api POST /open-apis/contact/v3/departments/search \
  --params '{"user_id_type":"open_id","department_id_type":"open_department_id","page_size":50}' \
  --data '{"query":"<部门名称>"}'

# Group: paginate fully, and only accept a unique chat_id whose name matches exactly.
lark-cli im +chat-search --query '<群名称>' --page-size 50
```

- Only accept a unique result that exactly matches the input name, email, or group name; department search only accepts a unique `od-...` for the complete query. If there are 0 results, multiple results, or pagination is incomplete, stop writing and have the user supplement or disambiguate.
- Resolve multiple objects one by one. After all are resolved successfully and the total does not exceed 100, place them into a single member write by type; if any object fails, do not partially write, and do not automatically split into batches.

<a id="成员操作"></a>
### Member operations

```bash
# Omit --member-type to return the complete users / departments / chats.
lark-cli apps +role-member-list --app-id <app_id> --role-id <role_id>

lark-cli apps +role-member-add --app-id <app_id> --role-id <role_id> \
  --users ou_x,ou_y --departments od-x --chats oc_x

lark-cli apps +role-member-remove --app-id <app_id> --role-id <role_id> \
  --users ou_x --yes

# Clear members without deleting the role.
lark-cli apps +role-member-remove --app-id <app_id> --role-id <role_id> \
  --all --yes
```

- `+role-member-list` is not paginated; `--member-type` returns only the fields of the selected type, and member fields not returned mean "not queried" rather than empty. It must be omitted when confirming impact or performing a complete comparison.
- When summarizing `--member-type` results, make clear that this is a filtered projection, and do not assert based on it that the role has no members of other types.
- When the user requests the CLI's native table, directly execute `+role-member-list --format table`; you may forward it as-is or provide a factual summary, but do not first fetch JSON and then manually rebuild a substitute table.
- Writes and the read-back that depends on their results must not be placed in the same concurrent batch; you must wait for the write to return successfully in full, then separately initiate the read-back. If they are mistakenly run concurrently, only a new read-back after the write completes may serve as evidence of the result.
- Before adding, read the complete baseline only when the user requests independent proof or confirmation that other member types are unchanged, and perform a complete read-back after the write; otherwise the successful response suffices as the result.
- Before a targeted removal, confirm the exact members and impact. If the result needs to be proven, perform a complete read-back after the write; do not treat the filtered result as the complete member set.
- Before `--all`, read the complete member scope and confirm; after success, execute one unfiltered `+role-member-list` to confirm that all three member arrays are empty.

<a id="权限"></a>
## Permissions

| Operation | Required scope |
|---|---|
| list / get / member-list / match-list | `spark:app:read` |
| create / update / delete / member-add / member-remove | `spark:app:write` |
