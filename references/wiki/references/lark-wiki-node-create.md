# wiki +node-create


Create a new node in a Feishu Wiki and automatically resolve the target knowledge space. This shortcut wraps the native `wiki.nodes.create` in a layer more suited to everyday use: you can specify `space_id` directly, or automatically look up the owning space from a parent node; under the `user` identity, if both `--space-id` and `--parent-node-token` are omitted, it will also automatically fall back to the personal knowledge base `my_library`.

<a id="命令"></a>
## Command

```bash
# Create a docx node under the root of the personal knowledge base (user identity defaults to falling back to my_library)
lark-cli wiki +node-create \
  --title "项目计划"

# Create a docx node in the specified knowledge space
lark-cli wiki +node-create \
  --space-id <SPACE_ID> \
  --title "项目计划"

# Create a child node under the specified parent node
lark-cli wiki +node-create \
  --parent-node-token <PARENT_NODE_TOKEN> \
  --title "迭代记录"

# Explicitly specify creation into the personal knowledge base (user identity only; bot does not support `--space-id my_library`)
lark-cli wiki +node-create \
  --space-id my_library \
  --title "学习笔记"

# Create a shortcut node (shortcut)
lark-cli wiki +node-create \
  --parent-node-token <PARENT_NODE_TOKEN> \
  --node-type shortcut \
  --origin-node-token <ORIGIN_NODE_TOKEN> \
  --title "原文档快捷方式"

# Create a node of a non-docx type
lark-cli wiki +node-create \
  --space-id <SPACE_ID> \
  --obj-type sheet \
  --title "周报数据"

# Preview the underlying call chain
lark-cli wiki +node-create \
  --title "Roadmap" \
  --dry-run
```

<a id="返回值"></a>
## Return Value

On success, a JSON object is returned; common fields include:

- `resolved_space_id`: the real knowledge space ID ultimately used for creation
- `resolved_by`: the source of space resolution, which may be `explicit_space_id`, `parent_node_token`, `my_library`
- `node_token`: the newly created wiki node token
- `obj_token`: the node's associated object token
- `obj_type`: the node's associated object type
- `node_type`: the node type
- `title`: the node title
- `permission_grant` (optional): returned only for `--as bot`, indicating whether manageable permission has been automatically granted to the current CLI user

> [!IMPORTANT]
> If the node is **created under the app identity (bot)**, such as `lark-cli wiki +node-create --as bot`, after successful creation the CLI will **attempt to automatically grant the current CLI user `full_access` (manageable permission) on that wiki node**.
>
> When created under the app identity, the result additionally returns the `permission_grant` field, clearly stating the authorization result:
> - `status = granted`: the current CLI user has obtained manageable permission on that wiki node
> - `status = skipped`: there is no available current user `open_id` locally, so no automatic authorization will occur; you may prompt the user to complete `lark-cli auth login` first, then let the AI / agent continue using the app identity (bot) to grant the current user permission
> - `status = failed`: the node was created successfully, but automatically authorizing the user failed; the failure reason will be included, and you will be prompted to retry later or continue handling the node using the bot identity
>
> `permission_grant.perm = full_access` indicates that the resource has been granted "manageable permission"
>
> **Do not perform owner transfer on your own initiative.** Creation or import does not imply owner transfer; when the user has explicitly requested a transfer and the target is determined, proceed with the authorization execution.

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--space-id` | No | Target knowledge space ID; the `user` identity may pass the special value `my_library` to indicate the personal knowledge base, while the `bot` identity does not support this value |
| `--parent-node-token` | No | Parent wiki node token or document obj_token; create the new node under the resolved Wiki node |
| `--title` | No | Node title |
| `--node-type` | No | Node type, defaults to `origin`; possible values: `origin`, `shortcut` |
| `--obj-type` | No | The object type corresponding to the node, defaults to `docx`; possible values: `sheet`, `mindnote`, `bitable`, `file`, `docx`, `slides`. `file` only supports `shortcut` nodes |
| `--origin-node-token` | No | Required when `--node-type=shortcut`, indicating the source node token that the shortcut points to |

<a id="空间解析规则"></a>
## Space Resolution Rules

- **Priority**: `--space-id` > `--parent-node-token` > `my_library`
- **Explicit space**: when `--space-id` is passed, the shortcut will use that space directly; if the value is `my_library`, it is available only under the `user` identity, and `GET /open-apis/wiki/v2/spaces/my_library` will first be called to resolve it into a real `space_id`
- **Parent node inference**: when `--space-id` is not passed but `--parent-node-token` is passed, `GET /open-apis/wiki/v2/spaces/node_by_token` will first be called to get the parent node, then its `space_id` will be read
- **Parent node type**: `--parent-node-token` accepts a Wiki `node_token` or a document `obj_token` already mounted to Wiki; creation uses the `node_token` returned by the query; when a space is explicitly passed, the parent node's space is also queried and validated.
- **Personal knowledge base fallback**: under the `user` identity, if neither `--space-id` nor `--parent-node-token` is passed, `my_library` will be automatically resolved
- **bot identity restrictions**: the `bot` identity has neither the "personal knowledge base" fallback semantics nor support for explicitly passing `--space-id my_library`; use a real `space_id` or `--parent-node-token` instead

<a id="节点类型与对象类型"></a>
## Node Types and Object Types

| `node_type` | Supported `obj_type` |
|-------------|-------------------|
| `origin` | `sheet`, `mindnote`, `bitable`, `docx`, `slides` |
| `shortcut` | `sheet`, `mindnote`, `bitable`, `file`, `docx`, `slides` |

- When `--node-type=shortcut`, `--origin-node-token` must also be provided
- When `--node-type=origin`, `--origin-node-token` must not be passed
- `--obj-type=file` only supports `--node-type=shortcut`; entity nodes do not support creating the `file` type
- A `shortcut` node is merely a shortcut entry in the wiki; the node actually referenced is specified by `--origin-node-token`
- If `+node-create` returns a parameter validation error due to the above combinations, it is forbidden to switch to raw `wiki nodes create` or call the OpenAPI directly to bypass validation; instead, fix `node_type`, `obj_type`, or `origin_node_token`

```bash
# Create a shortcut node pointing to a file
lark-cli wiki +node-create \
  --space-id <SPACE_ID> \
  --node-type shortcut \
  --obj-type file \
  --origin-node-token <ORIGIN_NODE_TOKEN>
