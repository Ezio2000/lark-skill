# apps +release-create

Create a release for a Miaoda app. For runtime command facts, refer to `lark-cli apps +release-create --help`.

<a id="何时用"></a>
## When to use

Use this to advance an app's code branch into the release process (html / frontend / full_stack all go through this entry point).

<a id="命令骨架"></a>
## Command skeleton

- Required: `--app-id`.
- Optional: `--branch`; when omitted, the server uses the default release branch.
- Returns `release_id` and `status`; subsequently poll with `+release-get`.

<a id="示例"></a>
## Example

```bash
lark-cli apps +release-create --app-id app_xxx
lark-cli apps +release-create --app-id app_xxx --branch sprint/default --dry-run
```

<a id="输出契约"></a>
## Output contract

- Successfully reads `data.release_id`, `data.status`, and `data.sync`; `release_id` is the input parameter for the subsequent `+release-get`.
- `sync=true` indicates synchronous deployment (the server waits for deployment to complete before returning); `sync=false` or missing indicates asynchronous deployment.
- `status=publishing` indicates the release is still in progress; continue polling with `+release-get`, and the polling interval should be 20s. App releases take about 2min on average, and the overall timeout is about 5min.
- `status=finished` indicates deployment is complete (in synchronous deployment, this status may be returned directly).
- `+release-create` returning a release only means the release has been initiated. Only after `+release-get` returns `finished` for the same `release_id` can you say that the latest version of this round has been deployed.

<a id="agent-规则"></a>
## Agent rules

`+release-create` deploys code that has already been pushed to the remote `sprint/default`, not the local workspace—if you have local changes that you modified but have not pushed, you need to first `git add` + `git commit` and `git push` to `sprint/default`, otherwise these changes will not be included in this release. If `git push` encounters authentication failure, 401/403, a missing credential helper, or an expired token, first run `lark-cli apps +git-credential-init --app-id <app_id> --as user` to refresh the local Git credentials, then retry the original git command; if refreshing credentials also fails, stop and report the error to the user, do not take a different path; do not manually copy the token or change the remote URL. After release, if the status is `publishing`, query with [`+release-get`](lark-apps-release-get.md). `+release-create` deployment and go-live is a high-impact action—when it is a consequential prerequisite for another command, obtain user consent first according to "High-impact actions and authorization" in index.md before releasing.
