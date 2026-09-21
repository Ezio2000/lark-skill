<a id="apps-automation-触发器命令族-sop"></a>
# apps automation trigger command family SOP

Manage automation triggers for Miaoda apps (four types: scheduled / record change / Webhook / Feishu approval). All operations require `--as user` (AuthType: user). `--help` is the complete source for parameter details; this file only records domain rules that an Agent will get wrong if it does not read them.

<a id="何时用本模块路由锚点"></a>
## When to use this module (routing anchors)

**When a user message contains a "Miaoda app name / app_id" + any of the following intents, route to this module, do not go through lark-event or lark-openapi-explorer:**

- "(every day / scheduled / every N hours / every week on X) run automatically / trigger automatically / sync on schedule" → `+automation-create --trigger-type cron`
- "when a data table / record / field X in the table is (added / updated / deleted / changed) (trigger / notify / process)" → `+automation-create --trigger-type record-change`
- "(webhook / external callback / external system call / HTTP trigger)" → `+automation-create --trigger-type webhook`
- "after (approval / reimbursement / leave request / business trip) is (approved / rejected / submitted / withdrawn), automatically X" → `+automation-create --trigger-type feishu-approval`
- "which (automations / triggers / scheduled tasks) are configured for this app" → `+automation-list`
- "(pause / disable / stop running automatically for now / turn off automatic triggering) a certain (trigger / scheduled task / automation)" → `+automation-disable` (not update to change conditions, not delete—this module does not provide deletion)
- "enable / start an existing trigger" → first verify the existing state; when only enabling, do not modify source code or publish the app.
- "change / reset the webhook callback address / URL" → `+automation-update --reset-url --app-env <preview|runtime>`
- "change / reset / rotate the webhook token / bearer" → `+automation-update --reset-token`
- "the trigger is not responding / enabled but not triggering / why did it not execute / verify the trigger" → first diagnose according to "Diagnostic order when not triggered"; for UPSERT and feishu-approval, only verify configuration boundaries, do not promise handler or live verification.

**Boundary (prevent mis-routing)**: `lark-event` is **real-time event stream consumption** (agent long-connection event subscription), and does not manage the **configuration** of Miaoda app triggers; when the user says "configure / set up a trigger" rather than "subscribe to an event stream", this module is the correct choice. "Trigger on approval approval" in the context of a Miaoda app belongs to this module's `feishu-approval` type, not lark-event.

<a id="回应怎么配类问题的正确姿势"></a>
### The correct posture for responding to "how to configure" questions

When the user asks "how to configure / how to set up an X trigger", **first show the complete command template + your inference of the core parameters** (so the user can confirm you understood correctly), then ask about the missing required items (such as `--name`) or optional items. **Do not skip the display and directly ask a chain of questions**, because then the user cannot confirm whether you understood the intent.

Example: the user says "once a reimbursement approval is approved, automatically trigger processing, how do I configure it?"
- ✅ Correct: first write out "this is the feishu-approval type, command template: `apps +automation-create --app-id <id> --name <name> --trigger-type feishu-approval --event-type approval_instance --instance-status APPROVED [--approval-code <code>]`. I need you to confirm: (1) the trigger name `<name>`; (2) whether to limit it to a specific approval process—if limited, pass `--approval-code` (obtained from the Feishu Approval admin console), if not passed it matches all approval definitions".
- ❌ Wrong: directly ask "what is it called? which approval does it listen to?"—the user cannot confirm whether you mapped "approval approved" to `--event-type approval_instance --instance-status APPROVED`.

Similarly, the "how to configure" for the three types cron/record-change/webhook all follow this pattern: first give the command + parameter inference, then ask about missing items.

<a id="命令路由"></a>
## Command routing

| Command | Purpose | Risk |
|---|---|---|
| `+automation-list` | List all triggers of the app (can filter by type, `--all` aggregate pagination) | read |
| `+automation-get` | View the complete configuration of a single trigger (Webhook Bearer Token always masked) | read |
| `+automation-create` | Create a trigger, all four types share one command, dispatched by `--trigger-type` | write |
| `+automation-update` | Change conditions/description, or manage Webhook URL·Token via dedicated flags | high-risk-write |
| `+automation-enable` | Enable a trigger (`status→enabled`, starts automatic triggering) | write |
| `+automation-disable` | Disable a trigger (`status→disabled`, stops triggering, does not delete) | write |

