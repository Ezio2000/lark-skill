<a id="生成和修改妙记管理妙记权限"></a>
# Generate and edit Minutes, manage Minutes permissions

Generating Minutes and editing Minutes are both write operations and must have explicit user intent. After successful generation, save `minute_token`; before editing, confirm the unique `minute_token` and the target content — providing a token does not equal authorization to edit. Except for `minutes +apply-permission`, the Minutes write commands in this scenario only support user identity; when the source identity is bot, stop and explain the limitation, and only after the user explicitly agrees, restart the editing flow with `--as user`. `minutes +apply-permission` supports user or app identity, and must use the same identity as when the permission error was triggered.

<a id="从本地音视频生成妙记"></a>
## Generate Minutes from local audio/video

The standard chain is Drive upload → Minutes create → read artifacts as needed. Do not switch to ffmpeg, Whisper, or other local ASR.

<a id="上传音视频到-drive"></a>
### Upload audio/video to Drive

Confirm the local media path and whether the user ultimately needs the Minutes link, transcript, summary, to-dos, or chapters. The source file must meet the format requirements of [`minutes +upload`](../references/lark-minutes-upload.md), with a duration of no more than 6 hours and a size of no more than 6 GB.

Follow the path and write operation rules of [`lark-drive`](../../drive/index.md) to execute `drive +upload` and obtain `file_token`. For upload parameters and file limits, see [`lark-drive-upload`](../../drive/references/lark-drive-upload.md).

<a id="使用-file_token-创建妙记"></a>
### Create Minutes using file_token

```bash
lark-cli minutes +upload --file-token <file_token> --as user
```

Extract `minute_token` from the last segment of the returned `minute_url` path, removing query parameters. For creation parameters, supported formats, and asynchronous semantics, see [`lark-minutes-upload`](../references/lark-minutes-upload.md). A successful `minutes +upload` only means the asynchronous creation request has been submitted; report the returned `minute_url` and the parseable `minute_token`. Before executing `minutes +detail` and confirming readiness, do not claim that the Minutes artifacts have been generated or are available. When the user only asks to initiate creation or return the link, stop here.

<a id="等待并读取妙记产物"></a>
### Wait for and read Minutes artifacts

When reading artifacts immediately after upload, you must add `--wait-ready`:

```bash
lark-cli minutes +detail --minute-tokens <minute_token> --wait-ready --transcript --as user
```

Replace or extend `--transcript` with the `--summary`, `--todo`, `--chapter`, or `--keyword` that the user needs. When the creation task is still processing, poll according to the returned status and retry hints; do not re-upload or re-create the Minutes.

When the user requests independent extraction or review, read the Transcript and analyze based on the original speech; do not restate the existing Summary. For artifact flags and waiting behavior, see [`lark-minutes-detail`](../references/lark-minutes-detail.md).

<a id="从失败阶段恢复"></a>
### Recover from the failed stage

- Drive upload succeeded but Minutes creation failed: retain and report `file_token`, continue from creating Minutes, and do not re-upload.
- Minutes creation succeeded but artifacts are not ready: retain `minute_token` and retry the query; do not re-create the Minutes.
- Do not misreport a successful Drive upload as a successful Minutes creation; clearly report whether the failure occurred at the upload, creation, or artifact generation stage.

<a id="修改妙记标题"></a>
## Edit Minutes title

Use `minutes +update --minute-token <token> ... --as user`. For parameters, see [`lark-minutes-update`](../references/lark-minutes-update.md).

<a id="替换-ai-总结"></a>
## Replace AI summary

Use `minutes +summary --minute-token <token> ... --as user` to replace the full summary text. For content format and permissions, see [`lark-minutes-summary`](../references/lark-minutes-summary.md).

<a id="增删改-ai-待办"></a>
## Add, delete, and edit AI to-dos

Minutes AI to-dos are not Feishu tasks. When the context contains a Minutes URL / `minute_token` and requires editing Minutes to-dos, it is forbidden to switch to `lark-task`; even if the user also specifies an assignee (including "the assignee is me"), the attribution does not change.