```

<a id="一致性校验"></a>
## Consistency Validation

- If both `--space-id` and `--parent-node-token` are passed, the shortcut will validate whether the space the parent node belongs to is consistent with `--space-id`
- If the spaces resolved from the two are inconsistent, the command will directly return a validation error instead of continuing to create
- For `my_library`, under the `user` identity, the real `space_id` will also be resolved first before performing this layer of validation

<a id="行为说明"></a>
## Behavior Description

- **Default object type**: when `--obj-type` is not passed, a `docx` node is created by default
- **Default node type**: when `--node-type` is not passed, a normal node `origin` is created by default
- **dry-run orchestration**:
  - Only `--title` passed: shows the two-step call of `my_library` resolution + node creation
  - Only `--parent-node-token` passed: shows the two-step call of "query parent node -> create node"
  - When both `my_library` and a parent node are needed: shows a three-step call chain
- **bot automatic authorization**: if `--as bot` is used, the result additionally includes `permission_grant`, used to indicate whether manageable permission on the newly created node has been automatically granted to the current CLI user
- **Output result**: on success, fields such as `resolved_space_id`, `resolved_by`, `node_token`, `obj_token`, `obj_type`, `node_type`, `title` are returned, making it convenient to continue operations afterward
- **Structural limits**: returning `131003` indicates that a structural limit such as the total node count of the knowledge space, directory depth, or the number of direct child nodes under a single parent node has been triggered. This is not a transient error, and retrying with the same parameters is forbidden. Based on the upstream error message, choose a shallower or different parent node, reorganize existing nodes, or clean up / switch to another knowledge space; do not blindly add intermediate levels when the specific limit cannot be confirmed.

<a id="推荐场景"></a>
## Recommended Scenarios

- When the user says "create a new page in my wiki", prefer `lark-cli wiki +node-create --title "..."`
- When the user has already given a parent page link or `parent_node_token`, prefer passing `--parent-node-token`, letting the shortcut automatically infer the space
- When a wiki shortcut needs to be created, use `--node-type shortcut --origin-node-token <token>`

> [!CAUTION]
> `wiki +node-create` is a **write operation**; user intent must be confirmed before execution.

<a id="参考"></a>
## References

- [lark-wiki](../index.md) -- all wiki commands
- [lark-shared](../../shared/index.md) -- authentication and global parameters