Triggers are located by the **app-internal unique `--name`** (not id). All single-item commands use `--app-id` + `--name`; if you forgot the name, first look it up with `+automation-list`.

<a id="四类触发器-payload"></a>
## Payloads for the four trigger types

`--trigger-type` uses Agent-facing kebab-case (`cron` / `record-change` / `webhook` / `feishu-approval`), and the CLI internally converts to snake_case before pushing down. Type-specific flags only take effect for the corresponding type.

<a id="cron定时"></a>
### cron (scheduled)

```bash
+automation-create --app-id <id> --name daily --trigger-type cron \
  --cron '0 9 * * *' [--timezone Asia/Shanghai]
```

- `--cron` is **five-field** (`minute hour day month weekday`), not six-field.
- **Minimum interval 30 minutes**: `--cron '* * * * *'` (every minute) or `*/n` (n<30) will be intercepted locally by the CLI and report an error; the backend also performs a second validation.
- If `--timezone` is omitted, it defaults to `Asia/Shanghai` (IANA time zone name).

<a id="record-change记录变更"></a>
### record-change (record change)

```bash
+automation-create --app-id <id> --name onUpd --trigger-type record-change \
  --table <table_name> --event UPDATE [--fields '["status"]']
```

- `--event` is an **uppercase enum**: `INSERT` / `UPDATE` / `UPSERT` / `DELETE` (the CLI will uppercase it, but please pass it according to the enum).
- `--table` is the **table name** in the app database (corresponding to the value of the `.name` field in the `+db-table-list` / `+db-table-get` output), required. Miaoda app dataloom tables use the name as the stable identifier, and there is no independent `table_id`.
- `--fields` is a JSON string array, meaningful only for `UPDATE`/`UPSERT`; `'["*"]'` means listen to all fields; not passing it means no field restriction.

<a id="webhook外部回调"></a>
### webhook (external callback)

```bash
+automation-create --app-id <id> --name hook --trigger-type webhook \
  [--white-ip-list '["1.1.1.1","2.2.2.2"]']
```

- At creation, `--white-ip-list` (JSON string array) is optional to restrict the callback source IPs.
- The callback URL has **two sets: preview / runtime**, and is not echoed back at creation; use `+automation-get` to check the current configuration, and `+automation-update --reset-url --app-env <preview|runtime>` to rotate it.
- The Bearer Token is the callback authentication credential, see "Credential masking and one-time echo" below.

<a id="feishu-approval飞书审批"></a>
### feishu-approval (Feishu approval)

```bash
+automation-create --app-id <id> --name apv --trigger-type feishu-approval \
  --event-type approval_instance --instance-status APPROVED [--approval-code <code>]
```

- `--event-type` is required, take `approval_instance` or `approval_task`, which determines which set of flags the status uses:
  - `approval_instance` → `--instance-status` (repeatable)
  - `approval_task` → `--task-status` (repeatable)
- **Domain rule**: statuses are validated in buckets by `event-type`, and the two buckets' enums are **not completely identical** (`PENDING`/`APPROVED`/`REJECTED`/`REVERTED`/`OVERTIME_CLOSE`/`OVERTIME_RECOVER` are shared by both buckets; `TRANSFERRED`/`ROLLBACK`/`DONE` exist only for task; `CANCELED`/`DELETED` exist only for instance); passing a status from the wrong bucket will be intercepted locally by the CLI, and the error message will print the list of valid values for that bucket. For the specific enums, see the command `--help`.

<a id="approval-code-获取路径"></a>
## approval-code acquisition path

`--approval-code` is **optional**. When not passed, it matches all approval definitions; to limit it to a specific approval process, obtain the specific code from the **Feishu Approval admin console** and pass it. The trigger OpenAPI does not provide approval definition query capability; the specific code must be looked up in the Approval admin console.

<a id="凭证脱敏与一次性回显安全关键"></a>
## Credential masking and one-time echo (security-critical)

