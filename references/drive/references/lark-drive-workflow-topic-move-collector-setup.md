<a id="主题资料收集工作流输入与目标确认"></a>
# Topic Material Collection Workflow: Input and Target Confirmation

Loaded by states `PARSE_INPUT`, `RESOLVE_TARGET`, `CONFIRM_CONTEXT`.

This document is responsible for user input parsing, target location parsing, pre-search confirmation, and `TargetLocation`. It must not execute search recall, resource classification, target creation, or resource movement.

This document only serves `topic_move_collector`. After entering this document, you must confirm `workflow_id=topic_move_collector`; you must not reroute the current task to another workflow.

<a id="必读上下文"></a>
## Required Context

Before executing the rules in this document:

1. Handle identity, authentication, and permissions according to [`../../shared/index.md`](../../shared/index.md).
2. When parsing a Drive target, follow [`lark-drive-inspect.md`](lark-drive-inspect.md), [`lark-drive-create-folder.md`](lark-drive-create-folder.md), and [`lark-drive-search.md`](lark-drive-search.md).
3. When parsing a Wiki target, follow [`../../wiki/index.md`](../../wiki/index.md), [`../../wiki/references/lark-wiki-node-get.md`](../../wiki/references/lark-wiki-node-get.md), and [`../../wiki/references/lark-wiki-node-create.md`](../../wiki/references/lark-wiki-node-create.md).

<a id="状态parse_input"></a>
## State: `PARSE_INPUT`

Entry condition: the workflow is triggered.

Must:

1. Extract `topic`, `target`, `identity`, `owner_scope`, and `constraints`.
2. Treat `topic` and `target` as required fields.
3. Unless the user explicitly requests the bot / app perspective, `identity` defaults to using the user identity.
4. Default `allow_cross_container_move=true`, but it must be displayed in `CONFIRM_CONTEXT`.
5. Default `owner_scope=mine`, meaning only search resources owned / managed by the current user.
6. Only set `owner_scope=all_visible` when the user explicitly requests "unrestricted owner", "include those shared with me", "all documents I can see", or "full search".
7. Unless the user explicitly provides restrictions, keep `constraints` empty.
8. If `topic` or `target` is missing, only ask the minimal clarifying question.

<a id="输入字段"></a>
### Input Fields

| Field | Description |
|-------|------|
| `topic` | The topic, keywords, content clues, synonyms, abbreviations, and exclusion terms the user wants to find. |
| `target` | The archive target, which can be an existing Drive folder, an existing Wiki node, a Drive folder to be created, or a Wiki node to be created. |
| `identity` | The execution identity, defaulting to `--as user`. |
| `owner_scope` | The search owner scope, defaulting to `mine`; `all_visible` is only used when the user explicitly requests expansion to all visible resources. |
| `constraints` | Restrictions explicitly given by the user, such as type, time, creator, comments, title, and scope. |
| `allow_cross_container_move` | Whether cross Drive / Wiki container movement is allowed; allowed by default, but must be confirmed. |

<a id="澄清模板"></a>
### Clarification Template

```text
I still need two pieces of information before I can start:

1. What is the topic / keyword / content clue to search for?
2. After finding it, which Drive folder or Wiki node should it be moved to? If a new target needs to be created, please also specify the parent location and the new name.
```

<a id="状态resolve_target"></a>
## State: `RESOLVE_TARGET`

Entry condition: `topic` and `target` have been obtained.

Must:

1. Parse the existing target into a concrete token.
2. If the target needs to be created, only parse the parent location and the new target name.
3. In this state, you must not create folders or Wiki nodes.
4. Keep the Drive folder token, Wiki node token, Wiki object token, space ID, and parent token separately.
5. If the target URL / token exists, but the current identity cannot read or parse the target location, set `target_resolve_status=permission_denied`, remain in `RESOLVE_TARGET`, and wait for the user to change the target or end; you must not enter search.
6. If the known movement direction is unsupported, mark it as early as possible.

<a id="目标解析"></a>
### Target Parsing

| Condition | What the agent must do | Set `target_type` |
|-----------|---------------|-------------------|
| Existing Drive folder URL or token | When there is a URL, parse it with `drive +inspect`; keep `folder_token` | `drive_folder` |
| Existing Wiki node URL or token | Parse with `wiki +node-get` or `drive +inspect`; keep `wiki_node_token` and `space_id` | `wiki_node` |
| Create a new Drive folder under a known parent | Parse the parent folder; save the new folder name; do not create | `new_drive_folder` |
| Create a new Wiki node under a known parent | Parse the knowledge space and optional parent node; save the new node title; do not create | `new_wiki_node` |
| Use the Wiki space root node as the target | Parse `space_id`; the parent token may be empty | `wiki_space` |
| The target name is ambiguous | Search or list candidates only when necessary; display candidates and wait for the user to choose | `unknown` |

