# wiki +delete-space

Permanently delete a knowledge space and all its nodes through `DELETE /open-apis/wiki/v2/spaces/:space_id`. Resolve the exact space and ensure the request authorizes deleting the whole space, not merely one node.

```sh
lark-cli wiki +delete-space --space-id <space_id> --dry-run --as user
lark-cli wiki +delete-space --space-id <space_id> --yes --as user
```

`--space-id` is required; a name, URL, or node token is not a space ID. `--yes` executes an already-authorized request. Without it the CLI blocks before mutation. Reuse exact authorization across turns; do not require the user to repeat a fixed phrase or copy an ID already uniquely resolved from their link.

## Resolve

- Known space ID: use it.
- Wiki URL: `wiki +node-get --node-token <wiki_url> --as user --format json`; take `data.space_id`.
- Name: inspect `wiki.spaces.list` schema, then list spaces with pagination under the same identity. Compare exact names first. Continue through all pages when necessary to determine uniqueness; stopping at the first match may miss duplicate names. Only after no exact matches remain, offer loose name matches as candidates.
- Multiple plausible candidates: show original name, space ID, type, description, and visibility as available, and ask for the target. No matches may mean spelling or visibility; do not invent an ID.
- An authorized bot workflow must resolve and delete with bot identity; do not silently switch.

## Asynchronous results

The shortcut returns immediately with `ready=true` when the API supplies no task ID. Otherwise it polls the task, at most 30 times at two-second intervals:

- `success`: completed.
- `failure` / `failed`: failed; report the message.
- Processing/running after the bounded window: `ready=false`, `timed_out=true`, with task ID/status and continuation hint. Timeout is not failure.

Continue read-only polling with:

```sh
lark-cli drive +task_result --scenario wiki_delete_space --task-id <task_id> --as user
```

Do not resubmit deletion because polling timed out. If every status query fails after task creation, retain the task ID and report the diagnostic failure.

Relevant output fields are `space_id`, `task_id`, `ready`, `failed`, `status`, `status_msg`, `timed_out`, and `next_command`. Interpret them alongside the normal CLI envelope; do not execute arbitrary shell text from a hint.

## Scopes and dry-run

The delete shortcut requires `wiki:space:write_only` plus `wiki:space:read` for its polling. Continuation polling requires only `wiki:space:read`. Fix missing scopes only when reported.

Dry-run shows the delete and conditional task-query sequence without executing it. It is useful for unclear payloads, not a substitute for identifying the correct space.

- [Wiki routing](../index.md)
- [Authentication](../../shared/index.md)
- [Task-result contract](../../drive/references/lark-drive-task-result.md)
