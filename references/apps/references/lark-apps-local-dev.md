<a id="lark-apps-本地开发"></a>
# lark-apps local development

Applies to: the user wants to pull Miaoda app (full_stack, frontend, or html) source code to local, develop with a local code agent/IDE, then publish. The debug database applies only to full_stack (frontend / html have no database).

<a id="新建-vs-已有应用"></a>
## New vs existing app

Whether to create new or modify an existing one is determined by the entry point above (index.md "Choose development path"); once in the local flow, follow the branch:

- **New**: start from `+create` and follow the end-to-end flow below.
- **Existing app** (no source code locally yet): skip `+create`, first get `app_id` per "Existing app entry" below, then `+init` (or `+git-credential-init` + `git clone`) to pull it locally, then develop as usual.

<a id="端到端流程新建应用"></a>
## End-to-end flow (new app)

### full_stack

`+create(full_stack)` -> `+init` (or manually `+git-credential-init` + `git clone`) -> read repo Skill -> `npm install && npm run dev` -> `+db-*` to call the database as needed -> for non-automation changes, commit/push/release per this page; when automation handlers are included, before any release switch to the [automation SOP](lark-apps-automation.md), which takes over the state gate and the full release.

```bash
# Create a new full_stack app
lark-cli apps +create --as user --name "审批系统" --app-type full_stack \
  --description "支持登录、提交申请、多级审批、状态查询"

# Initialize the local repository (for --dir values see "Domain rules" below; do not copy the example value here)
lark-cli apps +init --as user --app-id app_xxx --dir ./approval-app

# After entering the repository, start per the project scaffold
cd ./approval-app
npm install
npm run dev

# After development is complete: commit this change -> git push origin sprint/default -> +release-create.
# +release-create deploys the code already pushed on the remote sprint/default, not your local working tree—changes not committed + pushed will not enter the release.
git add <本次开发的文件>          # For commit granularity see "Deploy and go live after code changes" below
git commit -m "feat: ..."
git push origin sprint/default
lark-cli apps +release-create --as user --app-id app_xxx --branch sprint/default
```

### frontend

Pure frontend app (vite-react, no database). The flow is basically the same as full_stack—`+init` to install dependencies, `npm run dev`, commit/push/release—the difference is there is no `+db-*` database-call step. When database/backend capabilities are needed later, do not upgrade locally; follow index.md "Type upgrade" to guide to a cloud session.

```bash
# Create a new frontend app
lark-cli apps +create --as user --name "JSON 格式化工具" --app-type frontend \
  --description "纯前端交互工具，无需数据库"

# Initialize the local repository (for --dir values see "Domain rules" below; do not copy the example value here)
lark-cli apps +init --as user --app-id app_xxx --dir ./json-tool

# After entering the repository, start per the project scaffold (vite-react)
cd ./json-tool
npm install
npm run dev

# After development is complete: commit this change -> git push origin sprint/default -> +release-create
git add <本次开发的文件>
git commit -m "feat: ..."
git push origin sprint/default
lark-cli apps +release-create --as user --app-id app_xxx --branch sprint/default
# Publishing is asynchronous: only when +release-get polls to status=finished is deployment complete and online_url obtained
lark-cli apps +release-get --as user --app-id app_xxx --release-id <上一步返回的 release_id>
```

### html

<a id="首次开发无-app无代码"></a>
#### First development (no app, no code)

`+create(html)` → `+init` → load the [`creative-design`](../creative-design/creative-design.md) skill to produce files in the repo root → `git add .` + `git commit` → `git push origin sprint/default` → `+release-create` → `+release-get`.

```bash
lark-cli apps +create --name "活动页" --app-type html --as user

lark-cli apps +init --app-id app_xxx --dir ./my-page

cd ./my-page
# The html type does not need npm install; +init already skips dependency installation
# Load the creative-design skill to produce HTML and related files in the repo root (JSX components, starter components, etc.)

git add .
git commit -m "feat: ..."
git push origin sprint/default
lark-cli apps +release-create --app-id app_xxx
```