```bash
lark-cli minutes +todo --minute-token <token> --operation add|update|delete ... --as user
```

- For multiple additions, prefer using `--todos` for batch submission.
- Before updating or deleting, first execute `minutes +detail --minute-tokens <token> --todo --as user` and obtain the exact `todo_id` by content matching; do not use list order in place of the ID.
- For to-do IDs, batch structure, and partial success semantics, see [`lark-minutes-todo`](../references/lark-minutes-todo.md).

<a id="指定负责人"></a>
### Specify assignee

The established way for a Minutes to-do to indicate an assignee is to write `@姓名` as plain text into the to-do content; there is no independent assignee field:

- When the user directly provides a name, do not perform any lookup; concatenate the original text into `@姓名`.
- When the user says "the assignee is me", first use `lark-cli contact +get-user --as user` to get the real name and then concatenate; if it cannot be obtained, do not write any `@` mention, and do not retain the literal `@我`.
- Name resolution only affects the appended `@` text and must never block or cancel to-do creation; do not switch to `lark-task` to handle the assignee or perform further contact searches.
- Do not use "creating it under your identity means it belongs to you" as a substitute for the actual `@` text concatenation; `--as` identity and assignee are two unrelated things.
- In the reply, only state the result (Minutes, to-do content, assignee, completion status); do not explain API field limitations, and do not suggest switching to `lark-task` to "clarify the assignee".

For complete rules and examples, see "Assignee / `@` mention" in [`lark-minutes-todo`](../references/lark-minutes-todo.md).

<a id="批量替换逐字稿关键词"></a>
## Batch replace transcript keywords

`+word-replace` modifies the literal terms in the Minutes "transcription / transcript / text record" (different names for the same artifact).

`--minute-token` must be a Minutes token (for example `obcn...`); there are only two valid inputs: the `token` field returned by interfaces such as `minutes +search` / `vc +recording`, or the bare token extracted from the last path segment of the Minutes URL with query parameters removed. It is forbidden to directly pass the Minutes title, the slug in the URL, the meeting topic, or the full Minutes URL; when unsure, first run `minutes +search` / `vc +recording` to get `minute_token` before executing the replacement.

```bash
lark-cli minutes +word-replace --minute-token <token> --replace-words '[{"source_word":"<old>","target_word":"<new>"}]' --as user
```

Put multiple replacement groups in the same JSON array. For specific parameters, run `lark-cli minutes +word-replace --help`.

When the user provides the original word and the target word, replace directly: do not first read the Transcript to verify the wording, and do not read back the Transcript after a successful replacement to verify. The interface returns results word by word; just report according to the results.

As long as at least one keyword hits, it is a success: `data.message` lists the Succeeded and Failed keywords. When retrying, submit only the Failed words; do not resubmit the already successful words, otherwise the new words will be replaced again.

Only when none of the keywords hit is it a failure (`not_found`). This is a parameter issue, not a permission issue; truthfully tell the user which words did not hit, ask the user to confirm the exact wording, capitalization, and spaces, and then decide whether to retry; do not guess words on your own by reading the Transcript.

<a id="替换逐字稿说话人"></a>
## Replace transcript speakers

1. Call `lark-cli api GET "/open-apis/minutes/v1/minutes/<token>/transcript/speakerlist"` to obtain `speaker_id`.
2. Match exactly by the original speaker's display name. When candidates with the same name exist, show the candidates along with the Transcript and let the user confirm; do not choose on your own.
3. When the user only provides the target name, use [`lark-contact`](../../contact/index.md) to resolve it to the corresponding `ou_` open_id.
4. Execute `minutes +speaker-replace --from-speaker-id <speaker_id> --to-user-id <open_id> --as user`; do not pass the display name to `--from-speaker-id`.

For the complete flow and parameters, see [`lark-minutes-speaker-replace`](../references/lark-minutes-speaker-replace.md).

