# apps +init

`+init` Initializes the code for a Miaoda app (clone the repository, scaffold/sync the source code, pull local environment variables). For runtime command facts, `lark-cli apps +init --help` is authoritative.

<a id="何时用"></a>
## When to use

Use this to pull the Miaoda app source code locally and prepare the development environment. When the user only wants the cloud Agent to generate an app, do not initialize a local repository.

<a id="命令骨架"></a>
## Command skeleton

- Required: `--app-id`.
- Optional: `--dir`, the clone target directory; when omitted, defaults to `./<app-id>`.
- Fixed checkout branch: `sprint/default`.
- `+init` initializes Git credentials, clones the repository, switches to the working branch, and generates/syncs the local project.

<a id="示例"></a>
## Examples

```bash
lark-cli apps +init --app-id app_xxx --dir ./my-app
lark-cli apps +init --app-id app_xxx --dir /absolute/path/my-app
lark-cli apps +init --app-id app_xxx --dir ./my-app --dry-run
```

<a id="输出契约"></a>
## Output contract

- On a real run, stdout is a JSON envelope; stderr will have `->` / `→` progress lines. On success, read stdout; on failure, parse the JSON error at the end of stderr.
- On a successful normal initialization, read `data.clone_path`, `branch`, `committed`, `pushed`; `repository_url` has been redacted, do not use it as a credential.
- `scaffold=already_initialized` indicates the directory is already initialized: skip clone/scaffold/commit, but still perform one env-pull to refresh local environment variables (the output contains `env_pulled`, on success contains `env_file`, on failure contains `env_pull_error` and the exit code is still 0); in this case there is usually no `repository_url` / `branch`.
- `--dry-run` only prints the plan and does not execute git / npx; if the output contains `dir_error`, have the user change directories before a real run.

<a id="agent-规则"></a>
## Agent rules

- The target directory must not exist, must be an empty directory, or must already contain `.spark/meta.json` with an app_id matching `--app-id` for an already initialized repository.
- When the target directory already contains `.spark/meta.json`, `+init` skips clone/scaffold but still performs one env-pull to refresh local environment variables; tell the user "the repository is already initialized, local environment variables have been refreshed, and you can develop directly", and do not falsely report failure or clone again.
- There is no need to repeat the `+init` output verbatim; just tell the user the clone path, branch, and next step.
- When doing local initialization for a new app, if the selected target directory already exists, do not reuse it; use a non-conflicting directory name instead (when "just do it" has been pre-authorized, automatically append a suffix such as `-2`; otherwise confirm the directory name with the user).