<a id="已有-app二次开发迭代"></a>
#### Existing app, secondary development/iteration

`+init` (pull remote code) → load the creative-design skill to iterate in the repo root → `git add .` + `git commit` → `git push origin sprint/default` → `+release-create` → `+release-get`.

<a id="creative-design-已提前生成文件需要-init-后迁入"></a>
#### creative-design already generated files, need to migrate in after init

`+create(html)` → `+init` → first `ls` to view the repo root template structure (the creative mode template has no `src/` directory; files go directly in the root) → copy all already-generated output files (HTML, JSX components, starter components, etc.) to the repo root → `git add .` + `git commit` → `git push origin sprint/default` → `+release-create` → `+release-get`.

`+init` is the recommended convenient entry point; when you want step-by-step manual control, first `+git-credential-init` to get `repository_url`, then use native `git clone` / `git checkout sprint/default`.

When plugin integration is needed, read the app repository's `<project-path>/.agents/skills/plugin-guide/SKILL.md` to learn the plugin directory, instance configuration, and invocation method. It is the app project's own skill and is not within this package's module renaming scope; when the file does not exist, look it up per the project's actual documentation.

<a id="trigger-guide-的项目边界"></a>
## Project boundaries of the Trigger guide

When automation business code is involved, first check the workspace `.agents/skills/` and read the `trigger-guide` matching the automation task. It defines the implementation and integration constraints of business handlers; for Apps trigger configuration details see the [automation SOP](lark-apps-automation.md).

When the file is missing or cannot cover the current task, report that the project lacks a usable domain guide; do not guess installation commands, versions, or in-package directories in this lark-cli reference. Have the project maintainer fill it in through their supported initialization or sync flow, then continue the code loop; `+init` is only responsible for preparing the local project and cannot replace the domain guide.

<a id="改完代码后部署上线"></a>
## Deploy and go live after code changes

When the code has been pulled locally and changed, and the user says "push it up", "deploy", "go live", or "publish to the cloud", follow this sequence.

If this change includes automation handlers, before executing this section's general commit/push/release sequence, switch to the matching path of the [automation SOP](lark-apps-automation.md), and let that SOP handle the full state gate, commit/push, release, and optional enable/test; do not publish per this section first and then add trigger state checks. The general sequence below is only for changes that do not include automation handlers.

> `+release-create` deploys the code **already pushed** on the remote `sprint/default`, not your local working tree—changes not committed / not pushed will not enter this release. So before publishing, be sure to commit and push this change first.

1. `git status` to see this change; `git add <本次相关文件>` to stage, then `git commit` to commit. Just commit the changes relevant to this task; there is no need to force-clear unrelated scattered files—the release gate is "**this task's relevant changes are committed and pushed**", not "the working tree is absolutely clean".
2. `git push origin sprint/default` to push the working branch to the cloud (on non-fast-forward: first `git pull --rebase origin sprint/default` to resolve conflicts then push, never force-push; on Git authentication failure / 401 / 403 / missing credential helper / expired token: first run `lark-cli apps +git-credential-init --app-id <app_id> --as user` to refresh local Git credentials, then retry the original git command; if refreshing credentials also fails, stop and report the error to the user, do not switch paths).
3. `lark-cli apps +release-create --as user --app-id <app_id> --branch sprint/default` to initiate deployment and go live, and note the returned `release_id`.
4. `lark-cli apps +release-get --as user --app-id <app_id> --release-id <release_id>` to poll: when `publishing`, keep polling every 20 seconds, for at most about 5 minutes overall; if it still has not completed on timeout, stop this round of polling and report `release_id` and the current status. When `finished` succeeds, if `online_url` is returned, it can be used directly; when it is not returned, do not fabricate a link. Before delivering the online access link to others, note that `online_url` is by default visible only to the creator, so first inform that it is currently visible only to yourself, and use `+access-scope-set` as needed to open up the visibility scope. No need to call `+list` again; when `failed`, if a non-empty `error_logs` is returned, give the failure reason based on it; otherwise only report `release_id` and the current status, do not fabricate a reason (`+list` is only an independent query entry point).

