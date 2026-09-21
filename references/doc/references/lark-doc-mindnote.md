<a id="飞书思维笔记mindnote"></a>
# Feishu Mindnote


When a user wants to operate on a mindnote, the entry point belongs to `lark-doc`, but the actual command execution uses `lark-cli mindnotes nodes list/create`, not `docs +...`.

> [!IMPORTANT]
> This chain currently only supports **reading an existing mindnote**, and reading nodes and creating child nodes within an **existing mindnote**.
> `mindnotes nodes create` is a create/update node command, **not** creating a new mindnote.
> If the user wants to **create a new mindnote**, do not use this chain; use [lark-doc-whiteboard](lark-doc-whiteboard.md) instead.

<a id="获取-mindnote_id"></a>
## Obtaining the `mindnote_id`

`--mindnote-id` takes a **Mindnote document token**, not a node ID. `lark-cli mindnotes` is only responsible for reading and writing nodes inside a mindnote.

```bash
# The user provided a Mindnote URL, or provided a Wiki URL that may wrap a Mindnote
lark-cli drive +inspect --url "<mindnote_or_wiki_url>"
```

Handling rules:

- Regular Mindnote URL: the Mindnote token returned by `drive +inspect` can be used as `--mindnote-id`.
- Wiki URL: do not treat the wiki token in the `/wiki/` path as `--mindnote-id`; you must first unwrap it with `drive +inspect`, confirm the underlying type is `mindnote`, and then use the returned real token. Passing the wiki token directly to `mindnotes nodes list` usually returns `3410003 resource not found`.

<a id="命令"></a>
## Commands

```bash
# First check the command help
lark-cli mindnotes nodes list --help
lark-cli mindnotes nodes create --help

# Read the node list
lark-cli mindnotes nodes list --mindnote-id "<mindnote_token>"

# Create a child node
lark-cli mindnotes nodes create \
  --mindnote-id "<mindnote_token>" \
  --data '{"client_token":"<client_token>","nodes":[{"parent_id":"node_parent123","texts":[{"element_type":"text","text":{"content":"子节点内容"}}],"highlight":"yellow","finish":false}]}'

# Update an existing node
lark-cli mindnotes nodes create \
  --mindnote-id "<mindnote_token>" \
  --data '{"client_token":"<client_token>","nodes":[{"node_id":"node_existing123","texts":[{"element_type":"text","text":{"content":"更新后的节点内容"}}],"highlight":"blue","finish":true}]}'
```

<a id="参数"></a>
## Parameters

### `mindnotes nodes list`

| Parameter | Required | Description |
|------|------|------|
| `--mindnote-id` | Yes | Mindnote token / unique identifier |

Return highlights: common fields in `data.nodes` include `node_id`, `parent_id`, `texts`, `notes`, `images`, `finish`, `highlight`.

### `mindnotes nodes create`

Command parameters:

| Parameter | Required | Description |
|------|------|------|
| `--mindnote-id` | Yes | Mindnote token / unique identifier |
| `--data` | Yes | JSON request body |

Request body fields:

| Field | Required | Description |
|------|------|------|
| `client_token` | No | Idempotency token, recommended for write operations; using a timestamp or UUID is recommended |
| `nodes` | Yes | Array of nodes to create or update |
| `nodes[].node_id` | No | Node ID; passing an existing `node_id` means updating the corresponding node |
| `nodes[].parent_id` | No | Parent node ID; pass when creating a child node |
| `nodes[].texts` | No | Array of node body rich text |
| `nodes[].notes` | No | Array of node note rich text |
| `nodes[].images` | No | List of node images |
| `nodes[].highlight` | No | `red` / `yellow` / `pink` / `blue` / `cyan` / `olive` / `grey` |
| `nodes[].finish` | No | Node completion status |

The rich text fields `texts` / `notes` are element arrays. The most common one is:

```json
[{"element_type":"text","text":{"content":"节点内容"}}]
```

<a id="节点图片nodesimages"></a>
### Node images (`nodes[].images`)

`nodes[].images` accepts an **image token**, not a local file path, and not a URL.

```bash
# First upload the image and get the token
lark-cli docs +media-upload --file ./image.png --parent-type mindnote_image --parent-node <mindnote_token>

# Then write the token into the node
lark-cli mindnotes nodes create \
  --mindnote-id "<mindnote_token>" \
  --data '{"client_token":"<client_token>","nodes":[{"node_id":"node_existing123","images":[{"token":"canonical_token"}]}]}'
```

Parameter description:

| Parameter | Required | Description |
|------|------|------|
| `--file` | Yes | Local image path |
| `--parent-type` | Yes | Upload target type; use `mindnote_image` for images |
| `--parent-node` | Yes | Pass the Mindnote token |
| `nodes[].images[].token` | Yes | Image token returned after upload |

<a id="推荐工作流"></a>
## Recommended workflow

1. First determine whether the user's goal is to "create a new mindnote".
2. If it is to create a new mindnote, switch to [lark-doc-whiteboard](lark-doc-whiteboard.md).
3. If it is to operate on an existing mindnote, first follow "Obtaining the `mindnote_id`" above to confirm that the Mindnote document token has been obtained.
4. After confirming the target type is **Mindnote**, use the real Mindnote token as `--mindnote-id`.
5. First run `mindnotes nodes list` to confirm the target `parent_id`.
6. When adding a child node, pass `parent_id` in `nodes[]`; when updating an existing node, pass the existing `node_id` in `nodes[]`.
7. Then run `mindnotes nodes create`.
8. For write operations, preferably include `client_token`; using a timestamp or UUID is recommended to avoid duplicate creation or duplicate updates on retry.

> [!CAUTION]
> `mindnotes nodes create` is a write operation. When creating, confirm the insertion position; when updating, confirm that `node_id` points to the target node.

<a id="参考"></a>
## References

- [lark-doc-fetch](lark-doc-fetch.md) — fetch document content
- [lark-doc-whiteboard](lark-doc-whiteboard.md) — creating a new mindnote goes through the whiteboard chain
- [lark-drive](../../drive/index.md) — parse cloud space resources such as Mindnote / Wiki
- [lark-shared](../../shared/index.md) — authentication and global parameters
