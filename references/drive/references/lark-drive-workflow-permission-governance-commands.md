<a id="权限治理-command-patterns"></a>
# Permission Governance Command Patterns

This document only provides concrete `lark-cli` command examples for the `permission_governance` workflow. Read this document only when you have entered the corresponding state and need to assemble commands; the available command scope is still governed by the `Command Map` in [`lark-drive-workflow-permission-governance.md`](lark-drive-workflow-permission-governance.md).

<a id="目录"></a>
## Table of Contents

- `目标解析`
- `目标发现`
- `事实读取`
- `写前确认与执行`

<a id="目标解析"></a>
## Target Resolution

```bash
lark-cli drive +inspect --url '<url>' --as user --format json
```

`drive +inspect` supports Drive folders and is the unified resolution entry point for supported Drive URLs. To set permissions on the folder itself, first resolve the URL via `+inspect`, or use `drive +permission-get-setting --token '<folder_url>'` directly; when passing a bare folder token, you must explicitly pass `--type folder`.

`/wiki/space/<space_id>` URLs are Wiki space scoped; do not use `drive +inspect` to resolve them as a single document; directly extract `space_id` and then enter `DISCOVER_TARGETS`.

<a id="目标发现"></a>
## Target Discovery

Discover targets under a Wiki space / node:

```bash
lark-cli wiki +node-list \
  --space-id '<space_id>' --page-size 50 \
  --page-all --page-limit 0 \
  --as user --format json # replace $SPACE_ID before running

lark-cli wiki +node-list \
  --space-id '<space_id>' --parent-node-token '<node_token>' --page-size 50 \
  --page-all --page-limit 0 \
  --as user --format json # replace $SPACE_ID before running

lark-cli wiki +node-list \
  --space-id '<space_id>' --page-token '<PAGE_TOKEN>' --page-size 50 \
  --as user --format json # replace $SPACE_ID before running
```

When parsing the response, use `data.nodes`; do not read the top-level `items`. `--page-limit 0` means pagination at the current level has no page count limit; `--page-all` only covers pagination within the current `space-id` / `parent-node-token` scope and does not recurse into child nodes. When a node has `has_child=true`, you must continue to recursively read using that node's `node_token` as the `--parent-node-token`.

Discover targets under a Drive folder:

```bash
lark-cli drive files list \
  --params '{"folder_token":"<folder_token>","page_size":200}' \
  --as user --format json

lark-cli drive files list \
  --params '{"folder_token":"<folder_token>","page_size":200,"page_token":"<PAGE_TOKEN>"}' \
  --as user --format json
```

<a id="事实读取"></a>
## Fact Reading

Read metadata:

```bash
lark-cli drive metas batch_query \
  --data '{"request_docs":[{"doc_token":"<token>","doc_type":"<type>"}],"with_url":true}' \
  --as user --format json
```

Read permission settings:

```bash
lark-cli drive +permission-get-setting \
  --token '<url-or-token>' --type '<type>' \
  --as user --format json
```

A bare folder token must explicitly pass `--type folder`:

```bash
lark-cli drive +permission-get-setting \
  --token '<folder_token>' --type folder \
  --as user --format json
```

When reading permission settings via URL, `--type` may be omitted:

```bash
lark-cli drive +permission-get-setting \
  --token '<url>' \
  --as user --format json # replace $LARK_DRIVE_URL before running
```

Read the list of direct collaborators/authorized members as needed:

```bash
lark-cli drive +member-list \
  --token '<token_or_url>' \
  --type '<type>' \
  --fields 'name,type,external_label' \
  --as user --format json
```

`--fields` is not passed by default; pass it explicitly only when you need names, collaborator types, avatars, or external labels. It only declares the fields expected in the response and does not grant field-level permissions: when requesting the user's `name` / `avatar`, `contact:user.base:readonly` is also required ("Get user basic information"). When field permissions or data visibility are insufficient, the API may still succeed but omit the corresponding fields; a missing field must not be interpreted as an empty value.

Read access statistics as needed:

```bash
lark-cli drive file.statistics get \
  --params '{"file_token":"<token>","file_type":"<type>"}' \
  --as user --format json
```

Read recent access records as needed:

```bash
lark-cli drive file.view_records list \
  --params '{"file_token":"<token>","file_type":"<type>","page_size":50}' \
  --as user --format json
```

<a id="写前确认与执行"></a>
## Pre-write Confirmation and Execution

Check manage-public permission before patching:

```bash
lark-cli drive permission.members auth \
  --params '{"token":"<token>","type":"<type>","action":"manage_public"}' \
  --as user --format json
```

Read the current schema before patching:

```bash
lark-cli schema drive.permission.public.patch --format json
```

Only patch fields supported by the current schema; for Wiki targets, you must omit fields that the schema explicitly marks as unsupported for Wiki.

Patch public permission after explicit confirmation:

```bash
lark-cli drive permission.public patch \
  --params '{"token":"<token>","type":"<type>"}' \
  --data '{"link_share_entity":"closed","external_access":false}' \
  --as user --yes --format json
```

Request access permission after explicit confirmation:

```bash
lark-cli drive +apply-permission \
  --token '<url>' \
  --perm view --remark '<reason>' --as user --format json

lark-cli drive +apply-permission \
  --token '<bare-token>' --type '<type>' \
  --perm view --remark '<reason>' --as user --format json
```

Read the current schema before transferring owner:

```bash
lark-cli schema drive.permission.members.transfer_owner --format json
```

Transfer owner after explicit confirmation:

```bash
lark-cli drive permission.members transfer_owner \
  --params '{"token":"<token>","type":"<type>","need_notification":true,"remove_old_owner":false,"old_owner_perm":"full_access","stay_put":true}' \
  --data '{"member_id":"<new_owner_open_id>","member_type":"openid"}' \
  --as user --yes --format json
```

`member_type` can only use values supported by the current schema: `email`, `openid`, `userid`, `appid`. If the user only provides a name, you must first resolve it to a definite identity or ask the user to supply more information; do not guess `member_id`. Batch owner transfers must be executed sequentially, one target at a time.

Enumerate available labels before writing a secure label:

```bash
lark-cli drive +secure-label-list \
  --page-size 10 --lang zh \
  --as user --format json

lark-cli drive +secure-label-list \
  --page-size 10 --page-token '<PAGE_TOKEN>' --lang zh \
  --as user --format json
```

When the user provides a label name, classification text, or an uncertain label ID, you must first enumerate and resolve it to `label-id`; show the target label name and ID in the write confirmation. If no unique label can be found, stop and let the user choose; do not guess.

Update secure label after explicit confirmation:

```bash
lark-cli drive +secure-label-update \
  --token '<url>' \
  --label-id '<label-id>' --as user --format json # replace $LABEL_ID before running

lark-cli drive +secure-label-update \
  --token '<bare-token>' --type '<type>' \
  --label-id '<label-id>' --as user --format json # replace $LABEL_ID before running
```
