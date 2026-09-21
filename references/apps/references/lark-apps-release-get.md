# apps +release-get

Query details of a single release by release ID. For runtime command facts, refer to `lark-cli apps +release-get --help`.

<a id="何时用"></a>
## When to use

Use this to follow up on the release status of a known `release_id`. When there is no `release_id`, first read [`lark-apps-release-list.md`](lark-apps-release-list.md); do not ask the user to fill it in manually.

`release_id` is the Miaoda release ID (returned by `+release-create`), not a Feishu approval instance number; checking release progress/failures is all done within the `apps +release-*` command family, so do not route to lark-approval.

<a id="命令骨架"></a>
## Command skeleton

- Required: `--app-id`, `--release-id`.
- `release_id` comes from `+release-create` or `+release-list`.

<a id="示例"></a>
## Example

```bash
lark-cli apps +release-get --app-id app_xxx --release-id release_yyy
```

<a id="输出契约"></a>
## Output contract

- On success, the release fields may be returned directly, or they may be wrapped in `data.release`; read `release_id`, `status`, `created_at`, `updated_at`, and `commit_id` (the git commit SHA corresponding to this release; pretty output shows a line for it when it is non-empty).
- `status=publishing` keep polling. At this point there is still no `online_url`; do not pass off other links (such as the app homepage / development preview URL in `+list`) as the "access link for this release"—only report `release_id`, `status`, and explain that `online_url` may only exist after `finished`.
- `status=finished` release succeeded—if the output contains `online_url`, read it directly as the online access link for this release; if it is not returned, only report that the release is complete and do not fabricate a link. By default, this link is visible only to the creator; before delivering it to others, first inform them that it is currently visible only to you, and use `+access-scope-set` as needed to open up the visibility scope. There is no need to call `+list` again (`+list` can still be used to browse by app name, but it is not a required step in the main release flow).
- `status=failed` release failed—if the output contains `error_logs` (`step`/`error_log`), use it to relay to the user the key failed step and actionable fixes; if it is not returned, do not fabricate a failure reason.
- Only when this `release_id` has already returned `finished` can the `online_url` read afterward be described as the "access link after this release." Seeing `is_published=true` from `+list` alone cannot prove that the latest version has been deployed.
