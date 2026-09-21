# apps +env-pull


Pull Miaoda app dev startup environment variables to the `.env.local` at the local project root. Identity is fixed to `--as user`; scope is `spark:app:read`. `--app-id` is required; the target project root defaults to the current working directory (`--project-path` can specify it).

This command is a dev-only local recovery tool: internally it fixes `POST env_vars`, and the body is `env=dev`. It has no `--env` flag, and it does not manage online environment variables.

<a id="何时别用核心反模式"></a>
## When not to use it (core anti-pattern)

**Usually you do not need to run it manually**—the scaffold's `npm run dev` automatically pulls in the background when starting local development (non-blocking). Running it manually again does the same thing again, and overwrites keys with the same name in `.env.local` with the server-returned values; unrelated local lines and comments are preserved.

Use it only in these fallback scenarios:

- Not starting via `npm run dev` (running `node` / IDE debug directly).
- `.env.local` was broken / deleted, and you want to resync.

<a id="行为"></a>
## Behavior

- **Merge, do not clear**: when writing to `.env.local`, your handwritten content and comments are preserved—matched keys have their values replaced, new keys are appended, and there is no full overwrite.
- **Safety guardrail**: the returned envelope **does not echo any env key / value** (to prevent tokens / database credentials from leaking into logs or CI output). To see the actual values, read `.env.local` directly.

<a id="示例"></a>
## Examples

```bash
lark-cli apps +env-pull --app-id <app_id>
```

<a id="失败处理"></a>
## Failure handling

For `missing_scope` (did not get `spark:app:read`), follow lark-shared to guide `lark-cli auth login --domain apps`. For other failures, prioritize relaying `error.hint` / `error.message`.

<a id="参考"></a>
## References

- [lark-apps](../index.md) — all Miaoda app commands + mental model
- [lark-apps-local-dev](lark-apps-local-dev.md) — end-to-end local app development workflow
- [lark-shared](../../shared/index.md) — authentication and global parameters