- `+automation-get` / `+automation-list`: **never return the plaintext Bearer Token**—`trigger_condition.token_value` is masked as `null`. When the user wants to know "what the token is", neither list nor get can find the plaintext.
- `+automation-update --enable-token` / `--reset-token`: the plaintext Bearer Token is **echoed only once to stdout for that invocation**, and at the same time a one-time warning is printed to stderr:
  ```text
  warning: this bearer token is shown only once and is NOT stored by lark-cli — copy it now and store it in your own secret manager.
  ```
- The Webhook URL is the same: after `--reset-url`, the new URL is echoed only once for that invocation, and the old URL immediately becomes invalid.
- The CLI does not persist any plaintext token/URL to disk (not written to cache / config / recent / debug log / error messages).
- **A lost Token can only be reset**: it cannot be recovered, the only way to restore it is `+automation-update --reset-token` (the old token becomes invalid at the same time).

<a id="高危确认"></a>
## High-risk confirmation

`+automation-update` as a whole is `high-risk-write`, and any invocation requires an explicit `--yes`; when missing, the framework will require confirmation (exit code 10). **Do not automatically add `--yes`**—it must be added only after the user explicitly confirms. The following Webhook action flags are especially irreversible:

- `--reset-url` (the old callback URL immediately becomes invalid, requires configuring `--app-env preview|runtime`)
- `--reset-token` (the old token immediately becomes invalid)
- `--disable-token` (turns off token validation, **irreversible**)

The four Webhook action flags (`--reset-url` / `--enable-token` / `--disable-token` / `--reset-token`) **can only pass one at a time**. When unsure of the impact, first run `--dry-run` to see the request that will be sent (without plaintext).

<a id="写入目标与授权"></a>
### Write target and authorization

Resolve the unique app, trigger name, and environment, then execute. Resetting the URL must determine `--app-env preview|runtime`; the two are independent URLs and cannot be guessed. Resetting immediately invalidates the old URL/Token, and the new value is returned only in that invocation's response, the CLI does not save it; include the replacement and the impact on related callers within the scope the user has already authorized. When the scope is already clear, you may directly include `--yes`, otherwise first complete read-only location and dry-run, then ask about the missing choices. There is no need for a fixed confirmation passphrase or repeated confirmation of the same request.

Using `--disable-token` together with an empty `--white-ip-list` will allow callbacks from any source to trigger. Set these two only according to the user's actual request, and do not proactively change them; when the user has explicitly requested this combination, follow the authorization and retain the platform's own parameter restrictions.

<a id="默认-disabled"></a>
## Default disabled

After `+automation-create` creates a trigger, it is **disabled by default** and will not trigger automatically. It requires `+automation-enable` to start running automatically according to the conditions (and the trigger executes the **already-published online** app code—if the app is not published, even enabling it will have no actual effect).

**Agent behavior constraint**: when the user only says "create/configure a trigger", **do not** proactively `+automation-enable` in the same turn. When only creating, keep it disabled; when the user has already requested enabling or fully running the automation, you may continue to enable after verifying the configuration and publish status. Enabling will:
- make the webhook type immediately callable externally (the user may originally have just wanted to "prepare the URL for later use")
- make cron actually trigger at the scheduled time (the user may originally have wanted to "create it first and observe the configuration")
- make record-change immediately respond to table changes

Recommended wording after successful creation: `已创建 <name>，当前 disabled；需要真正开始自动运行时告诉我，我用 +automation-enable 启用它。` **do not** enable immediately after successful creation, even if the skill says "requires enable to trigger automatically"—this is an explanation for the user, not an action instruction for the agent.

<a id="本地全栈-trigger-闭环"></a>
## Local full-stack Trigger closed loop

When the user wants the trigger to actually execute business code, first confirm that the current workspace is an initialized app project, and read the guide in it that matches the trigger task.

`--name` is the app-internal unique trigger location key; the code-side binding name must be verbatim identical to it. Do not use the trigger ID or method name in its place. The specific handler syntax and integration method are subject to the project guide.

<a id="仅创建配置触发器"></a>
### Only create/configure the trigger

Applies to cron, record-change, webhook, and feishu-approval. Create with `+automation-create`, and omit `--status` or explicitly pass `disabled`, then report the name and disabled status.

