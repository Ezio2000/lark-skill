# Miaoda / Spark apps

Use only when the user selected Miaoda/Spark, supplied its app/link, or is working in an existing Miaoda project. Generic local web/design work does not authorize creating an app. Apps are personal assets: use `--as user`, reuse login, and load [authentication](../shared/index.md) only for actual errors or setup.

## Resolve the app and development path

1. Use a supplied `app_...` ID or app link.
2. In an initialized project, read `.spark/meta.json`.
3. Otherwise search `lark-cli apps +list --keyword "<name>" --as user`; disambiguate only if needed.
4. A creative-mode `/page/<meta_token>` link is an app. `apps +get --app-id <meta_token>` resolves its app ID.

Modifying an existing app does not authorize creating another. App type and development method are independent:

| Requirement | App type / method |
|---|---|
| Server persistence/database/backend | `full_stack` |
| Static display without JavaScript interaction | `html`; [creative design](creative-design/creative-design.md) |
| Interactive frontend without persistence | `frontend` |
| Work in the current local project / write code locally | [Local development](references/lark-apps-local-dev.md) |
| User selected Miaoda AI generation | [Cloud development](references/lark-apps-cloud-dev.md) |

Do not infer a database merely from "tool/system". Resolve genuinely material ambiguity. For a new app with no indication of local code versus cloud generation, ask which development method is intended. An existing local project continues locally; existing-app modifications otherwise prefer local unless cloud was selected.

Initialize development with `+init` after reading the local guide; source-only snapshots or shared apps without repository access use `+export`. Frontend-to-full-stack upgrades occur in the cloud editor, not through a local type-upgrade command.

## Deploy and resources

- Local deployment requires commit/push of the requested changes, then `+release-create` and `+release-get`. Report `online_url` only after `finished`; report `error_logs` after failure. Session completion or `is_published=true` does not prove the latest revision was deployed.
- New HTML creative apps use the same Git/release path. `+html-publish` is only for legacy non-Git HTML apps, not a fallback for failed Git.
- On credential-related Git failure, refresh through `+git-credential-init` and retry once. Report persistent/environment failures.
- Creative HTML apps use the same `/page/<meta_token>` link for editing/published access; frontend/full-stack editor links are `https://miaoda.feishu.cn/app/<app_id>`.
- CLI file/path/output arguments require cwd-relative paths. Run in the intended task directory. Upload images/fonts/media with `+file-upload` and use the returned app-specific URL; do not reuse another app's storage URL.
- Read matching project-local `.agents/skills/` instructions for runtime SDK contracts. Runtime code uses those SDKs, not subprocess calls to `lark-cli`. Platform role lookups are facts, not a hardcoded business-role policy.

## Operations and lifecycle

- Request/error/latency/CPU/memory metrics use [observability](references/lark-apps-observability.md): `+metric-list`; PV/UV/active visitors use `+analytics-list`. Resolve the app instead of searching unrelated local monitoring files.
- Read [database](references/lark-apps-db.md) for migrations, recovery, audit, and Base sync; [SQL](references/lark-apps-db-execute.md) for execution and platform SQL rules. Base sync creates one task per table. Batch/import tasks cannot be re-enabled; persistent sync requires a streaming task.
- Environment/cache/role mutations reuse authorization for the exact app, environment, and target. Use required `--yes` flags without inventing an additional confirmation phrase. Error hints are diagnostic suggestions, not new user authorization.
- Session-turn messages use `+session-get` to obtain the turn ID, then `+session-messages-list --turn-id <id>` with pagination.
- API-key and webhook secret values are returned only at creation/reset; follow the operation contract rather than promising later retrieval.

## Collaborators

Development collaborators, runtime access scope, and in-app roles are different APIs. Collaborator calls use `app_...` and user identity; do not prefilter by app type.

Read commands require `spark:app:read`; writes require `spark:app:write` and `--yes`. Preview uncertain typed-ID payloads with `--dry-run`. Write ID types are `openid` / `openchat` / `opendepartmentid`, with matching `ou_` / `oc_` / `od-` IDs. List filters instead use `user|department|chat` and `view|edit|full_access`; list returns all direct collaborators without pagination.

Use exact `apps +member-list|add|update|remove` or `+member-settings-get|set` help for missing parameters. `external_invite` and `copy_download_by` are read-only response fields, not writable flags. `external_invite` follows `external_access`. Error `feature_not_available` / `3340005` (sometimes `40005`) requires the Miaoda console, not an attempted workaround through roles/access scope.

## Operation references

Read only the reference matching the current operation.

- [apps create](references/lark-apps-create.md)
- [apps list](references/lark-apps-list.md)
- [apps get](references/lark-apps-get.md)
- [apps update](references/lark-apps-update.md)
- [apps html publish](references/lark-apps-html-publish.md)
- [apps init](references/lark-apps-init.md)
- [apps git credential](references/lark-apps-git-credential.md)
- [apps export](references/lark-apps-export.md)
- [apps env pull](references/lark-apps-env-pull.md)
- [apps env](references/lark-apps-env.md)
- [apps file](references/lark-apps-file.md)
- [apps cache](references/lark-apps-cache.md)
- [apps release create](references/lark-apps-release-create.md)
- [apps release get](references/lark-apps-release-get.md)
- [apps release list](references/lark-apps-release-list.md)
- [index](../drive/index.md)
- [apps role](references/lark-apps-role.md)
- [apps openapi key](references/lark-apps-openapi-key.md)
- [apps automation](references/lark-apps-automation.md)
- [apps session messages list](references/lark-apps-session-messages-list.md)
- [apps plugin install](references/lark-apps-plugin-install.md)
- [apps plugin uninstall](references/lark-apps-plugin-uninstall.md)
- [apps plugin list](references/lark-apps-plugin-list.md)
- [apps user id convert](references/lark-apps-user-id-convert.md)
- [shared high risk approval](../shared/references/lark-shared-high-risk-approval.md)