<a id="查看妙记授权列表"></a>
## View Minutes authorization list

When the user wants to see which members the Minutes has been authorized to, or query a member's current view / edit permissions, use the Drive collaborator list; this is not reading Minutes content, nor is it requesting permissions for the current identity. First read [`lark-drive`](../../drive/index.md) and [`drive +member-list`](../../drive/references/lark-drive-member-list.md).

```bash
lark-cli drive +member-list --token "<minute_url>" --as <source_identity> --format json
```

A full Minutes URL can automatically infer the resource type as `minutes`; a bare `minute_token` must explicitly pass `--type minutes`. When you need to verify a specified member, match exactly by `member_id` against the returned `items[]`; do not guess by name or list order.

<a id="分配妙记权限"></a>
## Assign Minutes permissions

When the user requests "share the Minutes with someone", "let someone view / edit", or "grant someone permission", what is being modified is the collaborator permission of the target Minutes, using `drive +member-add`; it is forbidden to use `minutes +apply-permission`, which only requests permission from the Minutes owner for the current calling identity.

First read [`lark-drive`](../../drive/index.md) and [`drive +member-add`](../../drive/references/lark-drive-member-add.md). When the target member has only a display name, uniquely resolve it to the corresponding ID according to [`lark-contact`](../../contact/index.md); when multiple candidates exist, ask the user to choose and do not guess.

```bash
lark-cli drive +member-add \
  --token "<minute_url>" \
  --member-id "<open_id>" \
  --member-type openid \
  --perm view \
  --yes \
  --as <source_identity> \
  --format json
```

A full Minutes URL can automatically infer the resource type as `minutes`; a bare `minute_token` must explicitly pass `--type minutes`. Choose `view` or `edit` according to the user's request; Minutes does not support `full_access`. Only when the Minutes, target member, and permission level are all clear, and the user has explicitly requested to execute the authorization, pass `--yes`.

After writing, use `drive +member-list` to read back and verify according to `member_id`. Only when the returned target member permission matches the user's request can you declare the assignment complete; if the target member already has a different permission, do not claim based only on the `member-add` receipt that the permission has been overwritten or downgraded.

<a id="为当前身份申请妙记权限"></a>
## Request Minutes permission for the current identity

When there is no view or edit permission, first state the permission facts. Only execute when the user explicitly requests to apply for permission:

```bash
lark-cli minutes +apply-permission --minute-token <token> --perm view --as <source_identity>
```

Choose `view` or `edit` according to the user's goal, and you must use the same identity as when the no-permission error was triggered. This only initiates an application and does not mean permission has been obtained. For identity and permission semantics, see [`lark-minutes-apply-permission`](../references/lark-minutes-apply-permission.md).

`permission_denied` means there is no edit permission for the Minutes, which is not the same as a missing OAuth scope; ask the owner to authorize, and do not mistakenly switch to `auth login --scope`.

<a id="asrai-额度不足"></a>
## Insufficient ASR/AI quota

`minutes +upload`, `+summary`, `+todo`, and `+word-replace` may all return `quota_exceeded`, indicating that the ASR/AI quota has been exhausted. `+upload` means the quota is insufficient to transcribe this audio/video, and the Minutes was not created at all; the other three mean that the quota was already used up when the Minutes was generated, the AI artifacts were not fully generated, and write operations cannot be persisted.

Ask the user to check the quota details on the Minutes detail page; do not retry: the CLI cannot supplement or increase the quota, and retrying the same request will not succeed. This is not a permission issue, and do not mistakenly switch to `+apply-permission` or `auth login --scope`.

<a id="确认修改结果"></a>
## Confirm edit results

Before editing, read only the target-related fields; after editing, read back with `minutes +detail` or the corresponding read interface. When the command itself already returns the write results item by item, do not read back again, for example the Succeeded / Failed keywords of `minutes +word-replace`. For batch or multi-step edits, report the pre-write value, post-write result, and failure reason item by item; on partial success, do not roll back the already successful items unless the command explicitly promises atomic rollback.
