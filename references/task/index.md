# Tasks

Use for ordinary tasks, lists, subtasks, assignees, followers, and reminders. Approval todos belong to [Approvals](../approval/index.md). Todos inside a Minutes recording belong to [Meetings](../meeting/index.md) `minutes +todo`, not Task lists.

## Discovery and selection

Use a documented shortcut below; if no exact match exists, inspect `lark-cli task --help`, then exact command help. For native APIs discover the resource/method and inspect `lark-cli schema task.<resource>.<method>`. On `unknown_subcommand`, rediscover instead of guessing variants.

- Actual keywords/task names: `+search`; task-list names: `+tasklist-search`.
- Assigned to me, without keywords: `+get-my-tasks`.
- Created/followed/otherwise related to me, without keywords: `+get-related-tasks`.
- Lists filtered by creator/date without a name keyword: native `tasklists list`, with pagination and local filtering.
- Time phrases are filters, not search keywords. Search does not automatically restrict results to the caller: resolve the current `open_id` and set `--assignee`, `--creator`, or `--follower` when required.
- Incomplete-only summaries must pass `--complete=false`; an unfiltered list can contain completed tasks.

## Identity and identifiers

Use explicit user identity for the user's tasks. A task GUID is not the client display number such as `t104121`/`suite_entity_num`. Extract `guid` from Task applink query parameters. Likewise a task-list applink's `guid` is its `tasklist_guid`.

For a known list, inspect `task.tasklists.tasks` and list its tasks; take each returned task's real `guid` into `+update`/`+complete`. Do not first search for an already-known list. These two shortcuts also accept task applinks containing `guid=`.

## Writes and output

- Recurrence/reminders require a due time. When both start and due are present, start must not be later than due.
- Bot identity cannot add cross-tenant task members.
- `+update` returns `updated_fields` and per-task `confirmed`; `+complete` returns status, completion time, and `already_completed`. Do not routinely refetch when those fields already answer the task.
- Show returned task/list URLs. Resolve human names when displaying otherwise opaque people IDs and access permits; do not fabricate names. Render timestamps in the user's timezone.
- Native resources include tasks, tasklists, subtasks, members, sections, custom_fields, custom_field_options, agent, and agent_task_step_info. Read/write scopes follow the relevant resource contract; do not request every scope preemptively.

## Operation references

- [task create](references/lark-task-create.md)
- [task update](references/lark-task-update.md)
- [task set ancestor](references/lark-task-set-ancestor.md)
- [task comment](references/lark-task-comment.md)
- [task complete](references/lark-task-complete.md)
- [task reopen](references/lark-task-reopen.md)
- [task assign](references/lark-task-assign.md)
- [task followers](references/lark-task-followers.md)
- [task reminder](references/lark-task-reminder.md)
- [task get my tasks](references/lark-task-get-my-tasks.md)
- [task get related tasks](references/lark-task-get-related-tasks.md)
- [task search](references/lark-task-search.md)
- [task upload attachment](references/lark-task-upload-attachment.md)
- [task tasklist create](references/lark-task-tasklist-create.md)
- [task tasklist search](references/lark-task-tasklist-search.md)
- [task tasklist task add](references/lark-task-tasklist-task-add.md)
- [task tasklist members](references/lark-task-tasklist-members.md)
