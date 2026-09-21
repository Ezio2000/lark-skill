<a id="apps-cache-域命令应用运行时缓存调试"></a>
# apps cache domain commands (application runtime cache debugging)

Debug the runtime cache of a Miaoda application: view the content of a cache key, delete a single key, or clear all cache in an environment. Cache is data an application temporarily stores for speed; after deletion or clearing, the application automatically fetches the latest data the next time it is needed. Command facts are governed by `lark-cli apps +<cmd> --help`; for authentication, `--as user`, exit codes, `_notice`, and other general handling, see [`../../shared/index.md`](../../shared/index.md) and this domain's [`index.md`](../index.md).

<a id="何时用"></a>
## When to use

When the user wants to troubleshoot "what is stored in a cache key / whether it was hit", wants to delete a key so the application fetches the latest data next time, or wants to clear the cache of an environment for a quick recovery.

<a id="命令一览"></a>
## Command list

| Command | What it does | Key parameters |
|---|---|---|
| `+cache-get` | View the content and information of a cache key | `--key`, `--environment`, `--format` |
| `+cache-delete` | Delete a cache key (repeated deletion does not error; no `--yes` needed) | `--key`, `--environment` |
| `+cache-clear` | Clear all cache in the specified environment (the CLI requires `--yes`; authorization follows the session) | `--environment`, `--yes` |

> All commands require `--app-id`.

<a id="约定先读"></a>
## Conventions (read first)

- **Environment `--environment dev|online` (optional)**: Cache is isolated by runtime environment. When not specified, it is selected automatically based on the application's current environment configuration—applications with multiple environments default to the development environment `dev`, while those without multiple environments use online `online`; the `environment` in the returned result tells you which environment was actually operated on this time. Pass it explicitly if you want to fix it.
- **Pass the cache key with `--key`**: Pass the key used in the business; whether it is valid (non-empty, length, etc.) is validated by the server, and an invalid one returns an error.
- **Risk levels**: `+cache-clear` clears the entire environment's cache and is a high-risk operation; without `--yes` it will be stopped by the confirmation gate, so before executing, verify whether the existing authorization covers that application and environment (criteria in [+cache-clear](#cache-clear高危)); `+cache-delete` deletes only a single key with limited impact and does not need `--yes`.
- **The content of `+cache-get` has two display modes**: `--format json` (default) returns the cache content as-is, suitable for precise comparison; `--format pretty` formats and expands the content, making it easier to read.

<a id="各命令"></a>
## Commands

### +cache-get
Query a single cache by `--key`. On a hit, it returns: whether it exists, remaining time to live (TTL), content and its size; on a miss (or if expired), it returns only `exists=false` without content.

> Every query returns the content along with it (there is no "view info only, without fetching content" mode), and the content may be large—when you only want to confirm "is it there / how long until it expires", be careful not to consume too much context.

```bash
lark-cli apps +cache-get --app-id app_xxx --key spotbonus:2026:winners:list:v1
lark-cli apps +cache-get --app-id app_xxx --environment online --key <key> --format pretty
```

### +cache-delete
Delete a cache key. **Repeated deletion, or deleting a key that never existed, both count as success** (returns `deleted_key_count=0`) and do not error; a hit returns `deleted_key_count=1`. After deletion, the application automatically fetches the latest data next time, with limited impact, so `--yes` is not needed.

**Do not misread `deleted_key_count` in the response**—it is the sole criterion for "whether something was actually deleted this time":

| `deleted_key_count` | Meaning | How to phrase it to the user |
|---|---|---|
| `1` | Hit and deleted | "The key has been deleted" |
| `0` | The request succeeded, but no key was deleted—this key **never existed or has expired** | "This key never existed / has expired, no deletion needed"—**do not say "successfully deleted"** |

To prove "the deletion took effect", use the chain "`+cache-get` before deletion confirms existence → `+cache-delete` gets `deleted_key_count=1` → after deletion `+cache-get` gets `exists=false`"; a single miss after deletion is not enough, because when the key never existed from the start (`deleted_key_count=0`) the result is exactly the same.

```bash
lark-cli apps +cache-delete --app-id app_xxx --environment dev --key <key>
```

<a id="cache-clear高危"></a>
### +cache-clear (high risk)
Clear all cache of the current application in the **specified environment**, used for quick recovery when the specific key cannot be located. The impact covers the entire environment, so `--yes` is required; it returns the number of keys cleared this time.

Before clearing, determine the application, environment, and the scope of "all cache". When the user has explicitly requested clearing a specified environment of a specified application, you may include `--yes` on the first call; there is no need to say the word "confirm" again. If they only say "clear the cache" and the environment cannot be determined from context, ask about the environment first. Existing authorization remains valid in subsequent turns and after authentication recovery, unless the target or impact changes.

You can use `--dry-run` to verify the request; handle exit 10 according to [confirmation parameter handling](../../shared/references/lark-shared-high-risk-approval.md). Do not rely on the server to automatically select the write environment.

```bash
# 1) Not confirmed: preview only, do not clear (--dry-run does not trigger the gate and produces no real action)
lark-cli apps +cache-clear --app-id app_xxx --environment online --dry-run

# 2) After user confirmation: add --yes to execute
lark-cli apps +cache-clear --app-id app_xxx --environment dev --yes
```

<a id="错误与边界"></a>
## Errors and boundaries

- **Invalid key / cache service temporarily unavailable**: The command returns an error with an explanation; relay it to the user according to `error.hint`; cases like "service temporarily unavailable" can be retried later.

<a id="agent-规则"></a>
## Agent rules

- **Determine the environment before write operations**: When `+cache-clear` / `+cache-delete` do not specify `--environment`, they fall to the automatically selected environment—**applications without multiple environments are directly affected on online `online` (production)**. When unsure whether the application has multiple environments, pass `--environment` explicitly for write operations; pure viewing (`+cache-get`) has limited impact and may omit it.
- **Clearing must explicitly include the environment**: When the specific application, environment, and clearing scope are already authorized, execute directly; when the scope is missing, only preview or ask.
- **Prefer `+cache-get` for troubleshooting cache content**: Use `--format pretty` to view structured, readable content; use the default JSON to get raw content for precise comparison.
- **Align on the key before deleting it**: When the user only describes the business meaning and does not give the exact key, confirm before deleting—deleting the wrong one has limited impact (the application rebuilds automatically), but accidental deletion should still be avoided.