<a id="目标解析状态"></a>
### Target Parsing Status

| Condition | `target_resolve_status` |
|------|--------------------------|
| The target has been parsed, or the parent location of the target to be created has been parsed | `resolved` |
| The target name is ambiguous, the candidates are not unique, or `target_type=unknown` requires the user to choose | `ambiguous` |
| The known target direction or target type is not supported by this workflow | `unsupported` |
| The target URL / token exists, but the current identity is not authorized to read, parse, or confirm the target location | `permission_denied` |

<a id="目标解析出口门禁"></a>
### Target Parsing Exit Gate

| `target_resolve_status` | Next State | What the agent must do |
|-------------------------|----------|----------------|
| `resolved` | `CONFIRM_CONTEXT` | Display the parsed target and proceed to pre-search confirmation. |
| `ambiguous` | Remain in `RESOLVE_TARGET` | Display candidates and wait for the user to choose; you must not enter `CONFIRM_CONTEXT`. |
| `unsupported` | Remain in `RESOLVE_TARGET` | Display the reason it is unsupported, and wait for the user to change the target or end; you must not search. |
| `permission_denied` | Remain in `RESOLVE_TARGET` | Display the permission blocker, and wait for the user to change the target or end; you must not search. |

After the user provides a new target, re-execute `RESOLVE_TARGET`. Only when the new parsing result is `resolved` may you enter `CONFIRM_CONTEXT`; when the user chooses to end, enter `DONE`.

<a id="跨容器规则"></a>
### Cross-Container Rules

| Source -> Target | Default Rule |
|------------------|---------|
| Drive resource -> Drive folder | Supported; use `drive +move`. |
| Drive document-type resource -> Wiki node / space | When the resource type is supported, use `wiki +move`. |
| Wiki node -> Wiki node / space | Supported; use `wiki +move --node-token`. |
| Wiki node -> Drive folder | `wiki +move-to-drive`. |

<a id="状态confirm_context"></a>
## State: `CONFIRM_CONTEXT`

Entry condition: `target_resolve_status=resolved`.

Must:

1. Display the topic, target, identity, search owner scope, restrictions, and target parsing fields.
2. Explain that the next step only performs search / read.
3. Explain whether target creation is planned, but has not yet been executed.
4. Display whether cross-container movement is allowed.
5. Stop before entering `SEARCH_RECALL` and wait for user confirmation.
6. If `owner_scope=all_visible`, clearly indicate that the number of candidates may be large and may include resources that cannot be moved.

<a id="确认-ui"></a>
### Confirmation UI

```text
Let me first confirm this collection task.

Search topic:
Target location:
Target parsing:
Execution identity:
Search scope:
Optional restrictions:
Cross-container movement:
Next action: only perform search and read verification, do not create targets, do not move resources.

Please confirm whether to start the search based on the above information?
```

Default search scope text:

```text
Search scope: resources owned / managed by the current user
```

Expanded search scope text:

```text
Search scope: all resources visible to the current identity
Risk notice: the number of candidates may be large, and some resources may not be movable; resource parsing and content verification will still be performed later.
```

If the user modifies any field, update `topic`, `target_location`, `owner_scope`, or `constraints`, then only re-execute the affected setup state and display the confirmation information again.

## TargetLocation

```json
{
  "target_type": "drive_folder|wiki_node|wiki_space|new_drive_folder|new_wiki_node|unknown",
  "target_token": "已有目标的 folder_token 或 wiki_node_token",
  "parent_token": "待创建目标的父级 folder_token 或 wiki_node_token",
  "space_id": "知识库空间 ID",
  "target_name": "待创建目标名称",
  "create_required": false,
  "allow_cross_container_move": true,
  "target_resolve_status": "resolved|ambiguous|unsupported|permission_denied"
}
```

| Field | Description |
|-------|------|
| `target_type` | The target location type, used to determine subsequent creation and movement commands. |
| `target_token` | The executable token of an existing target. |
| `parent_token` | The parent location token of the target to be created. |
| `space_id` | The knowledge space ID to which the Wiki target belongs. |
| `target_name` | The name of the target to be created. |
| `create_required` | Whether the target needs to be created in the `EXECUTE` stage. |
| `allow_cross_container_move` | Whether movement between Drive / Wiki is allowed. |
| `target_resolve_status` | The target location parsing status; do not mix it up with `ResourceItem.item_resolve_status`. |
