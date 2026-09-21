# apps Git credential

Miaoda Git credentials are used for local native `git clone/pull/push`. For runtime command facts, refer to `lark-cli apps +git-credential-init --help`, `+git-credential-list --help`, and `+git-credential-remove --help`.

<a id="命令"></a>
## Commands

```bash
lark-cli apps +git-credential-init --app-id app_xxx
lark-cli apps +git-credential-list
lark-cli apps +git-credential-remove --app-id app_xxx
```

<a id="输出契约"></a>
## Output contract

- After `+git-credential-init` succeeds, read `data.repository_url`; do not display or save the credential details within it, and use it only for the next step `git clone`. The response also includes `data.commit_author_name` and `data.commit_author_email`; these two fields are consumed internally by `+init` and automatically written to the repository's repo-local git config (`user.name` / `user.email`), so the agent and user do not need to configure them manually.
- `+git-credential-list` returns the local record and status; it can be used to determine whether re-init is needed.
- `+git-credential-remove` only clears the local configuration; after success, inform that the cloud app or repository will not be deleted.

<a id="行为规则"></a>
## Behavior rules

- `+git-credential-init` returns `repository_url` and configures a URL-scoped Git credential helper. Subsequent clone/pull/push use native git.
- `+git-credential-list` lists the locally configured Miaoda Git credentials and does not require `--app-id`.
- `+git-credential-remove` only removes the local credential/helper and does not delete the cloud app or repository.
- After seeing the Repository URL, continue:

```bash
git clone <repository_url>
cd <repo>
git checkout sprint/default
```

<a id="agent-规则"></a>
## Agent rules

- Do not manually print, save, or concatenate the token.
- Code repository operations such as clone, pull, push, diff, and log all use native `git`; there are no code read/write shortcuts such as `apps +pull` / `apps +push` / `apps code +read`, so do not invent them.
- Do not push/force-push `main`; `main` is a release-state snapshot that is advanced server-side after `apps +release-create` succeeds, and direct push/force-push will be rejected by server-side guardrails.
- If Git authentication fails, the local credential is corrupted, or the helper is missing, re-run `+git-credential-init --app-id <id>` to overwrite the local configuration; do not ask the user to copy the token into the remote URL.