Do not pass `--status enabled`, and do not write a handler, commit/push, release, or enable; even less should you call the creation API success "runnable". Default disabled is the endpoint of this intent, not a to-do to automatically enable later.

<a id="仅启用已有-disabled-trigger"></a>
### Only enable an existing disabled trigger

When the user only requests enabling an existing and disabled trigger, and does not request modifying code or producing a real runtime event, first use `+automation-get` to verify the name, type, and disabled status, then use `+release-list --status finished --page-size 1` to verify whether a finished online release exists. Release history can only prove that the current online app has a published version, and cannot prove that this trigger name is already bound to a handler. When no finished release exists, explain that enable will only change the configuration state and there is currently no executable online version; when it exists, explain that it will activate this trigger configuration for the current online app. Then execute `+automation-enable` as requested by the user, and use `+automation-get` to confirm enabled.

This path must not modify the handler, commit/push, or release. When unpublished, do not automatically create a release, and do not claim that the trigger has started actually running. Even if a finished release exists, you may only report enable as configuration activation; when there is no handler source or runtime result, do not claim that the business handler already exists, has run, or is available. If the user expects unpublished local changes to take effect, or after checking you find that a handler really needs to be added/modified, switch to the "implement or update the handler, then publish and start/test" path below; do not publish the entire `sprint/default` just to enable.

For UPSERT or feishu-approval, only change the configuration state; since this guide has no proven handler, delivery, or live verification contract for them, after enabling you must also not claim that the business code has run or that the trigger has been actually verified as usable.

<a id="测试已有线上-trigger不改代码"></a>
### Test an existing online trigger (without changing code)

When the user requests testing an already-published trigger and does not request modifying the handler, first use `+automation-get` to verify the name, type, and current status, then use `+release-list --status finished --page-size 1` to confirm that the app has a finished release, and explain that this test covers the current online code. When there is no finished release, stop the runtime test and only report the configuration state; do not automatically modify source code, commit/push, or release for the test. Release history does not prove that this name is already bound to a handler; the result of a real probe is the verification evidence for this test; if the user expects local unpublished changes, switch to the code change closed loop.

Record the pre-test state, and complete both types of authorization and all preflight before any temporary enable: the test request already explicitly includes temporary enable, or separately obtain enable authorization; at the same time, determine the specific event, impact, payload, observed result, and cleanup according to "Operation-level authorization for runtime verification" below. When it was originally disabled, only temporarily enable after completing these thresholds, and restore disabled after verification ends; when it was originally enabled, do not meaninglessly toggle the state. When it was originally disabled, regardless of whether the probe succeeds, fails, has an uncertain result, or ends early or is interrupted after temporary enable, you must ultimately `+automation-disable` and read back disabled, and must not stop at enabled. The test intent itself does not determine the database record, Webhook request, or other event payload.

<a id="仅完成-handler不发布不启用"></a>
### Only complete the handler (do not publish/do not enable)

Use this path only for cron, webhook, record-change's `INSERT`, `UPDATE`, `DELETE`.

Create or locate a disabled trigger with an already-clear name, read the project guide, implement the same-named business handler according to its requirements, and complete local verification. Only commit/push under existing Git confirmation or pre-authorization; stop before `+release-create` and `+automation-enable`. When the user has not explicitly said "publish it", ask first, and do not default to putting the complete app online.

<a id="把-handler-发布好但先不要启动"></a>
### Publish the handler, but do not start it yet

Use this path only for cron, webhook, record-change's `INSERT`, `UPDATE`, `DELETE`. First locate with `+automation-get`; when it does not exist, use `+automation-create` to create a same-named disabled trigger, and read it back again to confirm. When it already exists, record whether it is enabled. After completing the same-named business handler according to the project guide and verifying locally, commit, `git push origin sprint/default`. If the trigger is already enabled, first explain that it must be temporarily disabled before publishing and the possible runtime interruption, and obtain authorization for this temporary disable; when authorization is not obtained, stop before publishing. After obtaining authorization, execute `+automation-disable` before publishing, and use `+automation-get` again to confirm disabled. Then publish the complete app:

