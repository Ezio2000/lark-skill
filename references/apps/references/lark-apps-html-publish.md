# apps +html-publish

Publish a local HTML file or static directory as a Miaoda app access URL. For runtime command facts, refer to `lark-cli apps +html-publish --help`.

<a id="何时用"></a>
## When to use

Use this to publish an existing local HTML file or static artifact directory as a Miaoda access URL. It is not responsible for generating HTML content, nor for publishing full-stack application code.

<a id="命令骨架"></a>
## Command skeleton

- Required: `--app-id`, `--path`.
- `--path` **must be a relative path** (such as `./dist`, `./index.html`); absolute paths are not supported. If the target file is in another directory, first `cd` to that directory and then use a relative path, or use a path relative to the current directory.
- `--path` can be a single file or a directory; the entry point must be `index.html`.
- Optional: `--allow-sensitive`, to skip credential file scanning.
- The client packages a tar.gz and uploads it for publishing. There are three hard size limits; if any one is exceeded, the client rejects it and publishing cannot proceed: a single `.html` file ≤ 10MB, the packaged tar.gz ≤ 20MB, and the total uncompressed candidate file size ≤ 200MB.

<a id="示例"></a>
## Example

```bash
lark-cli apps +create --name "Demo" --app-type html
lark-cli apps +html-publish --app-id app_xxx --path ./dist
lark-cli apps +html-publish --app-id app_xxx --path ./index.html --dry-run
```

<a id="输出契约"></a>
## Output contract

The command internally completes tar.gz packaging → TOS upload → triggers publishing, and returns `data.release_id`. After obtaining `release_id`, use `+release-get --app-id <app_id> --release-id <release_id>` to poll the publishing status until `finished`, and read `online_url` from it.

- Business failures such as build failures or a nonexistent app usually include `error.hint`; prioritize relaying the hint. For network/server failures, suggest retrying later.

<a id="链接边界"></a>
## Link boundaries

- The published access link is based on the `online_url` returned by polling `finished` with `+release-get`.
- Before republishing, the `is_published=true` of `+list` only indicates that it was published historically; it does not mean the current local artifact has been deployed.

<a id="发布前置门第一步先于任何其他动作"></a>
## Pre-publish gate (first step, before any other action)

After receiving a publishing intent, the first action is to measure three sizes, not to read file contents and not to package:
1. A single `.html` ≤ 10MB / tar.gz ≤ 20MB / total uncompressed size ≤ 200MB.
2. If any one exceeds the limit → STOP immediately, relay the exceeded number to the user, and hand the decision back to them.
3. Only if all three pass → proceed to the command skeleton below.

<a id="预览与发布边界"></a>
## Preview and publish boundaries

- When the user only says "write a PPT/page with HTML for me to look at", first generate the local file or directory, return the path, and ask whether to publish it to Miaoda for sharing; do not create an app or deploy by default.
- Only when the user explicitly says "deploy it/publish a link/shareable" should you create a `html` app and use `+html-publish`.
- If the user wants to publish but there is no app_id, first use `+create --app-type html` to create an app; the app name can be generated from the page/site theme, and do not make the user manually provide an app_id.
- If the artifact's homepage is not `index.html`, rename or copy it to `index.html` before publishing; when publishing a directory, pass only the clean artifact directory, for example `./dist`. The `.git` directory is automatically excluded and will not enter the archive.
- When redeploying the same HTML app, reuse the original `app_id` and only re-execute `+html-publish --app-id <id> --path <dir-or-index.html>`.

<a id="安全规则"></a>
## Security rules

By default, credential files such as `.env`, `.npmrc`, and `.aws/credentials` are blocked. Only when the user explicitly wants to publish credential example files or tutorial content should you append `--allow-sensitive`; before appending, first explain which sensitive candidate files will be included.

<a id="常见失败"></a>
## Common failures

- `--path` was passed an absolute path: `--path` only accepts relative paths, and passing an absolute path reports `--path must be a relative path within the current directory`. Use `cd` + a relative path instead, for example `cd /target/dir && lark-cli apps +html-publish --path .`.
- Missing `index.html`: place `index.html` at the directory root, or point the single-file path directly to a file named `index.html`.
