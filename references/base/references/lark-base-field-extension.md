# base field-extension

Field extensions are used to extend basic field capabilities. When other cells in the same row are updated, they trigger LLM inference to generate new cells. The only publicly supported extension ID currently is `builtin_llm_completion`, which has been confirmed to work with text, single select, and number fields, allowing the target field to generate content based on a prompt and field references, and allowing manual triggering of asynchronous cell update tasks for that field.

Three commands:

- `+field-extension-get`: Read the currently recognizable extension configuration of the target field.
- `+field-extension-update`: Install, update, or clear the target field extension configuration.
- `+field-extension-update-cells`: Initiate a manual update task for a target field that already has a field extension configured.

<a id="何时使用字段插件"></a>
## When to use field extensions

Use a field extension when the user explicitly wants an existing field to automatically generate content, summarize, classify, translate, or extract information based on other fields, and the target capability can be expressed with a prompt. The currently confirmed target field types are text, single select, and number.

A field extension can only be built on an existing field; it cannot create a column schema. To create a new field, still use `+field-create`; to modify schema properties such as field type, options, or name, still use `+field-update`.

<a id="推荐命令"></a>
## Recommended commands

```bash
# Read the current extension configuration
lark-cli base +field-extension-get \
  --base-token <base_token> \
  --table-id <table_id> \
  --field-id <target_field_id> \
  --as user

# Install or update the LLM Completion extension
lark-cli base +field-extension-update \
  --base-token <base_token> \
  --table-id <table_id> \
  --field-id <target_field_id> \
  --json '{"extension_id":"builtin_llm_completion","inputs":{"prompt":[{"type":"text","text":"请根据 "},{"type":"field_ref","field":"需求描述"},{"type":"text","text":" 输出一句简洁结论。"}]}}' \
  --as user \
  --yes

# Clear the field extension configuration
lark-cli base +field-extension-update \
  --base-token <base_token> \
  --table-id <table_id> \
  --field-id <target_field_id> \
  --json '{}' \
  --as user \
  --yes

# Trigger a full-column update scoped by view
lark-cli base +field-extension-update-cells \
  --base-token <base_token> \
  --table-id <table_id> \
  --field-id <target_field_id> \
  --type column \
  --view-id <view_id> \
  --as user \
  --yes

# Update only specified records
lark-cli base +field-extension-update-cells \
  --base-token <base_token> \
  --table-id <table_id> \
  --field-id <target_field_id> \
  --type row \
  --record-id <record_id_1> \
  --record-id <record_id_2> \
  --as user \
  --yes
```

<a id="工作流"></a>
## Workflow

1. Locate the Base, Table, and target Field. The target Field is the existing field that carries the extension output, not the input field referenced in the prompt.
2. Use `+field-extension-get` to read the current configuration. Returning `current_extension=null` means it is not configured, cannot be recognized, or the existing configuration cannot be converted.
3. Construct `+field-extension-update --json`. When installing or updating, pass `extension_id=builtin_llm_completion` and `inputs.prompt`; when clearing, pass `{}`.
4. After the configuration succeeds, call `+field-extension-update-cells` to initiate an asynchronous generation task only when the user explicitly wants to immediately generate or refresh existing cells.
5. When acceptance of results is needed, wait for the task to complete or later use a record read command to sample the target field cells; `update_cells` only returns the task ID and does not directly return the generated results.

<a id="json-结构"></a>
## JSON structure

<a id="通用结构"></a>
### Common structure

The top-level structure of `+field-extension-update --json` is the field extension configuration envelope. Different `extension_id` correspond to different `inputs` structures; do not treat the `inputs` of one extension as the fixed structure for all field extensions.

| Field | Type | Description |
|---|---|---|
| `extension_id` | string | Extension ID. Currently only `builtin_llm_completion` is publicly supported |
| `inputs` | object | Extension configuration object; the structure is determined by `extension_id` |

When clearing the field extension configuration, pass an empty object:

```json
{}
```

### `builtin_llm_completion`

Currently `builtin_llm_completion` is used to let an existing field generate content based on a prompt. Its `inputs` structure is as follows:

| Field | Type | Description |
|---|---|---|
| `inputs.prompt` | PromptSegment[] | Ordered array of prompt segments |
| `prompt[].type` | string | `text` or `field_ref` |
| `prompt[].text` | string | Required when `type=text` |
| `prompt[].field` | string | Required when `type=field_ref`; can pass the field ID or field name of the current table |

Install or update example:

```json
{
  "extension_id": "builtin_llm_completion",
  "inputs": {
    "prompt": [
      {
        "type": "text",
        "text": "请根据 "
      },
      {
        "type": "field_ref",
        "field": "需求描述"
      },
      {
        "type": "text",
        "text": " 输出一句简洁的中文结论。"
      }
    ]
  }
}
```

`field_ref` can only reference other fields in the current table and cannot reference the target field itself; do not use attachment fields or other unsupported fields as reference fields.

<a id="更新单元格"></a>
## Update cells

`+field-extension-update-cells` has two scopes:

This is an asynchronous generation task; the response only indicates that the task has been created. The more cells there are, the longer generation and write-back usually take; full-column updates especially need scope control.

| Scope | Parameter | Semantics |
|---|---|---|
| `--type column` | Optional `--view-id` | Update the target field cells within that view's scope; when `--view-id` is not passed, the backend uses the first view of the target table |
| `--type row` | One or more `--record-id` required | Update only the target field cells on these records |

`--type row` do not pass `--view-id`; `--type column` do not pass `--record-id`.

The response only returns:

```json
{
  "task_id": "<task_id>"
}
```

<a id="返回重点"></a>
## Return highlights

Both reading and writing configuration return `current_extension`:

- When configured and recognizable, `current_extension.extension_id` indicates the extension ID, and `current_extension.inputs` is the configuration object corresponding to that extension.
- When not configured or currently unrecognizable, `current_extension` is `null`.

<a id="权限和风险"></a>
## Permissions and risks

- `+field-extension-get` is a read-only command with permission `base:field:read`.
- `+field-extension-update` is a high-risk write command with permission `base:field:update`; it changes the target field's automatic generation configuration and must be executed with `--yes`.
- `+field-extension-update-cells` is a high-risk write command with permission `base:record:update`; it triggers asynchronous write-back to the target field cells and must be executed with `--yes`.
- The user needs permission to manage the target table or the target field extension in order to trigger an update task; if the API returns insufficient permission, first confirm the user's permissions according to Base permissions or advanced permission roles.

<a id="注意事项"></a>
## Notes

- The target field must be a field type already supported by the current field extension; currently confirmed supported field types are text, single select, and number. Do not treat field extensions as a general capability available for any field type.
- After the extension configuration is written, automatic updates are forcibly enabled; currently there is no parameter to disable automatic updates.
- The `field_ref.field` in the read API usually returns the field name; when the field name is unavailable, it may return the field ID.
- `+field-extension-update` does not return `input_schemas`.
- `+field-extension-update-cells --type column` may trigger a large number of AI generation tasks; the more cells there are, the longer it usually takes; unless the user explicitly requests a full-column refresh, prefer precise updates of target records by `--type row`.