```bash
lark-cli apps +release-create --as user --app-id <app_id> --branch sprint/default
```

If `+release-create` itself returns an error or does not return `data.release_id`: treat it as confirmed that no release was created this round (the new code is not live); restore the originally enabled trigger to enabled and read it back, keep the originally disabled one disabled, then stop. If the creation result is unknown due to a timeout or similar, keep it disabled, first use `+release-list --status finished --page-size 1` to check whether a new release has been produced, and then decide. After obtaining `data.release_id`, call `+release-get` for **this round's** ID: when `publishing`, keep polling every 20 seconds, for a total of about 5 minutes at most; if it times out and the status is still uncertain, report `release_id` and the current status, and keep it disabled; only `data.status=finished` counts as complete. When `failed` is confirmed and the new code is not live, restore the originally enabled trigger to enabled and read it back, and keep the originally disabled one disabled. A release puts the entire app live and may affect existing online functionality; when startup or testing authorization has not been obtained, always keep it disabled after finished, and do not execute `+automation-enable`.

<a id="实现或更新-handler-后发布并启动测试"></a>
### Publish and start/test after implementing or updating a handler

Use this path only when this round genuinely requires adding or modifying a cron, webhook, or record-change `INSERT`, `UPDATE`, or `DELETE` handler, and the user asks to start or test after publishing this code. Execute in the following order, which must not be skipped:

1. Use `+automation-get` to locate and record the pre-publish state, then verify its `--name` and type and read the project guide; if it does not exist, use `+automation-create` to create a trigger with the same name and keep it disabled by default.
2. Complete the business handler with the same name according to the project guide and verify it locally.
3. When Git is confirmed/pre-authorized, commit, then execute `git push origin sprint/default`.
4. If the trigger is currently enabled, first explain that it must be temporarily disabled before publishing and the possible runtime interruption this may cause, and obtain authorization for this temporary disablement; if authorization is not obtained, stop before publishing. After obtaining authorization, execute `+automation-disable`, and use `+automation-get` again to confirm it is disabled; when it was originally disabled, do not toggle the state pointlessly.
5. Execute `+release-create --branch sprint/default`. If the command itself returns an error or does not return `data.release_id`: treat it as confirmed that no release was created this round (the new code is not live); restore the originally enabled trigger to enabled and read it back, keep the originally disabled one disabled, then stop. If the result is unknown due to a timeout or similar, keep it disabled, first use `+release-list --status finished --page-size 1` to check whether a new release has been produced, and then decide. After obtaining `data.release_id`, proceed to the next step.
6. Execute `+release-get` for that ID; only `data.status=finished` allows continuing; when `publishing`, keep polling every 20 seconds, for a total of about 5 minutes at most. If it times out and the status is still uncertain, stop polling for this round, report `release_id` and the current status, and keep it disabled; when `failed` is confirmed, report the publish failure; restore the originally enabled trigger to enabled only after confirming the new code is not live, and keep the originally disabled one disabled. When the publish status is still uncertain, do not enter the enable, probe, or state-restoration branches. `is_published=true` cannot substitute for this round's publish completion.
7. **Start only**: after obtaining continuous-start authorization, execute `+automation-enable`, and use `+automation-get` to confirm it is enabled; end here, and do not create a runtime probe.
8. **Test (including "start and test")**: first complete all preflight according to the next section "Operation-level authorization for runtime verification", including the specific event, sibling impact, payload, observed results, and cleanup; keep it disabled until that is complete, and only then execute `+automation-enable` and read it back, then have the authorized subject create real runtime conditions and verify the business result. If continuous start is also explicitly required, keep it enabled only after the probe succeeds.
9. If the user only asks for testing rather than continuous start, restore to the pre-publish state only after this round's release has `finished` and the probe succeeds: for a trigger that was originally disabled or newly created this round, `+automation-disable` and read it back; one that was originally enabled may remain enabled. Whether the user is only testing or starting and testing, if the probe fails, the result is uncertain, or it ends early after enable, always `+automation-disable` and read back disabled; do not use "enabled before publish" as the basis for recovery after failure, because this round's new code is already live. It may be enabled again only after the old release has been rolled back and verified, or after a fix and republish with a successful probe. If restoration fails, clearly report the current state.

