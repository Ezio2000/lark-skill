# mail +signature


View the mailbox signature list or details. Returns information such as the signature type, default usage, and content preview. Template variables in TENANT (enterprise) signatures are automatically replaced with actual values.

This module corresponds to the shortcut: `lark-cli mail +signature`.

<a id="命令"></a>
## Commands

```bash
# List all signatures
lark-cli mail +signature

# View the details of a signature (rendered content preview, template variable values, image information)
lark-cli mail +signature --detail <signature_id>

# Specify the mailbox
lark-cli mail +signature --from shared@example.com
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--from <email>` | No | Mailbox address (default `me`) |
| `--detail <id>` | No | Signature ID, to view details. If omitted, lists all signatures |

<a id="返回值"></a>
## Return Values

**List mode:**

```json
{
  "ok": true,
  "data": {
    "signatures": [
      {
        "id": "<签名ID>",
        "name": "个人签名",
        "type": "USER",
        "content_preview": "这是我的签名内容 [image] 超链接哈哈"
      },
      {
        "id": "<签名ID>",
        "name": "企业签名",
        "type": "TENANT",
        "is_send_default": true,
        "is_reply_default": true,
        "content_preview": "企业签名 姓名：陈煌 部门：研发团队"
      }
    ]
  }
}
```

**Detail mode (`--detail`):**

```json
{
  "ok": true,
  "data": {
    "id": "<签名ID>",
    "name": "企业签名",
    "type": "TENANT",
    "is_send_default": true,
    "is_reply_default": true,
    "images": [
      {"cid": "76CEB29E-...", "file_key": "121011...", "image_name": "image.png"}
    ],
    "template_vars": {"B-NAME": "陈煌", "B-DEPARTMENT": "研发团队"},
    "content_preview": "企业签名 姓名：陈煌 部门：研发团队"
  }
}
```

<a id="字段说明"></a>
## Field Descriptions

| Field | Description |
|------|------|
| `type` | `USER` (user signature, editable) or `TENANT` (enterprise signature, controlled by administrator template) |
| `is_send_default` | Whether it is the default signature for new emails |
| `is_reply_default` | Whether it is the default signature for replies/forwards |
| `images` | Inline image metadata in the signature (detail mode only) |
| `template_vars` | Replaced values of template variables for TENANT signatures (detail mode only) |
| `content_preview` | Plain text preview of the signature content (`<img>` displayed as `[image]`, up to 200 characters) |

<a id="与-compose-shortcut-配合"></a>
## Working with the compose shortcut

After obtaining the signature ID, you can attach the signature when sending/replying/forwarding:

```bash
# View the signature list to get the ID
lark-cli mail +signature

# Attach the signature when sending an email
lark-cli mail +send --to alice@example.com --subject '你好' --body '<p>内容</p>' --signature-id <签名ID>
```
