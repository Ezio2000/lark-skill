# apps +export

`+export` packages the source code of a Miaoda app into a zip and downloads it locally. For runtime command facts, `lark-cli apps +export --help` is authoritative.

<a id="何时用"></a>
## When to use

Scenarios where you just need a source snapshot: reading code, auditing, archiving, doing static analysis, feeding the source to other tools.

**Cross-app is its core value relative to `+init`**: a creative app's share link (`/page/<token>`) points to someone else's app, you have no permission on that repository, and `git clone` won't work; `+export` only requires that you have download permission on that app.

<a id="不要用它的时候"></a>
## When not to use it

If you want to continue development, use `+init`, not `+export` followed by a manual `git init`. The two produce different results:

| | `+export` | `+init` |
|---|---|---|
| Output | a zip | a full git workspace |
| Git credentials | not configured | configured, can push |
| Local environment variables | not pulled | pulls `.env.local` |
| Prerequisite | download permission on the app | permission on the **repository** |

The directory you get with `+export` has no git history, no remote, and no credentials, so you can't push changes back.

<a id="导出的是最后一次提交不是沙箱当前状态"></a>
## What is exported is the "last commit", not the sandbox's current state

The server runs `git archive` against the remote repository and never reads the sandbox filesystem. If a user changed files in the sandbox but didn't commit or publish, **those changes are not in the archive**.

This is by design, not a defect. If the export result looks like it's "missing code that was just written", first confirm whether the changes were committed, rather than retrying the export.

<a id="命令骨架"></a>
## Command skeleton

- `--app-id` and `--meta-token`: **pass exactly one of them**: the former is your own app, the latter is the token in a share link.
  The two go as independent fields in the request body of `POST /apps/export` (`app_id` / `meta_token`), and the server distinguishes them by the
  field passed in, no longer sharing a path segment—so callers who only have a token and no app_id don't have to cobble together a placeholder value in the path.
  - Both accept only a **bare identifier**. If you have the full link (`.../app/<app_id>` or `.../page/<token>`),
    pass only the last segment—passing the whole URL in will be caught locally and flagged, and won't turn into a 404 that looks like "app does not exist".
- `--output` is optional, relative to the current directory; when omitted, the filename given by the server is used (usually `<app_id>.zip`).

<a id="示例"></a>
## Examples

```bash
lark-cli apps +export --app-id app_xxx --output ./src.zip
lark-cli apps +export --app-id app_xxx                      # Save as ./app_xxx.zip
lark-cli apps +export --meta-token <share-token>            # An app someone shared with you
lark-cli apps +export --app-id app_xxx --dry-run
```

<a id="输出契约"></a>
## Output contract

- On success, stdout is a JSON envelope containing `output` (the absolute path written to disk) and `size_bytes`; when `--app-id` is passed, `app_id` is also echoed back.
- The archive is written to disk as a stream, so the whole package doesn't reside in memory, making it safe even for large repositories.
- On failure, no half-written file is left behind.

<a id="错误处理"></a>
## Error handling

| Situation | What to do |
|---|---|
| App not yet published (`code 40901 app not published`) | This app is in artifact-hosting form (such as a static HTML app), and what gets exported is the "latest published artifact", but it hasn't successfully published a version yet, so there's nothing to export right now. **Publish the app first, then retry**—it's not a wrong app_id, and retrying won't help |
| Insufficient permission (403) | You need download permission on the app. **Holding a share token does not mean you have permission** |
| App does not exist (404) | Use `+list --keyword <name>` to verify the app_id |
| Archive too large (413) | Exceeds the export size limit; switch to `+git-credential-init` + native git clone |
| Parameter error | `--app-id` and `--meta-token` can only be given one, and exactly one must be given; both require a bare identifier (not the full link) |