There is no general `automation-debug` or trigger log shortcut. When a safe event entry point, matching environment, or observable result is missing, record blocked; do not fabricate test success.

<a id="运行时验证的操作级授权"></a>
### Operation-level authorization for runtime verification

Authorization to enable a trigger is not authorization to create runtime events, and test authorization is not authorization for arbitrary database writes. cron may wait for the scheduled time; webhook may only send authorized, safe requests that do not leak credentials to an existing runtime URL. Before executing any DML, record-change must clearly define and obtain authorization covering the following scope: environment, table, operation, exact test record or filter condition, payload, expected result, and cleanup method.

Prefer dedicated test records; do not arbitrarily take online business records. When the user has explicitly authorized a precise, revocable test fixture and its cleanup, do not mechanically add another round of confirmation; when the target or impact is still unclear, you must stop. Before a record-change probe, first execute `+automation-list --trigger-type record-change --all` to check other enabled triggers that may be matched by the same environment, table, and operation; if a sibling match exists, you must explain the aggregated business impact and obtain authorization covering those impacts, or switch to an isolated fixture / authorized temporary disablement before testing. `UPDATE` must limit to precise conditions and preserve a restoration method; `INSERT` must pre-arrange cleanup; a restoration UPDATE or cleanup INSERT may also trigger automation again, and must be included in the impact explanation and authorization. `DELETE` must follow [lark-apps-db-execute.md](lark-apps-db-execute.md): first `SELECT count(*)`, execute `--dry-run`, show the impact and obtain explicit authorization for that deletion target, then execute with `--yes`; if the cleanup action includes a deletion that was not pre-authorized, it must also go through that threshold.

When a safe, authorized, and cleanable event entry point is missing, record blocked; do not derive arbitrary online data writes from "just test it".

<a id="upsert-与飞书审批边界"></a>
### UPSERT and Feishu approval boundaries

record-change UPSERT can create disabled configuration, but there is currently no proven runtime code contract; do not silently treat it as UPDATE, and do not promise handler or live verification.

feishu-approval can create disabled configuration and read or update `event_type`, the corresponding status, and optional `approval_code`. There is currently no proven runtime handler contract or actual delivery verification; do not call enable or approval API success as business code having executed.

<a id="未触发时的诊断顺序"></a>
### Diagnostic order when not triggered

Troubleshoot in the order of code integration required by `--name` / the project guide → this round's release `finished` → enabled state → type conditions, environment, and existing logs. Customer approval delivery failures belong to server-side event delivery troubleshooting; do not attribute them to this SOP or rewrite unrelated business code.

<a id="常见错误与决策场景"></a>
## Common errors and decision scenarios

| Symptom / user intent | Correct handling |
|---|---|
| Creation reports a name conflict (`--name` is unique within the app) | Change the name or add a suffix and retry |
| cron reports invalid / interval too small | Check whether it is five-field and whether the minute field is `*` or `*/n`(n<30) |
| `--reset-url` reports missing app-env | Add `--app-env preview` or `--app-env runtime` |
| Want to change a cron trigger to webhook (cross-type change) | update does not support changing type, and this module does not provide deletion either. The old trigger can only be disabled with `+automation-disable` (kept in the app), and a new webhook trigger created; if you really want to clean up the old trigger, manually delete it in the Miaoda web UI |
| Trigger is enabled but does not fire | For proven cron, webhook, and record-change (INSERT/UPDATE/DELETE), troubleshoot according to "Diagnostic order when not triggered"; for UPSERT and feishu-approval, only verify the configuration boundary, and do not promise handler or live verification. |
| "The token leaked" | Prefer `+automation-update --reset-token --yes` rotation (the old token becomes invalid immediately), rather than directly disable-token to turn off verification |
| "The callback URL leaked" | `+automation-update --reset-url --app-env <env> --yes` rotation |

<a id="不在本模块-范围"></a>
## Out of scope for this module

- Approval definition queries, webhook consumer implementation, real-time trigger log tail: not supported in this release.
- Identity selection, handling insufficient permissions, exit-10 approval, general framework for high-risk operations: see [`../../shared/index.md`](../../shared/index.md), not repeated here.