When the user only asks to enable an existing trigger, switch to [the "enable existing disabled trigger only" path of the automation SOP](lark-apps-automation.md#仅启用已有-disabled-trigger); do not, because of enable, reversely modify the handler, commit/push, or release.

<a id="领域规则"></a>
## Domain rules

- Code reading and writing use native `git`; the CLI handles credentials, initialization, publishing, and database debugging. There are no code read/write shortcuts such as `apps +pull` / `apps +push` / `apps code +read`; do not invent them.
- When the working environment has no `git`, first guide installation of Git (on macOS use `xcode-select --install` or `brew install git`; on Linux install per the distribution's package manager), then retry the original `+init` / git command; do not switch to another publishing path because of this.
- `+init` orchestrates `+git-credential-init`, `git clone`, switching to `sprint/default`, running the scaffold, and committing/pushing when there are changes.
- `+init --dir` uses the user-specified directory; when unspecified, you may choose a new empty directory based on the app name and explain its location. When the directory already exists and is non-empty, first confirm whether it is the target project to avoid overwriting; only ask when it cannot be determined.
- `sprint/default` is the working branch; `main` is the release-state snapshot, advanced by server-side fast-forward after `+release-create` succeeds; server-side guardrails prohibit direct push to `main`, reject force-push, and require `sprint/default` fast-forward.
- Once pulled locally, use native git for pull/push/diff/log; when the cloud `sprint/default` is newer than local, first `git pull --rebase origin sprint/default`, then push and publish after resolving conflicts.
- If `git clone` / `git pull` / `git push` report authentication failure, 401/403, missing credential helper, or expired token, preferentially re-run `lark-cli apps +git-credential-init --app-id <app_id> --as user` to update local Git credentials, then retry the original git command; if refreshing credentials also fails, stop and report the error to the user, do not switch paths; do not manually copy the token, and do not splice the token into the remote URL.
- Environment variables are handled by the scaffold at local startup; when a manual refresh is needed, use `+env-pull`.
- Resource-type files (images, fonts, audio/video, etc.) must not directly reference local paths, nor be committed to the git repository or inlined into code as base64. First upload to the app file storage via `lark-cli apps +file-upload --app-id <app_id> --file <local_path>`, and after obtaining the returned remote URL, reference that URL in the code. For details read [`lark-apps-file.md`](lark-apps-file.md). The link returned by upload is isolated per app; different apps must each re-upload and cannot reuse the same link across apps.
- For DB debugging use `+db-table-list` / `+db-table-get` / `+db-execute`; do not connect to the database bare or build connection strings yourself.
- DB is divided into `dev` / `online`; use `--environment dev|online`, do not use the old `--env`. Only guide `--environment dev` when it is confirmed that the app has multi-environment enabled; for single-environment apps omit `--environment` (the server selects online) or explicitly pass `--environment online`. Writing in dev cannot prove the online handler has been verified. When a dev database structure change needs to go live, still follow the app publishing path via `+release-create`; do not create a separate "database release" step.
- When an existing single-database app needs dev/online multi-environment, use `+db-env-create --environment dev`. This is an irreversible high-risk operation.
- Seeing `is_published=true` only from `+list` cannot prove that the code just pushed locally has been deployed; there must be a `+release-get finished` for this round.

<a id="存量应用入口"></a>
## Existing app entry

For an existing project directory, first read `.spark/meta.json` to get `app_id`; when there is no local project but the app name is known, use:

```bash
lark-cli apps +list --keyword "应用名"
```

After obtaining `app_id`, then `+init` or `+git-credential-init`.

<a id="何时不用"></a>
## When not to use

- The user explicitly wants the cloud Miaoda Agent to generate/iterate, rather than writing code locally: read [`lark-apps-cloud-dev.md`](lark-apps-cloud-dev.md).
