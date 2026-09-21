# mail +share-to-chat


Share an email as a card to a Feishu IM conversation (group chat or direct message). Internally completed in two steps: create a share credential → send the card to IM.

**Required Scope:** `mail:user_mailbox.message:readonly`, `im:message`, `im:message.send_as_user`

<a id="命令"></a>
## Command

```bash
# Share a single email to a group chat (default receive-id-type=chat_id)
lark-cli mail +share-to-chat --message-id <邮件ID> --receive-id oc_xxx

# Share an entire conversation to a group chat
lark-cli mail +share-to-chat --thread-id <会话ID> --receive-id oc_xxx

# Share to an individual via email address
lark-cli mail +share-to-chat --message-id <邮件ID> --receive-id user@example.com --receive-id-type email

# Dry Run
lark-cli mail +share-to-chat --message-id <邮件ID> --receive-id oc_xxx --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--message-id <id>` | No (choose one of two) | The email ID to share, mutually exclusive with `--thread-id` |
| `--thread-id <id>` | No (choose one of two) | The email conversation ID to share, mutually exclusive with `--message-id` |
| `--receive-id <id>` | Yes | Target recipient ID, the type is determined by `--receive-id-type` |
| `--receive-id-type <type>` | No | Recipient ID type (default `chat_id`). Options: `chat_id` / `open_id` / `user_id` / `union_id` / `email` |
| `--mailbox <email>` | No | Email address (default `me`) |
| `--dry-run` | No | Only print the request, do not execute |

<a id="返回值"></a>
## Return Value

```json
{
  "ok": true,
  "data": {
    "card_id": "550e8400-e29b-41d4-a716-446655440000",
    "im_message_id": "om_dc13264520392913993dd051dba21dcf"
  }
}
```

<a id="典型场景"></a>
## Typical Scenarios

<a id="场景-1用户说帮我把这封邮件分享到项目群"></a>
### Scenario 1: The user says "help me share this email to the project group"

```bash
# Step 1: Search the group chat to get the chat_id
lark-cli im +chat-search --query "项目群"
# → Get chat_id: oc_xxx

# Step 2: Share the email
lark-cli mail +share-to-chat --message-id <邮件ID> --receive-id oc_xxx
```

<a id="场景-2分享整个邮件会话"></a>
### Scenario 2: Share an entire email conversation

```bash
lark-cli mail +share-to-chat --thread-id <会话ID> --receive-id oc_xxx
```

<a id="场景-3通过邮箱分享给个人"></a>
### Scenario 3: Share to an individual via email address

```bash
lark-cli mail +share-to-chat --message-id <邮件ID> --receive-id alice@example.com --receive-id-type email
```

<a id="常见错误"></a>
## Common Errors

| Symptom | Cause | Solution |
|------|------|------|
| `either --message-id or --thread-id is required` | Neither parameter was passed | Pass one of them |
| `--message-id and --thread-id are mutually exclusive` | Both parameters were passed at the same time | Pass only one |
| 403 `user not in chat` | The user is not in the target conversation | Confirm the user is a group member |
| 404 `message not found` | Invalid email ID | Confirm the email ID is correct |
| 403 `permission not granted` | Missing `im:message` or `im:message.send_as_user` scope | Re-authorize: `lark-cli auth login --scope "im:message,im:message.send_as_user"` |

<a id="相关命令"></a>
## Related Commands

- `lark-cli im +chat-search` — Search the group chat to get the chat_id
- `lark-cli mail +message` — View email content
- `lark-cli mail +thread` — View email conversation
